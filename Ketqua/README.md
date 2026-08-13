# Kết quả chạy thử

Chạy ngày 12-08-2026, môi trường Linux Python 3.11, Streamlit headless.

| Buổi | Ảnh | Kết quả thực tế |
|---|---|---|
| 05 | `buoi_05.png` | UI khám phá chunks chạy; lọc nội dung tài liệu, hiển thị số liệu chunk theo 3 chiến lược. |
| 06 | `buoi_06.png` | Retrieval Top-3 chạy trên 510 chunks thuộc 3 tài liệu; trả về nguồn/chunk cho câu hỏi cơ cấu lại thời hạn trả nợ. |
| 07 | `buoi_07.png` | RAG trả lời thành công với 318 chunks, citations; embedding `gemini-embedding-001`, generation `openclaw0` qua router cục bộ. |
| 08 | `buoi_08.png` | Advanced RAG `hybrid_rerank` trả lời thành công; BM25 + dense vector + RRF + BGE reranker, kèm evidence/citations. |
| 09 | `buoi_09.png` | Multi-query Parent–Child RAG `multi_parent` trả lời thành công; 3 nguồn, 318 child chunks, 27 parent documents. |
| 10 | `buoi_10.png` | Neo4j xác minh thành công: 15 Documents, 7.381 Chunks, 8 quan hệ Document-to-Document, vector index `chunk_embeddings`. |
| 11 | `buoi_11.png` | Graph RAG Neo4j chạy thành công: 3 chunks trực tiếp, 2 liên kết, 4 chunks đa bước; `openclaw0` trả lời quan hệ thay thế Nghị định 46/2023/NĐ-CP và 73/2016/NĐ-CP. |

`buoi_10_run.log` lưu output xác minh chạy thật. Không đưa API key hoặc mật khẩu Neo4j vào repo.
