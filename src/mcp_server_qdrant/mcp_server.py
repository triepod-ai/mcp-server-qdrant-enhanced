"""
Enhanced MCP server with collection-specific embedding models and optimized configurations.
"""
import json
import logging
from datetime import datetime
from typing import Any, List, Dict
from mcp.server.fastmcp import Context, FastMCP
from mcp_server_qdrant.enhanced_qdrant import Entry, Metadata, EnhancedQdrantConnector
from mcp_server_qdrant.enhanced_settings import (
    EnhancedEmbeddingProviderSettings,
    EnhancedQdrantSettings,
)
from mcp_server_qdrant.settings import ToolSettings

logger = logging.getLogger(__name__)


class QdrantMCPServer(FastMCP):
    """
    Enhanced MCP server for Qdrant with collection-specific embedding models.
    """

    def __init__(
        self,
        tool_settings: ToolSettings,
        qdrant_settings: EnhancedQdrantSettings,
        embedding_provider_settings: EnhancedEmbeddingProviderSettings,
        name: str = "mcp-server-qdrant",
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
            information: str,
            collection_name: str,
            metadata: Metadata = None,  # type: ignore
        ) -> str:
            """
            Store information in Qdrant with collection-specific embedding model.
            
            :param ctx: The context for the request.
            :param information: The information to store.
            :param collection_name: The name of the collection to store in.
            :param metadata: JSON metadata to store with the information, optional.
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
            query: str,
            collection_name: str,
            limit: int = 10,
            score_threshold: float = 0.0
        ) -> Dict[str, Any]:
            """
            Find memories in Qdrant with structured results.
            
            Returns structured data instead of formatted strings for better programmatic use.
            
            :param ctx: The context for the request.
            :param query: The query to use for the search.
            :param collection_name: The name of the collection to search in.
            :param limit: Maximum number of results to return.
            :param score_threshold: Minimum relevance score.
            :return: Structured search results with metadata.
            """
            await ctx.debug(f"Enhanced searching in collection {collection_name} for: {query}")
            
            try:
                # Execute enhanced search
                search_results = await self.qdrant_connector.search(
                    query=query,
                    collection_name=collection_name,
                    limit=limit,
                    score_threshold=score_threshold
                )
                
                if not search_results:
                    return {
                        "query": query,
                        "collection": collection_name,
                        "results": [],
                        "total_found": 0,
                        "message": f"No information found for query '{query}' in collection {collection_name}"
                    }
                
                # Convert to structured response
                results_data = []
                for result in search_results:
                    results_data.append({
                        "content": result.content,
                        "score": round(result.score, 4),
                        "metadata": result.metadata or {},
                        "collection": result.collection_name,
                        "vector_model": result.vector_name
                    })
                
                return {
                    "query": query,
                    "collection": collection_name,
                    "results": results_data,
                    "total_found": len(results_data),
                    "search_params": {
                        "limit": limit,
                        "score_threshold": score_threshold
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                error_msg = f"Search failed: {str(e)}"
                logger.error(f"qdrant_find error: {error_msg}")
                
                return {
                    "query": query,
                    "collection": collection_name,
                    "results": [],
                    "total_found": 0,
                    "error": error_msg,
                    "timestamp": datetime.utcnow().isoformat()
                }

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

        async def qdrant_collection_info(ctx: Context, collection_name: str) -> str:
            """
            Get detailed information about a specific collection.
            
            :param ctx: The context for the request.
            :param collection_name: Name of the collection to inspect.
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

        async def qdrant_bulk_store(
            ctx: Context,
            documents: List[str],
            collection_name: str,
            metadata_list: List[Metadata] = None,  # type: ignore
            batch_size: int = 100
        ) -> Dict[str, Any]:
            """
            Store multiple documents efficiently in Qdrant with collection-specific embedding.
            
            :param ctx: The context for the request.
            :param documents: List of documents to store.
            :param collection_name: The name of the collection to store in.
            :param metadata_list: Optional list of metadata dicts (must match documents length).
            :param batch_size: Number of documents to process in each batch.
            :return: Storage results with statistics.
            """
            await ctx.debug(f"Bulk storing {len(documents)} documents in collection {collection_name}")
            
            if metadata_list and len(metadata_list) != len(documents):
                raise ValueError("metadata_list length must match documents length")
            
            # Create entries from documents and metadata
            entries = []
            for i, document in enumerate(documents):
                metadata = metadata_list[i] if metadata_list else None
                entries.append(Entry(content=document, metadata=metadata))
            
            # Execute bulk store operation
            result = await self.qdrant_connector.bulk_store(
                entries=entries,
                collection_name=collection_name,
                batch_size=batch_size
            )
            
            # Add operation context to result
            result.update({
                "operation": "bulk_store",
                "requested_documents": len(documents),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return result

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

        # Register tools with enhanced descriptions
        self.tool(
            description="Store information in Qdrant with automatic collection-specific embedding model selection."
        )(qdrant_store)
        
        self.tool(
            description="Store multiple documents efficiently in Qdrant with collection-specific embedding models and batch processing."
        )(qdrant_bulk_store)
        
        self.tool(
            description="Search for information in Qdrant using collection-specific embedding model with structured results."
        )(qdrant_find)
        
        self.tool(
            description="List all Qdrant collections with their configurations and model information."
        )(qdrant_list_collections)
        
        self.tool(
            description="Get detailed information about a specific Qdrant collection."
        )(qdrant_collection_info)
        
        self.tool(
            description="Show current collection-to-model mappings and available configurations."
        )(qdrant_model_mappings)