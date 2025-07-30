"""Agent进化度量系统 - 量化Agent的学习和进化效果"""

import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict

from src.utils import get_logger

logger = get_logger(__name__)


class MetricCategory(str, Enum):
    """指标类别"""
    PERFORMANCE = "performance"        # 性能指标
    LEARNING = "learning"             # 学习指标
    COLLABORATION = "collaboration"    # 协作指标
    ADAPTATION = "adaptation"         # 适应性指标
    INNOVATION = "innovation"         # 创新指标
    EFFICIENCY = "efficiency"         # 效率指标


class MetricTrend(str, Enum):
    """指标趋势"""
    IMPROVING = "improving"           # 改善中
    STABLE = "stable"                # 稳定
    DECLINING = "declining"          # 下降中
    VOLATILE = "volatile"            # 波动大


@dataclass
class EvolutionMetric:
    """进化指标"""
    name: str
    category: MetricCategory
    value: float
    timestamp: datetime
    context: Dict[str, Any]
    agent_id: str
    project_id: Optional[str]
    baseline_value: Optional[float]
    improvement_rate: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "agent_id": self.agent_id,
            "project_id": self.project_id,
            "baseline_value": self.baseline_value,
            "improvement_rate": self.improvement_rate,
            "confidence": self.confidence
        }


@dataclass
class EvolutionReport:
    """进化报告"""
    agent_id: str
    evaluation_period: Tuple[datetime, datetime]
    overall_score: float
    metric_scores: Dict[str, float]
    trend_analysis: Dict[str, MetricTrend]
    key_improvements: List[str]
    areas_for_improvement: List[str]
    evolution_recommendations: List[str]
    comparison_with_peers: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "evaluation_period": [
                self.evaluation_period[0].isoformat(),
                self.evaluation_period[1].isoformat()
            ],
            "overall_score": self.overall_score,
            "metric_scores": self.metric_scores,
            "trend_analysis": {k: v.value for k, v in self.trend_analysis.items()},
            "key_improvements": self.key_improvements,
            "areas_for_improvement": self.areas_for_improvement,
            "evolution_recommendations": self.evolution_recommendations,
            "comparison_with_peers": self.comparison_with_peers
        }


class EvolutionMetricsEngine:
    """
    Agent进化度量引擎 - 量化和评估Agent的进化效果
    
    核心功能：
    1. 多维度性能度量
    2. 学习效果评估
    3. 进化趋势分析
    4. 同伴对比分析
    5. 进化建议生成
    """
    
    def __init__(self):
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # 指标历史数据
        self.metric_history: Dict[str, List[EvolutionMetric]] = defaultdict(list)
        
        # 基线数据
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        # 度量配置
        self.metric_definitions = {
            # 性能指标
            "task_completion_rate": {
                "category": MetricCategory.PERFORMANCE,
                "weight": 0.25,
                "higher_is_better": True,
                "baseline_periods": 5
            },
            "response_time": {
                "category": MetricCategory.PERFORMANCE,
                "weight": 0.15,
                "higher_is_better": False,
                "baseline_periods": 5
            },
            "quality_score": {
                "category": MetricCategory.PERFORMANCE,
                "weight": 0.2,
                "higher_is_better": True,
                "baseline_periods": 5
            },
            
            # 学习指标
            "knowledge_acquisition_rate": {
                "category": MetricCategory.LEARNING,
                "weight": 0.15,
                "higher_is_better": True,
                "baseline_periods": 3
            },
            "pattern_recognition_accuracy": {
                "category": MetricCategory.LEARNING,
                "weight": 0.1,
                "higher_is_better": True,
                "baseline_periods": 3
            },
            "error_correction_speed": {
                "category": MetricCategory.LEARNING,
                "weight": 0.1,
                "higher_is_better": True,
                "baseline_periods": 3
            },
            
            # 协作指标
            "collaboration_effectiveness": {
                "category": MetricCategory.COLLABORATION,
                "weight": 0.1,
                "higher_is_better": True,
                "baseline_periods": 3
            },
            "communication_clarity": {
                "category": MetricCategory.COLLABORATION,
                "weight": 0.05,
                "higher_is_better": True,
                "baseline_periods": 3
            },
            
            # 适应性指标
            "context_adaptation_speed": {
                "category": MetricCategory.ADAPTATION,
                "weight": 0.08,
                "higher_is_better": True,
                "baseline_periods": 3
            },
            "new_domain_learning": {
                "category": MetricCategory.ADAPTATION,
                "weight": 0.07,
                "higher_is_better": True,
                "baseline_periods": 3
            },
            
            # 创新指标
            "solution_creativity": {
                "category": MetricCategory.INNOVATION,
                "weight": 0.05,
                "higher_is_better": True,
                "baseline_periods": 5
            },
            
            # 效率指标
            "resource_utilization": {
                "category": MetricCategory.EFFICIENCY,
                "weight": 0.1,
                "higher_is_better": True,
                "baseline_periods": 3
            }
        }
        
        # 评估配置
        self.evaluation_config = {
            "min_data_points": 5,          # 最少数据点数
            "trend_window_days": 14,       # 趋势分析窗口
            "improvement_threshold": 0.05,  # 改进阈值
            "volatility_threshold": 0.2    # 波动阈值
        }
    
    async def record_metric(
        self,
        agent_id: str,
        metric_name: str,
        value: float,
        context: Dict[str, Any] = None,
        project_id: str = None
    ):
        """记录Agent指标数据"""
        
        if metric_name not in self.metric_definitions:
            self.logger.warning(f"未知指标: {metric_name}")
            return
        
        # 获取基线值
        baseline_value = self._get_baseline_value(agent_id, metric_name)
        
        # 计算改进率
        if baseline_value is not None and baseline_value != 0:
            improvement_rate = (value - baseline_value) / abs(baseline_value)
        else:
            improvement_rate = 0.0
        
        # 创建指标记录
        metric = EvolutionMetric(
            name=metric_name,
            category=self.metric_definitions[metric_name]["category"],
            value=value,
            timestamp=datetime.utcnow(),
            context=context or {},
            agent_id=agent_id,
            project_id=project_id,
            baseline_value=baseline_value,
            improvement_rate=improvement_rate,
            confidence=self._calculate_metric_confidence(agent_id, metric_name, value)
        )
        
        # 存储指标
        metric_key = f"{agent_id}_{metric_name}"
        self.metric_history[metric_key].append(metric)
        
        # 限制历史数据数量
        if len(self.metric_history[metric_key]) > 1000:
            self.metric_history[metric_key] = self.metric_history[metric_key][-800:]
        
        # 更新基线
        await self._update_baseline(agent_id, metric_name)
        
        self.logger.debug(f"记录指标 {agent_id}.{metric_name} = {value}")
    
    async def evaluate_agent_evolution(
        self,
        agent_id: str,
        evaluation_period_days: int = 30
    ) -> EvolutionReport:
        """评估Agent进化效果"""
        
        self.logger.info(f"开始评估Agent {agent_id} 的进化效果...")
        
        # 确定评估周期
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=evaluation_period_days)
        evaluation_period = (start_time, end_time)
        
        # 收集评估周期内的指标数据
        period_metrics = self._get_metrics_in_period(agent_id, start_time, end_time)
        
        if not period_metrics:
            self.logger.warning(f"Agent {agent_id} 在评估周期内没有足够的指标数据")
            return self._create_empty_report(agent_id, evaluation_period)
        
        # 1. 计算各类指标得分
        metric_scores = await self._calculate_metric_scores(period_metrics)
        
        # 2. 计算总体得分
        overall_score = self._calculate_overall_score(metric_scores)
        
        # 3. 趋势分析
        trend_analysis = await self._analyze_trends(agent_id, period_metrics)
        
        # 4. 识别关键改进
        key_improvements = self._identify_key_improvements(period_metrics)
        
        # 5. 识别待改进领域
        areas_for_improvement = self._identify_improvement_areas(period_metrics, trend_analysis)
        
        # 6. 生成进化建议
        evolution_recommendations = await self._generate_evolution_recommendations(
            agent_id, metric_scores, trend_analysis
        )
        
        # 7. 同伴对比
        comparison_with_peers = await self._compare_with_peers(agent_id, metric_scores)
        
        # 创建评估报告
        report = EvolutionReport(
            agent_id=agent_id,
            evaluation_period=evaluation_period,
            overall_score=overall_score,
            metric_scores=metric_scores,
            trend_analysis=trend_analysis,
            key_improvements=key_improvements,
            areas_for_improvement=areas_for_improvement,
            evolution_recommendations=evolution_recommendations,
            comparison_with_peers=comparison_with_peers
        )
        
        self.logger.info(f"Agent {agent_id} 进化评估完成，总体得分: {overall_score:.3f}")
        
        return report
    
    async def _calculate_metric_scores(
        self,
        period_metrics: Dict[str, List[EvolutionMetric]]
    ) -> Dict[str, float]:
        """计算各指标得分"""
        
        metric_scores = {}
        
        for metric_name, metrics in period_metrics.items():
            if not metrics:
                continue
            
            metric_def = self.metric_definitions.get(metric_name, {})
            
            # 计算平均值
            values = [m.value for m in metrics]
            avg_value = statistics.mean(values)
            
            # 计算改进率
            improvement_rates = [m.improvement_rate for m in metrics if m.improvement_rate is not None]
            avg_improvement = statistics.mean(improvement_rates) if improvement_rates else 0
            
            # 计算趋势得分
            trend_score = self._calculate_trend_score(values)
            
            # 计算稳定性得分
            stability_score = self._calculate_stability_score(values)
            
            # 综合得分
            base_score = 0.5  # 基础分
            improvement_bonus = min(0.3, max(-0.3, avg_improvement))  # 改进奖励
            trend_bonus = trend_score * 0.1  # 趋势奖励
            stability_bonus = stability_score * 0.1  # 稳定性奖励
            
            final_score = base_score + improvement_bonus + trend_bonus + stability_bonus
            final_score = max(0, min(1, final_score))  # 限制在[0,1]范围内
            
            metric_scores[metric_name] = final_score
        
        return metric_scores
    
    def _calculate_overall_score(self, metric_scores: Dict[str, float]) -> float:
        """计算总体得分"""
        
        if not metric_scores:
            return 0.0
        
        weighted_sum = 0
        total_weight = 0
        
        for metric_name, score in metric_scores.items():
            weight = self.metric_definitions.get(metric_name, {}).get("weight", 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _analyze_trends(
        self,
        agent_id: str,
        period_metrics: Dict[str, List[EvolutionMetric]]
    ) -> Dict[str, MetricTrend]:
        """分析指标趋势"""
        
        trend_analysis = {}
        
        for metric_name, metrics in period_metrics.items():
            if len(metrics) < self.evaluation_config["min_data_points"]:
                trend_analysis[metric_name] = MetricTrend.STABLE
                continue
            
            # 提取时间序列数据
            values = [m.value for m in sorted(metrics, key=lambda x: x.timestamp)]
            
            # 计算趋势
            trend = self._calculate_trend(values)
            
            # 计算波动性
            volatility = self._calculate_volatility(values)
            
            # 确定趋势类型
            if volatility > self.evaluation_config["volatility_threshold"]:
                trend_analysis[metric_name] = MetricTrend.VOLATILE
            elif trend > self.evaluation_config["improvement_threshold"]:
                trend_analysis[metric_name] = MetricTrend.IMPROVING
            elif trend < -self.evaluation_config["improvement_threshold"]:
                trend_analysis[metric_name] = MetricTrend.DECLINING
            else:
                trend_analysis[metric_name] = MetricTrend.STABLE
        
        return trend_analysis
    
    def _identify_key_improvements(
        self,
        period_metrics: Dict[str, List[EvolutionMetric]]
    ) -> List[str]:
        """识别关键改进"""
        
        improvements = []
        
        for metric_name, metrics in period_metrics.items():
            if not metrics:
                continue
            
            # 计算平均改进率
            improvement_rates = [
                m.improvement_rate for m in metrics 
                if m.improvement_rate is not None
            ]
            
            if improvement_rates:
                avg_improvement = statistics.mean(improvement_rates)
                
                if avg_improvement > 0.1:  # 改进超过10%
                    improvement_desc = f"{metric_name}提升了{avg_improvement:.1%}"
                    improvements.append(improvement_desc)
        
        return improvements
    
    def _identify_improvement_areas(
        self,
        period_metrics: Dict[str, List[EvolutionMetric]],
        trend_analysis: Dict[str, MetricTrend]
    ) -> List[str]:
        """识别待改进领域"""
        
        areas = []
        
        for metric_name, trend in trend_analysis.items():
            if trend == MetricTrend.DECLINING:
                areas.append(f"{metric_name}呈下降趋势，需要关注")
            elif trend == MetricTrend.VOLATILE:
                areas.append(f"{metric_name}波动较大，需要稳定性改进")
        
        # 识别低分指标
        for metric_name, metrics in period_metrics.items():
            if metrics:
                avg_value = statistics.mean([m.value for m in metrics])
                # 这里需要根据具体指标的期望值范围来判断
                # 简化处理，假设期望值都在0.7以上
                if avg_value < 0.5:
                    areas.append(f"{metric_name}平均得分较低，需要重点改进")
        
        return areas
    
    async def _generate_evolution_recommendations(
        self,
        agent_id: str,
        metric_scores: Dict[str, float],
        trend_analysis: Dict[str, MetricTrend]
    ) -> List[str]:
        """生成进化建议"""
        
        recommendations = []
        
        # 基于趋势分析的建议
        declining_metrics = [
            name for name, trend in trend_analysis.items()
            if trend == MetricTrend.DECLINING
        ]
        
        if declining_metrics:
            recommendations.append(
                f"重点关注以下下降指标的改进: {', '.join(declining_metrics)}"
            )
        
        # 基于分数的建议
        low_score_metrics = [
            name for name, score in metric_scores.items()
            if score < 0.6
        ]
        
        if low_score_metrics:
            recommendations.append(
                f"优先改进低分指标: {', '.join(low_score_metrics)}"
            )
        
        # 基于指标类别的建议
        category_scores = defaultdict(list)
        for metric_name, score in metric_scores.items():
            category = self.metric_definitions.get(metric_name, {}).get("category")
            if category:
                category_scores[category].append(score)
        
        for category, scores in category_scores.items():
            avg_score = statistics.mean(scores)
            if avg_score < 0.6:
                recommendations.append(
                    f"加强{category.value}能力的整体提升"
                )
        
        # 个性化建议
        agent_specific_recommendations = await self._generate_agent_specific_recommendations(
            agent_id, metric_scores, trend_analysis
        )
        recommendations.extend(agent_specific_recommendations)
        
        return recommendations
    
    async def _compare_with_peers(
        self,
        agent_id: str,
        metric_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """与同伴Agent对比"""
        
        comparison = {}
        
        # 获取所有Agent的最近指标数据
        peer_scores = await self._get_peer_metric_scores(agent_id)
        
        for metric_name, agent_score in metric_scores.items():
            peer_values = peer_scores.get(metric_name, [])
            
            if peer_values:
                peer_avg = statistics.mean(peer_values)
                comparison[metric_name] = agent_score - peer_avg
            else:
                comparison[metric_name] = 0.0
        
        return comparison
    
    async def generate_team_evolution_summary(self) -> Dict[str, Any]:
        """生成团队进化总结"""
        
        all_agents = set()
        for metric_key in self.metric_history.keys():
            agent_id = metric_key.split('_')[0]
            all_agents.add(agent_id)
        
        team_summary = {
            "total_agents": len(all_agents),
            "evaluation_timestamp": datetime.utcnow().isoformat(),
            "agent_summaries": {},
            "team_averages": {},
            "top_performers": {},
            "improvement_opportunities": []
        }
        
        # 评估每个Agent
        agent_reports = {}
        for agent_id in all_agents:
            report = await self.evaluate_agent_evolution(agent_id)
            agent_reports[agent_id] = report
            team_summary["agent_summaries"][agent_id] = {
                "overall_score": report.overall_score,
                "key_improvements": report.key_improvements,
                "areas_for_improvement": report.areas_for_improvement
            }
        
        # 计算团队平均值
        if agent_reports:
            overall_scores = [r.overall_score for r in agent_reports.values()]
            team_summary["team_averages"]["overall_score"] = statistics.mean(overall_scores)
            
            # 各指标的团队平均
            all_metric_names = set()
            for report in agent_reports.values():
                all_metric_names.update(report.metric_scores.keys())
            
            for metric_name in all_metric_names:
                metric_scores = [
                    report.metric_scores.get(metric_name, 0)
                    for report in agent_reports.values()
                    if metric_name in report.metric_scores
                ]
                if metric_scores:
                    team_summary["team_averages"][metric_name] = statistics.mean(metric_scores)
        
        # 识别顶尖表现者
        for metric_name in team_summary["team_averages"].keys():
            if metric_name == "overall_score":
                continue
            
            best_agent = max(
                agent_reports.items(),
                key=lambda x: x[1].metric_scores.get(metric_name, 0)
            )
            team_summary["top_performers"][metric_name] = {
                "agent_id": best_agent[0],
                "score": best_agent[1].metric_scores.get(metric_name, 0)
            }
        
        return team_summary
    
    # Helper方法
    def _get_baseline_value(self, agent_id: str, metric_name: str) -> Optional[float]:
        """获取基线值"""
        return self.baselines.get(agent_id, {}).get(metric_name)
    
    def _calculate_metric_confidence(self, agent_id: str, metric_name: str, value: float) -> float:
        """计算指标置信度"""
        metric_key = f"{agent_id}_{metric_name}"
        history = self.metric_history.get(metric_key, [])
        
        if len(history) < 3:
            return 0.5  # 数据不足，中等置信度
        
        # 基于历史数据的变异性计算置信度
        recent_values = [m.value for m in history[-10:]]  # 最近10个值
        
        if len(recent_values) > 1:
            std_dev = statistics.stdev(recent_values)
            mean_val = statistics.mean(recent_values)
            
            # 变异系数越小，置信度越高
            if mean_val != 0:
                cv = std_dev / abs(mean_val)
                confidence = max(0.1, min(0.95, 1 - cv))
            else:
                confidence = 0.5
        else:
            confidence = 0.5
        
        return confidence
    
    def _calculate_trend_score(self, values: List[float]) -> float:
        """计算趋势得分 (-1到1，正值表示上升趋势)"""
        if len(values) < 2:
            return 0.0
        
        # 简单线性回归计算趋势
        n = len(values)
        x = list(range(n))
        
        # 计算斜率
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # 归一化到[-1, 1]范围
        max_slope = max(abs(slope), 1e-6)
        normalized_slope = slope / max_slope
        
        return max(-1, min(1, normalized_slope))
    
    def _calculate_stability_score(self, values: List[float]) -> float:
        """计算稳定性得分 (0到1，1表示最稳定)"""
        if len(values) < 2:
            return 1.0
        
        # 使用变异系数衡量稳定性
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.5
        
        std_dev = statistics.stdev(values)
        cv = std_dev / abs(mean_val)
        
        # 变异系数越小，稳定性越高
        stability = max(0, min(1, 1 - cv))
        
        return stability
    
    def _calculate_trend(self, values: List[float]) -> float:
        """计算数值序列的趋势"""
        return self._calculate_trend_score(values)
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """计算波动性"""
        if len(values) < 2:
            return 0.0
        
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.0
        
        std_dev = statistics.stdev(values)
        return std_dev / abs(mean_val)
    
    async def _update_baseline(self, agent_id: str, metric_name: str):
        """更新基线值"""
        metric_key = f"{agent_id}_{metric_name}"
        history = self.metric_history.get(metric_key, [])
        
        baseline_periods = self.metric_definitions.get(metric_name, {}).get("baseline_periods", 5)
        
        if len(history) >= baseline_periods:
            # 使用最早的几个数据点作为基线
            baseline_values = [m.value for m in history[:baseline_periods]]
            baseline = statistics.mean(baseline_values)
            
            if agent_id not in self.baselines:
                self.baselines[agent_id] = {}
            
            self.baselines[agent_id][metric_name] = baseline
    
    def _get_metrics_in_period(
        self,
        agent_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, List[EvolutionMetric]]:
        """获取指定时间段内的指标数据"""
        
        period_metrics = defaultdict(list)
        
        for metric_key, metrics in self.metric_history.items():
            if not metric_key.startswith(f"{agent_id}_"):
                continue
            
            metric_name = metric_key[len(agent_id)+1:]
            
            for metric in metrics:
                if start_time <= metric.timestamp <= end_time:
                    period_metrics[metric_name].append(metric)
        
        return dict(period_metrics)
    
    def _create_empty_report(self, agent_id: str, evaluation_period: Tuple[datetime, datetime]) -> EvolutionReport:
        """创建空的评估报告"""
        return EvolutionReport(
            agent_id=agent_id,
            evaluation_period=evaluation_period,
            overall_score=0.0,
            metric_scores={},
            trend_analysis={},
            key_improvements=[],
            areas_for_improvement=["缺乏足够的历史数据进行评估"],
            evolution_recommendations=["增加数据收集，建立性能基线"],
            comparison_with_peers={}
        )
    
    async def _get_peer_metric_scores(self, agent_id: str) -> Dict[str, List[float]]:
        """获取同伴Agent的指标得分"""
        # 实现获取其他Agent最近的指标数据
        # 这里简化处理，返回空字典
        return {}
    
    async def _generate_agent_specific_recommendations(
        self,
        agent_id: str,
        metric_scores: Dict[str, float],
        trend_analysis: Dict[str, MetricTrend]
    ) -> List[str]:
        """生成Agent特定的建议"""
        # 基于Agent类型和历史表现生成个性化建议
        recommendations = []
        
        # 这里可以根据agent_id的类型（如developer、qa等）给出特定建议
        if "developer" in agent_id.lower():
            if "code_quality" in metric_scores and metric_scores["code_quality"] < 0.7:
                recommendations.append("建议加强代码质量意识，多进行代码审查")
        
        return recommendations