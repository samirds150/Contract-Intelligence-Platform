# Complete Functions Reference Guide

This document provides detailed explanations of every function in the Contract RAG system.

---

## Table of Contents
1. [src/data_processor.py](#data_processor)
2. [src/embeddings.py](#embeddings)
3. [src/rag_system.py](#rag_system)
4. [ragapp/views.py](#views)
5. [query.py](#query)
6. [setup_knowledge_base.py](#setup_knowledge_base)

---

## <a name="data_processor"></a>1. src/data_processor.py

**Purpose**: Handles document loading, text cleaning, and chunking for the RAG system.

### Class: DataProcessor

#### Function 1: `__init__(chunk_size: int = 512, chunk_overlap: int = 100)`

**What it does**: Initializes the DataProcessor with chunk configuration parameters.

**Parameters**:
- `chunk_size` (int, default=512): Number of characters per chunk
- `chunk_overlap` (int, default=100): Number of overlapping characters between consecutive chunks

**Why overlap matters**: 
- Without overlap: If a sentence is split between chunks, information is lost
- With 100-char overlap: Important context is preserved across chunk boundaries
- Example: If a sentence spans chars 500-520, with overlap=100, it will appear in both chunk ending at 612 and chunk starting at 512

**Returns**: None (initializes instance variables)

**Example usage**:
```python
processor = DataProcessor(chunk_size=400, chunk_overlap=50)
```

---

#### Function 2: `load_documents(data_path: str) -> List[Dict[str, str]]`

**What it does**: Reads all `.txt` files from a directory and returns them as a list of dictionaries.

**Parameters**:
- `data_path` (str): Path to directory containing `.txt` contract files

**Process flow**:
1. Checks if directory exists
2. Finds all `.txt` files in the directory
3. Reads each file with UTF-8 encoding
4. Creates a dictionary with `filename` and `content` keys
5. Returns list of dictionaries

**Error handling**:
- Raises `FileNotFoundError` if directory doesn't exist
- Raises `FileNotFoundError` if no `.txt` files found
- Catches and prints errors for individual files (doesn't stop entire process)

**Returns**: List of dictionaries
```python
[
    {'filename': 'contract1.txt', 'content': '...full text...'},
    {'filename': 'contract2.txt', 'content': '...full text...'},
]
```

**Example**:
```python
processor = DataProcessor()
docs = processor.load_documents('data/raw')
# Returns documents with keys: 'filename', 'content'
```

---

#### Function 3: `clean_text(text: str) -> str`

**What it does**: Normalizes and cleans raw text from contract files.

**Parameters**:
- `text` (str): Raw text to clean

**Cleaning steps**:
1. **Remove extra whitespace**: Replaces multiple spaces/tabs/newlines with single space
   - `"Hello    world"` → `"Hello world"`
   - `"Line1\n\nLine2"` → `"Line1 Line2"`

2. **Remove control characters**: Strips non-printable Unicode characters (0x00-0x1F except tab)
   - Removes hidden formatting characters that PDFs might introduce

**Why this matters**: 
- RAG systems need consistent text format for accurate embeddings
- Multiple whitespaces can confuse the embedding model
- Control characters can cause encoding issues

**Returns**: Cleaned string

**Example**:
```python
raw = "Hello   world\n\nThis   is\t\ta test"
cleaned = processor.clean_text(raw)
# Returns: "Hello world This is a test"
```

---

#### Function 4: `chunk_documents(documents: List[Dict[str, str]]) -> List[Dict[str, str]]`

**What it does**: Splits documents into overlapping chunks with metadata preserved.

**Parameters**:
- `documents` (List[Dict]): List of documents from `load_documents()`

**Chunking logic**:
1. For each document, cleans the text
2. Creates overlapping chunks using sliding window:
   - First chunk: chars 0-512
   - Second chunk: chars (512-100) to (1024-100) = 412-1324
   - Maintains overlap of 100 characters
3. Preserves metadata for each chunk:
   - `text`: The chunk content
   - `source`: Which file it came from
   - `chunk_id`: Sequential ID

**Why overlapping chunks**:
- Ensures queries don't miss information at chunk boundaries
- Example: If query mentions "Section 5" at position 500, it will be in 2 overlapping chunks

**Returns**: List of chunk dictionaries
```python
[
    {
        'text': '...512 char chunk...',
        'source': 'contract1.txt',
        'chunk_id': 0
    },
    {
        'text': '...512 char chunk...',
        'source': 'contract1.txt',
        'chunk_id': 1
    },
]
```

**Example**:
```python
documents = processor.load_documents('data/raw')
chunks = processor.chunk_documents(documents)
# If 5 documents × 50KB each = ~250KB total
# With 512 char chunks + 100 overlap, creates ~500 chunks
```

---

#### Function 5: `process_pipeline(data_path: str) -> List[Dict[str, str]]`

**What it does**: Combines all processing steps into one complete pipeline.

**Parameters**:
- `data_path` (str): Path to raw data directory

**Process flow**:
```
data_path → load_documents() → chunk_documents() → chunks list
```

**Why a pipeline function**:
- Single entry point for all processing
- Easier to use: one call instead of three
- Makes error handling simpler

**Returns**: List of processed chunks

**Example**:
```python
processor = DataProcessor(chunk_size=400, chunk_overlap=50)
chunks = processor.process_pipeline('data/raw')
# Automatically: loads → cleans → chunks
```

---

## <a name="embeddings"></a>2. src/embeddings.py

**Purpose**: Manages vector embeddings using BERT-based SentenceTransformer and creates FAISS search index.

### Class: EmbeddingManager

#### Function 1: `__init__(model_name: str, device: str = "cpu")`

**What it does**: Initializes the embedding model and prepares for encoding documents.

**Parameters**:
- `model_name` (str): HuggingFace model identifier, e.g., `"sentence-transformers/all-MiniLM-L6-v2"`
- `device` (str, default="cpu"): Either `"cpu"` or `"cuda"` (for GPU)

**Process**:
1. Loads pre-trained BERT model from HuggingFace
2. Moves model to specified device (CPU or GPU)
3. Stores embedding dimension (usually 384 for MiniLM)

**Why MiniLM**:
- Fast: Optimized BERT distillation
- CPU-friendly: Small model, runs without GPU
- Accurate: Good performance on semantic similarity
- Dimension: 384-dimensional vectors (vs 768 for full BERT)

**Returns**: None (initializes instance)

**Behind the scenes**:
- First run downloads model (~90MB) to local cache
- Subsequent runs load from cache (fast)

**Example**:
```python
embedder = EmbeddingManager(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)
# Model loaded and ready to encode documents
```

---

#### Function 2: `encode_documents(chunks: List[Dict[str, str]], batch_size: int = 32) -> np.ndarray`

**What it does**: Converts text chunks into numerical vector embeddings using the transformer model.

**Parameters**:
- `chunks` (List[Dict]): List of chunk dictionaries from DataProcessor (with 'text' key)
- `batch_size` (int, default=32): How many chunks to process at once
  - Larger batch = faster but more memory
  - Smaller batch = slower but uses less memory

**Process**:
1. Extracts text from each chunk dictionary
2. Passes all texts to the BERT model
3. Model generates 384-dimensional vectors for each text
4. Returns as NumPy array (float32)

**Example vectors**:
- "payment terms" → `[-0.234, 0.567, -0.123, ..., 0.456]` (384 values)
- "liability clause" → `[-0.211, 0.598, -0.145, ..., 0.434]` (384 values)

**Why float32**:
- Uses less memory than float64 (8 bytes vs 16 bytes per value)
- FAISS expects float32 format

**Returns**: NumPy array of shape (num_chunks, 384)

**Example**:
```python
chunks = processor.chunk_documents(documents)
embeddings = embedder.encode_documents(chunks, batch_size=32)
# embeddings.shape = (500, 384)  # 500 chunks, 384-dim vectors
```

---

#### Function 3: `build_index(embeddings: np.ndarray, metadata: List[Dict[str, str]]) -> None`

**What it does**: Creates a FAISS index for fast similarity search over embeddings.

**Parameters**:
- `embeddings` (np.ndarray): Output from `encode_documents()`
- `metadata` (List[Dict]): Original chunk dictionaries (with source, chunk_id, etc.)

**FAISS Index Explanation**:
- FAISS = Facebook AI Similarity Search
- `IndexFlatL2`: Uses Euclidean distance (L2) to find similar vectors
- Fast: Can search 1M vectors in milliseconds
- Stores embeddings in optimized format

**Process**:
1. Creates empty FAISS index with 384 dimensions
2. Adds all embeddings to the index
3. Stores metadata separately (FAISS only stores vectors, not text)

**Why separate metadata**:
- FAISS: Stores only numerical vectors (fast, small)
- Metadata: Stores text, source, chunk_id (needed for results)

**Returns**: None (modifies instance)

**Example**:
```python
embedder.build_index(embeddings, chunks)
# Now ready to search: embedder.search("payment terms")
```

---

#### Function 4: `search(query: str, top_k: int = 5) -> List[Dict]`

**What it does**: Finds the top-k most similar chunks to a given query.

**Parameters**:
- `query` (str): User question or search text, e.g., "What are the payment terms?"
- `top_k` (int, default=5): Number of similar chunks to retrieve

**Search process**:
1. Encodes the query using same model (same 384-dim embedding)
2. Compares query embedding against all chunk embeddings using L2 distance
3. Returns indices of closest chunks
4. Calculates similarity score: `1 / (1 + distance)`
   - Small distance → high similarity (score close to 1)
   - Large distance → low similarity (score close to 0)

**Similarity scoring**:
```
L2 distance = sqrt((v1-v2)^2)
Similarity = 1 / (1 + distance)

Example:
- Distance 0.1 → Similarity = 1/(1+0.1) = 0.909
- Distance 1.0 → Similarity = 1/(1+1.0) = 0.500
- Distance 5.0 → Similarity = 1/(1+5.0) = 0.167
```

**Returns**: List of dictionaries with results
```python
[
    {
        'text': 'Payment must be made within 30 days...',
        'source': 'contract1.txt',
        'chunk_id': 42,
        'similarity': 0.856
    },
    ...
]
```

**Example**:
```python
results = embedder.search("payment deadline", top_k=3)
# Returns 3 most similar chunks
```

---

#### Function 5: `save_index(index_path: str, metadata_path: str) -> None`

**What it does**: Saves the FAISS index and metadata to disk for later use.

**Parameters**:
- `index_path` (str): Path to save FAISS binary file (e.g., `"models/faiss_index.bin"`)
- `metadata_path` (str): Path to save metadata pickle (e.g., `"models/metadata.pkl"`)

**What gets saved**:
1. **FAISS index** (binary file): All embeddings in optimized format
   - Size: ~1-10MB typically (depends on number of chunks)
2. **Metadata** (pickle file): Text, sources, chunk IDs
   - Size: Similar to compressed text

**Why save to disk**:
- Don't recreate embeddings every run (takes 30-60 seconds)
- Keep knowledge base persistent
- Load in seconds instead

**Returns**: None

**Example**:
```python
embedder.save_index('models/faiss_index.bin', 'models/metadata.pkl')
# Files now on disk, ready to load later
```

---

#### Function 6: `load_index(index_path: str, metadata_path: str) -> None`

**What it does**: Loads previously saved FAISS index and metadata from disk.

**Parameters**:
- `index_path` (str): Path to saved FAISS index file
- `metadata_path` (str): Path to saved metadata pickle file

**Process**:
1. Checks if both files exist
2. Loads FAISS binary index
3. Loads metadata from pickle
4. Index is now ready for searching

**Speed comparison**:
- Building index: 30-60 seconds (encoding, building FAISS)
- Loading index: 2-5 seconds (just reading from disk)

**Error handling**: Raises `FileNotFoundError` if files don't exist

**Returns**: None

**Example**:
```python
embedder.load_index('models/faiss_index.bin', 'models/metadata.pkl')
# Now can immediately search without rebuilding
```

---

## <a name="rag_system"></a>3. src/rag_system.py

**Purpose**: Orchestrates the complete RAG pipeline combining retrieval and question-answering.

### Class: ContractRAG

#### Function 1: `__init__(config: Dict)`

**What it does**: Initializes all RAG components with configuration.

**Parameters**:
- `config` (Dict): Configuration dictionary with structure:
```python
{
    'data': {'chunk_size': 400, 'chunk_overlap': 50},
    'embedding': {
        'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
        'faiss_index_path': 'models/faiss_index.bin',
        'metadata_path': 'models/metadata.pkl'
    },
    'rag': {'top_k': 3, 'similarity_threshold': 0.0},
    'model': {'device': 'cpu'}
}
```

**Initialization steps**:
1. Extracts device (CPU/GPU) from config
2. Creates DataProcessor with chunk size/overlap
3. Creates EmbeddingManager with model and device
4. Loads QA transformer pipeline

**QA Model** (`deepset/minilm-uncased-squad2`):
- Extractive QA: Finds answer within provided context
- Reads question and context, highlights the answer span
- Provides confidence score
- Runs on CPU

**Returns**: None (initializes RAG system)

**Example**:
```python
rag = ContractRAG(config)
# All components loaded and ready
```

---

#### Function 2: `build_knowledge_base(data_path: str) -> None`

**What it does**: Builds complete knowledge base from raw contract files.

**Parameters**:
- `data_path` (str): Path to directory with `.txt` contracts

**Process flow**:
```
Raw contracts → Process pipeline → Chunks 
    → Embeddings → FAISS index → Save to disk
```

**Step by step**:
1. `data_processor.process_pipeline()`: Load, clean, chunk documents
2. `embedding_manager.encode_documents()`: Convert chunks to vectors
3. `embedding_manager.build_index()`: Create FAISS index
4. `embedding_manager.save_index()`: Save to disk

**Returns**: None (saves to disk, ready for search)

**Example**:
```python
rag.build_knowledge_base('data/raw')
# Creates: models/faiss_index.bin, models/metadata.pkl
# (~30-60 seconds for 5 small contracts)
```

---

#### Function 3: `load_knowledge_base() -> None`

**What it does**: Loads previously built knowledge base from disk.

**Parameters**: None

**Process**:
- Calls `embedding_manager.load_index()` with paths from config

**Speed**: 2-5 seconds

**Returns**: None

**Example**:
```python
rag.load_knowledge_base()
# Index loaded, ready to search immediately
```

---

#### Function 4: `retrieve_context(query: str, top_k: int = None) -> List[Dict]`

**What it does**: Retrieves top-k relevant chunks for a query using semantic search.

**Parameters**:
- `query` (str): User question
- `top_k` (int, optional): Number of chunks to retrieve
  - If None, uses value from config (default 3)

**Process**:
1. Searches FAISS index for top-k similar chunks
2. Filters by similarity threshold from config
   - Only returns chunks with similarity ≥ threshold
   - Default threshold = 0.0 (keeps all results)
3. Returns filtered list

**Threshold filtering**:
- Threshold 0.0: Keeps all results (more context but potentially noisy)
- Threshold 0.5: Keeps only chunks with 50%+ similarity (stricter)
- Threshold 0.8: Very strict, only highly relevant chunks

**Returns**: List of chunk dictionaries with similarity scores

**Example**:
```python
chunks = rag.retrieve_context("payment deadline", top_k=3)
# Returns list of 3 most similar chunks (or fewer if filtered)
```

---

#### Function 5: `answer_question(question: str, top_k: int = 3) -> Dict`

**What it does**: Complete Q&A pipeline: retrieve context and generate answer.

**Parameters**:
- `question` (str): User question
- `top_k` (int, default=3): Number of context chunks to use

**Process**:
1. `retrieve_context()`: Get top-k relevant chunks
2. **No chunks found**: Return "No relevant information found"
3. **Chunks found**:
   - Concatenate all chunk texts as context
   - Pass to QA model: `qa_pipeline(question=question, context=context)`
   - QA model extraction answer span and confidence score
   - Compile response with answer, confidence, and sources

**Error handling**: Catches exceptions and returns error message

**Returns**: Dictionary with structure:
```python
{
    'answer': 'The payment is due within 30 days of invoice...',
    'confidence': 0.876,
    'context': [
        {
            'text': 'Truncated first 200 chars of chunk...',
            'source': 'contract1.txt',
            'similarity': 0.856
        }
    ],
    'sources': ['contract1.txt', 'contract2.txt']
}
```

**Confidence score**:
- 0.0-1.0 range
- Higher = higher confidence in answer
- Based on QA model's internal scorer

**Example**:
```python
result = rag.answer_question("When is payment due?")
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.1%}")
```

---

## <a name="views"></a>4. ragapp/views.py

**Purpose**: Django view functions handling HTTP requests for web UI.

### Utility Function: `get_rag_config() -> Dict`

**What it does**: Loads YAML config and wraps in nested structure expected by ContractRAG.

**Why needed**: 
- YAML config is flat: `chunk_size`, `models_path`
- ContractRAG expects nested: `config['data']['chunk_size']`
- This function bridges the gap

**Process**:
1. Reads `config/config.yaml`
2. Restructures into nested dictionary
3. Returns properly formatted config

**Returns**: Nested config dictionary

**Example**:
```python
config = get_rag_config()
# Returns properly nested structure for ContractRAG
```

---

### View Function 1: `index(request) -> HttpResponse`

**What it does**: Displays the main page with upload and query forms.

**Parameters**:
- `request`: Django HttpRequest object

**Process**:
1. Creates empty `UploadForm` (for file uploads)
2. Creates empty `AskForm` (for queries)
3. Gets list of uploaded files from media folder
4. Renders template with forms and file list

**Response**: HTML page with:
- File upload form
- Question input form
- List of current uploaded files

**Returns**: Rendered HTML template

**HTTP method**: GET

**Example URL**: `http://localhost:8000/`

---

### View Function 2: `upload(request) -> HttpResponse`

**What it does**: Handles file uploads and rebuilds knowledge base.

**Parameters**:
- `request`: Django HttpRequest with file data

**Process**:
1. Check if POST request
2. Validate form with `UploadForm`
3. If valid:
   - Save uploaded file to media folder
   - Initialize RAG system
   - Rebuild knowledge base from all files in folder
   - Return success message
4. If invalid or error: Return error message

**Process flow**:
```
User uploads file → Saved to disk 
    → RAG.build_knowledge_base() → FAISS index rebuilt 
    → Success response
```

**Key points**:
- Rebuilds entire KB (not incremental)
- All files in media folder included
- Takes 30-60 seconds for large contracts

**Returns**: HTML template with result/error message

**HTTP method**: POST

**Example**: User uploads `new_contract.txt` → KB rebuilt

---

### View Function 3: `ask(request) -> HttpResponse`

**What it does**: Handles question queries and returns answers.

**Parameters**:
- `request`: Django HttpRequest with question

**Process**:
1. Check if POST request
2. Validate form with `AskForm`
3. If valid:
   - Get raw config
   - Initialize RAG system
   - Load knowledge base from disk
   - Call `rag.answer_question(question)`
   - Return answer with context and sources
4. If invalid or error: Return error message

**Key points**:
- Loads existing KB (doesn't rebuild)
- Fast: 2-5 seconds (loading) + search + QA
- Returns answer with confidence and sources

**Returns**: HTML template with question, answer, confidence, and sources

**HTTP method**: POST

**Example**: User asks "What is the payment deadline?" → Returns answer from contracts

---

## <a name="query"></a>5. query.py

**Purpose**: Command-line interface for interactive querying of the knowledge base.

### Function: `main() -> None`

**What it does**: Runs interactive CLI loop for asking questions.

**Process**:
1. Load YAML config
2. Wrap config in nested structure
3. Initialize RAG system
4. Load knowledge base from disk
5. Start interactive loop:
   - Read user question
   - Check for 'exit'/'quit'
   - Call `rag.answer_question()`
   - Display answer, confidence, sources
   - Loop back

**Main loop**:
```
User input → question
    → rag.answer_question()
    → Display results → Loop
```

**Features**:
- Type 'exit' or 'quit' to stop
- Shows answer + confidence + sources
- Continues until user exits

**Returns**: None

**How to run**:
```bash
python query.py
```

**Example interaction**:
```
Question: What are the payment terms?
Searching...

Answer: Payment is due within 30 days of invoice date
Confidence: 87.00%
Sources: contract1.txt, contract2.txt
```

---

## <a name="setup_knowledge_base"></a>6. setup_knowledge_base.py

**Purpose**: Command-line script to build knowledge base from raw contract files.

### Function: `main() -> None`

**What it does**: One-time setup to build entire knowledge base.

**Process**:
1. Load YAML config
2. Wrap config in nested structure
3. Initialize RAG system
4. Get data path from config (default `data/raw`)
5. Call `rag.build_knowledge_base(data_path)`
6. Print success message

**Duration**: 30-60 seconds depending on:
- Number of files
- Total text size
- Model download (first run only)

**Creates**:
- `models/faiss_index.bin`: Embedding vectors in FAISS format
- `models/metadata.pkl`: Chunk metadata and text

**Returns**: None

**How to run**:
```bash
python setup_knowledge_base.py
```

**Example output**:
```
============================================================
BUILDING KNOWLEDGE BASE
============================================================

Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
✓ Model loaded. Embedding dimension: 384
Found 5 contract files
✓ Loaded: contract1.txt
✓ Loaded: contract2.txt
...
Created 47 chunks from 5 documents
Encoding 47 chunks...
Building FAISS index with 47 embeddings...
✓ Index built successfully

============================================================
✓ Knowledge base built successfully!
============================================================
```

---

## Quick Reference: Function Call Flow

### Building KB:
```
setup_knowledge_base.py (main)
  → ContractRAG.build_knowledge_base()
    → DataProcessor.process_pipeline()
      → load_documents()
      → chunk_documents()
    → EmbeddingManager.encode_documents()
    → EmbeddingManager.build_index()
    → EmbeddingManager.save_index()
```

### Querying (Web):
```
Django: upload view
  → ContractRAG.build_knowledge_base() [same as above]

Django: ask view
  → ContractRAG.load_knowledge_base()
    → EmbeddingManager.load_index()
  → ContractRAG.answer_question()
    → retrieve_context()
      → EmbeddingManager.search()
    → QA pipeline extraction
```

### Querying (CLI):
```
query.py (main)
  → ContractRAG.__init__()
  → ContractRAG.load_knowledge_base()
  → Loop: ContractRAG.answer_question()
```

---

## Configuration Structure

All functions expect this config structure (from `config/config.yaml` + wrapping):

```python
{
    'data': {
        'chunk_size': 400,          # Characters per chunk
        'chunk_overlap': 50         # Overlap between chunks
    },
    'embedding': {
        'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
        'faiss_index_path': 'models/faiss_index.bin',
        'metadata_path': 'models/metadata.pkl'
    },
    'rag': {
        'top_k': 3,                 # Default retrieve top-k
        'similarity_threshold': 0.0 # Min similarity score
    },
    'model': {
        'device': 'cpu'             # 'cpu' or 'cuda'
    }
}
```

---

## Summary Table

| File | Function/Class | Purpose | Key Methods |
|------|--------|---------|-------------|
| `data_processor.py` | DataProcessor | Load/chunk documents | `load_documents()`, `clean_text()`, `chunk_documents()`, `process_pipeline()` |
| `embeddings.py` | EmbeddingManager | Embeddings & search | `encode_documents()`, `build_index()`, `search()`, `save_index()`, `load_index()` |
| `rag_system.py` | ContractRAG | RAG orchestration | `build_knowledge_base()`, `load_knowledge_base()`, `retrieve_context()`, `answer_question()` |
| `views.py` | Django views | Web interface | `index()`, `upload()`, `ask()`, `get_rag_config()` |
| `query.py` | CLI | Interactive queries | `main()` |
| `setup_knowledge_base.py` | Setup | Build KB | `main()` |

