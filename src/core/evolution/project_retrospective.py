"""项目复盘系统 - 自动提取经验和学习模式"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re

from src.utils import get_logger
from src.core.memory.rag_retriever import RAGRetriever
from src.core.database.session import get_session
from src.core.database.models import Project, Sprint

logger = get_logger(__name__)


class LessonType(str, Enum):
    """经验教训类型"""
    SUCCESS_PATTERN = "success_pattern"      # 成功模式
    FAILURE_PATTERN = "failure_pattern"      # 失败模式
    OPTIMIZATION = "optimization"            # 优化机会
    BEST_PRACTICE = "best_practice"          # 最佳实践
    ANTI_PATTERN = "anti_pattern"           # 反模式
    KNOWLEDGE_GAP = "knowledge_gap"         # 知识缺口


@dataclass
class ProjectLesson:
    """项目经验教训"""
    lesson_type: LessonType
    title: str
    description: str
    context: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    confidence: float
    applicability: List[str]  # 适用场景
    actionable_steps: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "lesson_type": self.lesson_type.value,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "applicability": self.applicability,
            "actionable_steps": self.actionable_steps,
            "extracted_at": datetime.utcnow().isoformat()
        }


class ProjectRetrospectiveEngine:
    """
    项目复盘引擎 - 自动分析项目数据并提取可复用的经验
    
    核心功能：
    1. 多维度项目分析
    2. 成功/失败模式识别
    3. 可行动的改进建议
    4. 跨项目经验对比
    5. 知识库自动更新
    """
    
    def __init__(self):
        self.logger = get_logger(f"{self.__class__.__name__}")
        self.rag_retriever = RAGRetriever()
        
        # 分析维度配置
        self.analysis_dimensions = {
            "timeline_adherence": {"weight": 0.2, "critical": True},
            "quality_metrics": {"weight": 0.25, "critical": True},
            "team_collaboration": {"weight": 0.15, "critical": False},
            "technical_decisions": {"weight": 0.2, "critical": True},
            "risk_management": {"weight": 0.1, "critical": False},
            "stakeholder_satisfaction": {"weight": 0.1, "critical": False}
        }
        
        # 模式识别阈值
        self.pattern_thresholds = {
            "success_pattern": 0.8,     # 成功模式识别阈值
            "failure_pattern": 0.3,     # 失败模式识别阈值
            "optimization": 0.6,        # 优化机会识别阈值
            "confidence_minimum": 0.7   # 最低置信度
        }
    
    async def conduct_full_retrospective(
        self,
        project_id: str,
        include_historical_comparison: bool = True
    ) -> Dict[str, Any]:
        """全面项目复盘分析"""
        
        self.logger.info(f"开始项目 {project_id} 的全面复盘分析...")
        
        try:
            # 1. 收集项目数据
            project_data = await self._collect_project_data(project_id)
            
            # 2. 多维度性能分析
            performance_analysis = await self._analyze_project_performance(project_data)
            
            # 3. 识别经验教训
            lessons_learned = await self._extract_lessons_learned(project_data, performance_analysis)
            
            # 4. 历史项目对比
            historical_comparison = None
            if include_historical_comparison:
                historical_comparison = await self._compare_with_historical_projects(
                    project_data, lessons_learned
                )
            
            # 5. 生成改进建议
            improvement_recommendations = await self._generate_improvement_recommendations(
                lessons_learned, historical_comparison
            )
            
            # 6. 构建复盘报告
            retrospective_report = {
                "project_id": project_id,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "project_summary": self._create_project_summary(project_data),
                "performance_analysis": performance_analysis,
                "lessons_learned": [lesson.to_dict() for lesson in lessons_learned],
                "historical_comparison": historical_comparison,
                "improvement_recommendations": improvement_recommendations,
                "overall_score": self._calculate_overall_score(performance_analysis),
                "key_insights": self._extract_key_insights(lessons_learned)
            }
            
            # 7. 存储复盘结果
            await self._store_retrospective_report(retrospective_report)
            
            # 8. 更新知识库
            await self._update_knowledge_base(lessons_learned)
            
            self.logger.info(f"项目 {project_id} 复盘分析完成")
            return retrospective_report
            
        except Exception as e:
            self.logger.error(f"项目复盘分析失败: {str(e)}")
            raise
    
    async def _collect_project_data(self, project_id: str) -> Dict[str, Any]:
        """收集项目相关数据"""
        
        # 从数据库获取项目基本信息
        async with get_session() as session:
            project = await session.get(Project, project_id)
            if not project:
                raise ValueError(f"项目 {project_id} 不存在")
            
            # 获取所有Sprint数据
            sprints = await session.query(Sprint).filter(
                Sprint.project_id == project_id
            ).all()
        
        # 整合项目数据
        project_data = {
            "project_info": {
                "id": project.id,
                "name": project.name,
                "type": project.project_type,
                "start_date": project.created_at.isoformat(),
                "status": project.status,
                "tech_stack": project.tech_stack or {}
            },
            "sprints": [],
            "timeline": {
                "planned_duration": None,  # 需要从项目计划获取
                "actual_duration": None,
                "milestone_adherence": []
            },
            "team_composition": [],
            "metrics": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "bugs_found": 0,
                "bugs_fixed": 0,
                "code_coverage": 0.0,
                "performance_metrics": []
            }
        }
        
        # 处理Sprint数据
        for sprint in sprints:
            sprint_data = {
                "id": sprint.id,
                "goal": sprint.goal,
                "start_date": sprint.start_date.isoformat(),
                "end_date": sprint.end_date.isoformat() if sprint.end_date else None,
                "status": sprint.status,
                "artifacts": sprint.artifacts or {},
                "metrics": sprint.metrics or {}
            }
            project_data["sprints"].append(sprint_data)
            
            # 累计指标
            sprint_metrics = sprint.metrics or {}
            project_data["metrics"]["total_tasks"] += sprint_metrics.get("total_tasks", 0)
            project_data["metrics"]["completed_tasks"] += sprint_metrics.get("completed_tasks", 0)
        
        return project_data
    
    async def _analyze_project_performance(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """多维度项目性能分析"""
        
        analysis_results = {}
        
        # 1. 时间线遵守分析
        timeline_analysis = await self._analyze_timeline_adherence(project_data)
        analysis_results["timeline_adherence"] = timeline_analysis
        
        # 2. 质量指标分析
        quality_analysis = await self._analyze_quality_metrics(project_data)
        analysis_results["quality_metrics"] = quality_analysis
        
        # 3. 团队协作分析
        collaboration_analysis = await self._analyze_team_collaboration(project_data)
        analysis_results["team_collaboration"] = collaboration_analysis
        
        # 4. 技术决策分析
        technical_analysis = await self._analyze_technical_decisions(project_data)
        analysis_results["technical_decisions"] = technical_analysis
        
        # 5. 风险管理分析
        risk_analysis = await self._analyze_risk_management(project_data)
        analysis_results["risk_management"] = risk_analysis
        
        # 6. 利益相关者满意度分析
        stakeholder_analysis = await self._analyze_stakeholder_satisfaction(project_data)
        analysis_results["stakeholder_satisfaction"] = stakeholder_analysis
        
        return analysis_results
    
    async def _extract_lessons_learned(
        self,
        project_data: Dict[str, Any],
        performance_analysis: Dict[str, Any]
    ) -> List[ProjectLesson]:
        """从项目数据中提取经验教训"""
        
        lessons = []
        
        # 1. 识别成功模式
        success_patterns = await self._identify_success_patterns(project_data, performance_analysis)
        lessons.extend(success_patterns)
        
        # 2. 识别失败模式
        failure_patterns = await self._identify_failure_patterns(project_data, performance_analysis)
        lessons.extend(failure_patterns)
        
        # 3. 识别优化机会
        optimizations = await self._identify_optimization_opportunities(project_data, performance_analysis)
        lessons.extend(optimizations)
        
        # 4. 提取最佳实践
        best_practices = await self._extract_best_practices(project_data, performance_analysis)
        lessons.extend(best_practices)
        
        # 5. 识别反模式
        anti_patterns = await self._identify_anti_patterns(project_data, performance_analysis)
        lessons.extend(anti_patterns)
        
        # 6. 识别知识缺口
        knowledge_gaps = await self._identify_knowledge_gaps(project_data, performance_analysis)
        lessons.extend(knowledge_gaps)
        
        # 过滤低置信度的经验
        high_confidence_lessons = [
            lesson for lesson in lessons
            if lesson.confidence >= self.pattern_thresholds["confidence_minimum"]
        ]
        
        self.logger.info(f"提取到 {len(high_confidence_lessons)} 个高置信度经验教训")
        
        return high_confidence_lessons
    
    async def _identify_success_patterns(
        self,
        project_data: Dict[str, Any],
        performance_analysis: Dict[str, Any]
    ) -> List[ProjectLesson]:
        """识别成功模式"""
        
        success_patterns = []
        
        # 检查高性能维度
        for dimension, analysis in performance_analysis.items():
            if isinstance(analysis, dict) and analysis.get("score", 0) >= self.pattern_thresholds["success_pattern"]:
                
                # 提取成功因素
                success_factors = analysis.get("success_factors", [])
                if success_factors:
                    pattern = ProjectLesson(
                        lesson_type=LessonType.SUCCESS_PATTERN,
                        title=f"{dimension}维度的成功模式",
                        description=f"在{dimension}方面表现优秀，得分{analysis['score']:.2f}",
                        context={
                            "dimension": dimension,
                            "score": analysis["score"],
                            "project_type": project_data["project_info"]["type"]
                        },
                        evidence=[{
                            "type": "performance_score",
                            "score": analysis["score"],
                            "factors": success_factors
                        }],
                        confidence=min(0.95, analysis["score"]),
                        applicability=[
                            project_data["project_info"]["type"],
                            "similar_team_size",
                            "similar_tech_stack"
                        ],
                        actionable_steps=self._generate_success_replication_steps(success_factors)
                    )
                    success_patterns.append(pattern)
        
        return success_patterns
    
    async def _identify_failure_patterns(
        self,
        project_data: Dict[str, Any],
        performance_analysis: Dict[str, Any]
    ) -> List[ProjectLesson]:
        """识别失败模式"""
        
        failure_patterns = []
        
        # 检查低性能维度
        for dimension, analysis in performance_analysis.items():
            if isinstance(analysis, dict) and analysis.get("score", 1) <= self.pattern_thresholds["failure_pattern"]:
                
                # 提取失败因素
                failure_factors = analysis.get("failure_factors", [])
                if failure_factors:
                    pattern = ProjectLesson(
                        lesson_type=LessonType.FAILURE_PATTERN,
                        title=f"{dimension}维度的失败模式",
                        description=f"在{dimension}方面表现不佳，得分{analysis['score']:.2f}",
                        context={
                            "dimension": dimension,
                            "score": analysis["score"],
                            "project_type": project_data["project_info"]["type"]
                        },
                        evidence=[{
                            "type": "performance_score",
                            "score": analysis["score"],
                            "factors": failure_factors
                        }],
                        confidence=1.0 - analysis["score"],  # 分数越低，失败模式置信度越高
                        applicability=[
                            project_data["project_info"]["type"],
                            "risk_mitigation"
                        ],
                        actionable_steps=self._generate_failure_prevention_steps(failure_factors)
                    )
                    failure_patterns.append(pattern)
        
        return failure_patterns
    
    async def _compare_with_historical_projects(
        self,
        current_project: Dict[str, Any],
        current_lessons: List[ProjectLesson]
    ) -> Dict[str, Any]:
        """与历史项目对比分析"""
        
        # 查找相似的历史项目
        similar_projects = await self._find_similar_historical_projects(current_project)
        
        if not similar_projects:
            return {"message": "没有找到足够相似的历史项目进行对比"}
        
        comparison_results = {
            "similar_projects_count": len(similar_projects),
            "performance_comparison": {},
            "lesson_patterns": {},
            "improvement_potential": {},
            "benchmarking": {}
        }
        
        # 性能对比
        for project in similar_projects:
            project_id = project["project_id"]
            # 获取历史项目的性能数据
            historical_performance = project.get("performance_analysis", {})
            
            # 对比各维度性能
            for dimension in self.analysis_dimensions:
                if dimension not in comparison_results["performance_comparison"]:
                    comparison_results["performance_comparison"][dimension] = {
                        "current_score": 0,
                        "historical_average": 0,
                        "best_historical": 0,
                        "comparison": "unknown"
                    }
                
                current_score = current_project.get("performance_analysis", {}).get(dimension, {}).get("score", 0)
                historical_score = historical_performance.get(dimension, {}).get("score", 0)
                
                comparison_results["performance_comparison"][dimension]["current_score"] = current_score
                comparison_results["performance_comparison"][dimension]["historical_average"] += historical_score / len(similar_projects)
                comparison_results["performance_comparison"][dimension]["best_historical"] = max(
                    comparison_results["performance_comparison"][dimension]["best_historical"],
                    historical_score
                )
        
        # 设置对比结果
        for dimension, comparison in comparison_results["performance_comparison"].items():
            current = comparison["current_score"]
            average = comparison["historical_average"]
            
            if current > average * 1.1:
                comparison["comparison"] = "above_average"
            elif current < average * 0.9:
                comparison["comparison"] = "below_average"
            else:
                comparison["comparison"] = "average"
        
        return comparison_results
    
    async def _generate_improvement_recommendations(
        self,
        lessons_learned: List[ProjectLesson],
        historical_comparison: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成改进建议"""
        
        recommendations = []
        
        # 基于经验教训生成建议
        for lesson in lessons_learned:
            if lesson.lesson_type == LessonType.FAILURE_PATTERN:
                recommendations.append({
                    "type": "failure_prevention",
                    "priority": "high",
                    "title": f"避免{lesson.title}的重复",
                    "description": lesson.description,
                    "actionable_steps": lesson.actionable_steps,
                    "expected_impact": "避免类似失败"
                })
            
            elif lesson.lesson_type == LessonType.OPTIMIZATION:
                recommendations.append({
                    "type": "process_optimization",
                    "priority": "medium",
                    "title": f"优化{lesson.title}",
                    "description": lesson.description,
                    "actionable_steps": lesson.actionable_steps,
                    "expected_impact": "提升效率和质量"
                })
        
        # 基于历史对比生成建议
        if historical_comparison:
            for dimension, comparison in historical_comparison.get("performance_comparison", {}).items():
                if comparison["comparison"] == "below_average":
                    recommendations.append({
                        "type": "performance_improvement",
                        "priority": "high",
                        "title": f"提升{dimension}表现",
                        "description": f"当前{dimension}得分低于历史平均水平",
                        "actionable_steps": [
                            f"分析{dimension}表现不佳的根本原因",
                            f"参考历史最佳项目在{dimension}方面的做法",
                            f"制定针对性的{dimension}改进计划"
                        ],
                        "expected_impact": f"将{dimension}表现提升至平均水平以上"
                    })
        
        # 按优先级排序
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(
            key=lambda x: priority_order.get(x["priority"], 0),
            reverse=True
        )
        
        return recommendations
    
    # Helper方法实现
    def _create_project_summary(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目摘要"""
        return {
            "name": project_data["project_info"]["name"],
            "type": project_data["project_info"]["type"],
            "duration_days": len(project_data["sprints"]) * 14,  # 估算
            "total_sprints": len(project_data["sprints"]),
            "completion_rate": self._calculate_completion_rate(project_data)
        }
    
    def _calculate_overall_score(self, performance_analysis: Dict[str, Any]) -> float:
        """计算项目总体得分"""
        weighted_score = 0
        total_weight = 0
        
        for dimension, config in self.analysis_dimensions.items():
            if dimension in performance_analysis:
                score = performance_analysis[dimension].get("score", 0)
                weight = config["weight"]
                weighted_score += score * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0
    
    def _extract_key_insights(self, lessons_learned: List[ProjectLesson]) -> List[str]:
        """提取关键洞察"""
        insights = []
        
        # 按类型分组统计
        lesson_counts = {}
        for lesson in lessons_learned:
            lesson_type = lesson.lesson_type.value
            lesson_counts[lesson_type] = lesson_counts.get(lesson_type, 0) + 1
        
        # 生成洞察
        if lesson_counts.get("success_pattern", 0) > 3:
            insights.append("项目有多个成功模式可以复用")
        
        if lesson_counts.get("failure_pattern", 0) > 2:
            insights.append("需要重点关注失败模式的预防")
        
        if lesson_counts.get("optimization", 0) > 1:
            insights.append("存在明显的优化提升空间")
        
        return insights
    
    async def _store_retrospective_report(self, report: Dict[str, Any]):
        """存储复盘报告"""
        # 实现报告存储逻辑
        # 可以存储到数据库或文件系统
        pass
    
    async def _update_knowledge_base(self, lessons_learned: List[ProjectLesson]):
        """更新知识库"""
        # 将经验教训索引到RAG系统中
        for lesson in lessons_learned:
            await self.rag_retriever.index_memory(
                content=lesson.to_dict(),
                content_type="lesson_learned",
                project_id="knowledge_base"
            )
    
    # 其他分析方法的占位符实现
    async def _analyze_timeline_adherence(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """时间线遵守分析"""
        return {"score": 0.8, "analysis": "时间线分析"}
    
    async def _analyze_quality_metrics(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """质量指标分析"""
        return {"score": 0.7, "analysis": "质量分析"}
    
    async def _analyze_team_collaboration(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """团队协作分析"""
        return {"score": 0.75, "analysis": "协作分析"}
    
    async def _analyze_technical_decisions(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """技术决策分析"""
        return {"score": 0.85, "analysis": "技术决策分析"}
    
    async def _analyze_risk_management(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """风险管理分析"""
        return {"score": 0.6, "analysis": "风险管理分析"}
    
    async def _analyze_stakeholder_satisfaction(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """利益相关者满意度分析"""
        return {"score": 0.8, "analysis": "满意度分析"}