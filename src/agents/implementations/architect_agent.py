"""Architect Agent - System Architect for technical design and architecture decisions."""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from src.agents.base import BaseAgent, AgentRole, AgentStatus, AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


class ArchitecturePattern(str, Enum):
    """Common architecture patterns."""
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    LAYERED = "layered"
    MVC = "mvc"
    MVP = "mvp"
    MVVM = "mvvm"
    CLEAN_ARCHITECTURE = "clean_architecture"
    HEXAGONAL = "hexagonal"
    EVENT_DRIVEN = "event_driven"
    CQRS = "cqrs"


class TechStackCategory(str, Enum):
    """Technology stack categories."""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    MESSAGING = "messaging"
    CACHING = "caching"
    MONITORING = "monitoring"
    DEPLOYMENT = "deployment"
    SECURITY = "security"


class ArchitecturalDecisionStatus(str, Enum):
    """Status of architectural decisions."""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class ArchitectAgent(BaseAgent):
    """
    System Architect Agent responsible for:
    - System architecture design and documentation
    - Technology stack selection and evaluation
    - Module design and API specification
    - Integration patterns and data flow design
    - Technical risk assessment and mitigation
    - Architecture review and governance
    """
    
    def __init__(self, agent_id: str = "arch-001"):
        super().__init__(agent_id, AgentRole.ARCHITECT)
        
        # Architect-specific state
        self.architectural_decisions = {}
        self.technology_stack = {}
        self.system_modules = {}
        self.integration_patterns = []
        self.technical_constraints = []
        
        # Architect configuration
        self.preferred_patterns = [
            ArchitecturePattern.CLEAN_ARCHITECTURE,
            ArchitecturePattern.MICROSERVICES,
            ArchitecturePattern.EVENT_DRIVEN
        ]
        self.evaluation_criteria = {
            "scalability": 0.25,
            "maintainability": 0.20,
            "performance": 0.20,
            "security": 0.15,
            "cost": 0.10,
            "team_expertise": 0.10
        }
    
    async def process_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Process architecture tasks including design and technology selection.
        
        Args:
            task: Architecture task details
            context: Current context
            
        Returns:
            Task processing result
        """
        task_type = task.get("type", "design_architecture")
        
        self.logger.info(f"Processing Architect task: {task_type}")
        
        try:
            if task_type == "design_architecture":
                return await self._design_system_architecture(task, context)
            elif task_type == "select_technology":
                return await self._select_technology_stack(task, context)
            elif task_type == "design_modules":
                return await self._design_system_modules(task, context)
            elif task_type == "design_apis":
                return await self._design_api_specifications(task, context)
            elif task_type == "assess_technical_risk":
                return await self._assess_technical_risks(task, context)
            elif task_type == "review_architecture":
                return await self._review_architecture(task, context)
            elif task_type == "create_adr":
                return await self._create_architectural_decision(task, context)
            elif task_type == "analyze_codebase":
                return await self._analyze_existing_codebase(task, context)
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing Architect task: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _design_system_architecture(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Design overall system architecture based on requirements."""
        
        requirements = task.get("requirements", [])
        non_functional_requirements = task.get("non_functional_requirements", {})
        constraints = task.get("constraints", [])
        
        self.logger.info(f"Designing architecture for {len(requirements)} requirements")
        
        # Analyze requirements to determine architecture approach
        architecture_analysis = await self._analyze_architecture_requirements(
            requirements, non_functional_requirements
        )
        
        # Select appropriate architecture pattern
        recommended_pattern = await self._recommend_architecture_pattern(architecture_analysis)
        
        # Design system components
        system_components = await self._design_system_components(
            requirements, recommended_pattern
        )
        
        # Design data flow and integration
        data_flow = await self._design_data_flow(system_components, requirements)
        integration_patterns = await self._design_integration_patterns(system_components)
        
        # Create deployment architecture
        deployment_architecture = await self._design_deployment_architecture(
            system_components, non_functional_requirements
        )
        
        # Assess architecture quality
        quality_assessment = await self._assess_architecture_quality(
            recommended_pattern, system_components, non_functional_requirements
        )
        
        architecture_design = {
            "architecture_overview": {
                "pattern": recommended_pattern,
                "description": await self._generate_architecture_description(recommended_pattern),
                "design_principles": await self._define_design_principles(recommended_pattern),
                "quality_attributes": quality_assessment
            },
            "system_components": system_components,
            "data_flow": data_flow,
            "integration_patterns": integration_patterns,
            "deployment_architecture": deployment_architecture,
            "technical_decisions": await self._document_technical_decisions(
                recommended_pattern, system_components
            ),
            "implementation_roadmap": await self._create_implementation_roadmap(
                system_components, constraints
            ),
            "risks_and_mitigations": await self._identify_architecture_risks(
                recommended_pattern, system_components, constraints
            )
        }
        
        return {
            "status": "success",
            "architecture_design": architecture_design
        }
    
    async def _select_technology_stack(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Select appropriate technology stack based on requirements."""
        
        requirements = task.get("requirements", [])
        constraints = task.get("constraints", [])
        team_expertise = task.get("team_expertise", [])
        budget_constraints = task.get("budget", {})
        
        self.logger.info("Selecting technology stack")
        
        # Analyze requirements for technology needs
        tech_requirements = await self._analyze_technology_requirements(requirements)
        
        # Evaluate technologies for each category
        technology_evaluations = {}
        
        for category in TechStackCategory:
            if category.value in tech_requirements:
                candidates = await self._get_technology_candidates(category, tech_requirements[category.value])
                evaluation = await self._evaluate_technologies(
                    candidates, constraints, team_expertise, budget_constraints
                )
                technology_evaluations[category.value] = evaluation
        
        # Select final technology stack
        selected_stack = {}
        selection_rationale = {}
        
        for category, evaluation in technology_evaluations.items():
            if evaluation["candidates"]:
                best_candidate = max(evaluation["candidates"], key=lambda x: x["total_score"])
                selected_stack[category] = best_candidate
                selection_rationale[category] = {
                    "selected": best_candidate["name"],
                    "score": best_candidate["total_score"],
                    "reasons": best_candidate["strengths"],
                    "alternatives_considered": len(evaluation["candidates"]),
                    "key_factors": evaluation["key_decision_factors"]
                }
        
        # Assess technology compatibility
        compatibility_assessment = await self._assess_technology_compatibility(selected_stack)
        
        # Create migration strategy if needed
        migration_strategy = await self._create_migration_strategy(
            selected_stack, task.get("current_stack", {})
        )
        
        self.technology_stack = selected_stack
        
        return {
            "status": "success",
            "technology_stack": {
                "selected_technologies": selected_stack,
                "selection_rationale": selection_rationale,
                "compatibility_assessment": compatibility_assessment,
                "migration_strategy": migration_strategy,
                "total_estimated_cost": await self._estimate_technology_costs(selected_stack),
                "learning_curve_assessment": await self._assess_learning_curve(
                    selected_stack, team_expertise
                ),
                "recommendations": await self._generate_technology_recommendations(
                    selected_stack, constraints
                )
            }
        }
    
    async def _design_system_modules(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Design system modules and their interfaces."""
        
        requirements = task.get("requirements", [])
        architecture_pattern = task.get("architecture_pattern", "layered")
        
        self.logger.info("Designing system modules")
        
        # Identify functional domains
        functional_domains = await self._identify_functional_domains(requirements)
        
        # Design modules based on domains and architecture pattern
        modules = {}
        
        for domain in functional_domains:
            module = await self._design_module(domain, architecture_pattern, requirements)
            modules[domain["name"]] = module
        
        # Design module interfaces
        module_interfaces = await self._design_module_interfaces(modules)
        
        # Define module dependencies
        module_dependencies = await self._analyze_module_dependencies(modules)
        
        # Create module interaction patterns
        interaction_patterns = await self._design_module_interactions(
            modules, module_dependencies
        )
        
        # Validate module design
        design_validation = await self._validate_module_design(
            modules, module_dependencies, requirements
        )
        
        self.system_modules = modules
        
        return {
            "status": "success",
            "module_design": {
                "modules": modules,
                "interfaces": module_interfaces,
                "dependencies": module_dependencies,
                "interaction_patterns": interaction_patterns,
                "design_validation": design_validation,
                "implementation_guidelines": await self._create_implementation_guidelines(modules),
                "testing_strategy": await self._design_module_testing_strategy(modules)
            }
        }
    
    async def _design_api_specifications(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Design API specifications for system modules."""
        
        modules = task.get("modules", self.system_modules)
        api_style = task.get("api_style", "REST")  # REST, GraphQL, gRPC, etc.
        
        self.logger.info(f"Designing {api_style} API specifications")
        
        api_specifications = {}
        
        for module_name, module_info in modules.items():
            if module_info.get("exposes_api", False):
                api_spec = await self._design_module_api(
                    module_name, module_info, api_style
                )
                api_specifications[module_name] = api_spec
        
        # Design cross-cutting concerns
        cross_cutting_specs = await self._design_cross_cutting_api_concerns(api_style)
        
        # Create API documentation
        api_documentation = await self._generate_api_documentation(
            api_specifications, cross_cutting_specs
        )
        
        # Design API versioning strategy
        versioning_strategy = await self._design_api_versioning_strategy(api_style)
        
        # Create API testing specifications
        api_testing_specs = await self._design_api_testing_specifications(api_specifications)
        
        return {
            "status": "success",
            "api_design": {
                "specifications": api_specifications,
                "cross_cutting_concerns": cross_cutting_specs,
                "documentation": api_documentation,
                "versioning_strategy": versioning_strategy,
                "testing_specifications": api_testing_specs,
                "implementation_guidelines": await self._create_api_implementation_guidelines(
                    api_style, api_specifications
                )
            }
        }
    
    async def _assess_technical_risks(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Assess technical risks in the current architecture."""
        
        architecture = task.get("architecture", {})
        technology_stack = task.get("technology_stack", self.technology_stack)
        project_constraints = task.get("constraints", [])
        
        self.logger.info("Assessing technical risks")
        
        # Identify different types of risks
        risk_categories = {
            "technology_risks": await self._identify_technology_risks(technology_stack),
            "architecture_risks": await self._identify_architecture_risks_detailed(architecture),
            "integration_risks": await self._identify_integration_risks(architecture),
            "scalability_risks": await self._identify_scalability_risks(architecture),
            "security_risks": await self._identify_security_risks(architecture, technology_stack),
            "performance_risks": await self._identify_performance_risks(architecture),
            "maintenance_risks": await self._identify_maintenance_risks(architecture, technology_stack)
        }
        
        # Assess risk impact and probability
        risk_assessment = {}
        for category, risks in risk_categories.items():
            assessed_risks = []
            for risk in risks:
                assessment = await self._assess_risk_impact_probability(risk, project_constraints)
                risk.update(assessment)
                assessed_risks.append(risk)
            risk_assessment[category] = assessed_risks
        
        # Prioritize risks
        prioritized_risks = await self._prioritize_risks(risk_assessment)
        
        # Create mitigation strategies
        mitigation_strategies = {}
        for risk in prioritized_risks[:10]:  # Top 10 risks
            mitigation = await self._create_risk_mitigation_strategy(risk)
            mitigation_strategies[risk["id"]] = mitigation
        
        # Create risk monitoring plan
        monitoring_plan = await self._create_risk_monitoring_plan(prioritized_risks)
        
        return {
            "status": "success",
            "risk_assessment": {
                "risk_categories": risk_assessment,
                "prioritized_risks": prioritized_risks,
                "mitigation_strategies": mitigation_strategies,
                "monitoring_plan": monitoring_plan,
                "overall_risk_score": await self._calculate_overall_risk_score(prioritized_risks),
                "recommendations": await self._generate_risk_recommendations(prioritized_risks)
            }
        }
    
    async def _create_architectural_decision(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Create Architectural Decision Record (ADR)."""
        
        decision_context = task.get("context", "")
        problem_statement = task.get("problem", "")
        options = task.get("options", [])
        
        self.logger.info("Creating Architectural Decision Record")
        
        # Analyze each option
        option_analysis = []
        for option in options:
            analysis = await self._analyze_decision_option(option, decision_context)
            option_analysis.append(analysis)
        
        # Select best option
        recommended_option = await self._select_best_option(option_analysis)
        
        # Create ADR
        adr_id = f"ADR-{len(self.architectural_decisions) + 1:03d}"
        
        adr = {
            "id": adr_id,
            "title": task.get("title", f"Decision {adr_id}"),
            "status": ArchitecturalDecisionStatus.PROPOSED,
            "date": datetime.utcnow().isoformat(),
            "context": decision_context,
            "problem": problem_statement,
            "options_considered": option_analysis,
            "decision": recommended_option,
            "rationale": await self._generate_decision_rationale(
                recommended_option, option_analysis
            ),
            "consequences": await self._identify_decision_consequences(recommended_option),
            "implementation_notes": await self._generate_implementation_notes(recommended_option)
        }
        
        # Store ADR
        self.architectural_decisions[adr_id] = adr
        
        return {
            "status": "success",
            "adr": adr
        }
    
    async def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate Architect's output quality."""
        
        if not output or output.get("status") != "success":
            return False
        
        # Check for required architectural deliverables
        if "architecture_design" in output:
            design = output["architecture_design"]
            required_sections = ["architecture_overview", "system_components", "data_flow"]
            return all(section in design for section in required_sections)
        
        if "technology_stack" in output:
            stack = output["technology_stack"]
            return "selected_technologies" in stack and "selection_rationale" in stack
        
        if "module_design" in output:
            design = output["module_design"]
            return "modules" in design and "interfaces" in design
        
        if "api_design" in output:
            design = output["api_design"]
            return "specifications" in design
        
        return True
    
    def get_prompt_template(self) -> str:
        """Get Architect's prompt template."""
        return """
        You are an experienced System Architect responsible for designing scalable, maintainable software systems.
        
        Your responsibilities include:
        1. Designing system architecture and selecting appropriate patterns
        2. Selecting technology stacks based on requirements and constraints
        3. Designing system modules and their interfaces
        4. Creating API specifications and integration patterns
        5. Assessing technical risks and creating mitigation strategies
        6. Documenting architectural decisions and rationale
        
        Current context: {context}
        Task: {task}
        
        Focus on:
        - Scalability and performance considerations
        - Maintainability and code organization
        - Security and reliability requirements
        - Team capabilities and technology constraints
        - Cost-effectiveness and implementation complexity
        - Future extensibility and evolution
        
        Always consider both technical excellence and practical constraints in your decisions.
        """
    
    # Helper methods for architecture-specific functionality
    
    async def _analyze_architecture_requirements(self, requirements: List[Dict], nfr: Dict) -> Dict[str, Any]:
        """Analyze requirements to determine architecture approach."""
        analysis = {
            "complexity_level": "medium",
            "scalability_needs": nfr.get("scalability", {}).get("level", "medium"),
            "performance_requirements": nfr.get("performance", {}),
            "security_requirements": nfr.get("security", {}),
            "integration_complexity": "medium",
            "data_volume": nfr.get("data", {}).get("volume", "medium"),
            "user_load": nfr.get("users", {}).get("concurrent", 1000)
        }
        
        # Simple heuristics for analysis
        if len(requirements) > 50:
            analysis["complexity_level"] = "high"
        elif len(requirements) < 10:
            analysis["complexity_level"] = "low"
        
        return analysis
    
    async def _recommend_architecture_pattern(self, analysis: Dict[str, Any]) -> str:
        """Recommend architecture pattern based on analysis."""
        complexity = analysis.get("complexity_level", "medium")
        scalability = analysis.get("scalability_needs", "medium")
        
        if complexity == "high" and scalability == "high":
            return ArchitecturePattern.MICROSERVICES.value
        elif complexity == "high":
            return ArchitecturePattern.CLEAN_ARCHITECTURE.value
        elif scalability == "high":
            return ArchitecturePattern.EVENT_DRIVEN.value
        else:
            return ArchitecturePattern.LAYERED.value
    
    async def _design_system_components(self, requirements: List[Dict], pattern: str) -> Dict[str, Any]:
        """Design system components based on pattern."""
        components = {}
        
        if pattern == ArchitecturePattern.MICROSERVICES.value:
            # Design microservices
            domains = await self._identify_functional_domains(requirements)
            for i, domain in enumerate(domains[:5]):  # Limit for simplicity
                components[f"service_{i+1}"] = {
                    "name": domain.get("name", f"Service {i+1}"),
                    "responsibilities": domain.get("responsibilities", []),
                    "type": "microservice",
                    "apis": ["REST API"],
                    "database": f"{domain.get('name', 'service')}_db"
                }
        else:
            # Design layered components
            components = {
                "presentation_layer": {
                    "name": "Presentation Layer",
                    "responsibilities": ["UI", "API Controllers", "Input Validation"],
                    "type": "layer"
                },
                "business_layer": {
                    "name": "Business Logic Layer", 
                    "responsibilities": ["Business Rules", "Workflows", "Domain Logic"],
                    "type": "layer"
                },
                "data_layer": {
                    "name": "Data Access Layer",
                    "responsibilities": ["Database Access", "Data Mapping", "Persistence"],
                    "type": "layer"
                }
            }
        
        return components
    
    async def _identify_functional_domains(self, requirements: List[Dict]) -> List[Dict[str, Any]]:
        """Identify functional domains from requirements."""
        # Simplified domain identification
        domains = [
            {"name": "user_management", "responsibilities": ["Authentication", "User Profiles"]},
            {"name": "core_business", "responsibilities": ["Business Logic", "Workflows"]},
            {"name": "data_management", "responsibilities": ["Data Processing", "Storage"]},
            {"name": "notifications", "responsibilities": ["Messaging", "Alerts"]},
            {"name": "reporting", "responsibilities": ["Analytics", "Reports"]}
        ]
        
        # Return domains based on requirements (simplified)
        return domains[:min(len(requirements) // 5 + 1, len(domains))]
    
    # Placeholder methods for complex architecture operations
    # These would be implemented with more sophisticated logic in production
    
    async def _design_data_flow(self, components: Dict, requirements: List) -> Dict[str, Any]:
        """Design data flow between components."""
        return {"flow_type": "synchronous", "patterns": ["request-response", "event-driven"]}
    
    async def _design_integration_patterns(self, components: Dict) -> List[Dict[str, Any]]:
        """Design integration patterns."""
        return [{"pattern": "API Gateway", "usage": "External API access"}]
    
    async def _design_deployment_architecture(self, components: Dict, nfr: Dict) -> Dict[str, Any]:
        """Design deployment architecture."""
        return {
            "deployment_model": "cloud-native",
            "containerization": "Docker",
            "orchestration": "Kubernetes",
            "scaling_strategy": "horizontal"
        }
    
    async def _assess_architecture_quality(self, pattern: str, components: Dict, nfr: Dict) -> Dict[str, Any]:
        """Assess architecture quality attributes."""
        return {
            "scalability": 0.8,
            "maintainability": 0.85,
            "performance": 0.75,
            "security": 0.80,
            "reliability": 0.85
        }
    
    async def _generate_architecture_description(self, pattern: str) -> str:
        """Generate architecture description."""
        descriptions = {
            ArchitecturePattern.MICROSERVICES.value: "Distributed system with independently deployable services",
            ArchitecturePattern.LAYERED.value: "Traditional layered architecture with clear separation of concerns",
            ArchitecturePattern.CLEAN_ARCHITECTURE.value: "Clean architecture with dependency inversion and clear boundaries"
        }
        return descriptions.get(pattern, "Custom architecture pattern")
    
    async def _define_design_principles(self, pattern: str) -> List[str]:
        """Define design principles for the architecture."""
        return [
            "Single Responsibility Principle",
            "Dependency Inversion",
            "Separation of Concerns",
            "Loose Coupling",
            "High Cohesion"
        ]
    
    async def _document_technical_decisions(self, pattern: str, components: Dict) -> List[Dict[str, Any]]:
        """Document key technical decisions."""
        return [
            {
                "decision": f"Selected {pattern} architecture pattern",
                "rationale": "Best fit for scalability and maintainability requirements"
            }
        ]
    
    async def _create_implementation_roadmap(self, components: Dict, constraints: List) -> Dict[str, Any]:
        """Create implementation roadmap."""
        return {
            "phases": [
                {"name": "Foundation", "duration_weeks": 4, "components": ["core_infrastructure"]},
                {"name": "Core Features", "duration_weeks": 8, "components": ["business_logic"]},
                {"name": "Integration", "duration_weeks": 4, "components": ["external_apis"]}
            ]
        }
    
    async def _analyze_technology_requirements(self, requirements: List) -> Dict[str, Any]:
        """Analyze technology requirements from functional requirements."""
        return {
            "frontend": {"spa": True, "mobile": False},
            "backend": {"api": True, "real_time": False},
            "database": {"relational": True, "nosql": False},
            "caching": {"required": True},
            "messaging": {"required": False}
        }
    
    async def _get_technology_candidates(self, category: TechStackCategory, requirements: Dict) -> List[Dict[str, Any]]:
        """Get technology candidates for a category."""
        candidates_db = {
            TechStackCategory.FRONTEND: [
                {"name": "React", "type": "framework", "maturity": "high"},
                {"name": "Vue.js", "type": "framework", "maturity": "high"},
                {"name": "Angular", "type": "framework", "maturity": "high"}
            ],
            TechStackCategory.BACKEND: [
                {"name": "Node.js", "type": "runtime", "maturity": "high"},
                {"name": "Python/FastAPI", "type": "framework", "maturity": "high"},
                {"name": "Java/Spring", "type": "framework", "maturity": "high"}
            ],
            TechStackCategory.DATABASE: [
                {"name": "PostgreSQL", "type": "relational", "maturity": "high"},
                {"name": "MongoDB", "type": "document", "maturity": "high"},
                {"name": "Redis", "type": "cache", "maturity": "high"}
            ]
        }
        
        return candidates_db.get(category, [])
    
    async def _evaluate_technologies(self, candidates: List, constraints: List, expertise: List, budget: Dict) -> Dict[str, Any]:
        """Evaluate technology candidates."""
        evaluated = []
        
        for candidate in candidates:
            score = await self._calculate_technology_score(candidate, constraints, expertise)
            candidate["total_score"] = score
            candidate["strengths"] = ["Mature ecosystem", "Good performance"]
            evaluated.append(candidate)
        
        return {
            "candidates": sorted(evaluated, key=lambda x: x["total_score"], reverse=True),
            "key_decision_factors": ["Team expertise", "Ecosystem maturity", "Performance"]
        }
    
    async def _calculate_technology_score(self, candidate: Dict, constraints: List, expertise: List) -> float:
        """Calculate technology evaluation score."""
        base_score = 0.7  # Base score
        
        # Bonus for team expertise
        if candidate["name"].lower() in [e.lower() for e in expertise]:
            base_score += 0.2
        
        # Bonus for maturity
        if candidate.get("maturity") == "high":
            base_score += 0.1
        
        return min(1.0, base_score)
    
    async def _assess_technology_compatibility(self, stack: Dict) -> Dict[str, Any]:
        """Assess compatibility between selected technologies."""
        return {
            "compatibility_score": 0.9,
            "potential_issues": [],
            "integration_complexity": "medium"
        }
    
    async def _create_migration_strategy(self, new_stack: Dict, current_stack: Dict) -> Dict[str, Any]:
        """Create migration strategy from current to new stack."""
        if not current_stack:
            return {"type": "greenfield", "phases": []}
        
        return {
            "type": "incremental",
            "phases": [
                {"name": "Preparation", "duration_weeks": 2},
                {"name": "Migration", "duration_weeks": 8},
                {"name": "Validation", "duration_weeks": 2}
            ]
        }
    
    async def _estimate_technology_costs(self, stack: Dict) -> Dict[str, Any]:
        """Estimate costs for technology stack."""
        return {
            "licensing": 0,
            "infrastructure": 5000,
            "training": 10000,
            "total_monthly": 5000
        }
    
    async def _assess_learning_curve(self, stack: Dict, expertise: List) -> Dict[str, Any]:
        """Assess learning curve for the team."""
        return {
            "overall_difficulty": "medium",
            "training_weeks_required": 4,
            "team_readiness": 0.7
        }
    
    async def _generate_technology_recommendations(self, stack: Dict, constraints: List) -> List[str]:
        """Generate technology recommendations."""
        return [
            "Start with proof of concept for critical technologies",
            "Invest in team training early",
            "Set up development environments quickly"
        ]
    
    # Missing helper methods for architecture operations
    
    async def _identify_architecture_risks(self, pattern: str, components: Dict, constraints: List) -> List[Dict[str, Any]]:
        """Identify architecture-specific risks."""
        risks = []
        
        if pattern == ArchitecturePattern.MICROSERVICES.value:
            risks.append({
                "id": "ARCH-001",
                "type": "complexity",
                "description": "Microservices complexity may overwhelm small team",
                "impact": "high",
                "probability": 0.7
            })
            risks.append({
                "id": "ARCH-002", 
                "type": "network",
                "description": "Network latency between services",
                "impact": "medium",
                "probability": 0.8
            })
        
        if len(components) > 10:
            risks.append({
                "id": "ARCH-003",
                "type": "integration",
                "description": "High number of components increases integration complexity",
                "impact": "high",
                "probability": 0.6
            })
        
        return risks
    
    async def _design_module(self, domain: Dict, pattern: str, requirements: List) -> Dict[str, Any]:
        """Design a single module based on domain and pattern."""
        return {
            "name": domain["name"],
            "type": "module",
            "responsibilities": domain.get("responsibilities", []),
            "interfaces": {
                "public": [f"{domain['name']}_api"],
                "internal": []
            },
            "dependencies": [],
            "exposes_api": True if "api" in domain.get("responsibilities", []) else False,
            "data_access": True if any("data" in resp.lower() for resp in domain.get("responsibilities", [])) else False
        }
    
    async def _design_module_interfaces(self, modules: Dict) -> Dict[str, Any]:
        """Design interfaces between modules."""
        interfaces = {}
        
        for module_name, module_info in modules.items():
            if module_info.get("exposes_api"):
                interfaces[f"{module_name}_interface"] = {
                    "type": "REST API",
                    "endpoints": [
                        {"method": "GET", "path": f"/{module_name}"},
                        {"method": "POST", "path": f"/{module_name}"},
                        {"method": "PUT", "path": f"/{module_name}/{{id}}"},
                        {"method": "DELETE", "path": f"/{module_name}/{{id}}"}
                    ],
                    "authentication": "required",
                    "rate_limiting": True
                }
        
        return interfaces
    
    async def _analyze_module_dependencies(self, modules: Dict) -> Dict[str, List[str]]:
        """Analyze dependencies between modules."""
        dependencies = {}
        
        for module_name, module_info in modules.items():
            deps = []
            
            # Simple heuristic: modules with data access depend on data module
            if module_info.get("data_access") and "data_management" in modules:
                if module_name != "data_management":
                    deps.append("data_management")
            
            # User-related modules depend on user management
            if "user" in module_name.lower() and "user_management" in modules:
                if module_name != "user_management":
                    deps.append("user_management")
            
            dependencies[module_name] = deps
        
        return dependencies
    
    async def _design_module_interactions(self, modules: Dict, dependencies: Dict) -> List[Dict[str, Any]]:
        """Design interaction patterns between modules."""
        interactions = []
        
        for module_name, deps in dependencies.items():
            for dep in deps:
                interactions.append({
                    "from": module_name,
                    "to": dep,
                    "pattern": "synchronous_call",
                    "protocol": "HTTP/REST",
                    "authentication": "service_token"
                })
        
        return interactions
    
    async def _validate_module_design(self, modules: Dict, dependencies: Dict, requirements: List) -> Dict[str, Any]:
        """Validate module design against requirements."""
        validation = {
            "valid": True,
            "issues": [],
            "coverage_score": 0.9,
            "complexity_score": len(modules) * 0.1,  # Simple complexity metric
            "recommendations": []
        }
        
        # Check for circular dependencies
        for module, deps in dependencies.items():
            if module in deps:
                validation["issues"].append(f"Circular dependency in {module}")
                validation["valid"] = False
        
        # Check module count
        if len(modules) > 15:
            validation["recommendations"].append("Consider consolidating modules to reduce complexity")
        
        return validation
    
    async def _create_implementation_guidelines(self, modules: Dict) -> Dict[str, Any]:
        """Create implementation guidelines for modules."""
        return {
            "coding_standards": ["Follow clean architecture principles", "Use dependency injection"],
            "testing_requirements": ["Unit tests for all modules", "Integration tests for APIs"],
            "documentation": ["API documentation", "Module responsibility documentation"],
            "deployment": ["Containerize each module", "Use environment-specific configurations"]
        }
    
    async def _design_module_testing_strategy(self, modules: Dict) -> Dict[str, Any]:
        """Design testing strategy for modules."""
        return {
            "unit_testing": {
                "framework": "pytest",
                "coverage_target": 80,
                "mock_external_dependencies": True
            },
            "integration_testing": {
                "approach": "contract_testing",
                "test_doubles": "use_for_external_services"
            },
            "e2e_testing": {
                "scenarios": "critical_user_journeys",
                "environment": "staging"
            }
        }
    
    async def _design_module_api(self, module_name: str, module_info: Dict, api_style: str) -> Dict[str, Any]:
        """Design API for a specific module."""
        responsibilities = module_info.get("responsibilities", [])
        
        api_spec = {
            "module": module_name,
            "style": api_style,
            "base_path": f"/api/v1/{module_name}",
            "endpoints": [],
            "authentication": "bearer_token",
            "error_handling": "standard_http_codes"
        }
        
        # Generate endpoints based on responsibilities
        for responsibility in responsibilities:
            if "auth" in responsibility.lower():
                api_spec["endpoints"].extend([
                    {"method": "POST", "path": "/login", "description": "User login"},
                    {"method": "POST", "path": "/logout", "description": "User logout"},
                    {"method": "POST", "path": "/refresh", "description": "Refresh token"}
                ])
            elif "profile" in responsibility.lower():
                api_spec["endpoints"].extend([
                    {"method": "GET", "path": "/profile", "description": "Get profile"},
                    {"method": "PUT", "path": "/profile", "description": "Update profile"}
                ])
            else:
                # Generic CRUD endpoints
                api_spec["endpoints"].extend([
                    {"method": "GET", "path": f"/{responsibility}", "description": f"List {responsibility}"},
                    {"method": "POST", "path": f"/{responsibility}", "description": f"Create {responsibility}"},
                    {"method": "GET", "path": f"/{responsibility}/{{id}}", "description": f"Get {responsibility}"},
                    {"method": "PUT", "path": f"/{responsibility}/{{id}}", "description": f"Update {responsibility}"},
                    {"method": "DELETE", "path": f"/{responsibility}/{{id}}", "description": f"Delete {responsibility}"}
                ])
        
        return api_spec
    
    async def _design_cross_cutting_api_concerns(self, api_style: str) -> Dict[str, Any]:
        """Design cross-cutting concerns for APIs."""
        return {
            "authentication": {
                "type": "JWT Bearer Token",
                "token_expiry": "1 hour",
                "refresh_token_expiry": "7 days"
            },
            "authorization": {
                "model": "RBAC",
                "enforcement": "middleware"
            },
            "rate_limiting": {
                "requests_per_minute": 100,
                "burst_limit": 200
            },
            "logging": {
                "request_logging": True,
                "response_logging": True,
                "audit_logging": True
            },
            "error_handling": {
                "format": "RFC 7807 Problem Details",
                "include_stack_trace": False
            },
            "versioning": {
                "strategy": "URL versioning",
                "backward_compatibility": "2 versions"
            }
        }
    
    async def _generate_api_documentation(self, specifications: Dict, cross_cutting: Dict) -> Dict[str, Any]:
        """Generate API documentation."""
        return {
            "format": "OpenAPI 3.0",
            "sections": {
                "overview": "API overview and getting started",
                "authentication": "Authentication and authorization",
                "endpoints": "Detailed endpoint documentation",
                "examples": "Request/response examples",
                "error_codes": "Error handling guide"
            },
            "generation": "automated_from_code",
            "hosting": "developer_portal"
        }
    
    async def _design_api_versioning_strategy(self, api_style: str) -> Dict[str, Any]:
        """Design API versioning strategy."""
        return {
            "strategy": "URL versioning",
            "format": "/api/v{major}/",
            "backward_compatibility": "2 major versions",
            "deprecation_policy": "6 months notice",
            "breaking_changes": "major version only"
        }
    
    async def _design_api_testing_specifications(self, specifications: Dict) -> Dict[str, Any]:
        """Design API testing specifications."""
        return {
            "contract_testing": {
                "tool": "Pact",
                "consumer_driven": True
            },
            "load_testing": {
                "tool": "Artillery",
                "scenarios": ["normal_load", "peak_load", "stress_test"]
            },
            "security_testing": {
                "authentication": "test_invalid_tokens",
                "authorization": "test_privilege_escalation",
                "input_validation": "test_injection_attacks"
            }
        }
    
    async def _create_api_implementation_guidelines(self, api_style: str, specifications: Dict) -> Dict[str, Any]:
        """Create API implementation guidelines."""
        return {
            "conventions": {
                "naming": "snake_case for endpoints, camelCase for JSON",
                "http_methods": "RESTful conventions",
                "status_codes": "Semantic HTTP status codes"
            },
            "validation": {
                "input_validation": "validate_all_inputs",
                "output_validation": "schema_based"
            },
            "performance": {
                "pagination": "cursor_based",
                "caching": "ETags and Cache-Control headers",
                "compression": "gzip for responses > 1KB"
            }
        }
    
    # Risk assessment helper methods
    
    async def _identify_technology_risks(self, technology_stack: Dict) -> List[Dict[str, Any]]:
        """Identify technology-specific risks."""
        return [
            {
                "id": "TECH-001",
                "type": "technology_maturity",
                "description": "Using bleeding-edge technology versions",
                "impact": "medium",
                "probability": 0.5
            },
            {
                "id": "TECH-002",
                "type": "vendor_lockin",
                "description": "High dependency on specific vendor technologies",
                "impact": "high",
                "probability": 0.3
            }
        ]
    
    async def _identify_architecture_risks_detailed(self, architecture: Dict) -> List[Dict[str, Any]]:
        """Identify detailed architecture risks."""
        return [
            {
                "id": "ARCH-101",
                "type": "scalability",
                "description": "Architecture may not scale to required load",
                "impact": "high",
                "probability": 0.4
            }
        ]
    
    async def _identify_integration_risks(self, architecture: Dict) -> List[Dict[str, Any]]:
        """Identify integration risks."""
        return [
            {
                "id": "INT-001",
                "type": "api_compatibility",
                "description": "Third-party API changes breaking integration",
                "impact": "medium",
                "probability": 0.6
            }
        ]
    
    async def _identify_scalability_risks(self, architecture: Dict) -> List[Dict[str, Any]]:
        """Identify scalability risks."""
        return [
            {
                "id": "SCALE-001",
                "type": "database_bottleneck",
                "description": "Database becomes bottleneck under high load",
                "impact": "high",
                "probability": 0.7
            }
        ]
    
    async def _identify_security_risks(self, architecture: Dict, tech_stack: Dict) -> List[Dict[str, Any]]:
        """Identify security risks."""
        return [
            {
                "id": "SEC-001",
                "type": "authentication",
                "description": "Weak authentication mechanisms",
                "impact": "critical",
                "probability": 0.3
            }
        ]
    
    async def _identify_performance_risks(self, architecture: Dict) -> List[Dict[str, Any]]:
        """Identify performance risks."""
        return [
            {
                "id": "PERF-001",
                "type": "latency",
                "description": "High latency due to multiple service calls",
                "impact": "medium",
                "probability": 0.5
            }
        ]
    
    async def _identify_maintenance_risks(self, architecture: Dict, tech_stack: Dict) -> List[Dict[str, Any]]:
        """Identify maintenance risks."""
        return [
            {
                "id": "MAINT-001",
                "type": "complexity",
                "description": "High maintenance overhead due to complexity",
                "impact": "medium",
                "probability": 0.6
            }
        ]
    
    async def _assess_risk_impact_probability(self, risk: Dict, constraints: List) -> Dict[str, Any]:
        """Assess risk impact and probability."""
        return {
            "impact_score": {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(risk.get("impact", "medium"), 2),
            "probability_score": risk.get("probability", 0.5),
            "risk_score": risk.get("probability", 0.5) * {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(risk.get("impact", "medium"), 2)
        }
    
    async def _prioritize_risks(self, risk_categories: Dict) -> List[Dict[str, Any]]:
        """Prioritize risks across all categories."""
        all_risks = []
        
        for category, risks in risk_categories.items():
            for risk in risks:
                risk["category"] = category
                all_risks.append(risk)
        
        # Sort by risk score (probability * impact)
        return sorted(all_risks, key=lambda r: r.get("risk_score", 0), reverse=True)
    
    async def _create_risk_mitigation_strategy(self, risk: Dict) -> Dict[str, Any]:
        """Create mitigation strategy for a risk."""
        return {
            "risk_id": risk.get("id"),
            "mitigation_type": "preventive",
            "actions": [
                "Implement monitoring and alerting",
                "Create contingency plan",
                "Regular risk assessment review"
            ],
            "owner": "architecture_team",
            "timeline": "immediate",
            "cost_estimate": "medium"
        }
    
    async def _create_risk_monitoring_plan(self, risks: List) -> Dict[str, Any]:
        """Create risk monitoring plan."""
        return {
            "monitoring_frequency": "weekly",
            "key_metrics": ["system_performance", "error_rates", "user_satisfaction"],
            "escalation_procedures": "defined",
            "review_schedule": "monthly_architecture_review"
        }
    
    async def _calculate_overall_risk_score(self, risks: List) -> float:
        """Calculate overall risk score."""
        if not risks:
            return 0.0
        
        total_score = sum(risk.get("risk_score", 0) for risk in risks)
        return min(total_score / len(risks), 4.0)  # Cap at 4.0
    
    async def _generate_risk_recommendations(self, risks: List) -> List[str]:
        """Generate risk recommendations."""
        return [
            "Focus on high-priority risks first",
            "Implement continuous monitoring",
            "Regular architecture reviews",
            "Maintain risk register"
        ]
    
    # ADR helper methods
    
    async def _analyze_decision_option(self, option: Dict, context: str) -> Dict[str, Any]:
        """Analyze a decision option."""
        return {
            "name": option.get("name", "Unknown Option"),
            "pros": option.get("pros", []),
            "cons": option.get("cons", []),
            "feasibility_score": 0.8,
            "risk_score": 0.3,
            "cost_score": 0.5,
            "total_score": 0.7  # Weighted average
        }
    
    async def _select_best_option(self, options: List) -> Dict[str, Any]:
        """Select the best option from analysis."""
        if not options:
            return {"name": "No option selected", "score": 0}
        
        best_option = max(options, key=lambda o: o.get("total_score", 0))
        return best_option
    
    async def _generate_decision_rationale(self, selected_option: Dict, all_options: List) -> str:
        """Generate rationale for the decision."""
        option_name = selected_option.get("name", "Selected option")
        score = selected_option.get("total_score", 0)
        
        return f"{option_name} was selected with a score of {score:.2f} based on feasibility, risk, and cost analysis. This option provides the best balance of benefits while minimizing risks and costs."
    
    async def _identify_decision_consequences(self, option: Dict) -> Dict[str, List[str]]:
        """Identify consequences of the decision."""
        return {
            "positive": [
                "Improved system performance",
                "Better maintainability",
                "Reduced technical debt"
            ],
            "negative": [
                "Initial implementation complexity",
                "Learning curve for team",
                "Migration effort required"
            ],
            "neutral": [
                "New monitoring requirements",
                "Updated documentation needed"
            ]
        }
    
    async def _generate_implementation_notes(self, option: Dict) -> List[str]:
        """Generate implementation notes for the decision."""
        return [
            "Create detailed implementation plan",
            "Set up development environment",
            "Plan team training sessions",
            "Define success metrics",
            "Schedule regular review checkpoints"
        ]