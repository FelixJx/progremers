#!/usr/bin/env python3
"""Database setup script."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import init_db
from src.utils import get_logger

logger = get_logger(__name__)


def main():
    """Initialize database."""
    logger.info("Setting up database...")
    
    try:
        init_db()
        logger.info("Database setup completed successfully!")
        
        # Create initial agents
        from src.core.database.session import DatabaseManager
        
        logger.info("Creating initial agents...")
        
        agents = [
            ("manager-001", "manager", "deepseek"),
            ("pm-001", "pm", "deepseek"),
            ("arch-001", "architect", "qwen-max"),
            ("dev-001", "developer", "deepseek"),
            ("qa-001", "qa", "qwen-72b"),
            ("ui-001", "ui", "qwen-vl"),
            ("scrum-001", "scrum", "local"),
            ("reviewer-001", "reviewer", "deepseek"),
        ]
        
        for agent_id, role, llm_provider in agents:
            DatabaseManager.register_agent(agent_id, role, llm_provider)
            
        logger.info("Initial agents created successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()