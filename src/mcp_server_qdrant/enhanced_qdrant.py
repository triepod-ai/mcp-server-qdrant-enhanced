"""
Enhanced Qdrant connector with collection-specific embedding models and optimized configurations.
"""
import logging
import uuid
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, validator
from qdrant_client import AsyncQdrantClient, models
from mcp_server_qdrant.embeddings.enhanced_fastembed import EnhancedFastEmbedProvider
from mcp_server_qdrant.enhanced_settings import EnhancedEmbeddingProviderSettings, EnhancedQdrantSettings
from mcp_server_qdrant.validators import validate_search_results, sanitize_query, validate_metadata

logger = logging.getLogger(__name__)

Metadata = Dict[str, Any]


class SearchResult(BaseModel):
    """Enhanced search result with score and metadata."""
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    collection_name: str
    vector_name: str
    
    @property
    def is_relevant(self) -> bool:
        """Check if result meets relevance threshold."""
        return self.score >= 0.7  # Configurable threshold


class Entry(BaseModel):
    """Enhanced entry with validation methods."""
    content: str
    metadata: Optional[Metadata] = None
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    @validator('metadata')
    def metadata_must_be_valid(cls, v):
        if v is not None and not validate_metadata(v):
            raise ValueError('Invalid metadata format')
        return v
    
    def to_search_result(self, score: float, collection_name: str, vector_name: str) -> SearchResult:
        """Convert to SearchResult with additional context."""
        return SearchResult(
            content=self.content,
            score=score,
            metadata=self.metadata,
            collection_name=collection_name,
            vector_name=vector_name
        )


class EnhancedQdrantConnector:
    """
    Enhanced Qdrant connector that supports collection-specific embedding models and optimized configurations.
    """

    def __init__(
        self,
        qdrant_settings: EnhancedQdrantSettings,
        embedding_settings: EnhancedEmbeddingProviderSettings,
        default_collection_name: Optional[str] = None,
    ):
        import sys
        # print(f"[DEBUG] enhanced_qdrant.py: EnhancedQdrantConnector.__init__ called", file=sys.stderr)
        
        self._qdrant_settings = qdrant_settings
        self._embedding_settings = embedding_settings
        self._default_collection_name = default_collection_name
        
        # Create enhanced embedding provider
        self._embedding_provider = EnhancedFastEmbedProvider(
            embedding_settings=embedding_settings,
            default_model=embedding_settings.model_name
        )
        
        try:
            # print(f"[DEBUG] enhanced_qdrant.py: Creating AsyncQdrantClient", file=sys.stderr)
            self._client = AsyncQdrantClient(
                location=qdrant_settings.location, 
                api_key=qdrant_settings.api_key, 
                path=qdrant_settings.local_path
            )
            # print(f"[DEBUG] enhanced_qdrant.py: AsyncQdrantClient created successfully", file=sys.stderr)
        except Exception as e:
            # print(f"[ERROR] enhanced_qdrant.py: Failed to create AsyncQdrantClient: {type(e).__name__}: {e}", file=sys.stderr)
            raise

    async def _ensure_connection(self) -> None:
        """Ensure Qdrant connection with retry logic."""
        max_retries = 3
        base_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                # Test connection
                collections = await self._client.get_collections()
                logger.info(f"Connected to Qdrant, found {len(collections.collections)} collections")
                return
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to Qdrant after {max_retries} attempts: {e}")
                    raise ConnectionError(f"Cannot connect to Qdrant: {e}")
                
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)

    async def get_collection_names(self) -> list[str]:
        """Get the names of all collections in the Qdrant server."""
        response = await self._client.get_collections()
        return [collection.name for collection in response.collections]

    async def store(self, entry: Entry, *, collection_name: Optional[str] = None):
        """
        Store information in the Qdrant collection with collection-specific embedding.
        """
        collection_name = collection_name or self._default_collection_name
        assert collection_name is not None
        
        # Ensure collection exists with proper configuration
        await self._ensure_collection_exists(collection_name)

        # Set collection context for embedding provider
        self._embedding_provider.set_collection_context(collection_name)

        # Embed the document using collection-specific model
        embeddings = await self._embedding_provider.embed_documents([entry.content], collection_name)

        # Get collection-specific vector name
        vector_name = self._embedding_provider.get_vector_name(collection_name)
        
        # Prepare payload
        payload = {"document": entry.content, "metadata": entry.metadata}
        
        # Store in Qdrant
        await self._client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=uuid.uuid4().hex,
                    vector={vector_name: embeddings[0]},
                    payload=payload,
                )
            ],
        )

    async def bulk_store(
        self, 
        entries: List[Entry], 
        *, 
        collection_name: Optional[str] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Store multiple entries efficiently using collection-specific embedding models.
        
        Args:
            entries: List of Entry objects to store
            collection_name: Target collection (uses default if None)
            batch_size: Number of entries to process in each batch
            
        Returns:
            Dictionary with storage results and statistics
        """
        collection_name = collection_name or self._default_collection_name
        if not collection_name:
            raise ValueError("Collection name must be specified")
            
        if not entries:
            return {"success": True, "stored_count": 0, "batch_count": 0}
        
        # Ensure collection exists with proper configuration
        await self._ensure_collection_exists(collection_name)
        
        # Set collection context for embedding provider
        self._embedding_provider.set_collection_context(collection_name)
        
        # Get collection-specific vector name
        vector_name = self._embedding_provider.get_vector_name(collection_name)
        
        total_stored = 0
        batch_count = 0
        
        # Process entries in batches
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            batch_texts = [entry.content for entry in batch]
            
            try:
                # Embed all texts in the batch using collection-specific model
                embeddings = await self._embedding_provider.embed_documents(batch_texts, collection_name)
                
                # Prepare points for batch upsert
                points = []
                for j, (entry, embedding) in enumerate(zip(batch, embeddings)):
                    payload = {"document": entry.content, "metadata": entry.metadata}
                    points.append(
                        models.PointStruct(
                            id=uuid.uuid4().hex,  # Keep using UUID for backward compatibility
                            vector={vector_name: embedding},
                            payload=payload,
                        )
                    )
                
                # Batch upsert to Qdrant
                await self._client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                
                total_stored += len(batch)
                batch_count += 1
                
            except Exception as e:
                logger.error(f"Batch {batch_count + 1} failed: {e}")
                # Continue with remaining batches rather than failing completely
                continue
        
        return {
            "success": True,
            "stored_count": total_stored,
            "batch_count": batch_count,
            "collection_name": collection_name,
            "vector_model": self._embedding_provider.get_model_info_for_collection(collection_name)
        }

    async def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.0,
        include_score: bool = True
    ) -> List[SearchResult]:
        """
        Enhanced search with structured results and filtering.
        
        Args:
            query: Search query string
            collection_name: Target collection (uses default if None)
            limit: Maximum results to return
            score_threshold: Minimum relevance score
            include_score: Whether to include similarity scores
        
        Returns:
            List of SearchResult objects with scores and metadata
        """
        # Sanitize and validate query
        query = sanitize_query(query)
        
        collection_name = collection_name or self._default_collection_name
        if not collection_name:
            raise ValueError("Collection name must be specified")
        
        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists:
            return []

        # Set collection context for embedding provider
        self._embedding_provider.set_collection_context(collection_name)

        # Embed the query using collection-specific model
        query_vector = await self._embedding_provider.embed_query(query, collection_name)
        vector_name = self._embedding_provider.get_vector_name(collection_name)

        try:
            # Execute search with retry logic
            search_results = await self._search_with_retry(
                collection_name=collection_name,
                query_vector=query_vector,
                vector_name=vector_name,
                limit=limit
            )
            
            # Validate and filter results
            validated_results = validate_search_results(search_results.points)
            
            # Convert to SearchResult objects
            structured_results = []
            for result in validated_results:
                if result.score >= score_threshold:
                    entry = Entry(
                        content=result.payload["document"],
                        metadata=result.payload.get("metadata")
                    )
                    search_result = entry.to_search_result(
                        score=result.score if include_score else 1.0,
                        collection_name=collection_name,
                        vector_name=vector_name
                    )
                    structured_results.append(search_result)
            
            # Sort by score (highest first)
            structured_results.sort(key=lambda x: x.score, reverse=True)
            
            return structured_results[:limit]
            
        except Exception as e:
            # Enhanced error handling for named vector collections
            error_msg = str(e).lower()
            if "vector name" in error_msg or "using" in error_msg:
                # Try to get collection info to provide helpful suggestions
                try:
                    collection_info = await self._client.get_collection(collection_name)
                    available_vectors = list(collection_info.config.params.vectors.keys())
                    enhanced_error = (
                        f"Collection '{collection_name}' requires explicit vector name. "
                        f"Available vectors: {available_vectors}. "
                        f"Current model uses vector name: '{vector_name}'. "
                        f"Original error: {e}"
                    )
                    logger.error(enhanced_error)
                    raise ValueError(enhanced_error)
                except Exception:
                    # Fall back to original error if introspection fails
                    pass
            
            logger.error(f"Search failed for query '{query}' in collection '{collection_name}': {e}")
            raise

    async def _search_with_retry(
        self,
        collection_name: str,
        query_vector: List[float],
        vector_name: str,
        limit: int,
        max_retries: int = 3
    ) -> Any:
        """Execute search with exponential backoff retry."""
        
        for attempt in range(max_retries):
            try:
                return await self._client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    using=vector_name,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Search attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)

    async def _ensure_collection_exists(self, collection_name: str):
        """
        Ensure collection exists with optimal configuration for its purpose.
        """
        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists and self._qdrant_settings.auto_create_collections:
            
            # Get collection-specific configuration
            vector_size = self._embedding_provider.get_vector_size(collection_name)
            vector_name = self._embedding_provider.get_vector_name(collection_name)
            
            # Determine quantization based on vector size and settings
            quantization_config = None
            if self._qdrant_settings.enable_quantization:
                if vector_size >= 1024:
                    # Use binary quantization for large vectors (32x compression)
                    quantization_config = models.BinaryQuantization(
                        binary=models.BinaryQuantizationConfig(always_ram=True)
                    )
                elif vector_size >= 512:
                    # Use scalar quantization for medium vectors (4x compression)
                    quantization_config = models.ScalarQuantization(
                        scalar=models.ScalarQuantizationConfig(
                            type=models.ScalarType.INT8,
                            always_ram=True
                        )
                    )
                # No quantization for small vectors (384 dim) to preserve accuracy

            # Determine HNSW parameters based on collection purpose
            ef_construct = self._qdrant_settings.hnsw_ef_construct
            m = self._qdrant_settings.hnsw_m
            
            # Adjust parameters for legal collections (higher precision)
            if "legal" in collection_name.lower():
                ef_construct = max(200, ef_construct)
                m = max(16, m)
            elif "solutions" in collection_name.lower() or "patterns" in collection_name.lower():
                # Optimize for speed for technical collections
                ef_construct = min(100, ef_construct)
                m = min(8, m)

            import sys
            # print(f"[DEBUG] enhanced_qdrant.py: Creating collection {collection_name} with vector_size={vector_size}, vector_name={vector_name}", file=sys.stderr)
            
            # Create collection with optimized configuration
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    vector_name: models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                        hnsw_config=models.HnswConfigDiff(
                            ef_construct=ef_construct,
                            m=m,
                        )
                    )
                },
                quantization_config=quantization_config,
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=10000,  # Lower threshold for faster indexing
                ),
            )
            
            # print(f"[DEBUG] enhanced_qdrant.py: Collection {collection_name} created successfully", file=sys.stderr)

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed information about a collection."""
        try:
            collection_info = await self._client.get_collection(collection_name)
            model_info = self._embedding_provider.get_model_info_for_collection(collection_name)
            
            return {
                "collection_name": collection_name,
                "status": collection_info.status,
                "points_count": collection_info.points_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "vector_config": model_info,
                "config": {
                    "vectors": collection_info.config.params.vectors,
                    "hnsw_config": collection_info.config.hnsw_config,
                    "quantization_config": collection_info.config.quantization_config,
                }
            }
        except Exception as e:
            return {"error": str(e), "collection_name": collection_name}

    async def list_collections_with_info(self) -> list[Dict[str, Any]]:
        """List all collections with their detailed information."""
        collection_names = await self.get_collection_names()
        collections_info = []
        
        for name in collection_names:
            info = await self.get_collection_info(name)
            collections_info.append(info)
            
        return collections_info