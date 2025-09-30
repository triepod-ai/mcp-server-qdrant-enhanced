# MCP Tool Parameter Testing Plan

## Overview
Systematic testing plan to understand all MCP tool parameters for proper documentation.

## Tools and Parameters Identified

### Enhanced MCP Server Tools:
1. **qdrant_store**
   - `information: str` - The content to store
   - `collection_name: str` - Target collection name
   - `metadata: Metadata = None` - Optional JSON metadata

2. **qdrant_find**
   - `query: str` - Search query
   - `collection_name: str` - Collection to search in

3. **qdrant_list_collections**
   - No parameters

4. **qdrant_collection_info**
   - `collection_name: str` - Collection to inspect

5. **qdrant_model_mappings**
   - No parameters

### Legacy MCP Server Tools (additional):
6. **qdrant_bulk_store** (missing from enhanced)
   - `documents: List[str]` - List of documents to store
   - `collection_name: str` - Target collection name
   - `metadata_list: List[Metadata] = None` - Optional metadata list
   - `batch_size: int = 100` - Batch processing size

## Testing Strategy for Each Parameter Type

### String Parameters
**Test Cases:**
- Empty string: `""`
- Normal text: `"Hello world"`
- Long text: `"A" * 10000`
- Special characters: `"Special chars: àáâãäåæçèé !@#$%^&*()"`
- Unicode/Emoji: `"Hello 👋 世界 🌍"`
- Newlines/formatting: `"Line 1\nLine 2\n\nLine 4"`
- JSON-like strings: `'{"key": "value"}'`
- Invalid names: Collection names with spaces, special chars

### Collection Name Testing
**Specific Tests:**
- Valid names: `"test_collection"`, `"my-collection"`, `"collection123"`
- Invalid names: `"test collection"` (spaces), `"test@collection"` (special chars)
- Non-existent collections: `"does_not_exist"`
- Empty: `""`
- Very long names: `"a" * 255`

### Metadata Parameter Testing
**Test Cases:**
- `None` (default)
- Empty dict: `{}`
- Simple metadata: `{"key": "value"}`
- Nested metadata: `{"user": {"name": "John", "age": 30}}`
- Complex types: `{"numbers": [1,2,3], "bool": true, "null": null}`
- Large metadata: Very large JSON object
- Invalid JSON structures

### List Parameters (documents, metadata_list)
**Test Cases:**
- Empty list: `[]`
- Single item: `["document 1"]`
- Multiple items: `["doc1", "doc2", "doc3"]`
- Large lists: 1000+ items
- Mixed types within expected bounds
- Mismatched lengths (documents vs metadata_list)

### Integer Parameters (batch_size)
**Test Cases:**
- Default value: `100`
- Small values: `1`, `5`, `10`
- Large values: `1000`, `5000`
- Edge cases: `0`, `-1`
- Very large: `999999`

## Testing Methodology

### Phase 1: Basic Parameter Validation
For each parameter:
1. Test with expected valid values
2. Test with edge cases (empty, null, very large)
3. Test with invalid types
4. Document error messages and behaviors

### Phase 2: Integration Testing
1. Test parameter combinations
2. Test with real Qdrant collections
3. Test error conditions (network issues, collection not found)
4. Test performance with different parameter values

### Phase 3: Documentation Generation
1. Document each parameter's purpose
2. Document valid value ranges
3. Document default behaviors
4. Document error conditions
5. Provide usage examples

## Test Environment Setup

### Prerequisites:
1. Qdrant server running locally (port 6333)
2. Enhanced MCP server running
3. Test collections available
4. Network connectivity

### Test Data Preparation:
- Create test collections with different models
- Prepare sample documents of various sizes
- Prepare test metadata structures
- Set up error condition scenarios

## Expected Outputs

### Parameter Documentation Format:
```python
:param parameter_name: Description of what this parameter does, its purpose and behavior.
    Valid values: [range/examples]
    Default: [default value if applicable]
    Error conditions: [when it fails and why]
    Example: [practical usage example]
```

### Error Condition Documentation:
- Network failures
- Invalid collection names
- Type validation errors
- Size limit violations
- Permission/access errors

## Success Criteria
1. All parameters have comprehensive descriptions
2. All edge cases are documented
3. Error conditions are clearly explained
4. Usage examples are provided for each parameter
5. Type validation is properly documented