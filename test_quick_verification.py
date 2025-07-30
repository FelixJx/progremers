#!/usr/bin/env python3
"""Quick verification test for key agents after fixes."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.implementations.pm_agent import PMAgent
from src.agents.implementations.manager_agent import ManagerAgent
from src.agents.base import AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


async def test_pm_agent_fix():
    """Test PM Agent with string requirements."""
    print("🧪 Testing PM Agent Fix...")
    
    pm = PMAgent("pm-test")
    
    pm_task = {
        "type": "analyze_requirements",
        "requirements": [
            "User authentication system",  # String requirement
            "Data storage and retrieval",   # String requirement
            "RESTful API endpoints"         # String requirement
        ],
        "business_goals": ["Improve user engagement", "Increase security"]
    }
    
    context = AgentContext(project_id="test-fix", sprint_id="sprint-fix")
    
    result = await pm.process_task(pm_task, context)
    
    if result.get("status") == "success":
        print("✅ PM Agent works with string requirements")
        analysis = result.get("analysis", {})
        print(f"   📋 Requirements processed: {analysis.get('total_requirements', 0)}")
        return True
    else:
        print("❌ PM Agent still has issues")
        print(f"   Error: {result.get('message', 'Unknown error')}")
        return False


async def test_context_management():
    """Test enhanced context management."""
    print("\n🧪 Testing Enhanced Context Management...")
    
    manager = ManagerAgent("manager-context-test")
    context = AgentContext(project_id="context-test", sprint_id="sprint-context")
    
    # Add various types of context
    await manager.add_task_context({
        "type": "development",
        "title": "Implement user authentication",
        "priority": "high"
    })
    
    await manager.add_conversation_context(
        "Discussed technical approach with architect team", 
        "arch-001"
    )
    
    await manager.add_decision_context({
        "decision": "Use PostgreSQL for primary database",
        "rationale": "Better ACID compliance and team expertise"
    })
    
    # Get optimized context
    optimized_context = await manager.get_optimized_context("authentication database")
    
    if optimized_context:
        print("✅ Enhanced Context Management works")
        print(f"   📊 Context sections: {len(optimized_context.get('context_sections', {}))}")
        print(f"   🔢 Total tokens: {optimized_context.get('total_tokens', 0)}")
        
        # Show context stats
        stats = manager.get_context_stats()
        print(f"   📈 Context utilization: {stats.get('token_utilization', 0):.2%}")
        print(f"   📋 Total items: {stats.get('total_items', 0)}")
        return True
    else:
        print("❌ Enhanced Context Management failed")
        return False


async def test_team_coordination_simple():
    """Test simple team coordination."""
    print("\n🧪 Testing Team Coordination...")
    
    manager = ManagerAgent("manager-coord-test")
    context = AgentContext(project_id="coord-test", sprint_id="sprint-coord")
    
    coordination_task = {
        "type": "coordinate",
        "coordination_type": "daily_standup"
    }
    
    result = await manager.process_task(coordination_task, context)
    
    if result.get("status") == "success":
        print("✅ Team Coordination works")
        coord_result = result.get("coordination_result", {})
        print(f"   👥 Agents coordinated: {len(coord_result.get('agent_statuses', {}))}")
        print(f"   🚫 Blockers identified: {len(coord_result.get('blockers', []))}")
        return True
    else:
        print("❌ Team Coordination failed")
        return False


async def main():
    """Run quick verification tests."""
    
    print("🚀 Quick Verification Test")
    print("=" * 40)
    
    results = {}
    
    # Test 1: PM Agent Fix
    results["pm_fix"] = await test_pm_agent_fix()
    
    # Test 2: Context Management
    results["context_management"] = await test_context_management()
    
    # Test 3: Team Coordination
    results["team_coordination"] = await test_team_coordination_simple()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Verification Results:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All fixes verified! Ready for full team integration test.")
    else:
        print("⚠️ Some issues remain. Check failed tests.")


if __name__ == "__main__":
    asyncio.run(main())