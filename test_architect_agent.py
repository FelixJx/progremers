#!/usr/bin/env python3
"""Test Architect Agent functionality."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.implementations.architect_agent import ArchitectAgent
from src.agents.base import AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


async def test_architecture_design():
    """Test system architecture design."""
    
    print("\n🏗️ Testing Architecture Design...")
    
    architect = ArchitectAgent("arch-001")
    
    design_task = {
        "type": "design_architecture",
        "requirements": [
            {"id": "REQ-001", "description": "User authentication system"},
            {"id": "REQ-002", "description": "Real-time messaging"},
            {"id": "REQ-003", "description": "File upload and storage"},
            {"id": "REQ-004", "description": "Analytics dashboard"},
            {"id": "REQ-005", "description": "API for mobile apps"}
        ],
        "non_functional_requirements": {
            "scalability": {"level": "high", "concurrent_users": 10000},
            "performance": {"response_time": "< 200ms", "throughput": "1000 rps"},
            "security": {"authentication": "required", "encryption": "required"}
        },
        "constraints": ["budget", "6-month timeline", "team size: 8 developers"]
    }
    
    context = AgentContext(
        project_id="test-arch-001",
        sprint_id="arch-sprint-001"
    )
    
    result = await architect.process_task(design_task, context)
    
    if result.get("status") == "success":
        print("✅ Architecture Design works")
        
        design = result.get("architecture_design", {})
        overview = design.get("architecture_overview", {})
        
        print(f"   🏛️ Pattern: {overview.get('pattern', 'N/A')}")
        print(f"   📊 Components: {len(design.get('system_components', {}))}")
        print(f"   🔄 Integration Patterns: {len(design.get('integration_patterns', []))}")
        print(f"   ⚠️ Risks Identified: {len(design.get('risks_and_mitigations', []))}")
        
        # Show components
        components = design.get("system_components", {})
        for comp_name, comp_info in list(components.items())[:3]:  # Show first 3
            print(f"   🔧 {comp_name}: {comp_info.get('name', 'Unknown')}")
            
    else:
        print("❌ Architecture Design failed")
        print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_technology_selection():
    """Test technology stack selection."""
    
    print("\n💻 Testing Technology Selection...")
    
    architect = ArchitectAgent("arch-001")
    
    tech_task = {
        "type": "select_technology",
        "requirements": [
            {"category": "frontend", "needs": ["SPA", "responsive", "real-time updates"]},
            {"category": "backend", "needs": ["REST API", "authentication", "scalable"]},
            {"category": "database", "needs": ["ACID", "relational", "high performance"]}
        ],
        "constraints": ["open source preferred", "cloud deployment", "Docker compatible"],
        "team_expertise": ["JavaScript", "Python", "PostgreSQL", "React"],
        "budget": {"monthly": 5000, "setup": 20000}
    }
    
    context = AgentContext(project_id="test-tech-001", sprint_id="tech-sprint-001")
    
    result = await architect.process_task(tech_task, context)
    
    if result.get("status") == "success":
        print("✅ Technology Selection works")
        
        tech_stack = result.get("technology_stack", {})
        selected = tech_stack.get("selected_technologies", {})
        rationale = tech_stack.get("selection_rationale", {})
        
        print(f"   🛠️ Technologies Selected: {len(selected)}")
        print(f"   💰 Estimated Cost: ${tech_stack.get('total_estimated_cost', {}).get('total_monthly', 0)}/month")
        
        # Show selected technologies
        for category, tech in selected.items():
            tech_name = tech.get("name", "Unknown")
            score = rationale.get(category, {}).get("score", 0)
            print(f"   ⚙️ {category}: {tech_name} (score: {score:.2f})")
            
    else:
        print("❌ Technology Selection failed")
        print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_module_design():
    """Test system module design."""
    
    print("\n🧩 Testing Module Design...")
    
    architect = ArchitectAgent("arch-001")
    
    module_task = {
        "type": "design_modules",
        "requirements": [
            {"domain": "user_management", "functions": ["auth", "profiles", "permissions"]},
            {"domain": "content", "functions": ["create", "edit", "publish", "search"]},
            {"domain": "analytics", "functions": ["track", "report", "dashboard"]}
        ],
        "architecture_pattern": "clean_architecture"
    }
    
    context = AgentContext(project_id="test-modules-001", sprint_id="modules-sprint-001")
    
    result = await architect.process_task(module_task, context)
    
    if result.get("status") == "success":
        print("✅ Module Design works")
        
        design = result.get("module_design", {})
        modules = design.get("modules", {})
        interfaces = design.get("interfaces", {})
        dependencies = design.get("dependencies", {})
        
        print(f"   📦 Modules Designed: {len(modules)}")
        print(f"   🔌 Interfaces Defined: {len(interfaces)}")
        print(f"   🔗 Dependencies Mapped: {len(dependencies)}")
        
        # Show modules
        for module_name, module_info in list(modules.items())[:3]:
            responsibilities = module_info.get("responsibilities", [])
            print(f"   📁 {module_name}: {len(responsibilities)} responsibilities")
            
    else:
        print("❌ Module Design failed")
        print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_api_design():
    """Test API specification design."""
    
    print("\n🌐 Testing API Design...")
    
    architect = ArchitectAgent("arch-001")
    
    # First create some modules
    modules = {
        "user_service": {
            "name": "User Service",
            "exposes_api": True,
            "responsibilities": ["authentication", "user profiles"]
        },
        "content_service": {
            "name": "Content Service", 
            "exposes_api": True,
            "responsibilities": ["content management", "publishing"]
        }
    }
    
    api_task = {
        "type": "design_apis",
        "modules": modules,
        "api_style": "REST"
    }
    
    context = AgentContext(project_id="test-api-001", sprint_id="api-sprint-001")
    
    result = await architect.process_task(api_task, context)
    
    if result.get("status") == "success":
        print("✅ API Design works")
        
        design = result.get("api_design", {})
        specifications = design.get("specifications", {})
        documentation = design.get("documentation", {})
        
        print(f"   📋 API Specifications: {len(specifications)}")
        print(f"   📖 Documentation Sections: {len(documentation)}")
        
        # Show API specs
        for service_name, spec in specifications.items():
            endpoints = spec.get("endpoints", [])
            print(f"   🔗 {service_name}: {len(endpoints)} endpoints")
            
    else:
        print("❌ API Design failed")
        print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_risk_assessment():
    """Test technical risk assessment."""
    
    print("\n⚠️ Testing Risk Assessment...")
    
    architect = ArchitectAgent("arch-001")
    
    risk_task = {
        "type": "assess_technical_risk",
        "architecture": {
            "pattern": "microservices",
            "components": ["user_service", "content_service", "api_gateway"],
            "deployment": "cloud"
        },
        "technology_stack": {
            "frontend": {"name": "React"},
            "backend": {"name": "Node.js"},
            "database": {"name": "PostgreSQL"}
        },
        "constraints": ["6-month timeline", "small team", "budget constraints"]
    }
    
    context = AgentContext(project_id="test-risk-001", sprint_id="risk-sprint-001")
    
    result = await architect.process_task(risk_task, context)
    
    if result.get("status") == "success":
        print("✅ Risk Assessment works")
        
        assessment = result.get("risk_assessment", {})
        prioritized_risks = assessment.get("prioritized_risks", [])
        mitigation_strategies = assessment.get("mitigation_strategies", {})
        overall_score = assessment.get("overall_risk_score", 0)
        
        print(f"   📊 Overall Risk Score: {overall_score:.2f}")
        print(f"   ⚠️ Risks Identified: {len(prioritized_risks)}")
        print(f"   🛡️ Mitigation Strategies: {len(mitigation_strategies)}")
        
        # Show top risks
        for risk in prioritized_risks[:3]:
            risk_type = risk.get("type", "Unknown")
            impact = risk.get("impact", "Unknown")
            print(f"   🚨 {risk_type}: {impact} impact")
            
    else:
        print("❌ Risk Assessment failed")
        print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_adr_creation():
    """Test Architectural Decision Record creation."""
    
    print("\n📋 Testing ADR Creation...")
    
    architect = ArchitectAgent("arch-001")
    
    adr_task = {
        "type": "create_adr",
        "title": "Database Selection for User Management",
        "context": "Need to select database for user management system with high availability requirements",
        "problem": "Current database solution doesn't scale well with increasing user load",
        "options": [
            {
                "name": "PostgreSQL with read replicas",
                "pros": ["ACID compliance", "mature ecosystem", "good performance"],
                "cons": ["complexity of setup", "eventual consistency in replicas"]
            },
            {
                "name": "MongoDB with sharding",
                "pros": ["horizontal scaling", "flexible schema", "good for document data"],
                "cons": ["eventual consistency", "learning curve for team"]
            }
        ]
    }
    
    context = AgentContext(project_id="test-adr-001", sprint_id="adr-sprint-001")
    
    result = await architect.process_task(adr_task, context)
    
    if result.get("status") == "success":
        print("✅ ADR Creation works")
        
        adr = result.get("adr", {})
        
        print(f"   📄 ADR ID: {adr.get('id', 'N/A')}")
        print(f"   📅 Status: {adr.get('status', 'N/A')}")
        print(f"   🎯 Decision: {adr.get('decision', {}).get('name', 'N/A')}")
        print(f"   📝 Options Considered: {len(adr.get('options_considered', []))}")
        
        # Check if architect stored the ADR
        stored_adrs = len(architect.architectural_decisions)
        print(f"   💾 ADRs Stored: {stored_adrs}")
        
    else:
        print("❌ ADR Creation failed")
        print(f"   Error: {result.get('message', 'Unknown error')}")


async def test_output_validation():
    """Test architect output validation."""
    
    print("\n✅ Testing Output Validation...")
    
    architect = ArchitectAgent("arch-001")
    
    # Test valid outputs
    valid_outputs = [
        {
            "status": "success",
            "architecture_design": {
                "architecture_overview": {"pattern": "microservices"},
                "system_components": {"service1": {}},
                "data_flow": {"type": "async"}
            }
        },
        {
            "status": "success", 
            "technology_stack": {
                "selected_technologies": {"frontend": "React"},
                "selection_rationale": {"frontend": "Good for SPA"}
            }
        }
    ]
    
    invalid_outputs = [
        {"status": "error"},
        {"status": "success", "architecture_design": {}},  # Missing required sections
        {"status": "success", "technology_stack": {}}  # Missing required sections
    ]
    
    valid_count = 0
    for output in valid_outputs:
        if await architect.validate_output(output):
            valid_count += 1
    
    invalid_count = 0
    for output in invalid_outputs:
        if not await architect.validate_output(output):
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
    """Run all Architect Agent tests."""
    
    print("🏗️ AI Agent Team - Architect Agent Test")
    print("=" * 50)
    print("Testing Architect Agent functionality...")
    
    # Run tests
    await test_architecture_design()
    await test_technology_selection()
    await test_module_design()
    await test_api_design()
    await test_risk_assessment()
    await test_adr_creation()
    await test_output_validation()
    
    print("\n" + "=" * 50)
    print("🎉 Architect Agent tests completed!")
    
    print("\n📋 What the Architect Agent can do:")
    print("✅ System architecture design with pattern selection")
    print("✅ Technology stack selection with evaluation criteria")
    print("✅ System module design with interfaces and dependencies")
    print("✅ API specification design with documentation")
    print("✅ Technical risk assessment with mitigation strategies")
    print("✅ Architectural Decision Record (ADR) creation")
    print("✅ Output validation with quality checks")
    
    print("\n🚀 Architect Agent is ready for integration!")
    print("💡 Next: Integrate with Manager Agent and add MCP capabilities")


if __name__ == "__main__":
    asyncio.run(main())