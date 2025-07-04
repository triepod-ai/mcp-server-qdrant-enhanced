"""
Enhanced settings that support multiple embedding models and vector dimensions.
"""
from typing import Dict, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from mcp_server_qdrant.embeddings.types import EmbeddingProviderType

# Predefined embedding model configurations based on actual FastEmbed models
EMBEDDING_MODEL_CONFIGS = {
    # Legal analysis - high complexity (using largest available model)
    "bge-large-en-v1.5": {
        "dimensions": 1024,
        "vector_name": "bge-large-en-v1.5",
        "provider": EmbeddingProviderType.FASTEMBED,
        "fastembed_model": "BAAI/bge-large-en-v1.5"
    },
    
    # Workplace documentation - medium complexity  
    "bge-base-en-v1.5": {
        "dimensions": 768,
        "vector_name": "bge-base-en-v1.5",
        "provider": EmbeddingProviderType.FASTEMBED,
        "fastembed_model": "BAAI/bge-base-en-v1.5"
    },
    
    # Comprehensive analysis - medium-high complexity
    "bge-base-en": {
        "dimensions": 768,
        "vector_name": "bge-base-en",
        "provider": EmbeddingProviderType.FASTEMBED,
        "fastembed_model": "BAAI/bge-base-en"
    },
    
    # Technical solutions - standard (384D MiniLM for efficiency)
    "all-minilm-l6-v2": {
        "dimensions": 384,
        "vector_name": "all-minilm-l6-v2",
        "provider": EmbeddingProviderType.FASTEMBED,
        "fastembed_model": "sentence-transformers/all-MiniLM-L6-v2"
    }
}

# Collection-specific embedding model mappings - CORRECTED with proper high-dimension models
COLLECTION_MODEL_MAPPINGS = {
    # High-dimensional models (1024D) - Complex analysis requiring maximum precision
    "legal_analysis": "bge-large-en-v1.5",  # 1024D - complex legal document analysis
    "lodestar_legal_analysis": "bge-large-en-v1.5",  # 1024D - backward compatibility
    
    # Medium-dimensional models (768D) - Knowledge-intensive content
    "workplace_documentation": "bge-base-en-v1.5",  # 768D - business and workplace documents
    "lodestar_workplace_documentation": "bge-base-en-v1.5",  # 768D - backward compatibility
    "lessons_learned": "bge-base-en",  # 768D - comprehensive analysis
    "resume_projects": "bge-base-en",  # 768D - career content benefits from precision
    "job_search": "bge-base-en",  # 768D - strategic career content
    "mcp-optimization-knowledge": "bge-base-en",  # 768D - comprehensive technical knowledge
    "project_achievements": "bge-base-en",  # 768D - career-focused accomplishments
    "project_documentation": "bge-base-en",  # 768D - cross-project documentation discovery
    "cross_project_todos": "bge-base-en",  # 768D - semantic task similarity for deduplication
    "contextual_knowledge": "bge-base-en",  # 768D - comprehensive contextual knowledge analysis
    "triepod-documentation": "bge-base-en",  # 768D - project documentation with semantic search
    "development_patterns": "bge-base-en",  # 768D - comprehensive development pattern analysis
    "claude_code_documentation": "bge-base-en",  # 768D - comprehensive Claude Code documentation analysis
    "technical_documentation": "bge-large-en-v1.5",  # 1024D - complex technical documentation analysis
    
    # Low-dimensional models (384D) - Technical/debug content prioritizing speed
    "working_solutions": "all-minilm-l6-v2",  # 384D - efficient for technical solutions
    "debugging_patterns": "all-minilm-l6-v2",  # 384D - efficient for debug patterns
    "development_solutions": "all-minilm-l6-v2",  # 384D - quick technical solutions
    "troubleshooting": "all-minilm-l6-v2",  # 384D - general troubleshooting and technical issues
    
    # Legacy collections (backward compatibility)
    "lodestar_troubles": "all-minilm-l6-v2"  # 384D - backward compatibility
}

# Collection name aliases for backward compatibility and user-friendly naming
COLLECTION_ALIASES = {
    # Legacy lodestar names -> generic names
    "lodestar_legal_analysis": "legal_analysis",
    "lodestar_workplace_documentation": "workplace_documentation",
    "lodestar_troubles": "troubleshooting",
    
    # Common alternative names -> standard names
    "legal_docs": "legal_analysis",
    "legal_documents": "legal_analysis",
    "workplace_docs": "workplace_documentation",
    "business_docs": "workplace_documentation",
    "tech_troubleshooting": "troubleshooting",
    "technical_issues": "troubleshooting",
}


class EnhancedEmbeddingProviderSettings(BaseSettings):
    """
    Enhanced configuration for embedding providers with multi-model support.
    """

    provider_type: EmbeddingProviderType = Field(
        default=EmbeddingProviderType.FASTEMBED,
        validation_alias="EMBEDDING_PROVIDER",
    )
    
    # Default model for backward compatibility
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )
    
    # Collection-specific model mappings (JSON string)
    collection_model_mappings: str = Field(
        default="{}",
        validation_alias="COLLECTION_MODEL_MAPPINGS",
    )
    
    # Custom model configurations (JSON string)
    custom_model_configs: str = Field(
        default="{}",
        validation_alias="CUSTOM_MODEL_CONFIGS",
    )

    @field_validator('collection_model_mappings', 'custom_model_configs')
    @classmethod
    def parse_json_fields(cls, v: str) -> str:
        """Validate that JSON fields are properly formatted."""
        if v and v != "{}":
            import json
            try:
                json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        return v

    def get_model_config_for_collection(self, collection_name: str) -> Dict[str, Union[str, int]]:
        """
        Get the embedding model configuration for a specific collection.
        
        :param collection_name: Name of the collection
        :return: Model configuration dict with dimensions, vector_name, etc.
        """
        import json
        
        # Resolve collection name through aliases for backward compatibility
        resolved_collection_name = COLLECTION_ALIASES.get(collection_name, collection_name)
        
        # Parse collection mappings from settings
        collection_mappings = {}
        if self.collection_model_mappings and self.collection_model_mappings != "{}":
            collection_mappings = json.loads(self.collection_model_mappings)
        
        # Merge with default mappings
        all_mappings = {**COLLECTION_MODEL_MAPPINGS, **collection_mappings}
        
        # Parse custom configs from settings  
        custom_configs = {}
        if self.custom_model_configs and self.custom_model_configs != "{}":
            custom_configs = json.loads(self.custom_model_configs)
            
        # Merge with default configs
        all_configs = {**EMBEDDING_MODEL_CONFIGS, **custom_configs}
        
        # Find model for collection (try both original and resolved names)
        model_name = all_mappings.get(resolved_collection_name) or all_mappings.get(collection_name)
        if not model_name:
            # Fall back to default model
            return {
                "dimensions": 384,
                "vector_name": "all-minilm-l6-v2", 
                "provider": EmbeddingProviderType.FASTEMBED,
                "fastembed_model": self.model_name
            }
            
        # Get config for model
        config = all_configs.get(model_name)
        if not config:
            raise ValueError(f"No configuration found for model: {model_name}")
            
        return config

    def get_fastembed_model_for_collection(self, collection_name: str) -> str:
        """Get the FastEmbed model name for a collection."""
        config = self.get_model_config_for_collection(collection_name)
        return config.get("fastembed_model", self.model_name)
        
    def get_vector_name_for_collection(self, collection_name: str) -> str:
        """Get the vector name for a collection."""
        config = self.get_model_config_for_collection(collection_name)
        return config.get("vector_name", "all-minilm-l6-v2")
        
    def get_dimensions_for_collection(self, collection_name: str) -> int:
        """Get the vector dimensions for a collection."""
        config = self.get_model_config_for_collection(collection_name)
        return config.get("dimensions", 384)


class EnhancedQdrantSettings(BaseSettings):
    """
    Enhanced Qdrant settings with collection-specific configurations.
    """

    location: Optional[str] = Field(default=None, validation_alias="QDRANT_URL")
    api_key: Optional[str] = Field(default=None, validation_alias="QDRANT_API_KEY")
    collection_name: Optional[str] = Field(
        default=None, validation_alias="COLLECTION_NAME"
    )
    local_path: Optional[str] = Field(
        default=None, validation_alias="QDRANT_LOCAL_PATH"
    )
    search_limit: int = Field(default=10, validation_alias="QDRANT_SEARCH_LIMIT")
    read_only: bool = Field(default=False, validation_alias="QDRANT_READ_ONLY")
    
    # Enhanced: Auto-create collections with optimal configurations
    auto_create_collections: bool = Field(
        default=True, validation_alias="QDRANT_AUTO_CREATE_COLLECTIONS"
    )
    
    # Enhanced: Default quantization settings for memory optimization
    enable_quantization: bool = Field(
        default=True, validation_alias="QDRANT_ENABLE_QUANTIZATION"
    )
    
    # Enhanced: HNSW parameters for performance tuning
    hnsw_ef_construct: int = Field(default=200, validation_alias="QDRANT_HNSW_EF_CONSTRUCT")
    hnsw_m: int = Field(default=16, validation_alias="QDRANT_HNSW_M")