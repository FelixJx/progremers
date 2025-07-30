"""Sprint memory management system."""

import json
import redis
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class MemoryLayer(str, Enum):
    """Different layers of memory."""
    CORE = "core"           # Essential sprint information
    WORKING = "working"     # Current task context
    EPISODIC = "episodic"   # Event-based memories
    SEMANTIC = "semantic"   # Knowledge and patterns


@dataclass
class MemoryItem:
    """A single memory item."""
    id: str
    layer: MemoryLayer
    content: Dict[str, Any]
    importance: float  # 0-1 scale
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    project_id: str = ""
    sprint_id: str = ""


class SprintMemoryManager:
    """
    Manages multi-layered memory for sprints.
    
    Memory Layers:
    - Core: Sprint goal, key decisions, blockers (always in context)
    - Working: Current task details, recent discussions (2-4k tokens)
    - Episodic: Meeting records, significant events (compressed storage)
    - Semantic: Patterns, lessons learned (vector storage)
    """
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Memory size limits (in tokens)
        self.memory_limits = {
            MemoryLayer.CORE: 500,
            MemoryLayer.WORKING: 2000, 
            MemoryLayer.EPISODIC: 1000,
            MemoryLayer.SEMANTIC: 500
        }
        
        # Decay rates for memory importance
        self.decay_rates = {
            MemoryLayer.CORE: 0.0,      # Never decay
            MemoryLayer.WORKING: 0.1,   # Slow decay
            MemoryLayer.EPISODIC: 0.05, # Very slow decay
            MemoryLayer.SEMANTIC: 0.02  # Almost no decay
        }
    
    async def initialize_sprint_memory(
        self,
        project_id: str,
        sprint_id: str,
        sprint_goal: str,
        initial_context: Dict[str, Any]
    ) -> None:
        """Initialize memory for a new sprint."""
        
        self.logger.info(f"Initializing sprint memory: {sprint_id}")
        
        # Create core memory
        core_memory = {
            "sprint_goal": sprint_goal,
            "start_date": datetime.utcnow().isoformat(),
            "key_decisions": [],
            "active_blockers": [],
            "success_metrics": initial_context.get("success_metrics", [])
        }
        
        await self.store_memory(
            project_id=project_id,
            sprint_id=sprint_id,
            layer=MemoryLayer.CORE,
            content=core_memory,
            importance=1.0
        )
        
        # Initialize other layers
        for layer in [MemoryLayer.WORKING, MemoryLayer.EPISODIC, MemoryLayer.SEMANTIC]:
            await self.store_memory(
                project_id=project_id,
                sprint_id=sprint_id,
                layer=layer,
                content={},
                importance=0.5
            )
    
    async def store_memory(
        self,
        project_id: str,
        sprint_id: str,
        layer: MemoryLayer,
        content: Dict[str, Any],
        importance: float = 0.5,
        memory_id: Optional[str] = None
    ) -> str:
        """Store a memory item."""
        
        if memory_id is None:
            memory_id = f"{layer.value}_{datetime.utcnow().timestamp()}"
        
        memory_item = MemoryItem(
            id=memory_id,
            layer=layer,
            content=content,
            importance=importance,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            project_id=project_id,
            sprint_id=sprint_id
        )
        
        # Store in Redis
        key = self._get_memory_key(project_id, sprint_id, layer, memory_id)
        value = json.dumps({
            "id": memory_item.id,
            "layer": memory_item.layer.value,
            "content": memory_item.content,
            "importance": memory_item.importance,
            "created_at": memory_item.created_at.isoformat(),
            "last_accessed": memory_item.last_accessed.isoformat(),
            "access_count": memory_item.access_count,
            "project_id": memory_item.project_id,
            "sprint_id": memory_item.sprint_id
        })
        
        await self.redis_client.setex(
            key,
            timedelta(days=30).total_seconds(),  # 30 day expiry
            value
        )
        
        self.logger.info(f"Stored memory: {layer.value}/{memory_id}")
        return memory_id
    
    async def retrieve_memory(
        self,
        project_id: str,
        sprint_id: str,
        layer: Optional[MemoryLayer] = None,
        max_tokens: int = 3000
    ) -> Dict[MemoryLayer, List[MemoryItem]]:
        """Retrieve memories for context injection."""
        
        memories = {}
        total_tokens = 0
        
        # Always include core memory first
        core_memories = await self._get_layer_memories(project_id, sprint_id, MemoryLayer.CORE)
        if core_memories:
            memories[MemoryLayer.CORE] = core_memories
            total_tokens += self._estimate_tokens(core_memories)
        
        # Add other layers based on importance and token limit
        layers_to_check = [MemoryLayer.WORKING, MemoryLayer.EPISODIC, MemoryLayer.SEMANTIC]
        if layer:
            layers_to_check = [layer] + [l for l in layers_to_check if l != layer]
        
        for mem_layer in layers_to_check:
            if total_tokens >= max_tokens:
                break
                
            layer_memories = await self._get_layer_memories(project_id, sprint_id, mem_layer)
            if layer_memories:
                # Sort by importance and recency
                layer_memories.sort(key=lambda m: (m.importance, m.last_accessed), reverse=True)
                
                # Add memories until token limit
                selected_memories = []
                for memory in layer_memories:
                    memory_tokens = self._estimate_tokens([memory])
                    if total_tokens + memory_tokens <= max_tokens:
                        selected_memories.append(memory)
                        total_tokens += memory_tokens
                    else:
                        break
                
                if selected_memories:
                    memories[mem_layer] = selected_memories
        
        # Update access counts
        for layer_memories in memories.values():
            for memory in layer_memories:
                await self._update_access_count(memory)
        
        self.logger.info(f"Retrieved {sum(len(ms) for ms in memories.values())} memories ({total_tokens} tokens)")
        return memories
    
    async def update_memory(
        self,
        project_id: str,
        sprint_id: str,
        layer: MemoryLayer,
        memory_id: str,
        content_update: Dict[str, Any],
        importance_boost: float = 0.0
    ) -> bool:
        """Update an existing memory."""
        
        key = self._get_memory_key(project_id, sprint_id, layer, memory_id)
        
        try:
            existing_data = await self.redis_client.get(key)
            if not existing_data:
                return False
            
            memory_data = json.loads(existing_data)
            
            # Update content
            memory_data["content"].update(content_update)
            
            # Boost importance if requested
            if importance_boost > 0:
                memory_data["importance"] = min(1.0, memory_data["importance"] + importance_boost)
            
            # Update timestamps
            memory_data["last_accessed"] = datetime.utcnow().isoformat()
            
            # Save back to Redis
            await self.redis_client.setex(
                key,
                timedelta(days=30).total_seconds(),
                json.dumps(memory_data)
            )
            
            self.logger.info(f"Updated memory: {layer.value}/{memory_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update memory {memory_id}: {str(e)}")
            return False
    
    async def add_decision(
        self,
        project_id: str,
        sprint_id: str,
        decision: Dict[str, Any]
    ) -> None:
        """Add a key decision to core memory."""
        
        core_memories = await self._get_layer_memories(project_id, sprint_id, MemoryLayer.CORE)
        if core_memories:
            core_memory = core_memories[0]
            decisions = core_memory.content.get("key_decisions", [])
            decisions.append({
                **decision,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self.update_memory(
                project_id, sprint_id, MemoryLayer.CORE,
                core_memory.id,
                {"key_decisions": decisions}
            )
    
    async def add_blocker(
        self,
        project_id: str,
        sprint_id: str,
        blocker: Dict[str, Any]
    ) -> None:
        """Add a blocker to core memory."""
        
        core_memories = await self._get_layer_memories(project_id, sprint_id, MemoryLayer.CORE)
        if core_memories:
            core_memory = core_memories[0]
            blockers = core_memory.content.get("active_blockers", [])
            blockers.append({
                **blocker,
                "added_at": datetime.utcnow().isoformat()
            })
            
            await self.update_memory(
                project_id, sprint_id, MemoryLayer.CORE,
                core_memory.id,
                {"active_blockers": blockers}
            )
    
    async def resolve_blocker(
        self,
        project_id: str,
        sprint_id: str,
        blocker_id: str,
        resolution: str
    ) -> None:
        """Mark a blocker as resolved."""
        
        core_memories = await self._get_layer_memories(project_id, sprint_id, MemoryLayer.CORE)
        if core_memories:
            core_memory = core_memories[0]
            blockers = core_memory.content.get("active_blockers", [])
            
            for blocker in blockers:
                if blocker.get("id") == blocker_id:
                    blocker["resolved"] = True
                    blocker["resolution"] = resolution
                    blocker["resolved_at"] = datetime.utcnow().isoformat()
                    break
            
            await self.update_memory(
                project_id, sprint_id, MemoryLayer.CORE,
                core_memory.id,
                {"active_blockers": blockers}
            )
    
    async def add_meeting_memory(
        self,
        project_id: str,
        sprint_id: str,
        meeting_type: str,
        meeting_data: Dict[str, Any]
    ) -> None:
        """Add meeting record to episodic memory."""
        
        meeting_record = {
            "type": meeting_type,
            "data": meeting_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        memory_id = f"meeting_{meeting_type}_{datetime.utcnow().timestamp()}"
        
        await self.store_memory(
            project_id=project_id,
            sprint_id=sprint_id,
            layer=MemoryLayer.EPISODIC,
            content=meeting_record,
            importance=0.8,  # Meetings are important
            memory_id=memory_id
        )
    
    async def compress_working_memory(
        self,
        project_id: str,
        sprint_id: str
    ) -> None:
        """Compress working memory when it gets too large."""
        
        working_memories = await self._get_layer_memories(project_id, sprint_id, MemoryLayer.WORKING)
        
        if not working_memories:
            return
        
        # Estimate total tokens
        total_tokens = self._estimate_tokens(working_memories)
        limit = self.memory_limits[MemoryLayer.WORKING]
        
        if total_tokens <= limit:
            return
        
        self.logger.info(f"Compressing working memory: {total_tokens} -> {limit} tokens")
        
        # Sort by importance and recency
        working_memories.sort(key=lambda m: (m.importance, m.last_accessed), reverse=True)
        
        # Keep most important memories
        compressed_memories = []
        compressed_tokens = 0
        
        for memory in working_memories:
            memory_tokens = self._estimate_tokens([memory])
            if compressed_tokens + memory_tokens <= limit:
                compressed_memories.append(memory)
                compressed_tokens += memory_tokens
            else:
                # Move less important memories to episodic layer
                await self._move_to_episodic(memory, project_id, sprint_id)
        
        # Clear working memory and store compressed version
        await self._clear_layer_memories(project_id, sprint_id, MemoryLayer.WORKING)
        
        for memory in compressed_memories:
            await self.store_memory(
                project_id=project_id,
                sprint_id=sprint_id,
                layer=MemoryLayer.WORKING,
                content=memory.content,
                importance=memory.importance,
                memory_id=memory.id
            )
    
    async def decay_memories(
        self,
        project_id: str,
        sprint_id: str
    ) -> None:
        """Apply decay to memory importance over time."""
        
        for layer in MemoryLayer:
            if layer == MemoryLayer.CORE:
                continue  # Core memories don't decay
            
            memories = await self._get_layer_memories(project_id, sprint_id, layer)
            decay_rate = self.decay_rates[layer]
            
            for memory in memories:
                age_days = (datetime.utcnow() - memory.created_at).days
                decay_factor = (1 - decay_rate) ** age_days
                new_importance = memory.importance * decay_factor
                
                if new_importance < 0.1:
                    # Remove very unimportant memories
                    await self._delete_memory(memory, project_id, sprint_id)
                else:
                    await self.update_memory(
                        project_id, sprint_id, layer, memory.id,
                        {}, -memory.importance + new_importance
                    )
    
    async def get_context_for_agent(
        self,
        project_id: str,
        sprint_id: str,
        agent_role: str,
        max_tokens: int = 3000
    ) -> Dict[str, Any]:
        """Get formatted context for an agent."""
        
        memories = await self.retrieve_memory(project_id, sprint_id, max_tokens=max_tokens)
        
        context = {
            "project_id": project_id,
            "sprint_id": sprint_id,
            "agent_role": agent_role,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Format memories for agent consumption
        if MemoryLayer.CORE in memories:
            core_memory = memories[MemoryLayer.CORE][0]
            context.update({
                "sprint_goal": core_memory.content.get("sprint_goal"),
                "key_decisions": core_memory.content.get("key_decisions", []),
                "active_blockers": core_memory.content.get("active_blockers", [])
            })
        
        if MemoryLayer.WORKING in memories:
            working_items = [m.content for m in memories[MemoryLayer.WORKING]]
            context["recent_work"] = working_items
        
        if MemoryLayer.EPISODIC in memories:
            episodic_items = [m.content for m in memories[MemoryLayer.EPISODIC]]
            context["meeting_history"] = episodic_items
        
        if MemoryLayer.SEMANTIC in memories:
            semantic_items = [m.content for m in memories[MemoryLayer.SEMANTIC]]
            context["learned_patterns"] = semantic_items
        
        return context
    
    # Private helper methods
    
    def _get_memory_key(
        self,
        project_id: str,
        sprint_id: str,
        layer: MemoryLayer,
        memory_id: str
    ) -> str:
        """Generate Redis key for memory storage."""
        return f"memory:{project_id}:{sprint_id}:{layer.value}:{memory_id}"
    
    async def _get_layer_memories(
        self,
        project_id: str,
        sprint_id: str,
        layer: MemoryLayer
    ) -> List[MemoryItem]:
        """Get all memories for a specific layer."""
        
        pattern = f"memory:{project_id}:{sprint_id}:{layer.value}:*"
        keys = await self.redis_client.keys(pattern)
        
        memories = []
        for key in keys:
            try:
                data = await self.redis_client.get(key)
                if data:
                    memory_data = json.loads(data)
                    memory = MemoryItem(
                        id=memory_data["id"],
                        layer=MemoryLayer(memory_data["layer"]),
                        content=memory_data["content"],
                        importance=memory_data["importance"],
                        created_at=datetime.fromisoformat(memory_data["created_at"]),
                        last_accessed=datetime.fromisoformat(memory_data["last_accessed"]),
                        access_count=memory_data.get("access_count", 0),
                        project_id=memory_data["project_id"],
                        sprint_id=memory_data["sprint_id"]
                    )
                    memories.append(memory)
            except Exception as e:
                self.logger.error(f"Error loading memory from {key}: {str(e)}")
        
        return memories
    
    def _estimate_tokens(self, memories: List[MemoryItem]) -> int:
        """Estimate token count for memories."""
        # Simple estimation: ~4 characters per token
        total_chars = sum(len(json.dumps(m.content)) for m in memories)
        return total_chars // 4
    
    async def _update_access_count(self, memory: MemoryItem) -> None:
        """Update access count for a memory."""
        key = self._get_memory_key(
            memory.project_id, memory.sprint_id,
            memory.layer, memory.id
        )
        
        try:
            data = await self.redis_client.get(key)
            if data:
                memory_data = json.loads(data)
                memory_data["access_count"] = memory_data.get("access_count", 0) + 1
                memory_data["last_accessed"] = datetime.utcnow().isoformat()
                
                await self.redis_client.setex(
                    key,
                    timedelta(days=30).total_seconds(),
                    json.dumps(memory_data)
                )
        except Exception as e:
            self.logger.error(f"Error updating access count: {str(e)}")
    
    async def _move_to_episodic(
        self,
        memory: MemoryItem,
        project_id: str,
        sprint_id: str
    ) -> None:
        """Move a memory from working to episodic layer."""
        
        # Store in episodic layer with reduced importance
        await self.store_memory(
            project_id=project_id,
            sprint_id=sprint_id,
            layer=MemoryLayer.EPISODIC,
            content=memory.content,
            importance=memory.importance * 0.7,  # Reduce importance
            memory_id=f"archived_{memory.id}"
        )
        
        # Delete from working layer
        await self._delete_memory(memory, project_id, sprint_id)
    
    async def _clear_layer_memories(
        self,
        project_id: str,
        sprint_id: str,
        layer: MemoryLayer
    ) -> None:
        """Clear all memories from a layer."""
        
        pattern = f"memory:{project_id}:{sprint_id}:{layer.value}:*"
        keys = await self.redis_client.keys(pattern)
        
        if keys:
            await self.redis_client.delete(*keys)
    
    async def _delete_memory(
        self,
        memory: MemoryItem,
        project_id: str,
        sprint_id: str
    ) -> None:
        """Delete a specific memory."""
        
        key = self._get_memory_key(project_id, sprint_id, memory.layer, memory.id)
        await self.redis_client.delete(key)