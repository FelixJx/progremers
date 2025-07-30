"""Developer Agent - Software Developer with MCP capabilities for code development."""

import json
import os
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path

from src.agents.base import BaseAgent, AgentRole, AgentStatus, AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


class CodeLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    CSHARP = "csharp"


class TestFramework(str, Enum):
    """Supported testing frameworks."""
    PYTEST = "pytest"
    JEST = "jest"
    JUNIT = "junit" 
    GOLANG_TEST = "go_test"
    CARGO_TEST = "cargo_test"
    GTEST = "gtest"
    NUNIT = "nunit"


class DevelopmentTask(str, Enum):
    """Types of development tasks."""
    IMPLEMENT_FEATURE = "implement_feature"
    FIX_BUG = "fix_bug"
    REFACTOR_CODE = "refactor_code"
    WRITE_TESTS = "write_tests"
    CODE_REVIEW = "code_review"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    UPDATE_DOCUMENTATION = "update_documentation"


class DeveloperAgent(BaseAgent):
    """
    Software Developer Agent with MCP capabilities for:
    - Code implementation and development
    - File system operations (read/write code files)
    - Git operations (commit, branch, merge)
    - Shell command execution (build, test, run)
    - Code quality assurance and testing
    - Documentation and code comments
    """
    
    def __init__(self, agent_id: str = "dev-001"):
        super().__init__(agent_id, AgentRole.DEVELOPER)
        
        # Developer-specific state
        self.current_projects = {}
        self.code_patterns = {}
        self.test_results = {}
        self.git_repos = {}
        
        # MCP capabilities configuration
        self.mcp_enabled = True
        self.filesystem_access = True
        self.git_access = True
        self.shell_access = True
        
        # Developer preferences
        self.preferred_languages = [CodeLanguage.PYTHON, CodeLanguage.TYPESCRIPT]
        self.code_style_preferences = {
            "line_length": 100,
            "indent_size": 4,
            "use_type_hints": True,
            "enforce_docstrings": True
        }
        
        # Testing configuration
        self.test_coverage_threshold = 80
        self.run_tests_before_commit = True
        self.auto_format_code = True
    
    async def process_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Process development tasks with MCP capabilities.
        
        Args:
            task: Development task details
            context: Current context
            
        Returns:
            Task processing result
        """
        task_type = task.get("type", "implement_feature")
        
        self.logger.info(f"Processing Developer task: {task_type}")
        
        try:
            if task_type == "implement_feature":
                return await self._implement_feature(task, context)
            elif task_type == "fix_bug":
                return await self._fix_bug(task, context)
            elif task_type == "write_tests":
                return await self._write_tests(task, context)
            elif task_type == "refactor_code":
                return await self._refactor_code(task, context)
            elif task_type == "code_review":
                return await self._perform_code_review(task, context)
            elif task_type == "optimize_performance":
                return await self._optimize_performance(task, context)
            elif task_type == "setup_project":
                return await self._setup_project(task, context)
            elif task_type == "run_tests":
                return await self._run_tests(task, context)
            elif task_type == "deploy_code":
                return await self._deploy_code(task, context)
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing Developer task: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _implement_feature(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Implement a new feature with MCP filesystem operations."""
        
        feature_spec = task.get("feature_specification", {})
        project_path = task.get("project_path", "./")
        language = task.get("language", CodeLanguage.PYTHON.value)
        
        self.logger.info(f"Implementing feature: {feature_spec.get('name', 'Unknown')}")
        
        # Analyze existing codebase structure
        codebase_analysis = await self._analyze_codebase_structure(project_path, language)
        
        # Design implementation approach
        implementation_plan = await self._design_implementation_plan(
            feature_spec, codebase_analysis, language
        )
        
        # Generate code files 
        generated_files = []
        for file_spec in implementation_plan.get("files_to_create", []):
            file_content = await self._generate_code_file(
                file_spec, feature_spec, language, codebase_analysis
            )
            
            if self.filesystem_access:
                file_path = os.path.join(project_path, file_spec["path"])
                write_result = await self._write_file_mcp(file_path, file_content)
                if write_result["success"]:
                    generated_files.append(file_path)
            else:
                # Store in memory if MCP not available
                generated_files.append({
                    "path": file_spec["path"],
                    "content": file_content
                })
        
        # Generate tests for the feature
        test_files = []
        if task.get("include_tests", True):
            test_specs = await self._design_test_specifications(feature_spec, implementation_plan)
            
            for test_spec in test_specs:
                test_content = await self._generate_test_file(
                    test_spec, feature_spec, language
                )
                
                if self.filesystem_access:
                    test_path = os.path.join(project_path, test_spec["path"])
                    write_result = await self._write_file_mcp(test_path, test_content)
                    if write_result["success"]:
                        test_files.append(test_path)
                else:
                    test_files.append({
                        "path": test_spec["path"],
                        "content": test_content
                    })
        
        # Run tests if requested
        test_results = {}
        if task.get("run_tests", False) and self.shell_access:
            test_results = await self._run_tests_mcp(project_path, language)
        
        # Format code if enabled
        if self.auto_format_code and self.shell_access:
            format_results = await self._format_code_mcp(project_path, language)
        
        # Commit changes if git is available
        commit_result = {}
        if task.get("auto_commit", False) and self.git_access:
            commit_message = f"Implement feature: {feature_spec.get('name', 'New Feature')}"
            commit_result = await self._git_commit_mcp(project_path, commit_message)
        
        implementation_result = {
            "feature_name": feature_spec.get("name", "Unknown"),
            "implementation_plan": implementation_plan,
            "generated_files": generated_files,
            "test_files": test_files,
            "test_results": test_results,
            "commit_result": commit_result,
            "code_quality": await self._assess_code_quality(generated_files, language),
            "documentation": await self._generate_feature_documentation(
                feature_spec, implementation_plan, generated_files
            )
        }
        
        return {
            "status": "success",
            "implementation": implementation_result
        }
    
    async def _fix_bug(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Fix a bug with analysis and testing."""
        
        bug_report = task.get("bug_report", {})
        project_path = task.get("project_path", "./")
        language = task.get("language", CodeLanguage.PYTHON.value)
        
        self.logger.info(f"Fixing bug: {bug_report.get('title', 'Unknown Bug')}")
        
        # Analyze bug and locate affected files
        bug_analysis = await self._analyze_bug_report(bug_report, project_path)
        
        # Identify root cause
        root_cause_analysis = await self._perform_root_cause_analysis(
            bug_analysis, project_path, language
        )
        
        # Design fix strategy
        fix_strategy = await self._design_bug_fix_strategy(
            bug_report, root_cause_analysis, language
        )
        
        # Apply fixes to affected files
        fixed_files = []
        for file_fix in fix_strategy.get("file_fixes", []):
            if self.filesystem_access:
                # Read current file content
                file_content = await self._read_file_mcp(file_fix["file_path"])
                
                # Apply fix
                fixed_content = await self._apply_code_fix(
                    file_content, file_fix["changes"], language
                )
                
                # Write back fixed content
                write_result = await self._write_file_mcp(file_fix["file_path"], fixed_content)
                if write_result["success"]:
                    fixed_files.append(file_fix["file_path"])
        
        # Create regression tests
        regression_tests = []
        test_specs = await self._design_regression_tests(bug_report, fix_strategy)
        
        for test_spec in test_specs:
            test_content = await self._generate_test_file(test_spec, bug_report, language)
            
            if self.filesystem_access:
                test_path = os.path.join(project_path, test_spec["path"])
                write_result = await self._write_file_mcp(test_path, test_content)
                if write_result["success"]:
                    regression_tests.append(test_path)
        
        # Run tests to verify fix
        test_results = {}
        if self.shell_access:
            test_results = await self._run_tests_mcp(project_path, language)
        
        # Commit fix if tests pass
        commit_result = {}
        if (test_results.get("passed", False) and 
            task.get("auto_commit", False) and 
            self.git_access):
            commit_message = f"Fix bug: {bug_report.get('title', 'Bug Fix')}"
            commit_result = await self._git_commit_mcp(project_path, commit_message)
        
        bug_fix_result = {
            "bug_title": bug_report.get("title", "Unknown Bug"),
            "root_cause": root_cause_analysis,
            "fix_strategy": fix_strategy,
            "fixed_files": fixed_files,
            "regression_tests": regression_tests,
            "test_results": test_results,
            "commit_result": commit_result,
            "verification": await self._verify_bug_fix(bug_report, test_results)
        }
        
        return {
            "status": "success",
            "bug_fix": bug_fix_result
        }
    
    async def _write_tests(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Write comprehensive tests for code."""
        
        code_to_test = task.get("code_files", [])
        project_path = task.get("project_path", "./")
        language = task.get("language", CodeLanguage.PYTHON.value)
        test_framework = task.get("framework", TestFramework.PYTEST.value)
        
        self.logger.info(f"Writing tests for {len(code_to_test)} files")
        
        test_results = []
        
        for code_file in code_to_test:
            # Analyze code to understand what to test
            if self.filesystem_access:
                file_content = await self._read_file_mcp(code_file)
                code_analysis = await self._analyze_code_for_testing(
                    file_content, language
                )
            else:
                code_analysis = {"functions": [], "classes": [], "complexity": "medium"}
            
            # Design test cases
            test_cases = await self._design_test_cases(
                code_analysis, test_framework, language
            )
            
            # Generate test file
            test_file_content = await self._generate_comprehensive_test_file(
                code_file, test_cases, test_framework, language
            )
            
            # Write test file
            test_file_path = await self._get_test_file_path(code_file, language)
            
            if self.filesystem_access:
                write_result = await self._write_file_mcp(
                    os.path.join(project_path, test_file_path), 
                    test_file_content
                )
                
                test_results.append({
                    "source_file": code_file,
                    "test_file": test_file_path,
                    "test_cases_count": len(test_cases),
                    "written": write_result["success"]
                })
            else:
                test_results.append({
                    "source_file": code_file,
                    "test_file": test_file_path,
                    "test_content": test_file_content,
                    "test_cases_count": len(test_cases),
                    "written": False  # No filesystem access
                })
        
        # Run the tests
        execution_results = {}
        if self.shell_access:
            execution_results = await self._run_tests_mcp(project_path, language)
        
        # Generate test coverage report
        coverage_report = {}
        if self.shell_access:
            coverage_report = await self._generate_coverage_report_mcp(
                project_path, language
            )
        
        return {
            "status": "success",
            "test_writing": {
                "test_files_created": test_results,
                "execution_results": execution_results,
                "coverage_report": coverage_report,
                "total_test_cases": sum(tr.get("test_cases_count", 0) for tr in test_results),
                "recommendations": await self._generate_testing_recommendations(
                    test_results, execution_results, coverage_report
                )
            }
        }
    
    async def _setup_project(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Set up a new development project."""
        
        project_config = task.get("project_config", {})
        project_path = task.get("project_path", "./new_project")
        language = task.get("language", CodeLanguage.PYTHON.value)
        
        self.logger.info(f"Setting up new {language} project at {project_path}")
        
        # Create project directory structure
        directory_structure = await self._design_project_structure(
            project_config, language
        )
        
        created_dirs = []
        if self.filesystem_access:
            for directory in directory_structure:
                dir_path = os.path.join(project_path, directory)
                create_result = await self._create_directory_mcp(dir_path)
                if create_result["success"]:
                    created_dirs.append(directory)
        
        # Generate project files
        project_files = await self._generate_project_files(
            project_config, language
        )
        
        created_files = []
        for file_spec in project_files:
            if self.filesystem_access:
                file_path = os.path.join(project_path, file_spec["path"])
                write_result = await self._write_file_mcp(file_path, file_spec["content"])
                if write_result["success"]:
                    created_files.append(file_spec["path"])
        
        # Initialize git repository
        git_result = {}
        if self.git_access and task.get("init_git", True):
            git_result = await self._git_init_mcp(project_path)
            
            if git_result.get("success", False):
                # Create initial commit
                commit_result = await self._git_commit_mcp(
                    project_path, "Initial project setup"
                )
                git_result["initial_commit"] = commit_result
        
        # Install dependencies
        install_result = {}
        if self.shell_access and task.get("install_deps", True):
            install_result = await self._install_dependencies_mcp(
                project_path, language
            )
        
        # Run initial tests
        test_result = {}
        if self.shell_access and task.get("run_initial_tests", True):
            test_result = await self._run_tests_mcp(project_path, language)
        
        return {
            "status": "success",
            "project_setup": {
                "project_path": project_path,
                "language": language,
                "directories_created": created_dirs,
                "files_created": created_files,
                "git_initialization": git_result,
                "dependency_installation": install_result,
                "initial_test_results": test_result,
                "next_steps": await self._generate_project_next_steps(
                    project_config, language
                )
            }
        }
    
    # MCP Integration Methods
    
    async def _read_file_mcp(self, file_path: str) -> str:
        """Read file content using MCP filesystem capability."""
        try:
            if not self.filesystem_access:
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            return ""
    
    async def _write_file_mcp(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write file content using MCP filesystem capability."""
        try:
            if not self.filesystem_access:
                return {"success": False, "error": "Filesystem access disabled"}
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            return {"success": True, "file_path": file_path}
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_directory_mcp(self, dir_path: str) -> Dict[str, Any]:
        """Create directory using MCP filesystem capability."""
        try:
            if not self.filesystem_access:
                return {"success": False, "error": "Filesystem access disabled"}
            
            os.makedirs(dir_path, exist_ok=True)
            return {"success": True, "directory": dir_path}
        except Exception as e:
            self.logger.error(f"Error creating directory {dir_path}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_shell_command_mcp(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Run shell command using MCP shell capability."""
        try:
            if not self.shell_access:
                return {"success": False, "error": "Shell access disabled"}
            
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd,
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            self.logger.error(f"Error running command {command}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _git_commit_mcp(self, repo_path: str, message: str) -> Dict[str, Any]:
        """Commit changes using MCP git capability."""
        if not self.git_access:
            return {"success": False, "error": "Git access disabled"}
        
        # Add all changes
        add_result = await self._run_shell_command_mcp("git add .", cwd=repo_path)
        if not add_result["success"]:
            return add_result
        
        # Commit changes
        commit_command = f'git commit -m "{message}"'
        commit_result = await self._run_shell_command_mcp(commit_command, cwd=repo_path)
        
        return commit_result
    
    async def _git_init_mcp(self, repo_path: str) -> Dict[str, Any]:
        """Initialize git repository using MCP git capability."""
        if not self.git_access:
            return {"success": False, "error": "Git access disabled"}
        
        return await self._run_shell_command_mcp("git init", cwd=repo_path)
    
    async def _run_tests_mcp(self, project_path: str, language: str) -> Dict[str, Any]:
        """Run tests using MCP shell capability."""
        if not self.shell_access:
            return {"success": False, "error": "Shell access disabled"}
        
        # Determine test command based on language
        test_commands = {
            CodeLanguage.PYTHON.value: "python -m pytest --tb=short",
            CodeLanguage.JAVASCRIPT.value: "npm test",
            CodeLanguage.TYPESCRIPT.value: "npm test",
            CodeLanguage.JAVA.value: "mvn test",
            CodeLanguage.GO.value: "go test ./...",
            CodeLanguage.RUST.value: "cargo test"
        }
        
        test_command = test_commands.get(language, "echo 'No test command configured'")
        result = await self._run_shell_command_mcp(test_command, cwd=project_path)
        
        # Parse test results
        test_summary = await self._parse_test_results(result, language)
        result.update(test_summary)
        
        return result
    
    async def _format_code_mcp(self, project_path: str, language: str) -> Dict[str, Any]:
        """Format code using MCP shell capability."""
        if not self.shell_access:
            return {"success": False, "error": "Shell access disabled"}
        
        format_commands = {
            CodeLanguage.PYTHON.value: "black . && isort .",
            CodeLanguage.JAVASCRIPT.value: "npx prettier --write .",
            CodeLanguage.TYPESCRIPT.value: "npx prettier --write .",
            CodeLanguage.GO.value: "go fmt ./...",
            CodeLanguage.RUST.value: "cargo fmt"
        }
        
        format_command = format_commands.get(language, "echo 'No formatter configured'")
        return await self._run_shell_command_mcp(format_command, cwd=project_path)
    
    async def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate Developer's output quality."""
        
        if not output or output.get("status") != "success":
            return False
        
        # Check for required development deliverables
        if "implementation" in output:
            impl = output["implementation"]
            return bool(impl.get("generated_files") and impl.get("implementation_plan"))
        
        if "bug_fix" in output:
            fix = output["bug_fix"]
            return bool(fix.get("fixed_files") and fix.get("root_cause"))
        
        if "test_writing" in output:
            tests = output["test_writing"]
            return bool(tests.get("test_files_created"))
        
        return True
    
    def get_prompt_template(self) -> str:
        """Get Developer's prompt template."""
        return """
        You are an experienced Software Developer with access to filesystem, git, and shell operations.
        
        Your responsibilities include:
        1. Implementing features and writing clean, maintainable code
        2. Fixing bugs with proper root cause analysis
        3. Writing comprehensive tests with good coverage
        4. Performing code reviews and ensuring quality
        5. Optimizing performance and refactoring code
        6. Setting up projects and managing dependencies
        
        Current context: {context}
        Task: {task}
        
        MCP Capabilities Available:
        - Filesystem: Read/write files and directories
        - Git: Commit, branch, and repository operations
        - Shell: Run build, test, and deployment commands
        
        Focus on:
        - Code quality and best practices
        - Comprehensive testing and documentation
        - Security and performance considerations
        - Clean architecture and maintainable code
        - Proper error handling and logging
        
        Always write tests for your code and ensure they pass before committing.
        """
    
    # Helper methods for development operations
    
    async def _analyze_codebase_structure(self, project_path: str, language: str) -> Dict[str, Any]:
        """Analyze existing codebase structure."""
        return {
            "language": language,
            "structure_type": "modular",
            "main_directories": ["src", "tests", "docs"],
            "coding_patterns": ["MVC", "dependency_injection"],
            "dependencies": [],
            "test_coverage": 0.75
        }
    
    async def _design_implementation_plan(self, feature_spec: Dict, codebase: Dict, language: str) -> Dict[str, Any]:
        """Design implementation plan for a feature."""
        return {
            "approach": "incremental_development",
            "files_to_create": [
                {"path": f"src/{feature_spec.get('name', 'feature')}.py", "type": "implementation"},
                {"path": f"src/models/{feature_spec.get('name', 'feature')}_model.py", "type": "model"}
            ],
            "files_to_modify": [],
            "dependencies_to_add": [],
            "tests_to_write": [
                {"path": f"tests/test_{feature_spec.get('name', 'feature')}.py", "type": "unit_test"}
            ],
            "estimated_complexity": "medium",
            "implementation_order": ["models", "core_logic", "api_endpoints", "tests"]
        }
    
    async def _generate_code_file(self, file_spec: Dict, feature_spec: Dict, language: str, codebase: Dict) -> str:
        """Generate code file content."""
        
        if language == CodeLanguage.PYTHON.value:
            return f'''"""
{feature_spec.get('name', 'Feature')} implementation.

This module implements {feature_spec.get('description', 'a new feature')}.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class {feature_spec.get('name', 'Feature').title()}:
    """
    {feature_spec.get('description', 'Feature implementation class')}.
    """
    
    def __init__(self):
        self.logger = logger
        self.initialized = True
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the main feature logic.
        
        Args:
            data: Input data for processing
            
        Returns:
            Processed result
        """
        try:
            self.logger.info("Processing feature request")
            
            # Main feature logic here
            result = {{
                "status": "success",
                "data": data,
                "timestamp": "2025-01-01T00:00:00Z"
            }}
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing feature: {{str(e)}}")
            return {{"status": "error", "message": str(e)}}
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["id", "type"]
        return all(field in data for field in required_fields)
'''
        
        # Add other language templates as needed
        return f"// {feature_spec.get('name', 'Feature')} implementation\n// TODO: Implement feature logic"
    
    async def _generate_test_file(self, test_spec: Dict, feature_spec: Dict, language: str) -> str:
        """Generate test file content."""
        
        if language == CodeLanguage.PYTHON.value:
            feature_name = feature_spec.get('name', 'feature')
            class_name = feature_name.title()
            
            return f'''"""
Tests for {feature_name} feature.
"""

import pytest
from unittest.mock import Mock, patch
from src.{feature_name} import {class_name}


class Test{class_name}:
    """Test cases for {class_name}."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.{feature_name} = {class_name}()
        self.sample_data = {{
            "id": "test-001",
            "type": "test",
            "value": 42
        }}
    
    def test_initialization(self):
        """Test that {class_name} initializes correctly."""
        assert self.{feature_name}.initialized is True
    
    def test_process_valid_data(self):
        """Test processing with valid data."""
        result = self.{feature_name}.process(self.sample_data)
        
        assert result["status"] == "success"
        assert "data" in result
        assert "timestamp" in result
    
    def test_process_invalid_data(self):
        """Test processing with invalid data."""
        invalid_data = {{"invalid": "data"}}
        result = self.{feature_name}.process(invalid_data)
        
        # Should handle gracefully
        assert isinstance(result, dict)
    
    def test_validate_input_valid(self):
        """Test input validation with valid data."""
        assert self.{feature_name}.validate_input(self.sample_data) is True
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data."""
        invalid_data = {{"missing": "required_fields"}}
        assert self.{feature_name}.validate_input(invalid_data) is False
    
    @patch('{feature_name}.logger')
    def test_error_handling(self, mock_logger):
        """Test error handling and logging."""
        # Test error scenarios
        with patch.object(self.{feature_name}, 'validate_input', side_effect=Exception("Test error")):
            result = self.{feature_name}.process(self.sample_data)
            assert result["status"] == "error"
'''
        
        return f"// Test file for {feature_spec.get('name', 'feature')}\n// TODO: Implement tests"
    
    async def _parse_test_results(self, shell_result: Dict, language: str) -> Dict[str, Any]:
        """Parse test execution results."""
        
        if not shell_result.get("success", False):
            return {
                "passed": False,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error_message": shell_result.get("stderr", "Tests failed")
            }
        
        stdout = shell_result.get("stdout", "")
        
        # Simple parsing for pytest output
        if "pytest" in stdout.lower():
            if "failed" in stdout.lower():
                return {
                    "passed": False,
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 1,
                    "summary": "Some tests failed"
                }
            else:
                return {
                    "passed": True,
                    "total_tests": 1,
                    "passed_tests": 1,
                    "failed_tests": 0,
                    "summary": "All tests passed"
                }
        
        return {
            "passed": True,
            "summary": "Tests executed successfully"
        }
    
    # Placeholder methods for complex development operations
    
    async def _analyze_bug_report(self, bug_report: Dict, project_path: str) -> Dict[str, Any]:
        """Analyze bug report to understand the issue."""
        return {
            "bug_type": "logic_error",
            "affected_components": ["user_service"],
            "severity": "medium",
            "reproducible": True
        }
    
    async def _perform_root_cause_analysis(self, bug_analysis: Dict, project_path: str, language: str) -> Dict[str, Any]:
        """Perform root cause analysis for the bug."""
        return {
            "root_cause": "Null pointer exception in user validation",
            "contributing_factors": ["Missing input validation", "Incorrect error handling"],
            "fix_complexity": "low"
        }
    
    async def _design_bug_fix_strategy(self, bug_report: Dict, root_cause: Dict, language: str) -> Dict[str, Any]:
        """Design strategy to fix the bug."""
        return {
            "fix_approach": "Add input validation and improve error handling",
            "file_fixes": [
                {
                    "file_path": "src/user_service.py",
                    "changes": ["Add null checks", "Improve validation"]
                }
            ],
            "testing_strategy": "Add regression tests"
        }
    
    async def _apply_code_fix(self, file_content: str, changes: List[str], language: str) -> str:
        """Apply code fixes to file content."""
        # Simple implementation - in production would have sophisticated code modification
        return file_content + "\n# Applied fixes: " + ", ".join(changes)
    
    async def _design_regression_tests(self, bug_report: Dict, fix_strategy: Dict) -> List[Dict[str, Any]]:
        """Design regression tests for the bug fix."""
        return [
            {
                "path": "tests/test_bug_regression.py",
                "test_type": "regression",
                "scenarios": ["null_input", "boundary_conditions"]
            }
        ]
    
    async def _verify_bug_fix(self, bug_report: Dict, test_results: Dict) -> Dict[str, Any]:
        """Verify that the bug has been fixed."""
        return {
            "fixed": test_results.get("passed", False),
            "verification_method": "automated_tests",
            "confidence": "high" if test_results.get("passed", False) else "low"
        }
    
    async def _analyze_code_for_testing(self, file_content: str, language: str) -> Dict[str, Any]:
        """Analyze code to determine what needs testing."""
        return {
            "functions": ["process", "validate_input"],
            "classes": ["Feature"],
            "complexity": "medium",
            "test_coverage_needed": ["happy_path", "error_cases", "edge_cases"]
        }
    
    async def _design_test_cases(self, code_analysis: Dict, framework: str, language: str) -> List[Dict[str, Any]]:
        """Design comprehensive test cases."""
        return [
            {"name": "test_initialization", "type": "unit", "complexity": "simple"},
            {"name": "test_process_valid_data", "type": "unit", "complexity": "medium"},
            {"name": "test_error_handling", "type": "unit", "complexity": "medium"}
        ]
    
    async def _generate_comprehensive_test_file(self, source_file: str, test_cases: List, framework: str, language: str) -> str:
        """Generate comprehensive test file."""
        return f"# Comprehensive tests for {source_file}\n# Generated {len(test_cases)} test cases"
    
    async def _get_test_file_path(self, source_file: str, language: str) -> str:
        """Get appropriate test file path for source file."""
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        return f"tests/test_{base_name}.py"
    
    async def _generate_coverage_report_mcp(self, project_path: str, language: str) -> Dict[str, Any]:
        """Generate test coverage report."""
        return {
            "overall_coverage": 85.5,
            "file_coverage": {"src/feature.py": 90.0, "src/utils.py": 75.0},
            "missing_coverage": ["error_handling", "edge_cases"]
        }
    
    async def _generate_testing_recommendations(self, test_results: List, execution: Dict, coverage: Dict) -> List[str]:
        """Generate testing recommendations."""
        return [
            "Add more edge case testing",
            "Improve error handling test coverage",
            "Consider property-based testing for complex functions"
        ]
    
    async def _design_project_structure(self, project_config: Dict, language: str) -> List[str]:
        """Design directory structure for new project."""
        if language == CodeLanguage.PYTHON.value:
            return [
                "src",
                "tests", 
                "docs",
                "scripts",
                "config",
                ".github/workflows"
            ]
        return ["src", "tests", "docs"]
    
    async def _generate_project_files(self, project_config: Dict, language: str) -> List[Dict[str, str]]:
        """Generate initial project files."""
        files = []
        
        if language == CodeLanguage.PYTHON.value:
            files.extend([
                {
                    "path": "requirements.txt",
                    "content": "# Project dependencies\npytest>=7.0.0\nblack>=22.0.0\nisort>=5.0.0\n"
                },
                {
                    "path": "pyproject.toml", 
                    "content": '[tool.black]\nline-length = 100\ntarget-version = ["py39"]\n'
                },
                {
                    "path": "README.md",
                    "content": f"# {project_config.get('name', 'New Project')}\n\n{project_config.get('description', 'Project description')}\n"
                },
                {
                    "path": ".gitignore",
                    "content": "__pycache__/\n*.pyc\n.pytest_cache/\n.coverage\n.venv/\n"
                }
            ])
        
        return files
    
    async def _install_dependencies_mcp(self, project_path: str, language: str) -> Dict[str, Any]:
        """Install project dependencies."""
        if not self.shell_access:
            return {"success": False, "error": "Shell access disabled"}
        
        if language == CodeLanguage.PYTHON.value:
            return await self._run_shell_command_mcp("pip install -r requirements.txt", cwd=project_path)
        elif language == CodeLanguage.JAVASCRIPT.value:
            return await self._run_shell_command_mcp("npm install", cwd=project_path)
        
        return {"success": True, "message": "No dependencies to install"}
    
    async def _generate_project_next_steps(self, project_config: Dict, language: str) -> List[str]:
        """Generate next steps for project setup."""
        return [
            "Configure your IDE with the project",
            "Set up continuous integration",
            "Add more comprehensive tests", 
            "Configure code quality tools",
            "Set up deployment pipeline"
        ]
    
    async def _assess_code_quality(self, generated_files: List, language: str) -> Dict[str, Any]:
        """Assess quality of generated code."""
        return {
            "overall_score": 8.5,
            "metrics": {
                "complexity": "medium",
                "maintainability": "high",
                "testability": "high",
                "documentation": "good"
            },
            "suggestions": [
                "Add more inline comments",
                "Consider breaking down complex functions"
            ]
        }
    
    async def _generate_feature_documentation(self, feature_spec: Dict, plan: Dict, files: List) -> Dict[str, Any]:
        """Generate documentation for implemented feature."""
        return {
            "feature_overview": feature_spec.get("description", ""),
            "implementation_notes": "Feature implemented following clean architecture principles",
            "api_documentation": "Generated API docs available",
            "usage_examples": ["example_1.py", "example_2.py"],
            "testing_instructions": "Run pytest to execute all tests"
        }
    
    async def _design_test_specifications(self, feature_spec: Dict, implementation_plan: Dict) -> List[Dict[str, Any]]:
        """Design test specifications for the feature."""
        feature_name = feature_spec.get("name", "feature")
        
        test_specs = []
        
        # Unit tests for main implementation
        test_specs.append({
            "path": f"tests/test_{feature_name}.py",
            "type": "unit_test",
            "test_cases": [
                "test_initialization",
                "test_main_functionality",
                "test_error_handling",
                "test_edge_cases"
            ]
        })
        
        # Integration tests if API endpoints are involved
        if any("api" in file_spec.get("type", "") for file_spec in implementation_plan.get("files_to_create", [])):
            test_specs.append({
                "path": f"tests/integration/test_{feature_name}_api.py",
                "type": "integration_test",
                "test_cases": [
                    "test_api_endpoints",
                    "test_request_validation",
                    "test_response_format"
                ]
            })
        
        return test_specs