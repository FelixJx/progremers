"""BGE-M3 embedding service for high-quality semantic search."""

import asyncio
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

try:
    from FlagEmbedding import BGEM3FlagModel
    BGE_AVAILABLE = True
except ImportError:
    BGE_AVAILABLE = False
    logging.warning("FlagEmbedding not installed. Using fallback embedding.")

from src.utils import get_logger
from src.config import settings

logger = get_logger(__name__)


class BGEM3Embedding:
    """
    BGE-M3 embedding service providing high-quality multilingual embeddings.
    
    BGE-M3 advantages:
    - Multilingual support (Chinese, English, etc.)
    - High semantic quality
    - 1024-dimensional embeddings
    - Support for dense, sparse, and colbert retrieval
    """
    
    def __init__(self, model_name: str = "BAAI/bge-m3", use_fp16: bool = True):
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.model = None
        self.dimension = 1024  # BGE-M3 embedding dimension
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # Model configuration
        self.max_length = 8192  # BGE-M3 max input length
        self.batch_size = 16
        
        # Cache for embeddings (optional)
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.cache_enabled = True
        self.max_cache_size = 10000
    
    async def initialize(self) -> bool:
        """
        Initialize the BGE-M3 model.
        
        Returns:
            True if initialization successful, False otherwise
        """
        
        if not BGE_AVAILABLE:
            self.logger.error("FlagEmbedding not available. Please install: pip install FlagEmbedding")
            return False
        
        try:
            self.logger.info(f"Loading BGE-M3 model: {self.model_name}")
            
            # Initialize model in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                self._load_model
            )
            
            self.logger.info("BGE-M3 model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BGE-M3 model: {str(e)}")
            return False
    
    def _load_model(self) -> BGEM3FlagModel:
        """Load the BGE-M3 model (blocking operation)."""
        return BGEM3FlagModel(
            self.model_name,
            use_fp16=self.use_fp16,
            device='cpu'  # Use CPU for stability, change to 'cuda' if GPU available
        )
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        
        if not self.model:
            raise RuntimeError("BGE-M3 model not initialized")
        
        # Check cache first
        if self.cache_enabled and text in self.embedding_cache:
            return self.embedding_cache[text].tolist()
        
        try:
            # Truncate if text is too long
            if len(text) > self.max_length:
                text = text[:self.max_length-10] + "..."
                self.logger.warning(f"Text truncated to {self.max_length} characters")
            
            # Generate embedding in executor to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self._generate_embedding,
                text
            )
            
            # Cache the result
            if self.cache_enabled:
                self._update_cache(text, embedding)
            
            return embedding.tolist()
            
        except Exception as e:
            self.logger.error(f"Failed to generate embedding for text: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.dimension
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        
        if not self.model:
            raise RuntimeError("BGE-M3 model not initialized")
        
        if not texts:
            return []
        
        try:
            # Process in batches for memory efficiency
            all_embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                
                # Check cache for batch items
                batch_embeddings = []
                uncached_texts = []
                uncached_indices = []
                
                for j, text in enumerate(batch_texts):
                    if self.cache_enabled and text in self.embedding_cache:
                        batch_embeddings.append(self.embedding_cache[text])
                    else:
                        uncached_texts.append(text)
                        uncached_indices.append(j)
                        batch_embeddings.append(None)  # Placeholder
                
                # Generate embeddings for uncached texts
                if uncached_texts:
                    loop = asyncio.get_event_loop()
                    new_embeddings = await loop.run_in_executor(
                        None,
                        self._generate_batch_embeddings,
                        uncached_texts
                    )
                    
                    # Fill in the placeholders
                    for idx, embedding in zip(uncached_indices, new_embeddings):
                        batch_embeddings[idx] = embedding
                        
                        # Cache new embeddings
                        if self.cache_enabled:
                            self._update_cache(batch_texts[idx], embedding)
                
                # Convert to list format
                batch_results = [emb.tolist() for emb in batch_embeddings]
                all_embeddings.extend(batch_results)
            
            self.logger.info(f"Generated embeddings for {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            self.logger.error(f"Failed to generate batch embeddings: {str(e)}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimension for _ in texts]
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate single embedding (blocking operation)."""
        embeddings = self.model.encode([text])
        return embeddings[0]
    
    def _generate_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate batch embeddings (blocking operation)."""
        # Truncate long texts
        processed_texts = []
        for text in texts:
            if len(text) > self.max_length:
                text = text[:self.max_length-10] + "..."
            processed_texts.append(text)
        
        embeddings = self.model.encode(processed_texts)
        return [emb for emb in embeddings]
    
    def _update_cache(self, text: str, embedding: np.ndarray):
        """Update embedding cache with size limit."""
        
        if len(self.embedding_cache) >= self.max_cache_size:
            # Remove oldest entries (simple FIFO)
            oldest_key = next(iter(self.embedding_cache))
            del self.embedding_cache[oldest_key]
        
        self.embedding_cache[text] = embedding
    
    async def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        
        try:
            # Generate embeddings
            emb1 = await self.embed_text(text1)
            emb2 = await self.embed_text(text2)
            
            # Calculate cosine similarity
            emb1_np = np.array(emb1)
            emb2_np = np.array(emb2)
            
            similarity = np.dot(emb1_np, emb2_np) / (
                np.linalg.norm(emb1_np) * np.linalg.norm(emb2_np)
            )
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity: {str(e)}")
            return 0.0
    
    async def shutdown(self):
        """Cleanup resources."""
        
        if self.model:
            # Clear model from memory
            self.model = None
            
        # Clear cache
        self.embedding_cache.clear()
        
        self.logger.info("BGE-M3 embedding service shutdown")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "max_length": self.max_length,
            "cache_enabled": self.cache_enabled,
            "cache_size": len(self.embedding_cache),
            "is_initialized": self.model is not None,
            "bge_available": BGE_AVAILABLE
        }


class FallbackEmbedding:
    """Fallback embedding service when BGE-M3 is not available."""
    
    def __init__(self):
        self.dimension = 768  # Keep compatible dimension
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        self.logger.warning("Using fallback embedding service")
        return True
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate mock embedding (same as original MockEmbedding)."""
        hash_val = hash(text)
        np.random.seed(abs(hash_val) % 2**32)
        vector = np.random.normal(0, 1, self.dimension)
        return (vector / np.linalg.norm(vector)).tolist()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(text) for text in texts]
    
    async def get_similarity(self, text1: str, text2: str) -> float:
        emb1 = await self.embed_text(text1)
        emb2 = await self.embed_text(text2)
        emb1_np = np.array(emb1)
        emb2_np = np.array(emb2)
        return float(np.dot(emb1_np, emb2_np) / (np.linalg.norm(emb1_np) * np.linalg.norm(emb2_np)))
    
    async def shutdown(self):
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": "fallback",
            "dimension": self.dimension,
            "is_fallback": True
        }


def create_embedding_service() -> "Union[BGEM3Embedding, FallbackEmbedding]":
    """Factory function to create appropriate embedding service."""
    
    if BGE_AVAILABLE:
        return BGEM3Embedding()
    else:
        return FallbackEmbedding()