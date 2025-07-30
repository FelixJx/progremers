"""Communication protocol for agents."""

import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

from src.utils import get_logger

logger = get_logger(__name__)


class MessageType(str, Enum):
    """Types of messages between agents."""
    # Work coordination
    TASK_ASSIGNMENT = "task_assignment"
    WORK_COMPLETE = "work_complete"
    WORK_REQUEST = "work_request"
    DEPENDENCY_READY = "dependency_ready"
    
    # Information sharing
    INFORMATION_SHARE = "information_share"
    STATUS_UPDATE = "status_update"
    PROGRESS_REPORT = "progress_report"
    
    # Problem resolution
    HELP_REQUEST = "help_request"
    CONFLICT_REPORT = "conflict_report"
    BLOCKER_REPORT = "blocker_report"
    
    # Quality assurance
    VALIDATION_REQUEST = "validation_request"
    VALIDATION_RESPONSE = "validation_response"
    REVIEW_REQUEST = "review_request"
    REVIEW_RESPONSE = "review_response"
    
    # Meeting coordination
    MEETING_INVITE = "meeting_invite"
    MEETING_RESPONSE = "meeting_response"
    MEETING_UPDATE = "meeting_update"
    
    # System messages
    HEARTBEAT = "heartbeat"
    ERROR_REPORT = "error_report"
    SHUTDOWN_NOTICE = "shutdown_notice"


class MessagePriority(str, Enum):
    """Message priority levels."""
    CRITICAL = "critical"    # Immediate attention required
    HIGH = "high"           # Handle within minutes
    MEDIUM = "medium"       # Handle within hour
    LOW = "low"            # Handle when convenient


class MessageStatus(str, Enum):
    """Message delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class AgentMessage:
    """Standard message format for agent communication."""
    
    # Routing information (required fields first)
    from_agent: str
    to_agent: str  # Can be "*" for broadcast
    message_type: MessageType
    
    # Message identification
    message_id: Optional[str] = None
    conversation_id: Optional[str] = None  # For tracking related messages
    
    # Message metadata
    priority: MessagePriority = MessagePriority.MEDIUM
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Content
    subject: str = ""
    payload: Dict[str, Any] = None
    
    # Context
    project_id: Optional[str] = None
    sprint_id: Optional[str] = None
    task_id: Optional[str] = None
    
    # Delivery tracking
    status: MessageStatus = MessageStatus.PENDING
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    
    # Response tracking
    requires_response: bool = False
    response_timeout_seconds: Optional[int] = None
    in_reply_to: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.payload is None:
            self.payload = {}
        
        if self.conversation_id is None and self.in_reply_to:
            # Use the original message's conversation ID or create new one
            self.conversation_id = self.in_reply_to
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['expires_at']:
            data['expires_at'] = data['expires_at'].isoformat()
        
        # Convert enums to strings
        data['message_type'] = data['message_type'].value
        data['priority'] = data['priority'].value
        data['status'] = data['status'].value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary."""
        # Convert string values back to enums
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = MessagePriority(data['priority'])
        data['status'] = MessageStatus(data['status'])
        
        # Convert ISO strings back to datetime
        if data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Create message from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def should_retry_delivery(self) -> bool:
        """Check if message delivery should be retried."""
        return (
            self.status == MessageStatus.FAILED and
            self.delivery_attempts < self.max_delivery_attempts and
            not self.is_expired()
        )
    
    def create_reply(
        self,
        from_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        subject: str = ""
    ) -> 'AgentMessage':
        """Create a reply message."""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            conversation_id=self.conversation_id or self.message_id,
            from_agent=from_agent,
            to_agent=self.from_agent,
            message_type=message_type,
            priority=self.priority,
            subject=f"Re: {self.subject}" if not subject else subject,
            payload=payload,
            project_id=self.project_id,
            sprint_id=self.sprint_id,
            task_id=self.task_id,
            in_reply_to=self.message_id
        )


class MessageProtocol:
    """
    Defines the communication protocol and message formats for agents.
    """
    
    def __init__(self):
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Protocol configuration
        self.protocol_version = "1.0"
        self.default_timeout_seconds = 300  # 5 minutes
        self.max_message_size_bytes = 1024 * 1024  # 1MB
        
        # Message templates for different types
        self.message_templates = self._initialize_message_templates()
    
    def create_task_assignment(
        self,
        from_agent: str,
        to_agent: str,
        task_details: Dict[str, Any],
        project_id: str,
        priority: MessagePriority = MessagePriority.MEDIUM
    ) -> AgentMessage:
        """Create a task assignment message."""
        
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.TASK_ASSIGNMENT,
            priority=priority,
            subject=f"Task Assignment: {task_details.get('title', 'New Task')}",
            payload={
                "task": task_details,
                "deadline": task_details.get("deadline"),
                "requirements": task_details.get("requirements", []),
                "dependencies": task_details.get("dependencies", [])
            },
            project_id=project_id,
            requires_response=True,
            response_timeout_seconds=self.default_timeout_seconds
        )
    
    def create_work_complete(
        self,
        from_agent: str,
        to_agent: str,
        work_result: Dict[str, Any],
        project_id: str,
        task_id: Optional[str] = None
    ) -> AgentMessage:
        """Create a work completion message."""
        
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.WORK_COMPLETE,
            priority=MessagePriority.HIGH,
            subject=f"Work Complete: {work_result.get('task_name', 'Task')}",
            payload={
                "result": work_result,
                "completion_time": datetime.utcnow().isoformat(),
                "quality_metrics": work_result.get("quality_metrics", {}),
                "next_steps": work_result.get("next_steps", [])
            },
            project_id=project_id,
            task_id=task_id,
            requires_response=True
        )
    
    def create_help_request(
        self,
        from_agent: str,
        to_agent: str,
        help_details: Dict[str, Any],
        project_id: str,
        urgency: MessagePriority = MessagePriority.HIGH
    ) -> AgentMessage:
        """Create a help request message."""
        
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.HELP_REQUEST,
            priority=urgency,
            subject=f"Help Needed: {help_details.get('topic', 'Assistance Required')}",
            payload={
                "problem_description": help_details.get("problem", ""),
                "context": help_details.get("context", {}),
                "attempted_solutions": help_details.get("attempted", []),
                "urgency_reason": help_details.get("urgency_reason", "")
            },
            project_id=project_id,
            requires_response=True,
            response_timeout_seconds=1800  # 30 minutes for help requests
        )
    
    def create_conflict_report(
        self,
        from_agent: str,
        conflicting_agent: str,
        conflict_details: Dict[str, Any],
        project_id: str
    ) -> AgentMessage:
        """Create a conflict report message."""
        
        return AgentMessage(
            from_agent=from_agent,
            to_agent="manager-001",  # Always send conflicts to manager
            message_type=MessageType.CONFLICT_REPORT,
            priority=MessagePriority.HIGH,
            subject=f"Conflict Report: {from_agent} vs {conflicting_agent}",
            payload={
                "conflicting_agent": conflicting_agent,
                "conflict_type": conflict_details.get("type", "unknown"),
                "description": conflict_details.get("description", ""),
                "our_position": conflict_details.get("our_position", ""),
                "their_position": conflict_details.get("their_position", ""),
                "impact": conflict_details.get("impact", "medium"),
                "suggested_resolution": conflict_details.get("suggestion", "")
            },
            project_id=project_id,
            requires_response=True
        )
    
    def create_validation_request(
        self,
        from_agent: str,
        to_agent: str,
        validation_data: Dict[str, Any],
        project_id: str
    ) -> AgentMessage:
        """Create a validation request message."""
        
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.VALIDATION_REQUEST,
            priority=MessagePriority.MEDIUM,
            subject=f"Validation Request: {validation_data.get('item_type', 'Item')}",
            payload={
                "validation_type": validation_data.get("type", "general"),
                "item_to_validate": validation_data.get("item", {}),
                "validation_criteria": validation_data.get("criteria", []),
                "context": validation_data.get("context", {}),
                "deadline": validation_data.get("deadline")
            },
            project_id=project_id,
            requires_response=True,
            response_timeout_seconds=3600  # 1 hour for validation
        )
    
    def create_status_update(
        self,
        from_agent: str,
        to_agent: str,
        status_data: Dict[str, Any],
        project_id: str
    ) -> AgentMessage:
        """Create a status update message."""
        
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.LOW,
            subject=f"Status Update from {from_agent}",
            payload={
                "current_status": status_data.get("status", "working"),
                "current_task": status_data.get("current_task", {}),
                "progress": status_data.get("progress", 0.0),
                "blockers": status_data.get("blockers", []),
                "estimated_completion": status_data.get("eta"),
                "next_steps": status_data.get("next_steps", [])
            },
            project_id=project_id
        )
    
    def create_meeting_invite(
        self,
        from_agent: str,
        to_agents: List[str],
        meeting_details: Dict[str, Any],
        project_id: str
    ) -> List[AgentMessage]:
        """Create meeting invitation messages."""
        
        invites = []
        
        for to_agent in to_agents:
            invite = AgentMessage(
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=MessageType.MEETING_INVITE,
                priority=MessagePriority.MEDIUM,
                subject=f"Meeting Invitation: {meeting_details.get('title', 'Team Meeting')}",
                payload={
                    "meeting_type": meeting_details.get("type", "general"),
                    "title": meeting_details.get("title", ""),
                    "agenda": meeting_details.get("agenda", []),
                    "scheduled_time": meeting_details.get("time", ""),
                    "duration_minutes": meeting_details.get("duration", 60),
                    "attendees": to_agents,
                    "meeting_link": meeting_details.get("link", ""),
                    "preparation_required": meeting_details.get("preparation", [])
                },
                project_id=project_id,
                requires_response=True,
                response_timeout_seconds=7200  # 2 hours to respond to meeting
            )
            invites.append(invite)
        
        return invites
    
    def validate_message(self, message: AgentMessage) -> List[str]:
        """Validate message format and content."""
        
        errors = []
        
        # Check required fields
        if not message.from_agent:
            errors.append("Missing from_agent")
        
        if not message.to_agent:
            errors.append("Missing to_agent")
        
        if not message.message_type:
            errors.append("Missing message_type")
        
        # Check message size
        message_size = len(message.to_json().encode('utf-8'))
        if message_size > self.max_message_size_bytes:
            errors.append(f"Message too large: {message_size} bytes (max: {self.max_message_size_bytes})")
        
        # Check expiration
        if message.is_expired():
            errors.append("Message has expired")
        
        # Type-specific validation
        type_errors = self._validate_message_type(message)
        errors.extend(type_errors)
        
        return errors
    
    def _validate_message_type(self, message: AgentMessage) -> List[str]:
        """Validate message based on its type."""
        
        errors = []
        payload = message.payload
        
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            if "task" not in payload:
                errors.append("Task assignment missing task details")
        
        elif message.message_type == MessageType.WORK_COMPLETE:
            if "result" not in payload:
                errors.append("Work complete missing result")
        
        elif message.message_type == MessageType.HELP_REQUEST:
            if "problem_description" not in payload:
                errors.append("Help request missing problem description")
        
        elif message.message_type == MessageType.CONFLICT_REPORT:
            if "conflicting_agent" not in payload:
                errors.append("Conflict report missing conflicting agent")
            if "description" not in payload:
                errors.append("Conflict report missing description")
        
        elif message.message_type == MessageType.VALIDATION_REQUEST:
            if "item_to_validate" not in payload:
                errors.append("Validation request missing item to validate")
        
        return errors
    
    def _initialize_message_templates(self) -> Dict[MessageType, Dict[str, Any]]:
        """Initialize message templates for different types."""
        
        return {
            MessageType.TASK_ASSIGNMENT: {
                "required_fields": ["task"],
                "optional_fields": ["deadline", "requirements", "dependencies"],
                "response_required": True
            },
            MessageType.WORK_COMPLETE: {
                "required_fields": ["result"],
                "optional_fields": ["completion_time", "quality_metrics", "next_steps"],
                "response_required": True
            },
            MessageType.HELP_REQUEST: {
                "required_fields": ["problem_description"],
                "optional_fields": ["context", "attempted_solutions", "urgency_reason"],
                "response_required": True
            },
            MessageType.STATUS_UPDATE: {
                "required_fields": ["current_status"],
                "optional_fields": ["current_task", "progress", "blockers", "eta"],
                "response_required": False
            }
        }
    
    def get_template(self, message_type: MessageType) -> Optional[Dict[str, Any]]:
        """Get message template for a specific type."""
        return self.message_templates.get(message_type)