"""
Quick query script for asking single questions.
Usage: python query.py "What are the payment terms?"
"""

import yaml
import sys
from pathlib import Path
from src.rag_system import ContractRAG
import json


def main():
    """Process a single query."""
    if len(sys.argv) < 2:
        print("Usage: python query.py \"your question here\"")
        print("Example: python query.py \"What are the payment terms?\"")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    
    try:
        # Load configuration
        with open("config/config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Check if knowledge base exists
        index_path = Path(config['embedding']['faiss_index_path'])
        if not index_path.exists():
            print("Error: Knowledge base not found.")
            print("Please run: python setup_knowledge_base.py")
            sys.exit(1)
        
        # Initialize and load
        print("Loading knowledge base...")
        rag = ContractRAG(config)
        rag.load_knowledge_base()
        
        # Process query
        print(f"\n❓ Question: {question}\n")
        result = rag.answer_question(question)
        
        print(f"📝 Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.1%}")
        
        if result['sources']:
            print(f"\nSources: {', '.join(result['sources'])}")
        
        if result['context']:
            print("\nRelevant excerpts:")
            for i, ctx in enumerate(result['context'], 1):
                print(f"\n{i}. {ctx['source']} (similarity: {ctx['similarity']:.1%})")
                print(f"   {ctx['text']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
