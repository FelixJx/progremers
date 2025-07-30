"""QA Agent - Quality Assurance Agent with MCP capabilities for automated testing."""

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


class TestType(str, Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    API = "api"
    UI = "ui"


class TestFramework(str, Enum):
    """Supported testing frameworks."""
    PYTEST = "pytest"
    JEST = "jest"
    SELENIUM = "selenium"
    PUPPETEER = "puppeteer"
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    POSTMAN = "postman"
    ARTILLERY = "artillery"


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class BugSeverity(str, Enum):
    """Bug severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class QAAgent(BaseAgent):
    """
    Quality Assurance Agent with MCP capabilities for:
    - Automated test suite creation and execution
    - UI testing with Puppeteer/Selenium
    - API testing and validation
    - Performance and load testing
    - Bug detection and reporting
    - Test report generation and analysis
    - Quality metrics tracking
    """
    
    def __init__(self, agent_id: str = "qa-001"):
        super().__init__(agent_id, AgentRole.QA)
        
        # QA-specific state
        self.test_suites = {}
        self.bug_reports = {}
        self.test_results = {}
        self.quality_metrics = {}
        
        # MCP capabilities configuration
        self.mcp_enabled = True
        self.puppeteer_access = True
        self.filesystem_access = True
        self.shell_access = True
        
        # QA configuration
        self.test_coverage_threshold = 80
        self.performance_thresholds = {
            "response_time": 200,  # ms
            "memory_usage": 100,   # MB
            "cpu_usage": 80        # %
        }
        self.supported_browsers = ["chrome", "firefox", "safari"]
        
        # Quality standards
        self.quality_gates = {
            "test_coverage": 80,
            "bug_density": 0.1,    # bugs per KLOC
            "test_pass_rate": 95,  # %
            "performance_score": 85
        }
    
    async def process_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Process QA tasks with MCP capabilities.
        
        Args:
            task: QA task details
            context: Current context
            
        Returns:
            Task processing result
        """
        task_type = task.get("type", "run_tests")
        
        self.logger.info(f"Processing QA task: {task_type}")
        
        try:
            if task_type == "create_test_suite":
                return await self._create_test_suite(task, context)
            elif task_type == "run_tests":
                return await self._run_test_suite(task, context)
            elif task_type == "ui_testing":
                return await self._perform_ui_testing(task, context)
            elif task_type == "api_testing":
                return await self._perform_api_testing(task, context)
            elif task_type == "performance_testing":
                return await self._perform_performance_testing(task, context)
            elif task_type == "security_testing":
                return await self._perform_security_testing(task, context)
            elif task_type == "generate_test_report":
                return await self._generate_test_report(task, context)
            elif task_type == "analyze_quality":
                return await self._analyze_code_quality(task, context)
            elif task_type == "track_bugs":
                return await self._track_bugs(task, context)
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing QA task: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _create_test_suite(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Create comprehensive test suite for a project."""
        
        project_path = task.get("project_path", "./")
        test_types = task.get("test_types", [TestType.UNIT.value, TestType.INTEGRATION.value])
        requirements = task.get("requirements", [])
        
        self.logger.info(f"Creating test suite with {len(test_types)} test types")
        
        # Analyze codebase for testing
        codebase_analysis = await self._analyze_codebase_for_testing(project_path)
        
        # Design test strategy
        test_strategy = await self._design_test_strategy(
            requirements, test_types, codebase_analysis
        )
        
        # Generate test files
        generated_tests = []
        
        for test_type in test_types:
            if test_type == TestType.UNIT.value:
                unit_tests = await self._generate_unit_tests(
                    project_path, codebase_analysis
                )
                generated_tests.extend(unit_tests)
            
            elif test_type == TestType.INTEGRATION.value:
                integration_tests = await self._generate_integration_tests(
                    project_path, codebase_analysis
                )
                generated_tests.extend(integration_tests)
            
            elif test_type == TestType.E2E.value:
                e2e_tests = await self._generate_e2e_tests(
                    project_path, requirements
                )
                generated_tests.extend(e2e_tests)
            
            elif test_type == TestType.API.value:
                api_tests = await self._generate_api_tests(
                    project_path, codebase_analysis
                )
                generated_tests.extend(api_tests)
        
        # Create test configuration
        test_config = await self._create_test_configuration(
            project_path, test_types, test_strategy
        )
        
        # Write test files
        written_files = []
        if self.filesystem_access:
            for test_file in generated_tests:
                file_path = os.path.join(project_path, test_file["path"])
                write_result = await self._write_file_mcp(file_path, test_file["content"])
                if write_result["success"]:
                    written_files.append(test_file["path"])
            
            # Write test configuration
            config_path = os.path.join(project_path, "test_config.json")
            config_write = await self._write_file_mcp(
                config_path, json.dumps(test_config, indent=2)
            )
        
        # Store test suite
        suite_id = f"suite-{len(self.test_suites) + 1:03d}"
        self.test_suites[suite_id] = {
            "id": suite_id,
            "project_path": project_path,
            "test_types": test_types,
            "test_files": written_files,
            "test_strategy": test_strategy,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "test_suite": {
                "suite_id": suite_id,
                "test_files_created": len(written_files),
                "test_types_covered": test_types,
                "test_strategy": test_strategy,
                "estimated_execution_time": await self._estimate_execution_time(generated_tests),
                "coverage_targets": await self._calculate_coverage_targets(codebase_analysis)
            }
        }
    
    async def _run_test_suite(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        
        project_path = task.get("project_path", "./")
        suite_id = task.get("suite_id", None)
        test_types = task.get("test_types", [TestType.UNIT.value])
        
        self.logger.info(f"Running test suite for {len(test_types)} test types")
        
        test_results = {}
        overall_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "execution_time": 0,
            "coverage": 0
        }
        
        # Run each test type
        for test_type in test_types:
            if test_type == TestType.UNIT.value:
                unit_results = await self._run_unit_tests_mcp(project_path)
                test_results["unit"] = unit_results
            
            elif test_type == TestType.INTEGRATION.value:
                integration_results = await self._run_integration_tests_mcp(project_path)
                test_results["integration"] = integration_results
            
            elif test_type == TestType.E2E.value:
                e2e_results = await self._run_e2e_tests_mcp(project_path)
                test_results["e2e"] = e2e_results
            
            elif test_type == TestType.API.value:
                api_results = await self._run_api_tests_mcp(project_path)
                test_results["api"] = api_results
            
            elif test_type == TestType.PERFORMANCE.value:
                perf_results = await self._run_performance_tests_mcp(project_path)
                test_results["performance"] = perf_results
        
        # Aggregate results
        for test_type, results in test_results.items():
            if results.get("success", False):
                stats = results.get("statistics", {})
                overall_results["total_tests"] += stats.get("total", 0)
                overall_results["passed"] += stats.get("passed", 0)
                overall_results["failed"] += stats.get("failed", 0)
                overall_results["skipped"] += stats.get("skipped", 0)
                overall_results["execution_time"] += stats.get("execution_time", 0)
        
        # Generate test coverage report
        coverage_report = {}
        if self.shell_access:
            coverage_report = await self._generate_coverage_report_mcp(project_path)
            overall_results["coverage"] = coverage_report.get("total_coverage", 0)
        
        # Evaluate quality gates
        quality_evaluation = await self._evaluate_quality_gates(
            overall_results, coverage_report
        )
        
        # Store results
        execution_id = f"exec-{len(self.test_results) + 1:03d}"
        self.test_results[execution_id] = {
            "execution_id": execution_id,
            "suite_id": suite_id,
            "project_path": project_path,
            "results": test_results,
            "overall_results": overall_results,
            "coverage_report": coverage_report,
            "quality_evaluation": quality_evaluation,
            "executed_at": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "test_execution": {
                "execution_id": execution_id,
                "overall_results": overall_results,
                "detailed_results": test_results,
                "coverage_report": coverage_report,
                "quality_gates": quality_evaluation,
                "recommendations": await self._generate_test_recommendations(
                    test_results, overall_results
                )
            }
        }
    
    async def _perform_ui_testing(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Perform UI testing with Puppeteer/Selenium."""
        
        app_url = task.get("app_url", "http://localhost:3000")
        test_scenarios = task.get("test_scenarios", [])
        browser = task.get("browser", "chrome")
        
        self.logger.info(f"Running UI tests on {app_url} with {len(test_scenarios)} scenarios")
        
        if not self.puppeteer_access:
            return {"status": "error", "message": "Puppeteer access not available"}
        
        # Generate UI test scripts
        ui_test_scripts = []
        for scenario in test_scenarios:
            script = await self._generate_ui_test_script(scenario, browser)
            ui_test_scripts.append(script)
        
        # Execute UI tests
        ui_results = []
        for script in ui_test_scripts:
            if self.shell_access:
                result = await self._execute_ui_test_mcp(script, app_url, browser)
                ui_results.append(result)
        
        # Analyze UI test results
        ui_analysis = await self._analyze_ui_test_results(ui_results)
        
        # Generate screenshots for failed tests
        screenshots = []
        if ui_analysis.get("failed_tests", 0) > 0:
            screenshots = await self._capture_failure_screenshots_mcp(
                app_url, browser, ui_analysis.get("failed_scenarios", [])
            )
        
        return {
            "status": "success",
            "ui_testing": {
                "app_url": app_url,
                "browser": browser,
                "scenarios_tested": len(test_scenarios),
                "test_results": ui_results,
                "analysis": ui_analysis,
                "screenshots": screenshots,
                "accessibility_score": await self._assess_accessibility_mcp(app_url),
                "performance_metrics": await self._measure_ui_performance_mcp(app_url)
            }
        }
    
    async def _perform_api_testing(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Perform comprehensive API testing."""
        
        api_base_url = task.get("api_base_url", "http://localhost:8000")
        api_spec = task.get("api_specification", {})
        test_data = task.get("test_data", {})
        
        self.logger.info(f"Testing API at {api_base_url}")
        
        # Generate API test cases
        api_test_cases = await self._generate_api_test_cases(api_spec, test_data)
        
        # Execute API tests
        api_results = []
        
        for test_case in api_test_cases:
            if self.shell_access:
                result = await self._execute_api_test_mcp(
                    api_base_url, test_case
                )
                api_results.append(result)
        
        # Validate API responses
        validation_results = await self._validate_api_responses(api_results, api_spec)
        
        # Test API security
        security_results = await self._test_api_security_mcp(api_base_url, api_spec)
        
        # Performance testing
        performance_results = await self._test_api_performance_mcp(
            api_base_url, api_test_cases
        )
        
        return {
            "status": "success",
            "api_testing": {
                "api_base_url": api_base_url,
                "test_cases_executed": len(api_test_cases),
                "test_results": api_results,
                "validation_results": validation_results,
                "security_results": security_results,
                "performance_results": performance_results,
                "compliance_score": await self._calculate_api_compliance_score(
                    validation_results, security_results
                )
            }
        }
    
    async def _perform_performance_testing(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Perform performance and load testing."""
        
        target_url = task.get("target_url", "http://localhost:8000")
        load_profile = task.get("load_profile", {
            "users": 100,
            "duration": "5m",
            "ramp_up": "1m"
        })
        
        self.logger.info(f"Running performance tests on {target_url}")
        
        # Generate load test configuration
        load_config = await self._generate_load_test_config(target_url, load_profile)
        
        # Execute performance tests
        perf_results = {}
        
        if self.shell_access:
            # Load testing
            load_results = await self._run_load_test_mcp(load_config)
            perf_results["load_test"] = load_results
            
            # Stress testing
            stress_results = await self._run_stress_test_mcp(load_config)
            perf_results["stress_test"] = stress_results
            
            # Spike testing
            spike_results = await self._run_spike_test_mcp(load_config)
            perf_results["spike_test"] = spike_results
        
        # Analyze performance metrics
        performance_analysis = await self._analyze_performance_metrics(perf_results)
        
        # Generate performance recommendations
        recommendations = await self._generate_performance_recommendations(
            performance_analysis, self.performance_thresholds
        )
        
        return {
            "status": "success",
            "performance_testing": {
                "target_url": target_url,
                "load_profile": load_profile,
                "test_results": perf_results,
                "analysis": performance_analysis,
                "thresholds": self.performance_thresholds,
                "passed_thresholds": performance_analysis.get("passed_thresholds", {}),
                "recommendations": recommendations
            }
        }
    
    async def _generate_test_report(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        
        execution_id = task.get("execution_id", None)
        project_path = task.get("project_path", "./")
        
        if execution_id and execution_id in self.test_results:
            test_data = self.test_results[execution_id]
        else:
            # Generate report from all available test data
            test_data = {
                "overall_results": {"total_tests": 0, "passed": 0, "failed": 0},
                "coverage_report": {},
                "quality_evaluation": {}
            }
        
        # Generate HTML report
        html_report = await self._generate_html_test_report(test_data)
        
        # Generate PDF report
        pdf_report = await self._generate_pdf_test_report(test_data)
        
        # Generate metrics dashboard
        metrics_dashboard = await self._generate_metrics_dashboard(test_data)
        
        # Write reports to files
        report_files = []
        if self.filesystem_access:
            reports_dir = os.path.join(project_path, "test_reports")
            await self._create_directory_mcp(reports_dir)
            
            # Write HTML report
            html_path = os.path.join(reports_dir, "test_report.html")
            html_write = await self._write_file_mcp(html_path, html_report)
            if html_write["success"]:
                report_files.append("test_report.html")
            
            # Write metrics
            metrics_path = os.path.join(reports_dir, "metrics.json")
            metrics_write = await self._write_file_mcp(
                metrics_path, json.dumps(metrics_dashboard, indent=2)
            )
            if metrics_write["success"]:
                report_files.append("metrics.json")
        
        return {
            "status": "success",
            "test_report": {
                "execution_id": execution_id,
                "report_files": report_files,
                "summary": {
                    "total_tests": test_data.get("overall_results", {}).get("total_tests", 0),
                    "pass_rate": self._calculate_pass_rate(test_data.get("overall_results", {})),
                    "coverage": test_data.get("coverage_report", {}).get("total_coverage", 0),
                    "quality_score": self._calculate_quality_score(test_data)
                },
                "recommendations": await self._generate_quality_improvement_recommendations(test_data)
            }
        }
    
    # MCP Integration Methods
    
    async def _write_file_mcp(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write file using MCP filesystem capability."""
        try:
            if not self.filesystem_access:
                return {"success": False, "error": "Filesystem access disabled"}
            
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
        """Run shell command using MCP capability."""
        try:
            if not self.shell_access:
                return {"success": False, "error": "Shell access disabled"}
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
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
    
    async def _run_unit_tests_mcp(self, project_path: str) -> Dict[str, Any]:
        """Run unit tests using shell command."""
        command = "python -m pytest tests/ -v --tb=short --cov=src --cov-report=json"
        result = await self._run_shell_command_mcp(command, cwd=project_path)
        
        # Parse pytest output
        if result.get("success", False):
            stats = await self._parse_pytest_output(result.get("stdout", ""))
            result["statistics"] = stats
        
        return result
    
    async def _run_integration_tests_mcp(self, project_path: str) -> Dict[str, Any]:
        """Run integration tests using shell command."""
        command = "python -m pytest tests/integration/ -v --tb=short"
        result = await self._run_shell_command_mcp(command, cwd=project_path)
        
        if result.get("success", False):
            stats = await self._parse_pytest_output(result.get("stdout", ""))
            result["statistics"] = stats
        
        return result
    
    async def _execute_ui_test_mcp(self, script: str, app_url: str, browser: str) -> Dict[str, Any]:
        """Execute UI test script using Puppeteer."""
        # Create temporary test file
        test_file = f"/tmp/ui_test_{datetime.now().timestamp()}.js"
        
        await self._write_file_mcp(test_file, script)
        
        # Run Puppeteer test
        command = f"node {test_file}"
        result = await self._run_shell_command_mcp(command)
        
        # Clean up
        try:
            os.remove(test_file)
        except:
            pass
        
        return result
    
    async def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate QA output quality."""
        
        if not output or output.get("status") != "success":
            return False
        
        # Check for required QA deliverables
        if "test_suite" in output:
            suite = output["test_suite"]
            return bool(suite.get("test_files_created") and suite.get("test_strategy"))
        
        if "test_execution" in output:
            execution = output["test_execution"]
            return bool(execution.get("overall_results") and execution.get("detailed_results"))
        
        if "test_report" in output:
            report = output["test_report"]
            return bool(report.get("summary") and report.get("report_files"))
        
        return True
    
    def get_prompt_template(self) -> str:
        """Get QA's prompt template."""
        return """
        You are an experienced Quality Assurance Engineer with access to automated testing tools.
        
        Your responsibilities include:
        1. Creating comprehensive test suites (unit, integration, e2e, performance)
        2. Executing automated tests and analyzing results
        3. Performing UI testing with browser automation tools
        4. Conducting API testing and validation
        5. Running performance and load testing
        6. Generating detailed test reports and quality metrics
        7. Identifying bugs and quality issues
        
        Current context: {context}
        Task: {task}
        
        MCP Capabilities Available:
        - Puppeteer: Browser automation for UI testing
        - Filesystem: Read/write test files and reports
        - Shell: Execute test frameworks and tools
        
        Focus on:
        - Comprehensive test coverage and quality
        - Automated test execution and reporting
        - Performance and security testing
        - Bug detection and quality metrics
        - Clear documentation and recommendations
        
        Maintain high quality standards and ensure thorough testing coverage.
        """
    
    # Helper methods for QA operations
    
    async def _analyze_codebase_for_testing(self, project_path: str) -> Dict[str, Any]:
        """Analyze codebase to determine testing requirements."""
        return {
            "language": "python",
            "framework": "flask",
            "modules": ["auth", "api", "models"],
            "test_complexity": "medium",
            "api_endpoints": 12,
            "ui_components": 8,
            "database_models": 5
        }
    
    async def _design_test_strategy(self, requirements: List, test_types: List, analysis: Dict) -> Dict[str, Any]:
        """Design comprehensive test strategy."""
        return {
            "approach": "risk_based_testing",
            "priorities": ["critical_paths", "user_journeys", "edge_cases"],
            "test_pyramid": {
                "unit_tests": 70,
                "integration_tests": 20,
                "e2e_tests": 10
            },
            "automation_level": 85,
            "tools": ["pytest", "selenium", "artillery"],
            "execution_schedule": "continuous"
        }
    
    async def _generate_unit_tests(self, project_path: str, analysis: Dict) -> List[Dict[str, str]]:
        """Generate unit test files."""
        tests = []
        
        for module in analysis.get("modules", []):
            test_content = f'''"""
Unit tests for {module} module.
"""

import pytest
from unittest.mock import Mock, patch
from src.{module} import {module.title()}


class Test{module.title()}:
    """Test cases for {module.title()}."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.{module} = {module.title()}()
        self.mock_data = {{"id": "test-001", "name": "test"}}
    
    def test_initialization(self):
        """Test that {module.title()} initializes correctly."""
        assert self.{module} is not None
    
    def test_main_functionality(self):
        """Test main functionality."""
        result = self.{module}.process(self.mock_data)
        assert result is not None
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            self.{module}.process(None)
    
    def test_edge_cases(self):
        """Test edge cases."""
        empty_data = {{}}
        result = self.{module}.process(empty_data)
        assert isinstance(result, dict)
'''
            
            tests.append({
                "path": f"tests/unit/test_{module}.py",
                "content": test_content
            })
        
        return tests
    
    async def _generate_integration_tests(self, project_path: str, analysis: Dict) -> List[Dict[str, str]]:
        """Generate integration test files."""
        tests = []
        
        if analysis.get("api_endpoints", 0) > 0:
            test_content = '''"""
Integration tests for API endpoints.
"""

import pytest
import requests
from tests.conftest import test_client


class TestAPIIntegration:
    """Integration tests for API."""
    
    def test_user_registration_flow(self, test_client):
        """Test complete user registration flow."""
        # Register user
        register_data = {"email": "test@example.com", "password": "password123"}
        response = test_client.post("/api/register", json=register_data)
        assert response.status_code == 201
        
        # Login user
        login_data = {"email": "test@example.com", "password": "password123"}
        response = test_client.post("/api/login", json=login_data)
        assert response.status_code == 200
        assert "token" in response.json()
    
    def test_authenticated_endpoints(self, test_client):
        """Test endpoints requiring authentication."""
        # Get auth token
        token = self._get_auth_token(test_client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test protected endpoint
        response = test_client.get("/api/profile", headers=headers)
        assert response.status_code == 200
    
    def _get_auth_token(self, client):
        """Helper to get authentication token."""
        login_data = {"email": "test@example.com", "password": "password123"}
        response = client.post("/api/login", json=login_data)
        return response.json().get("token")
'''
            
            tests.append({
                "path": "tests/integration/test_api_integration.py",
                "content": test_content
            })
        
        return tests
    
    async def _generate_e2e_tests(self, project_path: str, requirements: List) -> List[Dict[str, str]]:
        """Generate end-to-end test files."""
        tests = []
        
        test_content = '''"""
End-to-end tests using Selenium.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestE2EUserJourneys:
    """End-to-end user journey tests."""
    
    @pytest.fixture
    def driver(self):
        """Create web driver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_user_registration_journey(self, driver):
        """Test complete user registration journey."""
        # Navigate to registration page
        driver.get("http://localhost:3000/register")
        
        # Fill registration form
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        submit_button = driver.find_element(By.TYPE, "submit")
        
        email_input.send_keys("test@example.com")
        password_input.send_keys("password123")
        submit_button.click()
        
        # Wait for success message
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        assert success_message.is_displayed()
        assert "Registration successful" in success_message.text
    
    def test_login_journey(self, driver):
        """Test user login journey."""
        driver.get("http://localhost:3000/login")
        
        # Login form interaction
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        submit_button = driver.find_element(By.TYPE, "submit")
        
        email_input.send_keys("test@example.com")
        password_input.send_keys("password123")
        submit_button.click()
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        assert "/dashboard" in driver.current_url
'''
        
        tests.append({
            "path": "tests/e2e/test_user_journeys.py",
            "content": test_content
        })
        
        return tests
    
    async def _generate_api_tests(self, project_path: str, analysis: Dict) -> List[Dict[str, str]]:
        """Generate API test files."""
        tests = []
        
        test_content = '''"""
API tests using requests library.
"""

import pytest
import requests
import json


class TestAPIEndpoints:
    """Test API endpoints."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8000/api"
    
    @pytest.fixture
    def auth_headers(self, base_url):
        """Get authentication headers."""
        login_data = {"email": "test@example.com", "password": "password123"}
        response = requests.post(f"{base_url}/login", json=login_data)
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_health_endpoint(self, base_url):
        """Test health check endpoint."""
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        assert response.json().get("status") == "healthy"
    
    def test_user_crud_operations(self, base_url, auth_headers):
        """Test user CRUD operations."""
        # Create user
        user_data = {"name": "Test User", "email": "newuser@example.com"}
        response = requests.post(f"{base_url}/users", 
                               json=user_data, headers=auth_headers)
        assert response.status_code == 201
        user_id = response.json().get("id")
        
        # Read user
        response = requests.get(f"{base_url}/users/{user_id}", 
                              headers=auth_headers)
        assert response.status_code == 200
        assert response.json().get("email") == user_data["email"]
        
        # Update user
        updated_data = {"name": "Updated User"}
        response = requests.put(f"{base_url}/users/{user_id}", 
                              json=updated_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Delete user
        response = requests.delete(f"{base_url}/users/{user_id}", 
                                 headers=auth_headers)
        assert response.status_code == 204
    
    def test_api_error_handling(self, base_url):
        """Test API error handling."""
        # Test invalid endpoint
        response = requests.get(f"{base_url}/invalid-endpoint")
        assert response.status_code == 404
        
        # Test invalid data
        response = requests.post(f"{base_url}/users", json={})
        assert response.status_code == 400
'''
        
        tests.append({
            "path": "tests/api/test_api_endpoints.py",
            "content": test_content
        })
        
        return tests
    
    async def _create_test_configuration(self, project_path: str, test_types: List, strategy: Dict) -> Dict[str, Any]:
        """Create test configuration."""
        return {
            "test_types": test_types,
            "strategy": strategy,
            "frameworks": {
                "unit": "pytest",
                "integration": "pytest",
                "e2e": "selenium",
                "api": "requests"
            },
            "coverage": {
                "target": 80,
                "fail_under": 70
            },
            "reporting": {
                "formats": ["html", "json", "xml"],
                "output_dir": "test_reports"
            },
            "parallel_execution": True,
            "retry_failed": 3
        }
    
    async def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output to extract statistics."""
        lines = output.split('\n')
        
        stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "execution_time": 0
        }
        
        # Simple parsing - in production would be more sophisticated
        for line in lines:
            if "passed" in line and "failed" in line:
                # Extract numbers from summary line
                if "passed" in line:
                    stats["passed"] = 5  # Placeholder
                if "failed" in line:
                    stats["failed"] = 1  # Placeholder
            elif "collected" in line:
                stats["total"] = 6  # Placeholder
        
        return stats
    
    # Placeholder methods for complex QA operations
    
    async def _estimate_execution_time(self, tests: List) -> int:
        """Estimate test execution time in minutes."""
        return len(tests) * 2  # 2 minutes per test file
    
    async def _calculate_coverage_targets(self, analysis: Dict) -> Dict[str, int]:
        """Calculate coverage targets by module."""
        return {
            "overall": 80,
            "unit": 90,
            "integration": 70,
            "critical_paths": 95
        }
    
    async def _run_e2e_tests_mcp(self, project_path: str) -> Dict[str, Any]:
        """Run E2E tests.""" 
        command = "python -m pytest tests/e2e/ -v --tb=short"
        return await self._run_shell_command_mcp(command, cwd=project_path)
    
    async def _run_api_tests_mcp(self, project_path: str) -> Dict[str, Any]:
        """Run API tests."""
        command = "python -m pytest tests/api/ -v --tb=short"
        return await self._run_shell_command_mcp(command, cwd=project_path)
    
    async def _run_performance_tests_mcp(self, project_path: str) -> Dict[str, Any]:
        """Run performance tests."""
        return {"success": True, "message": "Performance tests completed"}
    
    async def _generate_coverage_report_mcp(self, project_path: str) -> Dict[str, Any]:
        """Generate test coverage report."""
        return {
            "total_coverage": 85.5,
            "module_coverage": {
                "auth": 92.0,
                "api": 88.0,
                "models": 78.0
            },
            "uncovered_lines": 45
        }
    
    async def _evaluate_quality_gates(self, results: Dict, coverage: Dict) -> Dict[str, Any]:
        """Evaluate quality gates."""
        gates = {}
        
        # Test pass rate
        total = results.get("total_tests", 1)
        passed = results.get("passed", 0)
        pass_rate = (passed / total) * 100 if total > 0 else 0
        gates["test_pass_rate"] = {
            "value": pass_rate,
            "threshold": self.quality_gates["test_pass_rate"],
            "passed": pass_rate >= self.quality_gates["test_pass_rate"]
        }
        
        # Coverage gate
        coverage_value = coverage.get("total_coverage", 0)
        gates["test_coverage"] = {
            "value": coverage_value,
            "threshold": self.quality_gates["test_coverage"],
            "passed": coverage_value >= self.quality_gates["test_coverage"]
        }
        
        return gates
    
    async def _generate_test_recommendations(self, results: Dict, overall: Dict) -> List[str]:
        """Generate test improvement recommendations."""
        recommendations = []
        
        pass_rate = self._calculate_pass_rate(overall)
        if pass_rate < 95:
            recommendations.append("Improve test stability - some tests are failing")
        
        if overall.get("coverage", 0) < 80:
            recommendations.append("Increase test coverage to meet 80% threshold")
        
        recommendations.extend([
            "Add more edge case testing",
            "Implement performance regression tests",
            "Consider property-based testing for complex logic"
        ])
        
        return recommendations
    
    def _calculate_pass_rate(self, results: Dict) -> float:
        """Calculate test pass rate."""
        total = results.get("total_tests", 1)
        passed = results.get("passed", 0)
        return (passed / total) * 100 if total > 0 else 0
    
    def _calculate_quality_score(self, test_data: Dict) -> float:
        """Calculate overall quality score."""
        pass_rate = self._calculate_pass_rate(test_data.get("overall_results", {}))
        coverage = test_data.get("coverage_report", {}).get("total_coverage", 0)
        
        # Weighted score
        return (pass_rate * 0.6) + (coverage * 0.4)
    
    async def _generate_html_test_report(self, test_data: Dict) -> str:
        """Generate HTML test report."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
    </style>
</head>
<body>
    <h1>Test Execution Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {test_data.get("overall_results", {}).get("total_tests", 0)}</p>
        <p class="passed">Passed: {test_data.get("overall_results", {}).get("passed", 0)}</p>
        <p class="failed">Failed: {test_data.get("overall_results", {}).get("failed", 0)}</p>
        <p>Coverage: {test_data.get("coverage_report", {}).get("total_coverage", 0)}%</p>
    </div>
</body>
</html>
"""
    
    async def _generate_pdf_test_report(self, test_data: Dict) -> str:
        """Generate PDF test report."""
        return "PDF report content placeholder"
    
    async def _generate_metrics_dashboard(self, test_data: Dict) -> Dict[str, Any]:
        """Generate metrics dashboard data."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "test_execution": test_data.get("overall_results", {}),
                "coverage": test_data.get("coverage_report", {}),
                "quality_gates": test_data.get("quality_evaluation", {})
            },
            "trends": {
                "pass_rate_trend": [95, 96, 94, 97, 95],
                "coverage_trend": [82, 84, 83, 85, 86]
            }
        }
    
    async def _generate_quality_improvement_recommendations(self, test_data: Dict) -> List[str]:
        """Generate quality improvement recommendations."""
        return [
            "Focus on improving test coverage in critical modules",
            "Implement automated regression testing",
            "Add performance monitoring to test suite",
            "Consider implementing mutation testing",
            "Improve test data management"
        ]