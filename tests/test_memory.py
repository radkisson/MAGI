"""
Test suite for RIN Memory
"""

import pytest
from rin.memory import MemoryStore, VectorMemory, MemoryManager
from rin.memory.store import DEFAULT_EMBEDDING_DIM


def test_memory_store_initialization():
    """Test MemoryStore initialization"""
    store = MemoryStore()
    assert store is not None


def test_memory_store_store_and_retrieve():
    """Test storing and retrieving memories"""
    store = MemoryStore()
    
    # Store a memory
    success = store.store("test_key", "test_value")
    assert success is True
    
    # Retrieve the memory
    value = store.retrieve("test_key")
    assert value == "test_value"


def test_memory_store_search():
    """Test searching memories"""
    store = MemoryStore()
    
    store.store("key1", "This is a test about AI")
    store.store("key2", "This is about machine learning")
    store.store("key3", "Completely different topic")
    
    results = store.search("AI")
    assert len(results) >= 1


def test_vector_memory_initialization():
    """Test VectorMemory initialization"""
    vector_mem = VectorMemory()
    assert vector_mem is not None


def test_vector_memory_embed():
    """Test embedding generation"""
    vector_mem = VectorMemory()
    embedding = vector_mem.embed("test text")
    
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) == DEFAULT_EMBEDDING_DIM  # Use constant instead of magic number


def test_vector_memory_store():
    """Test storing vectors"""
    vector_mem = VectorMemory()
    vec_id = vector_mem.store_vector("test content")
    
    assert vec_id is not None
    assert vec_id.startswith("vec_")


def test_vector_memory_similarity_search():
    """Test similarity search"""
    vector_mem = VectorMemory()
    
    vector_mem.store_vector("AI and machine learning")
    vector_mem.store_vector("Deep neural networks")
    
    results = vector_mem.similarity_search("artificial intelligence", top_k=2)
    assert isinstance(results, list)


def test_memory_manager_initialization():
    """Test MemoryManager initialization"""
    manager = MemoryManager()
    assert manager is not None


def test_memory_manager_remember():
    """Test remember functionality"""
    manager = MemoryManager()
    mem_id = manager.remember("Test content", memory_type="vector")
    
    assert mem_id is not None


def test_memory_manager_recall():
    """Test recall functionality"""
    manager = MemoryManager()
    
    manager.remember("Important information about AI")
    results = manager.recall("AI", use_vector=True)
    
    assert isinstance(results, list)


def test_memory_manager_stats():
    """Test getting memory statistics"""
    manager = MemoryManager()
    
    manager.remember("Test 1", memory_type="vector")
    manager.remember("Test 2", memory_type="simple")
    
    stats = manager.get_stats()
    assert "total" in stats
    assert stats["total"] >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
