"""知识进化系统 - Agent团队的集体智慧积累与传承"""

import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import hashlib

from src.utils import get_logger
from src.core.memory.rag_retriever import RAGRetriever
from src.core.memory.bge_embedding import create_embedding_service

logger = get_logger(__name__)


class KnowledgeType(str, Enum):
    """知识类型"""
    PATTERN = "pattern"                    # 模式知识
    PROCEDURE = "procedure"                # 程序性知识
    FACTUAL = "factual"                   # 事实性知识
    HEURISTIC = "heuristic"               # 启发式知识
    CONTEXTUAL = "contextual"             # 上下文知识
    COLLABORATIVE = "collaborative"        # 协作知识
    DOMAIN_SPECIFIC = "domain_specific"    # 领域特定知识


class KnowledgeSource(str, Enum):
    """知识来源"""
    PROJECT_EXPERIENCE = "project_experience"
    AGENT_INTERACTION = "agent_interaction"
    ERROR_CORRECTION = "error_correction"
    SUCCESS_REPLICATION = "success_replication"
    EXTERNAL_INPUT = "external_input"
    PEER_LEARNING = "peer_learning"


@dataclass
class KnowledgeItem:
    """知识条目"""
    id: str
    knowledge_type: KnowledgeType
    source: KnowledgeSource
    title: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    confidence: float
    applicability_score: float
    usage_count: int
    success_rate: float
    created_at: datetime
    last_used: datetime
    creator_agent: str
    applicable_scenarios: List[str]
    prerequisites: List[str]
    expected_outcomes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "knowledge_type": self.knowledge_type.value,
            "source": self.source.value,
            "title": self.title,
            "content": self.content,
            "context": self.context,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "applicability_score": self.applicability_score,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "creator_agent": self.creator_agent,
            "applicable_scenarios": self.applicable_scenarios,
            "prerequisites": self.prerequisites,
            "expected_outcomes": self.expected_outcomes
        }
    
    def get_knowledge_hash(self) -> str:
        """生成知识内容的哈希值用于去重"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()


@dataclass
class KnowledgeEvolutionEvent:
    """知识进化事件"""
    event_type: str  # creation, update, merge, obsolete
    knowledge_id: str
    agent_id: str
    timestamp: datetime
    details: Dict[str, Any]
    impact_score: float


class KnowledgeEvolutionEngine:
    """
    知识进化引擎 - 管理Agent团队的集体智慧
    
    核心功能：
    1. 知识自动提取和结构化
    2. 知识质量评估和筛选
    3. 知识融合和去重
    4. 知识传承和应用
    5. 知识进化跟踪
    """
    
    def __init__(self):
        self.logger = get_logger(f"{self.__class__.__name__}")
        self.rag_retriever = RAGRetriever()
        self.embedding_service = create_embedding_service()
        
        # 知识库
        self.knowledge_base: Dict[str, KnowledgeItem] = {}
        self.knowledge_graph: Dict[str, Set[str]] = defaultdict(set)  # 知识关联图
        self.evolution_history: List[KnowledgeEvolutionEvent] = []
        
        # 知识质量配置
        self.quality_thresholds = {
            "min_confidence": 0.6,
            "min_evidence_count": 2,
            "min_success_rate": 0.5,
            "obsolete_threshold": 0.3
        }
        
        # 知识融合配置
        self.fusion_config = {
            "similarity_threshold": 0.85,      # 相似知识合并阈值
            "conflict_resolution": "weighted_average",  # 冲突解决策略
            "max_merge_candidates": 5
        }
    
    async def initialize(self):
        """初始化知识进化引擎"""
        await self.rag_retriever.initialize()
        await self.embedding_service.initialize()
        await self._load_existing_knowledge()
        self.logger.info("知识进化引擎初始化完成")
    
    async def extract_knowledge_from_experience(
        self,
        experience_data: Dict[str, Any],
        agent_id: str,
        context: Dict[str, Any] = None
    ) -> List[KnowledgeItem]:
        """从经验中提取知识"""
        
        extracted_knowledge = []
        
        # 1. 模式知识提取
        patterns = await self._extract_patterns(experience_data, agent_id, context)
        extracted_knowledge.extend(patterns)
        
        # 2. 程序性知识提取
        procedures = await self._extract_procedures(experience_data, agent_id, context)
        extracted_knowledge.extend(procedures)
        
        # 3. 启发式知识提取
        heuristics = await self._extract_heuristics(experience_data, agent_id, context)
        extracted_knowledge.extend(heuristics)
        
        # 4. 协作知识提取
        collaborative_knowledge = await self._extract_collaborative_knowledge(
            experience_data, agent_id, context
        )
        extracted_knowledge.extend(collaborative_knowledge)
        
        # 5. 质量过滤
        high_quality_knowledge = await self._filter_knowledge_quality(extracted_knowledge)
        
        # 6. 存储和索引
        for knowledge in high_quality_knowledge:
            await self._store_knowledge(knowledge)
        
        self.logger.info(f"从经验中提取了 {len(high_quality_knowledge)} 个高质量知识项")
        
        return high_quality_knowledge
    
    async def _extract_patterns(
        self,
        experience_data: Dict[str, Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[KnowledgeItem]:
        """提取模式知识"""
        
        patterns = []
        
        # 分析成功模式
        if "successful_actions" in experience_data:
            for action_sequence in experience_data["successful_actions"]:
                pattern = await self._create_pattern_knowledge(
                    action_sequence, "success_pattern", agent_id, context
                )
                if pattern:
                    patterns.append(pattern)
        
        # 分析失败模式
        if "failed_actions" in experience_data:
            for action_sequence in experience_data["failed_actions"]:
                pattern = await self._create_pattern_knowledge(
                    action_sequence, "failure_pattern", agent_id, context
                )
                if pattern:
                    patterns.append(pattern)
        
        # 分析协作模式
        if "collaboration_patterns" in experience_data:
            for collab_pattern in experience_data["collaboration_patterns"]:
                pattern = await self._create_collaboration_pattern(
                    collab_pattern, agent_id, context
                )
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    async def _create_pattern_knowledge(
        self,
        action_sequence: Dict[str, Any],
        pattern_type: str,
        agent_id: str,
        context: Dict[str, Any]
    ) -> Optional[KnowledgeItem]:
        """创建模式知识项"""
        
        if not action_sequence or not action_sequence.get("actions"):
            return None
        
        # 提取模式特征
        pattern_features = {
            "action_sequence": action_sequence["actions"],
            "context_conditions": action_sequence.get("context", {}),
            "outcome": action_sequence.get("outcome", {}),
            "pattern_type": pattern_type
        }
        
        # 计算置信度
        confidence = self._calculate_pattern_confidence(action_sequence)
        
        # 确定适用场景
        applicable_scenarios = self._determine_applicable_scenarios(
            pattern_features, context
        )
        
        knowledge_item = KnowledgeItem(
            id=self._generate_knowledge_id("pattern", agent_id),
            knowledge_type=KnowledgeType.PATTERN,
            source=KnowledgeSource.PROJECT_EXPERIENCE,
            title=f"{pattern_type.replace('_', ' ').title()} - {agent_id}",
            content=pattern_features,
            context=context or {},
            evidence=[{
                "type": "action_sequence",
                "data": action_sequence,
                "timestamp": datetime.utcnow().isoformat()
            }],
            confidence=confidence,
            applicability_score=0.8,  # 初始适用性分数
            usage_count=0,
            success_rate=1.0 if pattern_type == "success_pattern" else 0.0,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow(),
            creator_agent=agent_id,
            applicable_scenarios=applicable_scenarios,
            prerequisites=self._extract_prerequisites(action_sequence),
            expected_outcomes=self._extract_expected_outcomes(action_sequence)
        )
        
        return knowledge_item
    
    async def _extract_procedures(
        self,
        experience_data: Dict[str, Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[KnowledgeItem]:
        """提取程序性知识（如何做的知识）"""
        
        procedures = []
        
        # 从任务执行序列中提取程序
        if "task_executions" in experience_data:
            for task_exec in experience_data["task_executions"]:
                if task_exec.get("success", False):
                    procedure = await self._create_procedure_knowledge(
                        task_exec, agent_id, context
                    )
                    if procedure:
                        procedures.append(procedure)
        
        # 从问题解决过程中提取程序
        if "problem_solving_steps" in experience_data:
            for problem_solution in experience_data["problem_solving_steps"]:
                procedure = await self._create_problem_solving_procedure(
                    problem_solution, agent_id, context
                )
                if procedure:
                    procedures.append(procedure)
        
        return procedures
    
    async def _extract_heuristics(
        self,
        experience_data: Dict[str, Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[KnowledgeItem]:
        """提取启发式知识（经验法则）"""
        
        heuristics = []
        
        # 从决策过程中提取启发式规则
        if "decision_processes" in experience_data:
            for decision in experience_data["decision_processes"]:
                heuristic = await self._create_heuristic_knowledge(
                    decision, agent_id, context
                )
                if heuristic:
                    heuristics.append(heuristic)
        
        # 从优化经验中提取启发式
        if "optimization_insights" in experience_data:
            for insight in experience_data["optimization_insights"]:
                heuristic = await self._create_optimization_heuristic(
                    insight, agent_id, context
                )
                if heuristic:
                    heuristics.append(heuristic)
        
        return heuristics
    
    async def knowledge_fusion(self, knowledge_items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        """知识融合 - 合并相似知识，解决冲突"""
        
        if len(knowledge_items) < 2:
            return knowledge_items
        
        # 1. 计算知识相似度矩阵
        similarity_matrix = await self._calculate_knowledge_similarity_matrix(knowledge_items)
        
        # 2. 识别需要融合的知识对
        fusion_candidates = []
        for i in range(len(knowledge_items)):
            for j in range(i + 1, len(knowledge_items)):
                similarity = similarity_matrix[i][j]
                if similarity >= self.fusion_config["similarity_threshold"]:
                    fusion_candidates.append((i, j, similarity))
        
        # 3. 按相似度排序
        fusion_candidates.sort(key=lambda x: x[2], reverse=True)
        
        # 4. 执行知识融合
        fused_knowledge = []
        processed_indices = set()
        
        for i, j, similarity in fusion_candidates:
            if i in processed_indices or j in processed_indices:
                continue
            
            # 融合两个知识项
            fused_item = await self._fuse_knowledge_pair(
                knowledge_items[i], knowledge_items[j], similarity
            )
            
            if fused_item:
                fused_knowledge.append(fused_item)
                processed_indices.add(i)
                processed_indices.add(j)
        
        # 5. 添加未融合的知识项
        for i, item in enumerate(knowledge_items):
            if i not in processed_indices:
                fused_knowledge.append(item)
        
        self.logger.info(f"知识融合完成: {len(knowledge_items)} -> {len(fused_knowledge)}")
        
        return fused_knowledge
    
    async def _fuse_knowledge_pair(
        self,
        knowledge1: KnowledgeItem,
        knowledge2: KnowledgeItem,
        similarity: float
    ) -> Optional[KnowledgeItem]:
        """融合一对相似的知识项"""
        
        # 确保是同类型知识才能融合
        if knowledge1.knowledge_type != knowledge2.knowledge_type:
            return None
        
        # 选择更高质量的知识作为基础
        base_knowledge = knowledge1 if knowledge1.confidence >= knowledge2.confidence else knowledge2
        merge_knowledge = knowledge2 if base_knowledge == knowledge1 else knowledge1
        
        # 创建融合后的知识项
        fused_item = KnowledgeItem(
            id=self._generate_knowledge_id("fused", base_knowledge.creator_agent),
            knowledge_type=base_knowledge.knowledge_type,
            source=base_knowledge.source,
            title=f"融合知识: {base_knowledge.title}",
            content=self._merge_knowledge_content(base_knowledge.content, merge_knowledge.content),
            context=self._merge_contexts(base_knowledge.context, merge_knowledge.context),
            evidence=base_knowledge.evidence + merge_knowledge.evidence,
            confidence=self._calculate_fused_confidence(knowledge1, knowledge2, similarity),
            applicability_score=max(base_knowledge.applicability_score, merge_knowledge.applicability_score),
            usage_count=base_knowledge.usage_count + merge_knowledge.usage_count,
            success_rate=self._calculate_weighted_success_rate(knowledge1, knowledge2),
            created_at=min(base_knowledge.created_at, merge_knowledge.created_at),
            last_used=max(base_knowledge.last_used, merge_knowledge.last_used),
            creator_agent=f"{base_knowledge.creator_agent}+{merge_knowledge.creator_agent}",
            applicable_scenarios=self._merge_scenarios(
                base_knowledge.applicable_scenarios,
                merge_knowledge.applicable_scenarios
            ),
            prerequisites=self._merge_prerequisites(
                base_knowledge.prerequisites,
                merge_knowledge.prerequisites
            ),
            expected_outcomes=self._merge_outcomes(
                base_knowledge.expected_outcomes,
                merge_knowledge.expected_outcomes
            )
        )
        
        # 记录融合事件
        self._record_evolution_event(
            "knowledge_fusion",
            fused_item.id,
            base_knowledge.creator_agent,
            {
                "merged_knowledge_ids": [knowledge1.id, knowledge2.id],
                "similarity_score": similarity,
                "fusion_strategy": self.fusion_config["conflict_resolution"]
            }
        )
        
        return fused_item
    
    async def recommend_knowledge_for_task(
        self,
        task_context: Dict[str, Any],
        agent_id: str,
        limit: int = 5
    ) -> List[Tuple[KnowledgeItem, float]]:
        """为特定任务推荐相关知识"""
        
        # 1. 基于任务上下文生成查询向量
        task_description = self._extract_task_description(task_context)
        
        # 2. 使用RAG检索相关知识
        similar_items = await self.rag_retriever.retrieve_similar(
            query=task_description,
            project_id="knowledge_base",
            content_types=["knowledge_item"],
            limit=limit * 2  # 获取更多候选项
        )
        
        # 3. 根据适用性和质量重新排序
        recommendations = []
        for item in similar_items:
            knowledge_id = item.metadata.get("knowledge_id")
            if knowledge_id in self.knowledge_base:
                knowledge = self.knowledge_base[knowledge_id]
                
                # 计算推荐分数
                relevance_score = item.similarity_score
                quality_score = self._calculate_knowledge_quality_score(knowledge)
                applicability_score = self._calculate_task_applicability(knowledge, task_context)
                
                final_score = (
                    relevance_score * 0.4 +
                    quality_score * 0.3 +
                    applicability_score * 0.3
                )
                
                recommendations.append((knowledge, final_score))
        
        # 4. 按分数排序并返回top-k
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        self.logger.info(f"为任务推荐了 {len(recommendations[:limit])} 个知识项")
        
        return recommendations[:limit]
    
    async def apply_knowledge_to_task(
        self,
        knowledge_item: KnowledgeItem,
        task_context: Dict[str, Any],
        agent_id: str
    ) -> Dict[str, Any]:
        """将知识应用到具体任务中"""
        
        # 1. 更新知识使用统计
        knowledge_item.usage_count += 1
        knowledge_item.last_used = datetime.utcnow()
        
        # 2. 根据知识类型生成应用指导
        application_guidance = {}
        
        if knowledge_item.knowledge_type == KnowledgeType.PATTERN:
            application_guidance = await self._apply_pattern_knowledge(
                knowledge_item, task_context
            )
        elif knowledge_item.knowledge_type == KnowledgeType.PROCEDURE:
            application_guidance = await self._apply_procedure_knowledge(
                knowledge_item, task_context
            )
        elif knowledge_item.knowledge_type == KnowledgeType.HEURISTIC:
            application_guidance = await self._apply_heuristic_knowledge(
                knowledge_item, task_context
            )
        
        # 3. 记录应用事件
        self._record_evolution_event(
            "knowledge_application",
            knowledge_item.id,
            agent_id,
            {
                "task_context": task_context,
                "application_guidance": application_guidance
            }
        )
        
        return application_guidance
    
    async def update_knowledge_feedback(
        self,
        knowledge_id: str,
        application_result: Dict[str, Any],
        agent_id: str
    ):
        """根据应用结果更新知识质量"""
        
        if knowledge_id not in self.knowledge_base:
            return
        
        knowledge = self.knowledge_base[knowledge_id]
        
        # 根据应用结果更新成功率
        success = application_result.get("success", False)
        
        # 使用指数移动平均更新成功率
        alpha = 0.1  # 学习率
        new_success_rate = (1 - alpha) * knowledge.success_rate + alpha * (1.0 if success else 0.0)
        knowledge.success_rate = new_success_rate
        
        # 更新置信度
        if success:
            knowledge.confidence = min(0.95, knowledge.confidence + 0.05)
        else:
            knowledge.confidence = max(0.1, knowledge.confidence - 0.1)
        
        # 添加反馈证据
        knowledge.evidence.append({
            "type": "application_feedback",
            "result": application_result,
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # 记录反馈事件
        self._record_evolution_event(
            "knowledge_feedback",
            knowledge_id,
            agent_id,
            {
                "application_result": application_result,
                "new_success_rate": new_success_rate,
                "new_confidence": knowledge.confidence
            }
        )
        
        self.logger.debug(f"更新知识 {knowledge_id} 的反馈: 成功率 {new_success_rate:.3f}")
    
    async def evolve_knowledge_base(self) -> Dict[str, Any]:
        """定期进化知识库 - 清理过时知识，优化知识结构"""
        
        evolution_summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "before_count": len(self.knowledge_base),
            "actions": {
                "obsoleted": 0,
                "merged": 0,
                "enhanced": 0,
                "created": 0
            }
        }
        
        # 1. 识别过时知识
        obsolete_knowledge = []
        for knowledge in self.knowledge_base.values():
            if self._is_knowledge_obsolete(knowledge):
                obsolete_knowledge.append(knowledge.id)
        
        # 2. 移除过时知识
        for knowledge_id in obsolete_knowledge:
            del self.knowledge_base[knowledge_id]
            evolution_summary["actions"]["obsoleted"] += 1
        
        # 3. 知识融合优化
        all_knowledge = list(self.knowledge_base.values())
        fused_knowledge = await self.knowledge_fusion(all_knowledge)
        
        if len(fused_knowledge) < len(all_knowledge):
            # 更新知识库
            self.knowledge_base = {k.id: k for k in fused_knowledge}
            evolution_summary["actions"]["merged"] = len(all_knowledge) - len(fused_knowledge)
        
        # 4. 知识质量提升
        enhanced_count = await self._enhance_knowledge_quality()
        evolution_summary["actions"]["enhanced"] = enhanced_count
        
        evolution_summary["after_count"] = len(self.knowledge_base)
        
        self.logger.info(f"知识库进化完成: {evolution_summary}")
        
        return evolution_summary
    
    # Helper方法
    def _generate_knowledge_id(self, prefix: str, agent_id: str) -> str:
        """生成知识ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{agent_id}_{timestamp}"
    
    def _calculate_pattern_confidence(self, action_sequence: Dict[str, Any]) -> float:
        """计算模式置信度"""
        base_confidence = 0.6
        
        # 基于证据数量调整
        evidence_count = len(action_sequence.get("evidence", []))
        evidence_bonus = min(0.3, evidence_count * 0.1)
        
        # 基于成功率调整
        success_rate = action_sequence.get("success_rate", 0.5)
        success_bonus = (success_rate - 0.5) * 0.4
        
        return min(0.95, base_confidence + evidence_bonus + success_bonus)
    
    def _is_knowledge_obsolete(self, knowledge: KnowledgeItem) -> bool:
        """判断知识是否过时"""
        
        # 基于成功率判断
        if knowledge.success_rate < self.quality_thresholds["obsolete_threshold"]:
            return True
        
        # 基于使用频率判断
        days_since_last_use = (datetime.utcnow() - knowledge.last_used).days
        if days_since_last_use > 90 and knowledge.usage_count < 3:
            return True
        
        # 基于置信度判断
        if knowledge.confidence < self.quality_thresholds["min_confidence"]:
            return True
        
        return False
    
    def _record_evolution_event(
        self,
        event_type: str,
        knowledge_id: str,
        agent_id: str,
        details: Dict[str, Any]
    ):
        """记录知识进化事件"""
        event = KnowledgeEvolutionEvent(
            event_type=event_type,
            knowledge_id=knowledge_id,
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
            details=details,
            impact_score=self._calculate_impact_score(event_type, details)
        )
        
        self.evolution_history.append(event)
        
        # 限制历史记录数量
        if len(self.evolution_history) > 10000:
            self.evolution_history = self.evolution_history[-8000:]
    
    async def get_evolution_statistics(self) -> Dict[str, Any]:
        """获取知识进化统计信息"""
        
        return {
            "total_knowledge_items": len(self.knowledge_base),
            "knowledge_by_type": self._count_knowledge_by_type(),
            "knowledge_by_source": self._count_knowledge_by_source(),
            "average_confidence": self._calculate_average_confidence(),
            "average_success_rate": self._calculate_average_success_rate(),
            "total_evolution_events": len(self.evolution_history),
            "recent_activity": self._get_recent_activity_summary()
        }
    
    # 其他helper方法的占位符实现
    async def _calculate_knowledge_similarity_matrix(self, knowledge_items: List[KnowledgeItem]) -> List[List[float]]:
        """计算知识相似度矩阵"""
        # 实现知识相似度计算
        n = len(knowledge_items)
        return [[0.0 for _ in range(n)] for _ in range(n)]
    
    # ... 其他方法的实现