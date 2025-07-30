"""Project context management and switching."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from src.core.memory import SprintMemoryManager
from src.core.memory.context_compressor import ContextCompressor, CompressionStrategy
from src.utils import get_logger

logger = get_logger(__name__)


@dataclass
class ProjectContext:
    """
    Encapsulates all context information for a project.
    """
    project_id: str
    project_name: str
    project_type: str
    tech_stack: Dict[str, str]
    current_sprint_id: Optional[str]
    sprint_goal: Optional[str]
    team_members: List[str]
    key_decisions: List[Dict[str, Any]]
    active_blockers: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    knowledge_base: Dict[str, Any]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectContext':
        """Create from dictionary."""
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)
    
    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if context is stale and needs refresh."""
        age = datetime.utcnow() - self.last_updated
        return age.total_seconds() > (max_age_hours * 3600)


class ProjectSwitcher:
    """
    Handles seamless switching between project contexts for agents.
    
    Manages context saving, loading, and compression to ensure agents
    can switch between projects without losing important information.
    """
    
    def __init__(self, memory_manager: SprintMemoryManager):
        self.memory_manager = memory_manager
        self.context_compressor = ContextCompressor()
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Context cache to avoid repeated loading
        self.context_cache: Dict[str, ProjectContext] = {}
        self.agent_contexts: Dict[str, str] = {}  # agent_id -> current_project_id
        
        # Switching statistics
        self.switch_stats = {
            "total_switches": 0,
            "successful_switches": 0,
            "failed_switches": 0,
            "average_switch_time": 0.0
        }
    
    async def switch_agent_to_project(
        self,
        agent_id: str,
        target_project_id: str,
        agent_role: str,
        preserve_working_memory: bool = True
    ) -> bool:
        """
        Switch an agent to a different project context.
        
        Args:
            agent_id: Agent to switch
            target_project_id: Target project
            agent_role: Agent's role for context customization
            preserve_working_memory: Whether to preserve working memory
            
        Returns:
            True if switch successful
        """
        
        start_time = datetime.utcnow()
        self.switch_stats["total_switches"] += 1
        
        current_project_id = self.agent_contexts.get(agent_id)
        
        self.logger.info(f"Switching {agent_id} from {current_project_id} to {target_project_id}")
        
        try:
            # Step 1: Save current project context if switching from another project
            if current_project_id and current_project_id != target_project_id:
                await self._save_agent_working_memory(
                    agent_id, current_project_id, preserve_working_memory
                )
            
            # Step 2: Load target project context
            target_context = await self._load_project_context(target_project_id)
            if not target_context:
                self.logger.error(f"Failed to load context for project {target_project_id}")
                return False
            
            # Step 3: Customize context for agent role
            customized_context = await self._customize_context_for_agent(
                target_context, agent_id, agent_role
            )
            
            # Step 4: Compress context if needed
            compressed_context = await self.context_compressor.compress_context(
                customized_context,
                target_tokens=3000,  # Adjust based on LLM limits
                strategy=CompressionStrategy.HIERARCHICAL
            )
            
            # Step 5: Update agent's current project
            self.agent_contexts[agent_id] = target_project_id
            
            # Step 6: Cache the context for quick access
            self.context_cache[target_project_id] = target_context
            
            # Update statistics
            switch_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_switch_stats(True, switch_time)
            
            self.logger.info(f"Successfully switched {agent_id} to project {target_project_id} in {switch_time:.2f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to switch {agent_id} to project {target_project_id}: {str(e)}")
            self._update_switch_stats(False, 0)
            return False
    
    async def get_agent_context(
        self,
        agent_id: str,
        agent_role: str,
        max_tokens: int = 3000
    ) -> Optional[Dict[str, Any]]:
        """
        Get current context for an agent.
        
        Args:
            agent_id: Agent identifier
            agent_role: Agent's role
            max_tokens: Maximum context tokens
            
        Returns:
            Agent's current context
        """
        
        current_project_id = self.agent_contexts.get(agent_id)
        if not current_project_id:
            return None
        
        # Load project context
        project_context = await self._load_project_context(current_project_id)
        if not project_context:
            return None
        
        # Customize for agent
        customized_context = await self._customize_context_for_agent(
            project_context, agent_id, agent_role
        )
        
        # Compress if needed
        if max_tokens:
            customized_context = await self.context_compressor.compress_context(
                customized_context,
                target_tokens=max_tokens,
                strategy=CompressionStrategy.HIERARCHICAL
            )
        
        return customized_context
    
    async def refresh_project_context(self, project_id: str) -> bool:
        """Refresh cached project context."""
        
        try:
            # Remove from cache to force reload
            if project_id in self.context_cache:
                del self.context_cache[project_id]
            
            # Reload context
            context = await self._load_project_context(project_id, force_reload=True)
            return context is not None
            
        except Exception as e:
            self.logger.error(f"Failed to refresh context for project {project_id}: {str(e)}")
            return False
    
    async def get_context_summary(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of project context."""
        
        context = await self._load_project_context(project_id)
        if not context:
            return None
        
        return {
            "project_id": project_id,
            "project_name": context.project_name,
            "sprint_goal": context.sprint_goal,
            "team_size": len(context.team_members),
            "decisions_count": len(context.key_decisions),
            "blockers_count": len(context.active_blockers),
            "last_updated": context.last_updated.isoformat(),
            "is_stale": context.is_stale()
        }
    
    async def cleanup_stale_contexts(self, max_age_hours: int = 24) -> int:
        """Clean up stale contexts from cache."""
        
        removed_count = 0
        stale_projects = []
        
        for project_id, context in self.context_cache.items():
            if context.is_stale(max_age_hours):
                stale_projects.append(project_id)
        
        for project_id in stale_projects:
            del self.context_cache[project_id]
            removed_count += 1
        
        self.logger.info(f"Cleaned up {removed_count} stale contexts")
        return removed_count
    
    async def get_switching_stats(self) -> Dict[str, Any]:
        """Get context switching statistics."""
        
        return {
            **self.switch_stats,
            "cached_contexts": len(self.context_cache),
            "active_agent_contexts": len(self.agent_contexts),
            "success_rate": (
                self.switch_stats["successful_switches"] / 
                max(1, self.switch_stats["total_switches"])
            )
        }
    
    # Private helper methods
    
    async def _load_project_context(
        self,
        project_id: str,
        force_reload: bool = False
    ) -> Optional[ProjectContext]:
        """Load project context from memory system."""
        
        # Check cache first
        if not force_reload and project_id in self.context_cache:
            cached_context = self.context_cache[project_id]
            if not cached_context.is_stale():
                return cached_context
        
        try:
            # Load from memory system
            sprint_memories = await self.memory_manager.retrieve_memory(
                project_id=project_id,
                sprint_id=None,  # Get all sprints
                max_tokens=5000  # More tokens for loading
            )
            
            # Extract project information
            project_info = await self._extract_project_info(project_id, sprint_memories)
            
            if not project_info:
                return None
            
            # Create context object
            context = ProjectContext(
                project_id=project_id,
                project_name=project_info.get("name", f"Project {project_id}"),
                project_type=project_info.get("type", "unknown"),
                tech_stack=project_info.get("tech_stack", {}),
                current_sprint_id=project_info.get("current_sprint_id"),
                sprint_goal=project_info.get("sprint_goal"),
                team_members=project_info.get("team_members", []),
                key_decisions=project_info.get("key_decisions", []),
                active_blockers=project_info.get("active_blockers", []),
                recent_activities=project_info.get("recent_activities", []),
                knowledge_base=project_info.get("knowledge_base", {}),
                last_updated=datetime.utcnow()
            )
            
            # Cache the context
            self.context_cache[project_id] = context
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to load project context {project_id}: {str(e)}")
            return None
    
    async def _extract_project_info(
        self,
        project_id: str,
        memories: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract project information from memories."""
        
        # This would integrate with the database and memory system
        # For now, return mock data
        
        return {
            "name": f"Project {project_id}",
            "type": "web",
            "tech_stack": {"frontend": "React", "backend": "Node.js"},
            "current_sprint_id": f"sprint-{project_id}-1",
            "sprint_goal": "Implement core functionality",
            "team_members": ["dev-001", "qa-001", "pm-001"],
            "key_decisions": [
                {
                    "id": "decision-1",
                    "description": "Choose React for frontend",
                    "rationale": "Team expertise and component reusability",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "active_blockers": [],
            "recent_activities": [
                {
                    "type": "code_commit",
                    "description": "Initial project setup",
                    "agent": "dev-001",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "knowledge_base": {
                "patterns": [],
                "lessons_learned": []
            }
        }
    
    async def _customize_context_for_agent(
        self,
        context: ProjectContext,
        agent_id: str,
        agent_role: str
    ) -> Dict[str, Any]:
        """Customize context based on agent role."""
        
        base_context = context.to_dict()
        
        # Role-specific customizations
        if agent_role == "pm":
            # PM needs requirements and user story context
            base_context["focus_areas"] = ["requirements", "user_stories", "priorities"]
            base_context["relevant_decisions"] = [
                d for d in context.key_decisions 
                if "requirement" in d.get("description", "").lower()
            ]
        
        elif agent_role == "developer":
            # Developers need technical context
            base_context["focus_areas"] = ["tech_stack", "architecture", "code_patterns"]
            base_context["relevant_decisions"] = [
                d for d in context.key_decisions 
                if any(tech in d.get("description", "").lower() 
                      for tech in ["technical", "architecture", "code"])
            ]
        
        elif agent_role == "qa":
            # QA needs testing context
            base_context["focus_areas"] = ["quality_standards", "test_cases", "bugs"]
            base_context["relevant_blockers"] = [
                b for b in context.active_blockers
                if "test" in b.get("description", "").lower()
            ]
        
        elif agent_role == "ui":
            # UI designers need design context
            base_context["focus_areas"] = ["user_experience", "design_system", "mockups"]
        
        # Add agent-specific working memory
        base_context["agent_context"] = {
            "agent_id": agent_id,
            "role": agent_role,
            "last_switched": datetime.utcnow().isoformat(),
            "working_memory": await self._get_agent_working_memory(agent_id, context.project_id)
        }
        
        return base_context
    
    async def _save_agent_working_memory(
        self,
        agent_id: str,
        project_id: str,
        preserve: bool
    ) -> None:
        """Save agent's working memory for the project."""
        
        if not preserve:
            return
        
        # This would save agent's current working state
        # For now, just log
        self.logger.info(f"Saving working memory for {agent_id} in project {project_id}")
    
    async def _get_agent_working_memory(
        self,
        agent_id: str,
        project_id: str
    ) -> Dict[str, Any]:
        """Get agent's working memory for the project."""
        
        # This would retrieve agent's working memory
        # For now, return empty
        return {}
    
    def _update_switch_stats(self, success: bool, switch_time: float) -> None:
        """Update switching statistics."""
        
        if success:
            self.switch_stats["successful_switches"] += 1
        else:
            self.switch_stats["failed_switches"] += 1
        
        # Update average switch time
        total_successful = self.switch_stats["successful_switches"]
        if total_successful > 0:
            current_avg = self.switch_stats["average_switch_time"]
            self.switch_stats["average_switch_time"] = (
                (current_avg * (total_successful - 1) + switch_time) / total_successful
            )


class ProjectContextManager:
    """
    High-level manager for project context operations.
    """
    
    def __init__(self, memory_manager: SprintMemoryManager):
        self.memory_manager = memory_manager
        self.project_switcher = ProjectSwitcher(memory_manager)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    async def initialize_project_context(
        self,
        project_id: str,
        project_config: Dict[str, Any]
    ) -> bool:
        """Initialize context for a new project."""
        
        try:
            # Initialize sprint memory
            await self.memory_manager.initialize_sprint_memory(
                project_id=project_id,
                sprint_id="project_init",
                sprint_goal=f"Initialize {project_config.get('name', 'project')}",
                initial_context=project_config
            )
            
            self.logger.info(f"Initialized context for project {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize project context: {str(e)}")
            return False
    
    async def archive_project_context(self, project_id: str) -> bool:
        """Archive project context when project completes."""
        
        try:
            # This would archive all project memories
            self.logger.info(f"Archiving context for project {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to archive project context: {str(e)}")
            return False
    
    async def clone_project_context(
        self,
        source_project_id: str,
        target_project_id: str,
        elements_to_clone: List[str]
    ) -> bool:
        """Clone context elements from one project to another."""
        
        try:
            # Load source context
            source_context = await self.project_switcher._load_project_context(source_project_id)
            if not source_context:
                return False
            
            # Clone specified elements
            cloned_data = {}
            
            if "tech_stack" in elements_to_clone:
                cloned_data["tech_stack"] = source_context.tech_stack
            
            if "key_decisions" in elements_to_clone:
                cloned_data["key_decisions"] = source_context.key_decisions
            
            if "knowledge_base" in elements_to_clone:
                cloned_data["knowledge_base"] = source_context.knowledge_base
            
            # Initialize target project with cloned data
            await self.initialize_project_context(target_project_id, cloned_data)
            
            self.logger.info(f"Cloned context from {source_project_id} to {target_project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clone project context: {str(e)}")
            return False