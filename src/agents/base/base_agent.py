"""Base agent class for all AI agents."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from pydantic import BaseModel, Field

from src.utils import get_logger
from src.config import settings
from src.core.context.context_manager import (
    AdaptiveContextManager, ContextType, ContextImportance
)


class AgentRole(str, Enum):
    """Agent roles in the development team."""
    MANAGER = "manager"
    PM = "pm"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    QA = "qa"
    UI = "ui"
    SCRUM = "scrum"
    REVIEWER = "reviewer"


class AgentStatus(str, Enum):
    """Agent operational status."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    OFFLINE = "offline"


class AgentMessage(BaseModel):
    """Message format for inter-agent communication."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str
    to_agent: str
    task_id: Optional[str] = None
    message_type: str  # work_complete, need_help, conflict, validation_request
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: str = "medium"  # high, medium, low
    
    
class AgentContext(BaseModel):
    """Context information for agent operations."""
    project_id: str
    sprint_id: Optional[str] = None
    task_id: Optional[str] = None
    memory_context: Dict[str, Any] = Field(default_factory=dict)
    shared_knowledge: List[Dict[str, Any]] = Field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        llm_provider: Optional[str] = None,
    ):
        self.agent_id = agent_id
        self.role = role
        self.status = AgentStatus.IDLE
        self.logger = get_logger(f"{self.__class__.__name__}[{agent_id}]")
        
        # Get LLM provider from settings if not specified
        if llm_provider is None:
            llm_provider = settings.agent_llm_mapping.get(role.value, "deepseek")
        
        self.llm_provider = llm_provider
        self.llm_config = settings.get_llm_config(llm_provider)
        
        # Agent state
        self.current_task_id: Optional[str] = None
        self.current_context: Optional[AgentContext] = None
        self.message_queue: List[AgentMessage] = []
        
        # Enhanced context management inspired by context-rot research
        self.context_manager = AdaptiveContextManager(max_context_tokens=8000)
        
        self.logger.info(f"Agent initialized: {role.value} with {llm_provider}")
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Process a task and return the result.
        
        Args:
            task: Task details
            context: Agent context including project and memory
            
        Returns:
            Task processing result
        """
        pass
    
    @abstractmethod
    async def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate the agent's output.
        
        Args:
            output: Output to validate
            
        Returns:
            True if output is valid
        """
        pass
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Get the agent's prompt template."""
        pass
    
    async def send_message(self, to_agent: str, message_type: str, payload: Dict[str, Any]) -> None:
        """Send a message to another agent."""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            task_id=self.current_task_id,
            message_type=message_type,
            payload=payload,
        )
        
        # In real implementation, this would use a message queue
        self.logger.info(f"Sending message to {to_agent}: {message_type}")
        # TODO: Implement actual message sending via Redis or RabbitMQ
    
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive and process a message."""
        self.message_queue.append(message)
        self.logger.info(f"Received message from {message.from_agent}: {message.message_type}")
    
    def update_status(self, status: AgentStatus) -> None:
        """Update agent status."""
        old_status = self.status
        self.status = status
        self.logger.info(f"Status changed: {old_status.value} -> {status.value}")
    
    async def initialize_for_project(self, project_id: str, context: Dict[str, Any]) -> None:
        """Initialize agent for a specific project."""
        self.current_context = AgentContext(
            project_id=project_id,
            memory_context=context,
        )
        self.logger.info(f"Initialized for project: {project_id}")
    
    async def add_context(self, content: str, context_type: ContextType, 
                         importance: ContextImportance = ContextImportance.MEDIUM) -> str:
        """Add context information with automatic management."""
        return await self.context_manager.add_context(content, context_type, importance)
    
    async def get_optimized_context(self, query: str = "") -> Dict[str, Any]:
        """Get context optimized to prevent context rot."""
        return await self.context_manager.get_optimized_context(query)
    
    async def add_task_context(self, task: Dict[str, Any]) -> None:
        """Add task-specific context."""
        task_content = f"Task: {task.get('type', 'unknown')}\nDetails: {str(task)}"
        await self.add_context(
            task_content, 
            ContextType.TASK_CONTEXT, 
            ContextImportance.CRITICAL
        )
    
    async def add_conversation_context(self, message: str, from_agent: str = None) -> None:
        """Add conversation context."""
        if from_agent:
            content = f"Message from {from_agent}: {message}"
        else:
            content = f"Agent {self.agent_id}: {message}"
        
        await self.add_context(
            content,
            ContextType.CONVERSATION,
            ContextImportance.HIGH
        )
    
    async def add_decision_context(self, decision: Dict[str, Any]) -> None:
        """Add decision-making context."""
        decision_content = f"Decision: {decision.get('decision', '')}\nRationale: {decision.get('rationale', '')}"
        await self.add_context(
            decision_content,
            ContextType.DECISION_HISTORY,
            ContextImportance.HIGH
        )
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context management statistics."""
        return self.context_manager.get_context_stats()
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        self.status = AgentStatus.OFFLINE
        self.current_task_id = None
        self.current_context = None
        self.message_queue.clear()
        self.logger.info("Agent cleanup completed")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, role={self.role.value}, status={self.status.value})"