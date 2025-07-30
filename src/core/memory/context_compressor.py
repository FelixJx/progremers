"""Context compression for managing LLM token limits."""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from src.utils import get_logger

logger = get_logger(__name__)


class CompressionLevel(str, Enum):
    """Levels of compression."""
    LIGHT = "light"      # 10-20% reduction
    MEDIUM = "medium"    # 30-50% reduction  
    HEAVY = "heavy"      # 60-80% reduction
    EXTREME = "extreme"  # 80%+ reduction


class CompressionStrategy(str, Enum):
    """Compression strategies."""
    SUMMARIZE = "summarize"           # Use AI to summarize
    EXTRACT_KEY = "extract_key"       # Extract key information
    REMOVE_REDUNDANT = "remove_redundant"  # Remove duplicate info
    HIERARCHICAL = "hierarchical"     # Hierarchical importance
    TEMPORAL = "temporal"             # Time-based prioritization


class ContextCompressor:
    """
    Compresses agent context to fit within token limits while preserving
    the most important information.
    """
    
    def __init__(self):
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Compression weights for different content types
        self.content_weights = {
            "sprint_goal": 1.0,        # Never compress
            "key_decisions": 0.9,      # High importance
            "active_blockers": 0.95,   # Very high importance
            "user_stories": 0.8,       # Important
            "meeting_notes": 0.6,      # Medium importance
            "code_snippets": 0.7,      # Medium-high importance
            "test_results": 0.5,       # Medium importance
            "discussions": 0.3,        # Lower importance
            "logs": 0.2               # Lowest importance
        }
        
        # Token estimation: roughly 4 characters per token
        self.chars_per_token = 4
    
    async def compress_context(
        self,
        context: Dict[str, Any],
        target_tokens: int,
        strategy: CompressionStrategy = CompressionStrategy.HIERARCHICAL
    ) -> Dict[str, Any]:
        """
        Compress context to fit within target token limit.
        
        Args:
            context: The context to compress
            target_tokens: Maximum tokens allowed
            strategy: Compression strategy to use
            
        Returns:
            Compressed context
        """
        
        original_tokens = self._estimate_tokens(context)
        
        if original_tokens <= target_tokens:
            return context  # No compression needed
        
        compression_ratio = target_tokens / original_tokens
        level = self._determine_compression_level(compression_ratio)
        
        self.logger.info(f"Compressing context: {original_tokens} -> {target_tokens} tokens ({level.value})")
        
        if strategy == CompressionStrategy.HIERARCHICAL:
            compressed = await self._hierarchical_compression(context, target_tokens)
        elif strategy == CompressionStrategy.TEMPORAL:
            compressed = await self._temporal_compression(context, target_tokens)
        elif strategy == CompressionStrategy.SUMMARIZE:
            compressed = await self._summarize_compression(context, target_tokens)
        elif strategy == CompressionStrategy.EXTRACT_KEY:
            compressed = await self._extract_key_compression(context, target_tokens)
        else:
            compressed = await self._remove_redundant_compression(context, target_tokens)
        
        final_tokens = self._estimate_tokens(compressed)
        
        # Add compression metadata
        compressed["_compression_info"] = {
            "original_tokens": original_tokens,
            "compressed_tokens": final_tokens,
            "compression_ratio": final_tokens / original_tokens,
            "strategy": strategy.value,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Compression complete: {final_tokens} tokens ({final_tokens/original_tokens:.1%})")
        return compressed
    
    async def _hierarchical_compression(
        self,
        context: Dict[str, Any],
        target_tokens: int
    ) -> Dict[str, Any]:
        """Compress based on content importance hierarchy."""
        
        compressed = {}
        current_tokens = 0
        
        # Sort content by importance (weight)
        items = []
        for key, value in context.items():
            if key.startswith("_"):  # Skip metadata
                continue
                
            weight = self.content_weights.get(key, 0.5)
            tokens = self._estimate_tokens({key: value})
            items.append((key, value, weight, tokens))
        
        # Sort by weight (importance) descending
        items.sort(key=lambda x: x[2], reverse=True)
        
        # Add items in order of importance until we hit the limit
        for key, value, weight, tokens in items:
            if current_tokens + tokens <= target_tokens:
                compressed[key] = value
                current_tokens += tokens
            else:
                # Try to compress this item to fit
                remaining_tokens = target_tokens - current_tokens
                if remaining_tokens > 50:  # Minimum viable size
                    compressed_value = await self._compress_single_item(
                        key, value, remaining_tokens
                    )
                    if compressed_value is not None:
                        compressed[key] = compressed_value
                        current_tokens += self._estimate_tokens({key: compressed_value})
                break
        
        return compressed
    
    async def _temporal_compression(
        self,
        context: Dict[str, Any],
        target_tokens: int
    ) -> Dict[str, Any]:
        """Compress based on recency (newer content has higher priority)."""
        
        compressed = {}
        current_tokens = 0
        
        # Separate items by whether they have timestamps
        timestamped_items = []
        non_timestamped_items = []
        
        for key, value in context.items():
            if key.startswith("_"):
                continue
                
            timestamp = self._extract_timestamp(value)
            tokens = self._estimate_tokens({key: value})
            
            if timestamp:
                timestamped_items.append((key, value, timestamp, tokens))
            else:
                # Non-timestamped items get medium priority
                non_timestamped_items.append((key, value, tokens))
        
        # Sort timestamped items by recency (newest first)
        timestamped_items.sort(key=lambda x: x[2], reverse=True)
        
        # Add recent items first
        for key, value, timestamp, tokens in timestamped_items:
            if current_tokens + tokens <= target_tokens:
                compressed[key] = value
                current_tokens += tokens
            else:
                break
        
        # Add non-timestamped items if space remains
        for key, value, tokens in non_timestamped_items:
            if current_tokens + tokens <= target_tokens:
                compressed[key] = value
                current_tokens += tokens
            else:
                break
        
        return compressed
    
    async def _summarize_compression(
        self,
        context: Dict[str, Any],
        target_tokens: int
    ) -> Dict[str, Any]:
        """Use AI summarization to compress content."""
        
        # For now, use simple summarization heuristics
        # In production, this would use an LLM
        
        compressed = {}
        current_tokens = 0
        
        for key, value in context.items():
            if key.startswith("_"):
                continue
                
            item_tokens = self._estimate_tokens({key: value})
            
            if current_tokens + item_tokens <= target_tokens:
                compressed[key] = value
                current_tokens += item_tokens
            else:
                # Summarize this item
                summary = self._create_summary(key, value)
                summary_tokens = self._estimate_tokens({key: summary})
                
                if current_tokens + summary_tokens <= target_tokens:
                    compressed[f"{key}_summary"] = summary
                    current_tokens += summary_tokens
        
        return compressed
    
    async def _extract_key_compression(
        self,
        context: Dict[str, Any],
        target_tokens: int
    ) -> Dict[str, Any]:
        """Extract only key information from each context item."""
        
        compressed = {}
        current_tokens = 0
        
        for key, value in context.items():
            if key.startswith("_"):
                continue
                
            # Extract key information based on content type
            key_info = self._extract_key_info(key, value)
            key_tokens = self._estimate_tokens({key: key_info})
            
            if current_tokens + key_tokens <= target_tokens:
                compressed[key] = key_info
                current_tokens += key_tokens
            else:
                break
        
        return compressed
    
    async def _remove_redundant_compression(
        self,
        context: Dict[str, Any],
        target_tokens: int
    ) -> Dict[str, Any]:
        """Remove redundant and duplicate information."""
        
        # Find and remove duplicates
        seen_content = set()
        compressed = {}
        current_tokens = 0
        
        for key, value in context.items():
            if key.startswith("_"):
                continue
                
            # Create a content hash for duplicate detection
            content_hash = self._hash_content(value)
            
            if content_hash not in seen_content:
                item_tokens = self._estimate_tokens({key: value})
                
                if current_tokens + item_tokens <= target_tokens:
                    compressed[key] = value
                    current_tokens += item_tokens
                    seen_content.add(content_hash)
                else:
                    break
        
        return compressed
    
    async def _compress_single_item(
        self,
        key: str,
        value: Any,
        target_tokens: int
    ) -> Optional[Any]:
        """Compress a single context item to fit in target tokens."""
        
        if isinstance(value, dict):
            return await self._compress_dict(value, target_tokens)
        elif isinstance(value, list):
            return self._compress_list(value, target_tokens)
        elif isinstance(value, str):
            return self._compress_string(value, target_tokens)
        else:
            return value  # Can't compress other types
    
    async def _compress_dict(self, data: Dict[str, Any], target_tokens: int) -> Dict[str, Any]:
        """Compress a dictionary by removing less important keys."""
        
        compressed = {}
        current_tokens = 0
        
        # Sort keys by importance (if we have weights for them)
        items = [(k, v) for k, v in data.items()]
        items.sort(key=lambda x: self.content_weights.get(x[0], 0.5), reverse=True)
        
        for key, value in items:
            item_tokens = self._estimate_tokens({key: value})
            
            if current_tokens + item_tokens <= target_tokens:
                compressed[key] = value
                current_tokens += item_tokens
            else:
                break
        
        return compressed
    
    def _compress_list(self, data: List[Any], target_tokens: int) -> List[Any]:
        """Compress a list by keeping most recent/important items."""
        
        if not data:
            return data
        
        # Try to keep items from the end (most recent)
        compressed = []
        current_tokens = 0
        
        for item in reversed(data):
            item_tokens = self._estimate_tokens(item)
            
            if current_tokens + item_tokens <= target_tokens:
                compressed.insert(0, item)  # Insert at beginning to maintain order
                current_tokens += item_tokens
            else:
                break
        
        return compressed
    
    def _compress_string(self, text: str, target_tokens: int) -> str:
        """Compress a string by truncating or summarizing."""
        
        target_chars = target_tokens * self.chars_per_token
        
        if len(text) <= target_chars:
            return text
        
        # Simple truncation with ellipsis
        if target_chars > 20:
            return text[:target_chars-3] + "..."
        else:
            return text[:target_chars]
    
    def _determine_compression_level(self, ratio: float) -> CompressionLevel:
        """Determine compression level based on ratio."""
        
        if ratio >= 0.8:
            return CompressionLevel.LIGHT
        elif ratio >= 0.5:
            return CompressionLevel.MEDIUM
        elif ratio >= 0.2:
            return CompressionLevel.HEAVY
        else:
            return CompressionLevel.EXTREME
    
    def _estimate_tokens(self, data: Any) -> int:
        """Estimate token count for data."""
        
        if isinstance(data, str):
            return len(data) // self.chars_per_token
        else:
            json_str = json.dumps(data, ensure_ascii=False)
            return len(json_str) // self.chars_per_token
    
    def _extract_timestamp(self, data: Any) -> Optional[datetime]:
        """Extract timestamp from data if available."""
        
        if isinstance(data, dict):
            # Look for common timestamp fields
            for field in ["timestamp", "created_at", "date", "time"]:
                if field in data:
                    try:
                        return datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    except:
                        continue
        
        return None
    
    def _create_summary(self, key: str, value: Any) -> str:
        """Create a simple summary of content."""
        
        if isinstance(value, dict):
            # Summarize dictionary
            summary_parts = []
            for k, v in value.items():
                if isinstance(v, (str, int, float, bool)):
                    summary_parts.append(f"{k}: {v}")
                elif isinstance(v, list):
                    summary_parts.append(f"{k}: {len(v)} items")
                else:
                    summary_parts.append(f"{k}: [complex object]")
            
            return f"Summary of {key}: " + "; ".join(summary_parts[:5])  # Limit to 5 items
        
        elif isinstance(value, list):
            return f"Summary of {key}: {len(value)} items"
        
        elif isinstance(value, str):
            # Extract first and last sentences
            sentences = re.split(r'[.!?]+', value)
            if len(sentences) > 2:
                return f"{sentences[0]}... {sentences[-2]}"
            else:
                return value[:200] + "..." if len(value) > 200 else value
        
        else:
            return f"Summary of {key}: {str(value)[:100]}"
    
    def _extract_key_info(self, key: str, value: Any) -> Any:
        """Extract key information based on content type."""
        
        if key == "sprint_goal":
            return value  # Never compress sprint goal
        
        elif key == "key_decisions":
            # Keep only the most recent decisions
            if isinstance(value, list) and len(value) > 3:
                return value[-3:]  # Last 3 decisions
            return value
        
        elif key == "active_blockers":
            # Keep only unresolved blockers
            if isinstance(value, list):
                return [b for b in value if not b.get("resolved", False)]
            return value
        
        elif key == "user_stories":
            # Keep only essential fields
            if isinstance(value, list):
                simplified = []
                for story in value:
                    if isinstance(story, dict):
                        simplified.append({
                            "title": story.get("title", ""),
                            "status": story.get("status", ""),
                            "priority": story.get("priority", ""),
                            "assigned_to": story.get("assigned_to", "")
                        })
                return simplified
            return value
        
        else:
            # Default: return as-is
            return value
    
    def _hash_content(self, content: Any) -> str:
        """Create a hash for content to detect duplicates."""
        
        # Simple hash based on string representation
        content_str = json.dumps(content, sort_keys=True) if not isinstance(content, str) else content
        return str(hash(content_str))
    
    def get_compression_stats(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get compression statistics for context."""
        
        if "_compression_info" not in context:
            return {"compressed": False}
        
        info = context["_compression_info"]
        
        return {
            "compressed": True,
            "original_tokens": info["original_tokens"],
            "compressed_tokens": info["compressed_tokens"],
            "compression_ratio": info["compression_ratio"],
            "space_saved": info["original_tokens"] - info["compressed_tokens"],
            "strategy": info["strategy"],
            "level": info["level"],
            "timestamp": info["timestamp"]
        }