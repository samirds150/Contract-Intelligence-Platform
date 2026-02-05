def test_imports():
    # Basic import smoke test to ensure package modules load without syntax errors
    import src.rag_system as rag_system
    import src.data_processor as data_processor
    import src.embeddings as embeddings

    # Ensure classes are present
    assert hasattr(rag_system, 'ContractRAG')
    assert hasattr(data_processor, 'DataProcessor')
    assert hasattr(embeddings, 'EmbeddingManager')
