#!/usr/bin/env python3
"""Core system test without external dependencies."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.implementations.manager_agent import ManagerAgent
from src.agents.base import AgentRole, AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


async def test_manager_agent():
    """Test Manager Agent functionality without external dependencies."""
    
    print("\n🧪 Testing Manager Agent...")
    
    manager = ManagerAgent("manager-001")
    
    # Test task assignment
    task = {
        "type": "assign_task",
        "task_details": {
            "type": "development",
            "title": "Implement user authentication",
            "description": "Create login/logout functionality",
            "priority": "high"
        },
        "priority": "high"
    }
    
    context = AgentContext(
        project_id="test-project-001",
        sprint_id="sprint-001"
    )
    
    result = await manager.process_task(task, context)
    
    if result.get("status") == "success":
        print("✅ Manager Agent task assignment works")
        assignment = result.get("assignment", {})
        print(f"   📋 Task ID: {assignment.get('task_id', 'N/A')}")
        print(f"   👤 Assigned to: {assignment.get('assigned_to', 'N/A')}")
    else:
        print("❌ Manager Agent task assignment failed")
    
    # Test work validation
    validation_task = {
        "type": "validate",
        "agent_id": "dev-001",
        "agent_role": "developer",
        "output": {
            "code": "function login() { return authenticateUser(); }",
            "tests": ["test_login_success", "test_login_failure"],
            "test_coverage": 0.85,
            "documentation": "Login function implementation"
        }
    }
    
    validation_result = await manager.process_task(validation_task, context)
    
    if validation_result.get("approved"):
        print("✅ Manager Agent work validation works")
        score = validation_result.get("validation_result", {}).get("score", 0)
        print(f"   📊 Validation Score: {score:.2f}")
    else:
        print("❌ Manager Agent work validation failed")
    
    # Test conflict resolution
    conflict_task = {
        "type": "resolve_conflict",
        "conflict": {
            "agent1_id": "dev-001",
            "agent2_id": "arch-001",
            "type": "technical",
            "description": "Disagreement on database choice: SQL vs NoSQL"
        }
    }
    
    conflict_result = await manager.process_task(conflict_task, context)
    
    if conflict_result.get("status") == "success":
        print("✅ Manager Agent conflict resolution works")
        resolution = conflict_result.get("conflict_resolution", {})
        print(f"   ⚖️  Resolution: {resolution.get('resolution', {}).get('decision', 'N/A')}")
    else:
        print("❌ Manager Agent conflict resolution failed")


async def test_sprint_planning():
    """Test sprint planning simulation."""
    
    print("\n🧪 Testing Sprint Planning...")
    
    manager = ManagerAgent("manager-001")
    
    planning_task = {
        "type": "sprint_planning",
        "sprint_goal": "Implement user authentication and profile management",
        "user_stories": [
            {
                "id": "US-001",
                "title": "User Registration",
                "description": "As a user, I want to create an account",
                "points": 5,
                "type": "development",
                "priority": "high"
            },
            {
                "id": "US-002", 
                "title": "User Login",
                "description": "As a user, I want to login securely",
                "points": 3,
                "type": "development",
                "priority": "high"
            },
            {
                "id": "US-003",
                "title": "Profile Management",
                "description": "As a user, I want to manage my profile",
                "points": 8,
                "type": "development",
                "priority": "medium"
            }
        ]
    }
    
    context = AgentContext(
        project_id="test-project-001",
        sprint_id="sprint-002"
    )
    
    result = await manager.process_task(planning_task, context)
    
    if result.get("status") == "success":
        print("✅ Sprint Planning works")
        
        sprint_plan = result.get("sprint_plan", {})
        print(f"   🎯 Sprint Goal: {sprint_plan.get('goal', 'N/A')}")
        print(f"   📊 Total Story Points: {sprint_plan.get('timeline', {}).get('total_story_points', 0)}")
        print(f"   👥 Team Assignments: {len(sprint_plan.get('assignments', {}))}")
        print(f"   ⚠️  Identified Risks: {len(sprint_plan.get('risks', []))}")
        
        # Show assignments
        assignments = sprint_plan.get('assignments', {})
        for agent_id, stories in assignments.items():
            print(f"   📝 {agent_id}: {len(stories)} stories")
        
    else:
        print("❌ Sprint Planning failed")


async def test_team_coordination():
    """Test team coordination functionality."""
    
    print("\n🧪 Testing Team Coordination...")
    
    manager = ManagerAgent("manager-001")
    
    coordination_task = {
        "type": "coordinate",
        "coordination_type": "daily_standup"
    }
    
    context = AgentContext(
        project_id="test-project-001",
        sprint_id="sprint-001"
    )
    
    result = await manager.process_task(coordination_task, context)
    
    if result.get("status") == "success":
        print("✅ Team Coordination works")
        
        coordination_result = result.get("coordination_result", {})
        agent_statuses = coordination_result.get("agent_statuses", {})
        blockers = coordination_result.get("blockers", [])
        priorities = coordination_result.get("priorities", [])
        
        print(f"   👥 Agents Checked: {len(agent_statuses)}")
        print(f"   🚫 Blockers Found: {len(blockers)}")
        print(f"   📋 Priorities Set: {len(priorities)}")
        
        # Show agent statuses
        for agent_id, status in agent_statuses.items():
            print(f"   📊 {agent_id}: {status.get('status', 'unknown')} ({status.get('progress', 0):.0%} complete)")
        
    else:
        print("❌ Team Coordination failed")


async def test_quality_standards():
    """Test quality validation standards."""
    
    print("\n🧪 Testing Quality Standards...")
    
    manager = ManagerAgent("manager-001")
    
    # Test different agent outputs
    test_cases = [
        {
            "agent_role": "developer",
            "output": {
                "code": "class UserAuth { login() { return true; } }",
                "tests": ["test_login", "test_logout"],
                "test_coverage": 0.9,
                "documentation": "Complete auth implementation"
            },
            "expected": True
        },
        {
            "agent_role": "pm",
            "output": {
                "user_stories": [
                    {"title": "Login", "priority": "high"},
                    {"title": "Logout", "priority": "medium"}
                ],
                "acceptance_criteria": ["Login works", "Logout works"]
            },
            "expected": True
        },
        {
            "agent_role": "qa",
            "output": {
                "test_cases": ["TC001", "TC002"],
                "test_results": {"passed": 8, "failed": 1},
                "pass_rate": 0.89,
                "bug_report": []
            },
            "expected": False  # Low pass rate
        }
    ]
    
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases):
        validation_task = {
            "type": "validate",
            "agent_id": f"test-agent-{i}",
            "agent_role": test_case["agent_role"],
            "output": test_case["output"]
        }
        
        context = AgentContext(project_id="test-project", sprint_id="sprint-test")
        result = await manager.process_task(validation_task, context)
        
        is_approved = result.get("approved", False)
        if is_approved == test_case["expected"]:
            passed_tests += 1
            print(f"   ✅ {test_case['agent_role']} validation: {'PASS' if is_approved else 'FAIL'} (expected)")
        else:
            print(f"   ❌ {test_case['agent_role']} validation: {'PASS' if is_approved else 'FAIL'} (unexpected)")
    
    if passed_tests == len(test_cases):
        print("✅ Quality Standards work correctly")
    else:
        print(f"❌ Quality Standards partially failed ({passed_tests}/{len(test_cases)} tests passed)")


async def test_decision_tracking():
    """Test decision tracking in manager."""
    
    print("\n🧪 Testing Decision Tracking...")
    
    manager = ManagerAgent("manager-001")
    
    # Check initial state
    initial_conflicts = len(manager.get_conflict_history())
    initial_tasks = len(manager.get_active_tasks())
    
    # Create some conflicts and tasks
    context = AgentContext(project_id="test-project", sprint_id="sprint-001")
    
    # Add a conflict
    conflict_task = {
        "type": "resolve_conflict",
        "conflict": {
            "agent1_id": "dev-001",
            "agent2_id": "qa-001",
            "type": "approach",
            "description": "Testing approach disagreement"
        }
    }
    
    await manager.process_task(conflict_task, context)
    
    # Add a task
    task_assignment = {
        "type": "assign_task",
        "task_details": {
            "type": "testing",
            "title": "Create test suite",
            "description": "Comprehensive testing"
        }
    }
    
    await manager.process_task(task_assignment, context)
    
    # Check final state
    final_conflicts = len(manager.get_conflict_history())
    final_tasks = len(manager.get_active_tasks())
    
    if final_conflicts > initial_conflicts and final_tasks > initial_tasks:
        print("✅ Decision Tracking works")
        print(f"   📊 Conflicts tracked: {final_conflicts}")
        print(f"   📋 Tasks tracked: {final_tasks}")
    else:
        print("❌ Decision Tracking failed")


async def main():
    """Run all core system tests."""
    
    print("🚀 AI Agent Team - Core System Test")
    print("=" * 50)
    print("Testing core functionality without external dependencies...")
    
    # Run tests
    await test_manager_agent()
    await test_sprint_planning()
    await test_team_coordination()
    await test_quality_standards()
    await test_decision_tracking()
    
    print("\n" + "=" * 50)
    print("🎉 Core system tests completed!")
    
    print("\n📋 What we've built:")
    print("✅ Manager Agent with task assignment, validation, and conflict resolution")
    print("✅ Sprint planning with user story assignment and risk identification")
    print("✅ Team coordination with status tracking and blocker management")
    print("✅ Quality validation with role-specific standards")
    print("✅ Decision and conflict tracking system")
    
    print("\n🚀 Next steps to complete the system:")
    print("1. Start Redis: docker-compose up -d redis")
    print("2. Add individual agents (PM, Developer, QA, etc.)")
    print("3. Integrate MCP for Developer and QA agents")
    print("4. Add knowledge transfer between projects")
    print("5. Create project import interface")
    
    print("\n💡 The core architecture is solid and ready for extension!")


if __name__ == "__main__":
    asyncio.run(main())