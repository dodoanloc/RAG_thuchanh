"""
Giao diện Streamlit RAG Foundation - Buổi 07.
Sử dụng trực tiếp các hàm public từ module rag.py (không duplicate logic RAG).
"""

from pathlib import Path
# pyrefly: ignore [missing-import]
import streamlit as st

# Import các hàm từ rag.py trong cùng thư mục
from rag import (
    BASE_DIR,
    load_config,
    get_status,
    index_chunks,
    query_rag,
    ALLOWED_STRATEGIES
)

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="RAG Foundation - Buổi 07",
    page_icon="🔍",
    layout="wide"
)

# Load cấu hình hệ thống
try:
    config = load_config()
except Exception as e:
    st.error(f"Lỗi nạp cấu hình hệ thống: {e}")
    st.stop()

# --- SIDEBAR: CẤU HÌNH VÀ TRẠNG THÁI ---
st.sidebar.title("⚙️ Cấu Hình & Trạng Thái")

# Chọn strategy
strategy_list = sorted(list(ALLOWED_STRATEGIES))
selected_strategy = st.sidebar.selectbox(
    "Chiến lược Chunking (Strategy):",
    options=strategy_list,
    index=strategy_list.index("hierarchical") if "hierarchical" in strategy_list else 0
)

# Chọn Top-k
selected_top_k = st.sidebar.slider(
    "Số lượng kết quả truy xuất (Top-K):",
    min_value=1,
    max_value=10,
    value=config.get("top_k", 5)
)

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Trạng Thái Hệ Thống")

# Lấy trạng thái read-only cho strategy đang chọn
try:
    status_info = get_status(strategy=selected_strategy)
except Exception as e:
    st.sidebar.error(f"Lỗi đọc trạng thái collection: {e}")
    status_info = {
        "has_api_key": config["has_api_key"],
        "embedding_model": config["embedding_model"],
        "embedding_dim": config["embedding_dim"],
        "collection_name": "N/A",
        "collection_exists": False,
        "record_count": 0
    }

st.sidebar.markdown(f"**API Key**: {'✅ Có' if status_info['has_api_key'] else '❌ Thiếu'}")
st.sidebar.markdown(f"**Embedding Model**: `{status_info['embedding_model']}`")
st.sidebar.markdown(f"**Embedding Dim**: `{status_info['embedding_dim']}`")
st.sidebar.markdown(f"**Generation Model**: `{config['generation_model']}`")
st.sidebar.markdown(f"**Collection Name**: `{status_info['collection_name']}`")
st.sidebar.markdown(f"**Collection Tồn Tại**: {'✅ Có' if status_info['collection_exists'] else '⚠️ Chưa'}")
st.sidebar.markdown(f"**Số Chunk Hiện Tại**: `{status_info['record_count']}`")
st.sidebar.markdown(f"**RAG_MAX_DISTANCE**: `{config['max_distance']}`")

if not status_info['has_api_key']:
    st.sidebar.warning("⚠️ Chưa có API Key! Hãy điền `GEMINI_API_KEY` vào file `.env`.")

# --- NỘI DUNG CHÍNH ---
st.title("🔍 RAG Foundation - Buổi 07")
st.caption("Hệ thống Hỏi-Đáp RAG với Google GenAI, ChromaDB và Grounding Precision.")

tab_query, tab_index = st.tabs(["💬 Hỏi - Đáp RAG", "📦 Index Dữ Liệu Vector"])

# --- TAB 1: HỎI - ĐÁP RAG ---
with tab_query:
    st.header("Đặt Câu Hỏi Cho Hệ Thống RAG")

    question_input = st.text_area(
        "Nhập câu hỏi của bạn (tối đa 2000 ký tự):",
        placeholder="Ví dụ: Quy định về cơ cấu lại thời hạn trả nợ như thế nào?",
        height=100
    )

    btn_query = st.button("🚀 Gửi Câu Hỏi", type="primary", use_container_width=True)

    if btn_query:
        clean_q = question_input.strip()
        if not clean_q:
            st.warning("⚠️ Vui lòng nhập nội dung câu hỏi trước khi gửi.")
        elif not config["has_api_key"]:
            st.error("❌ Chưa cấu hình GEMINI_API_KEY trong file `.env`!")
        elif not status_info["collection_exists"]:
            st.warning(f"⚠️ Collection cho strategy '{selected_strategy}' chưa tồn tại. Hãy sang tab 'Index Dữ Liệu Vector' để nạp dữ liệu trước.")
        elif status_info["record_count"] == 0:
            st.warning(f"⚠️ Collection cho strategy '{selected_strategy}' hiện chưa có record nào. Hãy nạp dữ liệu trước.")
        else:
            with st.spinner("🔍 Đang truy vấn vector và sinh câu trả lời..."):
                try:
                    query_res = query_rag(
                        question=clean_q,
                        strategy=selected_strategy,
                        top_k=selected_top_k
                    )
                    st.session_state["query_result"] = query_res
                except Exception as e:
                    st.error(f"❌ Lỗi khi thực hiện truy vấn RAG: {e}")

    # Hiển thị kết quả query từ session_state
    if "query_result" in st.session_state:
        res = st.session_state["query_result"]
        st.markdown("---")

        # Hiển thị Status Badge
        status_val = res.get("status", "unknown")
        if status_val == "answered":
            st.success("✅ Trạng thái: Answered (Đã trả lời từ ngữ cảnh đạt ngưỡng)")
        elif status_val == "insufficient_evidence":
            st.warning("⚠️ Trạng thái: Insufficient Evidence (Không tìm thấy đủ thông tin liên quan)")
        elif status_val == "retrieval_only":
            st.info("ℹ️ Trạng thái: Retrieval Only (Đã truy xuất nguồn nhưng chưa tạo được câu trả lời tổng hợp)")

        # Câu trả lời
        st.subheader("💡 Câu Trả Lời")
        st.markdown(res.get("answer", ""))

        # Cảnh báo (nếu có)
        if res.get("warnings"):
            for w in res["warnings"]:
                st.warning(f"⚠️ {w}")

        # Trích dẫn (Citations)
        if res.get("citations"):
            st.subheader("📚 Danh Sách Trích Dẫn (Citations Mapped)")
            for cit in res["citations"]:
                st.info(f"📌 **[{cit['evidence_id']}]**: {cit['display']}")

        # Nguồn tham khảo (Evidences)
        st.markdown("---")
        st.subheader("📖 Nguồn Tham Khảo (Retrieved Evidences)")
        st.caption(f"Khoảng cách vector (Distance) thấp hơn thể hiện độ tương đồng cao hơn. Ngưỡng lọc tin cậy `RAG_MAX_DISTANCE = {config['max_distance']}`.")

        evidences = res.get("evidence", [])
        if not evidences:
            st.info("Chưa có evidence nào được truy xuất.")
        else:
            for ev in evidences:
                p_str = f"tr. {ev['page_start']}" if ev['page_start'] == ev['page_end'] else f"tr. {ev['page_start']}-{ev['page_end']}"
                status_tag = "✅ ĐẠT GATE" if ev["accepted"] else "❌ BỊ LOẠI (> Threshold)"
                summary_label = f"[{ev['evidence_id']}] [{status_tag}] {ev['source']} – {p_str} – Chunk: {ev['chunk_id']} (Distance: {ev['distance']:.4f})"

                with st.expander(summary_label):
                    st.markdown(f"**Evidence ID**: `{ev['evidence_id']}`")
                    st.markdown(f"**File nguồn**: `{ev['source']}`")
                    st.markdown(f"**Trang**: `{p_str}`")
                    st.markdown(f"**Chunk ID**: `{ev['chunk_id']}`")
                    st.markdown(f"**Khoảng cách Distance**: `{ev['distance']:.4f}`")
                    st.markdown(f"**Đạt Confidence Gate**: {'Có' if ev['accepted'] else 'Không (Vượt ngưỡng RAG_MAX_DISTANCE)'}")
                    st.markdown("**Nội dung đoạn văn (Text):**")
                    st.code(ev["text"], language="text")

# --- TAB 2: INDEX DỮ LIỆU VECTOR ---
with tab_index:
    st.header("Index Dữ Liệu Vector Vào ChromaDB")
    st.caption("Nạp toàn bộ dữ liệu chunks JSON của Buổi 05 vào ChromaDB persistent storage.")

    reset_flag = st.checkbox("🔄 Reset collection trước khi index (xóa collection cũ của strategy này)", value=False)
    btn_index = st.button("⚡ Index Dữ Liệu Ngay", type="primary")

    if btn_index:
        if not config["has_api_key"]:
            st.error("❌ Chưa cấu hình GEMINI_API_KEY trong file `.env`! Vui lòng điền API key trước khi index.")
        else:
            with st.spinner(f"⏳ Đang nạp và tạo vector embeddings cho strategy '{selected_strategy}'..."):
                try:
                    idx_res = index_chunks(
                        strategy=selected_strategy,
                        reset=reset_flag
                    )
                    st.session_state["index_result"] = idx_res
                    st.success("🎉 Index dữ liệu thành công!")
                except Exception as e:
                    st.error(f"❌ Lỗi khi thực hiện index dữ liệu: {e}")

    if "index_result" in st.session_state:
        res_idx = st.session_state["index_result"]
        st.markdown("---")
        st.subheader("📊 Kết Quả Index Gần Nhất")
        col1, col2, col3 = st.columns(3)
        col1.metric("Strategy", res_idx.get("strategy", ""))
        col2.metric("Số Chunk Đã Nạp", res_idx.get("indexed_chunks", 0))
        col3.metric("Tổng Record Trong Col", res_idx.get("total_in_collection", 0))
        st.info(f"Tên Collection: `{res_idx.get('collection_name', '')}`")
