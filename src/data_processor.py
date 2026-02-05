"""
Data processing module for contract documents.
Handles loading, cleaning, and chunking contract files.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple
import re


class DataProcessor:
    """Process and chunk contract documents."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 100):
        """
        Initialize data processor.
        
        Args:
            chunk_size: Number of characters per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_documents(self, data_path: str) -> List[Dict[str, str]]:
        """
        Load all txt files from a directory.
        
        Args:
            data_path: Path to directory containing contract files
            
        Returns:
            List of dictionaries with 'filename' and 'content' keys
        """
        documents = []
        data_dir = Path(data_path)
        
        if not data_dir.exists():
            raise FileNotFoundError(f"Data path does not exist: {data_path}")
        
        txt_files = list(data_dir.glob("*.txt"))
        
        if not txt_files:
            raise FileNotFoundError(f"No .txt files found in {data_path}")
        
        print(f"Found {len(txt_files)} contract files")
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                documents.append({
                    'filename': file_path.name,
                    'content': content
                })
                print(f"✓ Loaded: {file_path.name}")
            except Exception as e:
                print(f"✗ Error loading {file_path.name}: {e}")
        
        return documents
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        return text.strip()
    
    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Split documents into overlapping chunks.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        for doc in documents:
            filename = doc['filename']
            content = self.clean_text(doc['content'])
            
            # Create overlapping chunks
            for start_idx in range(0, len(content), self.chunk_size - self.chunk_overlap):
                end_idx = min(start_idx + self.chunk_size, len(content))
                chunk_text = content[start_idx:end_idx].strip()
                
                if chunk_text:  # Only add non-empty chunks
                    chunks.append({
                        'text': chunk_text,
                        'source': filename,
                        'chunk_id': len(chunks)
                    })
        
        print(f"\nCreated {len(chunks)} chunks from {len(documents)} documents")
        return chunks
    
    def process_pipeline(self, data_path: str) -> List[Dict[str, str]]:
        """
        Complete pipeline: load -> clean -> chunk.
        
        Args:
            data_path: Path to raw contract files
            
        Returns:
            List of processed chunks
        """
        documents = self.load_documents(data_path)
        chunks = self.chunk_documents(documents)
        return chunks
