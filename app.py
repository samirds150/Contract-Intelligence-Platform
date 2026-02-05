"""
Flask web application for Contract RAG System.
Provides a user-friendly interface for asking questions about contracts.
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import yaml
from pathlib import Path
from src.rag_system import ContractRAG
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
app.config['UPLOAD_FOLDER'] = Path('data/raw')
app.config['ALLOWED_EXTENSIONS'] = {'.txt'}

# Global RAG instance
rag = None


def initialize_rag():
    """Initialize RAG system on startup."""
    global rag
    try:
        with open("config/config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        rag = ContractRAG(config)
        
        # Check if knowledge base exists
        index_path = Path(config['embedding']['faiss_index_path'])
        if index_path.exists():
            logger.info("Loading knowledge base...")
            rag.load_knowledge_base()
            logger.info("✓ Knowledge base loaded successfully")
            return True
        else:
            logger.warning("⚠ Knowledge base not found. Run setup_knowledge_base.py first.")
            return False
    except Exception as e:
        logger.error(f"Error initializing RAG: {e}")
        return False


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/api/files', methods=['GET'])
def list_files():
    """Return list of uploaded contract files."""
    folder = app.config['UPLOAD_FOLDER']
    folder.mkdir(parents=True, exist_ok=True)
    files = [f.name for f in folder.glob('*.txt')]
    return jsonify({'success': True, 'files': files})


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle uploading of .txt contract files and optionally rebuild index."""
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files part in request'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'success': False, 'error': 'No files uploaded'}), 400

    saved = []
    upload_folder = app.config['UPLOAD_FOLDER']
    upload_folder.mkdir(parents=True, exist_ok=True)

    for file in files:
        filename = secure_filename(file.filename)
        if filename == '':
            continue
        if not allowed_file(filename):
            continue
        dest = upload_folder / filename
        file.save(dest)
        saved.append(dest.name)

    # If rag not initialized, try initializing
    global rag
    if rag is None:
        initialize_rag()

    # Rebuild knowledge base to include new files
    try:
        rag.build_knowledge_base(str(upload_folder))
        return jsonify({'success': True, 'saved': saved})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'saved': saved}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """
    API endpoint for asking questions.
    
    Request JSON:
    {
        "question": "What are the payment terms?"
    }
    
    Response JSON:
    {
        "success": true,
        "answer": "...",
        "confidence": 0.95,
        "sources": [...],
        "context": [...]
    }
    """
    if rag is None:
        return jsonify({
            'success': False,
            'error': 'Knowledge base not initialized. Please run setup_knowledge_base.py'
        }), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question cannot be empty'
            }), 400
        
        if len(question) > 500:
            return jsonify({
                'success': False,
                'error': 'Question too long (max 500 characters)'
            }), 400
        
        logger.info(f"Processing question: {question}")
        
        # Get answer from RAG system
        result = rag.answer_question(question)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'context': result['context']
        })
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok' if rag is not None else 'error',
        'message': 'RAG system is running' if rag is not None else 'RAG system not initialized'
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("CONTRACT RAG WEB APPLICATION")
    print("="*60)
    
    # Initialize RAG system
    if initialize_rag():
        print("\n✓ Starting web server...")
        print("🌐 Open your browser: http://localhost:5000")
        print("="*60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        )
    else:
        print("\n❌ Failed to initialize RAG system")
        print("Please run: python setup_knowledge_base.py")
