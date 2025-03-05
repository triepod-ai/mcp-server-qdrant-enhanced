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
