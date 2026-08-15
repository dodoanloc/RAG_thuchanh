import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.bm25_retriever import tokenize_vietnamese_legal
from src.unified_retriever import retrieve


def test_legal_tokenizer_preserves_document_code():
    tokens = tokenize_vietnamese_legal("01/2014/TT-NHNN Điều 50")
    assert "01/2014/tt-nhnn" in tokens
    assert "50" in tokens


def test_unified_retriever_rejects_empty_question():
    with pytest.raises(ValueError):
        retrieve("", method="bm25")


def test_unified_retriever_rejects_unknown_method():
    with pytest.raises(ValueError):
        retrieve("một câu hỏi", method="unknown")


def test_evaluation_artifact_has_four_methods():
    import pandas as pd

    artifact = BASE_DIR / "outputs" / "retrieval_comparison.csv"
    df = pd.read_csv(artifact)
    assert set(df["method"]) == {"bm25", "dense", "hybrid", "hybrid_rerank"}
    assert df["question_id"].nunique() >= 3
