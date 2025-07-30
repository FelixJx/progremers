#!/usr/bin/env python3
"""Quick setup test to verify all components are working."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        from src.config import settings
        print("✅ Config loaded successfully")
        
        from src.utils import get_logger
        logger = get_logger(__name__)
        logger.info("Logger working correctly")
        print("✅ Logger working")
        
        from src.agents.base import BaseAgent, AgentRole, MCPEnabledAgent
        print("✅ Base agent classes imported")
        
        from src.core.database import Base, Project, get_db
        print("✅ Database models imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_settings():
    """Test settings configuration."""
    print("\n⚙️  Testing settings...")
    
    try:
        from src.config import settings
        
        print(f"Environment: {settings.app_env}")
        print(f"API Port: {settings.api_port}")
        
        # Test LLM configurations
        deepseek_config = settings.get_llm_config("deepseek")
        print(f"DeepSeek API configured: {'✅' if deepseek_config['api_key'] else '❌'}")
        
        qwen_config = settings.get_llm_config("qwen-max")
        print(f"Qwen API configured: {'✅' if qwen_config['api_key'] else '❌'}")
        
        local_config = settings.get_llm_config("local")
        print(f"Local LM Studio: {local_config['base_url']}")
        
        print("✅ Settings test passed")
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {str(e)}")
        return False

def test_agent_creation():
    """Test agent creation."""
    print("\n🤖 Testing agent creation...")
    
    try:
        from src.agents.base import BaseAgent, AgentRole
        from src.config import settings
        
        # Create a mock agent class
        class TestAgent(BaseAgent):
            async def process_task(self, task, context):
                return {"status": "test_success"}
            
            async def validate_output(self, output):
                return True
            
            def get_prompt_template(self):
                return "Test agent prompt"
        
        # Create agent instance
        agent = TestAgent("test-001", AgentRole.DEVELOPER)
        print(f"Agent created: {agent}")
        print(f"Agent role: {agent.role}")
        print(f"Agent LLM provider: {agent.llm_provider}")
        
        print("✅ Agent creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Agent creation test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 AI Agent Team - Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_settings,
        test_agent_creation,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Start databases: docker-compose up -d")
        print("2. Initialize database: python scripts/setup_database.py")
        print("3. Check status: python -m src.cli status")
        print("4. Create a project: python -m src.cli create-project")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)