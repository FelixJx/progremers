"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Integer, Float,
    ForeignKey, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class ProjectStatus(str, PyEnum):
    """Project status enum."""
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SprintStatus(str, PyEnum):
    """Sprint status enum."""
    PLANNING = "planning"
    ACTIVE = "active"
    REVIEW = "review"
    COMPLETED = "completed"


class TaskStatus(str, PyEnum):
    """Task status enum."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class Project(Base):
    """Project model."""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    project_type = Column(String(50))  # web, mobile, desktop, etc.
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    tech_stack = Column(JSON)  # {"frontend": "React", "backend": "Node.js", etc.}
    team_config = Column(JSON)  # Which agents are assigned
    repository_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    sprints = relationship("Sprint", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    agent_outputs = relationship("AgentOutput", back_populates="project", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_project_status", "status"),
        Index("idx_project_created", "created_at"),
    )


class Sprint(Base):
    """Sprint model for agile development cycles."""
    __tablename__ = "sprints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    sprint_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    goal = Column(Text)
    status = Column(Enum(SprintStatus), default=SprintStatus.PLANNING)
    
    # Sprint timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Sprint artifacts
    planning_notes = Column(JSON)  # Planning meeting notes
    review_notes = Column(JSON)    # Review meeting notes
    retrospective_notes = Column(JSON)  # Retrospective notes
    daily_standups = Column(JSON)  # Array of daily standup records
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("project_id", "sprint_number", name="uq_project_sprint_number"),
        Index("idx_sprint_status", "status"),
    )


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(UUID(as_uuid=True), ForeignKey("sprints.id"))
    
    title = Column(String(500), nullable=False)
    description = Column(Text)
    task_type = Column(String(50))  # feature, bug, improvement, etc.
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    story_points = Column(Integer)
    
    # Assignment
    assigned_agent_id = Column(String(100))
    assigned_agent_role = Column(String(50))
    
    # Task details
    acceptance_criteria = Column(JSON)
    dependencies = Column(JSON)  # List of task IDs this depends on
    blockers = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    agent_outputs = relationship("AgentOutput", back_populates="task", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_task_status", "status"),
        Index("idx_task_assigned", "assigned_agent_id"),
        Index("idx_task_priority", "priority"),
    )


class Agent(Base):
    """Agent registry and configuration."""
    __tablename__ = "agents"
    
    id = Column(String(100), primary_key=True)  # e.g., "dev-001"
    role = Column(String(50), nullable=False)  # manager, pm, developer, etc.
    llm_provider = Column(String(50))
    mcp_config = Column(JSON)  # MCP server configuration
    
    # Agent state
    current_status = Column(String(50), default="idle")
    current_project_id = Column(UUID(as_uuid=True))
    current_task_id = Column(UUID(as_uuid=True))
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    average_task_time = Column(Float)  # in hours
    quality_score = Column(Float)  # 0-1
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime)
    
    # Relationships
    outputs = relationship("AgentOutput", back_populates="agent", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_agent_role", "role"),
        Index("idx_agent_status", "current_status"),
    )


class AgentOutput(Base):
    """Agent output and activity log."""
    __tablename__ = "agent_outputs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), ForeignKey("agents.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    
    output_type = Column(String(50))  # code, document, test, design, etc.
    content = Column(JSON)  # The actual output
    confidence_score = Column(Float)  # Agent's confidence in the output
    
    # Quality metrics
    validated = Column(Boolean, default=False)
    validation_score = Column(Float)
    validation_feedback = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # in seconds
    tokens_used = Column(Integer)
    
    # Relationships
    agent = relationship("Agent", back_populates="outputs")
    project = relationship("Project", back_populates="agent_outputs")
    task = relationship("Task", back_populates="agent_outputs")
    
    # Indexes
    __table_args__ = (
        Index("idx_output_created", "created_at"),
        Index("idx_output_type", "output_type"),
    )


class ConflictResolution(Base):
    """Record of conflicts and their resolutions."""
    __tablename__ = "conflict_resolutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Conflict details
    agent1_id = Column(String(100), nullable=False)
    agent2_id = Column(String(100), nullable=False)
    conflict_type = Column(String(50))  # technical, priority, approach, etc.
    conflict_description = Column(Text)
    
    # Resolution
    resolution_method = Column(String(50))  # rule_based, precedent, manager, human
    resolution_decision = Column(Text)
    resolution_rationale = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))  # agent_id or "human"
    
    # Indexes
    __table_args__ = (
        Index("idx_conflict_created", "created_at"),
        Index("idx_conflict_agents", "agent1_id", "agent2_id"),
    )


class SharedKnowledge(Base):
    """Cross-project knowledge base."""
    __tablename__ = "shared_knowledge"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_type = Column(String(50))  # pattern, solution, bug_fix, best_practice
    title = Column(String(500), nullable=False)
    content = Column(JSON, nullable=False)
    
    # Source and applicability
    source_project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    applicable_domains = Column(JSON)  # ["e-commerce", "social", "fintech"]
    tags = Column(JSON)  # ["authentication", "performance", "security"]
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.5)  # 0-1
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_agent = Column(String(100))
    
    # Indexes
    __table_args__ = (
        Index("idx_knowledge_type", "knowledge_type"),
        Index("idx_knowledge_effectiveness", "effectiveness_score"),
    )