# Contract RAG — Full Project Guide

This document provides a High-Level Design (HLD), Low-Level Design (LLD), and the full source code for the Contract RAG project, with step-by-step explanations so you can recreate the project locally. At the end there are instructions to convert this file to PDF.

--

**Contents**
- Overview (HLD)
- Architecture diagram (text)
- Components and responsibilities (LLD)
- File-by-file code (ordered sequence to build the project)
- How to run locally
- Generate PDF from this file

--

## High-Level Design (HLD)

Goal: build a CPU-friendly Retrieval-Augmented-Generation (RAG) system to answer questions about procurement/contract documents.

- Ingest contract text files (.txt)
- Chunk and embed documents using a small Sentence-Transformers model
- Store embeddings in a FAISS (faiss-cpu) index
- Retrieve top-k chunks for a query and run an extractive QA model over the retrieved context
- Provide a web UI (Django) to upload files, rebuild index, and ask questions

Key design constraints:
- CPU-only (no GPU required)
- Use local models from Hugging Face (MiniLM for embeddings, small QA model)
- Keep the system simple and reproducible

## Architecture (text diagram)

Frontend (Django) <---> Backend (ContractRAG in `src/`) --> FAISS index + metadata
                                                  \--> SentenceTransformers (embeddings)
                                                  \--> Transformers QA pipeline

## Low-Level Design (LLD): Components

- `src/data_processor.py`: load `.txt` files, clean text, chunk into fixed-size overlapping chunks
- `src/embeddings.py`: wrap SentenceTransformers; encode chunks, build & search FAISS index, save/load index and metadata
- `src/rag_system.py`: orchestrates processing, indexing, retrieval, and QA (using transformers pipeline for question-answering)
- `setup_knowledge_base.py`: CLI to build KB from `data/raw/`
- `query.py`: interactive CLI to query the built KB
- Django app `ragapp`: routes, forms, templates that call into `src/ContractRAG`
- `config/config.yaml`: small config file for model names and paths

## Step-by-step files and code (create in this order)

1) `config/config.yaml`

```yaml
data_path: data/raw
models_path: models
embedding_model: sentence-transformers/all-MiniLM-L6-v2
qa_model: deepset/minilm-uncased-squad2
chunk_size: 400
chunk_overlap: 50
```

2) `src/data_processor.py`

```python
from pathlib import Path
from typing import List, Dict

class DataProcessor:
    """Load .txt files and produce overlapping text chunks.

    Methods:
    - load_documents(data_path): returns list of dicts {source, text}
    - clean_text(text): minimal normalization
    - chunk_documents(docs): yield chunks with source metadata
    """

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_documents(self, data_path: str) -> List[Dict]:
        p = Path(data_path)
        docs = []
        for f in p.glob('*.txt'):
            text = f.read_text(encoding='utf-8')
            docs.append({'source': f.name, 'text': text})
        return docs

    def clean_text(self, text: str) -> str:
        # Minimal cleaning: normalize whitespace
        return ' '.join(text.split())

    def chunk_documents(self, docs: List[Dict]) -> List[Dict]:
        chunks = []
        for d in docs:
            text = self.clean_text(d['text'])
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunk_text = text[start:end]
                chunks.append({'source': d['source'], 'text': chunk_text})
                start += self.chunk_size - self.chunk_overlap
        return chunks

    def process_pipeline(self, data_path: str) -> List[Dict]:
        docs = self.load_documents(data_path)
        return self.chunk_documents(docs)
```

Explanation: this module reads `.txt` files and creates overlapping chunks which are used for indexing and retrieval.

3) `src/embeddings.py`

```python
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle
from typing import List, Dict

class EmbeddingManager:
    def __init__(self, model_name: str, device: str = 'cpu'):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = None

    def encode_documents(self, chunks: List[Dict]) -> np.ndarray:
        texts = [c['text'] for c in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return np.array(embeddings, dtype='float32')

    def build_index(self, embeddings: np.ndarray, chunks: List[Dict]):
        self.index = faiss.IndexFlatIP(self.dim)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 3):
        q_emb = self.model.encode([query])
        q_emb = np.array(q_emb, dtype='float32')
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, top_k)
        return D[0], I[0]

    def save_index(self, faiss_path: str, metadata_path: str, chunks: List[Dict]):
        faiss.write_index(self.index, faiss_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump(chunks, f)

    def load_index(self, faiss_path: str, metadata_path: str):
        self.index = faiss.read_index(faiss_path)
        with open(metadata_path, 'rb') as f:
            chunks = pickle.load(f)
        return chunks
```

Explanation: handles embedding generation, FAISS index creation/search, and persistence.

4) `src/rag_system.py`

```python
from typing import List, Dict
from src.data_processor import DataProcessor
from src.embeddings import EmbeddingManager
from transformers import pipeline

class ContractRAG:
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
        self.qa_pipeline = pipeline('question-answering', model=config.get('qa_model', 'deepset/minilm-uncased-squad2'), device=-1)

    def build_knowledge_base(self, data_path: str):
        chunks = self.data_processor.process_pipeline(data_path)
        embeddings = self.embedding_manager.encode_documents(chunks)
        self.embedding_manager.build_index(embeddings, chunks)
        self.embedding_manager.save_index(self.config['embedding']['faiss_index_path'], self.config['embedding']['metadata_path'], chunks)

    def load_knowledge_base(self):
        self.chunks = self.embedding_manager.load_index(self.config['embedding']['faiss_index_path'], self.config['embedding']['metadata_path'])

    def retrieve_context(self, question: str, top_k: int = 3):
        D, I = self.embedding_manager.search(question, top_k=top_k)
        results = []
        for score, idx in zip(D, I):
            results.append({'text': self.chunks[idx]['text'], 'source': self.chunks[idx]['source'], 'similarity': float(score)})
        return results

    def answer_question(self, question: str, top_k: int = 3):
        context = ' '.join([c['text'] for c in self.retrieve_context(question, top_k)])
        if not context:
            return {'answer': 'No relevant info found', 'confidence': 0.0, 'context': [], 'sources': []}
        res = self.qa_pipeline(question=question, context=context)
        return {'answer': res.get('answer'), 'confidence': res.get('score', 0.0), 'context': [], 'sources': []}
```

Explanation: ties together preprocessing, embeddings and QA. `build_knowledge_base` creates the FAISS index files.

5) `setup_knowledge_base.py` (root)

```python
import yaml
from src.rag_system import ContractRAG

with open('config/config.yaml') as f:
    c = yaml.safe_load(f)

cfg = {
    'data': {'chunk_size': c.get('chunk_size', 400), 'chunk_overlap': c.get('chunk_overlap', 50)},
    'embedding': {'model_name': c.get('embedding_model'), 'faiss_index_path': f"{c.get('models_path')}/faiss_index.bin", 'metadata_path': f"{c.get('models_path')}/metadata.pkl"},
    'model': {'device': 'cpu'},
}

rag = ContractRAG(cfg)
rag.build_knowledge_base(c.get('data_path', 'data/raw'))
```

6) `query.py` (CLI interactive)

```python
import yaml
from src.rag_system import ContractRAG

with open('config/config.yaml') as f:
    c = yaml.safe_load(f)

cfg = {
    'data': {'chunk_size': c.get('chunk_size', 400), 'chunk_overlap': c.get('chunk_overlap', 50)},
    'embedding': {'model_name': c.get('embedding_model'), 'faiss_index_path': f"{c.get('models_path')}/faiss_index.bin", 'metadata_path': f"{c.get('models_path')}/metadata.pkl"},
    'model': {'device': 'cpu'},
}

rag = ContractRAG(cfg)
rag.load_knowledge_base()

while True:
    q = input('Question (or "exit"): ').strip()
    if q.lower() in ('exit', 'quit'):
        break
    print(rag.answer_question(q))
```

7) Django pieces (short summary)

- `ragsite/settings.py` — standard Django settings; set `MEDIA_ROOT` to `data/raw` so uploads land in the same folder used for indexing.
- `ragapp/forms.py` — `UploadForm` (`forms.FileField`) and `AskForm`.
- `ragapp/views.py` — views that accept uploads, save files to `MEDIA_ROOT`, call `ContractRAG.build_knowledge_base()` and `ContractRAG.answer_question()`.
- `templates/` — `django_index.html`, `upload_result.html`, `answer.html` (server-rendered forms).

8) Tests and CI

- Keep tests small and unit-focused in CI. Heavy integration tests that download models can be scheduled separately.

## How to recreate the project from scratch (commands)

1. Create virtualenv and activate

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

2. Prepare folders and add contracts

```bash
mkdir -p data/raw
# put your .txt files in data/raw/
```

3. Build knowledge base

```bash
python setup_knowledge_base.py
```

4. Run Django server

```bash
python manage.py migrate
python manage.py runserver
```

## Generate PDF from this document

Recommended: install `pandoc` and run:

```bash
pandoc docs/Full_Project_Guide.md -o docs/Full_Project_Guide.pdf --from markdown
```

Or use VS Code's Markdown preview and export as PDF.

--

Notes and further reading: keep models small for CPU; consider async rebuilds for long-running indexing; persist RAG instance in memory when running under a production WSGI server to avoid reloading heavy models per request.

--

If you want, I can now:
- generate the PDF here (if you prefer, I can add a script that attempts conversion locally), or
- split this single large file into per-file templates or a downloadable ZIP, or
- produce a step-by-step script that creates the full project skeleton automatically.

Tell me which of the above you'd like next.

<!-- Trigger note: minor whitespace update to trigger CI workflow -->
