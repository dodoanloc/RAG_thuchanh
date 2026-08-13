"""Buổi 10 — Dashboard trực quan dữ liệu Graph RAG Neo4j."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from buoi_10_db import get_db_config, get_neo4j_driver

st.set_page_config(page_title="Graph RAG Neo4j | Buổi 10", page_icon="🕸️", layout="wide")
st.title("🕸️ Buổi 10 — Graph RAG Foundation: Neo4j Dashboard")
st.caption("Kết quả app chạy trực tiếp từ Neo4j: văn bản, chunks, vector index và liên kết đồ thị.")


@st.cache_data(ttl=30, show_spinner=False)
def load_dashboard() -> dict:
    cfg = get_db_config()
    driver = get_neo4j_driver()
    try:
        driver.verify_connectivity()
        with driver.session(database=cfg["database"]) as session:
            counts = session.run("""
                MATCH (d:Document) WITH count(d) AS documents
                MATCH (c:Chunk) WITH documents, count(c) AS chunks
                MATCH (a:Document)-[r]->(b:Document)
                RETURN documents, chunks, count(r) AS document_relations
            """).single().data()
            rels = session.run("""
                MATCH (a:Document)-[r]->(b:Document)
                RETURN coalesce(a.so_ky_hieu, a.id) AS `Văn bản nguồn`,
                       type(r) AS `Quan hệ`,
                       r.relationship AS `Diễn giải`,
                       coalesce(b.so_ky_hieu, b.id) AS `Văn bản đích`
                ORDER BY `Quan hệ`, `Văn bản nguồn`
            """).data()
            rel_summary = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS `Loại quan hệ`, count(r) AS `Số lượng`
                ORDER BY `Số lượng` DESC
            """).data()
            docs = session.run("""
                MATCH (d:Document)
                RETURN coalesce(d.so_ky_hieu, d.id) AS `Số ký hiệu`,
                       d.loai_van_ban AS `Loại`, d.co_quan_ban_hanh AS `Cơ quan`,
                       d.tinh_trang_hieu_luc AS `Hiệu lực`, d.title AS `Tên văn bản`
                ORDER BY `Số ký hiệu`
            """).data()
            index_names = [r["name"] for r in session.run("SHOW VECTOR INDEXES")]
        return {"ok": True, "db": cfg["database"], "counts": counts, "rels": rels,
                "rel_summary": rel_summary, "docs": docs, "indexes": index_names}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        driver.close()


with st.sidebar:
    st.header("⚙️ Kết nối Neo4j")
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        load_dashboard.clear()
        st.rerun()

with st.spinner("Đang đọc đồ thị Neo4j..."):
    data = load_dashboard()

if not data["ok"]:
    st.error(f"Không kết nối được Neo4j: {data['error']}")
    st.stop()

st.success(f"Neo4j kết nối thành công — Database `{data['db']}`")
st.caption("Quan hệ cần kiểm tra gồm THAY_THE, CAN_CU, HOP_NHAT, SUA_DOI_BO_SUNG và VAN_BAN_BO_SUNG.")
counts = data["counts"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Văn bản pháp luật", counts["documents"])
c2.metric("Chunks đã nạp", f"{counts['chunks']:,}")
c3.metric("Liên kết văn bản", counts["document_relations"])
c4.metric("Vector index", ", ".join(data["indexes"]) or "Chưa có")

left, right = st.columns([1, 1])
with left:
    st.subheader("Phân bố quan hệ toàn đồ thị")
    st.bar_chart(pd.DataFrame(data["rel_summary"]).set_index("Loại quan hệ"))
with right:
    st.subheader("8 liên kết giữa các văn bản")
    st.dataframe(pd.DataFrame(data["rels"]), use_container_width=True, hide_index=True)

st.subheader("Danh mục 15 văn bản đã nạp")
st.dataframe(pd.DataFrame(data["docs"]), use_container_width=True, hide_index=True)

st.info("Kết quả này được truy vấn trực tiếp từ Neo4j qua Bolt; bấm “Làm mới dữ liệu” để chạy lại truy vấn.")
