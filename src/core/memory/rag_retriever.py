"""RAG (Retrieval-Augmented Generation) system for agent memory."""

import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from src.utils import get_logger
from src.config import settings
from src.core.memory.bge_embedding import create_embedding_service

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """Result from retrieval operation."""
    content: Dict[str, Any]
    similarity_score: float
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]


class MockVectorStore:
    """Mock vector store for development (would use Pinecone/Weaviate in production)."""
    
    def __init__(self):
        self.vectors = {}  # id -> (vector, metadata)
        self.dimension = 768  # Common embedding dimension
    
    async def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]):
        """Store vector with metadata."""
        self.vectors[id] = (np.array(vector), metadata)
    
    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Query similar vectors."""
        
        if not self.vectors:
            return []
        
        query_vector = np.array(vector)
        results = []
        
        for vec_id, (stored_vector, metadata) in self.vectors.items():
            # Apply filters if provided
            if filter_dict:
                if not all(metadata.get(k) == v for k, v in filter_dict.items()):
                    continue
            
            # Calculate cosine similarity
            similarity = np.dot(query_vector, stored_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(stored_vector)
            )
            
            results.append((vec_id, float(similarity), metadata))
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    async def delete(self, id: str):
        """Delete vector by ID."""
        if id in self.vectors:
            del self.vectors[id]


class MockEmbedding:
    """Mock embedding service (would use OpenAI/local model in production)."""
    
    def __init__(self):
        self.dimension = 768
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        # Simple hash-based mock embedding
        hash_val = hash(text)
        np.random.seed(abs(hash_val) % 2**32)
        vector = np.random.normal(0, 1, self.dimension)
        return vector / np.linalg.norm(vector)  # Normalize
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [await self.embed_text(text) for text in texts]


class RAGRetriever:
    """
    Retrieval-Augmented Generation system for agent memory.
    
    Provides semantic search over stored memories, decisions, and knowledge
    to enhance agent context with relevant historical information.
    """
    
    def __init__(self):
        self.vector_store = MockVectorStore()
        self.embedding_service = create_embedding_service()
        self.logger = get_logger(f"{self.__class__.__name__}")
        self._initialized = False
        
        # Indexing configuration
        self.index_types = {
            "decisions": {"weight": 1.0, "retention_days": 90},
            "code": {"weight": 0.8, "retention_days": 60},
            "bugs": {"weight": 0.9, "retention_days": 120},
            "patterns": {"weight": 0.7, "retention_days": 180},
            "meetings": {"weight": 0.6, "retention_days": 30}
        }
    
    async def initialize(self) -> bool:
        """Initialize the RAG retriever with embedding service."""
        
        if self._initialized:
            return True
        
        try:
            # Initialize embedding service
            success = await self.embedding_service.initialize()
            if success:
                self._initialized = True
                self.logger.info("RAG retriever initialized successfully")
                
                # Update vector store dimension if needed
                if hasattr(self.embedding_service, 'dimension'):
                    self.vector_store.dimension = self.embedding_service.dimension
                
                return True
            else:
                self.logger.error("Failed to initialize embedding service")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG retriever: {str(e)}")
            return False
    
    async def shutdown(self):
        """Shutdown the RAG retriever."""
        
        if hasattr(self.embedding_service, 'shutdown'):
            await self.embedding_service.shutdown()
        
        self._initialized = False
        self.logger.info("RAG retriever shutdown")
    
    async def index_memory(
        self,
        content: Dict[str, Any],
        content_type: str,
        project_id: str,
        sprint_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> str:
        """
        Index content for retrieval.
        
        Args:
            content: Content to index
            content_type: Type of content (decision, code, bug, etc.)
            project_id: Project identifier
            sprint_id: Sprint identifier (optional)
            agent_id: Agent that created content (optional)
            
        Returns:
            Document ID
        """
        
        # Create document ID
        doc_id = f"{content_type}_{project_id}_{datetime.utcnow().timestamp()}"
        
        # Extract text for embedding
        text_content = self._extract_text_content(content)
        
        if not text_content:
            self.logger.warning(f"No text content found for indexing: {doc_id}")
            return doc_id
        
        try:
            # Generate embedding
            embedding = await self.embedding_service.embed_text(text_content)
            
            # Create metadata
            metadata = {
                "content_type": content_type,
                "project_id": project_id,
                "sprint_id": sprint_id,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "text_content": text_content[:500],  # Store snippet for debugging
                "full_content": json.dumps(content)  # Store full content
            }
            
            # Store in vector database
            await self.vector_store.upsert(doc_id, embedding, metadata)
            
            self.logger.info(f"Indexed content: {content_type} ({doc_id})")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to index content {doc_id}: {str(e)}")
            return doc_id
    
    async def retrieve_similar(
        self,
        query: str,
        project_id: str,
        content_types: Optional[List[str]] = None,
        sprint_id: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[RetrievalResult]:
        """
        Retrieve similar content based on query.
        
        Args:
            query: Query text
            project_id: Project to search in
            content_types: Filter by content types
            sprint_id: Filter by sprint
            limit: Maximum results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of retrieval results
        """
        
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_text(query)
            
            # Prepare filters
            filters = {"project_id": project_id}
            if sprint_id:
                filters["sprint_id"] = sprint_id
            
            # Query vector store
            raw_results = await self.vector_store.query(
                query_embedding,
                top_k=limit * 2,  # Get more to filter
                filter_dict=filters
            )
            
            # Process and filter results
            results = []
            for doc_id, similarity, metadata in raw_results:
                # Apply similarity threshold
                if similarity < similarity_threshold:
                    continue
                
                # Apply content type filter
                if content_types and metadata.get("content_type") not in content_types:
                    continue
                
                # Parse content
                try:
                    full_content = json.loads(metadata.get("full_content", "{}"))
                except:
                    full_content = {"text": metadata.get("text_content", "")}
                
                result = RetrievalResult(
                    content=full_content,
                    similarity_score=similarity,
                    source=doc_id,
                    timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.utcnow().isoformat())),
                    metadata=metadata
                )
                
                results.append(result)
                
                if len(results) >= limit:
                    break
            
            self.logger.info(f"Retrieved {len(results)} similar items for query: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve similar content: {str(e)}")
            return []
    
    async def retrieve_by_context(
        self,
        context: Dict[str, Any],
        project_id: str,
        limit: int = 10
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant content based on current context.
        
        Args:
            context: Current agent context
            project_id: Project identifier
            limit: Maximum results
            
        Returns:
            List of relevant results
        """
        
        # Extract queries from context
        queries = self._extract_context_queries(context)
        
        if not queries:
            return []
        
        # Retrieve for each query and combine results
        all_results = []
        
        for query, weight in queries:
            results = await self.retrieve_similar(
                query=query,
                project_id=project_id,
                limit=max(2, limit // len(queries))  # Distribute limit across queries
            )
            
            # Apply weight to similarity scores
            for result in results:
                result.similarity_score *= weight
            
            all_results.extend(results)
        
        # Remove duplicates and sort by score
        unique_results = {}
        for result in all_results:
            if result.source not in unique_results or result.similarity_score > unique_results[result.source].similarity_score:
                unique_results[result.source] = result
        
        # Sort by similarity and return top results
        final_results = list(unique_results.values())
        final_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return final_results[:limit]
    
    async def index_sprint_artifacts(
        self,
        project_id: str,
        sprint_id: str,
        artifacts: Dict[str, Any]
    ) -> List[str]:
        """
        Index all artifacts from a completed sprint.
        
        Args:
            project_id: Project identifier
            sprint_id: Sprint identifier
            artifacts: Sprint artifacts to index
            
        Returns:
            List of document IDs
        """
        
        indexed_docs = []
        
        # Index different types of artifacts
        artifact_types = {
            "decisions": artifacts.get("decisions", []),
            "code": artifacts.get("code_changes", []),
            "bugs": artifacts.get("bugs_found", []),
            "patterns": artifacts.get("learned_patterns", []),
            "meetings": artifacts.get("meeting_minutes", [])
        }
        
        for artifact_type, items in artifact_types.items():
            if not items:
                continue
                
            if isinstance(items, list):
                for item in items:
                    doc_id = await self.index_memory(
                        content=item,
                        content_type=artifact_type,
                        project_id=project_id,
                        sprint_id=sprint_id
                    )
                    indexed_docs.append(doc_id)
            else:
                doc_id = await self.index_memory(
                    content=items,
                    content_type=artifact_type,
                    project_id=project_id,
                    sprint_id=sprint_id
                )
                indexed_docs.append(doc_id)
        
        self.logger.info(f"Indexed {len(indexed_docs)} artifacts from sprint {sprint_id}")
        return indexed_docs
    
    async def find_similar_projects(
        self,
        project_context: Dict[str, Any],
        limit: int = 3
    ) -> List[RetrievalResult]:
        """
        Find similar projects based on project context.
        
        Args:
            project_context: Current project context
            limit: Maximum similar projects to return
            
        Returns:
            List of similar project results
        """
        
        # Create project description query
        tech_stack = project_context.get("tech_stack", {})
        project_type = project_context.get("project_type", "")
        features = project_context.get("features", [])
        
        query_parts = []
        if project_type:
            query_parts.append(f"Project type: {project_type}")
        if tech_stack:
            query_parts.append(f"Technologies: {', '.join(tech_stack.values())}")
        if features:
            query_parts.append(f"Features: {', '.join(features[:3])}")  # Top 3 features
        
        query = ". ".join(query_parts)
        
        if not query:
            return []
        
        # Search across all projects (no project filter)
        results = await self.retrieve_similar(
            query=query,
            project_id="*",  # Special value to search all projects
            content_types=["patterns", "decisions"],
            limit=limit * 2  # Get more to filter for unique projects
        )
        
        # Group by project and return best result from each
        project_results = {}
        for result in results:
            result_project_id = result.metadata.get("project_id")
            if result_project_id not in project_results or result.similarity_score > project_results[result_project_id].similarity_score:
                project_results[result_project_id] = result
        
        # Return top similar projects
        similar_projects = list(project_results.values())
        similar_projects.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return similar_projects[:limit]
    
    async def get_relevant_knowledge(
        self,
        agent_role: str,
        task_context: Dict[str, Any],
        project_id: str,
        limit: int = 5
    ) -> List[RetrievalResult]:
        """
        Get relevant knowledge for a specific agent role and task.
        
        Args:
            agent_role: Role of the requesting agent
            task_context: Current task context
            project_id: Project identifier
            limit: Maximum results
            
        Returns:
            List of relevant knowledge
        """
        
        # Create role-specific query
        role_queries = {
            "pm": ["requirements", "user stories", "product decisions"],
            "architect": ["architecture", "technical decisions", "design patterns"],
            "developer": ["code patterns", "implementation", "bug fixes"],
            "qa": ["test cases", "bug reports", "quality issues"],
            "ui": ["design decisions", "user interface", "user experience"]
        }
        
        base_queries = role_queries.get(agent_role, ["general development"])
        
        # Add task-specific context
        task_type = task_context.get("type", "")
        task_description = task_context.get("description", "")
        
        if task_type:
            base_queries.append(task_type)
        if task_description:
            base_queries.append(task_description[:100])  # Limit length
        
        # Search for each query
        all_results = []
        for query in base_queries:
            results = await self.retrieve_similar(
                query=query,
                project_id=project_id,
                limit=max(1, limit // len(base_queries))
            )
            all_results.extend(results)
        
        # Remove duplicates and return top results
        unique_results = {r.source: r for r in all_results}
        final_results = list(unique_results.values())
        final_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return final_results[:limit]
    
    async def cleanup_old_indexes(self, retention_days: int = 180):
        """Clean up old indexed content."""
        
        cutoff_date = datetime.utcnow().timestamp() - (retention_days * 24 * 3600)
        
        # This would require iteration over all vectors in production
        # For now, just log the operation
        self.logger.info(f"Cleanup old indexes older than {retention_days} days")
    
    # Private helper methods
    
    def _extract_text_content(self, content: Dict[str, Any]) -> str:
        """Extract searchable text from content."""
        
        text_parts = []
        
        # Extract text from various fields
        text_fields = ["title", "description", "summary", "content", "text", "message", "rationale"]
        
        for field in text_fields:
            if field in content and isinstance(content[field], str):
                text_parts.append(content[field])
        
        # Extract from nested structures
        if "decisions" in content and isinstance(content["decisions"], list):
            for decision in content["decisions"]:
                if isinstance(decision, dict):
                    text_parts.extend(self._extract_text_from_dict(decision))
        
        if "user_stories" in content and isinstance(content["user_stories"], list):
            for story in content["user_stories"]:
                if isinstance(story, dict):
                    text_parts.extend(self._extract_text_from_dict(story))
        
        return " ".join(text_parts)
    
    def _extract_text_from_dict(self, data: Dict[str, Any]) -> List[str]:
        """Extract text values from a dictionary."""
        
        text_values = []
        for value in data.values():
            if isinstance(value, str) and len(value.strip()) > 0:
                text_values.append(value.strip())
        
        return text_values
    
    def _extract_context_queries(self, context: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Extract queries from agent context with weights."""
        
        queries = []
        
        # Sprint goal (high weight)
        sprint_goal = context.get("sprint_goal")
        if sprint_goal:
            queries.append((sprint_goal, 1.0))
        
        # Active blockers (high weight)
        blockers = context.get("active_blockers", [])
        for blocker in blockers[:2]:  # Top 2 blockers
            if isinstance(blocker, dict) and "description" in blocker:
                queries.append((blocker["description"], 0.9))
        
        # Recent work (medium weight)
        recent_work = context.get("recent_work", [])
        for work_item in recent_work[:3]:  # Top 3 recent items
            if isinstance(work_item, dict):
                work_text = self._extract_text_content(work_item)
                if work_text:
                    queries.append((work_text[:200], 0.6))  # Limit length
        
        # Key decisions (medium weight)
        decisions = context.get("key_decisions", [])
        for decision in decisions[-2:]:  # Last 2 decisions
            if isinstance(decision, dict) and "description" in decision:
                queries.append((decision["description"], 0.7))
        
        return queries