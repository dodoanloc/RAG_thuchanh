"""Append-only JSONL audit events. Never persist secrets."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json, re, uuid
ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "outputs/audit_log.jsonl"
SECRET = re.compile(r"(?i)(api[_-]?key|password|secret|token|private[_-]?key)")

def _safe(value):
    if isinstance(value, dict): return {k: _safe(v) for k,v in value.items() if not SECRET.search(str(k))}
    if isinstance(value, list): return [_safe(x) for x in value]
    if isinstance(value, str) and SECRET.search(value): return "[REDACTED]"
    return value

def log_event(*, user_id_demo, user_role, action, query, retrieval_method, retrieved_document_ids=None, retrieved_chunk_ids=None, citation_ids=None, rbac_filtered_count=0, status="SUCCESS", request_id=None):
    event = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "request_id": request_id or str(uuid.uuid4()), "user_id_demo": user_id_demo, "user_role": user_role, "action": action, "query": query, "retrieval_method": retrieval_method, "retrieved_document_ids": retrieved_document_ids or [], "retrieved_chunk_ids": retrieved_chunk_ids or [], "citation_ids": citation_ids or [], "rbac_filtered_count": int(rbac_filtered_count), "status": status}
    event = _safe(event); LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f: f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event

def read_events():
    if not LOG.exists(): return []
    return [json.loads(x) for x in LOG.read_text(encoding="utf-8").splitlines() if x.strip()]
