"""
Tests for validator functions and type guards.
"""
import pytest
from mcp_server_qdrant.validators import (
    is_valid_entry_payload,
    is_valid_search_result, 
    is_valid_score,
    is_valid_collection_name,
    validate_search_results,
    validate_metadata,
    sanitize_query
)


class TestEntryPayloadValidation:
    """Test entry payload validation."""
    
    def test_valid_entry_payload(self):
        """Test valid entry payloads."""
        valid_payload = {
            "document": "Test content",
            "metadata": {"key": "value"}
        }
        assert is_valid_entry_payload(valid_payload)
        
        # Test with None metadata
        valid_payload_no_meta = {
            "document": "Test content",
            "metadata": None
        }
        assert is_valid_entry_payload(valid_payload_no_meta)

    def test_invalid_entry_payload(self):
        """Test invalid entry payloads."""
        invalid_payloads = [
            {"document": ""},  # Empty content
            {"document": "   "},  # Whitespace only
            {},  # Missing document
            {"document": None},  # None content
            {"document": "Test", "metadata": "invalid"},  # Invalid metadata type
        ]
        for payload in invalid_payloads:
            assert not is_valid_entry_payload(payload)


class TestSearchResultValidation:
    """Test search result validation."""
    
    def test_valid_search_result(self):
        """Test valid search results."""
        class MockResult:
            def __init__(self, payload, score):
                self.payload = payload
                self.score = score
        
        valid_result = MockResult(
            payload={"document": "Test", "metadata": {}},
            score=0.85
        )
        assert is_valid_search_result(valid_result)

    def test_invalid_search_result(self):
        """Test invalid search results."""
        class MockResult:
            def __init__(self, payload, score):
                self.payload = payload
                self.score = score
        
        invalid_result = MockResult(
            payload={"document": ""},  # Empty document
            score="invalid"  # Invalid score type
        )
        assert not is_valid_search_result(invalid_result)


class TestScoreValidation:
    """Test score validation."""
    
    def test_valid_scores(self):
        """Test valid similarity scores."""
        valid_scores = [0.0, 0.5, 1.0, 0.85, 0.123]
        for score in valid_scores:
            assert is_valid_score(score)
    
    def test_invalid_scores(self):
        """Test invalid similarity scores."""
        import math
        invalid_scores = [-0.1, 1.1, "0.5", None, math.nan]
        for score in invalid_scores:
            assert not is_valid_score(score)


class TestCollectionNameValidation:
    """Test collection name validation."""
    
    def test_valid_collection_names(self):
        """Test valid collection names."""
        valid_names = [
            "test_collection",
            "collection-name",
            "Collection123",
            "legal_analysis",
            "working-solutions"
        ]
        for name in valid_names:
            assert is_valid_collection_name(name)
    
    def test_invalid_collection_names(self):
        """Test invalid collection names."""
        invalid_names = [
            "",  # Empty
            "   ",  # Whitespace only
            ".hidden",  # Starts with dot
            "collection with spaces",  # Contains spaces
            "collection@invalid",  # Invalid characters
            None,  # None type
            123  # Wrong type
        ]
        for name in invalid_names:
            assert not is_valid_collection_name(name)


class TestMetadataValidation:
    """Test metadata validation."""
    
    def test_valid_metadata(self):
        """Test valid metadata."""
        valid_metadata = [
            None,
            {},
            {"key": "value"},
            {"number": 123, "bool": True},
            {"nested": {"key": "value"}}
        ]
        for metadata in valid_metadata:
            assert validate_metadata(metadata)
    
    def test_invalid_metadata(self):
        """Test invalid metadata."""
        # Create large metadata that exceeds size limit
        large_metadata = {"key": "x" * 20000}  # >10KB
        assert not validate_metadata(large_metadata)
        
        # Non-dict metadata
        assert not validate_metadata("string")
        assert not validate_metadata(123)
        assert not validate_metadata([1, 2, 3])


class TestQuerySanitization:
    """Test query sanitization."""
    
    def test_query_sanitization(self):
        """Test query string sanitization."""
        test_cases = [
            ("  hello world  ", "hello world"),
            ("hello\n\nworld", "hello world"),
            ("multiple   spaces", "multiple spaces"),
            ("trim  \t  whitespace  ", "trim whitespace")
        ]
        for input_query, expected in test_cases:
            assert sanitize_query(input_query) == expected
    
    def test_invalid_queries(self):
        """Test invalid query handling."""
        with pytest.raises(TypeError):
            sanitize_query(None)
        
        with pytest.raises(TypeError):
            sanitize_query(123)
        
        with pytest.raises(ValueError):
            sanitize_query("")
        
        with pytest.raises(ValueError):
            sanitize_query("   ")


class TestSearchResultsValidation:
    """Test search results validation."""
    
    def test_validate_search_results(self):
        """Test search results validation."""
        class MockResult:
            def __init__(self, payload, score):
                self.payload = payload
                self.score = score
        
        results = [
            MockResult({"document": "Valid 1", "metadata": {}}, 0.9),
            MockResult({"document": "", "metadata": {}}, 0.8),  # Invalid - empty doc
            MockResult({"document": "Valid 2", "metadata": {}}, "invalid"),  # Invalid - bad score
            MockResult({"document": "Valid 3", "metadata": {}}, 0.7),
        ]
        
        validated = validate_search_results(results)
        assert len(validated) == 2  # Only 2 valid results
        assert validated[0].payload["document"] == "Valid 1"
        assert validated[1].payload["document"] == "Valid 3"