#!/usr/bin/env python3
"""Buổi 16: tạo Golden Dataset, chạy Secure RAG, chấm Ragas, xuất báo cáo.

Chạy: .venv/bin/python scripts/evaluate_rag_pipeline.py
Có HF_TOKEN: chạy Generator/Judger qua HF Router. Không có token: tự động chạy
offline proxy, không gọi mạng; kết quả ghi rõ là proxy, không giả danh Ragas LLM judge.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import random
import re
import sys
from pathlib import Path
from statistics import mean
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
CORPUS_PATH = BASE_DIR / "data/processed/chunks_secure.csv"
EVAL_DIR = BASE_DIR / "data/eval"
QA_PATH = EVAL_DIR / "qa_dataset.csv"
RESULTS_PATH = EVAL_DIR / "evaluation_results.csv"
REPORT_PATH = BASE_DIR / "outputs/ragas_evaluation_report.md"
ROLES = ["Admin", "HR", "Risk_Manager", "Staff"]
HF_BASE_URL = "https://router.huggingface.co/v1"
GENERATOR_MODEL = "Qwen/Qwen3.5-9B:deepinfra"
JUDGER_MODEL = "openai/gpt-oss-20b:deepinfra"
METRICS = ("context_precision", "context_recall", "faithfulness", "answer_relevancy")


def load_environment() -> bool:
    """Load project-local .env without exposing credentials."""
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError("Thiếu python-dotenv. Cài dependencies trước.") from exc
    load_dotenv(BASE_DIR / ".env")
    return bool(os.getenv("HF_TOKEN"))


def parse_json_object(value: str) -> dict[str, Any]:
    """Parse JSON object, including ```json fenced model output."""
    cleaned = value.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("Model không trả về JSON object")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("JSON output phải là object")
    return parsed


def parse_contexts(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            parsed = [value]
    return [str(item) for item in parsed] if isinstance(parsed, list) else [str(parsed)]


def call_chat(model: str, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
    from openai import OpenAI
    client = OpenAI(base_url=HF_BASE_URL, api_key=os.environ["HF_TOKEN"])
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        extra_body={"reasoning": {"enabled": False}},
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError(f"{model} trả về nội dung trống")
    return content.strip()


def classify_usecase(row: dict[str, str]) -> str:
    text = " ".join(row.get(k, "") for k in ("title", "chapter", "section", "text")).lower()
    if any(token in text for token in ("nhân sự", "lao động", "cán bộ", "người lao động", "tuyển dụng")):
        return "HR"
    if any(token in text for token in ("rủi ro", "an toàn", "kiểm soát", "bảo mật", "phòng chống", "tiền mặt")):
        return "Risk"
    return "Common"


def read_corpus() -> list[dict[str, str]]:
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Không có corpus: {CORPUS_PATH}")
    with CORPUS_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def select_source_chunks(rows: list[dict[str, str]], count: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)
    groups: dict[str, list[dict[str, str]]] = {"HR": [], "Risk": [], "Common": []}
    for row in rows:
        groups[classify_usecase(row)].append(row)
    selected: list[dict[str, str]] = []
    for group in groups.values():
        selected.extend(rng.sample(group, min(4, len(group))))
    remaining = [row for row in rows if row not in selected]
    selected.extend(rng.sample(remaining, max(0, min(count, len(rows)) - len(selected))))
    return selected[:count]


def generate_golden_dataset(rows: list[dict[str, str]], question_count: int, seed: int) -> list[dict[str, str]]:
    sources = select_source_chunks(rows, count=min(15, max(10, question_count)), seed=seed)
    dataset: list[dict[str, str]] = []
    difficulties = ["easy", "medium", "hard"]
    for index in range(question_count):
        source = sources[index % len(sources)]
        usecase = classify_usecase(source)
        difficulty = difficulties[index % len(difficulties)]
        prompt = f"""Bạn tạo dữ liệu đánh giá RAG tiếng Việt từ DUY NHẤT đoạn văn bản pháp lý dưới đây.
Trả JSON thuần, đúng schema: {{\"question\": \"...\", \"ground_truth\": \"...\"}}.
Câu hỏi mức {difficulty}, use case {usecase}. Đáp án chuẩn ngắn, chỉ nêu dữ kiện có trong đoạn. Không bịa, không dẫn chiếu ngoài đoạn.

ĐOẠN VĂN BẢN:
{source.get('text', '')[:6000]}"""
        generated = parse_json_object(call_chat(GENERATOR_MODEL, [{"role": "user", "content": prompt}], 0.2))
        question, truth = str(generated.get("question", "")).strip(), str(generated.get("ground_truth", "")).strip()
        if not question or not truth:
            raise RuntimeError(f"Golden record {index + 1} thiếu question hoặc ground_truth")
        dataset.append({
            "id": str(index + 1), "usecase": usecase, "difficulty": difficulty,
            "source_chunk_id": source.get("chunk_id", ""), "question": question,
            "ground_truth": truth,
        })
    return dataset


def generate_offline_golden_dataset(rows: list[dict[str, str]], question_count: int, seed: int) -> list[dict[str, str]]:
    """Create reproducible QA without an external model or token."""
    sources = select_source_chunks(rows, count=min(15, max(10, question_count)), seed=seed)
    difficulties = ["easy", "medium", "hard"]
    result = []
    for index in range(question_count):
        source = sources[index % len(sources)]
        text = re.sub(r"\s+", " ", source.get("text", "")).strip()
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]
        truth = sentences[0][:500] if sentences else text[:500]
        article = source.get("article", "quy định này") or "quy định này"
        result.append({
            "id": str(index + 1), "usecase": classify_usecase(source),
            "difficulty": difficulties[index % 3], "source_chunk_id": source.get("chunk_id", ""),
            "question": f"Nội dung chính của {article} là gì?", "ground_truth": truth,
        })
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Không có dữ liệu để ghi {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def retrieve_contexts(question: str, top_k: int) -> list[str]:
    # BM25 path avoids heavy model downloads; still uses SecureRetriever access filter.
    from src.secure_retriever import retrieve
    items = retrieve(question, ROLES, method="bm25", top_k=top_k, candidate_k=max(20, top_k))
    return [str(item.get("text", "")) for item in items if item.get("text")]


def generate_answer(question: str, contexts: list[str]) -> str:
    formatted = "\n\n".join(f"[Context {i + 1}]\n{text}" for i, text in enumerate(contexts))
    prompt = f"""Trả lời tiếng Việt dựa CHỈ trên contexts. Không suy diễn. Nếu contexts không đủ, trả lời: \"Không đủ thông tin trong ngữ cảnh được cung cấp.\" Trả lời ngắn, trực tiếp; không mô tả reasoning.

QUESTION: {question}

CONTEXTS:
{formatted}"""
    return call_chat(GENERATOR_MODEL, [{"role": "user", "content": prompt}], 0.0)


def generate_offline_answer(contexts: list[str]) -> str:
    """Conservative local answer: return first retrieved evidence sentence."""
    text = re.sub(r"\s+", " ", contexts[0]).strip() if contexts else ""
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]
    return sentences[0][:500] if sentences else "Không đủ thông tin trong ngữ cảnh được cung cấp."


def _token_set(value: str) -> set[str]:
    return set(re.findall(r"[\wÀ-ỹ]+", value.lower()))


def evaluate_offline_proxy(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic smoke/evaluation proxy used only when HF_TOKEN is absent."""
    for row in rows:
        question_tokens = _token_set(row["question"])
        truth_tokens = _token_set(row["ground_truth"])
        answer_tokens = _token_set(row["answer"])
        context_tokens = _token_set(" ".join(row["contexts"]))
        overlap = len(truth_tokens & context_tokens) / max(1, len(truth_tokens))
        answer_overlap = len(question_tokens & answer_tokens) / max(1, len(question_tokens))
        faithfulness = len(answer_tokens & context_tokens) / max(1, len(answer_tokens))
        row.update({
            "context_precision": round(min(1.0, overlap), 4),
            "context_recall": round(min(1.0, overlap), 4),
            "faithfulness": round(min(1.0, faithfulness), 4),
            "answer_relevancy": round(min(1.0, max(answer_overlap, 0.5)), 4),
        })
    return rows


def evaluate_with_ragas(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run four requested Ragas metrics through independent GPT-OSS judge."""
    try:
        from datasets import Dataset
        from langchain_openai import ChatOpenAI
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness
    except ImportError as exc:
        raise RuntimeError("Ragas dependencies lỗi hoặc thiếu; xem hướng dẫn cài đặt.") from exc
    judge = ChatOpenAI(model=JUDGER_MODEL, base_url=HF_BASE_URL, api_key=os.environ["HF_TOKEN"], temperature=0.0, model_kwargs={"reasoning": {"enabled": False}})
    data = Dataset.from_list([{
        "question": row["question"], "answer": row["answer"], "contexts": row["contexts"],
        "ground_truth": row["ground_truth"],
    } for row in rows])
    result = evaluate(data, metrics=[context_precision, context_recall, faithfulness, answer_relevancy], llm=judge, raise_exceptions=True)
    metric_rows = result.to_pandas().to_dict(orient="records")
    for row, scores in zip(rows, metric_rows, strict=True):
        for metric in METRICS:
            row[metric] = float(scores[metric])
    return rows


def build_report(rows: list[dict[str, Any]], evaluation_mode: str = "ragas-llm-judge") -> str:
    averages = {metric: mean(float(row[metric]) for row in rows) for metric in METRICS}
    labels = {
        "context_precision": "Context Precision", "context_recall": "Context Recall",
        "faithfulness": "Faithfulness", "answer_relevancy": "Answer Relevancy",
    }
    lines = ["# Báo cáo Ragas — Buổi 16", "", f"Chế độ: **{evaluation_mode}**", f"Số câu đánh giá: **{len(rows)}**", "", "## Điểm trung bình", "", "| Metric | Điểm |", "|---|---:|"]
    lines += [f"| {labels[key]} | {averages[key]:.3f} |" for key in METRICS]
    low = [row for row in rows if any(float(row[m]) < 0.7 for m in METRICS)]
    lines += ["", "## Câu cần phân tích (< 0.7)", ""]
    if not low:
        lines.append("Không có câu nào dưới ngưỡng 0.7.")
    else:
        for row in low:
            scores = ", ".join(f"{labels[m]}={float(row[m]):.2f}" for m in METRICS if float(row[m]) < 0.7)
            lines += [f"### Câu {row['id']} — {scores}", f"- Hỏi: {row['question']}", f"- Đáp án sinh: {row['answer']}", "- Nhận định: kiểm tra chunk truy xuất, top_k và tính nghiêm ngặt prompt.", ""]
    lines += ["## Đề xuất tối ưu", ""]
    if averages["context_recall"] < 0.7:
        lines.append("- Context Recall thấp: tăng `top_k`, query expansion, mở rộng graph lân cận.")
    if averages["context_precision"] < 0.7:
        lines.append("- Context Precision thấp: hiệu chỉnh RRF và dùng Cross-Encoder reranker.")
    if averages["faithfulness"] < 0.8:
        lines.append("- Faithfulness thấp: rút ngắn/lọc contexts, siết prompt chỉ dùng evidence.")
    if averages["answer_relevancy"] < 0.8:
        lines.append("- Answer Relevancy thấp: ép trả lời trực tiếp, ngắn và thêm few-shot examples.")
    if not any([averages["context_recall"] < .7, averages["context_precision"] < .7, averages["faithfulness"] < .8, averages["answer_relevancy"] < .8]):
        lines.append("- Duy trì benchmark; thử top_k và reranker trên tập test lớn hơn trước khi triển khai.")
    lines += ["", "## An toàn dữ liệu", "", "Corpus nội bộ được gửi tới HF Router trong run này. Môi trường thật phải dùng endpoint nội bộ/đã được phê duyệt hoặc judge chạy local; không gửi tài liệu mật sang API công cộng."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--seed", type=int, default=16)
    parser.add_argument("--reuse-dataset", action="store_true")
    args = parser.parse_args()
    if args.questions < 1:
        raise ValueError("--questions phải lớn hơn 0")
    has_hf_token = load_environment()
    mode = "ragas-llm-judge" if has_hf_token else "offline-proxy"
    corpus_rows = read_corpus()
    try:
        if not has_hf_token:
            print("HF_TOKEN không có; chạy offline-proxy, không gọi HF Router.")
        qa_rows = read_csv(QA_PATH) if args.reuse_dataset and QA_PATH.exists() else (generate_golden_dataset(corpus_rows, args.questions, args.seed) if has_hf_token else generate_offline_golden_dataset(corpus_rows, args.questions, args.seed))
        write_csv(QA_PATH, qa_rows)
        run_rows: list[dict[str, Any]] = []
        for row in qa_rows:
            contexts = retrieve_contexts(row["question"], args.top_k)
            if not contexts:
                raise RuntimeError(f"Không truy xuất được context cho câu {row['id']}")
            run_rows.append({**row, "contexts": contexts, "answer": generate_answer(row["question"], contexts) if has_hf_token else generate_offline_answer(contexts)})
        scored = evaluate_with_ragas(run_rows) if has_hf_token else evaluate_offline_proxy(run_rows)
    except Exception as exc:
        if not has_hf_token:
            raise
        print(f"HF Router/Ragas lỗi ({exc}); tự động chuyển offline-proxy.")
        mode = "offline-proxy"
        qa_rows = generate_offline_golden_dataset(corpus_rows, args.questions, args.seed)
        write_csv(QA_PATH, qa_rows)
        run_rows = []
        for row in qa_rows:
            contexts = retrieve_contexts(row["question"], args.top_k)
            if not contexts:
                raise RuntimeError(f"Không truy xuất được context cho câu {row['id']}")
            run_rows.append({**row, "contexts": contexts, "answer": generate_offline_answer(contexts)})
        scored = evaluate_offline_proxy(run_rows)
    serializable = [{**row, "contexts": json.dumps(row["contexts"], ensure_ascii=False)} for row in scored]
    write_csv(RESULTS_PATH, serializable)
    report = build_report(serializable, evaluation_mode=mode)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print("RAGAS_AVERAGES")
    for metric in METRICS:
        print(f"{metric}: {mean(float(row[metric]) for row in serializable):.3f}")
    print("\nREPORT_SAMPLE\n" + "\n".join(report.splitlines()[:24]))
    print(f"\nArtifacts: {QA_PATH}\n{RESULTS_PATH}\n{REPORT_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
