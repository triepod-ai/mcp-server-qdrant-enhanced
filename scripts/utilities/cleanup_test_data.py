#!/usr/bin/env python3
"""
Cleanup Test Data Utility
Consolidated script for finding and deleting test documents from Qdrant collections
"""

import asyncio
import argparse
import sys
import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient

# Add src directory to path for enhanced connector access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from mcp_server_qdrant.enhanced_settings import EnhancedQdrantSettings, EnhancedEmbeddingProviderSettings


class TestDataCleaner:
    def __init__(self, collection_name: str = "lodestar_legal_analysis"):
        self.collection_name = collection_name
        self.client = QdrantClient(host='localhost', port=6333)

    def get_collection_info(self) -> Dict[str, Any]:
        """Get current collection statistics"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "points_count": collection_info.points_count,
                "status": "available"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def delete_by_metadata(self, test_types: List[str]) -> Dict[str, Any]:
        """
        Delete documents by test_type metadata field

        Args:
            test_types: List of test_type values to match and delete
        """
        print(f"Searching for documents with test_type in: {test_types}")
        print("=" * 60)

        initial_info = self.get_collection_info()
        initial_count = initial_info.get("points_count", 0)
        print(f"Initial collection size: {initial_count} points")

        documents_to_delete = []

        try:
            # Scroll through all points
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                with_payload=True,
                with_vectors=False
            )

            points = scroll_result[0]
            next_offset = scroll_result[1]

            # Check each point for matching metadata
            for point in points:
                if point.payload and 'metadata' in point.payload:
                    metadata = point.payload.get('metadata', {})
                    test_type = metadata.get('test_type')

                    if test_type in test_types:
                        documents_to_delete.append({
                            'id': point.id,
                            'test_type': test_type,
                            'content_preview': point.payload.get('document', '')[:100] + "..."
                        })
                        print(f"✓ Found: ID {point.id}, Type: {test_type}")

            # Continue scrolling if more pages exist
            while next_offset:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    offset=next_offset,
                    limit=100,
                    with_payload=True,
                    with_vectors=False
                )

                points = scroll_result[0]
                next_offset = scroll_result[1]

                for point in points:
                    if point.payload and 'metadata' in point.payload:
                        metadata = point.payload.get('metadata', {})
                        test_type = metadata.get('test_type')

                        if test_type in test_types:
                            documents_to_delete.append({
                                'id': point.id,
                                'test_type': test_type,
                                'content_preview': point.payload.get('document', '')[:100] + "..."
                            })
                            print(f"✓ Found: ID {point.id}, Type: {test_type}")

        except Exception as e:
            print(f"Error during scroll: {e}")
            return {"status": "error", "error": str(e)}

        print(f"\nFound {len(documents_to_delete)} test documents to delete")

        if documents_to_delete:
            point_ids = [doc['id'] for doc in documents_to_delete]

            try:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )

                final_info = self.get_collection_info()
                final_count = final_info.get("points_count", 0)

                print(f"✅ Deleted {len(point_ids)} test documents")
                print(f"Collection size: {initial_count} → {final_count}")
                print(f"Documents removed: {initial_count - final_count}")

                return {
                    "status": "success",
                    "deleted_count": len(point_ids),
                    "initial_count": initial_count,
                    "final_count": final_count
                }

            except Exception as e:
                print(f"❌ Error deleting documents: {e}")
                return {"status": "error", "error": str(e)}
        else:
            print("No test documents found to delete")
            return {"status": "no_documents_found"}

    async def delete_by_content_patterns(self, patterns: List[str]) -> Dict[str, Any]:
        """
        Delete documents by content pattern matching

        Args:
            patterns: List of content patterns to search for
        """
        print(f"Searching for documents matching patterns: {patterns}")
        print("=" * 60)

        initial_info = self.get_collection_info()
        initial_count = initial_info.get("points_count", 0)
        print(f"Initial collection size: {initial_count} points")

        documents_to_delete = []

        try:
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                with_payload=True,
                with_vectors=False
            )

            points = scroll_result[0]
            next_offset = scroll_result[1]

            # Check each point for pattern matches
            for point in points:
                if point.payload and 'document' in point.payload:
                    content = point.payload.get('document', '')

                    for pattern in patterns:
                        if pattern in content:
                            documents_to_delete.append({
                                'id': point.id,
                                'pattern': pattern,
                                'content_preview': content[:100] + "..."
                            })
                            print(f"✓ Found: ID {point.id}, Pattern: {pattern}")
                            break

            # Continue scrolling
            while next_offset:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    offset=next_offset,
                    limit=100,
                    with_payload=True,
                    with_vectors=False
                )

                points = scroll_result[0]
                next_offset = scroll_result[1]

                for point in points:
                    if point.payload and 'document' in point.payload:
                        content = point.payload.get('document', '')

                        for pattern in patterns:
                            if pattern in content:
                                documents_to_delete.append({
                                    'id': point.id,
                                    'pattern': pattern,
                                    'content_preview': content[:100] + "..."
                                })
                                print(f"✓ Found: ID {point.id}, Pattern: {pattern}")
                                break

        except Exception as e:
            print(f"Error during scroll: {e}")
            return {"status": "error", "error": str(e)}

        print(f"\nFound {len(documents_to_delete)} test documents to delete")

        if documents_to_delete:
            point_ids = [doc['id'] for doc in documents_to_delete]

            try:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )

                final_info = self.get_collection_info()
                final_count = final_info.get("points_count", 0)

                print(f"✅ Deleted {len(point_ids)} test documents")
                print(f"Collection size: {initial_count} → {final_count}")

                return {
                    "status": "success",
                    "deleted_count": len(point_ids),
                    "initial_count": initial_count,
                    "final_count": final_count
                }

            except Exception as e:
                print(f"❌ Error deleting documents: {e}")
                return {"status": "error", "error": str(e)}
        else:
            print("No test documents found to delete")
            return {"status": "no_documents_found"}


async def main():
    parser = argparse.ArgumentParser(
        description="Cleanup test data from Qdrant collections"
    )
    parser.add_argument(
        "--collection",
        default="lodestar_legal_analysis",
        help="Collection name to clean (default: lodestar_legal_analysis)"
    )
    parser.add_argument(
        "--mode",
        choices=["metadata", "pattern"],
        default="metadata",
        help="Deletion mode: metadata (by test_type) or pattern (by content)"
    )
    parser.add_argument(
        "--test-types",
        nargs="+",
        default=["gpu_legal_analysis", "regulatory_analysis", "case_law_analysis",
                 "ip_analysis", "litigation_support"],
        help="Test types to delete (for metadata mode)"
    )
    parser.add_argument(
        "--patterns",
        nargs="+",
        default=["GPU-Accelerated Document Processing",
                 "Enhanced Vector Processing for Legal Technology"],
        help="Content patterns to match (for pattern mode)"
    )

    args = parser.parse_args()

    cleaner = TestDataCleaner(collection_name=args.collection)

    if args.mode == "metadata":
        result = await cleaner.delete_by_metadata(args.test_types)
    else:
        result = await cleaner.delete_by_content_patterns(args.patterns)

    print("\n" + "=" * 60)
    print(f"Cleanup Result: {result.get('status', 'unknown')}")
    if result.get('deleted_count'):
        print(f"Documents deleted: {result['deleted_count']}")


if __name__ == "__main__":
    asyncio.run(main())
