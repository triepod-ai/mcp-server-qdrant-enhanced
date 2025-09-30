#!/usr/bin/env python3
"""
Collection Inspector Utility
Consolidated script for inspecting Qdrant collections and their contents
"""

import asyncio
import argparse
import sys
import os
import json
from typing import Dict, Any, Optional
from qdrant_client import QdrantClient

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from mcp_server_qdrant.enhanced_settings import EnhancedQdrantSettings, EnhancedEmbeddingProviderSettings


class CollectionInspector:
    def __init__(self):
        self.client = QdrantClient(host='localhost', port=6333)

    def list_all_collections(self) -> None:
        """List all available collections with statistics"""
        print("=" * 80)
        print("QDRANT COLLECTIONS")
        print("=" * 80)

        try:
            collections = self.client.get_collections()

            if not collections.collections:
                print("No collections found")
                return

            largest_collection = None
            max_points = 0

            for collection in collections.collections:
                try:
                    collection_info = self.client.get_collection(collection.name)
                    points_count = collection_info.points_count

                    # Track largest collection
                    if points_count > max_points:
                        max_points = points_count
                        largest_collection = collection.name

                    # Get vector config
                    vector_config = collection_info.config.params.vectors
                    if hasattr(vector_config, 'size'):
                        vector_size = vector_config.size
                    else:
                        vector_size = "multi-vector"

                    print(f"\n📦 Collection: {collection.name}")
                    print(f"   Points: {points_count:,}")
                    print(f"   Vector Size: {vector_size}")
                    print(f"   Status: {collection_info.status}")

                except Exception as e:
                    print(f"\n❌ Collection: {collection.name}")
                    print(f"   Error: {e}")

            if largest_collection:
                print("\n" + "=" * 80)
                print(f"🏆 Largest Collection: {largest_collection} ({max_points:,} points)")
                print("=" * 80)

        except Exception as e:
            print(f"Error listing collections: {e}")

    def inspect_collection(self, collection_name: str, limit: int = 10) -> None:
        """
        Inspect a specific collection and show recent points

        Args:
            collection_name: Name of collection to inspect
            limit: Number of points to display
        """
        print("=" * 80)
        print(f"COLLECTION INSPECTION: {collection_name}")
        print("=" * 80)

        try:
            # Get collection info
            collection_info = self.client.get_collection(collection_name)
            points_count = collection_info.points_count

            print(f"\n📊 Collection Statistics:")
            print(f"   Total Points: {points_count:,}")
            print(f"   Status: {collection_info.status}")

            # Get vector configuration
            vector_config = collection_info.config.params.vectors
            if hasattr(vector_config, 'size'):
                print(f"   Vector Size: {vector_config.size}D")
            else:
                print(f"   Vector Config: Multi-vector")

            # Scroll through points
            print(f"\n📄 Sample Points (showing up to {limit}):")
            print("-" * 80)

            scroll_result = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            points = scroll_result[0]

            if not points:
                print("   No points found in collection")
                return

            for idx, point in enumerate(points, 1):
                print(f"\n   Point {idx}:")
                print(f"   ID: {point.id}")

                if point.payload:
                    # Show document content preview
                    if 'document' in point.payload:
                        content = point.payload['document']
                        print(f"   Content: {content[:150]}...")

                    # Show metadata if present
                    if 'metadata' in point.payload:
                        metadata = point.payload['metadata']
                        print(f"   Metadata: {json.dumps(metadata, indent=6)}")

                print("-" * 80)

        except Exception as e:
            print(f"❌ Error inspecting collection '{collection_name}': {e}")

    def find_largest_collection(self) -> Optional[Dict[str, Any]]:
        """Find and return information about the largest collection"""
        try:
            collections = self.client.get_collections()

            largest = None
            max_points = 0

            for collection in collections.collections:
                try:
                    collection_info = self.client.get_collection(collection.name)
                    points_count = collection_info.points_count

                    if points_count > max_points:
                        max_points = points_count
                        largest = {
                            "name": collection.name,
                            "points_count": points_count,
                            "status": collection_info.status
                        }

                except Exception:
                    continue

            return largest

        except Exception as e:
            print(f"Error finding largest collection: {e}")
            return None


async def main():
    parser = argparse.ArgumentParser(
        description="Inspect Qdrant collections and their contents"
    )
    parser.add_argument(
        "--mode",
        choices=["list", "inspect", "largest"],
        default="list",
        help="Inspection mode: list (all collections), inspect (specific collection), largest (find largest)"
    )
    parser.add_argument(
        "--collection",
        help="Collection name to inspect (required for inspect mode)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of points to show (default: 10)"
    )

    args = parser.parse_args()

    inspector = CollectionInspector()

    if args.mode == "list":
        inspector.list_all_collections()

    elif args.mode == "inspect":
        if not args.collection:
            print("Error: --collection is required for inspect mode")
            parser.print_help()
            return

        inspector.inspect_collection(args.collection, args.limit)

    elif args.mode == "largest":
        largest = inspector.find_largest_collection()
        if largest:
            print("=" * 80)
            print(f"🏆 Largest Collection: {largest['name']}")
            print(f"   Points: {largest['points_count']:,}")
            print(f"   Status: {largest['status']}")
            print("=" * 80)
        else:
            print("No collections found")


if __name__ == "__main__":
    asyncio.run(main())
