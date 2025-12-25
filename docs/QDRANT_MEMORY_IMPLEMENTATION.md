# Qdrant Memory Tool - Implementation Guide

## Overview

The `qdrant_memory.py` tool now provides **complete RAG (Retrieval Augmented Generation)** functionality for RIN's long-term memory system. This implementation bridges Open WebUI (Cortex) with Qdrant (Memory) using semantic vector search.

## What Was Implemented

### 1. Embedding Generation
- **Model**: `all-mpnet-base-v2` from sentence-transformers
- **Dimensions**: 768 (matches Qdrant collection configuration)
- **Quality**: High-quality semantic embeddings for accurate retrieval
- **Loading**: Lazy initialization - model loads only when first needed

### 2. Vector Storage (`store_memory`)
- Converts text content into 768-dimensional vectors
- Stores vectors in Qdrant using upsert API
- Generates unique UUIDs for each memory (no collision risk)
- Preserves metadata including:
  - User ID and username
  - Custom tags/metadata
  - Timestamp of storage
- Returns confirmation with memory ID

### 3. Vector Search (`recall_memory`)
- Converts search queries into vectors
- Performs cosine similarity search in Qdrant
- Returns top-k most relevant memories
- Formats results with similarity scores
- Handles empty result sets gracefully

### 4. Infrastructure
- Automatic collection creation on first use
- Comprehensive error handling
- UI feedback via event emitters
- Connection timeout handling

## Technical Details

### Dependencies
Added to `requirements.txt`:
```
sentence-transformers>=2.2.0
```

### Memory ID Generation
- Uses UUID v4 for unique identification
- Prevents hash collisions that could occur with MD5
- Each memory gets a unique identifier regardless of content

### Metadata Structure
```python
{
    "user_id": "user123",           # From __user__ context
    "user_name": "John Doe",        # From __user__ context
    "timestamp": 1703520345.123,    # Unix timestamp
    "custom_tag": "value"           # Any custom metadata
}
```

### Vector Storage Format
```python
{
    "id": "uuid-string",
    "vector": [0.1, 0.2, ..., 0.8],  # 768 dimensions
    "payload": {
        "content": "The actual text content",
        "metadata": { /* metadata dict */ }
    }
}
```

## Usage Examples

### Storing a Memory
```python
# In Open WebUI chat, use the tool:
store_memory(
    content="Paris is the capital of France",
    metadata={"category": "geography", "source": "user"}
)
```

**Returns**:
```
✅ Stored in RIN's long-term memory

**Memory ID**: 550e8400-e29b-41d4-a716-446655440000
**Content**: Paris is the capital of France

This information can now be recalled using semantic search.
```

### Recalling Memories
```python
# In Open WebUI chat, use the tool:
recall_memory(
    query="What is the capital of France?",
    limit=5
)
```

**Returns**:
```
# Memory Recall: 'What is the capital of France?'

Found 1 relevant memories:

## Memory 1 (Similarity: 0.912)
Paris is the capital of France

*Metadata: {
  "category": "geography",
  "source": "user",
  "user_id": "user123",
  "user_name": "John Doe",
  "timestamp": 1703520345.123
}*

---
```

## Performance Considerations

### Model Loading
- First call: ~2-5 seconds (downloads model if not cached)
- Subsequent calls: Instant (model cached in memory)
- Model size: ~420MB download (one-time)
- Model is shared across all tool instances

### Embedding Generation
- Speed: ~50-100 texts/second on CPU
- Scales well with longer texts
- GPU acceleration available if PyTorch with CUDA is installed

### Vector Search
- Speed: Sub-second for collections up to 1M vectors
- Scalable: Qdrant handles millions of vectors efficiently
- Network: Assumes Qdrant on same Docker network (low latency)

## Deployment Notes

### Docker Environment
The tool is designed to run within the RIN Docker environment where:
- Qdrant is accessible at `http://qdrant:6333`
- Model files are cached in the Open WebUI container
- No external network access needed after initial model download

### First Run
On first execution:
1. The embedding model will be downloaded from Hugging Face (~420MB)
2. The Qdrant collection will be created automatically
3. Subsequent runs will use cached model and existing collection

### Resource Requirements
- **Memory**: ~1GB RAM for embedding model
- **Storage**: ~500MB for model cache
- **CPU**: Any modern CPU works, GPU optional
- **Network**: Initial download only, then offline-capable

## Error Handling

The implementation handles:
- Qdrant connection failures
- Model loading errors
- Network timeouts
- Empty search results
- Invalid inputs

All errors are gracefully returned to the user with descriptive messages.

## Security

### CodeQL Analysis
✅ Passed with zero security vulnerabilities

### Data Privacy
- All data stays within your infrastructure
- No external API calls after model download
- User metadata is stored securely in Qdrant
- UUIDs prevent information leakage

## Testing

Comprehensive tests validate:
- Initialization and configuration
- Embedding generation structure
- Vector storage API calls
- Vector search functionality
- Error handling scenarios

All tests pass successfully.

## Future Enhancements

Possible improvements:
1. **Configurable Models**: Support for different embedding models
2. **Batch Operations**: Store/recall multiple memories at once
3. **Memory Management**: Delete, update, or expire old memories
4. **Filtering**: Search within specific metadata categories
5. **Hybrid Search**: Combine vector + keyword search

## Architecture Diagram

```
┌─────────────────┐
│   Open WebUI    │  User interacts with chat
│   (Cortex)      │
└────────┬────────┘
         │
         │ Tool Call: store_memory() / recall_memory()
         │
         ▼
┌─────────────────┐
│ qdrant_memory.py│
│                 │
│  1. Generate    │──► sentence-transformers
│     Embedding   │    (all-mpnet-base-v2)
│                 │
│  2. Store/      │
│     Search      │──► Qdrant HTTP API
│                 │    (Vector Database)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│     Qdrant      │  Persistent vector storage
│    (Memory)     │  with semantic search
└─────────────────┘
```

## Conclusion

The Qdrant memory tool is now fully functional with production-ready RAG capabilities. It provides RIN with genuine long-term memory, enabling:
- Persistent knowledge storage
- Semantic information retrieval
- Context-aware conversations
- Reduced hallucination through factual grounding

The implementation is efficient, secure, and ready for deployment in the RIN sovereign AI infrastructure.
