from mcp_server_qdrant.embeddings import EmbeddingProvider


def create_embedding_provider(provider_type: str, **kwargs) -> EmbeddingProvider:
    """
    Create an embedding provider based on the specified type.

    :param provider_type: The type of embedding provider to create.
    :param kwargs: Additional arguments to pass to the provider constructor.
    :return: An instance of the specified embedding provider.
    """
    if provider_type.lower() == "fastembed":
        from .fastembed import FastEmbedProvider
        model_name = kwargs.get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
        return FastEmbedProvider(model_name)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider_type}")
from typing import Optional
from .fastembed import FastEmbedProvider
from .base import EmbeddingProvider


def create_embedding_provider(provider_type: str, model_name: Optional[str] = None) -> EmbeddingProvider:
    """
    Create an embedding provider based on the provider type.
    
    Args:
        provider_type: The type of embedding provider to create.
        model_name: The name of the model to use.
        
    Returns:
        An instance of EmbeddingProvider.
        
    Raises:
        ValueError: If the provider type is not supported.
    """
    if provider_type.lower() == "fastembed":
        return FastEmbedProvider(model_name)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider_type}")
from typing import Literal

from .fastembed import FastEmbedProvider


def create_embedding_provider(
    provider_type: Literal["fastembed"], 
    **kwargs
) -> FastEmbedProvider:
    """
    Factory function to create an embedding provider.
    
    Args:
        provider_type: The type of embedding provider to create.
        **kwargs: Additional arguments to pass to the provider constructor.
        
    Returns:
        An instance of the requested embedding provider.
        
    Raises:
        ValueError: If the provider type is not supported.
    """
    if provider_type == "fastembed":
        model_name = kwargs.get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
        return FastEmbedProvider(model_name)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider_type}")
