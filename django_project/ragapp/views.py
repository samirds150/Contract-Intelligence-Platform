import os
from pathlib import Path
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from .forms import UploadForm, AskForm

# Reuse existing RAG implementation
from src.rag_system import ContractRAG
import yaml


def get_config():
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)


def index(request):
    upload_form = UploadForm()
    ask_form = AskForm()
    # list files
    upload_folder = Path(settings.MEDIA_ROOT)
    upload_folder.mkdir(parents=True, exist_ok=True)
    files = [p.name for p in upload_folder.glob('*.txt')]
    return render(request, 'django_index.html', {'upload_form': upload_form, 'ask_form': ask_form, 'files': files})


def upload(request):
    if request.method != 'POST':
        return redirect('ragapp:index')

    form = UploadForm(request.POST, request.FILES)
    if form.is_valid():
        files = request.FILES.getlist('files')
        saved = []
        upload_folder = Path(settings.MEDIA_ROOT)
        for f in files:
            dest = upload_folder / f.name
            with open(dest, 'wb') as out:
                for chunk in f.chunks():
                    out.write(chunk)
            saved.append(dest.name)

        # rebuild knowledge base
        config = get_config()
        rag = ContractRAG(config)
        rag.build_knowledge_base(str(upload_folder))

        return render(request, 'upload_result.html', {'saved': saved})

    return render(request, 'django_index.html', {'upload_form': form})


def ask(request):
    if request.method != 'POST':
        return redirect('ragapp:index')

    form = AskForm(request.POST)
    if form.is_valid():
        question = form.cleaned_data['question']
        # load existing knowledge base
        config = get_config()
        rag = ContractRAG(config)
        rag.load_knowledge_base()
        result = rag.answer_question(question)
        return render(request, 'answer.html', {'question': question, 'result': result})

    return render(request, 'django_index.html', {'ask_form': form})
