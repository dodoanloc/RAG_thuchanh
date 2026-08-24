"""UC1 grounded lookup with RBAC and audit."""
from __future__ import annotations
import sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from secure_retrieval_adapter import retrieve_secure
from audit_logger import log_event

DENY_MESSAGE = "Truy cập bị từ chối."
FALLBACK = "Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập."

def lookup(question: str, user_role: str, top_k: int = 5) -> dict:
    request_id = str(uuid.uuid4())
    try:
        results = retrieve_secure(question, user_role, top_k=top_k, method="bm25")
    except ValueError:
        log_event(user_id_demo="demo01", user_role=user_role, action="internal_lookup", query=question, retrieval_method="bm25_secure", status="DENIED", request_id=request_id)
        return {"answer": DENY_MESSAGE, "citations": [], "request_id": request_id, "access_scope": "DENY"}
    answer = FALLBACK if not results else "Kết quả chỉ dựa trên tài liệu được phép truy cập: " + " ".join(x["text"].splitlines()[-1][:400] for x in results[:2])
    event = log_event(user_id_demo="demo01", user_role=user_role, action="internal_lookup", query=question, retrieval_method="bm25_secure", retrieved_document_ids=[x["document_id"] for x in results], retrieved_chunk_ids=[x["chunk_id"] for x in results], citation_ids=[x["citation"] for x in results], status="SUCCESS", request_id=request_id)
    return {"answer": answer, "citations": results, "request_id": request_id, "access_scope": user_role, "audit": event}

def run_demo() -> Path:
    rows=[]
    for question, role in [("hồ sơ hợp nhất", "Admin"), ("điều kiện chuyển đổi", "Risk_Manager"), ("quản lý vốn tài sản", "Guest")]:
        result=lookup(question, role, 2)
        rows.append(f"## {role}: {question}\n\nAnswer: {result['answer'][:500]}\n\nCitations: {[x['citation'] for x in result['citations']]}\nRequest ID: {result['request_id']}\n")
    path=Path(__file__).resolve().parents[1]/"outputs/internal_lookup_demo.md"
    path.write_text("# Internal Lookup Demo\n\n"+"\n".join(rows), encoding="utf-8")
    return path

if __name__ == "__main__":
    result=lookup("quy định tín dụng", "Staff", 2)
    assert result["citations"] and all(x["citation"] and x["chunk_id"] for x in result["citations"])
    print(run_demo())
    print("INTERNAL LOOKUP: PASS")
