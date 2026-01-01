"""
Enhanced FastEmbed provider that supports collection-specific models and dimensions.
"""

import asyncio
import os
import sys
from typing import Dict, List, Optional
from fastembed import TextEmbedding
from fastembed.common.model_description import DenseModelDescription
from mcp_server_qdrant.embeddings.base import EmbeddingProvider


class EnhancedFastEmbedProvider(EmbeddingProvider):
    """
    Enhanced FastEmbed implementation that supports multiple models per collection.
    """

    def __init__(
        self,
        embedding_settings,
        default_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        # print(f"[DEBUG] enhanced_fastembed.py: EnhancedFastEmbedProvider.__init__ called", file=sys.stderr)

        self.embedding_settings = embedding_settings
        self.default_model = default_model
        self._model_cache: Dict[str, TextEmbedding] = {}
        self._current_collection: Optional[str] = None

        # Check for CUDA support
        self.use_cuda = os.getenv("FASTEMBED_CUDA", "false").lower() == "true"

        # Initialize default model with GPU support if available
        try:
            # print(f"[DEBUG] enhanced_fastembed.py: Creating default TextEmbedding with model={default_model}, cuda={self.use_cuda}", file=sys.stderr)
            self._model_cache[default_model] = self._create_text_embedding(
                default_model
            )
            # print(f"[DEBUG] enhanced_fastembed.py: Default TextEmbedding created successfully", file=sys.stderr)
        except Exception:
            # print(f"[ERROR] enhanced_fastembed.py: Failed to create default TextEmbedding: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc(file=sys.stderr)
            raise

    def set_collection_context(self, collection_name: str):
        """Set the current collection context for model selection."""
        self._current_collection = collection_name

    def _create_text_embedding(self, model_name: str) -> TextEmbedding:
        """Create TextEmbedding with GPU support if available."""
        if self.use_cuda:
            try:
                # Try CUDA providers first (don't use cuda=True when specifying providers)
                return TextEmbedding(
                    model_name,
                    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
                )
            except Exception as e:
                print(
                    f"[WARNING] CUDA initialization failed for {model_name}, falling back to CPU: {e}",
                    file=sys.stderr,
                )
                return TextEmbedding(model_name, providers=["CPUExecutionProvider"])
        else:
            return TextEmbedding(model_name, providers=["CPUExecutionProvider"])

    def _get_model_for_collection(
        self, collection_name: Optional[str] = None
    ) -> TextEmbedding:
        """Get the appropriate embedding model for a collection."""
        collection_name = collection_name or self._current_collection

        if not collection_name:
            # Use default model
            return self._model_cache[self.default_model]

        # Get model name for this collection
        fastembed_model = self.embedding_settings.get_fastembed_model_for_collection(
            collection_name
        )

        # Check if we already have this model cached
        if fastembed_model not in self._model_cache:
            try:
                print(
                    f"[DEBUG] enhanced_fastembed.py: Loading new model {fastembed_model} for collection {collection_name}",
                    file=sys.stderr,
                )
                self._model_cache[fastembed_model] = self._create_text_embedding(
                    fastembed_model
                )
                print(
                    f"[DEBUG] enhanced_fastembed.py: Model {fastembed_model} loaded successfully",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"[ERROR] enhanced_fastembed.py: Failed to load model {fastembed_model} for collection {collection_name}: {e}",
                    file=sys.stderr,
                )
                print(
                    f"[ERROR] enhanced_fastembed.py: This will cause vector name mismatch! Expected: {self.embedding_settings.get_vector_name_for_collection(collection_name)}, but using default model vector name",
                    file=sys.stderr,
                )
                # Fall back to default model but log the issue
                return self._model_cache[self.default_model]

        return self._model_cache[fastembed_model]

    async def embed_documents(
        self, documents: List[str], collection_name: Optional[str] = None
    ) -> List[List[float]]:
        """Embed a list of documents into vectors."""
        model = self._get_model_for_collection(collection_name)

        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(model.passage_embed(documents))
        )
        return [embedding.tolist() for embedding in embeddings]

    async def embed_query(
        self, query: str, collection_name: Optional[str] = None
    ) -> List[float]:
        """Embed a query into a vector."""
        model = self._get_model_for_collection(collection_name)

        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(model.query_embed([query]))
        )
        return embeddings[0].tolist()

    def get_vector_name(self, collection_name: Optional[str] = None) -> str:
        """
        Return the name of the vector for the Qdrant collection.
        """
        collection_name = collection_name or self._current_collection
        if collection_name:
            expected_vector_name = (
                self.embedding_settings.get_vector_name_for_collection(collection_name)
            )

            # Verify that the model we'll use matches the expected vector name
            try:
                model = self._get_model_for_collection(collection_name)
                actual_fastembed_model = (
                    self.embedding_settings.get_fastembed_model_for_collection(
                        collection_name
                    )
                )

                # Check if the model in cache matches what we expect
                if actual_fastembed_model not in self._model_cache:
                    print(
                        f"[WARNING] enhanced_fastembed.py: Expected model {actual_fastembed_model} not in cache for collection {collection_name}",
                        file=sys.stderr,
                    )

            except Exception as e:
                print(
                    f"[WARNING] enhanced_fastembed.py: Error verifying model for collection {collection_name}: {e}",
                    file=sys.stderr,
                )

            return expected_vector_name

        # Default behavior for backward compatibility
        model = self._get_model_for_collection(collection_name)
        model_name = model.model_name.split("/")[-1].lower()
        return f"fast-{model_name}"

    def get_vector_size(self, collection_name: Optional[str] = None) -> int:
        """Get the size of the vector for the Qdrant collection."""
        collection_name = collection_name or self._current_collection
        if collection_name:
            return self.embedding_settings.get_dimensions_for_collection(
                collection_name
            )

        # Default behavior for backward compatibility
        model = self._get_model_for_collection(collection_name)
        fastembed_model = self.embedding_settings.get_fastembed_model_for_collection(
            collection_name or ""
        )
        model_description: DenseModelDescription = model._get_model_description(
            fastembed_model
        )
        return model_description.dim

    def get_model_info_for_collection(self, collection_name: str) -> Dict[str, any]:
        """Get comprehensive model information for a collection."""
        config = self.embedding_settings.get_model_config_for_collection(
            collection_name
        )
        return {
            "collection_name": collection_name,
            "vector_name": config.get("vector_name"),
            "dimensions": config.get("dimensions"),
            "fastembed_model": config.get("fastembed_model"),
            "provider": config.get("provider"),
        }
