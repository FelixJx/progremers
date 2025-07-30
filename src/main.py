"""Main application entry point."""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config import settings
from src.utils import get_logger
from src.core.database import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Agent Team API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Agent Team API...")


# Create FastAPI app
app = FastAPI(
    title="AI Agent Team API",
    description="API for managing AI agent development teams",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "AI Agent Team API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "services": {
            "api": "running",
            "database": "connected",  # TODO: Implement actual check
            "redis": "connected",     # TODO: Implement actual check
        }
    }


@app.post("/projects")
async def create_project(
    name: str,
    description: str,
    project_type: str = "web"
) -> Dict[str, Any]:
    """Create a new project."""
    from src.core.database.session import DatabaseManager
    
    try:
        project_id = DatabaseManager.create_project(name, description, project_type)
        return {
            "status": "success",
            "project_id": project_id,
            "message": f"Project '{name}' created successfully"
        }
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/sprints")
async def create_sprint(
    project_id: str,
    name: str,
    goal: str
) -> Dict[str, Any]:
    """Create a new sprint for a project."""
    from src.core.database.session import DatabaseManager
    
    try:
        sprint_id = DatabaseManager.create_sprint(project_id, name, goal)
        return {
            "status": "success",
            "sprint_id": sprint_id,
            "message": f"Sprint '{name}' created successfully"
        }
    except Exception as e:
        logger.error(f"Failed to create sprint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/register")
async def register_agent(
    agent_id: str,
    role: str,
    llm_provider: str
) -> Dict[str, str]:
    """Register a new agent."""
    from src.core.database.session import DatabaseManager
    
    try:
        DatabaseManager.register_agent(agent_id, role, llm_provider)
        return {
            "status": "success",
            "message": f"Agent '{agent_id}' registered successfully"
        }
    except Exception as e:
        logger.error(f"Failed to register agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def run_server():
    """Run the FastAPI server."""
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run_server()