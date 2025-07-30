#!/usr/bin/env python3
"""AI Agent Development Team - Complete Team Integration Test."""

import asyncio
import sys
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.implementations.manager_agent import ManagerAgent
from src.agents.implementations.pm_agent import PMAgent
from src.agents.implementations.architect_agent import ArchitectAgent
from src.agents.implementations.developer_agent import DeveloperAgent
from src.agents.implementations.qa_agent import QAAgent
from src.agents.base import AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


class AIAgentTeam:
    """AI Agent Development Team orchestrator."""
    
    def __init__(self):
        self.manager = ManagerAgent("manager-001")
        self.pm = PMAgent("pm-001")
        self.architect = ArchitectAgent("arch-001")
        self.developer = DeveloperAgent("dev-001")
        self.qa = QAAgent("qa-001")
        
        self.team_members = {
            "manager": self.manager,
            "pm": self.pm,
            "architect": self.architect,
            "developer": self.developer,
            "qa": self.qa
        }
    
    async def execute_development_workflow(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete development workflow with all agents."""
        
        context = AgentContext(
            project_id=project_spec.get("project_id", "team-project-001"),
            sprint_id="sprint-001"
        )
        
        workflow_results = {}
        
        # Phase 1: Requirements Analysis (PM)
        print("🎯 Phase 1: Requirements Analysis...")
        requirements_task = {
            "type": "analyze_requirements",
            "requirements": project_spec.get("requirements", []),
            "business_goals": project_spec.get("business_goals", []),
            "user_feedback": []
        }
        
        pm_result = await self.pm.process_task(requirements_task, context)
        workflow_results["requirements_analysis"] = pm_result
        
        if pm_result.get("status") != "success":
            return {"status": "failed", "phase": "requirements_analysis", "error": pm_result}
        
        # Phase 2: User Stories Creation (PM)
        print("📝 Phase 2: User Stories Creation...")
        stories_task = {
            "type": "create_user_stories",
            "requirements": pm_result.get("analysis", {}).get("requirements", []),
            "personas": project_spec.get("personas", [])
        }
        
        stories_result = await self.pm.process_task(stories_task, context)
        workflow_results["user_stories"] = stories_result
        
        if stories_result.get("status") != "success":
            return {"status": "failed", "phase": "user_stories", "error": stories_result}
        
        # Phase 3: Architecture Design (Architect)
        print("🏗️ Phase 3: Architecture Design...")
        arch_task = {
            "type": "design_architecture",
            "requirements": pm_result.get("analysis", {}).get("requirements", []),
            "non_functional_requirements": project_spec.get("non_functional_requirements", {}),
            "constraints": project_spec.get("constraints", [])
        }
        
        arch_result = await self.architect.process_task(arch_task, context)
        workflow_results["architecture_design"] = arch_result
        
        if arch_result.get("status") != "success":
            return {"status": "failed", "phase": "architecture_design", "error": arch_result}
        
        # Phase 4: Technology Selection (Architect)
        print("💻 Phase 4: Technology Selection...")
        tech_task = {
            "type": "select_technology",
            "requirements": arch_result.get("architecture_design", {}).get("system_components", {}),
            "constraints": project_spec.get("constraints", []),
            "team_expertise": project_spec.get("team_expertise", []),
            "budget": project_spec.get("budget", {})
        }
        
        tech_result = await self.architect.process_task(tech_task, context)
        workflow_results["technology_selection"] = tech_result
        
        if tech_result.get("status") != "success":
            return {"status": "failed", "phase": "technology_selection", "error": tech_result}
        
        # Phase 5: Sprint Planning (Manager)
        print("📋 Phase 5: Sprint Planning...")
        sprint_task = {
            "type": "sprint_planning",
            "sprint_goal": project_spec.get("sprint_goal", "Implement core functionality"),
            "user_stories": stories_result.get("user_stories", [])
        }
        
        sprint_result = await self.manager.process_task(sprint_task, context)
        workflow_results["sprint_planning"] = sprint_result
        
        if sprint_result.get("status") != "success":
            return {"status": "failed", "phase": "sprint_planning", "error": sprint_result}
        
        # Phase 6: Feature Implementation (Developer)
        print("🛠️ Phase 6: Feature Implementation...")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Select a user story for implementation
            user_stories = stories_result.get("user_stories", [])
            if user_stories:
                selected_story = user_stories[0]
                
                impl_task = {
                    "type": "implement_feature",
                    "feature_specification": {
                        "name": selected_story.get("title", "feature").lower().replace(" ", "_"),
                        "description": selected_story.get("description", ""),
                        "requirements": selected_story.get("acceptance_criteria", [])
                    },
                    "project_path": temp_dir,
                    "language": "python",
                    "include_tests": True,
                    "run_tests": False,
                    "auto_commit": False
                }
                
                impl_result = await self.developer.process_task(impl_task, context)
                workflow_results["feature_implementation"] = impl_result
                
                if impl_result.get("status") != "success":
                    return {"status": "failed", "phase": "feature_implementation", "error": impl_result}
                
                # Phase 7: Test Suite Creation (QA)
                print("🧪 Phase 7: Test Suite Creation...")
                test_suite_task = {
                    "type": "create_test_suite",
                    "project_path": temp_dir,
                    "test_types": ["unit", "integration"],
                    "requirements": pm_result.get("analysis", {}).get("requirements", [])
                }
                
                test_suite_result = await self.qa.process_task(test_suite_task, context)
                workflow_results["test_suite_creation"] = test_suite_result
                
                if test_suite_result.get("status") != "success":
                    return {"status": "failed", "phase": "test_suite_creation", "error": test_suite_result}
                
                # Phase 8: Test Execution (QA)
                print("🔍 Phase 8: Test Execution...")
                test_exec_task = {
                    "type": "run_tests",
                    "project_path": temp_dir,
                    "suite_id": test_suite_result.get("test_suite", {}).get("suite_id"),
                    "test_types": ["unit", "integration"]
                }
                
                test_exec_result = await self.qa.process_task(test_exec_task, context)
                workflow_results["test_execution"] = test_exec_result
                
                if test_exec_result.get("status") != "success":
                    return {"status": "failed", "phase": "test_execution", "error": test_exec_result}
        
        # Phase 9: Quality Review (Manager)
        print("✅ Phase 9: Quality Review...")
        review_task = {
            "type": "validate",
            "agent_id": "dev-001",
            "agent_role": "developer",
            "output": workflow_results.get("feature_implementation", {}).get("implementation", {})
        }
        
        review_result = await self.manager.process_task(review_task, context)
        workflow_results["quality_review"] = review_result
        
        # Phase 10: Final Report Generation (QA)
        print("📊 Phase 10: Final Report Generation...")
        if "test_execution" in workflow_results:
            report_task = {
                "type": "generate_test_report",
                "execution_id": workflow_results["test_execution"].get("test_execution", {}).get("execution_id"),
                "project_path": temp_dir if 'temp_dir' in locals() else "./"
            }
            
            report_result = await self.qa.process_task(report_task, context)
            workflow_results["final_report"] = report_result
        
        return {
            "status": "success",
            "workflow_results": workflow_results,
            "summary": await self._generate_workflow_summary(workflow_results)
        }
    
    async def _generate_workflow_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of workflow execution."""
        summary = {
            "phases_completed": len([r for r in results.values() if r.get("status") == "success"]),
            "total_phases": len(results),
            "success_rate": 0,
            "deliverables": {},
            "metrics": {}
        }
        
        # Calculate success rate
        successful_phases = len([r for r in results.values() if r.get("status") == "success"])
        summary["success_rate"] = (successful_phases / len(results)) * 100 if results else 0
        
        # Extract key deliverables
        if "requirements_analysis" in results:
            req_analysis = results["requirements_analysis"].get("analysis", {})
            summary["deliverables"]["requirements"] = req_analysis.get("total_requirements", 0)
        
        if "user_stories" in results:
            stories = results["user_stories"].get("user_stories", [])
            summary["deliverables"]["user_stories"] = len(stories)
        
        if "architecture_design" in results:
            arch_design = results["architecture_design"].get("architecture_design", {})
            components = arch_design.get("system_components", {})
            summary["deliverables"]["system_components"] = len(components)
        
        if "feature_implementation" in results:
            implementation = results["feature_implementation"].get("implementation", {})
            summary["deliverables"]["code_files"] = len(implementation.get("generated_files", []))
            summary["deliverables"]["test_files"] = len(implementation.get("test_files", []))
        
        if "test_execution" in results:
            test_exec = results["test_execution"].get("test_execution", {})
            overall = test_exec.get("overall_results", {})
            summary["metrics"]["total_tests"] = overall.get("total_tests", 0)
            summary["metrics"]["test_pass_rate"] = (overall.get("passed", 0) / max(overall.get("total_tests", 1), 1)) * 100
            summary["metrics"]["test_coverage"] = test_exec.get("coverage_report", {}).get("total_coverage", 0)
        
        return summary


async def test_individual_agents():
    """Test each agent individually."""
    
    print("\n🧪 Testing Individual Agents...")
    print("=" * 50)
    
    context = AgentContext(project_id="test-001", sprint_id="sprint-001")
    results = {}
    
    # Test Manager Agent
    print("👨‍💼 Testing Manager Agent...")
    manager = ManagerAgent("manager-test")
    manager_task = {
        "type": "assign_task",
        "task_details": {
            "type": "development",
            "title": "Test task assignment",
            "description": "Testing manager capabilities"
        }
    }
    
    manager_result = await manager.process_task(manager_task, context)
    results["manager"] = manager_result.get("status") == "success"
    print(f"   {'✅' if results['manager'] else '❌'} Manager Agent")
    
    # Test PM Agent
    print("📋 Testing PM Agent...")
    pm = PMAgent("pm-test")
    pm_task = {
        "type": "analyze_requirements",
        "requirements": [
            "User authentication system",
            "Data storage and retrieval",
            "RESTful API endpoints"
        ],
        "business_goals": ["Improve user engagement", "Increase security"]
    }
    
    pm_result = await pm.process_task(pm_task, context)
    results["pm"] = pm_result.get("status") == "success"
    print(f"   {'✅' if results['pm'] else '❌'} PM Agent")
    
    # Test Architect Agent
    print("🏗️ Testing Architect Agent...")
    architect = ArchitectAgent("arch-test")
    arch_task = {
        "type": "design_architecture",
        "requirements": [
            {"id": "REQ-001", "description": "User authentication"},
            {"id": "REQ-002", "description": "Data processing"}
        ],
        "non_functional_requirements": {
            "scalability": {"level": "high"},
            "performance": {"response_time": "< 200ms"}
        }
    }
    
    arch_result = await architect.process_task(arch_task, context)
    results["architect"] = arch_result.get("status") == "success"
    print(f"   {'✅' if results['architect'] else '❌'} Architect Agent")
    
    # Test Developer Agent
    print("👨‍💻 Testing Developer Agent...")
    developer = DeveloperAgent("dev-test")
    with tempfile.TemporaryDirectory() as temp_dir:
        dev_task = {
            "type": "implement_feature",
            "feature_specification": {
                "name": "user_auth",
                "description": "Basic user authentication",
                "requirements": ["Login functionality", "Password validation"]
            },
            "project_path": temp_dir,
            "language": "python"
        }
        
        dev_result = await developer.process_task(dev_task, context)
        results["developer"] = dev_result.get("status") == "success"
        print(f"   {'✅' if results['developer'] else '❌'} Developer Agent")
    
    # Test QA Agent
    print("🔍 Testing QA Agent...")
    qa = QAAgent("qa-test")
    with tempfile.TemporaryDirectory() as temp_dir:
        qa_task = {
            "type": "create_test_suite",
            "project_path": temp_dir,
            "test_types": ["unit", "integration"],
            "requirements": ["Test user authentication", "Test data validation"]
        }
        
        qa_result = await qa.process_task(qa_task, context)
        results["qa"] = qa_result.get("status") == "success"
        print(f"   {'✅' if results['qa'] else '❌'} QA Agent")
    
    # Summary
    successful_agents = sum(results.values())
    total_agents = len(results)
    
    print(f"\n📊 Individual Agent Test Results:")
    print(f"   Successful: {successful_agents}/{total_agents}")
    print(f"   Success Rate: {(successful_agents/total_agents)*100:.1f}%")
    
    return results


async def test_team_collaboration():
    """Test full team collaboration on a sample project."""
    
    print("\n🤝 Testing Team Collaboration...")
    print("=" * 50)
    
    # Create AI agent team
    team = AIAgentTeam()
    
    # Sample project specification
    project_spec = {
        "project_id": "sample-ecommerce-001",
        "name": "E-commerce Platform",
        "description": "Modern e-commerce platform with user management and shopping cart",
        "requirements": [
            "User registration and authentication",
            "Product catalog browsing",
            "Shopping cart functionality",
            "Order processing",
            "Payment integration",
            "Admin dashboard"
        ],
        "business_goals": [
            "Increase online sales",
            "Improve user experience",
            "Reduce cart abandonment",
            "Enhance security"
        ],
        "personas": [
            {
                "name": "Customer",
                "id": "customer-001",
                "primary_goal": "Find and purchase products easily"
            },
            {
                "name": "Admin",
                "id": "admin-001", 
                "primary_goal": "Manage products and orders efficiently"
            }
        ],
        "non_functional_requirements": {
            "scalability": {"level": "high", "concurrent_users": 1000},
            "performance": {"response_time": "< 300ms", "throughput": "500 rps"},
            "security": {"authentication": "required", "data_encryption": "required"}
        },
        "constraints": [
            "Budget: $50,000",
            "Timeline: 3 months",
            "Team size: 5 developers",
            "Must use cloud deployment"
        ],
        "team_expertise": ["Python", "JavaScript", "React", "PostgreSQL", "AWS"],
        "budget": {"development": 40000, "infrastructure": 10000},
        "sprint_goal": "Implement core user authentication and product catalog"
    }
    
    # Execute full development workflow
    print("🚀 Starting Development Workflow...")
    
    workflow_result = await team.execute_development_workflow(project_spec)
    
    if workflow_result.get("status") == "success":
        print("✅ Team Collaboration Test PASSED")
        
        summary = workflow_result.get("summary", {})
        print(f"\n📈 Workflow Summary:")
        print(f"   Phases Completed: {summary.get('phases_completed', 0)}/{summary.get('total_phases', 0)}")
        print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        deliverables = summary.get("deliverables", {})
        print(f"\n📦 Deliverables Generated:")
        for key, value in deliverables.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        metrics = summary.get("metrics", {})
        if metrics:
            print(f"\n📊 Quality Metrics:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"   {key.replace('_', ' ').title()}: {value:.1f}%")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value}")
        
        return True
        
    else:
        print("❌ Team Collaboration Test FAILED")
        failed_phase = workflow_result.get("phase", "unknown")
        error = workflow_result.get("error", {})
        print(f"   Failed at phase: {failed_phase}")
        print(f"   Error: {error.get('message', 'Unknown error')}")
        
        return False


async def test_agent_communication():
    """Test inter-agent communication capabilities."""
    
    print("\n💬 Testing Agent Communication...")
    print("=" * 50)
    
    # Test Manager coordinating with team
    manager = ManagerAgent("manager-comm")
    context = AgentContext(project_id="comm-test", sprint_id="sprint-comm")
    
    # Test daily standup coordination
    standup_task = {
        "type": "coordinate",
        "coordination_type": "daily_standup"
    }
    
    standup_result = await manager.process_task(standup_task, context)
    
    if standup_result.get("status") == "success":
        print("✅ Manager-Team Communication works")
        
        coordination = standup_result.get("coordination_result", {})
        agents_checked = len(coordination.get("agent_statuses", {}))
        blockers = len(coordination.get("blockers", []))
        priorities = len(coordination.get("priorities", []))
        
        print(f"   👥 Agents Coordinated: {agents_checked}")
        print(f"   🚫 Blockers Identified: {blockers}")
        print(f"   📋 Priorities Set: {priorities}")
        
        return True
    else:
        print("❌ Manager-Team Communication failed")
        return False


async def test_quality_assurance():
    """Test quality assurance and validation."""
    
    print("\n🛡️ Testing Quality Assurance...")
    print("=" * 50)
    
    manager = ManagerAgent("manager-qa")
    context = AgentContext(project_id="qa-test", sprint_id="sprint-qa")
    
    # Test different types of work validation
    test_cases = [
        {
            "name": "Developer Output",
            "task": {
                "type": "validate",
                "agent_id": "dev-001",
                "agent_role": "developer",
                "output": {
                    "code": "class UserAuth: pass",
                    "tests": ["test_auth_valid", "test_auth_invalid"],
                    "test_coverage": 0.85,
                    "documentation": "Authentication implementation"
                }
            },
            "expected": True
        },
        {
            "name": "PM Output",
            "task": {
                "type": "validate",
                "agent_id": "pm-001", 
                "agent_role": "pm",
                "output": {
                    "user_stories": [
                        {"title": "User Login", "acceptance_criteria": ["Valid login"], "priority": "high"}
                    ]
                }
            },
            "expected": True
        },
        {
            "name": "QA Output",
            "task": {
                "type": "validate",
                "agent_id": "qa-001",
                "agent_role": "qa",
                "output": {
                    "test_cases": ["TC001", "TC002"],
                    "test_results": {"passed": 7, "failed": 3},
                    "pass_rate": 0.70,  # Below threshold
                    "bug_report": []
                }
            },
            "expected": False  # Should fail due to low pass rate
        }
    ]
    
    passed_validations = 0
    
    for test_case in test_cases:
        result = await manager.process_task(test_case["task"], context)
        
        is_approved = result.get("approved", False)
        expected = test_case["expected"]
        
        if is_approved == expected:
            passed_validations += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"   {status} {test_case['name']}: {'APPROVED' if is_approved else 'REJECTED'}")
        
        if result.get("validation_result"):
            score = result["validation_result"].get("score", 0)
            print(f"      Quality Score: {score:.2f}")
    
    success_rate = (passed_validations / len(test_cases)) * 100
    print(f"\n📊 Quality Validation Results:")
    print(f"   Passed: {passed_validations}/{len(test_cases)}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    return success_rate >= 80  # 80% success threshold


async def main():
    """Run comprehensive AI Agent Team tests."""
    
    print("🤖 AI Agent Development Team - Integration Test")
    print("=" * 60)
    print("Testing complete team capabilities and collaboration...")
    
    test_results = {}
    
    # Test 1: Individual Agent Capabilities
    individual_results = await test_individual_agents()
    test_results["individual_agents"] = all(individual_results.values())
    
    # Test 2: Team Collaboration
    collaboration_result = await test_team_collaboration()
    test_results["team_collaboration"] = collaboration_result
    
    # Test 3: Agent Communication
    communication_result = await test_agent_communication()
    test_results["agent_communication"] = communication_result
    
    # Test 4: Quality Assurance
    quality_result = await test_quality_assurance()
    test_results["quality_assurance"] = quality_result
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 AI Agent Team Integration Test Complete!")
    
    successful_tests = sum(test_results.values())
    total_tests = len(test_results)
    overall_success_rate = (successful_tests / total_tests) * 100
    
    print(f"\n📊 Overall Test Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Summary:")
    print(f"   Tests Passed: {successful_tests}/{total_tests}")
    print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
    
    if overall_success_rate >= 80:
        print("\n🏆 AI Agent Development Team is READY for production!")
        print("💡 The team can handle complex development projects with:")
        print("   • Requirements analysis and user story creation")
        print("   • System architecture design and technology selection") 
        print("   • Feature implementation with MCP capabilities")
        print("   • Comprehensive testing and quality assurance")
        print("   • Team coordination and workflow management")
    else:
        print("\n⚠️ AI Agent Development Team needs improvement")
        print("💡 Focus on failing test areas for better performance")
    
    print(f"\n🚀 Ready to start building amazing software with AI agents!")


if __name__ == "__main__":
    asyncio.run(main())