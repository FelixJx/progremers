"""Message bus for agent communication."""

import asyncio
import json
import redis.asyncio as redis
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid

from src.core.communication.protocol import AgentMessage, MessageStatus, MessageType, MessagePriority
from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class DeliveryMode(str, Enum):
    """Message delivery modes."""
    DIRECT = "direct"        # Direct delivery to specific agent
    BROADCAST = "broadcast"  # Broadcast to all agents
    ROLE_BASED = "role_based"  # Delivery to agents with specific role
    PROJECT_BASED = "project_based"  # Delivery to all agents in project


class MessageHandler:
    """Base class for message handlers."""
    
    def __init__(self, agent_id: str, supported_types: List[MessageType]):
        self.agent_id = agent_id
        self.supported_types = supported_types
        self.logger = get_logger(f"MessageHandler[{agent_id}]")
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle an incoming message.
        
        Args:
            message: The message to handle
            
        Returns:
            Optional reply message
        """
        if message.message_type not in self.supported_types:
            self.logger.warning(f"Unsupported message type: {message.message_type}")
            return None
        
        try:
            # Route to specific handler method
            handler_method = getattr(self, f"handle_{message.message_type.value}", None)
            
            if handler_method:
                return await handler_method(message)
            else:
                return await self.handle_default(message)
                
        except Exception as e:
            self.logger.error(f"Error handling message {message.message_id}: {str(e)}")
            return None
    
    async def handle_default(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Default message handler."""
        self.logger.info(f"Received {message.message_type} from {message.from_agent}")
        return None


class MessageBus:
    """
    Redis-based message bus for agent communication.
    
    Provides reliable message delivery, queuing, and broadcasting
    capabilities for the agent team.
    """
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Message routing
        self.agent_handlers: Dict[str, MessageHandler] = {}
        self.agent_queues: Dict[str, str] = {}  # agent_id -> queue_name
        self.active_subscriptions: Set[str] = set()
        
        # Message tracking
        self.message_tracking: Dict[str, Dict[str, Any]] = {}
        self.delivery_stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "average_delivery_time": 0.0
        }
        
        # Configuration
        self.max_retry_attempts = 3
        self.message_ttl_seconds = 3600  # 1 hour
        self.dead_letter_queue = "dead_letter_queue"
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self) -> None:
        """Initialize the message bus."""
        
        self.logger.info("Initializing message bus...")
        
        try:
            # Test Redis connection
            await self.redis_client.ping()
            
            # Start background tasks
            self._background_tasks = [
                asyncio.create_task(self._message_processor()),
                asyncio.create_task(self._retry_failed_messages()),
                asyncio.create_task(self._cleanup_expired_messages())
            ]
            
            self.logger.info("Message bus initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize message bus: {str(e)}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the message bus."""
        
        self.logger.info("Shutting down message bus...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Close Redis connection
        await self.redis_client.close()
        
        self.logger.info("Message bus shutdown complete")
    
    async def register_agent(
        self,
        agent_id: str,
        handler: MessageHandler,
        queue_name: Optional[str] = None
    ) -> None:
        """
        Register an agent with the message bus.
        
        Args:
            agent_id: Agent identifier
            handler: Message handler for the agent
            queue_name: Custom queue name (optional)
        """
        
        if queue_name is None:
            queue_name = f"agent_queue_{agent_id}"
        
        self.agent_handlers[agent_id] = handler
        self.agent_queues[agent_id] = queue_name
        
        # Create queue if it doesn't exist
        await self._ensure_queue_exists(queue_name)
        
        self.logger.info(f"Registered agent {agent_id} with queue {queue_name}")
    
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the message bus."""
        
        if agent_id in self.agent_handlers:
            del self.agent_handlers[agent_id]
        
        if agent_id in self.agent_queues:
            queue_name = self.agent_queues[agent_id]
            del self.agent_queues[agent_id]
            
            # Optionally clear the queue
            await self.redis_client.delete(queue_name)
        
        self.logger.info(f"Unregistered agent {agent_id}")
    
    async def send_message(
        self,
        message: AgentMessage,
        delivery_mode: DeliveryMode = DeliveryMode.DIRECT
    ) -> bool:
        """
        Send a message through the bus.
        
        Args:
            message: Message to send
            delivery_mode: How to deliver the message
            
        Returns:
            True if message was queued successfully
        """
        
        self.logger.info(f"Sending {message.message_type} from {message.from_agent} to {message.to_agent}")
        
        try:
            # Track message
            self.message_tracking[message.message_id] = {
                "message": message,
                "sent_at": datetime.utcnow(),
                "delivery_attempts": 0,
                "status": MessageStatus.PENDING
            }
            
            # Route message based on delivery mode
            if delivery_mode == DeliveryMode.DIRECT:
                success = await self._send_direct_message(message)
            elif delivery_mode == DeliveryMode.BROADCAST:
                success = await self._send_broadcast_message(message)
            elif delivery_mode == DeliveryMode.ROLE_BASED:
                success = await self._send_role_based_message(message)
            elif delivery_mode == DeliveryMode.PROJECT_BASED:
                success = await self._send_project_based_message(message)
            else:
                self.logger.error(f"Unknown delivery mode: {delivery_mode}")
                return False
            
            if success:
                self.delivery_stats["messages_sent"] += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send message {message.message_id}: {str(e)}")
            return False
    
    async def _send_direct_message(self, message: AgentMessage) -> bool:
        """Send message directly to a specific agent."""
        
        target_agent = message.to_agent
        
        if target_agent not in self.agent_queues:
            self.logger.error(f"Agent {target_agent} not registered")
            return False
        
        queue_name = self.agent_queues[target_agent]
        
        # Add message to agent's queue
        message_data = {
            "message": message.to_json(),
            "priority": message.priority.value,
            "expires_at": (datetime.utcnow() + timedelta(seconds=self.message_ttl_seconds)).isoformat()
        }
        
        await self.redis_client.lpush(queue_name, json.dumps(message_data))
        
        # Notify agent (if subscribed)
        await self.redis_client.publish(f"notify_{target_agent}", message.message_id)
        
        return True
    
    async def _send_broadcast_message(self, message: AgentMessage) -> bool:
        """Send message to all registered agents."""
        
        success_count = 0
        
        for agent_id in self.agent_queues:
            if agent_id != message.from_agent:  # Don't send to self
                # Create a copy for each recipient
                message_copy = AgentMessage.from_dict(message.to_dict())
                message_copy.to_agent = agent_id
                message_copy.message_id = str(uuid.uuid4())
                
                if await self._send_direct_message(message_copy):
                    success_count += 1
        
        return success_count > 0
    
    async def _send_role_based_message(self, message: AgentMessage) -> bool:
        """Send message to agents with specific role."""
        
        target_role = message.to_agent  # Role name instead of agent ID
        success_count = 0
        
        # Find agents with the target role
        for agent_id in self.agent_queues:
            agent_role = await self._get_agent_role(agent_id)
            if agent_role == target_role:
                message_copy = AgentMessage.from_dict(message.to_dict())
                message_copy.to_agent = agent_id
                message_copy.message_id = str(uuid.uuid4())
                
                if await self._send_direct_message(message_copy):
                    success_count += 1
        
        return success_count > 0
    
    async def _send_project_based_message(self, message: AgentMessage) -> bool:
        """Send message to all agents in a project."""
        
        if not message.project_id:
            self.logger.error("Project-based message missing project_id")
            return False
        
        success_count = 0
        
        # Find agents working on the project
        project_agents = await self._get_project_agents(message.project_id)
        
        for agent_id in project_agents:
            if agent_id != message.from_agent:  # Don't send to self
                message_copy = AgentMessage.from_dict(message.to_dict())
                message_copy.to_agent = agent_id
                message_copy.message_id = str(uuid.uuid4())
                
                if await self._send_direct_message(message_copy):
                    success_count += 1
        
        return success_count > 0
    
    async def receive_messages(
        self,
        agent_id: str,
        max_messages: int = 10,
        timeout_seconds: int = 5
    ) -> List[AgentMessage]:
        """
        Receive messages for an agent.
        
        Args:
            agent_id: Agent to receive messages for
            max_messages: Maximum messages to retrieve
            timeout_seconds: Timeout for blocking receive
            
        Returns:
            List of received messages
        """
        
        if agent_id not in self.agent_queues:
            return []
        
        queue_name = self.agent_queues[agent_id]
        messages = []
        
        try:
            # Get messages from queue
            for _ in range(max_messages):
                # Use blocking pop with timeout
                result = await self.redis_client.brpop([queue_name], timeout_seconds)
                
                if not result:
                    break  # Timeout reached
                
                _, message_data = result
                message_info = json.loads(message_data)
                
                # Check if message has expired
                expires_at = datetime.fromisoformat(message_info["expires_at"])
                if datetime.utcnow() > expires_at:
                    continue  # Skip expired message
                
                # Parse message
                message = AgentMessage.from_json(message_info["message"])
                
                # Update delivery status
                if message.message_id in self.message_tracking:
                    self.message_tracking[message.message_id]["status"] = MessageStatus.DELIVERED
                    self.delivery_stats["messages_delivered"] += 1
                
                messages.append(message)
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to receive messages for {agent_id}: {str(e)}")
            return []
    
    async def process_agent_messages(self, agent_id: str) -> None:
        """Process all pending messages for an agent."""
        
        if agent_id not in self.agent_handlers:
            return
        
        handler = self.agent_handlers[agent_id]
        messages = await self.receive_messages(agent_id, max_messages=20)
        
        for message in messages:
            try:
                # Let the agent handle the message
                reply = await handler.handle_message(message)
                
                # Update message status
                if message.message_id in self.message_tracking:
                    self.message_tracking[message.message_id]["status"] = MessageStatus.PROCESSED
                
                # Send reply if provided
                if reply:
                    await self.send_message(reply)
                
                # Send acknowledgment if required
                if message.requires_response and not reply:
                    ack_message = message.create_reply(
                        from_agent=agent_id,
                        message_type=MessageType.STATUS_UPDATE,
                        payload={"status": "received", "processed": True}
                    )
                    await self.send_message(ack_message)
                    
            except Exception as e:
                self.logger.error(f"Error processing message {message.message_id}: {str(e)}")
                
                # Mark as failed
                if message.message_id in self.message_tracking:
                    self.message_tracking[message.message_id]["status"] = MessageStatus.FAILED
    
    async def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a sent message."""
        
        if message_id not in self.message_tracking:
            return None
        
        tracking_info = self.message_tracking[message_id]
        
        return {
            "message_id": message_id,
            "status": tracking_info["status"].value,
            "sent_at": tracking_info["sent_at"].isoformat(),
            "delivery_attempts": tracking_info["delivery_attempts"],
            "from_agent": tracking_info["message"].from_agent,
            "to_agent": tracking_info["message"].to_agent,
            "message_type": tracking_info["message"].message_type.value
        }
    
    async def get_agent_queue_size(self, agent_id: str) -> int:
        """Get the number of pending messages for an agent."""
        
        if agent_id not in self.agent_queues:
            return 0
        
        queue_name = self.agent_queues[agent_id]
        return await self.redis_client.llen(queue_name)
    
    async def get_bus_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        
        return {
            "registered_agents": len(self.agent_handlers),
            "active_queues": len(self.agent_queues),
            "tracked_messages": len(self.message_tracking),
            "delivery_stats": self.delivery_stats.copy(),
            "queue_sizes": {
                agent_id: await self.get_agent_queue_size(agent_id)
                for agent_id in self.agent_queues
            }
        }
    
    # Background tasks
    
    async def _message_processor(self) -> None:
        """Background task to process messages."""
        
        while not self._shutdown_event.is_set():
            try:
                # Process messages for all registered agents
                for agent_id in list(self.agent_handlers.keys()):
                    await self.process_agent_messages(agent_id)
                
                # Wait before next processing cycle
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in message processor: {str(e)}")
                await asyncio.sleep(5)
    
    async def _retry_failed_messages(self) -> None:
        """Background task to retry failed message deliveries."""
        
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                for message_id, tracking_info in list(self.message_tracking.items()):
                    if tracking_info["status"] == MessageStatus.FAILED:
                        message = tracking_info["message"]
                        
                        if message.should_retry_delivery():
                            # Retry delivery
                            success = await self._send_direct_message(message)
                            
                            if success:
                                tracking_info["status"] = MessageStatus.PENDING
                                tracking_info["delivery_attempts"] += 1
                            else:
                                # Move to dead letter queue if max attempts reached
                                if tracking_info["delivery_attempts"] >= self.max_retry_attempts:
                                    await self._move_to_dead_letter_queue(message)
                                    del self.message_tracking[message_id]
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in retry task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_messages(self) -> None:
        """Background task to clean up expired messages."""
        
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                expired_messages = []
                
                for message_id, tracking_info in self.message_tracking.items():
                    message = tracking_info["message"]
                    if message.is_expired():
                        expired_messages.append(message_id)
                
                # Remove expired messages
                for message_id in expired_messages:
                    del self.message_tracking[message_id]
                
                if expired_messages:
                    self.logger.info(f"Cleaned up {len(expired_messages)} expired messages")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(600)
    
    # Helper methods
    
    async def _ensure_queue_exists(self, queue_name: str) -> None:
        """Ensure a queue exists in Redis."""
        # Redis lists are created automatically when first item is added
        pass
    
    async def _get_agent_role(self, agent_id: str) -> str:
        """Get the role of an agent."""
        # This would query the database for agent role
        # For now, extract from agent ID
        if "pm" in agent_id:
            return "pm"
        elif "dev" in agent_id:
            return "developer"
        elif "qa" in agent_id:
            return "qa"
        elif "arch" in agent_id:
            return "architect"
        elif "manager" in agent_id:
            return "manager"
        else:
            return "unknown"
    
    async def _get_project_agents(self, project_id: str) -> List[str]:
        """Get list of agents working on a project."""
        # This would query the database for project team members
        # For now, return all registered agents
        return list(self.agent_queues.keys())
    
    async def _move_to_dead_letter_queue(self, message: AgentMessage) -> None:
        """Move a message to the dead letter queue."""
        
        dead_letter_data = {
            "message": message.to_json(),
            "failed_at": datetime.utcnow().isoformat(),
            "reason": "max_retry_attempts_exceeded"
        }
        
        await self.redis_client.lpush(self.dead_letter_queue, json.dumps(dead_letter_data))
        self.delivery_stats["messages_failed"] += 1
        
        self.logger.warning(f"Moved message {message.message_id} to dead letter queue")