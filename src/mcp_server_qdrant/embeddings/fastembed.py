from typing import List
import asyncio
from fastembed import TextEmbedding

from .base import EmbeddingProvider


class FastEmbedProvider(EmbeddingProvider):
    """FastEmbed implementation of the embedding provider."""

    def __init__(self, model_name: str):
        """
        Initialize the FastEmbed provider.

        :param model_name: The name of the FastEmbed model to use.
        """
        self.model_name = model_name
        self.embedding_model = TextEmbedding(model_name)

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents into vectors."""
        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self.embedding_model.passage_embed(documents))
        )
        return [embedding.tolist() for embedding in embeddings]

    async def embed_query(self, query: str) -> List[float]:
        """Embed a query into a vector."""
        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self.embedding_model.query_embed([query]))
        )
        return embeddings[0].tolist()
