from mcp_server_qdrant.embeddings.base import EmbeddingProvider
from mcp_server_qdrant.embeddings.types import EmbeddingProviderType
from mcp_server_qdrant.settings import EmbeddingProviderSettings


def create_embedding_provider(settings: EmbeddingProviderSettings) -> EmbeddingProvider:
    """
    Create an embedding provider based on the specified type.
    :param settings: The settings for the embedding provider.
    :return: An instance of the specified embedding provider.
    """
    import sys
    #     print(f"[DEBUG] factory.py: create_embedding_provider called with provider_type={settings.provider_type}, model_name={settings.model_name}", file=sys.stderr)
    
    if settings.provider_type == EmbeddingProviderType.FASTEMBED:
        try:
            #             print(f"[DEBUG] factory.py: Importing FastEmbedProvider", file=sys.stderr)
            from mcp_server_qdrant.embeddings.fastembed import FastEmbedProvider
            #             print(f"[DEBUG] factory.py: Creating FastEmbedProvider with model_name={settings.model_name}", file=sys.stderr)
            provider = FastEmbedProvider(settings.model_name)
            #             print(f"[DEBUG] factory.py: FastEmbedProvider created successfully", file=sys.stderr)
            return provider
        except Exception as e:
            #             print(f"[ERROR] factory.py: Failed to create FastEmbedProvider: {type(e).__name__}: {e}", file=sys.stderr)
            raise
    else:
        raise ValueError(f"Unsupported embedding provider: {settings.provider_type}")
