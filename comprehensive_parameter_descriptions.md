# Comprehensive MCP Tool Parameter Descriptions

## Overview
This document provides detailed parameter descriptions for all MCP tools based on systematic code analysis and behavior understanding.

## Enhanced MCP Server Tools

### 1. qdrant_store

**Purpose**: Store documents in Qdrant collections with optional metadata and automatic collection-specific model selection.

**Parameters**:

#### `information: str` (Required)
- **Description**: The text content to store in the vector database. This is the primary document content that will be embedded and stored.
- **Type**: String
- **Valid Values**: Any text content
- **Size Limits**: No explicit limits in code, but practical limits depend on embedding model context windows
- **Examples**:
  - Simple text: `"Python programming tutorial"`
  - Multi-line content: `"Line 1\nLine 2\nLine 3"`
  - Complex content: `"Technical documentation with detailed explanations..."`
- **Special Handling**:
  - Empty strings are accepted but may not provide useful search results
  - Unicode and emoji characters are supported
  - Very long texts will be processed but may be truncated by embedding models

#### `collection_name: str` (Required)
- **Description**: Name of the Qdrant collection to store the document in. Collections are auto-created with optimal configurations based on the name.
- **Type**: String
- **Valid Values**: Collection names following Qdrant naming conventions
- **Naming Rules**:
  - Must contain only alphanumeric characters, underscores, and hyphens
  - Cannot contain spaces or special characters like @, ., $, %, etc.
  - Length should be reasonable (typically < 255 characters)
- **Examples**:
  - Valid: `"legal_analysis"`, `"my-collection"`, `"collection123"`
  - Invalid: `"test collection"` (spaces), `"test@collection"` (special chars)
- **Auto-Creation**: Collections are automatically created if they don't exist
- **Model Selection**: Collection names trigger automatic model selection:
  - Names containing "legal", "career", "resume" → 1024D BGE-Large models (max precision)
  - Names containing "knowledge", "lessons", "documentation" → 768D BGE-Base models (balanced)
  - Names containing "debug", "working", "solutions" → 384D MiniLM models (speed optimized)

#### `metadata: Metadata = None` (Optional)
- **Description**: Optional JSON metadata to store alongside the document content. Used for filtering, categorization, and additional context.
- **Type**: Optional dictionary/JSON object
- **Default**: `None` (no metadata)
- **Structure**: Any valid JSON object with string keys
- **Examples**:
  - Simple: `{"category": "tutorial", "author": "john"}`
  - Complex: `{"user": {"name": "John", "age": 30}, "tags": ["python", "programming"]}`
  - Mixed types: `{"count": 42, "active": true, "notes": null}`
- **Size Considerations**: Large metadata objects are supported but may impact performance
- **Search Integration**: Metadata can be used for filtering search results (implementation-dependent)

**Return Value**: Success message with collection name, model information, and confirmation of storage.

### 2. qdrant_find

**Purpose**: Search for documents in Qdrant collections using semantic similarity with collection-specific embedding models.

**Parameters**:

#### `query: str` (Required)
- **Description**: The search query text used to find similar documents through semantic vector search.
- **Type**: String
- **Valid Values**: Any text content
- **Search Behavior**:
  - Uses the same embedding model as the target collection for optimal results
  - Semantic similarity matching (not exact text matching)
  - Returns results ranked by similarity score
- **Examples**:
  - Single word: `"Python"`
  - Multi-word: `"Python programming tutorial"`
  - Natural language: `"How to optimize database queries?"`
- **Edge Cases**:
  - Empty string: May return all documents or error (implementation-dependent)
  - Very long queries: May be truncated by embedding model limits
  - Non-existent terms: May still return semantically similar results

#### `collection_name: str` (Required)
- **Description**: Name of the collection to search within. Must be an existing collection.
- **Type**: String
- **Valid Values**: Names of existing collections only
- **Error Conditions**:
  - Non-existent collection names will return "No information found" message
  - Invalid collection names may cause search failures
- **Model Consistency**: Uses the same embedding model that was used to store documents in this collection

**Return Value**: List of formatted entries with content and metadata, or "No information found" message.

### 3. qdrant_list_collections

**Purpose**: List all Qdrant collections with their configurations, model information, and statistics.

**Parameters**: None

**Return Value**: Formatted text showing:
- Collection names and status
- Point counts (number of stored documents)
- Vector configurations (dimensions, model names)
- Model information (FastEmbed model details)
- Error status for any problematic collections

### 4. qdrant_collection_info

**Purpose**: Get detailed information about a specific Qdrant collection.

**Parameters**:

#### `collection_name: str` (Required)
- **Description**: Name of the collection to inspect and get detailed information about.
- **Type**: String
- **Valid Values**: Any string (will check if collection exists)
- **Error Handling**: Returns error message if collection doesn't exist or is inaccessible
- **Information Retrieved**:
  - Collection status and health
  - Document count (points)
  - Vector configuration details
  - Optimization settings (quantization, HNSW parameters)
  - Model information

**Return Value**: Detailed formatted information about the collection or error message.

### 5. qdrant_model_mappings

**Purpose**: Display current collection-to-model mappings and available model configurations.

**Parameters**: None

**Return Value**: Comprehensive information about:
- Predefined collection-to-model mappings
- Available model configurations (384D, 768D, 1024D)
- FastEmbed model details
- Configuration reference for optimal collection setup

## Legacy MCP Server Tools (Additional)

### 6. qdrant_bulk_store

**Purpose**: Store multiple documents efficiently in batch with collection-specific embedding models.
**Note**: This tool is available in legacy server but missing from enhanced server.

**Parameters**:

#### `documents: List[str]` (Required)
- **Description**: List of text documents to store in batch for efficient processing.
- **Type**: Array of strings
- **Valid Values**: List of text content strings
- **Size Considerations**:
  - Empty lists are accepted but perform no operations
  - Very large lists may be processed in batches
  - Each document follows same rules as `information` parameter in `qdrant_store`
- **Examples**:
  - Simple: `["Document 1", "Document 2", "Document 3"]`
  - Mixed: `["Short text", "Much longer document with detailed content..."]`

#### `collection_name: str` (Required)
- **Description**: Target collection name for batch storage (same as qdrant_store).
- **Type**: String
- **Valid Values**: Same validation rules as other collection_name parameters
- **Auto-Creation**: Collection will be created if it doesn't exist

#### `metadata_list: List[Metadata] = None` (Optional)
- **Description**: Optional list of metadata objects corresponding to each document.
- **Type**: Optional array of JSON objects
- **Default**: `None` (no metadata for any document)
- **Length Matching**:
  - If provided, must match the length of documents list
  - Each metadata object corresponds to the document at the same index
  - Mismatched lengths may cause errors
- **Examples**:
  - Matching length: `[{"id": 1}, {"id": 2}, {"id": 3}]` for 3 documents
  - Mixed metadata: `[{"category": "A"}, {}, {"category": "B", "priority": "high"}]`

#### `batch_size: int = 100` (Optional)
- **Description**: Number of documents to process in each batch for memory and performance optimization.
- **Type**: Integer
- **Default**: `100`
- **Valid Range**: Typically 1-1000+ (no hard limits in code)
- **Performance Impact**:
  - Smaller batches: Lower memory usage, more API calls
  - Larger batches: Higher memory usage, fewer API calls
- **Recommended Values**:
  - Small documents: 100-500
  - Large documents: 10-50
  - Memory constrained: 1-10

**Return Value**: Dictionary with batch processing statistics and results.

## Parameter Validation Patterns

### String Parameters
- **Empty Strings**: Generally accepted but may not provide useful functionality
- **Unicode Support**: Full Unicode support including emojis and international characters
- **Size Limits**: No explicit limits but practical constraints from embedding models and Qdrant
- **Special Characters**: Handled appropriately based on context (collection names have restrictions)

### Collection Names
- **Validation**: Must follow Qdrant naming conventions (alphanumeric, underscores, hyphens only)
- **Case Sensitivity**: Collection names are case-sensitive
- **Auto-Creation**: Non-existent collections are automatically created with optimal settings
- **Model Selection**: Name patterns trigger automatic embedding model selection

### Metadata Objects
- **JSON Compliance**: Must be valid JSON structures
- **Nesting**: Unlimited nesting depth supported
- **Types**: Supports strings, numbers, booleans, null, arrays, and objects
- **Size**: Large metadata supported but may impact performance

### Lists and Arrays
- **Empty Lists**: Accepted and handle gracefully
- **Length Limits**: No hard limits but practical performance considerations
- **Type Consistency**: Array elements must match expected types

### Integer Parameters
- **Range Validation**: Practical limits based on use case (batch_size should be positive)
- **Default Handling**: Sensible defaults provided for optional parameters
- **Performance Impact**: Values affect memory usage and processing time

## Error Conditions and Messages

### Common Error Patterns
1. **Network Errors**: Qdrant server unavailable or connection issues
2. **Validation Errors**: Invalid parameter types or values
3. **Collection Errors**: Access issues or collection corruption
4. **Model Errors**: Embedding model loading or processing failures
5. **Memory Errors**: Insufficient resources for large operations

### Error Message Formats
- Clear, descriptive error messages indicating the problem
- Specific parameter names when validation fails
- Suggestions for resolution when possible
- Preservation of error context for debugging

## Best Practices for Parameter Usage

### Information/Query Content
- Use descriptive, well-written text for better embedding quality
- Include relevant context and keywords
- Consider the target embedding model's strengths

### Collection Naming
- Use descriptive names that indicate content type
- Leverage automatic model selection by using appropriate keywords
- Maintain consistent naming conventions within projects

### Metadata Design
- Keep metadata relevant and structured
- Use consistent schemas within collections
- Balance metadata richness with performance considerations

### Batch Operations
- Optimize batch sizes based on document sizes and available memory
- Use metadata lists consistently with document lists
- Monitor performance and adjust batch sizes as needed