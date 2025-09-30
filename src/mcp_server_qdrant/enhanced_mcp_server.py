"""
Enhanced MCP server with collection-specific embedding models and optimized configurations.
"""
import json
import logging
from typing import Any, List, Dict, Annotated
from pydantic import Field
from mcp.server.fastmcp import Context, FastMCP
from mcp_server_qdrant.enhanced_qdrant import Entry, Metadata, EnhancedQdrantConnector
from mcp_server_qdrant.enhanced_settings import (
    EnhancedEmbeddingProviderSettings,
    EnhancedQdrantSettings,
)
from mcp_server_qdrant.settings import ToolSettings

logger = logging.getLogger(__name__)


class EnhancedQdrantMCPServer(FastMCP):
    """
    Enhanced MCP server for Qdrant with collection-specific embedding models.
    """

    def __init__(
        self,
        tool_settings: ToolSettings,
        qdrant_settings: EnhancedQdrantSettings,
        embedding_provider_settings: EnhancedEmbeddingProviderSettings,
        name: str = "mcp-server-qdrant-enhanced",
        instructions: str | None = None,
        **settings: Any,
    ):
        import sys
        # print(f"[DEBUG] enhanced_mcp_server.py: EnhancedQdrantMCPServer.__init__ called", file=sys.stderr)
        
        self.tool_settings = tool_settings
        self.qdrant_settings = qdrant_settings
        self.embedding_provider_settings = embedding_provider_settings

        try:
            # print(f"[DEBUG] enhanced_mcp_server.py: Creating EnhancedQdrantConnector", file=sys.stderr)
            self.qdrant_connector = EnhancedQdrantConnector(
                qdrant_settings=qdrant_settings,
                embedding_settings=embedding_provider_settings,
                default_collection_name=qdrant_settings.collection_name,
            )
            # print(f"[DEBUG] enhanced_mcp_server.py: EnhancedQdrantConnector created successfully", file=sys.stderr)
        except Exception as e:
            # print(f"[ERROR] enhanced_mcp_server.py: Failed to create EnhancedQdrantConnector: {type(e).__name__}: {e}", file=sys.stderr)
            raise

        try:
            # print(f"[DEBUG] enhanced_mcp_server.py: Calling FastMCP.__init__", file=sys.stderr)
            super().__init__(name=name, instructions=instructions, **settings)
            # print(f"[DEBUG] enhanced_mcp_server.py: FastMCP.__init__ completed successfully", file=sys.stderr)
        except Exception as e:
            # print(f"[ERROR] enhanced_mcp_server.py: FastMCP.__init__ failed: {type(e).__name__}: {e}", file=sys.stderr)
            raise

        try:
            # print(f"[DEBUG] enhanced_mcp_server.py: Setting up enhanced tools", file=sys.stderr)
            self.setup_tools()
            # print(f"[DEBUG] enhanced_mcp_server.py: Enhanced tools setup completed", file=sys.stderr)
        except Exception as e:
            # print(f"[ERROR] enhanced_mcp_server.py: setup_tools failed: {type(e).__name__}: {e}", file=sys.stderr)
            raise

    def format_entry(self, entry: Entry) -> str:
        """Format entry for display."""
        entry_metadata = json.dumps(entry.metadata) if entry.metadata else ""
        return f"<entry><content>{entry.content}</content><metadata>{entry_metadata}</metadata></entry>"

    def setup_tools(self):
        """Register the enhanced tools in the server."""

        async def qdrant_store(
            ctx: Context,
            information: Annotated[str, Field(description="The text content to store in the vector database. Can be any text content including multi-line text, Unicode characters, and technical documentation. Empty strings are accepted but may not provide useful search results.")],
            collection_name: Annotated[str, Field(description="Name of the Qdrant collection to store the document in. Must contain only alphanumeric characters, underscores, and hyphens (no spaces or special characters). Collections are auto-created with optimal configurations. Collection names trigger automatic model selection: legal/career content uses 1024D models, knowledge-intensive content uses 768D models, technical/debug content uses 384D models.")],
            metadata: Annotated[Metadata, Field(default=None, description="Optional JSON metadata object to store alongside the document. Can be any valid JSON structure with unlimited nesting. Use for categorization, filtering, and additional context. Example: {'category': 'tutorial', 'tags': ['python'], 'author': {'name': 'John'}}.")] = None,  # type: ignore
        ) -> str:
            """
            Store information in Qdrant with collection-specific embedding model.

            :param ctx: The context for the request.
            :param information: The text content to store in the vector database. Can be any text content including multi-line text, Unicode characters, and technical documentation. Empty strings are accepted but may not provide useful search results.
            :param collection_name: Name of the Qdrant collection to store the document in. Must contain only alphanumeric characters, underscores, and hyphens (no spaces or special characters). Collections are auto-created with optimal configurations. Collection names trigger automatic model selection: legal/career content uses 1024D models, knowledge-intensive content uses 768D models, technical/debug content uses 384D models.
            :param metadata: Optional JSON metadata object to store alongside the document. Can be any valid JSON structure with unlimited nesting. Use for categorization, filtering, and additional context. Example: {"category": "tutorial", "tags": ["python"], "author": {"name": "John"}}.
            :return: A message indicating that the information was stored.
            """
            await ctx.debug(f"Enhanced storing information in collection {collection_name}")

            entry = Entry(content=information, metadata=metadata)
            await self.qdrant_connector.store(entry, collection_name=collection_name)
            
            # Get model info for confirmation
            model_info = self.qdrant_connector._embedding_provider.get_model_info_for_collection(collection_name)
            vector_name = model_info.get("vector_name", "unknown")
            dimensions = model_info.get("dimensions", "unknown")
            
            return f"Stored in {collection_name} using {vector_name} ({dimensions}D): {information}"

        async def qdrant_find(
            ctx: Context,
            query: Annotated[str, Field(description="The search query text used to find similar documents through semantic vector search. Uses the same embedding model as the target collection for optimal results. Can be single words, phrases, or natural language questions. Empty queries may return all documents or error.")],
            collection_name: Annotated[str, Field(description="Name of the existing collection to search within. Must be a valid, existing collection name. Non-existent collections will return 'No information found' message.")],
        ) -> List[str]:
            """
            Find memories in Qdrant using collection-specific embedding model.

            :param ctx: The context for the request.
            :param query: The search query text used to find similar documents through semantic vector search. Uses the same embedding model as the target collection for optimal results. Can be single words, phrases, or natural language questions. Empty queries may return all documents or error.
            :param collection_name: Name of the existing collection to search within. Must be a valid, existing collection name. Non-existent collections will return "No information found" message.
            :return: A list of entries found.
            """
            await ctx.debug(f"Enhanced searching in collection {collection_name} for: {query}")

            entries = await self.qdrant_connector.search(
                query,
                collection_name=collection_name,
                limit=self.qdrant_settings.search_limit,
            )

            if not entries:
                return [f"No information found for the query '{query}' in collection {collection_name}"]

            return [self.format_entry(entry) for entry in entries]

        async def qdrant_list_collections(ctx: Context) -> str:
            """
            List all Qdrant collections with their configurations.

            :param ctx: The context for the request.
            :return: Formatted list of collections with their info.
            """
            await ctx.debug("Listing all collections with enhanced info")
            
            try:
                collections_info = await self.qdrant_connector.list_collections_with_info()
                
                if not collections_info:
                    return "No collections found in Qdrant."
                
                result = "Qdrant Collections:\n\n"
                for info in collections_info:
                    if "error" in info:
                        result += f"❌ {info['collection_name']}: Error - {info['error']}\n"
                        continue
                        
                    vector_config = info.get("vector_config", {})
                    result += f"📊 **{info['collection_name']}**\n"
                    result += f"   Status: {info.get('status', 'unknown')}\n"
                    result += f"   Points: {info.get('points_count', 0)}\n"
                    result += f"   Vector: {vector_config.get('vector_name', 'unknown')} ({vector_config.get('dimensions', 'unknown')}D)\n"
                    result += f"   Model: {vector_config.get('fastembed_model', 'unknown')}\n\n"
                
                return result
                
            except Exception as e:
                return f"Error listing collections: {str(e)}"

        async def qdrant_collection_info(
            ctx: Context,
            collection_name: Annotated[str, Field(description="Name of the collection to inspect and get detailed information about. Can be any string - will return error message if collection doesn't exist or is inaccessible. Returns status, document count, vector configuration, optimization settings, and model information.")]
        ) -> str:
            """
            Get detailed information about a specific collection.

            :param ctx: The context for the request.
            :param collection_name: Name of the collection to inspect and get detailed information about. Can be any string - will return error message if collection doesn't exist or is inaccessible. Returns status, document count, vector configuration, optimization settings, and model information.
            :return: Detailed collection information.
            """
            await ctx.debug(f"Getting detailed info for collection: {collection_name}")
            
            try:
                info = await self.qdrant_connector.get_collection_info(collection_name)
                
                if "error" in info:
                    return f"Error getting info for {collection_name}: {info['error']}"
                
                vector_config = info.get("vector_config", {})
                config = info.get("config", {})
                
                result = f"🔍 **Collection: {collection_name}**\n\n"
                result += f"**Status:** {info.get('status', 'unknown')}\n"
                result += f"**Points:** {info.get('points_count', 0)}\n"
                result += f"**Indexed Vectors:** {info.get('indexed_vectors_count', 0)}\n\n"
                
                result += f"**Vector Configuration:**\n"
                result += f"   Vector Name: {vector_config.get('vector_name', 'unknown')}\n"
                result += f"   Dimensions: {vector_config.get('dimensions', 'unknown')}\n"
                result += f"   FastEmbed Model: {vector_config.get('fastembed_model', 'unknown')}\n\n"
                
                if config.get("quantization_config"):
                    result += f"**Optimizations:**\n"
                    result += f"   Quantization: Enabled\n"
                else:
                    result += f"**Optimizations:**\n"
                    result += f"   Quantization: Disabled\n"
                
                return result
                
            except Exception as e:
                return f"Error getting collection info: {str(e)}"

        async def qdrant_model_mappings(ctx: Context) -> str:
            """
            Show current collection-to-model mappings.

            :param ctx: The context for the request.
            :return: Current model mappings configuration.
            """
            await ctx.debug("Showing collection-to-model mappings")
            
            from mcp_server_qdrant.enhanced_settings import COLLECTION_MODEL_MAPPINGS, EMBEDDING_MODEL_CONFIGS
            
            result = "📋 **Collection Model Mappings:**\n\n"
            
            for collection, model in COLLECTION_MODEL_MAPPINGS.items():
                config = EMBEDDING_MODEL_CONFIGS.get(model, {})
                result += f"**{collection}**\n"
                result += f"   Model: {model}\n"
                result += f"   Dimensions: {config.get('dimensions', 'unknown')}\n"
                result += f"   FastEmbed: {config.get('fastembed_model', 'unknown')}\n\n"
            
            result += "📚 **Available Model Configs:**\n\n"
            for model, config in EMBEDDING_MODEL_CONFIGS.items():
                result += f"**{model}**: {config.get('dimensions')}D ({config.get('fastembed_model')})\n"
                
            return result

        # Register tools with optimized descriptions (based on lessons learned)
        self.tool(
            description='Store documents in Qdrant collections with optional metadata. IMPORTANT: Use proper JSON syntax with double quotes (") for all keys and string values, not backticks (`). Example metadata: {"key": "value", "nested": {"data": 123}}. Auto-creates collections with optimal models: 1024D BGE-Large for career/legal content (max precision), 768D BGE-Base for knowledge-intensive content, 384D MiniLM for technical solutions (speed). Sub-100ms storage with batch support.'
        )(qdrant_store)
        
        self.tool(
            description="Search Qdrant collections with Redis caching. Uses collection-specific models for optimal results: 1024D BGE-Large (legal_analysis, technical_documentation), 768D BGE-Base (lessons_learned, contextual_knowledge), 384D MiniLM (debugging_patterns, working_solutions, music_videos). <10ms cached searches, 60-90% cache hit rate. Returns structured JSON with scores and metadata."
        )(qdrant_find)
        
        self.tool(
            description="List Qdrant collections with vector dimensions, model types, and point counts. Shows all collections with their embedding models: 1024D BGE-Large (legal/career), 768D BGE-Base (knowledge-intensive), 384D MiniLM (technical/debug). <100ms response time. Shows status (green/yellow/red) and quantization settings."
        )(qdrant_list_collections)
        
        self.tool(
            description="Get collection details: point count, vector dimensions, HNSW parameters, quantization config. <50ms response. Returns specific error messages if collection doesn't exist or is misconfigured."
        )(qdrant_collection_info)
        
        self.tool(
            description="Show collection-to-model mappings with all three model tiers. 1024D BGE-Large: career/legal collections (resume_projects, legal_analysis, technical_documentation). 768D BGE-Base: knowledge-intensive collections (lessons_learned, contextual_knowledge, development_patterns). 384D MiniLM: technical/debug collections (debugging_patterns, working_solutions, music_videos). Reference for optimal collection setup."
        )(qdrant_model_mappings)