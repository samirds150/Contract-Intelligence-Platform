from pathlib import Path
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadForm, AskForm

from src.rag_system import ContractRAG
import yaml


def get_rag_config():
    """Load YAML config and wrap in nested structure expected by ContractRAG"""
    with open('config/config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    
    models_path = cfg.get('models_path', 'models')
    return {
        'data': {
            'chunk_size': cfg.get('chunk_size', 400),
            'chunk_overlap': cfg.get('chunk_overlap', 50),
        },
        'embedding': {
            'model_name': cfg.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
            'faiss_index_path': f"{models_path}/faiss_index.bin",
            'metadata_path': f"{models_path}/metadata.pkl",
        },
        'rag': {
            'top_k': 3,
            'similarity_threshold': 0.0,
        },
        'model': {
            'device': 'cpu',
        },
    }


def index(request):
    upload_form = UploadForm()
    ask_form = AskForm()
    upload_folder = Path(settings.MEDIA_ROOT)
    upload_folder.mkdir(parents=True, exist_ok=True)
    files = sorted([p.name for p in upload_folder.glob('*.txt')])
    return render(request, 'django_index.html', {'upload_form': upload_form, 'ask_form': ask_form, 'files': files})


def upload(request):
    if request.method != 'POST':
        return redirect('ragapp:index')
    form = UploadForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            upload_folder = Path(settings.MEDIA_ROOT)
            upload_folder.mkdir(parents=True, exist_ok=True)
            dest = upload_folder / uploaded_file.name
            with open(dest, 'wb') as out:
                for chunk in uploaded_file.chunks():
                    out.write(chunk)
            
            try:
                # Rebuild KB
                config = get_rag_config()
                rag = ContractRAG(config)
                rag.build_knowledge_base(str(upload_folder))
                return render(request, 'upload_result.html', {'saved': [uploaded_file.name], 'error': None})
            except Exception as e:
                return render(request, 'upload_result.html', {'saved': [], 'error': str(e)})

    return render(request, 'django_index.html', {'upload_form': form})


def ask(request):
    if request.method != 'POST':
        return redirect('ragapp:index')
    form = AskForm(request.POST)
    if form.is_valid():
        question = form.cleaned_data['question']
        try:
            config = get_rag_config()
            rag = ContractRAG(config)
            rag.load_knowledge_base()
            result = rag.answer_question(question)
            return render(request, 'answer.html', {'question': question, 'result': result, 'error': None})
        except Exception as e:
            return render(request, 'answer.html', {'question': question, 'result': None, 'error': str(e)})

    return render(request, 'django_index.html', {'ask_form': form})
