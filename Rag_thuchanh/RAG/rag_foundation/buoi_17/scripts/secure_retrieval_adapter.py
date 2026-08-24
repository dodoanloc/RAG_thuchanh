"""Adapter reusing Buoi 14 SecureRetriever; no retriever rebuild."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT / ".." / "buoi_14"
if not PREVIOUS.exists(): PREVIOUS = ROOT / ".." / "buoi_16"
sys.path.insert(0, str(PREVIOUS.resolve()))
from src.secure_retriever import retrieve as _retrieve  # type: ignore
from rbac import validate_roles

def retrieve_secure(query: str, user_role: str | list[str], top_k: int = 5, method: str = "bm25") -> list[dict]:
    roles = sorted(validate_roles(user_role if isinstance(user_role, list) else [user_role]))
    raw = _retrieve(query, roles, method=method, top_k=top_k, candidate_k=max(20, top_k))
    result = []
    for rank, item in enumerate(raw, 1):
        result.append({
            "rank": rank, "chunk_id": item.get("chunk_id", ""),
            "document_id": item.get("document_id", ""), "title": item.get("title", ""),
            "article": item.get("article", ""), "text": item.get("text", ""),
            "citation": item.get("citation", ""), "allowed_roles": item.get("allowed_roles", []),
            "access_decision": "ALLOW", "retrieval_method": item.get("retrieval_method", method),
            "score": item.get("score", item.get("retrieval_score", 0.0)),
        })
    return result

if __name__ == "__main__":
    print(retrieve_secure("quy định tín dụng", "Staff", top_k=1))
