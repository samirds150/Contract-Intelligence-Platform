# Contract Intelligence Platform

A **CPU-friendly RAG (Retrieval-Augmented Generation) system** for intelligent contract Q&A. Upload contract documents, ask questions, and get accurate answers backed by semantic search and extractive QA.

## What It Does

- **📄 Upload Contracts**: Add `.txt` contract files through the web interface
- **❓ Ask Questions**: Query your contract knowledge base in natural language
- **🧠 Get Smart Answers**: Uses BERT embeddings + FAISS search + transformer QA to find answers with confidence scores
- **📌 See Sources**: Every answer includes the relevant contract sections and similarity scores

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Web Framework** | Django 4.2 |
| **Embeddings** | Sentence-Transformers (all-MiniLM-L6-v2) |
| **Vector Search** | FAISS (CPU-based) |
| **QA Model** | Transformers (deepset/minilm-uncased-squad2) |
| **Language** | Python 3.11+ |
| **Config** | YAML |

## Quick Start (5 Steps)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/samirds150/Contract-Intelligence-Platform.git
cd Contract-Intelligence-Platform/contract-rag
```

### 2️⃣ Activate Virtual Environment

```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**Installs**: Django, sentence-transformers, faiss-cpu, transformers, PyYAML

### 4️⃣ Build Knowledge Base

```bash
# 1. Add your contract files to data/raw/
# Example: data/raw/contract1.txt, data/raw/contract2.txt

# 2. Build the knowledge base
python setup_knowledge_base.py
```

**Creates**:
- `models/faiss_index.bin` - Vector embeddings (~1-10MB)
- `models/metadata.pkl` - Chunk metadata

### 5️⃣ Start the Server

#### **Option A: Simple WSGI Server** ✅ (Recommended on Windows)

```bash
python start_server.py
```

Open: **http://127.0.0.1:8000/**

#### **Option B: Django Development Server** (May have Windows issues)

```bash
python manage.py runserver 127.0.0.1:8000
```

---

## How to Use the Web Interface

### 🏠 Home Page
- Shows all uploaded contract files
- Quick stats on knowledge base size

### 📤 Upload Tab
1. Select a `.txt` contract file
2. Click "Upload"
3. System rebuilds knowledge base automatically
4. Shows success message

### ❓ Ask Tab
1. Type your question (e.g., "What are the payment terms?")
2. Click "Ask"
3. See the answer + confidence score + source documents

---

## Project Structure

```
contract-rag/
│
├── src/                              # Core RAG backend
│   ├── data_processor.py            # Load & chunk documents
│   ├── embeddings.py                # BERT embeddings + FAISS indexing
│   ├── rag_system.py                # Orchestrates RAG pipeline
│   └── __init__.py
│
├── ragapp/                           # Django web application
│   ├── views.py                     # Web endpoints (upload, ask, index)
│   ├── forms.py                     # Django forms
│   ├── urls.py                      # URL routing
│   ├── models.py                    # Django models
│   └── templates/                   # HTML templates
│       ├── django_index.html        # Main page
│       ├── upload_result.html       # Upload confirmation
│       └── answer.html              # Answer display
│
├── ragsite/                          # Django project config
│   ├── settings.py                  # Django settings (Windows-compatible)
│   ├── urls.py                      # Main URL dispatcher
│   ├── wsgi.py                      # WSGI application
│   └── __init__.py
│
├── config/
│   └── config.yaml                  # Configuration (models, chunk size, etc.)
│
├── data/
│   └── raw/                         # ⬅️ PUT YOUR .TXT CONTRACTS HERE
│
├── models/                          # Saved FAISS index & metadata
│   ├── faiss_index.bin
│   └── metadata.pkl
│
├── docs/
│   ├── FUNCTIONS_REFERENCE.html    # API documentation (25+ functions)
│   └── Full_Project_Guide.html     # Detailed guide + code walkthrough
│
├── templates/
│   ├── django_index.html           # Upload & query forms
│   ├── upload_result.html          # Upload status page
│   └── answer.html                 # Query results
│
├── start_server.py                 # ⭐ Windows-compatible server launcher
├── setup_knowledge_base.py         # Build KB from data/raw/
├── query.py                        # Interactive CLI for querying
├── manage.py                       # Django management interface
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## How It Works

### 🔄 The Pipeline

```
User Question
    ↓
[Django Web UI] ← Browser sends question
    ↓
[Encode Question] ← Sentence-Transformers → 384-dim vector
    ↓
[Search FAISS] ← Find top-k similar chunks (fast!)
    ↓
[Retrieve Chunks] ← Get source text + metadata
    ↓
[QA Model] ← Transformers extracts answer span
    ↓
[Return Result] ← Answer + confidence + sources
    ↓
User Sees Answer ← Browser displays results
```

### 🧩 Key Components

| Component | File | Purpose | Tech |
|-----------|------|---------|------|
| **DataProcessor** | `src/data_processor.py` | Load, clean, chunk documents | Python |
| **EmbeddingManager** | `src/embeddings.py` | Create embeddings, store in FAISS | Sentence-Transformers, FAISS |
| **ContractRAG** | `src/rag_system.py` | Orchestrates full RAG workflow | Transformers |
| **Django Views** | `ragapp/views.py` | Web endpoints | Django |

---

## Usage Examples

### 📱 Web Interface (Recommended)

**First Time:**
1. Place `.txt` files in `data/raw/`
2. Run `python setup_knowledge_base.py`
3. Start: `python start_server.py`
4. Open http://127.0.0.1:8000/
5. Upload contracts via web UI
6. Ask questions

**Ongoing:**
- Upload new contracts → KB rebuilds automatically
- Ask questions anytime

### 💻 Command Line

```bash
# Interactive query loop
python query.py

# Example session:
# Question: What is the contract duration?
# Searching...
# Answer: The contract duration is 12 months from the effective date
# Confidence: 91.45%
# Sources: employment_agreement.txt, terms_and_conditions.txt
#
# Question: exit
# Goodbye!
```

---

## Configuration

Edit `config/config.yaml` to customize:

```yaml
# Data
data_path: data/raw                          # Where to find .txt files
models_path: models                          # Where to save FAISS index

# Chunking
chunk_size: 400                              # Characters per chunk
chunk_overlap: 50                            # Overlap between chunks

# Models
embedding_model: sentence-transformers/all-MiniLM-L6-v2
qa_model: deepset/minilm-uncased-squad2

# RAG parameters
top_k: 3                                     # Retrieve top-k chunks
similarity_threshold: 0.0                    # Min similarity (0.0 = all results)
```

---

## 📚 Full Documentation

- **[FUNCTIONS_REFERENCE.html](docs/FUNCTIONS_REFERENCE.html)** 
  - Complete API reference for all 25+ functions
  - Parameters, return values, examples
  
- **[Full_Project_Guide.html](docs/Full_Project_Guide.html)**
  - Architecture (HLD + LLD)
  - Step-by-step code walkthrough
  - Detailed component explanations

**💡 Tip**: Open HTML files in browser. Use Ctrl+P to print/save as PDF.

---

## ⚙️ Troubleshooting

### ❌ Server won't start with `python manage.py runserver`

**Cause**: NumPy + MINGW compatibility issue on Windows

**Solution**: Use `python start_server.py` instead

```bash
# ❌ This may crash on Windows:
python manage.py runserver

# ✅ Use this instead:
python start_server.py
```

### ❌ ImportError: No module named 'src'

**Cause**: Running from wrong directory

**Solution**: Ensure you're in `contract-rag/` directory
```bash
cd contract-rag
python setup_knowledge_base.py  # Now it works!
```

### ❌ Knowledge base won't build

**Cause**: Missing or improperly encoded `.txt` files

**Solution**: 
- Ensure files are UTF-8 encoded
- Check files exist in `data/raw/`
- Try: `python setup_knowledge_base.py` with verbose output

### ❌ Low confidence answers

**Cause**: Query not similar enough to documents

**Solution**:
- Ask more specific questions
- Add more relevant documents
- Check documents are actually related to your questions

### ⏳ Server is slow first time

**Cause**: Models being downloaded (~500MB)

**Solution**: Wait 2-5 minutes on first run. Subsequent runs are cached and fast.

---

## 📊 Performance Metrics

| Operation | Time | Memory |
|-----------|------|--------|
| Build knowledge base | 30-60s | 1-2GB |
| Load knowledge base | 2-5s | 800MB |
| Query (search + QA) | 3-10s | - |
| Per document | ~5s | - |

**System Requirements:**
- **CPU**: Any (no GPU needed)
- **RAM**: 4GB recommended, 2GB minimum
- **Disk**: 2GB+ (for models)
- **OS**: Windows / Mac / Linux

---

## 🔧 Development

### Adding a New Feature

**New ML Model:**
1. Update `config/config.yaml`
2. Modify `src/rag_system.py` to use new model
3. Rebuild knowledge base: `python setup_knowledge_base.py`

**New Web Page:**
1. Create HTML in `ragapp/templates/`
2. Add view function in `ragapp/views.py`
3. Add URL in `ragapp/urls.py`

**New API Endpoint:**
1. Add function to `ragapp/views.py`
2. Register in `ragapp/urls.py`
3. Access via: `http://127.0.0.1:8000/your-endpoint/`

### Running Tests

```bash
# Run test suite
pytest tests/

# Run specific test
pytest tests/test_rag_system.py
```

---

## 🚀 Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn ragsite.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

### Using Waitress (Windows Recommended)

```bash
pip install waitress
waitress-serve --port=8000 ragsite.wsgi:application
```

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["waitress-serve", "--port=8000", "ragsite.wsgi:application"]
```

---

## 🎯 Next Steps

1. ✅ Add your contract `.txt` files to `data/raw/`
2. ✅ Run `python setup_knowledge_base.py` to build the index
3. ✅ Start the server: `python start_server.py`
4. ✅ Open **http://127.0.0.1:8000/** in your browser
5. ✅ Start asking questions!

---

## 🤝 Contributing

Found a bug? Have a feature idea? We'd love your input!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📋 License

This project is provided as-is for educational and research purposes.

---

## 🔗 Links

- **GitHub Repository**: [samirds150/Contract-Intelligence-Platform](https://github.com/samirds150/Contract-Intelligence-Platform)
- **Main Branch**: `main`
- **Issues & Discussions**: Use GitHub Issues

---

## 📞 Need Help?

**Check these first:**
1. [FUNCTIONS_REFERENCE.html](docs/FUNCTIONS_REFERENCE.html) - API docs
2. [Full_Project_Guide.html](docs/Full_Project_Guide.html) - Detailed guide
3. Troubleshooting section above

**Still stuck?**
- Open a GitHub Issue with:
  - What you tried
  - Error message
  - Your system (Windows/Mac/Linux, Python version)

---

**Built with** 💙 **Python • Django • BERT • FAISS • Transformers**

*Making contracts intelligent, one question at a time.*
