"""
Embedding module using BERT-based sentence transformers.
Creates and manages vector embeddings for documents.
"""

import numpy as np
from typing import List, Dict
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    """Manage document embeddings and similarity search."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", 
                 device: str = "cpu"):
        """
        Initialize embedding manager with BERT model.
        
        Args:
            model_name: HuggingFace model name for embeddings
            device: "cpu" or "cuda"
        """
        self.device = device
        self.model_name = model_name
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.metadata = []
        print(f"✓ Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def encode_documents(self, chunks: List[Dict[str, str]], 
                        batch_size: int = 32) -> np.ndarray:
        texts = [chunk['text'] for chunk in chunks]
        print(f"Encoding {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size, 
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.astype('float32')
    
    def build_index(self, embeddings: np.ndarray, metadata: List[Dict[str, str]]) -> None:
        print(f"Building FAISS index with {len(embeddings)} embeddings...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings)
        self.metadata = metadata
        print(f"✓ Index built successfully")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        query_embedding = self.model.encode([query], convert_to_numpy=True).astype('float32')
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            similarity = 1 / (1 + distance)
            results.append({
                'text': self.metadata[idx]['text'],
                'source': self.metadata[idx]['source'],
                'chunk_id': self.metadata[idx]['chunk_id'],
                'similarity': float(similarity)
            })
        return results
    
    def save_index(self, index_path: str, metadata_path: str) -> None:
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def load_index(self, index_path: str, metadata_path: str) -> None:
        if not Path(index_path).exists() or not Path(metadata_path).exists():
            raise FileNotFoundError(f"Index files not found at {index_path} or {metadata_path}")
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        print(f"✓ Index loaded from {index_path}")
