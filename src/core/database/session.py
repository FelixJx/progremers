"""Database session management."""

from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from src.config import settings
from src.utils import get_logger
from .models import Base

logger = get_logger(__name__)

# Create engine
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # Disable connection pooling for async compatibility
    echo=settings.app_env == "development",  # Log SQL in development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Usage:
        with get_db() as db:
            # Use db session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database session.
    
    Usage:
        with get_db_context() as db:
            # Use db session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseManager:
    """Database operations manager."""
    
    @staticmethod
    def create_project(name: str, description: str, project_type: str = "web") -> str:
        """Create a new project."""
        from .models import Project
        
        with get_db_context() as db:
            project = Project(
                name=name,
                description=description,
                project_type=project_type,
            )
            db.add(project)
            db.flush()
            project_id = str(project.id)
            
        logger.info(f"Created project: {name} (ID: {project_id})")
        return project_id
    
    @staticmethod
    def create_sprint(project_id: str, name: str, goal: str) -> str:
        """Create a new sprint."""
        from .models import Sprint
        
        with get_db_context() as db:
            # Get sprint number
            sprint_count = db.query(Sprint).filter_by(project_id=project_id).count()
            
            sprint = Sprint(
                project_id=project_id,
                sprint_number=sprint_count + 1,
                name=name,
                goal=goal,
            )
            db.add(sprint)
            db.flush()
            sprint_id = str(sprint.id)
            
        logger.info(f"Created sprint: {name} (ID: {sprint_id})")
        return sprint_id
    
    @staticmethod
    def register_agent(agent_id: str, role: str, llm_provider: str) -> None:
        """Register a new agent."""
        from .models import Agent
        
        with get_db_context() as db:
            # Check if agent exists
            existing = db.query(Agent).filter_by(id=agent_id).first()
            if existing:
                # Update existing agent
                existing.role = role
                existing.llm_provider = llm_provider
            else:
                # Create new agent
                agent = Agent(
                    id=agent_id,
                    role=role,
                    llm_provider=llm_provider,
                )
                db.add(agent)
        
        logger.info(f"Registered agent: {agent_id} (role: {role})")