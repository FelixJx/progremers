"""Meeting minutes management system."""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from src.utils import get_logger
from src.core.memory.sprint_memory import SprintMemoryManager

logger = get_logger(__name__)


class MeetingType(str, Enum):
    """Types of meetings in the sprint cycle."""
    PLANNING = "planning"
    DAILY = "daily"
    REVIEW = "review"
    RETROSPECTIVE = "retrospective"
    AD_HOC = "ad_hoc"


@dataclass
class MeetingParticipant:
    """Meeting participant information."""
    agent_id: str
    role: str
    attendance: str = "present"  # present, absent, partial


@dataclass
class ActionItem:
    """Action item from meeting."""
    id: str
    description: str
    assigned_to: str
    due_date: Optional[str] = None
    priority: str = "medium"
    status: str = "open"


class MeetingMinutesManager:
    """
    Manages meeting minutes for all sprint meetings.
    
    Automatically generates structured meeting records and integrates
    with the sprint memory system.
    """
    
    def __init__(self, memory_manager: SprintMemoryManager):
        self.memory_manager = memory_manager
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Meeting templates
        self.meeting_templates = {
            MeetingType.PLANNING: self._get_planning_template(),
            MeetingType.DAILY: self._get_daily_template(),
            MeetingType.REVIEW: self._get_review_template(),
            MeetingType.RETROSPECTIVE: self._get_retrospective_template()
        }
    
    async def create_meeting_minutes(
        self,
        project_id: str,
        sprint_id: str,
        meeting_type: MeetingType,
        participants: List[MeetingParticipant],
        agenda: Dict[str, Any],
        outcomes: Dict[str, Any]
    ) -> str:
        """Create structured meeting minutes."""
        
        meeting_id = f"{meeting_type.value}_{datetime.utcnow().timestamp()}"
        
        minutes = {
            "meeting_id": meeting_id,
            "type": meeting_type.value,
            "date": datetime.utcnow().isoformat(),
            "participants": [
                {
                    "agent_id": p.agent_id,
                    "role": p.role,
                    "attendance": p.attendance
                } for p in participants
            ],
            "agenda": agenda,
            "outcomes": outcomes,
            "action_items": [],
            "decisions": [],
            "blockers_identified": [],
            "next_steps": []
        }
        
        # Apply meeting-specific processing
        await self._process_meeting_type(minutes, meeting_type, outcomes)
        
        # Store in memory system
        await self.memory_manager.add_meeting_memory(
            project_id, sprint_id, meeting_type.value, minutes
        )
        
        # Update core memory with key decisions
        if minutes["decisions"]:
            for decision in minutes["decisions"]:
                await self.memory_manager.add_decision(
                    project_id, sprint_id, decision
                )
        
        # Update core memory with blockers
        if minutes["blockers_identified"]:
            for blocker in minutes["blockers_identified"]:
                await self.memory_manager.add_blocker(
                    project_id, sprint_id, blocker
                )
        
        self.logger.info(f"Created meeting minutes: {meeting_type.value} ({meeting_id})")
        return meeting_id
    
    async def _process_meeting_type(
        self,
        minutes: Dict[str, Any],
        meeting_type: MeetingType,
        outcomes: Dict[str, Any]
    ) -> None:
        """Apply meeting-type specific processing."""
        
        if meeting_type == MeetingType.PLANNING:
            await self._process_planning_meeting(minutes, outcomes)
        elif meeting_type == MeetingType.DAILY:
            await self._process_daily_meeting(minutes, outcomes)
        elif meeting_type == MeetingType.REVIEW:
            await self._process_review_meeting(minutes, outcomes)
        elif meeting_type == MeetingType.RETROSPECTIVE:
            await self._process_retrospective_meeting(minutes, outcomes)
    
    async def _process_planning_meeting(
        self,
        minutes: Dict[str, Any],
        outcomes: Dict[str, Any]
    ) -> None:
        """Process sprint planning meeting."""
        
        # Extract sprint planning specific information
        sprint_goal = outcomes.get("sprint_goal", "")
        user_stories = outcomes.get("user_stories", [])
        team_capacity = outcomes.get("team_capacity", {})
        
        # Generate action items
        action_items = []
        
        # Create action items for each user story
        for story in user_stories:
            if story.get("assigned_to"):
                action_item = ActionItem(
                    id=f"story_{story.get('id', 'unknown')}",
                    description=f"Complete user story: {story.get('title', 'Untitled')}",
                    assigned_to=story["assigned_to"],
                    due_date=story.get("due_date"),
                    priority=story.get("priority", "medium")
                )
                action_items.append(action_item)
        
        minutes["action_items"] = [
            {
                "id": item.id,
                "description": item.description,
                "assigned_to": item.assigned_to,
                "due_date": item.due_date,
                "priority": item.priority,
                "status": item.status
            } for item in action_items
        ]
        
        # Record key decisions
        minutes["decisions"] = [
            {
                "type": "sprint_goal",
                "description": f"Sprint goal set: {sprint_goal}",
                "rationale": "Team consensus during planning",
                "impact": "high"
            }
        ]
        
        # Identify capacity concerns as potential blockers
        if team_capacity:
            total_story_points = sum(story.get("points", 0) for story in user_stories)
            available_capacity = sum(team_capacity.values())
            
            if total_story_points > available_capacity * 1.2:  # 20% buffer
                minutes["blockers_identified"].append({
                    "id": f"capacity_concern_{datetime.utcnow().timestamp()}",
                    "type": "capacity",
                    "description": f"Story points ({total_story_points}) exceed team capacity ({available_capacity})",
                    "severity": "medium",
                    "suggested_action": "Consider removing lower priority stories"
                })
    
    async def _process_daily_meeting(
        self,
        minutes: Dict[str, Any],
        outcomes: Dict[str, Any]
    ) -> None:
        """Process daily standup meeting."""
        
        # Extract standup information
        agent_updates = outcomes.get("agent_updates", {})
        new_blockers = outcomes.get("blockers", [])
        
        # Process each agent's update
        for agent_id, update in agent_updates.items():
            # Record blockers
            if update.get("blockers"):
                for blocker_desc in update["blockers"]:
                    blocker = {
                        "id": f"blocker_{agent_id}_{datetime.utcnow().timestamp()}",
                        "type": "task",
                        "description": blocker_desc,
                        "affected_agent": agent_id,
                        "severity": "medium"
                    }
                    minutes["blockers_identified"].append(blocker)
            
            # Create action items for help needed
            if update.get("needs_help"):
                action_item = ActionItem(
                    id=f"help_{agent_id}_{datetime.utcnow().timestamp()}",
                    description=f"Provide assistance to {agent_id}: {update['needs_help']}",
                    assigned_to="manager-001",  # Manager coordinates help
                    priority="high"
                )
                minutes["action_items"].append({
                    "id": action_item.id,
                    "description": action_item.description,
                    "assigned_to": action_item.assigned_to,
                    "priority": action_item.priority,
                    "status": action_item.status
                })
        
        # Set next steps
        minutes["next_steps"] = [
            "Continue with assigned tasks",
            "Address identified blockers",
            "Coordinate on dependencies"
        ]
    
    async def _process_review_meeting(
        self,
        minutes: Dict[str, Any],
        outcomes: Dict[str, Any]
    ) -> None:
        """Process sprint review meeting."""
        
        # Extract review information
        completed_stories = outcomes.get("completed_stories", [])
        incomplete_stories = outcomes.get("incomplete_stories", [])
        demo_feedback = outcomes.get("demo_feedback", [])
        
        # Record completion decisions
        if completed_stories:
            minutes["decisions"].append({
                "type": "story_completion",
                "description": f"Accepted {len(completed_stories)} completed stories",
                "details": [story.get("title") for story in completed_stories],
                "impact": "high"
            })
        
        # Handle incomplete stories
        if incomplete_stories:
            for story in incomplete_stories:
                action_item = ActionItem(
                    id=f"carryover_{story.get('id', 'unknown')}",
                    description=f"Carry over incomplete story: {story.get('title')}",
                    assigned_to=story.get("assigned_to", "pm-001"),
                    priority="high"
                )
                minutes["action_items"].append({
                    "id": action_item.id,
                    "description": action_item.description,
                    "assigned_to": action_item.assigned_to,
                    "priority": action_item.priority,
                    "status": action_item.status
                })
        
        # Process demo feedback
        if demo_feedback:
            minutes["decisions"].extend([
                {
                    "type": "feedback_item",
                    "description": feedback.get("description", ""),
                    "priority": feedback.get("priority", "medium"),
                    "action_required": feedback.get("action_required", False)
                } for feedback in demo_feedback
            ])
    
    async def _process_retrospective_meeting(
        self,
        minutes: Dict[str, Any],
        outcomes: Dict[str, Any]
    ) -> None:
        """Process sprint retrospective meeting."""
        
        # Extract retrospective information
        what_worked = outcomes.get("what_worked", [])
        what_didnt_work = outcomes.get("what_didnt_work", [])
        improvements = outcomes.get("improvements", [])
        
        # Create action items for improvements
        for improvement in improvements:
            action_item = ActionItem(
                id=f"improvement_{datetime.utcnow().timestamp()}",
                description=improvement.get("description", ""),
                assigned_to=improvement.get("owner", "manager-001"),
                priority=improvement.get("priority", "medium")
            )
            minutes["action_items"].append({
                "id": action_item.id,
                "description": action_item.description,
                "assigned_to": action_item.assigned_to,
                "priority": action_item.priority,
                "status": action_item.status
            })
        
        # Record improvement decisions
        if improvements:
            minutes["decisions"].extend([
                {
                    "type": "process_improvement",
                    "description": imp.get("description", ""),
                    "rationale": "Identified during retrospective",
                    "expected_benefit": imp.get("expected_benefit", "")
                } for imp in improvements
            ])
        
        # Set next steps for next sprint
        minutes["next_steps"] = [
            "Apply identified improvements in next sprint",
            "Monitor effectiveness of changes",
            "Continue practices that worked well"
        ]
    
    async def get_meeting_history(
        self,
        project_id: str,
        sprint_id: str,
        meeting_type: Optional[MeetingType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get meeting history for a sprint."""
        
        # This would integrate with the memory system to retrieve meeting records
        # For now, return a placeholder
        return []
    
    async def generate_meeting_summary(
        self,
        meeting_minutes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a concise summary of meeting minutes."""
        
        summary = {
            "meeting_id": meeting_minutes["meeting_id"],
            "type": meeting_minutes["type"],
            "date": meeting_minutes["date"],
            "key_outcomes": [],
            "action_items_count": len(meeting_minutes.get("action_items", [])),
            "decisions_count": len(meeting_minutes.get("decisions", [])),
            "blockers_count": len(meeting_minutes.get("blockers_identified", []))
        }
        
        # Extract key outcomes based on meeting type
        meeting_type = MeetingType(meeting_minutes["type"])
        
        if meeting_type == MeetingType.PLANNING:
            summary["key_outcomes"] = [
                f"Sprint goal: {meeting_minutes['outcomes'].get('sprint_goal', 'Not set')}",
                f"Stories planned: {len(meeting_minutes['outcomes'].get('user_stories', []))}",
                f"Team capacity: {meeting_minutes['outcomes'].get('team_capacity', 'Not specified')}"
            ]
        
        elif meeting_type == MeetingType.REVIEW:
            completed = len(meeting_minutes["outcomes"].get("completed_stories", []))
            incomplete = len(meeting_minutes["outcomes"].get("incomplete_stories", []))
            summary["key_outcomes"] = [
                f"Stories completed: {completed}",
                f"Stories incomplete: {incomplete}",
                f"Demo feedback items: {len(meeting_minutes['outcomes'].get('demo_feedback', []))}"
            ]
        
        return summary
    
    # Meeting templates
    
    def _get_planning_template(self) -> Dict[str, Any]:
        """Get sprint planning meeting template."""
        return {
            "agenda_items": [
                "Review sprint goal",
                "Estimate user stories",
                "Assign stories to team members",
                "Identify dependencies and risks",
                "Confirm team capacity"
            ],
            "expected_outcomes": [
                "Sprint goal defined",
                "User stories estimated and assigned",
                "Sprint backlog finalized",
                "Risks identified and mitigated"
            ]
        }
    
    def _get_daily_template(self) -> Dict[str, Any]:
        """Get daily standup template."""
        return {
            "agenda_items": [
                "What did you complete yesterday?",
                "What will you work on today?",
                "Are there any blockers or impediments?"
            ],
            "expected_outcomes": [
                "Progress visibility",
                "Blocker identification",
                "Team coordination"
            ]
        }
    
    def _get_review_template(self) -> Dict[str, Any]:
        """Get sprint review template."""
        return {
            "agenda_items": [
                "Demo completed features",
                "Review sprint goals achievement",
                "Gather stakeholder feedback",
                "Discuss incomplete items"
            ],
            "expected_outcomes": [
                "Features demonstrated",
                "Feedback collected",
                "Incomplete items identified",
                "Next sprint input gathered"
            ]
        }
    
    def _get_retrospective_template(self) -> Dict[str, Any]:
        """Get retrospective template."""
        return {
            "agenda_items": [
                "What went well?",
                "What could be improved?",
                "What will we commit to improve?",
                "Action items for next sprint"
            ],
            "expected_outcomes": [
                "Process improvements identified",
                "Action items defined",
                "Team alignment on changes",
                "Commitment to improvements"
            ]
        }