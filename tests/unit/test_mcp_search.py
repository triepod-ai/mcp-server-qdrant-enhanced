#!/usr/bin/env python3
"""
Test search functionality on the documents we just wrote
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from mcp_server_qdrant.enhanced_settings import EnhancedQdrantSettings, EnhancedEmbeddingProviderSettings

async def test_search():
    settings = EnhancedQdrantSettings()
    embedding_settings = EnhancedEmbeddingProviderSettings()
    connector = EnhancedQdrantConnector(settings, embedding_settings)

    target_collection = "stress_test_collection"

    search_queries = [
        "CUDA acceleration",
        "MCP SDK 1.14.1",
        "performance optimization",
        "multi-vector support"
    ]

    print(f"Testing search on collection '{target_collection}' (1005 points)")
    print("=" * 60)

    for query in search_queries:
        try:
            results = await connector.search(
                query=query,
                collection_name=target_collection,
                limit=2
            )

            print(f"Query: '{query}'")
            print(f"  Found {len(results)} results:")

            for i, result in enumerate(results, 1):
                # Handle different result formats
                if hasattr(result, 'payload') and hasattr(result, 'score'):
                    content = result.payload.get('content', 'N/A')[:80] + "..."
                    score = result.score
                    metadata = result.payload.get('metadata', {})
                else:
                    content = str(result)[:80] + "..."
                    score = "N/A"
                    metadata = {}

                print(f"    {i}. Score: {score:.3f}" if score != "N/A" else f"    {i}. Score: {score}")
                print(f"       Content: {content}")
                if metadata:
                    print(f"       Test Type: {metadata.get('test_type', 'N/A')}")

        except Exception as e:
            print(f"Query: '{query}' - Error: {e}")

        print()

if __name__ == "__main__":
    asyncio.run(test_search())