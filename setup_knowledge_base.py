"""
Script to build and index contract documents.
Run this once after adding contract files to data/raw/
"""

import yaml
import sys
from pathlib import Path
from src.rag_system import ContractRAG


def main():
    """Build knowledge base from contract files."""
    print("\n" + "="*60)
    print("BUILDING CONTRACT KNOWLEDGE BASE")
    print("="*60)
    
    try:
        # Load configuration
        with open("config/config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Check if raw data exists
        raw_path = Path(config['data']['raw_data_path'])
        if not raw_path.exists():
            print(f"Error: {raw_path} does not exist")
            sys.exit(1)
        
        contract_files = list(raw_path.glob("*.txt"))
        if not contract_files:
            print(f"Error: No .txt files found in {raw_path}")
            sys.exit(1)
        
        print(f"\nFound {len(contract_files)} contract files:")
        for file in contract_files:
            print(f"  - {file.name}")
        
        # Initialize and build
        rag = ContractRAG(config)
        rag.build_knowledge_base(str(raw_path))
        
        print("\n" + "="*60)
        print("✓ Knowledge base built successfully!")
        print("You can now run: python main.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
