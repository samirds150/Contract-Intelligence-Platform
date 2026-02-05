"""
RAG (Retrieval Augmented Generation) system for contract Q&A.
Combines document retrieval with text generation.
"""

from typing import List, Dict
from src.data_processor import DataProcessor
from src.embeddings import EmbeddingManager
from transformers import pipeline
import torch


class ContractRAG:
    """Main RAG system for contract question answering."""
    
    def __init__(self, config: Dict):
        """
        Initialize RAG system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.device = config['model']['device']
        
        # Initialize components
        self.data_processor = DataProcessor(
            chunk_size=config['data']['chunk_size'],
            chunk_overlap=config['data']['chunk_overlap']
        )
        
        self.embedding_manager = EmbeddingManager(
            model_name=config['embedding']['model_name'],
            device=self.device
        )
        
        # Initialize QA pipeline using transformers
        print("\nLoading QA model...")
        self.qa_pipeline = pipeline(
            "question-answering",
            model="deepset/minilm-uncased-squad2",
            device=0 if self.device == "cuda" else -1
        )
        print("✓ QA model loaded")
    
    def build_knowledge_base(self, data_path: str) -> None:
        """
        Build vector database from contract files.
        
        Args:
            data_path: Path to raw contract files
        """
        print("\n" + "="*50)
        print("BUILDING KNOWLEDGE BASE")
        print("="*50)
        
        # Process documents
        chunks = self.data_processor.process_pipeline(data_path)
        
        # Create embeddings
        embeddings = self.embedding_manager.encode_documents(chunks)
        
        # Build FAISS index
        self.embedding_manager.build_index(embeddings, chunks)
        
        # Save for future use
        self.embedding_manager.save_index(
            self.config['embedding']['faiss_index_path'],
            self.config['embedding']['metadata_path']
        )
        
        print(f"\n✓ Knowledge base built with {len(chunks)} chunks")
    
    def load_knowledge_base(self) -> None:
        """Load pre-built knowledge base from disk."""
        print("Loading knowledge base...")
        self.embedding_manager.load_index(
            self.config['embedding']['faiss_index_path'],
            self.config['embedding']['metadata_path']
        )
    
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            
        Returns:
            List of relevant chunks
        """
        if top_k is None:
            top_k = self.config['rag']['top_k']
        
        results = self.embedding_manager.search(query, top_k=top_k)
        
        # Filter by similarity threshold
        threshold = self.config['rag']['similarity_threshold']
        results = [r for r in results if r['similarity'] >= threshold]
        
        return results
    
    def answer_question(self, question: str, top_k: int = 3) -> Dict:
        """
        Answer a question using RAG pipeline.
        
        Args:
            question: User's question
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dictionary with answer, context, and sources
        """
        # Retrieve context
        context_chunks = self.retrieve_context(question, top_k=top_k)
        
        if not context_chunks:
            return {
                'answer': "No relevant information found in the contract documents.",
                'confidence': 0.0,
                'context': [],
                'sources': []
            }
        
        # Combine context chunks
        context = " ".join([chunk['text'] for chunk in context_chunks])
        
        # Get answer from QA model
        try:
            result = self.qa_pipeline(question=question, context=context)
            
            return {
                'answer': result['answer'],
                'confidence': result['score'],
                'context': [
                    {
                        'text': chunk['text'][:200] + "...",
                        'source': chunk['source'],
                        'similarity': chunk['similarity']
                    }
                    for chunk in context_chunks
                ],
                'sources': list(set([chunk['source'] for chunk in context_chunks]))
            }
        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'confidence': 0.0,
                'context': [],
                'sources': []
            }
    
    def interactive_qa(self) -> None:
        """Run interactive question-answering session."""
        print("\n" + "="*50)
        print("INTERACTIVE Q&A SESSION")
        print("="*50)
        print("Ask questions about the contracts (type 'exit' to quit)\n")
        
        while True:
            question = input("❓ Question: ").strip()
            
            if question.lower() == 'exit':
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nSearching contracts...")
            result = self.answer_question(question)
            
            print(f"\n📝 Answer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.2%}")
            
            if result['context']:
                print("\nContext from:")
                for i, ctx in enumerate(result['context'], 1):
                    print(f"  {i}. {ctx['source']} (similarity: {ctx['similarity']:.2%})")
            
            print("-" * 50 + "\n")
