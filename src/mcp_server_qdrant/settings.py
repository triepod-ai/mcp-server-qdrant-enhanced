import argparse
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class EmbeddingProviderSettings(BaseSettings):
    """
    Configuration for the embedding provider.
    """

    provider_type: str = Field(
        default="fastembed", validation_alias="EMBEDDING_PROVIDER"
    )
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )


class QdrantSettings(BaseSettings):
    """
    Configuration for the Qdrant connector.
    """

    location: Optional[str] = Field(default=None, validation_alias="QDRANT_URL")
    api_key: Optional[str] = Field(default=None, validation_alias="QDRANT_API_KEY")
    collection_name: str = Field(validation_alias="COLLECTION_NAME")
    local_path: Optional[str] = Field(
        default=None, validation_alias="QDRANT_LOCAL_PATH"
    )

    def get_qdrant_location(self) -> str:
        """
        Get the Qdrant location, either the URL or the local path.
        """
        return self.location or self.local_path


def parse_args() -> Dict[str, Any]:
    """
    Parse command line arguments for the MCP server.

    Returns:
        Dict[str, Any]: Dictionary of parsed arguments
    """
    parser = argparse.ArgumentParser(description="Qdrant MCP Server")

    # Qdrant connection options
    connection_group = parser.add_mutually_exclusive_group()
    connection_group.add_argument(
        "--qdrant-url",
        help="URL of the Qdrant server, e.g. http://localhost:6333",
    )
    connection_group.add_argument(
        "--qdrant-local-path",
        help="Path to the local Qdrant database",
    )

    # Other Qdrant settings
    parser.add_argument(
        "--qdrant-api-key",
        help="API key for the Qdrant server",
    )
    parser.add_argument(
        "--collection-name",
        help="Name of the collection to use",
    )

    # Embedding settings
    parser.add_argument(
        "--embedding-provider",
        help="Embedding provider to use (currently only 'fastembed' is supported)",
    )
    parser.add_argument(
        "--embedding-model",
        help="Name of the embedding model to use",
    )

    args = parser.parse_args()

    # Convert to dictionary and filter out None values
    args_dict = {k: v for k, v in vars(args).items() if v is not None}

    # Convert argument names to environment variable format
    env_vars = {}
    if "qdrant_url" in args_dict:
        env_vars["QDRANT_URL"] = args_dict["qdrant_url"]
    if "qdrant_api_key" in args_dict:
        env_vars["QDRANT_API_KEY"] = args_dict["qdrant_api_key"]
    if "collection_name" in args_dict:
        env_vars["COLLECTION_NAME"] = args_dict["collection_name"]
    if "embedding_model" in args_dict:
        env_vars["EMBEDDING_MODEL"] = args_dict["embedding_model"]
    if "embedding_provider" in args_dict:
        env_vars["EMBEDDING_PROVIDER"] = args_dict["embedding_provider"]
    if "qdrant_local_path" in args_dict:
        env_vars["QDRANT_LOCAL_PATH"] = args_dict["qdrant_local_path"]

    return env_vars
