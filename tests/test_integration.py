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

    # config: point to the temporary data dir and models output inside tmp_path
    cfg = {
        "data_path": str(data_dir),
        "models_path": str(tmp_path / "models"),
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "qa_model": "deepset/minilm-uncased-squad2",
        "chunk_size": 400,
        "chunk_overlap": 50,
    }

    # build KB (this will download models on first run)
    rag = ContractRAG(cfg)
    rag.build_knowledge_base()

    # give a short sleep to ensure files are flushed on CI
    time.sleep(1)

    # run a simple query
    answer = rag.answer_question("What is the contract term?")
    assert answer is not None and isinstance(answer, str)

    # clean up to avoid leaving large files in runner workspace
    shutil.rmtree(cfg["models_path"], ignore_errors=True)