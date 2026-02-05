#!/usr/bin/env python
"""
Script to build the knowledge base from contract files in data/raw/
"""

import yaml
from src.rag_system import ContractRAG


def main():
    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Wrap config in nested structure expected by ContractRAG
    cfg = {
        'data': {
            'chunk_size': config.get('chunk_size', 400),
            'chunk_overlap': config.get('chunk_overlap', 50),
        },
        'embedding': {
            'model_name': config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
            'faiss_index_path': f"{config.get('models_path', 'models')}/faiss_index.bin",
            'metadata_path': f"{config.get('models_path', 'models')}/metadata.pkl",
        },
        'rag': {
            'top_k': 3,
            'similarity_threshold': 0.0,
        },
        'model': {
            'device': 'cpu',
        },
    }
    
    # Initialize RAG system and build knowledge base
    print("\n" + "="*60)
    print("BUILDING KNOWLEDGE BASE")
    print("="*60)
    
    rag = ContractRAG(cfg)
    data_path = config.get('data_path', 'data/raw')
    rag.build_knowledge_base(data_path)
    
    print("\n" + "="*60)
    print("✓ Knowledge base built successfully!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
