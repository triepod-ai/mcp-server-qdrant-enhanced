#!/usr/bin/env python3
"""
Test delete_points functionality for EnhancedQdrantConnector.
"""

import uuid
import pytest

from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector, Entry
from mcp_server_qdrant.enhanced_settings import EnhancedQdrantSettings, EnhancedEmbeddingProviderSettings


@pytest.fixture
async def enhanced_connector(monkeypatch):
    """Fixture to provide an EnhancedQdrantConnector with in-memory Qdrant."""
    # Use environment variable to set in-memory mode
    monkeypatch.setenv("QDRANT_URL", ":memory:")
    settings = EnhancedQdrantSettings()
    embedding_settings = EnhancedEmbeddingProviderSettings()
    connector = EnhancedQdrantConnector(settings, embedding_settings)
    yield connector


@pytest.mark.asyncio
async def test_delete_points_by_id(enhanced_connector):
    """Test deleting points by their IDs."""
    collection_name = f"test_delete_{uuid.uuid4().hex}"

    # Store a test entry
    test_entry = Entry(
        content="Entry to be deleted for testing",
        metadata={"test": True, "purpose": "deletion_test"}
    )
    await enhanced_connector.store(test_entry, collection_name=collection_name)

    # Search to get the point ID
    results = await enhanced_connector.search(
        query="deleted testing",
        collection_name=collection_name,
        limit=5
    )
    assert len(results) >= 1, "Should find the stored entry"

    point_id = results[0].point_id
    assert point_id is not None, "Point ID should be returned"

    # Delete the point
    delete_result = await enhanced_connector.delete_points(
        point_ids=[point_id],
        collection_name=collection_name
    )

    assert delete_result["success"] is True
    assert delete_result["deleted_count"] == 1
    assert delete_result["collection_name"] == collection_name

    # Verify the point is gone
    results_after = await enhanced_connector.search(
        query="deleted testing",
        collection_name=collection_name,
        limit=5
    )
    assert len(results_after) == 0, "Entry should be deleted"


@pytest.mark.asyncio
async def test_delete_multiple_points(enhanced_connector):
    """Test deleting multiple points at once."""
    collection_name = f"test_multi_delete_{uuid.uuid4().hex}"

    # Store multiple entries
    entries = [
        Entry(content="First entry to delete", metadata={"index": 1}),
        Entry(content="Second entry to delete", metadata={"index": 2}),
        Entry(content="Third entry to delete", metadata={"index": 3}),
    ]

    for entry in entries:
        await enhanced_connector.store(entry, collection_name=collection_name)

    # Search to get all point IDs
    results = await enhanced_connector.search(
        query="entry delete",
        collection_name=collection_name,
        limit=10
    )
    assert len(results) == 3, "Should find all 3 entries"

    point_ids = [r.point_id for r in results]

    # Delete all points at once
    delete_result = await enhanced_connector.delete_points(
        point_ids=point_ids,
        collection_name=collection_name
    )

    assert delete_result["success"] is True
    assert delete_result["deleted_count"] == 3

    # Verify all points are gone
    results_after = await enhanced_connector.search(
        query="entry delete",
        collection_name=collection_name,
        limit=10
    )
    assert len(results_after) == 0, "All entries should be deleted"


@pytest.mark.asyncio
async def test_delete_nonexistent_points(enhanced_connector):
    """Test deleting non-existent point IDs.

    Note: In-memory Qdrant raises KeyError for non-existent points.
    Real Qdrant server v1.7+ treats this as no-op. This test validates
    our error handling for the in-memory case.
    """
    collection_name = f"test_nonexistent_{uuid.uuid4().hex}"

    # Store an entry to create the collection
    await enhanced_connector.store(
        Entry(content="Dummy entry to create collection"),
        collection_name=collection_name
    )

    # Try to delete non-existent point ID
    fake_id = uuid.uuid4().hex
    delete_result = await enhanced_connector.delete_points(
        point_ids=[fake_id],
        collection_name=collection_name
    )

    # In-memory Qdrant raises KeyError for non-existent IDs
    # Real Qdrant server would succeed as no-op
    # Either way, our code should handle gracefully without crashing
    assert "success" in delete_result
    if not delete_result["success"]:
        # In-memory client returns error
        assert "error" in delete_result


@pytest.mark.asyncio
async def test_delete_from_nonexistent_collection(enhanced_connector):
    """Test deleting from a collection that doesn't exist."""
    nonexistent_collection = f"nonexistent_{uuid.uuid4().hex}"
    fake_id = uuid.uuid4().hex

    delete_result = await enhanced_connector.delete_points(
        point_ids=[fake_id],
        collection_name=nonexistent_collection
    )

    # Should fail gracefully
    assert delete_result["success"] is False
    assert "does not exist" in delete_result["error"]


@pytest.mark.asyncio
async def test_delete_empty_list(enhanced_connector):
    """Test deleting with empty point_ids list."""
    collection_name = f"test_empty_{uuid.uuid4().hex}"

    delete_result = await enhanced_connector.delete_points(
        point_ids=[],
        collection_name=collection_name
    )

    # Should succeed with count 0
    assert delete_result["success"] is True
    assert delete_result["deleted_count"] == 0
    assert "No point IDs provided" in delete_result.get("message", "")


@pytest.mark.asyncio
async def test_delete_idempotent(enhanced_connector):
    """Test that deleting the same points twice is safe (idempotent)."""
    collection_name = f"test_idempotent_{uuid.uuid4().hex}"

    # Store an entry
    await enhanced_connector.store(
        Entry(content="Entry for idempotent delete test"),
        collection_name=collection_name
    )

    # Get the point ID
    results = await enhanced_connector.search(
        query="idempotent delete",
        collection_name=collection_name,
        limit=5
    )
    point_id = results[0].point_id

    # Delete once
    result1 = await enhanced_connector.delete_points(
        point_ids=[point_id],
        collection_name=collection_name
    )
    assert result1["success"] is True

    # Delete again (same ID - should still succeed)
    result2 = await enhanced_connector.delete_points(
        point_ids=[point_id],
        collection_name=collection_name
    )
    assert result2["success"] is True  # Idempotent - no error on second delete


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
