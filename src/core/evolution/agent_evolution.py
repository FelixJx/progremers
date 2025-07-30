"""Agent自我进化系统 - 通过项目经验持续学习和优化"""

import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

from src.utils import get_logger
from src.core.memory.rag_retriever import RAGRetriever
from src.core.database.session import get_session
from src.core.database.models import Project, Sprint

logger = get_logger(__name__)


class EvolutionTrigger(str, Enum):
    """进化触发条件"""
    PROJECT_COMPLETION = "project_completion"    # 项目完成
    PERFORMANCE_DECLINE = "performance_decline"  # 性能下降
    ERROR_PATTERN = "error_pattern"              # 错误模式
    FEEDBACK_NEGATIVE = "feedback_negative"      # 负面反馈
    KNOWLEDGE_GAP = "knowledge_gap"              # 知识缺口
    PERIODIC_REVIEW = "periodic_review"          # 定期复盘


class EvolutionAction(str, Enum):
    """进化行动类型"""
    PROMPT_OPTIMIZATION = "prompt_optimization"    # 提示词优化
    KNOWLEDGE_UPDATE = "knowledge_update"          # 知识库更新
    STRATEGY_ADJUSTMENT = "strategy_adjustment"    # 策略调整
    SKILL_ENHANCEMENT = "skill_enhancement"        # 技能增强
    BEHAVIOR_CORRECTION = "behavior_correction"    # 行为纠正
    COLLABORATION_IMPROVEMENT = "collaboration_improvement"  # 协作改进


@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_name: str
    value: float
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


@dataclass
class EvolutionInsight:
    """进化洞察"""
    insight_type: str
    description: str
    evidence: List[Dict[str, Any]]
    confidence: float
    action_recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvolutionPlan:
    """进化计划"""
    agent_id: str
    trigger: EvolutionTrigger
    insights: List[EvolutionInsight]
    actions: List[EvolutionAction]
    expected_improvements: Dict[str, float]
    implementation_timeline: Dict[str, datetime]
    success_criteria: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "trigger": self.trigger.value,
            "insights": [insight.to_dict() for insight in self.insights],
            "actions": [action.value for action in self.actions],
            "expected_improvements": self.expected_improvements,
            "implementation_timeline": {
                k: v.isoformat() for k, v in self.implementation_timeline.items()
            },
            "success_criteria": self.success_criteria
        }


class AgentEvolutionEngine:
    """
    Agent进化引擎 - 核心自我进化系统
    
    功能：
    1. 持续监控Agent表现
    2. 识别改进机会
    3. 生成进化计划
    4. 执行优化措施
    5. 验证进化效果
    """
    
    def __init__(self):
        self.logger = get_logger(f"{self.__class__.__name__}")
        self.rag_retriever = RAGRetriever()
        
        # 性能追踪
        self.performance_history: Dict[str, List[PerformanceMetric]] = {}
        
        # 进化配置
        self.evolution_config = {
            "min_projects_for_evolution": 3,      # 最少项目数
            "performance_window_days": 30,        # 性能窗口期
            "decline_threshold": 0.15,            # 性能下降阈值
            "confidence_threshold": 0.7,          # 置信度阈值
            "max_concurrent_evolutions": 2        # 最大并发进化数
        }
        
        # 当前进化状态
        self.active_evolutions: Dict[str, EvolutionPlan] = {}
        
    async def initialize(self):
        """初始化进化引擎"""
        await self.rag_retriever.initialize()
        self.logger.info("Agent进化引擎初始化完成")
    
    async def record_performance(
        self,
        agent_id: str,
        metric_name: str,
        value: float,
        context: Dict[str, Any] = None
    ):
        """记录Agent性能指标"""
        
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = []
        
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.utcnow(),
            context=context or {}
        )
        
        self.performance_history[agent_id].append(metric)
        
        # 限制历史记录数量
        if len(self.performance_history[agent_id]) > 1000:
            self.performance_history[agent_id] = self.performance_history[agent_id][-800:]
        
        self.logger.debug(f"记录{agent_id}性能: {metric_name}={value}")
        
        # 检查是否需要触发进化
        await self._check_evolution_triggers(agent_id, metric)
    
    async def conduct_project_retrospective(
        self,
        project_id: str,
        sprint_data: Dict[str, Any]
    ) -> Dict[str, EvolutionInsight]:
        """项目复盘 - 提取经验和改进点"""
        
        self.logger.info(f"开始项目{project_id}复盘...")
        
        insights = {}
        
        # 1. 分析各Agent表现
        for agent_id in sprint_data.get("team_members", []):
            agent_insights = await self._analyze_agent_performance(
                agent_id, project_id, sprint_data
            )
            insights[agent_id] = agent_insights
        
        # 2. 团队协作分析
        collaboration_insights = await self._analyze_team_collaboration(
            project_id, sprint_data
        )
        insights["team_collaboration"] = collaboration_insights
        
        # 3. 技术决策分析
        tech_insights = await self._analyze_technical_decisions(
            project_id, sprint_data
        )
        insights["technical_decisions"] = tech_insights
        
        # 4. 存储复盘结果
        await self._store_retrospective_results(project_id, insights)
        
        # 5. 触发必要的进化
        for agent_id, agent_insights in insights.items():
            if agent_id.startswith("agent_"):
                await self._trigger_evolution(
                    agent_id, 
                    EvolutionTrigger.PROJECT_COMPLETION,
                    [agent_insights]
                )
        
        self.logger.info(f"项目{project_id}复盘完成")
        return insights
    
    async def _analyze_agent_performance(
        self,
        agent_id: str,
        project_id: str,
        sprint_data: Dict[str, Any]
    ) -> EvolutionInsight:
        """分析单个Agent的项目表现"""
        
        evidence = []
        recommendations = []
        
        # 获取Agent的历史性能数据
        agent_metrics = self.performance_history.get(agent_id, [])
        recent_metrics = [
            m for m in agent_metrics 
            if m.timestamp > datetime.utcnow() - timedelta(days=30)
        ]
        
        # 1. 任务完成质量分析
        task_quality = await self._analyze_task_quality(agent_id, project_id, sprint_data)
        evidence.append({
            "type": "task_quality",
            "metrics": task_quality,
            "analysis": "任务完成质量评估"
        })
        
        # 2. 响应时间分析
        response_times = [
            m.value for m in recent_metrics 
            if m.metric_name == "response_time"
        ]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            evidence.append({
                "type": "response_time",
                "average": avg_response_time,
                "trend": self._calculate_trend(response_times)
            })
            
            if avg_response_time > 5.0:  # 超过5秒
                recommendations.append("优化响应速度，考虑并行处理")
        
        # 3. 错误模式识别
        error_patterns = await self._identify_error_patterns(agent_id, recent_metrics)
        if error_patterns:
            evidence.append({
                "type": "error_patterns",
                "patterns": error_patterns
            })
            recommendations.extend([
                f"改进{pattern['type']}相关的处理逻辑" 
                for pattern in error_patterns
            ])
        
        # 4. 协作效率分析
        collaboration_score = await self._analyze_collaboration_efficiency(
            agent_id, project_id, sprint_data
        )
        evidence.append({
            "type": "collaboration",
            "score": collaboration_score,
            "details": "与其他Agent的协作效率"
        })
        
        # 计算置信度
        confidence = min(1.0, len(evidence) * 0.2 + len(recent_metrics) * 0.01)
        
        return EvolutionInsight(
            insight_type="agent_performance",
            description=f"Agent {agent_id} 项目表现分析",
            evidence=evidence,
            confidence=confidence,
            action_recommendations=recommendations
        )
    
    async def _analyze_team_collaboration(
        self,
        project_id: str,
        sprint_data: Dict[str, Any]
    ) -> EvolutionInsight:
        """分析团队协作模式"""
        
        evidence = []
        recommendations = []
        
        # 1. 消息流量分析
        message_stats = sprint_data.get("communication_stats", {})
        if message_stats:
            evidence.append({
                "type": "communication_volume",
                "stats": message_stats
            })
            
            # 检查通信不平衡
            agent_messages = message_stats.get("agent_message_counts", {})
            if agent_messages:
                values = list(agent_messages.values())
                if max(values) > 3 * min(values):
                    recommendations.append("优化Agent间通信平衡，避免过度依赖单一Agent")
        
        # 2. 决策冲突分析
        conflicts = sprint_data.get("decision_conflicts", [])
        if conflicts:
            evidence.append({
                "type": "decision_conflicts",
                "count": len(conflicts),
                "patterns": self._analyze_conflict_patterns(conflicts)
            })
            
            if len(conflicts) > 3:
                recommendations.append("改进决策流程，减少不必要的冲突")
        
        # 3. 任务移交效率
        handoff_delays = sprint_data.get("task_handoff_delays", [])
        if handoff_delays:
            avg_delay = statistics.mean(handoff_delays)
            evidence.append({
                "type": "handoff_efficiency",
                "average_delay": avg_delay,
                "total_delays": len(handoff_delays)
            })
            
            if avg_delay > 2.0:  # 超过2小时
                recommendations.append("优化任务移交流程，提高上下文传递效率")
        
        confidence = min(1.0, len(evidence) * 0.3)
        
        return EvolutionInsight(
            insight_type="team_collaboration",
            description="团队协作模式分析",
            evidence=evidence,
            confidence=confidence,
            action_recommendations=recommendations
        )
    
    async def _analyze_technical_decisions(
        self,
        project_id: str,
        sprint_data: Dict[str, Any]
    ) -> EvolutionInsight:
        """分析技术决策质量"""
        
        evidence = []
        recommendations = []
        
        # 1. 架构决策评估
        arch_decisions = sprint_data.get("architecture_decisions", [])
        for decision in arch_decisions:
            # 评估决策的后续影响
            impact_score = await self._evaluate_decision_impact(
                decision, sprint_data
            )
            evidence.append({
                "type": "architecture_decision",
                "decision": decision.get("summary", ""),
                "impact_score": impact_score
            })
            
            if impact_score < 0.6:
                recommendations.append(f"重新评估决策: {decision.get('summary', '')[:50]}")
        
        # 2. 技术债务积累
        tech_debt = sprint_data.get("technical_debt", [])
        if tech_debt:
            debt_score = sum(item.get("severity", 1) for item in tech_debt)
            evidence.append({
                "type": "technical_debt",
                "total_score": debt_score,
                "items": len(tech_debt)
            })
            
            if debt_score > 10:
                recommendations.append("制定技术债务清理计划")
        
        # 3. 代码质量趋势
        quality_metrics = sprint_data.get("code_quality", {})
        if quality_metrics:
            evidence.append({
                "type": "code_quality",
                "metrics": quality_metrics
            })
            
            coverage = quality_metrics.get("test_coverage", 0)
            if coverage < 0.8:
                recommendations.append("提高测试覆盖率")
        
        confidence = min(1.0, len(evidence) * 0.25)
        
        return EvolutionInsight(
            insight_type="technical_decisions",
            description="技术决策质量分析",
            evidence=evidence,
            confidence=confidence,
            action_recommendations=recommendations
        )
    
    async def generate_evolution_plan(
        self,
        agent_id: str,
        trigger: EvolutionTrigger,
        insights: List[EvolutionInsight]
    ) -> EvolutionPlan:
        """生成Agent进化计划"""
        
        # 1. 综合分析洞察
        high_confidence_insights = [
            insight for insight in insights 
            if insight.confidence >= self.evolution_config["confidence_threshold"]
        ]
        
        if not high_confidence_insights:
            self.logger.warning(f"Agent {agent_id} 缺乏高置信度洞察，跳过进化")
            return None
        
        # 2. 确定进化行动
        actions = []
        expected_improvements = {}
        
        for insight in high_confidence_insights:
            # 根据洞察类型决定行动
            if "response_time" in str(insight.evidence):
                actions.append(EvolutionAction.PROMPT_OPTIMIZATION)
                expected_improvements["response_time"] = 0.2  # 期望提升20%
            
            if "error_patterns" in str(insight.evidence):
                actions.append(EvolutionAction.BEHAVIOR_CORRECTION)
                expected_improvements["error_rate"] = -0.3  # 期望减少30%错误
            
            if "collaboration" in insight.insight_type:
                actions.append(EvolutionAction.COLLABORATION_IMPROVEMENT)
                expected_improvements["collaboration_score"] = 0.15
            
            if "knowledge_gap" in str(insight.evidence):
                actions.append(EvolutionAction.KNOWLEDGE_UPDATE)
                expected_improvements["task_accuracy"] = 0.1
        
        # 去重
        actions = list(set(actions))
        
        # 3. 制定实施时间线
        timeline = {}
        base_time = datetime.utcnow()
        
        for i, action in enumerate(actions):
            timeline[action.value] = base_time + timedelta(days=i+1)
        
        # 4. 设定成功标准
        success_criteria = {}
        for metric, improvement in expected_improvements.items():
            current_value = await self._get_current_metric_value(agent_id, metric)
            if current_value is not None:
                if improvement > 0:
                    success_criteria[metric] = current_value * (1 + improvement)
                else:
                    success_criteria[metric] = current_value * (1 + improvement)
        
        plan = EvolutionPlan(
            agent_id=agent_id,
            trigger=trigger,
            insights=high_confidence_insights,
            actions=actions,
            expected_improvements=expected_improvements,
            implementation_timeline=timeline,
            success_criteria=success_criteria
        )
        
        self.logger.info(f"为Agent {agent_id} 生成进化计划: {len(actions)}个行动")
        return plan
    
    async def execute_evolution_plan(self, plan: EvolutionPlan) -> bool:
        """执行进化计划"""
        
        agent_id = plan.agent_id
        self.logger.info(f"开始执行Agent {agent_id} 的进化计划...")
        
        try:
            # 记录进化开始
            self.active_evolutions[agent_id] = plan
            
            # 逐个执行进化行动
            for action in plan.actions:
                success = await self._execute_evolution_action(agent_id, action, plan)
                if not success:
                    self.logger.error(f"进化行动失败: {action.value}")
                    return False
                
                # 等待一段时间让变化生效
                await asyncio.sleep(1)
            
            # 记录进化完成
            await self._record_evolution_completion(plan)
            
            # 清理活跃进化记录
            if agent_id in self.active_evolutions:
                del self.active_evolutions[agent_id]
            
            self.logger.info(f"Agent {agent_id} 进化计划执行完成")
            return True
            
        except Exception as e:
            self.logger.error(f"执行进化计划失败: {str(e)}")
            return False
    
    async def _execute_evolution_action(
        self,
        agent_id: str,
        action: EvolutionAction,
        plan: EvolutionPlan
    ) -> bool:
        """执行具体的进化行动"""
        
        try:
            if action == EvolutionAction.PROMPT_OPTIMIZATION:
                return await self._optimize_agent_prompts(agent_id, plan)
            
            elif action == EvolutionAction.KNOWLEDGE_UPDATE:
                return await self._update_agent_knowledge(agent_id, plan)
            
            elif action == EvolutionAction.STRATEGY_ADJUSTMENT:
                return await self._adjust_agent_strategy(agent_id, plan)
            
            elif action == EvolutionAction.BEHAVIOR_CORRECTION:
                return await self._correct_agent_behavior(agent_id, plan)
            
            elif action == EvolutionAction.COLLABORATION_IMPROVEMENT:
                return await self._improve_collaboration(agent_id, plan)
            
            else:
                self.logger.warning(f"未知进化行动: {action.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"执行进化行动{action.value}失败: {str(e)}")
            return False
    
    async def validate_evolution_effectiveness(
        self,
        agent_id: str,
        plan: EvolutionPlan,
        validation_period_days: int = 7
    ) -> Dict[str, Any]:
        """验证进化效果"""
        
        self.logger.info(f"开始验证Agent {agent_id} 的进化效果...")
        
        validation_results = {
            "agent_id": agent_id,
            "validation_start": datetime.utcnow().isoformat(),
            "plan_id": f"{agent_id}_{plan.trigger.value}",
            "metrics_comparison": {},
            "success_rate": 0.0,
            "recommendations": []
        }
        
        # 获取进化后的性能数据
        cutoff_date = datetime.utcnow() - timedelta(days=validation_period_days)
        recent_metrics = [
            m for m in self.performance_history.get(agent_id, [])
            if m.timestamp > cutoff_date
        ]
        
        # 对比成功标准
        met_criteria = 0
        total_criteria = len(plan.success_criteria)
        
        for metric_name, target_value in plan.success_criteria.items():
            current_value = await self._get_current_metric_value(agent_id, metric_name)
            
            if current_value is not None:
                improvement = (current_value - target_value) / target_value if target_value != 0 else 0
                validation_results["metrics_comparison"][metric_name] = {
                    "target": target_value,
                    "current": current_value,
                    "improvement": improvement,
                    "met": current_value >= target_value if target_value > 0 else current_value <= target_value
                }
                
                if validation_results["metrics_comparison"][metric_name]["met"]:
                    met_criteria += 1
        
        validation_results["success_rate"] = met_criteria / total_criteria if total_criteria > 0 else 0
        
        # 生成建议
        if validation_results["success_rate"] < 0.7:
            validation_results["recommendations"].append("考虑调整进化策略或延长验证期")
        
        if validation_results["success_rate"] >= 0.8:
            validation_results["recommendations"].append("进化效果良好，可考虑类似优化")
        
        self.logger.info(f"Agent {agent_id} 进化效果验证完成: {validation_results['success_rate']:.2%}")
        
        return validation_results
    
    # Helper方法实现
    async def _check_evolution_triggers(self, agent_id: str, metric: PerformanceMetric):
        """检查进化触发条件"""
        # 实现进化触发逻辑
        pass
    
    async def _trigger_evolution(self, agent_id: str, trigger: EvolutionTrigger, insights: List[EvolutionInsight]):
        """触发进化过程"""
        plan = await self.generate_evolution_plan(agent_id, trigger, insights)
        if plan:
            await self.execute_evolution_plan(plan)
    
    # ... 其他helper方法的实现
    
    async def get_evolution_status(self, agent_id: str = None) -> Dict[str, Any]:
        """获取进化状态"""
        
        if agent_id:
            return {
                "agent_id": agent_id,
                "active_evolution": self.active_evolutions.get(agent_id),
                "performance_history_count": len(self.performance_history.get(agent_id, [])),
                "last_evolution": await self._get_last_evolution_record(agent_id)
            }
        else:
            return {
                "total_agents_monitored": len(self.performance_history),
                "active_evolutions": len(self.active_evolutions),
                "evolution_config": self.evolution_config
            }
    
    # 数据持久化方法
    async def _store_retrospective_results(self, project_id: str, insights: Dict[str, EvolutionInsight]):
        """存储复盘结果"""
        # 实现数据存储逻辑
        pass
    
    async def _record_evolution_completion(self, plan: EvolutionPlan):
        """记录进化完成"""
        # 实现进化记录存储
        pass