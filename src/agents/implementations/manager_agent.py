"""Manager Agent - Orchestrates the development team."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from src.agents.base import BaseAgent, AgentRole, AgentStatus, AgentContext, AgentMessage
from src.utils import get_logger
from src.config import settings

logger = get_logger(__name__)


class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConflictType(str, Enum):
    """Types of conflicts between agents."""
    TECHNICAL = "technical"
    PRIORITY = "priority"
    APPROACH = "approach"
    RESOURCE = "resource"
    TIMELINE = "timeline"


class ManagerAgent(BaseAgent):
    """
    Manager Agent - The central coordinator of the development team.
    
    Responsibilities:
    - Task assignment and scheduling
    - Work quality validation
    - Conflict resolution
    - Progress monitoring
    - Sprint coordination
    """
    
    def __init__(self, agent_id: str = "manager-001"):
        super().__init__(agent_id, AgentRole.MANAGER)
        
        # Manager state
        self.team_agents: Dict[str, BaseAgent] = {}
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.quality_standards: Dict[str, Dict[str, Any]] = {}
        self.conflict_history: List[Dict[str, Any]] = []
        self.project_plans: Dict[str, Dict[str, Any]] = {}
        
        # Initialize quality standards
        self._initialize_quality_standards()
    
    def _initialize_quality_standards(self) -> None:
        """Initialize quality standards for different agent outputs."""
        self.quality_standards = {
            "pm": {
                "required_fields": ["user_stories", "acceptance_criteria", "priority"],
                "min_story_count": 3,
                "clarity_threshold": 0.8
            },
            "architect": {
                "required_fields": ["tech_stack", "architecture_diagram", "api_design"],
                "scalability_score": 0.7,
                "security_considerations": True
            },
            "developer": {
                "required_fields": ["code", "tests", "documentation"],
                "test_coverage": 0.8,
                "code_quality_score": 0.85
            },
            "qa": {
                "required_fields": ["test_cases", "test_results", "bug_report"],
                "test_coverage": 0.9,
                "pass_rate": 0.95
            },
            "ui": {
                "required_fields": ["design_specs", "components", "style_guide"],
                "accessibility_score": 0.8,
                "responsiveness": True
            }
        }
    
    async def process_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Process a management task.
        
        Args:
            task: Management task details
            context: Current context
            
        Returns:
            Task processing result
        """
        task_type = task.get("type", "coordinate")
        
        self.logger.info(f"Processing management task: {task_type}")
        
        try:
            if task_type == "coordinate":
                return await self._coordinate_team(task, context)
            elif task_type == "validate":
                return await self._validate_work(task, context)
            elif task_type == "resolve_conflict":
                return await self._resolve_conflict(task, context)
            elif task_type == "assign_task":
                return await self._assign_task(task, context)
            elif task_type == "sprint_planning":
                return await self._conduct_sprint_planning(task, context)
            elif task_type == "project_planning":
                return await self._conduct_project_planning(task, context)
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _coordinate_team(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Coordinate team activities."""
        project_id = context.project_id
        coordination_type = task.get("coordination_type", "daily_standup")
        
        if coordination_type == "daily_standup":
            # Gather status from all agents
            agent_statuses = await self._gather_agent_statuses()
            
            # Identify blockers and priorities
            blockers = self._identify_blockers(agent_statuses)
            next_priorities = self._determine_priorities(agent_statuses, context)
            
            return {
                "status": "success",
                "coordination_result": {
                    "type": "daily_standup",
                    "agent_statuses": agent_statuses,
                    "blockers": blockers,
                    "priorities": next_priorities,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        
        return {"status": "success", "message": "Team coordination completed"}
    
    async def _validate_work(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Validate work output from an agent."""
        agent_id = task.get("agent_id")
        output = task.get("output", {})
        agent_role = task.get("agent_role", "").lower()
        
        if not agent_id or not output:
            return {"status": "error", "message": "Missing agent_id or output"}
        
        # Get quality standards for this agent role
        standards = self.quality_standards.get(agent_role, {})
        validation_result = await self._perform_validation(output, standards, agent_role)
        
        # Log validation result
        self.logger.info(f"Validation result for {agent_id}: {validation_result['score']}")
        
        # Store validation in database
        await self._store_validation_result(agent_id, output, validation_result, context)
        
        return {
            "status": "success",
            "validation_result": validation_result,
            "approved": validation_result["score"] >= 0.8
        }
    
    async def _perform_validation(
        self,
        output: Dict[str, Any],
        standards: Dict[str, Any],
        agent_role: str
    ) -> Dict[str, Any]:
        """Perform detailed validation of agent output."""
        validation_score = 0.0
        validation_details = []
        max_score = 0.0
        
        # Check required fields
        required_fields = standards.get("required_fields", [])
        if required_fields:
            field_score = 0
            for field in required_fields:
                if field in output and output[field]:
                    field_score += 1
                    validation_details.append(f"✅ Required field '{field}' present")
                else:
                    validation_details.append(f"❌ Missing required field '{field}'")
            
            field_percentage = field_score / len(required_fields)
            validation_score += field_percentage * 0.4  # 40% weight for required fields
            max_score += 0.4
        
        # Role-specific validations
        if agent_role == "pm":
            story_count = len(output.get("user_stories", []))
            min_stories = standards.get("min_story_count", 3)
            if story_count >= min_stories:
                validation_score += 0.3
                validation_details.append(f"✅ Sufficient user stories ({story_count})")
            else:
                validation_details.append(f"❌ Insufficient user stories ({story_count} < {min_stories})")
            max_score += 0.3
            
        elif agent_role == "developer":
            # Check test coverage
            test_coverage = output.get("test_coverage", 0)
            min_coverage = standards.get("test_coverage", 0.8)
            if test_coverage >= min_coverage:
                validation_score += 0.3
                validation_details.append(f"✅ Good test coverage ({test_coverage:.1%})")
            else:
                validation_details.append(f"❌ Low test coverage ({test_coverage:.1%} < {min_coverage:.1%})")
            max_score += 0.3
            
        elif agent_role == "qa":
            # Check pass rate
            pass_rate = output.get("pass_rate", 0)
            min_pass_rate = standards.get("pass_rate", 0.95)
            if pass_rate >= min_pass_rate:
                validation_score += 0.3
                validation_details.append(f"✅ High pass rate ({pass_rate:.1%})")
            else:
                validation_details.append(f"❌ Low pass rate ({pass_rate:.1%} < {min_pass_rate:.1%})")
            max_score += 0.3
        
        # General quality check (using AI)
        general_quality = await self._assess_general_quality(output, agent_role)
        validation_score += general_quality * 0.3
        max_score += 0.3
        validation_details.append(f"General quality score: {general_quality:.2f}")
        
        # Normalize score
        final_score = validation_score / max_score if max_score > 0 else 0
        
        return {
            "score": final_score,
            "details": validation_details,
            "pass": final_score >= 0.8,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _assess_general_quality(self, output: Dict[str, Any], agent_role: str) -> float:
        """Use AI to assess general quality of output."""
        # This would use the LLM to assess quality
        # For now, return a mock score based on output completeness
        
        if not output:
            return 0.0
        
        # Simple heuristic: more complete outputs score higher
        completeness = len([v for v in output.values() if v]) / len(output) if output else 0
        return min(1.0, completeness + 0.2)  # Add small bonus
    
    async def _resolve_conflict(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Resolve conflicts between agents."""
        conflict = task.get("conflict", {})
        agent1_id = conflict.get("agent1_id")
        agent2_id = conflict.get("agent2_id")
        conflict_type = ConflictType(conflict.get("type", "approach"))
        description = conflict.get("description", "")
        
        self.logger.info(f"Resolving conflict between {agent1_id} and {agent2_id}: {conflict_type}")
        
        # Try rule-based resolution first
        resolution = await self._apply_conflict_rules(conflict, context)
        
        if not resolution:
            # Use AI-based resolution
            resolution = await self._ai_conflict_resolution(conflict, context)
        
        # Store conflict resolution
        conflict_record = {
            "agent1_id": agent1_id,
            "agent2_id": agent2_id,
            "type": conflict_type.value,
            "description": description,
            "resolution": resolution,
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": context.project_id
        }
        
        self.conflict_history.append(conflict_record)
        
        return {
            "status": "success",
            "conflict_resolution": conflict_record
        }
    
    async def _apply_conflict_rules(self, conflict: Dict[str, Any], context: AgentContext) -> Optional[Dict[str, Any]]:
        """Apply predefined rules for conflict resolution."""
        conflict_type = ConflictType(conflict.get("type", "approach"))
        
        # Predefined resolution rules
        if conflict_type == ConflictType.PRIORITY:
            return {
                "decision": "Defer to PM Agent for priority decisions",
                "rationale": "PM Agent has primary responsibility for prioritization",
                "method": "rule_based"
            }
        
        elif conflict_type == ConflictType.TECHNICAL:
            return {
                "decision": "Defer to Architect Agent for technical decisions",
                "rationale": "Architect Agent has primary responsibility for technical architecture",
                "method": "rule_based"
            }
        
        return None
    
    async def _ai_conflict_resolution(self, conflict: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Use AI to resolve complex conflicts."""
        # This would use the LLM to analyze and resolve conflicts
        # For now, return a generic resolution
        
        return {
            "decision": "Compromise solution needed - both agents should collaborate",
            "rationale": "Complex conflicts require collaborative approach",
            "method": "ai_mediated",
            "next_steps": [
                "Schedule joint meeting",
                "Define shared objectives",
                "Create compromise implementation plan"
            ]
        }
    
    async def _assign_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Assign a task to the most suitable agent."""
        task_details = task.get("task_details", {})
        task_type = task_details.get("type", "")
        priority = TaskPriority(task.get("priority", "medium"))
        
        # Determine best agent for this task
        assigned_agent = self._select_agent_for_task(task_type, task_details)
        
        if not assigned_agent:
            return {"status": "error", "message": "No suitable agent found"}
        
        # Create task assignment
        assignment = {
            "task_id": task.get("task_id", f"task-{datetime.utcnow().timestamp()}"),
            "assigned_to": assigned_agent,
            "task_details": task_details,
            "priority": priority.value,
            "assigned_at": datetime.utcnow().isoformat(),
            "deadline": task.get("deadline"),
            "project_id": context.project_id
        }
        
        self.active_tasks[assignment["task_id"]] = assignment
        
        self.logger.info(f"Assigned task {assignment['task_id']} to {assigned_agent}")
        
        return {
            "status": "success",
            "assignment": assignment
        }
    
    def _select_agent_for_task(self, task_type: str, task_details: Dict[str, Any]) -> Optional[str]:
        """Select the most suitable agent for a task."""
        task_agent_mapping = {
            "requirements": "pm-001",
            "architecture": "arch-001", 
            "development": "dev-001",
            "testing": "qa-001",
            "ui_design": "ui-001",
            "code_review": "reviewer-001"
        }
        
        return task_agent_mapping.get(task_type)
    
    async def _conduct_sprint_planning(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Conduct sprint planning meeting."""
        sprint_goal = task.get("sprint_goal", "")
        user_stories = task.get("user_stories", [])
        
        # Generate sprint plan
        sprint_plan = {
            "sprint_id": f"sprint-{context.project_id}-{datetime.utcnow().timestamp()}",
            "goal": sprint_goal,
            "stories": user_stories,
            "assignments": {},
            "timeline": self._create_sprint_timeline(user_stories),
            "risks": self._identify_sprint_risks(user_stories),
            "success_criteria": self._define_success_criteria(sprint_goal, user_stories)
        }
        
        # Assign stories to agents
        for story in user_stories:
            agent_id = self._select_agent_for_task(story.get("type", "development"), story)
            if agent_id:
                if agent_id not in sprint_plan["assignments"]:
                    sprint_plan["assignments"][agent_id] = []
                sprint_plan["assignments"][agent_id].append(story)
        
        return {
            "status": "success",
            "sprint_plan": sprint_plan
        }
    
    def _create_sprint_timeline(self, user_stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create timeline for sprint stories."""
        # Simple timeline based on story points
        total_points = sum(story.get("points", 1) for story in user_stories)
        sprint_days = 10  # 2-week sprint
        
        return {
            "total_story_points": total_points,
            "sprint_duration_days": sprint_days,
            "daily_velocity": total_points / sprint_days,
            "milestones": [
                {"day": 3, "target": "Requirements finalized"},
                {"day": 6, "target": "Development 50% complete"},
                {"day": 9, "target": "Testing complete"},
                {"day": 10, "target": "Sprint review ready"}
            ]
        }
    
    def _identify_sprint_risks(self, user_stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential risks in the sprint."""
        risks = []
        
        # Check for high-complexity stories
        complex_stories = [s for s in user_stories if s.get("points", 1) >= 8]
        if complex_stories:
            risks.append({
                "type": "complexity",
                "description": f"{len(complex_stories)} high-complexity stories may cause delays",
                "mitigation": "Break down complex stories, add buffer time"
            })
        
        # Check for dependency chains
        if len(user_stories) > 5:
            risks.append({
                "type": "scope",
                "description": "Large number of stories may be ambitious for one sprint",
                "mitigation": "Prioritize must-have features, defer nice-to-haves"
            })
        
        return risks
    
    def _define_success_criteria(self, sprint_goal: str, user_stories: List[Dict[str, Any]]) -> List[str]:
        """Define success criteria for the sprint."""
        criteria = [
            f"Sprint goal achieved: {sprint_goal}",
            f"All {len(user_stories)} user stories completed",
            "No critical bugs in production",
            "All acceptance criteria met",
            "Code review approval for all changes"
        ]
        
        return criteria
    
    async def _gather_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Gather current status from all team agents."""
        # In real implementation, this would query each agent
        # For now, return mock data
        
        return {
            "pm-001": {
                "status": "working",
                "current_task": "Refining user stories for sprint 2",
                "progress": 0.75,
                "blockers": [],
                "estimated_completion": "2024-01-15"
            },
            "dev-001": {
                "status": "working", 
                "current_task": "Implementing user authentication API",
                "progress": 0.60,
                "blockers": ["Waiting for database schema approval"],
                "estimated_completion": "2024-01-16"
            },
            "qa-001": {
                "status": "idle",
                "current_task": None,
                "progress": 0.0,
                "blockers": ["Waiting for development completion"],
                "estimated_completion": None
            }
        }
    
    def _identify_blockers(self, agent_statuses: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify blockers across the team."""
        blockers = []
        
        for agent_id, status in agent_statuses.items():
            agent_blockers = status.get("blockers", [])
            for blocker in agent_blockers:
                blockers.append({
                    "agent_id": agent_id,
                    "blocker": blocker,
                    "severity": "high" if "waiting" in blocker.lower() else "medium"
                })
        
        return blockers
    
    def _determine_priorities(
        self,
        agent_statuses: Dict[str, Dict[str, Any]],
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        """Determine next priorities based on current status."""
        priorities = []
        
        # Find idle agents and assign priorities
        for agent_id, status in agent_statuses.items():
            if status["status"] == "idle":
                priorities.append({
                    "agent_id": agent_id,
                    "priority": "Assign new task",
                    "urgency": "high"
                })
            elif status["progress"] > 0.8:
                priorities.append({
                    "agent_id": agent_id,
                    "priority": "Prepare for task completion and handoff",
                    "urgency": "medium"
                })
        
        return priorities
    
    async def _store_validation_result(
        self,
        agent_id: str,
        output: Dict[str, Any],
        validation_result: Dict[str, Any],
        context: AgentContext
    ) -> None:
        """Store validation result in database."""
        # This would store the validation result in the database
        # For now, just log it
        self.logger.info(f"Validation stored for {agent_id}: score={validation_result['score']:.2f}")
    
    async def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate manager's own output."""
        required_fields = ["status", "coordination_result"]
        return all(field in output for field in required_fields)
    
    def get_prompt_template(self) -> str:
        """Get the manager's prompt template."""
        return """
        You are an experienced Engineering Manager responsible for coordinating an AI development team.
        
        Your responsibilities include:
        1. Task assignment and prioritization
        2. Quality validation of team outputs  
        3. Conflict resolution between team members
        4. Sprint planning and coordination
        5. Progress monitoring and reporting
        
        Current context: {context}
        Task: {task}
        
        Provide clear, actionable decisions and maintain team productivity.
        Focus on practical solutions that move the project forward.
        """
    
    def get_quality_standards(self, agent_role: str) -> Dict[str, Any]:
        """Get quality standards for a specific agent role."""
        return self.quality_standards.get(agent_role.lower(), {})
    
    def get_conflict_history(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conflict resolution history."""
        if project_id:
            return [c for c in self.conflict_history if c.get("project_id") == project_id]
        return self.conflict_history
    
    def get_active_tasks(self, agent_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get active task assignments."""
        if agent_id:
            return {k: v for k, v in self.active_tasks.items() if v.get("assigned_to") == agent_id}
        return self.active_tasks
    
    async def _conduct_project_planning(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Conduct project planning and team assignment."""
        
        project_info = task.get("project_info", {})
        team_composition = task.get("team_composition", {})
        
        self.logger.info(f"Planning project: {project_info.get('name', 'Unnamed Project')}")
        
        # Analyze project requirements
        project_complexity = self._assess_project_complexity(project_info)
        required_agents = self._determine_required_agents(project_info, team_composition)
        estimated_timeline = self._estimate_timeline(project_info, project_complexity)
        
        # Create project plan
        project_plan = {
            "project_id": context.project_id,
            "name": project_info.get("name"),
            "complexity_level": project_complexity,
            "assigned_agents": required_agents,
            "estimated_timeline": estimated_timeline,
            "phases": [
                {"phase": "requirements_analysis", "agent": "PM", "duration": "1-2 weeks"},
                {"phase": "architecture_design", "agent": "Architect", "duration": "1-2 weeks"},
                {"phase": "development", "agent": "Developer", "duration": "4-8 weeks"},
                {"phase": "testing", "agent": "QA", "duration": "2-3 weeks"},
                {"phase": "deployment", "agent": "DevOps", "duration": "1 week"}
            ],
            "risk_factors": self._identify_risk_factors(project_info),
            "success_criteria": self._define_success_criteria(project_info)
        }
        
        # Store project plan
        self.project_plans[context.project_id] = project_plan
        
        return {
            "status": "success",
            "project_plan": project_plan,
            "message": f"Project planning completed for {project_info.get('name')}"
        }
    
    def _assess_project_complexity(self, project_info: Dict[str, Any]) -> str:
        """Assess project complexity level."""
        requirements_count = len(project_info.get("requirements", []))
        project_type = project_info.get("type", "web")
        budget = project_info.get("budget", 0)
        
        if requirements_count > 10 or budget > 1000000 or project_type in ["enterprise", "platform"]:
            return "high"
        elif requirements_count > 5 or budget > 500000:
            return "medium"
        else:
            return "low"
    
    def _determine_required_agents(self, project_info: Dict[str, Any], team_composition: Dict[str, Any]) -> List[str]:
        """Determine which agents are required for the project."""
        base_agents = ["Manager", "PM", "Architect", "Developer", "QA"]
        
        project_type = project_info.get("type", "web")
        complexity = self._assess_project_complexity(project_info)
        
        if project_type in ["mobile", "desktop"]:
            base_agents.append("UI")
        
        if complexity == "high":
            base_agents.append("DevOps")
            base_agents.append("Security")
        
        return base_agents
    
    def _estimate_timeline(self, project_info: Dict[str, Any], complexity: str) -> Dict[str, Any]:
        """Estimate project timeline."""
        base_weeks = {
            "low": 6,
            "medium": 12,
            "high": 24
        }
        
        return {
            "estimated_weeks": base_weeks.get(complexity, 12),
            "phases_breakdown": {
                "planning": "1-2 weeks",
                "development": f"{base_weeks.get(complexity, 12) - 4}-{base_weeks.get(complexity, 12) - 2} weeks",
                "testing": "1-2 weeks",
                "deployment": "1 week"
            }
        }
    
    def _identify_risk_factors(self, project_info: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        if len(project_info.get("requirements", [])) > 15:
            risks.append("Complex requirements may lead to scope creep")
        
        if project_info.get("budget", 0) < 100000:
            risks.append("Limited budget may constrain development options")
        
        if "AI" in project_info.get("description", "").upper():
            risks.append("AI/ML components may require specialized expertise")
        
        return risks
    
    def _define_success_criteria(self, project_info: Dict[str, Any]) -> List[str]:
        """Define project success criteria."""
        return [
            "All functional requirements implemented and tested",
            "Performance meets specified benchmarks",
            "User acceptance testing passed",
            f"Project delivered within {project_info.get('timeline', '3 months')}",
            f"Budget maintained within {project_info.get('budget', 'allocated')} limits"
        ]