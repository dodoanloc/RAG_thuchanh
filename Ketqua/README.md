# Kết quả chạy thử

Chạy ngày 12-08-2026, môi trường Linux Python 3.11, Streamlit headless.

| Buổi | Ảnh | Kết quả thực tế |
|---|---|---|
| 05 | `buoi_05.png` | UI chạy; nạp sẵn reports/chunks từ `output/`. |
| 06 | `buoi_06.png` | UI chạy; index thành công 510 chunks thuộc 3 tài liệu. |
| 07 | `buoi_07.png` | UI chạy. Chức năng index/hỏi đáp cần `GEMINI_API_KEY`. |
| 08 | `buoi_08.png` | UI chạy; nhận 318 hierarchical chunks. Vector index/hỏi đáp cần `GEMINI_API_KEY`. |
| 09 | `buoi_09.png` | UI chạy. Pipeline cần `GEMINI_API_KEY` để build/index hierarchy và truy vấn. |
| 10 | `buoi_10.png`, `buoi_10_run.log` | Script xác minh đã chạy nhưng dừng tại Neo4j `localhost:7687`: connection refused. Máy chưa có Neo4j local. |
| 11 | `buoi_11.png` | UI chạy, mô hình embedding MSMARCO CPU tải thành công. Chức năng Graph RAG bị chặn vì Neo4j `localhost:7687` chưa chạy; sinh trả lời cần `GEMINI_API_KEY`. |

Không đưa API key, mật khẩu Neo4j, hoặc dữ liệu bí mật vào repo.
