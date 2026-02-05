"""
RAG (Retrieval Augmented Generation) system for contract Q&A.
Combines document retrieval with text generation.
"""

from typing import List, Dict
from src.data_processor import DataProcessor
from src.embeddings import EmbeddingManager
from transformers import pipeline
import yaml


class ContractRAG:
    """Main RAG system for contract question answering."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = config.get('model', {}).get('device', 'cpu')
        self.data_processor = DataProcessor(
            chunk_size=config['data']['chunk_size'],
            chunk_overlap=config['data']['chunk_overlap']
        )
        self.embedding_manager = EmbeddingManager(
            model_name=config['embedding']['model_name'],
            device=self.device
        )
        print("\nLoading QA model...")
        self.qa_pipeline = pipeline(
            "question-answering",
            model="deepset/minilm-uncased-squad2",
            device=0 if self.device == "cuda" else -1
        )
        print("✓ QA model loaded")

    def build_knowledge_base(self, data_path: str) -> None:
        print("\nBUILDING KNOWLEDGE BASE")
        chunks = self.data_processor.process_pipeline(data_path)
        embeddings = self.embedding_manager.encode_documents(chunks)
        self.embedding_manager.build_index(embeddings, chunks)
        self.embedding_manager.save_index(
            self.config['embedding']['faiss_index_path'],
            self.config['embedding']['metadata_path']
        )

    def load_knowledge_base(self) -> None:
        self.embedding_manager.load_index(
            self.config['embedding']['faiss_index_path'],
            self.config['embedding']['metadata_path']
        )

    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict]:
        if top_k is None:
            top_k = self.config['rag']['top_k']
        results = self.embedding_manager.search(query, top_k=top_k)
        threshold = self.config['rag']['similarity_threshold']
        results = [r for r in results if r['similarity'] >= threshold]
        return results

    def answer_question(self, question: str, top_k: int = 3) -> Dict:
        context_chunks = self.retrieve_context(question, top_k=top_k)
        if not context_chunks:
            return {'answer': 'No relevant information found in the contract documents.', 'confidence': 0.0, 'context': [], 'sources': []}
        context = " ".join([chunk['text'] for chunk in context_chunks])
        try:
            result = self.qa_pipeline(question=question, context=context)
            return {
                'answer': result.get('answer', ''),
                'confidence': result.get('score', 0.0),
                'context': [
                    {
                        'text': chunk['text'][:200] + '...',
                        'source': chunk['source'],
                        'similarity': chunk['similarity']
                    }
                    for chunk in context_chunks
                ],
                'sources': list(set([chunk['source'] for chunk in context_chunks]))
            }
        except Exception as e:
            return {'answer': f'Error generating answer: {str(e)}', 'confidence': 0.0, 'context': [], 'sources': []}
