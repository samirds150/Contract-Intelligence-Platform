"""
Main entry point for Contract RAG Application.
"""

import yaml
import sys
from pathlib import Path
from src.rag_system import ContractRAG


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main application entry point."""
    print("\n" + "="*60)
    print("CONTRACT RAG APPLICATION")
    print("="*60)
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize RAG system
        rag = ContractRAG(config)
        
        # Check if knowledge base exists
        index_path = Path(config['embedding']['faiss_index_path'])
        
        if index_path.exists():
            print("\nKnowledge base found. Loading...")
            rag.load_knowledge_base()
        else:
            print("\nNo knowledge base found.")
            response = input("Would you like to build it now? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                rag.build_knowledge_base(config['data']['raw_data_path'])
            else:
                print("Cannot proceed without knowledge base.")
                return
        
        # Start interactive session
        rag.interactive_qa()
        
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
