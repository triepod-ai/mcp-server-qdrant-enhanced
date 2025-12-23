# Tool Descriptions - Knowledge & Processes

## Overview

Tool descriptions are critical static documentation that inform users about MCP tool capabilities, requirements, and usage patterns. They serve as the primary interface between users and MCP server functionality, preventing errors and guiding proper usage.

## Core Principles

### 1. Static Documentation Philosophy
- **Never include dynamic data** (point counts, timestamps, current states)
- **Focus on capabilities** rather than current conditions
- **Provide consistent information** that won't become outdated
- **Document behavior patterns** rather than specific instances

### 2. Error Prevention Through Clear Guidance
- **Include explicit format requirements** (JSON syntax, parameter types)
- **Provide concrete examples** of correct usage
- **Address common pitfalls** proactively in descriptions
- **Use clear, unambiguous language** to prevent misinterpretation

### 3. Complete Feature Coverage
- **Document all model tiers** and capabilities
- **Include performance characteristics** where relevant
- **Explain auto-selection behaviors** and fallback strategies
- **Cover edge cases and error conditions**

## Tool Description Structure

### Essential Components
1. **Primary Function** - What the tool does
2. **Input Requirements** - Parameter types and formats
3. **Behavior Description** - How the tool operates
4. **Output Format** - What users can expect back
5. **Performance Notes** - Speed/efficiency characteristics
6. **Error Prevention** - Common mistakes and how to avoid them

### Format Template
```
[Primary Function]. [Specific Requirements/Format Guidance]. [Behavior Description with examples]. [Performance characteristics]. [Error handling/fallbacks].
```

## Lessons Learned from Qdrant MCP Enhancement

### Problem: JSON Syntax Errors
**Issue**: Users were using backticks (`) instead of double quotes (") in JSON metadata
**Root Cause**: Tool description didn't specify JSON formatting requirements
**Solution**: Added explicit JSON syntax guidance with examples

**Before**:
```
Store documents in Qdrant collections. Auto-creates collections with optimal models.
```

**After**:
```
Store documents in Qdrant collections with optional metadata. IMPORTANT: Use proper JSON syntax with double quotes (") for all keys and string values, not backticks (`). Example metadata: {"key": "value", "nested": {"data": 123}}.
```

### Problem: Incomplete Model Documentation
**Issue**: Tool descriptions only mentioned 768D and 384D models, omitting 1024D BGE-Large models
**Root Cause**: Descriptions weren't updated when new model tiers were added
**Solution**: Documented all three model tiers with specific use cases

**Before**:
```
Auto-creates collections with optimal models (768D BGE-Base for most collections, 384D MiniLM for simple tasks).
```

**After**:
```
Auto-creates collections with optimal models: 1024D BGE-Large for career/legal content (max precision), 768D BGE-Base for knowledge-intensive content, 384D MiniLM for technical solutions (speed).
```

### Problem: Dynamic Data in Static Descriptions
**Issue**: Including current point counts that become outdated
**Root Cause**: Confusion between tool descriptions (static) and tool output (dynamic)
**Solution**: Removed specific counts, focused on categorization

**Before**:
```
Top collections by volume: music_videos (66 points, 384D), legal_analysis (38 points, 1024D)
```

**After**:
```
Shows all collections with their embedding models: 1024D BGE-Large (legal/career), 768D BGE-Base (knowledge-intensive), 384D MiniLM (technical/debug).
```

## Process for Tool Description Updates

### 1. Analysis Phase
- **Identify the gap** - What's missing or incorrect?
- **Understand user impact** - How does this affect user experience?
- **Review current descriptions** - What needs to change?
- **Check for similar issues** - Are other tools affected?

### 2. Enhancement Phase
- **Write clear, specific guidance** - Address the root cause
- **Include concrete examples** - Show correct usage
- **Test against real scenarios** - Ensure descriptions prevent errors
- **Maintain consistency** - Use similar patterns across tools

### 3. Validation Phase
- **Review for static content** - No dynamic data included
- **Check completeness** - All features documented
- **Verify clarity** - Unambiguous language used
- **Test with users** - Confirm descriptions prevent errors

### 4. Deployment Phase
- **Update source code** - Modify tool registration
- **Rebuild containers** - Deploy updated descriptions
- **Verify deployment** - Test tools are working
- **Monitor usage** - Watch for remaining issues

## Best Practices

### Do's
- ✅ **Be explicit about requirements** (JSON format, parameter types)
- ✅ **Include concrete examples** showing correct usage
- ✅ **Document all capabilities** including edge cases
- ✅ **Use consistent language** across related tools
- ✅ **Focus on user needs** rather than implementation details
- ✅ **Prevent common errors** through clear guidance

### Don'ts
- ❌ **Include dynamic data** (current counts, timestamps)
- ❌ **Use vague language** that can be misinterpreted
- ❌ **Assume user knowledge** about formats or requirements
- ❌ **Forget to update** when adding new features
- ❌ **Make descriptions too long** - keep them focused
- ❌ **Skip examples** for complex parameters

## Enhanced Qdrant MCP Tool Descriptions

### Current Implementation

#### qdrant_store
```python
description='Store documents in Qdrant collections with optional metadata. IMPORTANT: Use proper JSON syntax with double quotes (") for all keys and string values, not backticks (`). Example metadata: {"key": "value", "nested": {"data": 123}}. Auto-creates collections with optimal models: 1024D BGE-Large for career/legal content (max precision), 768D BGE-Base for knowledge-intensive content, 384D MiniLM for technical solutions (speed). Sub-100ms storage with batch support.'
```

**Key Features**:
- Explicit JSON formatting guidance
- Concrete example of correct syntax
- Complete model tier documentation
- Performance characteristics
- Capability overview

#### qdrant_find
```python
description="Search Qdrant collections with Redis caching. Uses collection-specific models for optimal results: 1024D BGE-Large (legal_analysis, technical_documentation), 768D BGE-Base (lessons_learned, contextual_knowledge, music_videos), 384D MiniLM (debugging_patterns, working_solutions). <10ms cached searches, 60-90% cache hit rate. Returns structured JSON with scores, metadata, and point_ids for use with update tools."
```

**Key Features**:
- Specific collection examples for each model tier
- Performance metrics (cache hit rates, response times)
- Output format specification (includes `point_id` for each result)
- Real collection names for context
- **Enhanced (2025-12-23)**: Now returns `point_id` in results for use with `qdrant_get_point` and `qdrant_update_payload`

#### qdrant_list_collections
```python
description="List Qdrant collections with vector dimensions, model types, and point counts. Shows all collections with their embedding models: 1024D BGE-Large (legal/career), 768D BGE-Base (knowledge-intensive), 384D MiniLM (technical/debug). <100ms response time. Shows status (green/yellow/red) and quantization settings."
```

**Key Features**:
- Complete output description
- Model categorization by use case
- Performance expectations
- Status information explanation

#### qdrant_model_mappings
```python
description="Show collection-to-model mappings with all three model tiers. 1024D BGE-Large: career/legal collections (resume_projects, legal_analysis, technical_documentation). 768D BGE-Base: knowledge-intensive collections (lessons_learned, contextual_knowledge, development_patterns, music_videos). 384D MiniLM: technical/debug collections (debugging_patterns, working_solutions). Reference for optimal collection setup."
```

**Key Features**:
- Complete model tier breakdown
- Specific collection examples
- Use case categorization
- Purpose statement (reference tool)

#### qdrant_get_point (Added: 2025-12-23)
```python
description="Retrieve a single point by ID for inspection or verification after updates."
```

**Key Features**:
- Point ID retrieved from `qdrant_find` search results
- Returns full payload (document + metadata)
- Read-only operation (no modifications)
- Useful for verifying updates worked
- Returns point ID, payload, and collection name

**Use Case**:
```
1. Search with qdrant_find → get point_id from results
2. Verify/inspect with qdrant_get_point(point_id, collection_name)
```

#### qdrant_update_payload (Added: 2025-12-23)
```python
description="Update payload fields on existing points without re-embedding (10-100x faster than re-storing). Uses merge semantics."
```

**Key Features**:
- **Merge semantics**: Only specified fields are modified, existing fields preserved
- **No re-embedding**: 10-100x faster than re-storing the entire document
- **Idempotent**: Safe to retry on failure
- **Batch support**: Update multiple points in a single call

**Critical: The `key` Parameter for Nested Structures**

Qdrant payload has nested structure: `payload.document` and `payload.metadata.{fields}`. The `key` parameter controls WHERE updates are applied:

| `key` value | Update target | Example |
|-------------|---------------|---------|
| `None` (default) | Root payload level | Creates `payload.sync_status` |
| `"metadata"` | Nested metadata object | Updates `payload.metadata.sync_status` |

**Without `key`** - Updates write to ROOT level:
```python
qdrant_update_payload(
    point_ids=["abc..."],
    payload={"sync_status": "synced"},  # Creates payload.sync_status (WRONG!)
    collection_name="session_work_logs"
)
```

**With `key="metadata"`** - Updates target NESTED metadata object:
```python
qdrant_update_payload(
    point_ids=["abc..."],
    payload={"sync_status": "synced"},  # Updates payload.metadata.sync_status (CORRECT!)
    collection_name="session_work_logs",
    key="metadata"
)
```

**Use Case** (session_work_logs sync workflow):
```
1. Search: qdrant_find(query="...", collection_name="session_work_logs")
   → Returns point_ids in results

2. Update: qdrant_update_payload(
     point_ids=["abc123..."],
     payload={"sync_status": "synced", "synced_to_asana": true},
     collection_name="session_work_logs",
     key="metadata"  # REQUIRED for nested metadata fields!
   )

3. Verify: qdrant_get_point(point_id="abc123...", collection_name="session_work_logs")
```

## Quality Metrics

### Effectiveness Indicators
- **Error Reduction**: Fewer user mistakes after description updates
- **User Adoption**: Increased tool usage following clearer descriptions
- **Support Requests**: Reduced questions about tool usage
- **Feature Discovery**: Users finding and using advanced features

### Maintenance Indicators
- **Description Freshness**: Regular updates when features change
- **Consistency**: Similar patterns across related tools
- **Completeness**: All features documented appropriately
- **Accuracy**: Descriptions match actual tool behavior

## Future Considerations

### Automated Description Generation
- Extract behavior from code comments
- Generate examples from test cases
- Validate descriptions against actual tool behavior
- Monitor for description drift over time

### User-Driven Improvements
- Collect feedback on confusing descriptions
- Track common usage errors
- A/B test different description formats
- Integrate with user onboarding flows

### Integration with Documentation Systems
- Link to detailed guides for complex tools
- Provide progressive disclosure (brief → detailed)
- Support multiple languages/locales
- Version descriptions with tool releases

---

*Last Updated: December 23, 2025 - Added qdrant_get_point and qdrant_update_payload tools for point retrieval and payload updates*