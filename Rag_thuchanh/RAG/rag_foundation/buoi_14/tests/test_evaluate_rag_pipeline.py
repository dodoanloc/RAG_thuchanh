from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))


def test_report_contains_four_metrics():
    from scripts.evaluate_rag_pipeline import build_report

    rows = [{
        "question": "Q", "ground_truth": "A", "answer": "A", "contexts": "[\"ctx\"]",
        "context_precision": "0.8", "context_recall": "0.7",
        "faithfulness": "0.9", "answer_relevancy": "0.8",
    }]
    report = build_report(rows, evaluation_mode="offline-proxy")
    for metric in ("Context Precision", "Context Recall", "Faithfulness", "Answer Relevancy"):
        assert metric in report
    assert "offline-proxy" in report


def test_parse_json_object_accepts_fenced_json():
    from scripts.evaluate_rag_pipeline import parse_json_object

    assert parse_json_object('```json\n{"question":"Q","ground_truth":"A"}\n```')["question"] == "Q"


def test_script_defines_model_separation():
    from scripts.evaluate_rag_pipeline import GENERATOR_MODEL, JUDGER_MODEL

    assert GENERATOR_MODEL != JUDGER_MODEL
    assert "Qwen" in GENERATOR_MODEL
    assert "gpt-oss" in JUDGER_MODEL


def test_offline_pipeline_runs_without_hf_token(tmp_path, monkeypatch):
    from scripts.evaluate_rag_pipeline import generate_offline_golden_dataset, evaluate_offline_proxy

    rows = [{
        "chunk_id": "c1", "title": "Quy định chung", "chapter": "", "section": "", "text": "Điều 1. Ngân hàng phải lưu hồ sơ tối thiểu 5 năm.",
    }]
    qa = generate_offline_golden_dataset(rows, question_count=2, seed=16)
    assert len(qa) == 2
    scored = evaluate_offline_proxy([{**qa[0], "contexts": [rows[0]["text"]], "answer": rows[0]["text"]}])
    assert all(metric in scored[0] for metric in ("context_precision", "context_recall", "faithfulness", "answer_relevancy"))
    assert all(0 <= float(scored[0][metric]) <= 1 for metric in ("context_precision", "context_recall", "faithfulness", "answer_relevancy"))
