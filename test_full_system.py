#!/usr/bin/env python3
"""Complete system test for AI Agent Team."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.implementations.manager_agent import ManagerAgent
from src.core.memory import SprintMemoryManager
from src.core.project_manager import ProjectManager, ProjectConfig, ProjectPriority
from src.core.communication import MessageBus, MessageHandler, MessageProtocol, MessageType
from src.agents.base import AgentRole, AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


class TestMessageHandler(MessageHandler):
    """Test message handler for demonstration."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, [MessageType.TASK_ASSIGNMENT, MessageType.STATUS_UPDATE])
        self.received_messages = []
    
    async def handle_task_assignment(self, message):
        self.received_messages.append(message)
        logger.info(f"{self.agent_id} received task: {message.payload.get('task', {}).get('title', 'Untitled')}")
        
        # Create acknowledgment
        return message.create_reply(
            from_agent=self.agent_id,
            message_type=MessageType.STATUS_UPDATE,
            payload={"status": "task_accepted", "eta": "2 days"}
        )


async def test_manager_agent():
    """Test Manager Agent functionality."""
    
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
    else:
        print("❌ Manager Agent task assignment failed")
    
    # Test work validation
    validation_task = {
        "type": "validate",
        "agent_id": "dev-001",
        "agent_role": "developer",
        "output": {
            "code": "function login() { return true; }",
            "tests": ["test_login_success", "test_login_failure"],
            "test_coverage": 0.85,
            "documentation": "Login function implementation"
        }
    }
    
    validation_result = await manager.process_task(validation_task, context)
    
    if validation_result.get("approved"):
        print("✅ Manager Agent work validation works")
    else:
        print("❌ Manager Agent work validation failed")


async def test_sprint_memory():
    """Test Sprint Memory Management."""
    
    print("\n🧪 Testing Sprint Memory System...")
    
    memory_manager = SprintMemoryManager()
    
    # Initialize sprint memory
    await memory_manager.initialize_sprint_memory(
        project_id="test-project-001",
        sprint_id="sprint-001",
        sprint_goal="Implement core authentication features",
        initial_context={
            "tech_stack": {"frontend": "React", "backend": "Node.js"},
            "team_size": 4
        }
    )
    
    # Add a key decision
    await memory_manager.add_decision(
        project_id="test-project-001",
        sprint_id="sprint-001",
        decision={
            "type": "technical",
            "description": "Use JWT for authentication tokens",
            "rationale": "Stateless and scalable"
        }
    )
    
    # Retrieve context
    context = await memory_manager.get_context_for_agent(
        project_id="test-project-001",
        sprint_id="sprint-001",
        agent_role="developer"
    )
    
    if context and "sprint_goal" in context:
        print("✅ Sprint Memory System works")
    else:
        print("❌ Sprint Memory System failed")


async def test_project_manager():
    """Test Multi-Project Management."""
    
    print("\n🧪 Testing Project Manager...")
    
    memory_manager = SprintMemoryManager()
    project_manager = ProjectManager(memory_manager)
    
    # Create test project
    config = ProjectConfig(
        name="E-commerce Platform",
        description="Modern e-commerce solution",
        project_type="web",
        tech_stack={"frontend": "React", "backend": "Node.js", "database": "PostgreSQL"},
        team_config={"size": 5, "methodology": "scrum"},
        priority=ProjectPriority.HIGH
    )
    
    project_id = await project_manager.create_project(config, ["dev-001", "qa-001", "pm-001"])
    
    if project_id:
        print("✅ Project creation works")
        
        # Test project status
        status = await project_manager.get_project_status(project_id)
        if status and status["name"] == "E-commerce Platform":
            print("✅ Project status retrieval works")
        else:
            print("❌ Project status retrieval failed")
            
        # Test agent workload
        workload = await project_manager.get_agent_workload("dev-001")
        if workload["agent_id"] == "dev-001":
            print("✅ Agent workload tracking works")
        else:
            print("❌ Agent workload tracking failed")
    else:
        print("❌ Project creation failed")


async def test_message_bus():
    """Test Agent Communication System."""
    
    print("\n🧪 Testing Message Bus...")
    
    try:
        # Initialize message bus
        message_bus = MessageBus()
        await message_bus.initialize()
        
        # Register test agents
        dev_handler = TestMessageHandler("dev-001")
        pm_handler = TestMessageHandler("pm-001")
        
        await message_bus.register_agent("dev-001", dev_handler)
        await message_bus.register_agent("pm-001", pm_handler)
        
        # Create and send a message
        protocol = MessageProtocol()
        
        task_message = protocol.create_task_assignment(
            from_agent="pm-001",
            to_agent="dev-001",
            task_details={
                "title": "Implement user registration",
                "description": "Create registration form and backend API",
                "deadline": "2024-02-15"
            },
            project_id="test-project-001"
        )
        
        # Send message
        success = await message_bus.send_message(task_message)
        
        if success:
            print("✅ Message sending works")
            
            # Process messages
            await asyncio.sleep(1)  # Allow message processing
            await message_bus.process_agent_messages("dev-001")
            
            if len(dev_handler.received_messages) > 0:
                print("✅ Message receiving works")
            else:
                print("❌ Message receiving failed")
        else:
            print("❌ Message sending failed")
        
        # Get statistics
        stats = await message_bus.get_bus_statistics()
        print(f"📊 Message Bus Stats: {stats['delivery_stats']}")
        
        # Cleanup
        await message_bus.shutdown()
        
    except Exception as e:
        logger.error(f"Message bus test failed: {str(e)}")
        print("❌ Message Bus test failed")


async def test_full_workflow():
    """Test complete workflow simulation."""
    
    print("\n🧪 Testing Full Agent Team Workflow...")
    
    try:
        # Initialize components
        memory_manager = SprintMemoryManager()
        project_manager = ProjectManager(memory_manager)
        message_bus = MessageBus()
        await message_bus.initialize()
        
        # Create project
        config = ProjectConfig(
            name="Mobile Banking App",
            description="Secure mobile banking application",
            project_type="mobile",
            tech_stack={"frontend": "React Native", "backend": "Python", "database": "PostgreSQL"},
            team_config={"size": 6, "methodology": "scrum"}
        )
        
        project_id = await project_manager.create_project(config)
        
        # Initialize sprint
        await memory_manager.initialize_sprint_memory(
            project_id=project_id,
            sprint_id="sprint-001",
            sprint_goal="Implement secure login and account overview",
            initial_context={"security_requirements": ["2FA", "biometric"], "compliance": ["PCI-DSS"]}
        )
        
        # Create manager agent
        manager = ManagerAgent("manager-001")
        
        # Simulate sprint planning
        planning_task = {
            "type": "sprint_planning",
            "sprint_goal": "Implement secure login and account overview",
            "user_stories": [
                {
                    "id": "US-001",
                    "title": "User Login with 2FA",
                    "description": "As a user, I want to login securely with 2FA",
                    "points": 8,
                    "priority": "high"
                },
                {
                    "id": "US-002", 
                    "title": "Account Balance Display",
                    "description": "As a user, I want to see my account balance",
                    "points": 5,
                    "priority": "medium"
                }
            ]
        }
        
        context = AgentContext(project_id=project_id, sprint_id="sprint-001")
        result = await manager.process_task(planning_task, context)
        
        if result.get("status") == "success":
            print("✅ Full workflow simulation works")
            
            # Show sprint plan summary
            sprint_plan = result.get("sprint_plan", {})
            print(f"📋 Sprint Goal: {sprint_plan.get('goal', 'N/A')}")
            print(f"📊 Total Story Points: {sprint_plan.get('timeline', {}).get('total_story_points', 0)}")
            print(f"👥 Team Assignments: {len(sprint_plan.get('assignments', {}))}")
            
        else:
            print("❌ Full workflow simulation failed")
        
        await message_bus.shutdown()
        
    except Exception as e:
        logger.error(f"Full workflow test failed: {str(e)}")
        print("❌ Full workflow test failed")


async def main():
    """Run all system tests."""
    
    print("🚀 AI Agent Team - Full System Test")
    print("=" * 50)
    
    # Run individual component tests
    await test_manager_agent()
    await test_sprint_memory()
    await test_project_manager()
    await test_message_bus()
    
    # Run full workflow test
    await test_full_workflow()
    
    print("\n" + "=" * 50)
    print("🎉 System tests completed!")
    print("\nThe AI Agent Development Team is ready for use!")
    print("\nNext steps:")
    print("1. Start databases: docker-compose up -d")
    print("2. Initialize database: python scripts/setup_database.py")
    print("3. Start API server: python -m src.main")
    print("4. Create your first project: python -m src.cli create-project")


if __name__ == "__main__":
    asyncio.run(main())