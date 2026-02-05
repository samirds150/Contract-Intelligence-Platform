#!/usr/bin/env python
"""
Interactive CLI for querying the contract RAG system
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
    
    # Initialize and load knowledge base
    print("\n" + "="*60)
    print("CONTRACT RAG INTERACTIVE QUERY")
    print("="*60 + "\n")
    
    rag = ContractRAG(cfg)
    rag.load_knowledge_base()
    
    # Interactive query loop
    print("Type 'exit' or 'quit' to exit.\n")
    
    while True:
        question = input("Question: ").strip()
        
        if question.lower() in ['exit', 'quit']:
            print("\nGoodbye!")
            break
        
        if not question:
            continue
        
        print("\nSearching...\n")
        result = rag.answer_question(question)
        
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2%}")
        
        if result['sources']:
            print(f"Sources: {', '.join(result['sources'])}")
        
        print()


if __name__ == '__main__':
    main()
