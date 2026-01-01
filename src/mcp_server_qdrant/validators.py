"""
Type guards and validation utilities for enhanced Qdrant MCP server.

This module provides TypeScript-inspired type guards and validation functions
for ensuring data integrity and type safety throughout the application.
"""

import logging
from typing import Any, Dict, TypeGuard, List

logger = logging.getLogger(__name__)


def is_valid_entry_payload(payload: Dict[str, Any]) -> TypeGuard[Dict[str, Any]]:
    """
    Type guard for valid entry payloads.

    Args:
        payload: Dictionary to validate as a valid entry payload

    Returns:
        True if payload is valid, False otherwise
    """
    return (
        isinstance(payload.get("document"), str)
        and len(payload["document"].strip()) > 0
        and isinstance(payload.get("metadata"), (dict, type(None)))
    )


def is_valid_search_result(result: Any) -> TypeGuard[Dict[str, Any]]:
    """
    Type guard for valid Qdrant search results.

    Args:
        result: Search result object to validate

    Returns:
        True if result is valid, False otherwise
    """
    return (
        hasattr(result, "payload")
        and hasattr(result, "score")
        and isinstance(result.score, (int, float))
        and is_valid_entry_payload(result.payload)
    )


def is_valid_score(score: Any) -> TypeGuard[float]:
    """
    Type guard for valid similarity scores.

    Args:
        score: Score value to validate

    Returns:
        True if score is valid, False otherwise
    """
    return (
        isinstance(score, (int, float))
        and 0.0 <= score <= 1.0
        and not (isinstance(score, float) and (score != score))  # Check for NaN
    )


def is_valid_collection_name(name: Any) -> TypeGuard[str]:
    """
    Type guard for valid collection names.

    Args:
        name: Collection name to validate

    Returns:
        True if name is valid, False otherwise
    """
    return (
        isinstance(name, str)
        and len(name.strip()) > 0
        and not name.startswith(".")
        and all(c.isalnum() or c in "_-" for c in name)
    )


def validate_search_results(results: List[Any]) -> List[Any]:
    """
    Filter and validate search results, removing invalid entries.

    Args:
        results: List of search results to validate

    Returns:
        List of validated search results
    """
    validated = []
    for i, result in enumerate(results):
        if is_valid_search_result(result):
            if is_valid_score(result.score):
                validated.append(result)
            else:
                logger.warning(f"Invalid score in search result {i}: {result.score}")
        else:
            logger.warning(f"Invalid search result filtered out at index {i}: {result}")
    return validated


def validate_metadata(metadata: Any) -> bool:
    """
    Validate metadata dictionary.

    Args:
        metadata: Metadata to validate

    Returns:
        True if metadata is valid, False otherwise
    """
    if metadata is None:
        return True

    if not isinstance(metadata, dict):
        return False

    # Check for reasonable size limit (10KB serialized)
    try:
        import json

        serialized = json.dumps(metadata)
        if len(serialized) > 10240:  # 10KB limit
            logger.warning(f"Metadata too large: {len(serialized)} bytes")
            return False
    except (TypeError, ValueError) as e:
        logger.warning(f"Metadata not JSON serializable: {e}")
        return False

    return True


def sanitize_query(query: str) -> str:
    """
    Sanitize and normalize query strings.

    Args:
        query: Query string to sanitize

    Returns:
        Sanitized query string
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string")

    # Remove excessive whitespace and normalize
    sanitized = " ".join(query.strip().split())

    if not sanitized:
        raise ValueError("Query cannot be empty after sanitization")

    if len(sanitized) > 10000:  # 10KB limit
        logger.warning(f"Query truncated from {len(sanitized)} to 10000 characters")
        sanitized = sanitized[:10000]

    return sanitized
