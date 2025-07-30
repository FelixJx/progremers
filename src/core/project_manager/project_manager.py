"""Multi-project management system."""

import asyncio
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from src.core.database.session import get_db_context, DatabaseManager
from src.core.database.models import Project, ProjectStatus, Sprint, Agent
from src.core.memory import SprintMemoryManager
from src.utils import get_logger

logger = get_logger(__name__)


class ProjectPriority(str, Enum):
    """Project priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ProjectConfig:
    """Project configuration."""
    name: str
    description: str
    project_type: str
    tech_stack: Dict[str, str]
    team_config: Dict[str, Any]
    priority: ProjectPriority = ProjectPriority.MEDIUM
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class AgentAllocation:
    """Agent allocation to project."""
    agent_id: str
    role: str
    allocation_percentage: float  # 0.0 to 1.0
    start_date: datetime
    end_date: Optional[datetime] = None


class ProjectManager:
    """
    Manages multiple concurrent projects with agent allocation,
    resource scheduling, and project switching capabilities.
    """
    
    def __init__(self, memory_manager: SprintMemoryManager):
        self.memory_manager = memory_manager
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Active project tracking
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        self.agent_allocations: Dict[str, List[AgentAllocation]] = {}  # agent_id -> allocations
        self.project_priorities: Dict[str, ProjectPriority] = {}
        
        # Resource limits
        self.max_concurrent_projects = 10
        self.max_agents_per_project = 8
        self.agent_capacity_limits = {
            "manager": 3,    # Can manage up to 3 projects
            "pm": 2,         # Can handle 2 projects
            "architect": 2,  # Can architect 2 projects
            "developer": 1,  # Focus on 1 project at a time
            "qa": 2,         # Can test 2 projects
            "ui": 2,         # Can design for 2 projects
            "scrum": 5,      # Can facilitate 5 projects
            "reviewer": 3    # Can review for 3 projects
        }
    
    async def create_project(
        self,
        config: ProjectConfig,
        initial_team: Optional[List[str]] = None
    ) -> str:
        """
        Create a new project.
        
        Args:
            config: Project configuration
            initial_team: Initial team member agent IDs
            
        Returns:
            Project ID
        """
        
        self.logger.info(f"Creating project: {config.name}")
        
        # Check concurrent project limit
        if len(self.active_projects) >= self.max_concurrent_projects:
            raise ValueError(f"Maximum concurrent projects ({self.max_concurrent_projects}) reached")
        
        # Create project in database
        project_id = DatabaseManager.create_project(
            name=config.name,
            description=config.description,
            project_type=config.project_type
        )
        
        # Initialize project state
        project_state = {
            "id": project_id,
            "config": config,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "team_members": initial_team or [],
            "current_sprint": None,
            "resource_allocation": {},
            "context_cache": {}
        }
        
        self.active_projects[project_id] = project_state
        self.project_priorities[project_id] = config.priority
        
        # Allocate initial team if provided
        if initial_team:
            await self._allocate_team(project_id, initial_team)
        
        # Initialize project memory
        await self.memory_manager.initialize_sprint_memory(
            project_id=project_id,
            sprint_id="project_init",
            sprint_goal=f"Initialize project: {config.name}",
            initial_context={
                "project_type": config.project_type,
                "tech_stack": config.tech_stack,
                "team_config": config.team_config
            }
        )
        
        self.logger.info(f"Project created successfully: {project_id}")
        return project_id
    
    async def assign_agent_to_project(
        self,
        project_id: str,
        agent_id: str,
        allocation_percentage: float = 1.0,
        duration_days: Optional[int] = None
    ) -> bool:
        """
        Assign an agent to a project.
        
        Args:
            project_id: Project identifier
            agent_id: Agent identifier
            allocation_percentage: Percentage of agent's time (0.0-1.0)
            duration_days: Assignment duration in days
            
        Returns:
            True if assignment successful
        """
        
        if project_id not in self.active_projects:
            self.logger.error(f"Project not found: {project_id}")
            return False
        
        # Check agent capacity
        if not await self._check_agent_capacity(agent_id, allocation_percentage):
            self.logger.warning(f"Agent {agent_id} exceeds capacity with new allocation")
            return False
        
        # Check project team size limit
        current_team = self.active_projects[project_id]["team_members"]
        if len(current_team) >= self.max_agents_per_project:
            self.logger.warning(f"Project {project_id} has reached max team size")
            return False
        
        # Create allocation
        end_date = None
        if duration_days:
            end_date = datetime.utcnow().replace(day=datetime.utcnow().day + duration_days)
        
        allocation = AgentAllocation(
            agent_id=agent_id,
            role=await self._get_agent_role(agent_id),
            allocation_percentage=allocation_percentage,
            start_date=datetime.utcnow(),
            end_date=end_date
        )
        
        # Store allocation
        if agent_id not in self.agent_allocations:
            self.agent_allocations[agent_id] = []
        self.agent_allocations[agent_id].append(allocation)
        
        # Update project team
        if agent_id not in current_team:
            current_team.append(agent_id)
        
        # Update resource allocation
        self.active_projects[project_id]["resource_allocation"][agent_id] = allocation_percentage
        
        self.logger.info(f"Assigned {agent_id} to project {project_id} ({allocation_percentage:.0%})")
        return True
    
    async def remove_agent_from_project(
        self,
        project_id: str,
        agent_id: str
    ) -> bool:
        """Remove an agent from a project."""
        
        if project_id not in self.active_projects:
            return False
        
        # Remove from project team
        project_state = self.active_projects[project_id]
        if agent_id in project_state["team_members"]:
            project_state["team_members"].remove(agent_id)
        
        # Remove resource allocation
        if agent_id in project_state["resource_allocation"]:
            del project_state["resource_allocation"][agent_id]
        
        # End agent allocation
        if agent_id in self.agent_allocations:
            for allocation in self.agent_allocations[agent_id]:
                if allocation.end_date is None:  # Active allocation
                    allocation.end_date = datetime.utcnow()
        
        self.logger.info(f"Removed {agent_id} from project {project_id}")
        return True
    
    async def switch_project_context(
        self,
        agent_id: str,
        from_project_id: Optional[str],
        to_project_id: str
    ) -> bool:
        """
        Switch an agent's context between projects.
        
        Args:
            agent_id: Agent to switch
            from_project_id: Previous project (None if agent was idle)
            to_project_id: Target project
            
        Returns:
            True if switch successful
        """
        
        self.logger.info(f"Switching {agent_id}: {from_project_id} -> {to_project_id}")
        
        # Validate target project exists
        if to_project_id not in self.active_projects:
            self.logger.error(f"Target project not found: {to_project_id}")
            return False
        
        try:
            # Save current project state if switching from another project
            if from_project_id and from_project_id in self.active_projects:
                await self._save_agent_context(agent_id, from_project_id)
            
            # Load target project context
            await self._load_agent_context(agent_id, to_project_id)
            
            # Update agent's current project in database
            await self._update_agent_current_project(agent_id, to_project_id)
            
            self.logger.info(f"Successfully switched {agent_id} to project {to_project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to switch project context: {str(e)}")
            return False
    
    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive project status."""
        
        if project_id not in self.active_projects:
            return None
        
        project_state = self.active_projects[project_id]
        
        # Get team status
        team_status = {}
        for agent_id in project_state["team_members"]:
            allocation = self.agent_allocations.get(agent_id, [])
            active_allocation = next((a for a in allocation if a.end_date is None), None)
            
            team_status[agent_id] = {
                "role": active_allocation.role if active_allocation else "unknown",
                "allocation": active_allocation.allocation_percentage if active_allocation else 0.0,
                "status": await self._get_agent_status(agent_id)
            }
        
        # Get sprint information
        current_sprint = None
        if project_state["current_sprint"]:
            with get_db_context() as db:
                sprint = db.query(Sprint).filter_by(id=project_state["current_sprint"]).first()
                if sprint:
                    current_sprint = {
                        "id": str(sprint.id),
                        "name": sprint.name,
                        "goal": sprint.goal,
                        "status": sprint.status.value,
                        "start_date": sprint.start_date.isoformat() if sprint.start_date else None,
                        "end_date": sprint.end_date.isoformat() if sprint.end_date else None
                    }
        
        # Calculate project health metrics
        health_metrics = await self._calculate_project_health(project_id)
        
        return {
            "project_id": project_id,
            "name": project_state["config"].name,
            "status": project_state["status"],
            "priority": self.project_priorities[project_id].value,
            "created_at": project_state["created_at"],
            "team_status": team_status,
            "current_sprint": current_sprint,
            "health_metrics": health_metrics,
            "resource_utilization": self._calculate_resource_utilization(project_id)
        }
    
    async def list_active_projects(self) -> List[Dict[str, Any]]:
        """List all active projects with summary information."""
        
        projects = []
        
        for project_id in self.active_projects:
            status = await self.get_project_status(project_id)
            if status:
                # Add summary information
                summary = {
                    "project_id": project_id,
                    "name": status["name"],
                    "priority": status["priority"],
                    "team_size": len(status["team_status"]),
                    "health_score": status["health_metrics"]["overall_score"],
                    "resource_utilization": status["resource_utilization"]["total_utilization"]
                }
                projects.append(summary)
        
        # Sort by priority and health
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        projects.sort(
            key=lambda p: (
                priority_order.get(p["priority"], 4),
                -p["health_score"]  # Higher health score first
            )
        )
        
        return projects
    
    async def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get agent's current workload across all projects."""
        
        allocations = self.agent_allocations.get(agent_id, [])
        active_allocations = [a for a in allocations if a.end_date is None]
        
        total_allocation = sum(a.allocation_percentage for a in active_allocations)
        
        workload = {
            "agent_id": agent_id,
            "total_allocation": total_allocation,
            "capacity_utilization": total_allocation,
            "is_overallocated": total_allocation > 1.0,
            "projects": []
        }
        
        for allocation in active_allocations:
            # Find project for this allocation
            project_info = None
            for pid, pstate in self.active_projects.items():
                if agent_id in pstate["team_members"]:
                    project_info = {
                        "project_id": pid,
                        "project_name": pstate["config"].name,
                        "allocation_percentage": allocation.allocation_percentage,
                        "role": allocation.role,
                        "start_date": allocation.start_date.isoformat()
                    }
                    break
            
            if project_info:
                workload["projects"].append(project_info)
        
        return workload
    
    async def optimize_resource_allocation(self) -> Dict[str, Any]:
        """Optimize agent allocation across projects."""
        
        self.logger.info("Optimizing resource allocation across projects")
        
        optimization_results = {
            "reallocation_suggestions": [],
            "overallocated_agents": [],
            "underutilized_agents": [],
            "project_resource_gaps": []
        }
        
        # Check for overallocated agents
        for agent_id in self.agent_allocations:
            workload = await self.get_agent_workload(agent_id)
            
            if workload["is_overallocated"]:
                optimization_results["overallocated_agents"].append({
                    "agent_id": agent_id,
                    "total_allocation": workload["total_allocation"],
                    "excess_allocation": workload["total_allocation"] - 1.0,
                    "projects": workload["projects"]
                })
            elif workload["total_allocation"] < 0.7:  # Less than 70% utilized
                optimization_results["underutilized_agents"].append({
                    "agent_id": agent_id,
                    "available_capacity": 1.0 - workload["total_allocation"],
                    "current_projects": len(workload["projects"])
                })
        
        # Check for project resource gaps
        for project_id, project_state in self.active_projects.items():
            required_roles = self._get_required_roles(project_state["config"])
            current_roles = set()
            
            for agent_id in project_state["team_members"]:
                role = await self._get_agent_role(agent_id)
                current_roles.add(role)
            
            missing_roles = required_roles - current_roles
            if missing_roles:
                optimization_results["project_resource_gaps"].append({
                    "project_id": project_id,
                    "project_name": project_state["config"].name,
                    "missing_roles": list(missing_roles),
                    "priority": self.project_priorities[project_id].value
                })
        
        # Generate reallocation suggestions
        await self._generate_reallocation_suggestions(optimization_results)
        
        return optimization_results
    
    async def pause_project(self, project_id: str, reason: str) -> bool:
        """Pause a project and free up its resources."""
        
        if project_id not in self.active_projects:
            return False
        
        self.logger.info(f"Pausing project {project_id}: {reason}")
        
        try:
            # Save current state
            project_state = self.active_projects[project_id]
            project_state["status"] = "paused"
            project_state["pause_reason"] = reason
            project_state["paused_at"] = datetime.utcnow().isoformat()
            
            # Save all agent contexts
            for agent_id in project_state["team_members"]:
                await self._save_agent_context(agent_id, project_id)
            
            # Update database
            with get_db_context() as db:
                project = db.query(Project).filter_by(id=project_id).first()
                if project:
                    project.status = ProjectStatus.PAUSED
            
            self.logger.info(f"Project {project_id} paused successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause project {project_id}: {str(e)}")
            return False
    
    async def resume_project(self, project_id: str) -> bool:
        """Resume a paused project."""
        
        if project_id not in self.active_projects:
            return False
        
        project_state = self.active_projects[project_id]
        if project_state["status"] != "paused":
            return False
        
        self.logger.info(f"Resuming project {project_id}")
        
        try:
            # Restore project state
            project_state["status"] = "active"
            project_state["resumed_at"] = datetime.utcnow().isoformat()
            
            # Check if team members are available
            available_agents = []
            for agent_id in project_state["team_members"]:
                workload = await self.get_agent_workload(agent_id)
                if workload["total_allocation"] < 1.0:  # Has capacity
                    available_agents.append(agent_id)
            
            # Restore contexts for available agents
            for agent_id in available_agents:
                await self._load_agent_context(agent_id, project_id)
            
            # Update database
            with get_db_context() as db:
                project = db.query(Project).filter_by(id=project_id).first()
                if project:
                    project.status = ProjectStatus.ACTIVE
            
            self.logger.info(f"Project {project_id} resumed with {len(available_agents)} agents")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume project {project_id}: {str(e)}")
            return False
    
    # Private helper methods
    
    async def _allocate_team(self, project_id: str, agent_ids: List[str]) -> None:
        """Allocate initial team to project."""
        
        for agent_id in agent_ids:
            await self.assign_agent_to_project(project_id, agent_id, 1.0)
    
    async def _check_agent_capacity(self, agent_id: str, additional_allocation: float) -> bool:
        """Check if agent has capacity for additional allocation."""
        
        current_workload = await self.get_agent_workload(agent_id)
        new_total = current_workload["total_allocation"] + additional_allocation
        
        # Get agent role to check role-specific limits
        role = await self._get_agent_role(agent_id)
        role_limit = self.agent_capacity_limits.get(role, 1.0)
        
        return new_total <= role_limit
    
    async def _get_agent_role(self, agent_id: str) -> str:
        """Get agent role from database."""
        
        with get_db_context() as db:
            agent = db.query(Agent).filter_by(id=agent_id).first()
            return agent.role if agent else "unknown"
    
    async def _get_agent_status(self, agent_id: str) -> str:
        """Get current agent status."""
        
        with get_db_context() as db:
            agent = db.query(Agent).filter_by(id=agent_id).first()
            return agent.current_status if agent else "unknown"
    
    async def _save_agent_context(self, agent_id: str, project_id: str) -> None:
        """Save agent's current context for a project."""
        
        # This would integrate with the memory system to save agent state
        # For now, just log the operation
        self.logger.info(f"Saving context for {agent_id} in project {project_id}")
    
    async def _load_agent_context(self, agent_id: str, project_id: str) -> None:
        """Load agent's context for a project."""
        
        # This would restore agent context from memory system
        self.logger.info(f"Loading context for {agent_id} in project {project_id}")
    
    async def _update_agent_current_project(self, agent_id: str, project_id: str) -> None:
        """Update agent's current project in database."""
        
        with get_db_context() as db:
            agent = db.query(Agent).filter_by(id=agent_id).first()
            if agent:
                agent.current_project_id = project_id
    
    async def _calculate_project_health(self, project_id: str) -> Dict[str, Any]:
        """Calculate project health metrics."""
        
        # Mock implementation - would calculate real metrics
        return {
            "overall_score": 0.85,
            "team_velocity": 0.9,
            "quality_score": 0.8,
            "timeline_adherence": 0.7,
            "resource_efficiency": 0.9
        }
    
    def _calculate_resource_utilization(self, project_id: str) -> Dict[str, Any]:
        """Calculate resource utilization for project."""
        
        project_state = self.active_projects[project_id]
        allocations = project_state.get("resource_allocation", {})
        
        total_allocation = sum(allocations.values())
        
        return {
            "total_utilization": total_allocation,
            "agent_count": len(allocations),
            "average_allocation": total_allocation / len(allocations) if allocations else 0.0,
            "utilization_efficiency": min(1.0, total_allocation / len(allocations)) if allocations else 0.0
        }
    
    def _get_required_roles(self, project_config: ProjectConfig) -> Set[str]:
        """Get required roles for a project type."""
        
        base_roles = {"manager", "pm", "developer", "qa"}
        
        if project_config.project_type in ["web", "mobile"]:
            base_roles.add("ui")
        
        if project_config.project_type in ["enterprise", "large"]:
            base_roles.add("architect")
            base_roles.add("reviewer")
        
        return base_roles
    
    async def _generate_reallocation_suggestions(self, optimization_results: Dict[str, Any]) -> None:
        """Generate suggestions for resource reallocation."""
        
        suggestions = []
        
        # Match underutilized agents with projects needing resources
        underutilized = optimization_results["underutilized_agents"]
        resource_gaps = optimization_results["project_resource_gaps"]
        
        for gap in resource_gaps:
            for missing_role in gap["missing_roles"]:
                # Find underutilized agents with this role
                suitable_agents = []
                for agent_info in underutilized:
                    agent_id = agent_info["agent_id"]
                    agent_role = await self._get_agent_role(agent_id)
                    
                    if agent_role == missing_role:
                        suitable_agents.append({
                            "agent_id": agent_id,
                            "available_capacity": agent_info["available_capacity"]
                        })
                
                if suitable_agents:
                    # Suggest the agent with most capacity
                    best_agent = max(suitable_agents, key=lambda a: a["available_capacity"])
                    
                    suggestions.append({
                        "type": "assign_agent",
                        "agent_id": best_agent["agent_id"],
                        "target_project": gap["project_id"],
                        "role": missing_role,
                        "allocation": min(0.5, best_agent["available_capacity"]),
                        "priority": gap["priority"],
                        "reason": f"Fill missing {missing_role} role"
                    })
        
        optimization_results["reallocation_suggestions"] = suggestions