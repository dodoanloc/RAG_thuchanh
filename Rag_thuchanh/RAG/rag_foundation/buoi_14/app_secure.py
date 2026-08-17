"""Streamlit RBAC demo for Buổi 15."""
from __future__ import annotations
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
from src.config import RBAC_CONFIG  # noqa: E402
from src.secure_retriever import retrieve  # noqa: E402

st.set_page_config(page_title="Secure RAG — Buổi 15", layout="wide")
st.title("Secure Retrieval Pipeline — RBAC")
st.caption("Lọc quyền trước BM25/Dense/Hybrid/Reranker")

with st.sidebar:
    st.header("Cấu hình")
    roles = st.multiselect("Vai trò của bạn", RBAC_CONFIG["roles"], default=[RBAC_CONFIG["default_role"]])
    method = st.selectbox("Method", ["bm25", "dense", "hybrid", "hybrid_rerank"], index=3)
    top_k = st.slider("top_k", 1, 20, 5)
    candidate_k = st.slider("candidate_k", max(5, top_k), 100, 20)

query = st.text_input("Câu hỏi", placeholder="Ví dụ: Quy trình phê duyệt hạn mức tín dụng?")
if st.button("Tìm kiếm", type="primary", disabled=not bool(roles)):
    if not query.strip():
        st.warning("Nhập câu hỏi trước.")
    else:
        with st.spinner("Đang tìm kiếm an toàn..."):
            try:
                results = retrieve(query, roles, method, top_k, candidate_k)
                st.session_state["results"] = results
                st.session_state["query"] = query
            except Exception as exc:
                st.error(f"Lỗi retrieval: {exc}")

results = st.session_state.get("results", [])
if query and results:
    st.subheader(f"Kết quả ({len(results)})")
    for item in results:
        with st.container(border=True):
            st.markdown(f"**{item.get('rank', '?')}. {item.get('citation', item.get('chunk_id', ''))}**")
            st.caption(f"Quyền xem: {item.get('allowed_roles', [])} · Score: {item.get('score', item.get('rerank_score', ''))}")
            st.write(item.get("text", ""))
elif st.session_state.get("query"):
    st.info("Không có kết quả trong phạm vi quyền đã chọn.")

st.divider()
st.caption("Security rule: ứng viên bị cấm bị loại trước Hybrid Fusion và Cross-Encoder Reranker.")
