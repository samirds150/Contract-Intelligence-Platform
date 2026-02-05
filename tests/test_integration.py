import tempfile
from pathlib import Path
import shutil
import time

import pytest

from src.rag_system import ContractRAG


@pytest.mark.integration
def test_full_rag_pipeline(tmp_path):
    # create a tiny sample document
    data_dir = tmp_path / "data_raw"
    data_dir.mkdir()
    sample = data_dir / "sample_contract.txt"
    sample.write_text(
        """
        This is a sample contract between Company A and Company B. The contract term is 12 months.
        Payment will be made within 30 days of invoice. Confidentiality must be maintained.
        """
    )

    # config: nested structure expected by ContractRAG
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    cfg = {
        "data": {"chunk_size": 400, "chunk_overlap": 50},
        "embedding": {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "faiss_index_path": str(models_dir / "faiss_index.bin"),
            "metadata_path": str(models_dir / "metadata.pkl"),
        },
        "rag": {"top_k": 3, "similarity_threshold": 0.0},
        "model": {"device": "cpu"},
    }

    # build KB (this will download models on first run)
    rag = ContractRAG(cfg)
    rag.build_knowledge_base(str(data_dir))

    # give a short sleep to ensure files are flushed on CI
    time.sleep(1)

    # run a simple query
    result = rag.answer_question("What is the contract term?")
    assert isinstance(result, dict)
    assert 'answer' in result and isinstance(result['answer'], str)

    # clean up to avoid leaving large files in runner workspace
    shutil.rmtree(str(models_dir), ignore_errors=True)
