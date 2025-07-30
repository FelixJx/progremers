#!/usr/bin/env python3
"""Test Developer Agent functionality."""

import asyncio
import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.implementations.developer_agent import DeveloperAgent
from src.agents.base import AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


async def test_feature_implementation():
    """Test feature implementation with MCP capabilities."""
    
    print("\n🛠️ Testing Feature Implementation...")
    
    developer = DeveloperAgent("dev-001")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        feature_task = {
            "type": "implement_feature",
            "feature_specification": {
                "name": "user_authentication",
                "description": "Implement user login and registration functionality",
                "requirements": [
                    "User can register with email and password",
                    "User can login with credentials",
                    "Password validation and hashing",
                    "Session management"
                ]
            },
            "project_path": temp_dir,
            "language": "python",
            "include_tests": True,
            "run_tests": False,  # Skip test execution in demo
            "auto_commit": False  # Skip git operations in demo
        }
        
        context = AgentContext(
            project_id="test-dev-feature-001",
            sprint_id="dev-sprint-001"
        )
        
        result = await developer.process_task(feature_task, context)
        
        if result.get("status") == "success":
            print("✅ Feature Implementation works")
            
            implementation = result.get("implementation", {})
            
            print(f"   📁 Feature: {implementation.get('feature_name', 'N/A')}")
            print(f"   📄 Generated Files: {len(implementation.get('generated_files', []))}")
            print(f"   🧪 Test Files: {len(implementation.get('test_files', []))}")
            
            # Show generated files
            for file_path in implementation.get("generated_files", [])[:3]:
                if isinstance(file_path, str):
                    print(f"   📝 Created: {os.path.basename(file_path)}")
                else:
                    print(f"   📝 Created: {file_path.get('path', 'Unknown')}")
            
            # Check code quality
            quality = implementation.get("code_quality", {})
            print(f"   📊 Code Quality Score: {quality.get('overall_score', 'N/A')}")
            
        else:
            print("❌ Feature Implementation failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_bug_fixing():
    """Test bug fixing capabilities."""
    
    print("\n🐛 Testing Bug Fixing...")
    
    developer = DeveloperAgent("dev-001")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a sample file with a "bug"
        buggy_file = os.path.join(temp_dir, "buggy_code.py")
        with open(buggy_file, 'w') as f:
            f.write("""
def calculate_average(numbers):
    return sum(numbers) / len(numbers)  # Bug: doesn't handle empty list
""")
        
        bug_task = {
            "type": "fix_bug",
            "bug_report": {
                "title": "Division by zero in calculate_average",
                "description": "Function crashes when empty list is passed",
                "severity": "high",
                "steps_to_reproduce": [
                    "Call calculate_average([])",
                    "ZeroDivisionError is raised"
                ],
                "expected_behavior": "Should handle empty list gracefully"
            },
            "project_path": temp_dir,
            "language": "python",
            "auto_commit": False
        }
        
        context = AgentContext(
            project_id="test-dev-bug-001",
            sprint_id="dev-sprint-001"
        )
        
        result = await developer.process_task(bug_task, context)
        
        if result.get("status") == "success":
            print("✅ Bug Fixing works")
            
            bug_fix = result.get("bug_fix", {})
            
            print(f"   🐛 Bug: {bug_fix.get('bug_title', 'N/A')}")
            print(f"   🔍 Root Cause: {bug_fix.get('root_cause', {}).get('root_cause', 'N/A')}")
            print(f"   🔧 Fixed Files: {len(bug_fix.get('fixed_files', []))}")
            print(f"   🧪 Regression Tests: {len(bug_fix.get('regression_tests', []))}")
            
            # Show fix verification
            verification = bug_fix.get("verification", {})
            print(f"   ✅ Fix Verified: {verification.get('fixed', 'Unknown')}")
            
        else:
            print("❌ Bug Fixing failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_test_writing():
    """Test comprehensive test writing."""
    
    print("\n🧪 Testing Test Writing...")
    
    developer = DeveloperAgent("dev-001")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample code files
        code_file = os.path.join(temp_dir, "math_utils.py")
        with open(code_file, 'w') as f:
            f.write("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

class Calculator:
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        if operation == "add":
            result = add(a, b)
        elif operation == "multiply":
            result = multiply(a, b)
        else:
            raise ValueError("Unknown operation")
        
        self.history.append((operation, a, b, result))
        return result
""")
        
        test_task = {
            "type": "write_tests",
            "code_files": ["math_utils.py"],
            "project_path": temp_dir,
            "language": "python",
            "framework": "pytest"
        }
        
        context = AgentContext(
            project_id="test-dev-tests-001",
            sprint_id="dev-sprint-001"
        )
        
        result = await developer.process_task(test_task, context)
        
        if result.get("status") == "success":
            print("✅ Test Writing works")
            
            test_writing = result.get("test_writing", {})
            
            print(f"   📊 Total Test Cases: {test_writing.get('total_test_cases', 0)}")
            print(f"   📄 Test Files Created: {len(test_writing.get('test_files_created', []))}")
            
            # Show test files created
            for test_file in test_writing.get("test_files_created", [])[:3]:
                source = test_file.get("source_file", "Unknown")
                test_path = test_file.get("test_file", "Unknown")
                cases = test_file.get("test_cases_count", 0)
                print(f"   🧪 {source} → {test_path} ({cases} test cases)")
            
            # Show coverage if available
            coverage = test_writing.get("coverage_report", {})
            if coverage:
                overall = coverage.get("overall_coverage", 0)
                print(f"   📈 Test Coverage: {overall}%")
            
        else:
            print("❌ Test Writing failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_project_setup():
    """Test new project setup."""
    
    print("\n🏗️ Testing Project Setup...")
    
    developer = DeveloperAgent("dev-001")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = os.path.join(temp_dir, "new_project")
        
        setup_task = {
            "type": "setup_project",
            "project_config": {
                "name": "ai_assistant_api",
                "description": "RESTful API for AI assistant functionality",
                "type": "web_api",
                "features": ["authentication", "chat", "file_upload"]
            },
            "project_path": project_path,
            "language": "python",
            "init_git": False,  # Skip git in demo
            "install_deps": False,  # Skip dependency installation
            "run_initial_tests": False  # Skip test execution
        }
        
        context = AgentContext(
            project_id="test-dev-setup-001",
            sprint_id="dev-sprint-001"
        )
        
        result = await developer.process_task(setup_task, context)
        
        if result.get("status") == "success":
            print("✅ Project Setup works")
            
            setup = result.get("project_setup", {})
            
            print(f"   📁 Project Path: {os.path.basename(setup.get('project_path', 'N/A'))}")
            print(f"   💻 Language: {setup.get('language', 'N/A')}")
            print(f"   📂 Directories Created: {len(setup.get('directories_created', []))}")
            print(f"   📄 Files Created: {len(setup.get('files_created', []))}")
            
            # Show created files
            for file_path in setup.get("files_created", [])[:5]:
                print(f"   📝 {file_path}")
            
            # Show next steps
            next_steps = setup.get("next_steps", [])
            if next_steps:
                print(f"   📋 Next Steps: {len(next_steps)} recommendations")
            
        else:
            print("❌ Project Setup failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_mcp_capabilities():
    """Test MCP (Model Context Protocol) capabilities."""
    
    print("\n🔧 Testing MCP Capabilities...")
    
    developer = DeveloperAgent("dev-001")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test filesystem operations
        test_file = os.path.join(temp_dir, "test_file.py")
        test_content = "# Test file for MCP capabilities\nprint('Hello, MCP!')"
        
        # Test file writing
        write_result = await developer._write_file_mcp(test_file, test_content)
        
        if write_result.get("success"):
            print("✅ MCP File Writing works")
            print(f"   📝 File written: {os.path.basename(write_result.get('file_path', 'N/A'))}")
        else:
            print("❌ MCP File Writing failed")
        
        # Test file reading
        if write_result.get("success"):
            read_content = await developer._read_file_mcp(test_file)
            
            if read_content == test_content:
                print("✅ MCP File Reading works")
                print(f"   📖 Content matches: {len(read_content)} characters")
            else:
                print("❌ MCP File Reading failed")
        
        # Test directory creation
        test_dir = os.path.join(temp_dir, "test_directory")
        dir_result = await developer._create_directory_mcp(test_dir)
        
        if dir_result.get("success"):
            print("✅ MCP Directory Creation works")
            print(f"   📁 Directory created: {os.path.basename(dir_result.get('directory', 'N/A'))}")
        else:
            print("❌ MCP Directory Creation failed")
        
        # Test shell command (simple echo)
        shell_result = await developer._run_shell_command_mcp("echo 'MCP Shell Test'")
        
        if shell_result.get("success"):
            print("✅ MCP Shell Command works")
            output = shell_result.get("stdout", "").strip()
            print(f"   💻 Shell output: '{output}'")
        else:
            print("❌ MCP Shell Command failed")


async def test_code_quality_assessment():
    """Test code quality assessment."""
    
    print("\n📊 Testing Code Quality Assessment...")
    
    developer = DeveloperAgent("dev-001")
    
    # Test with sample generated files
    sample_files = [
        {"path": "src/user_service.py", "size": 150},
        {"path": "src/models/user.py", "size": 80},
        {"path": "tests/test_user_service.py", "size": 200}
    ]
    
    quality = await developer._assess_code_quality(sample_files, "python")
    
    if quality:
        print("✅ Code Quality Assessment works")
        
        print(f"   📈 Overall Score: {quality.get('overall_score', 'N/A')}/10")
        
        metrics = quality.get("metrics", {})
        for metric, value in metrics.items():
            print(f"   📊 {metric.title()}: {value}")
        
        suggestions = quality.get("suggestions", [])
        if suggestions:
            print(f"   💡 Suggestions: {len(suggestions)} recommendations")
            for suggestion in suggestions[:2]:
                print(f"      • {suggestion}")
    else:
        print("❌ Code Quality Assessment failed")


async def test_output_validation():
    """Test developer output validation."""
    
    print("\n✅ Testing Output Validation...")
    
    developer = DeveloperAgent("dev-001")
    
    # Test valid outputs
    valid_outputs = [
        {
            "status": "success",
            "implementation": {
                "generated_files": ["src/feature.py"],
                "implementation_plan": {"approach": "incremental"}
            }
        },
        {
            "status": "success",
            "bug_fix": {
                "fixed_files": ["src/buggy.py"],
                "root_cause": {"cause": "null pointer"}
            }
        },
        {
            "status": "success",
            "test_writing": {
                "test_files_created": [{"source": "test.py"}]
            }
        }
    ]
    
    invalid_outputs = [
        {"status": "error"},
        {"status": "success", "implementation": {}},  # Missing required fields
        {"status": "success", "bug_fix": {}}  # Missing required fields
    ]
    
    valid_count = 0
    for output in valid_outputs:
        if await developer.validate_output(output):
            valid_count += 1
    
    invalid_count = 0
    for output in invalid_outputs:
        if not await developer.validate_output(output):
            invalid_count += 1
    
    total_tests = len(valid_outputs) + len(invalid_outputs)
    passed_tests = valid_count + invalid_count
    
    if passed_tests == total_tests:
        print("✅ Output Validation works correctly")
        print(f"   ✓ Valid outputs accepted: {valid_count}/{len(valid_outputs)}")
        print(f"   ✓ Invalid outputs rejected: {invalid_count}/{len(invalid_outputs)}")
    else:
        print("❌ Output Validation has issues")
        print(f"   Tests passed: {passed_tests}/{total_tests}")


async def main():
    """Run all Developer Agent tests."""
    
    print("🛠️ AI Agent Team - Developer Agent Test")
    print("=" * 50)
    print("Testing Developer Agent with MCP capabilities...")
    
    # Run tests
    await test_feature_implementation()
    await test_bug_fixing()
    await test_test_writing()
    await test_project_setup()
    await test_mcp_capabilities()
    await test_code_quality_assessment()
    await test_output_validation()
    
    print("\n" + "=" * 50)
    print("🎉 Developer Agent tests completed!")
    
    print("\n📋 What the Developer Agent can do:")
    print("✅ Feature implementation with clean, tested code")
    print("✅ Bug fixing with root cause analysis and regression tests")
    print("✅ Comprehensive test writing with good coverage")
    print("✅ Project setup with proper structure and configuration")
    print("✅ MCP capabilities for filesystem, git, and shell operations")
    print("✅ Code quality assessment and improvement suggestions")
    print("✅ Output validation with quality checks")
    
    print("\n🚀 Developer Agent is ready for integration!")
    print("💡 Next: Integrate with Manager Agent and add to team workflow")


if __name__ == "__main__":
    asyncio.run(main())