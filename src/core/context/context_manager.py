"""
Enhanced Context Manager inspired by context-rot research.

This module addresses context degradation issues identified in the chroma-core/context-rot project
by implementing adaptive context management strategies for AI agents.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import numpy as np

from src.utils import get_logger

logger = get_logger(__name__)


class ContextImportance(str, Enum):
    """Context importance levels for prioritization."""
    CRITICAL = "critical"      # Must retain (current task, active decisions)
    HIGH = "high"             # Important for coherence (recent interactions)
    MEDIUM = "medium"         # Useful background (project context)
    LOW = "low"              # Nice to have (historical data)
    MINIMAL = "minimal"       # Can be compressed heavily


class ContextType(str, Enum):
    """Types of context information."""
    TASK_CONTEXT = "task_context"           # Current task details
    CONVERSATION = "conversation"           # Agent conversations
    DECISION_HISTORY = "decision_history"   # Past decisions and rationale
    PROJECT_STATE = "project_state"         # Current project status
    KNOWLEDGE_BASE = "knowledge_base"       # Domain knowledge
    TEMPORAL_CONTEXT = "temporal_context"   # Time-sensitive information
    DEPENDENCY_GRAPH = "dependency_graph"   # Task/resource dependencies


@dataclass
class ContextItem:
    """Individual context item with metadata."""
    id: str
    content: str
    context_type: ContextType
    importance: ContextImportance
    created_at: datetime
    last_accessed: datetime
    access_count: int
    semantic_hash: str
    token_count: int
    compression_level: float = 0.0  # 0.0 = original, 1.0 = maximum compression
    
    def update_access(self):
        """Update access metadata."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def calculate_relevance_score(self, current_time: datetime = None) -> float:
        """Calculate context relevance score based on multiple factors."""
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Time decay factor
        time_diff = (current_time - self.last_accessed).total_seconds()
        time_decay = np.exp(-time_diff / 3600)  # Decay over hours
        
        # Access frequency factor
        access_frequency = min(self.access_count / 10, 1.0)  # Normalize to [0,1]
        
        # Importance weights
        importance_weights = {
            ContextImportance.CRITICAL: 1.0,
            ContextImportance.HIGH: 0.8,
            ContextImportance.MEDIUM: 0.6,
            ContextImportance.LOW: 0.4,
            ContextImportance.MINIMAL: 0.2
        }
        
        importance_weight = importance_weights.get(self.importance, 0.5)
        
        # Combined score
        relevance_score = (time_decay * 0.4 + 
                          access_frequency * 0.3 + 
                          importance_weight * 0.3)
        
        return relevance_score


class ContextRotMitigator:
    """
    Context degradation mitigation strategies inspired by context-rot research.
    
    Implements techniques to handle the "10,000th token problem" where LLM 
    performance degrades with long contexts.
    """
    
    def __init__(self, max_context_tokens: int = 8000):
        self.max_context_tokens = max_context_tokens
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Context rot detection parameters
        self.performance_threshold = 0.8  # Below this, context is considered degraded
        self.token_position_sensitivity = True  # Account for position effects
        
        # Needle-in-haystack detection for important information
        self.semantic_needles = set()  # Important facts to preserve
        
    async def detect_context_degradation(self, context_items: List[ContextItem]) -> Dict[str, Any]:
        """
        Detect potential context degradation using context-rot principles.
        
        Returns assessment of context health and recommendations.
        """
        total_tokens = sum(item.token_count for item in context_items)
        
        # Check for length-based degradation risk
        length_risk = min(total_tokens / self.max_context_tokens, 1.0)
        
        # Check for position-based risks (important info buried in middle)
        position_risks = await self._analyze_position_risks(context_items)
        
        # Check for semantic needle preservation
        needle_preservation = await self._check_needle_preservation(context_items)
        
        # Detect repetitive patterns that may confuse models
        repetition_issues = await self._detect_repetition_issues(context_items)
        
        degradation_assessment = {
            "overall_risk": (length_risk + position_risks["avg_risk"] + 
                           (1 - needle_preservation) + repetition_issues) / 4,
            "length_risk": length_risk,
            "position_risks": position_risks,
            "needle_preservation": needle_preservation,
            "repetition_issues": repetition_issues,
            "total_tokens": total_tokens,
            "max_tokens": self.max_context_tokens,
            "recommendations": []
        }
        
        # Generate recommendations
        if length_risk > 0.8:
            degradation_assessment["recommendations"].append("urgent_compression_needed")
        if position_risks["avg_risk"] > 0.6:
            degradation_assessment["recommendations"].append("reorder_context_items")
        if needle_preservation < 0.7:
            degradation_assessment["recommendations"].append("protect_critical_information")
        if repetition_issues > 0.5:
            degradation_assessment["recommendations"].append("deduplicate_content")
        
        return degradation_assessment
    
    async def _analyze_position_risks(self, context_items: List[ContextItem]) -> Dict[str, Any]:
        """Analyze risks based on context position (inspired by NIAH experiments)."""
        if not context_items:
            return {"avg_risk": 0, "high_risk_positions": []}
        
        total_tokens = sum(item.token_count for item in context_items)
        high_risk_positions = []
        position_risks = []
        
        current_position = 0
        for i, item in enumerate(context_items):
            # Calculate relative position (0 = start, 1 = end)
            relative_position = current_position / max(total_tokens, 1)
            
            # Middle positions (0.3-0.7) are highest risk based on research
            if 0.3 <= relative_position <= 0.7:
                risk_multiplier = 2.0
                if item.importance in [ContextImportance.CRITICAL, ContextImportance.HIGH]:
                    high_risk_positions.append({
                        "item_id": item.id,
                        "position": relative_position,
                        "importance": item.importance.value,
                        "risk_score": risk_multiplier * (1 - item.calculate_relevance_score())
                    })
            else:
                risk_multiplier = 1.0
            
            position_risk = risk_multiplier * (1 - item.calculate_relevance_score())
            position_risks.append(position_risk)
            
            current_position += item.token_count
        
        return {
            "avg_risk": np.mean(position_risks) if position_risks else 0,
            "max_risk": max(position_risks) if position_risks else 0,
            "high_risk_positions": high_risk_positions
        }
    
    async def _check_needle_preservation(self, context_items: List[ContextItem]) -> float:
        """Check if semantic needles (critical info) are preserved."""
        if not self.semantic_needles:
            return 1.0  # No needles to check
        
        preserved_needles = 0
        
        for item in context_items:
            if item.importance == ContextImportance.CRITICAL:
                # Check if critical information is present and accessible
                content_hash = hashlib.md5(item.content.encode()).hexdigest()
                if content_hash in self.semantic_needles or any(
                    needle in item.content.lower() for needle in self.semantic_needles
                ):
                    preserved_needles += 1
        
        return preserved_needles / max(len(self.semantic_needles), 1)
    
    async def _detect_repetition_issues(self, context_items: List[ContextItem]) -> float:
        """Detect repetitive content that may confuse models."""
        if len(context_items) < 2:
            return 0.0
        
        content_hashes = [item.semantic_hash for item in context_items]
        unique_hashes = set(content_hashes)
        
        # Calculate repetition ratio
        repetition_ratio = 1 - (len(unique_hashes) / len(content_hashes))
        
        return repetition_ratio
    
    def add_semantic_needle(self, needle: str):
        """Add important information that should be preserved."""
        self.semantic_needles.add(needle.lower())


class AdaptiveContextManager:
    """
    Advanced context manager with adaptive compression and prioritization.
    
    Implements strategies to mitigate context rot while maintaining
    information fidelity for AI agents.
    """
    
    def __init__(self, max_context_tokens: int = 8000):
        self.max_context_tokens = max_context_tokens
        self.context_items: Dict[str, ContextItem] = {}
        self.context_rot_mitigator = ContextRotMitigator(max_context_tokens)
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Adaptive parameters
        self.compression_strategies = {
            "summarization": self._summarize_content,
            "extraction": self._extract_key_points,
            "deduplication": self._deduplicate_content,
            "temporal_filtering": self._filter_by_time
        }
        
        # Context window management
        self.sliding_window_size = max_context_tokens // 2
        self.context_buffer_ratio = 0.2  # Keep 20% buffer for new context
    
    async def add_context(self, content: str, context_type: ContextType, 
                         importance: ContextImportance = ContextImportance.MEDIUM) -> str:
        """Add new context with automatic management."""
        
        # Create context item
        item_id = hashlib.md5(f"{content}{datetime.utcnow()}".encode()).hexdigest()[:12]
        semantic_hash = hashlib.md5(content.encode()).hexdigest()
        
        context_item = ContextItem(
            id=item_id,
            content=content,
            context_type=context_type,
            importance=importance,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            semantic_hash=semantic_hash,
            token_count=len(content.split()) * 1.3  # Approximate token count
        )
        
        self.context_items[item_id] = context_item
        
        # Check for context degradation
        degradation_assessment = await self.context_rot_mitigator.detect_context_degradation(
            list(self.context_items.values())
        )
        
        # Apply mitigation strategies if needed
        if degradation_assessment["overall_risk"] > 0.7:
            await self._apply_mitigation_strategies(degradation_assessment)
        
        self.logger.info(f"Added context item {item_id}, total items: {len(self.context_items)}")
        
        return item_id
    
    async def get_optimized_context(self, query_context: str = "", 
                                  max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Get optimized context that mitigates context rot effects.
        
        Returns context organized to minimize position-based degradation.
        """
        if max_tokens is None:
            max_tokens = self.max_context_tokens
        
        # Get relevant context items
        relevant_items = await self._rank_context_items(query_context)
        
        # Optimize context ordering to minimize position effects
        optimized_items = await self._optimize_context_ordering(relevant_items, max_tokens)
        
        # Apply compression if needed
        if sum(item.token_count for item in optimized_items) > max_tokens:
            optimized_items = await self._apply_adaptive_compression(optimized_items, max_tokens)
        
        # Structure final context
        structured_context = await self._structure_final_context(optimized_items, query_context)
        
        return structured_context
    
    async def _rank_context_items(self, query_context: str) -> List[ContextItem]:
        """Rank context items by relevance to current query."""
        current_time = datetime.utcnow()
        
        scored_items = []
        for item in self.context_items.values():
            base_score = item.calculate_relevance_score(current_time)
            
            # Boost score for query relevance (simple keyword matching)
            if query_context and any(word.lower() in item.content.lower() 
                                   for word in query_context.split()):
                base_score *= 1.5
            
            scored_items.append((base_score, item))
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return [item for score, item in scored_items]
    
    async def _optimize_context_ordering(self, items: List[ContextItem], 
                                       max_tokens: int) -> List[ContextItem]:
        """
        Optimize context ordering to minimize position-based degradation.
        
        Based on context-rot research: place critical info at start/end,
        avoid burying important information in the middle.
        """
        if not items:
            return []
        
        # Separate items by importance
        critical_items = [item for item in items if item.importance == ContextImportance.CRITICAL]
        high_items = [item for item in items if item.importance == ContextImportance.HIGH]
        medium_items = [item for item in items if item.importance == ContextImportance.MEDIUM]
        low_items = [item for item in items if item.importance in [ContextImportance.LOW, ContextImportance.MINIMAL]]
        
        # Optimal ordering: critical at start, high at end, others in middle
        optimized_order = []
        
        # Start with critical items
        optimized_order.extend(critical_items)
        
        # Add medium and low items in middle positions
        optimized_order.extend(medium_items)
        optimized_order.extend(low_items)
        
        # End with high importance items for recency effect
        optimized_order.extend(high_items)
        
        # Trim to fit token limit
        total_tokens = 0
        final_items = []
        
        for item in optimized_order:
            if total_tokens + item.token_count <= max_tokens:
                final_items.append(item)
                total_tokens += item.token_count
            else:
                break
        
        return final_items
    
    async def _apply_adaptive_compression(self, items: List[ContextItem], 
                                        max_tokens: int) -> List[ContextItem]:
        """Apply adaptive compression to fit within token limits."""
        
        compressed_items = []
        remaining_tokens = max_tokens
        
        for item in items:
            if item.token_count <= remaining_tokens:
                # No compression needed
                compressed_items.append(item)
                remaining_tokens -= item.token_count
            elif item.importance in [ContextImportance.CRITICAL, ContextImportance.HIGH]:
                # Compress but preserve important items
                compression_ratio = remaining_tokens / item.token_count
                if compression_ratio > 0.3:  # Don't over-compress important items
                    compressed_content = await self._compress_content(
                        item.content, compression_ratio
                    )
                    
                    compressed_item = ContextItem(
                        id=item.id,
                        content=compressed_content,
                        context_type=item.context_type,
                        importance=item.importance,
                        created_at=item.created_at,
                        last_accessed=item.last_accessed,
                        access_count=item.access_count,
                        semantic_hash=item.semantic_hash,
                        token_count=remaining_tokens,
                        compression_level=1 - compression_ratio
                    )
                    
                    compressed_items.append(compressed_item)
                    remaining_tokens = 0
                    break
            # Skip less important items if no space
        
        return compressed_items
    
    async def _compress_content(self, content: str, compression_ratio: float) -> str:
        """Compress content while preserving key information."""
        
        if compression_ratio >= 1.0:
            return content
        
        # Simple compression: keep first and last parts, summarize middle
        words = content.split()
        target_length = int(len(words) * compression_ratio)
        
        if target_length < 10:
            # Very aggressive compression - keep only key phrases
            sentences = content.split('.')
            return '. '.join(sentences[:2]) + '...'
        
        # Keep beginning and end, compress middle
        keep_start = target_length // 3
        keep_end = target_length // 3
        
        if len(words) <= target_length:
            return content
        
        compressed = ' '.join(words[:keep_start]) + ' [...] ' + ' '.join(words[-keep_end:])
        
        return compressed
    
    async def _structure_final_context(self, items: List[ContextItem], 
                                     query_context: str) -> Dict[str, Any]:
        """Structure final context for optimal LLM consumption."""
        
        structured_context = {
            "query_context": query_context,
            "total_items": len(items),
            "total_tokens": sum(item.token_count for item in items),
            "context_sections": {},
            "metadata": {
                "optimization_applied": True,
                "context_rot_mitigation": True,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        # Group by context type for better organization
        for context_type in ContextType:
            type_items = [item for item in items if item.context_type == context_type]
            if type_items:
                structured_context["context_sections"][context_type.value] = [
                    {
                        "id": item.id,
                        "content": item.content,
                        "importance": item.importance.value,
                        "compression_level": item.compression_level,
                        "token_count": item.token_count
                    }
                    for item in type_items
                ]
        
        return structured_context
    
    async def _apply_mitigation_strategies(self, assessment: Dict[str, Any]):
        """Apply context rot mitigation strategies based on assessment."""
        
        recommendations = assessment.get("recommendations", [])
        
        if "urgent_compression_needed" in recommendations:
            await self._emergency_compression()
        
        if "reorder_context_items" in recommendations:
            await self._reorder_context_items()
        
        if "protect_critical_information" in recommendations:
            await self._protect_critical_information()
        
        if "deduplicate_content" in recommendations:
            await self._deduplicate_context()
    
    async def _emergency_compression(self):
        """Apply emergency compression to reduce context size."""
        
        items_list = list(self.context_items.values())
        
        # Remove least important items first
        items_list.sort(key=lambda x: (x.importance.value, x.calculate_relevance_score()))
        
        # Keep only top 70% of items
        keep_count = int(len(items_list) * 0.7)
        items_to_keep = items_list[:keep_count]
        
        # Update context items
        self.context_items = {item.id: item for item in items_to_keep}
        
        self.logger.info(f"Emergency compression: reduced from {len(items_list)} to {len(items_to_keep)} items")
    
    async def _reorder_context_items(self):
        """Reorder context items to minimize position effects."""
        # This is handled in get_optimized_context method
        pass
    
    async def _protect_critical_information(self):
        """Ensure critical information is marked as semantic needles."""
        for item in self.context_items.values():
            if item.importance == ContextImportance.CRITICAL:
                self.context_rot_mitigator.add_semantic_needle(item.content[:100])
    
    async def _deduplicate_context(self):
        """Remove duplicate context items."""
        seen_hashes = set()
        unique_items = {}
        
        for item in self.context_items.values():
            if item.semantic_hash not in seen_hashes:
                seen_hashes.add(item.semantic_hash)
                unique_items[item.id] = item
            else:
                # Update access count of existing item
                existing_items = [i for i in unique_items.values() 
                                if i.semantic_hash == item.semantic_hash]
                if existing_items:
                    existing_items[0].access_count += item.access_count
        
        removed_count = len(self.context_items) - len(unique_items)
        self.context_items = unique_items
        
        if removed_count > 0:
            self.logger.info(f"Deduplication: removed {removed_count} duplicate items")
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context management statistics."""
        
        total_tokens = sum(item.token_count for item in self.context_items.values())
        
        importance_distribution = {}
        for importance in ContextImportance:
            count = len([item for item in self.context_items.values() 
                        if item.importance == importance])
            importance_distribution[importance.value] = count
        
        type_distribution = {}
        for context_type in ContextType:
            count = len([item for item in self.context_items.values() 
                        if item.context_type == context_type])
            type_distribution[context_type.value] = count
        
        return {
            "total_items": len(self.context_items),
            "total_tokens": total_tokens,
            "token_utilization": total_tokens / self.max_context_tokens,
            "importance_distribution": importance_distribution,
            "type_distribution": type_distribution,
            "average_item_age_hours": self._calculate_average_age(),
            "context_health": "healthy" if total_tokens < self.max_context_tokens * 0.8 else "approaching_limit"
        }
    
    def _calculate_average_age(self) -> float:
        """Calculate average age of context items in hours."""
        if not self.context_items:
            return 0.0
        
        current_time = datetime.utcnow()
        total_age_hours = sum(
            (current_time - item.created_at).total_seconds() / 3600
            for item in self.context_items.values()
        )
        
        return total_age_hours / len(self.context_items)
    
    # Missing compression strategy methods  
    async def _summarize_content(self, content: str, target_ratio: float) -> str:
        """Summarize content to reduce size."""
        sentences = content.split('.')
        target_sentences = max(1, int(len(sentences) * target_ratio))
        return '. '.join(sentences[:target_sentences]) + '.'
    
    async def _extract_key_points(self, content: str, target_ratio: float) -> str:
        """Extract key points from content."""
        lines = content.split('\n')
        target_lines = max(1, int(len(lines) * target_ratio))
        # Simple heuristic: keep lines with keywords
        keywords = ['important', 'critical', 'required', 'must', 'should']
        key_lines = [line for line in lines if any(keyword in line.lower() for keyword in keywords)]
        
        if len(key_lines) >= target_lines:
            return '\n'.join(key_lines[:target_lines])
        else:
            return '\n'.join(lines[:target_lines])
    
    async def _deduplicate_content(self, content: str, target_ratio: float) -> str:
        """Remove duplicate content."""
        lines = content.split('\n')
        seen_lines = set()
        unique_lines = []
        
        for line in lines:
            line_normalized = line.strip().lower()
            if line_normalized not in seen_lines:
                seen_lines.add(line_normalized)
                unique_lines.append(line)
        
        target_lines = max(1, int(len(unique_lines) * target_ratio))
        return '\n'.join(unique_lines[:target_lines])
    
    async def _filter_by_time(self, content: str, target_ratio: float) -> str:
        """Filter content by time relevance."""
        # Simple implementation - keep most recent content
        lines = content.split('\n')
        target_lines = max(1, int(len(lines) * target_ratio))
        return '\n'.join(lines[-target_lines:])  # Keep last N lines