"""PM Agent - Product Manager for requirement analysis and user story creation."""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from src.agents.base import BaseAgent, AgentRole, AgentStatus, AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


class StoryPriority(str, Enum):
    """User story priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class StoryType(str, Enum):
    """Types of user stories."""
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    IMPROVEMENT = "improvement"
    TECHNICAL = "technical"
    SPIKE = "spike"


class PMAgent(BaseAgent):
    """
    Product Manager Agent responsible for:
    - Requirements gathering and analysis
    - User story creation and prioritization
    - Product roadmap planning
    - Stakeholder communication
    - Acceptance criteria definition
    """
    
    def __init__(self, agent_id: str = "pm-001"):
        super().__init__(agent_id, AgentRole.PM)
        
        # PM-specific state
        self.stakeholder_feedback = []
        self.user_stories = {}
        self.product_roadmap = {}
        self.requirements_backlog = []
        
        # PM configuration
        self.story_estimation_enabled = True
        self.stakeholder_validation_required = True
        self.max_stories_per_sprint = 15
    
    async def process_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Process PM tasks including requirements analysis and story creation.
        
        Args:
            task: PM task details
            context: Current context
            
        Returns:
            Task processing result
        """
        task_type = task.get("type", "analyze_requirements")
        
        self.logger.info(f"Processing PM task: {task_type}")
        
        try:
            if task_type == "analyze_requirements":
                return await self._analyze_requirements(task, context)
            elif task_type == "create_user_stories":
                return await self._create_user_stories(task, context)
            elif task_type == "prioritize_backlog":
                return await self._prioritize_backlog(task, context)
            elif task_type == "define_acceptance_criteria":
                return await self._define_acceptance_criteria(task, context)
            elif task_type == "create_prd":
                return await self._create_prd(task, context)
            elif task_type == "stakeholder_review":
                return await self._conduct_stakeholder_review(task, context)
            elif task_type == "roadmap_planning":
                return await self._plan_roadmap(task, context)
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing PM task: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _analyze_requirements(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Analyze and structure requirements from various sources."""
        
        raw_requirements = task.get("requirements", [])
        business_goals = task.get("business_goals", [])
        user_feedback = task.get("user_feedback", [])
        
        self.logger.info(f"Analyzing {len(raw_requirements)} requirements")
        
        # Structure and categorize requirements
        structured_requirements = []
        
        for req in raw_requirements:
            if isinstance(req, str):
                # Parse text requirement
                structured_req = await self._parse_text_requirement(req)
            else:
                # Already structured
                structured_req = req
            
            # Add metadata
            structured_req.update({
                "id": f"REQ-{len(structured_requirements) + 1:03d}",
                "analyzed_at": datetime.utcnow().isoformat(),
                "source": req.get("source", "unknown") if isinstance(req, dict) else "text_input",
                "category": await self._categorize_requirement(structured_req)
            })
            
            structured_requirements.append(structured_req)
        
        # Identify dependencies and conflicts
        dependencies = await self._identify_dependencies(structured_requirements)
        conflicts = await self._identify_conflicts(structured_requirements)
        
        # Calculate business value
        for req in structured_requirements:
            req["business_value"] = await self._calculate_business_value(req, business_goals)
        
        analysis_result = {
            "total_requirements": len(structured_requirements),
            "requirements": structured_requirements,
            "dependencies": dependencies,
            "conflicts": conflicts,
            "business_alignment": await self._assess_business_alignment(structured_requirements, business_goals),
            "implementation_complexity": await self._assess_complexity(structured_requirements),
            "recommendations": await self._generate_requirements_recommendations(
                structured_requirements, dependencies, conflicts
            )
        }
        
        # Store in backlog
        self.requirements_backlog.extend(structured_requirements)
        
        return {
            "status": "success",
            "analysis": analysis_result
        }
    
    async def _create_user_stories(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Create user stories from requirements."""
        
        requirements = task.get("requirements", [])
        personas = task.get("personas", [])
        
        if not requirements:
            requirements = self.requirements_backlog
        
        self.logger.info(f"Creating user stories from {len(requirements)} requirements")
        
        user_stories = []
        
        for req in requirements:
            # Generate stories for each relevant persona
            relevant_personas = await self._identify_relevant_personas(req, personas)
            
            for persona in relevant_personas:
                story = await self._generate_user_story(req, persona)
                
                if story:
                    story.update({
                        "id": f"US-{len(user_stories) + 1:03d}",
                        "requirement_id": req.get("id"),
                        "persona": persona.get("name", "User"),
                        "created_at": datetime.utcnow().isoformat(),
                        "priority": await self._calculate_story_priority(story, req),
                        "story_type": await self._determine_story_type(story, req),
                        "complexity": await self._estimate_story_complexity(story),
                        "acceptance_criteria": await self._generate_acceptance_criteria(story, req)
                    })
                    
                    user_stories.append(story)
        
        # Group related stories into epics
        epics = await self._group_stories_into_epics(user_stories)
        
        # Store stories
        for story in user_stories:
            self.user_stories[story["id"]] = story
        
        return {
            "status": "success",
            "user_stories": user_stories,
            "epics": epics,
            "summary": {
                "total_stories": len(user_stories),
                "by_priority": self._count_by_priority(user_stories),
                "by_type": self._count_by_type(user_stories),
                "estimated_effort": sum(s.get("story_points", 0) for s in user_stories)
            }
        }
    
    async def _prioritize_backlog(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Prioritize product backlog using various factors."""
        
        stories = task.get("stories", list(self.user_stories.values()))
        prioritization_method = task.get("method", "moscow")  # moscow, kano, rice, etc.
        
        self.logger.info(f"Prioritizing {len(stories)} stories using {prioritization_method} method")
        
        if prioritization_method == "moscow":
            prioritized_stories = await self._moscow_prioritization(stories)
        elif prioritization_method == "rice":
            prioritized_stories = await self._rice_prioritization(stories)
        elif prioritization_method == "kano":
            prioritized_stories = await self._kano_prioritization(stories)
        else:
            prioritized_stories = await self._value_effort_prioritization(stories)
        
        # Generate sprint recommendations
        sprint_recommendations = await self._recommend_sprint_allocation(prioritized_stories)
        
        return {
            "status": "success",
            "prioritized_backlog": prioritized_stories,
            "sprint_recommendations": sprint_recommendations,
            "prioritization_rationale": await self._explain_prioritization(prioritized_stories, prioritization_method)
        }
    
    async def _define_acceptance_criteria(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Define detailed acceptance criteria for user stories."""
        
        story_ids = task.get("story_ids", [])
        stories = [self.user_stories.get(sid) for sid in story_ids if sid in self.user_stories]
        
        enhanced_stories = []
        
        for story in stories:
            if not story:
                continue
                
            # Generate comprehensive acceptance criteria
            acceptance_criteria = await self._generate_detailed_acceptance_criteria(story)
            
            # Add test scenarios
            test_scenarios = await self._generate_test_scenarios(story, acceptance_criteria)
            
            # Add edge cases
            edge_cases = await self._identify_edge_cases(story)
            
            enhanced_story = story.copy()
            enhanced_story.update({
                "acceptance_criteria": acceptance_criteria,
                "test_scenarios": test_scenarios,
                "edge_cases": edge_cases,
                "definition_of_done": await self._generate_definition_of_done(story),
                "updated_at": datetime.utcnow().isoformat()
            })
            
            enhanced_stories.append(enhanced_story)
            
            # Update stored story
            self.user_stories[story["id"]] = enhanced_story
        
        return {
            "status": "success",
            "enhanced_stories": enhanced_stories,
            "quality_metrics": {
                "avg_criteria_per_story": sum(len(s.get("acceptance_criteria", [])) for s in enhanced_stories) / len(enhanced_stories) if enhanced_stories else 0,
                "total_test_scenarios": sum(len(s.get("test_scenarios", [])) for s in enhanced_stories),
                "edge_cases_identified": sum(len(s.get("edge_cases", [])) for s in enhanced_stories)
            }
        }
    
    async def _create_prd(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Create a comprehensive Product Requirements Document."""
        
        project_overview = task.get("project_overview", {})
        target_users = task.get("target_users", [])
        business_objectives = task.get("business_objectives", [])
        
        # Gather all relevant information
        relevant_stories = list(self.user_stories.values())
        relevant_requirements = self.requirements_backlog
        
        prd = {
            "document_info": {
                "title": f"Product Requirements Document - {project_overview.get('name', 'Product')}",
                "version": "1.0",
                "created_by": self.agent_id,
                "created_at": datetime.utcnow().isoformat(),
                "project_id": context.project_id
            },
            
            "executive_summary": await self._generate_executive_summary(
                project_overview, business_objectives, relevant_stories
            ),
            
            "product_overview": {
                "vision": project_overview.get("vision", ""),
                "mission": project_overview.get("mission", ""),
                "success_metrics": await self._define_success_metrics(business_objectives),
                "target_market": await self._analyze_target_market(target_users)
            },
            
            "user_personas": await self._detailed_persona_analysis(target_users),
            
            "functional_requirements": await self._organize_functional_requirements(relevant_requirements),
            
            "user_stories": await self._organize_stories_for_prd(relevant_stories),
            
            "non_functional_requirements": await self._define_non_functional_requirements(project_overview),
            
            "technical_constraints": await self._identify_technical_constraints(context),
            
            "assumptions_and_dependencies": await self._document_assumptions_dependencies(
                relevant_requirements, relevant_stories
            ),
            
            "success_criteria": await self._define_detailed_success_criteria(business_objectives),
            
            "risks_and_mitigation": await self._identify_product_risks(),
            
            "roadmap": await self._create_high_level_roadmap(relevant_stories)
        }
        
        return {
            "status": "success",
            "prd": prd,
            "document_statistics": {
                "total_pages_estimated": await self._estimate_document_length(prd),
                "requirements_covered": len(relevant_requirements),
                "user_stories_included": len(relevant_stories),
                "completeness_score": await self._assess_prd_completeness(prd)
            }
        }
    
    async def _conduct_stakeholder_review(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Simulate stakeholder review and feedback collection."""
        
        review_items = task.get("items", [])  # Stories, requirements, or PRD sections
        stakeholders = task.get("stakeholders", ["Business", "Development", "Design", "QA"])
        
        feedback_results = []
        
        for item in review_items:
            item_feedback = {
                "item_id": item.get("id", f"item-{len(feedback_results)}"),
                "item_type": item.get("type", "user_story"),
                "stakeholder_feedback": []
            }
            
            for stakeholder in stakeholders:
                feedback = await self._simulate_stakeholder_feedback(item, stakeholder)
                item_feedback["stakeholder_feedback"].append(feedback)
            
            # Aggregate feedback
            item_feedback["consensus_level"] = await self._calculate_consensus(
                item_feedback["stakeholder_feedback"]
            )
            item_feedback["action_required"] = await self._determine_required_actions(
                item_feedback["stakeholder_feedback"]
            )
            
            feedback_results.append(item_feedback)
        
        # Generate overall review summary
        review_summary = {
            "total_items_reviewed": len(review_items),
            "consensus_reached": len([f for f in feedback_results if f["consensus_level"] > 0.7]),
            "items_requiring_changes": len([f for f in feedback_results if f["action_required"]]),
            "overall_approval_rate": sum(f["consensus_level"] for f in feedback_results) / len(feedback_results) if feedback_results else 0
        }
        
        return {
            "status": "success",
            "feedback_results": feedback_results,
            "review_summary": review_summary,
            "next_steps": await self._recommend_next_steps(feedback_results)
        }
    
    async def _plan_roadmap(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Create product roadmap based on prioritized backlog."""
        
        time_horizon = task.get("horizon_months", 12)
        team_capacity = task.get("team_capacity", {"velocity": 40, "sprints_per_month": 2})
        
        # Get prioritized stories
        prioritized_stories = list(self.user_stories.values())
        prioritized_stories.sort(key=lambda s: self._get_priority_score(s), reverse=True)
        
        # Plan releases
        releases = []
        current_capacity = 0
        current_release = {
            "release_number": 1,
            "target_date": datetime.utcnow().isoformat(),
            "stories": [],
            "total_points": 0,
            "themes": []
        }
        
        monthly_capacity = team_capacity["velocity"] * team_capacity["sprints_per_month"]
        
        for story in prioritized_stories:
            story_points = story.get("story_points", 3)
            
            if current_capacity + story_points > monthly_capacity:
                # Complete current release
                releases.append(current_release)
                
                # Start new release
                current_release = {
                    "release_number": len(releases) + 1,
                    "target_date": datetime.utcnow().isoformat(),  # Would calculate actual date
                    "stories": [],
                    "total_points": 0,
                    "themes": []
                }
                current_capacity = 0
            
            current_release["stories"].append(story)
            current_release["total_points"] += story_points
            current_capacity += story_points
        
        # Add final release if it has stories
        if current_release["stories"]:
            releases.append(current_release)
        
        # Identify themes for each release
        for release in releases:
            release["themes"] = await self._identify_release_themes(release["stories"])
        
        roadmap = {
            "time_horizon_months": time_horizon,
            "total_releases": len(releases),
            "releases": releases,
            "assumptions": {
                "team_velocity": team_capacity["velocity"],
                "sprints_per_month": team_capacity["sprints_per_month"],
                "capacity_utilization": 0.8  # 80% utilization assumed
            },
            "key_milestones": await self._identify_key_milestones(releases),
            "risks": await self._identify_roadmap_risks(releases)
        }
        
        self.product_roadmap = roadmap
        
        return {
            "status": "success",
            "roadmap": roadmap
        }
    
    async def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate PM's output quality."""
        
        if not output or output.get("status") != "success":
            return False
        
        # Check for required PM deliverables
        if "user_stories" in output:
            stories = output["user_stories"]
            return all(
                story.get("title") and 
                story.get("acceptance_criteria") and
                story.get("priority")
                for story in stories
            )
        
        if "prd" in output:
            prd = output["prd"]
            required_sections = ["executive_summary", "functional_requirements", "user_stories"]
            return all(section in prd for section in required_sections)
        
        return True
    
    def get_prompt_template(self) -> str:
        """Get PM's prompt template."""
        return """
        You are an experienced Product Manager responsible for defining product requirements and creating user stories.
        
        Your responsibilities include:
        1. Analyzing and structuring requirements from stakeholders
        2. Creating clear, actionable user stories with acceptance criteria
        3. Prioritizing product backlog based on business value
        4. Writing comprehensive Product Requirements Documents (PRDs)
        5. Facilitating stakeholder reviews and gathering feedback
        6. Planning product roadmaps and release schedules
        
        Current context: {context}
        Task: {task}
        
        Focus on:
        - User-centric thinking and clear value propositions
        - Detailed acceptance criteria that prevent ambiguity
        - Business value and impact assessment
        - Feasibility and technical constraints
        - Stakeholder alignment and communication
        
        Always consider the user's perspective and business objectives in your decisions.
        """
    
    # Helper methods for PM-specific functionality
    
    async def _parse_text_requirement(self, text: str) -> Dict[str, Any]:
        """Parse natural language requirement into structured format."""
        # Simplified parsing - in real implementation would use NLP
        return {
            "description": text,
            "type": "functional" if "should" in text.lower() else "non-functional",
            "complexity": "medium",
            "priority": "medium"
        }
    
    async def _categorize_requirement(self, requirement: Dict[str, Any]) -> str:
        """Categorize requirement by type."""
        description = requirement.get("description", "").lower()
        
        if any(word in description for word in ["performance", "speed", "load"]):
            return "performance"
        elif any(word in description for word in ["security", "auth", "encrypt"]):
            return "security"
        elif any(word in description for word in ["ui", "interface", "design"]):
            return "interface"
        elif any(word in description for word in ["data", "database", "store"]):
            return "data"
        else:
            return "functional"
    
    async def _calculate_business_value(self, requirement: Dict[str, Any], business_goals: List[str]) -> float:
        """Calculate business value score for requirement."""
        # Simplified scoring - would use more sophisticated analysis
        base_score = 0.5
        
        description = requirement.get("description", "").lower()
        
        for goal in business_goals:
            if any(word in description for word in goal.lower().split()):
                base_score += 0.2
        
        return min(1.0, base_score)
    
    async def _generate_user_story(self, requirement: Dict[str, Any], persona: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate user story from requirement and persona."""
        
        req_desc = requirement.get("description", "")
        persona_name = persona.get("name", "User")
        persona_goal = persona.get("primary_goal", "accomplish tasks")
        
        # Generate story in "As a... I want... So that..." format
        story = {
            "title": f"{persona_name} - {req_desc[:50]}...",
            "story": f"As a {persona_name}, I want to {req_desc.lower()}, so that I can {persona_goal}",
            "description": req_desc,
            "persona_id": persona.get("id", "default")
        }
        
        return story
    
    async def _calculate_story_priority(self, story: Dict[str, Any], requirement: Dict[str, Any]) -> str:
        """Calculate story priority based on various factors."""
        
        business_value = requirement.get("business_value", 0.5)
        complexity = story.get("complexity", "medium")
        
        if business_value > 0.8:
            return StoryPriority.HIGH.value
        elif business_value > 0.6:
            return StoryPriority.MEDIUM.value
        elif complexity == "low" and business_value > 0.4:
            return StoryPriority.MEDIUM.value
        else:
            return StoryPriority.LOW.value
    
    async def _estimate_story_complexity(self, story: Dict[str, Any]) -> int:
        """Estimate story points for the story."""
        
        description_length = len(story.get("description", ""))
        
        if description_length < 100:
            return 2
        elif description_length < 300:
            return 5
        elif description_length < 500:
            return 8
        else:
            return 13
    
    async def _generate_acceptance_criteria(self, story: Dict[str, Any], requirement: Dict[str, Any]) -> List[str]:
        """Generate acceptance criteria for user story."""
        
        criteria = [
            f"Given the user is authenticated",
            f"When they {story.get('description', 'perform the action').lower()}",
            f"Then the system should respond appropriately",
            f"And the user should see confirmation of the action"
        ]
        
        return criteria
    
    def _count_by_priority(self, stories: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count stories by priority."""
        counts = {}
        for story in stories:
            priority = story.get("priority", "medium")
            counts[priority] = counts.get(priority, 0) + 1
        return counts
    
    def _count_by_type(self, stories: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count stories by type."""
        counts = {}
        for story in stories:
            story_type = story.get("story_type", "feature")
            counts[story_type] = counts.get(story_type, 0) + 1
        return counts
    
    def _get_priority_score(self, story: Dict[str, Any]) -> float:
        """Get numeric priority score for sorting."""
        priority = story.get("priority", "medium")
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(priority, 2)
    
    # Placeholder methods for complex PM operations
    # These would be implemented with more sophisticated logic in production
    
    async def _identify_dependencies(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify dependencies between requirements."""
        return []  # Simplified
    
    async def _identify_conflicts(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify conflicts between requirements."""
        return []  # Simplified
    
    async def _assess_business_alignment(self, requirements: List[Dict[str, Any]], goals: List[str]) -> float:
        """Assess how well requirements align with business goals."""
        return 0.85  # Simplified
    
    async def _assess_complexity(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess implementation complexity."""
        return {"overall": "medium", "technical_risk": "low"}  # Simplified
    
    async def _generate_requirements_recommendations(self, requirements, dependencies, conflicts) -> List[str]:
        """Generate recommendations for requirements."""
        return ["Prioritize core functionality first", "Address conflicts before implementation"]
    
    async def _identify_relevant_personas(self, requirement: Dict[str, Any], personas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify personas relevant to a requirement."""
        return personas[:1] if personas else [{"name": "User", "id": "default"}]  # Simplified
    
    async def _determine_story_type(self, story: Dict[str, Any], requirement: Dict[str, Any]) -> str:
        """Determine the type of user story."""
        return StoryType.FEATURE.value  # Simplified
    
    async def _group_stories_into_epics(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group related stories into epics."""
        return []  # Simplified - would implement grouping logic
    
    async def _moscow_prioritization(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply MoSCoW prioritization method."""
        # Simplified implementation
        for story in stories:
            priority = story.get("priority", "medium")
            if priority == "critical":
                story["moscow"] = "Must"
            elif priority == "high":
                story["moscow"] = "Should"
            elif priority == "medium":
                story["moscow"] = "Could"
            else:
                story["moscow"] = "Won't"
        
        return sorted(stories, key=lambda s: {"Must": 4, "Should": 3, "Could": 2, "Won't": 1}.get(s["moscow"], 1), reverse=True)
    
    async def _rice_prioritization(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply RICE prioritization method."""
        return stories  # Simplified
    
    async def _kano_prioritization(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply Kano model prioritization."""
        return stories  # Simplified
    
    async def _value_effort_prioritization(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply value vs effort prioritization."""
        return stories  # Simplified