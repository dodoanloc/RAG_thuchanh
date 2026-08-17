"""Secure retrieval: access filtering happens before fusion and reranking."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import hashlib
import json
import pandas as pd

from src.config import validate_roles

BASE_DIR = Path(__file__).resolve().parent.parent
SECURE_CSV = BASE_DIR / "data/processed/chunks_secure.csv"
_COMPONENTS: dict[str, dict[str, Any]] = {}


def _allowed(raw: object) -> list[str]:
    if isinstance(raw, (list, tuple, set)):
        return [str(x) for x in raw]
    try:
        value = json.loads(str(raw))
        return [str(x) for x in value] if isinstance(value, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


def _filtered_csv_for_roles(roles: set[str]) -> Path:
    if not SECURE_CSV.exists():
        raise FileNotFoundError(f"Chưa có {SECURE_CSV}; chạy assign_security_tags.py trước.")
    key = hashlib.sha1("|".join(sorted(roles)).encode("utf-8")).hexdigest()[:12]
    cache = BASE_DIR / "cache_secure"
    cache.mkdir(parents=True, exist_ok=True)
    subset_path = cache / f"chunks_{key}.csv"
    if subset_path.exists() and subset_path.stat().st_mtime >= SECURE_CSV.stat().st_mtime:
        return subset_path
    df = pd.read_csv(SECURE_CSV, dtype=str).fillna("")
    mask = df["allowed_roles"].apply(lambda raw: bool(set(_allowed(raw)) & roles))
    subset = df[mask].copy()
    subset.to_csv(subset_path, index=False)
    return subset_path


def _components(roles: set[str], need_neural: bool) -> dict[str, Any]:
    subset_csv = _filtered_csv_for_roles(roles)
    key = subset_csv.stem
    if key not in _COMPONENTS:
        from src.bm25_retriever import BM25Retriever
        _COMPONENTS[key] = {"bm25": BM25Retriever(subset_csv)}
    components = _COMPONENTS[key]
    if need_neural and "hybrid" not in components:
        from src.dense_retriever import DenseRetriever
        from src.hybrid_retriever import HybridRetriever
        from src.reranker import CrossEncoderReranker
        cache = BASE_DIR / "cache_secure" / key
        dense = DenseRetriever(subset_csv, cache)
        components.update({
            "dense": dense,
            "hybrid": HybridRetriever(components["bm25"], dense, subset_csv, cache),
            "reranker": CrossEncoderReranker(),
        })
    return components


def _decorate(items: list[dict], roles: set[str]) -> list[dict]:
    result = []
    for rank, item in enumerate(items, 1):
        # Secure corpus is already pre-filterable; this second check is defense in depth.
        allowed = _allowed(item.get("allowed_roles", "[]"))
        if allowed and not (set(allowed) & roles):
            continue
        output = dict(item)
        output["rank"] = rank
        output["allowed_roles"] = allowed
        output.setdefault("score", output.get("rerank_score", output.get("rrf_score", output.get("retrieval_score", 0.0))))
        output.setdefault("document_id", "")
        output.setdefault("chunk_id", "")
        result.append(output)
    return result


def retrieve(query: str, user_roles: list[str], method: str = "hybrid_rerank", top_k: int = 5, candidate_k: int = 20) -> list[dict]:
    roles = validate_roles(user_roles)
    if not query or not query.strip():
        raise ValueError("query không được để trống")
    if method not in {"bm25", "dense", "hybrid", "hybrid_rerank"}:
        raise ValueError("method phải là bm25, dense, hybrid hoặc hybrid_rerank")
    components = _components(roles, need_neural=method != "bm25")
    if method == "bm25":
        raw = components["bm25"].search(query, top_k=max(top_k, candidate_k))
    elif method == "dense":
        raw = components["dense"].search(query, top_k=max(top_k, candidate_k))
    elif method == "hybrid":
        raw = components["hybrid"].search(query, top_k=max(top_k, candidate_k), candidate_k=candidate_k)
    else:
        # Secure CSV carries tags into the retriever chunks. Filter BEFORE reranker.
        candidates = components["hybrid"].search(query, top_k=candidate_k, candidate_k=candidate_k)
        candidates = _decorate(candidates, roles)
        raw = components["reranker"].rerank(query, candidates, top_k=top_k)
    results = _decorate(raw, roles)
    return results[:top_k]


def secure_cypher(user_roles: list[str]) -> tuple[str, dict[str, list[str]]]:
    roles = sorted(validate_roles(user_roles))
    query = """
    MATCH (v:VanBan)-[:CONTAINS]->(d:DieuKhoan)
    WHERE any(role IN coalesce(v.allowed_roles, d.allowed_roles, []) WHERE role IN $user_roles)
      AND any(role IN coalesce(d.allowed_roles, v.allowed_roles, []) WHERE role IN $user_roles)
    RETURN v, d
    """
    return query, {"user_roles": roles}
