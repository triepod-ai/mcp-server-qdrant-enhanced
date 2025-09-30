#!/usr/bin/env python3
"""
MCP Tool Parameter Testing Script

This script systematically tests each MCP tool parameter to understand:
- Valid parameter types and ranges
- Default behaviors
- Error conditions
- Performance characteristics
- Usage examples

Results will be used to write comprehensive parameter descriptions.
"""

import asyncio
import json
import os
import time
from typing import List, Dict, Any, Optional
from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector, Entry
from mcp_server_qdrant.enhanced_settings import (
    EnhancedQdrantSettings,
    EnhancedEmbeddingProviderSettings
)

class ParameterTester:
    def __init__(self):
        # Set environment variables for settings
        os.environ["QDRANT_URL"] = "http://localhost:6333"
        os.environ["COLLECTION_NAME"] = "parameter_test_collection"

        # Initialize enhanced settings
        self.qdrant_settings = EnhancedQdrantSettings()
        self.embedding_settings = EnhancedEmbeddingProviderSettings()

        # Initialize connector
        self.connector = EnhancedQdrantConnector(
            qdrant_settings=self.qdrant_settings,
            embedding_settings=self.embedding_settings,
            default_collection_name="parameter_test_collection"
        )

        self.test_results = {}

    async def test_string_parameter(self, param_name: str, test_func, valid_tests: List[str]):
        """Test string parameter with various inputs"""
        results = {
            "param_name": param_name,
            "type": "string",
            "valid_tests": [],
            "invalid_tests": [],
            "edge_cases": [],
            "error_conditions": []
        }

        print(f"\n=== Testing {param_name} (string) ===")

        # Test valid strings
        for test_string in valid_tests:
            try:
                start_time = time.time()
                result = await test_func(test_string)
                duration = time.time() - start_time

                results["valid_tests"].append({
                    "input": test_string,
                    "success": True,
                    "duration": duration,
                    "result_summary": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                })
                print(f"✅ '{test_string[:50]}...' -> Success ({duration:.3f}s)")
            except Exception as e:
                results["invalid_tests"].append({
                    "input": test_string,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                print(f"❌ '{test_string[:50]}...' -> Error: {e}")

        # Test edge cases
        edge_cases = [
            "",  # Empty string
            " ",  # Single space
            "a" * 10000,  # Very long string
            "Hello 👋 世界 🌍",  # Unicode/emoji
            "Line1\nLine2\nLine3",  # Multi-line
            '{"key": "value"}',  # JSON-like string
            "Special: àáâãäåæçèé !@#$%^&*()",  # Special characters
        ]

        for edge_case in edge_cases:
            try:
                start_time = time.time()
                result = await test_func(edge_case)
                duration = time.time() - start_time

                results["edge_cases"].append({
                    "input": edge_case,
                    "success": True,
                    "duration": duration,
                    "description": self._describe_edge_case(edge_case)
                })
                print(f"✅ Edge case '{self._describe_edge_case(edge_case)}' -> Success ({duration:.3f}s)")
            except Exception as e:
                results["edge_cases"].append({
                    "input": edge_case,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "description": self._describe_edge_case(edge_case)
                })
                print(f"❌ Edge case '{self._describe_edge_case(edge_case)}' -> Error: {e}")

        return results

    def _describe_edge_case(self, test_input: str) -> str:
        """Generate human-readable description of edge case"""
        if test_input == "":
            return "empty string"
        elif test_input == " ":
            return "single space"
        elif len(test_input) > 1000:
            return f"very long string ({len(test_input)} chars)"
        elif any(ord(c) > 127 for c in test_input):
            return "unicode/emoji text"
        elif "\n" in test_input:
            return "multi-line text"
        elif test_input.startswith('{"'):
            return "JSON-like string"
        else:
            return "special characters"

    async def test_collection_name_parameter(self):
        """Test collection_name parameter specifically"""
        print(f"\n=== Testing collection_name Parameter ===")

        # Test collection name validation
        valid_names = [
            "test_collection",
            "my-collection",
            "collection123",
            "a",  # Single character
            "test_collection_with_underscores",
            "test-collection-with-hyphens"
        ]

        invalid_names = [
            "test collection",  # Spaces
            "test@collection",  # Special chars
            "test.collection",  # Dots
            "",  # Empty
            "a" * 300,  # Very long
        ]

        results = {
            "param_name": "collection_name",
            "type": "collection_identifier",
            "valid_names": [],
            "invalid_names": [],
            "non_existent": []
        }

        # Test valid collection names
        for name in valid_names:
            try:
                # Test by trying to get collection info
                start_time = time.time()
                info = await self.connector.get_collection_info(name)
                duration = time.time() - start_time

                results["valid_names"].append({
                    "name": name,
                    "success": True,
                    "duration": duration,
                    "exists": "error" not in info
                })
                print(f"✅ Collection name '{name}' -> Valid format ({duration:.3f}s)")
            except Exception as e:
                results["valid_names"].append({
                    "name": name,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                print(f"❌ Collection name '{name}' -> Error: {e}")

        # Test invalid collection names
        for name in invalid_names:
            try:
                start_time = time.time()
                info = await self.connector.get_collection_info(name)
                duration = time.time() - start_time

                results["invalid_names"].append({
                    "name": name,
                    "success": True,  # Didn't throw error
                    "duration": duration,
                    "description": self._describe_invalid_name(name)
                })
                print(f"⚠️  Invalid name '{name}' -> Accepted (might be validation issue)")
            except Exception as e:
                results["invalid_names"].append({
                    "name": name,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "description": self._describe_invalid_name(name)
                })
                print(f"✅ Invalid name '{name}' -> Properly rejected: {e}")

        return results

    def _describe_invalid_name(self, name: str) -> str:
        """Describe why a collection name is invalid"""
        if not name:
            return "empty name"
        elif " " in name:
            return "contains spaces"
        elif len(name) > 255:
            return f"too long ({len(name)} chars)"
        elif any(c in name for c in "@.$%^&*()"):
            return "contains special characters"
        else:
            return "invalid format"

    async def test_metadata_parameter(self):
        """Test metadata parameter with various JSON structures"""
        print(f"\n=== Testing metadata Parameter ===")

        results = {
            "param_name": "metadata",
            "type": "json_metadata",
            "valid_metadata": [],
            "invalid_metadata": [],
            "large_metadata": []
        }

        # Valid metadata test cases
        valid_metadata_cases = [
            None,  # Default/None
            {},  # Empty dict
            {"key": "value"},  # Simple key-value
            {"user": {"name": "John", "age": 30}},  # Nested object
            {"tags": ["tag1", "tag2", "tag3"]},  # Array
            {"numbers": [1, 2, 3], "bool": True, "null": None},  # Mixed types
            {"text": "Some text with unicode: 世界"},  # Unicode
        ]

        for i, metadata in enumerate(valid_metadata_cases):
            try:
                # Test by storing a document with this metadata
                test_collection = f"metadata_test_{i}"
                start_time = time.time()

                entry = Entry(content=f"Test document {i}", metadata=metadata)
                await self.connector.store(entry, collection_name=test_collection)

                duration = time.time() - start_time

                results["valid_metadata"].append({
                    "metadata": metadata,
                    "success": True,
                    "duration": duration,
                    "description": self._describe_metadata(metadata)
                })
                print(f"✅ Metadata {self._describe_metadata(metadata)} -> Success ({duration:.3f}s)")
            except Exception as e:
                results["invalid_metadata"].append({
                    "metadata": metadata,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "description": self._describe_metadata(metadata)
                })
                print(f"❌ Metadata {self._describe_metadata(metadata)} -> Error: {e}")

        # Test large metadata
        large_metadata = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}
        try:
            test_collection = "metadata_test_large"
            start_time = time.time()

            entry = Entry(content="Test document with large metadata", metadata=large_metadata)
            await self.connector.store(entry, collection_name=test_collection)

            duration = time.time() - start_time

            results["large_metadata"].append({
                "size_estimate": len(json.dumps(large_metadata)),
                "success": True,
                "duration": duration
            })
            print(f"✅ Large metadata ({len(json.dumps(large_metadata))} bytes) -> Success ({duration:.3f}s)")
        except Exception as e:
            results["large_metadata"].append({
                "size_estimate": len(json.dumps(large_metadata)),
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            })
            print(f"❌ Large metadata -> Error: {e}")

        return results

    def _describe_metadata(self, metadata) -> str:
        """Generate description of metadata structure"""
        if metadata is None:
            return "None/null"
        elif metadata == {}:
            return "empty dict"
        elif isinstance(metadata, dict) and len(metadata) == 1:
            key = list(metadata.keys())[0]
            value = metadata[key]
            if isinstance(value, dict):
                return "nested object"
            elif isinstance(value, list):
                return "array value"
            else:
                return "simple key-value"
        elif isinstance(metadata, dict) and len(metadata) > 1:
            return f"multiple keys ({len(metadata)})"
        else:
            return "complex structure"

    async def test_query_parameter(self):
        """Test query parameter for search functionality"""
        print(f"\n=== Testing query Parameter ===")

        # First, let's store some test data
        test_collection = "query_test_collection"
        test_documents = [
            "Python programming language tutorial",
            "JavaScript web development guide",
            "Machine learning with neural networks",
            "Database design and SQL optimization",
            "React frontend framework documentation"
        ]

        # Store test documents
        for i, doc in enumerate(test_documents):
            entry = Entry(content=doc, metadata={"doc_id": i, "category": "tutorial"})
            await self.connector.store(entry, collection_name=test_collection)

        results = {
            "param_name": "query",
            "type": "search_string",
            "valid_queries": [],
            "edge_case_queries": [],
            "performance_tests": []
        }

        # Test various query types
        query_tests = [
            "Python",  # Single word
            "Python programming",  # Multiple words
            "web development",  # Phrase
            "machine learning neural",  # Multiple keywords
            "tutorial",  # Common word
            "nonexistentword",  # Non-existent term
        ]

        for query in query_tests:
            try:
                start_time = time.time()
                entries = await self.connector.search(query, collection_name=test_collection, limit=5)
                duration = time.time() - start_time

                results["valid_queries"].append({
                    "query": query,
                    "success": True,
                    "duration": duration,
                    "results_count": len(entries),
                    "has_results": len(entries) > 0
                })
                print(f"✅ Query '{query}' -> {len(entries)} results ({duration:.3f}s)")
            except Exception as e:
                results["valid_queries"].append({
                    "query": query,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                print(f"❌ Query '{query}' -> Error: {e}")

        # Test edge cases
        edge_queries = [
            "",  # Empty query
            " ",  # Space only
            "a",  # Single character
            "a" * 1000,  # Very long query
            "Hello 👋 世界",  # Unicode
            "special@chars#$%",  # Special characters
        ]

        for query in edge_queries:
            try:
                start_time = time.time()
                entries = await self.connector.search(query, collection_name=test_collection, limit=5)
                duration = time.time() - start_time

                results["edge_case_queries"].append({
                    "query": query,
                    "success": True,
                    "duration": duration,
                    "results_count": len(entries),
                    "description": self._describe_query_edge_case(query)
                })
                print(f"✅ Edge query '{self._describe_query_edge_case(query)}' -> {len(entries)} results ({duration:.3f}s)")
            except Exception as e:
                results["edge_case_queries"].append({
                    "query": query,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "description": self._describe_query_edge_case(query)
                })
                print(f"❌ Edge query '{self._describe_query_edge_case(query)}' -> Error: {e}")

        return results

    def _describe_query_edge_case(self, query: str) -> str:
        """Describe query edge case"""
        if query == "":
            return "empty query"
        elif query == " ":
            return "space-only query"
        elif len(query) == 1:
            return "single character"
        elif len(query) > 500:
            return f"very long query ({len(query)} chars)"
        elif any(ord(c) > 127 for c in query):
            return "unicode query"
        else:
            return "special characters"

    async def run_all_tests(self):
        """Run comprehensive parameter testing"""
        print("🧪 Starting MCP Tool Parameter Testing")
        print("=" * 50)

        # Test collection_name parameter
        collection_results = await self.test_collection_name_parameter()
        self.test_results["collection_name"] = collection_results

        # Test metadata parameter
        metadata_results = await self.test_metadata_parameter()
        self.test_results["metadata"] = metadata_results

        # Test query parameter
        query_results = await self.test_query_parameter()
        self.test_results["query"] = query_results

        # Test information parameter (string content)
        info_test_func = lambda text: self.connector.store(
            Entry(content=text, metadata={"test": "info_param"}),
            collection_name="info_test_collection"
        )

        info_results = await self.test_string_parameter(
            "information",
            info_test_func,
            [
                "Simple test content",
                "Multi-line content\nwith several\nlines of text",
                "Content with special characters: àáâãäåæçèé",
                "Very detailed technical content explaining complex concepts in software engineering and system architecture design patterns for scalable applications."
            ]
        )
        self.test_results["information"] = info_results

        # Save results to file
        with open("parameter_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        print("\n" + "=" * 50)
        print("🎉 Parameter testing completed!")
        print("Results saved to: parameter_test_results.json")
        print("\nSummary:")
        for param_name, results in self.test_results.items():
            print(f"📋 {param_name}: {self._summarize_results(results)}")

    def _summarize_results(self, results: Dict) -> str:
        """Generate summary of test results"""
        total_tests = 0
        successful_tests = 0

        for section_key in results:
            if isinstance(results[section_key], list):
                section_results = results[section_key]
                for test in section_results:
                    if isinstance(test, dict) and "success" in test:
                        total_tests += 1
                        if test["success"]:
                            successful_tests += 1

        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            return f"{successful_tests}/{total_tests} tests passed ({success_rate:.1f}%)"
        else:
            return "No quantifiable tests"


async def main():
    """Main testing function"""
    tester = ParameterTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())