# Contract RAG Application

A CPU-friendly Retrieval Augmented Generation (RAG) system for answering questions about procurement contracts using BERT embeddings and lightweight transformers.

## 📋 Overview

This application allows you to:
- **Load** multiple contract files (TXT format)
- **Index** them using BERT embeddings and FAISS vector database
- **Ask questions** about contracts in natural language
- **Get answers** with relevant context from the documents

## 🏗️ Architecture

```
contract-rag/
├── data/
│   ├── raw/                    # 📄 Add your contract .txt files here
│   └── processed/              # Processed chunks (auto-generated)
├── models/                     # 🔍 FAISS index and metadata
├── src/
│   ├── data_processor.py       # Document loading & chunking
│   ├── embeddings.py           # BERT embeddings & FAISS indexing
│   └── rag_system.py           # Main RAG pipeline
├── config/
│   └── config.yaml             # ⚙️ Configuration settings
├── main.py                     # Interactive Q&A interface
├── setup_knowledge_base.py     # Build the knowledge base
├── query.py                    # Single query script
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Navigate to project directory
cd contract-rag

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Add Your Contract Files

Copy your 3 contract TXT files to the `data/raw/` folder:

```
data/raw/
├── contract_1.txt
├── contract_2.txt
└── contract_3.txt
```

### 3. Build Knowledge Base

After adding files, index them:

```bash
python setup_knowledge_base.py
```

This will:
- Load all .txt files from `data/raw/`
- Split them into chunks (512 characters with overlap)
- Create BERT embeddings using all-MiniLM-L6-v2 model
- Build FAISS index for fast similarity search
- Save index to `models/` folder

### 4. Ask Questions

**Option A: Interactive Mode**
```bash
python main.py
```
Then type your questions (type "exit" to quit)

**Option B: Single Query**
```bash
python query.py "What are the payment terms?"
```

## 📊 How It Works

```
User Question
    ↓
[1] RETRIEVAL (BERT + FAISS)
    ├─ Encode question with BERT
    ├─ Search FAISS index
    └─ Retrieve top-5 relevant chunks
    ↓
[2] CONTEXT COMBINATION
    └─ Merge retrieved chunks
    ↓
[3] GENERATION (Question-Answering Model)
    ├─ Pass question + context to QA model
    └─ Generate answer with confidence score
    ↓
Answer + Sources
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
data:
  chunk_size: 512              # Characters per chunk
  chunk_overlap: 100           # Overlap between chunks

embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"  # BERT model
  # Alternatives (faster/slower/more accurate):
  # - "sentence-transformers/all-distilroberta-v1"      (faster)
  # - "sentence-transformers/all-mpnet-base-v2"         (more accurate)

rag:
  top_k: 5                     # Chunks to retrieve
  similarity_threshold: 0.3    # Minimum similarity score
```

## 🔧 Models Used

### Embeddings
- **all-MiniLM-L6-v2** (default)
  - 384-dimensional embeddings
  - Fast on CPU
  - Good accuracy for contracts

### Question Answering
- **minilm-uncased-squad2** (SQuAD 2.0 fine-tuned)
  - Extracts answers from context
  - Provides confidence scores

## 💡 Example Questions

```
"What are the payment terms?"
"What is the contract duration?"
"What are the termination conditions?"
"Who are the parties involved?"
"What penalties are mentioned?"
"What insurance requirements are specified?"
```

## 📈 Performance Tips

1. **First run is slow**: Model downloads happen automatically (~500MB)
2. **Subsequent runs are fast**: Models cached locally
3. **For GPU support**: Change `device: "cpu"` to `device: "cuda"` in config.yaml and remove `-cpu` from faiss dependency

## 🐛 Troubleshooting

### Issue: "No .txt files found"
- Ensure contract files are in `data/raw/`
- Files must end with `.txt` extension

### Issue: Model download fails
- Check internet connection
- Models auto-download from HuggingFace Hub
- Can take 5-10 minutes on first run

### Issue: Out of memory
- Reduce `batch_size` in config.yaml
- Use smaller model: "sentence-transformers/all-MiniLM-L12-v2"

### Issue: Low confidence answers
- Try adjusting `similarity_threshold` in config.yaml
- Ensure contracts are in clear, structured text format

## 📝 Project Structure Details

### `src/data_processor.py`
- Loads contract files
- Cleans and normalizes text
- Creates overlapping chunks for better context

### `src/embeddings.py`
- BERT embedding creation using sentence-transformers
- FAISS index building and searching
- Similarity scoring

### `src/rag_system.py`
- Combines retrieval + generation
- Question-answering pipeline
- Interactive session manager

## 🔄 Workflow Summary

```
1. Place contracts in data/raw/
       ↓
2. python setup_knowledge_base.py    (one-time)
       ↓
3. python main.py                    (interactive mode)
   OR
   python query.py "question"         (single query)
```

## 📚 Requirements Summary

- **PyTorch**: Deep learning framework (CPU optimized)
- **Transformers**: HuggingFace models and pipelines
- **Sentence-Transformers**: BERT-based embeddings
- **FAISS**: Fast vector similarity search
- **NumPy/Pandas**: Data processing

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Add your 3 contract files to `data/raw/`
3. ✅ Run `python setup_knowledge_base.py`
4. ✅ Start asking questions with `python main.py`

---

**CPU-optimized for inference without GPU. No external API keys required.**
