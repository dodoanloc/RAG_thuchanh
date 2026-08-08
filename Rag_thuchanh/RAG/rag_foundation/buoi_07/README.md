# Buổi 07: RAG Foundation — Production-Grade RAG Pipeline

Dự án **Buổi 07** hướng dẫn xây dựng hệ thống Retrieval-Augmented Generation (RAG) hoàn chỉnh, tuân thủ nghiêm ngặt quy trình kiểm soát chất lượng (Validation), định danh bộ nhớ lưu trữ vector (Collection Identity), lọc ngưỡng tin cậy (Confidence Gate), sinh câu trả lời có căn cứ (Grounding), trích dẫn nguồn thực tế (Citation Mapping) và giao diện trực quan (Streamlit UI).

---

## 1. Mục Tiêu

- Xây dựng quy trình RAG Pipeline chuẩn sản xuất từ dữ liệu chunks JSON có sẵn.
- Quản lý bộ nhớ lưu trữ vector bằng ChromaDB Persistent Client.
- Tạo vector nhúng (Embeddings) bằng Google GenAI API (`gemini-embedding-2`, 768 chiều).
- Sinh câu trả lời grounding chống bịa đặt (Anti-Hallucination) với Gemini (`gemini-3.5-flash-lite`).
- Trích dẫn chính xác nguồn tài liệu (`source`, `page_start`, `page_end`, `chunk_id`).
- Cung cấp giao diện Streamlit UI và bộ công cụ CLI tiện ích.

---

## 2. Quan Hệ Với Buổi 05 Và Buổi 06

- **Buổi 05**: Nguồn cung cấp dữ liệu đầu vào đã được phân mảnh (`rag_foundation/buoi_05/output/chunks/`) và môi trường ảo Python (`rag_foundation/buoi_05/.venv/`). Buổi 07 **không** thực hiện lại OCR, parse PDF hay chunking.
- **Buổi 06**: Dự án tài liệu tham khảo kiến thức.
- **Buổi 07**: Kế thừa dữ liệu và Virtual Environment của Buổi 05 để phát triển toàn bộ pipeline RAG độc lập trong `rag_foundation/buoi_07/`. Tuyệt đối không chỉnh sửa mã nguồn hay dữ liệu của Buổi 05 và Buổi 06.

---

## 3. Sơ Đồ Pipeline RAG

```
┌───────────────────────────────┐
│ Input Chunks JSON (Buổi 05)   │
└──────────────┬────────────────┘
               │ (1. Load & Validate)
               ▼
┌───────────────────────────────┐
│ Chunks Data Contract Check    │
└──────────────┬────────────────┘
               │ (2. Gemini Embedding API)
               ▼
┌───────────────────────────────┐
│ Embeddings Validation (Dim/NaN)│
└──────────────┬────────────────┘
               │ (3. Upsert Batch)
               ▼
┌───────────────────────────────┐
│ ChromaDB Persistent Storage   │
└──────────────┬────────────────┘
               │ (4. Cosine Similarity Query)
               ▼
┌───────────────────────────────┐
│ Confidence Gate Threshold Check│ (distance <= RAG_MAX_DISTANCE)
└──────┬─────────────────┬──────┘
       │ (ACCEPTED)      │ (REJECTED / Empty)
       ▼                 ▼
┌───────────────┐ ┌──────────────────────────────────────────────────┐
│ Grounding LLM │ │ Status: insufficient_evidence                    │
│ Prompt        │ │ "Không tìm thấy đủ thông tin liên quan..."        │
└──────┬────────┘ └──────────────────────────────────────────────────┘
       │ (5. Gemini Generation API)
       ▼
┌───────────────────────────────┐
│ Citation Mapping & Display    │
└──────────────┬────────────────┘
               │ (6. Output Result Schema)
               ▼
┌───────────────────────────────┐
│ CLI Output & Streamlit UI     │
└───────────────────────────────┘
```

---

## 4. Cấu Trúc Thư Mục

```
rag_foundation/buoi_07/
├── SPEC_buoi_07.md         # Đặc tả kỹ thuật chi tiết của hệ thống
├── buoi_07.md              # Tài liệu hướng dẫn bước học
├── rag.py                  # Module lõi RAG (Loader, Validator, Index, Retrieval, Query)
├── app.py                  # Giao diện ứng dụng Streamlit UI
├── requirements.txt        # Thư viện phụ thuộc trực tiếp
├── .env.example            # Cấu hình biến môi trường mẫu
├── .gitignore              # Cấu hình bỏ qua Git (.env, cache, storage/chroma)
├── README.md               # Tài liệu hướng dẫn nghiệm thu và vận hành
├── storage/
│   ├── .gitkeep
│   └── chroma/             # Bộ nhớ lưu trữ đĩa Chroma persistent storage
└── tests/
    ├── __init__.py
    ├── fixtures/
    │   └── chunks_sample.json # Fixture dữ liệu mẫu cho unit testing
    └── test_rag.py         # Bộ kiểm thử tự động 37 test methods (offline)
```

---

## 5. Điều Kiện Đầu Vào

- Thư mục chứa dữ liệu chunks JSON của Buổi 05 phải tồn tại tại đường dẫn: `rag_foundation/buoi_05/output/chunks/`.
- Môi trường Virtual Environment Python của Buổi 05 đã tạo thành công.

---

## 6. Hướng Dẫn Sử Dụng `.venv` Buổi 05

Luôn đứng tại thư mục gốc `RAG` (thư mục chứa trực tiếp `rag_foundation/`) để chạy các câu lệnh:

- **Windows PowerShell**:
  `.\rag_foundation\buoi_05\.venv\Scripts\python.exe`
- **Linux/macOS**:
  `rag_foundation/buoi_05/.venv/bin/python`

---

## 7. Cách Cài Đặt Requirements

Thực thi câu lệnh cài đặt các thư viện bắt buộc trong `requirements.txt`:

- **Windows PowerShell**:
  ```powershell
  $env:PYTHONUTF8=1; & ".\rag_foundation\buoi_05\.venv\Scripts\python.exe" -m pip install -r rag_foundation/buoi_07/requirements.txt
  ```
- **Linux/macOS**:
  ```bash
  rag_foundation/buoi_05/.venv/bin/python -m pip install -r rag_foundation/buoi_07/requirements.txt
  ```

---

## 8. Cách Tạo File `.env` Từ `.env.example`

Sao chép file cấu hình mẫu `.env.example` thành `.env` và điền `GEMINI_API_KEY`:

- **Windows PowerShell**:
  ```powershell
  Copy-Item rag_foundation/buoi_07/.env.example rag_foundation/buoi_07/.env
  ```
- **Linux/macOS**:
  ```bash
  cp rag_foundation/buoi_07/.env.example rag_foundation/buoi_07/.env
  ```

---

## 9. Giải Thích Các Biến Môi Trường

| Biến Môi Trường | Giá Trị Mặc Định | Giải Thích Ý Nghĩa |
|---|---|---|
| `GEMINI_API_KEY` | `""` | Khóa API truy cập dịch vụ Google GenAI |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-2` | Mô hình tạo vector nhúng biểu diễn ngữ cảnh |
| `GEMINI_EMBEDDING_DIM` | `768` | Kích thước số chiều của vector (hỗ trợ 128 - 3072) |
| `GEMINI_GENERATION_MODEL` | `gemini-3.5-flash-lite` | Mô hình ngôn ngữ sinh câu trả lời tổng hợp |
| `DEFAULT_TOP_K` | `5` | Số lượng đoạn văn bản tối đa cần truy xuất (1 - 20) |
| `RAG_MAX_DISTANCE` | `0.45` | Ngưỡng khoảng cách Cosine tối đa để chấp nhận ngữ cảnh |

---

## 10. Lệnh Validate Dữ Liệu CLI

Lệnh đọc và kiểm tra tính hợp lệ của toàn bộ file chunks JSON mà không can thiệp vào cơ sở dữ liệu:

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe rag_foundation/buoi_07/rag.py validate --strategy hierarchical
```

---

## 11. Lệnh Kiểm Tra Trạng Thái Status CLI

Lệnh kiểm tra read-only thông tin collection trong ChromaDB:

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe rag_foundation/buoi_07/rag.py status --strategy hierarchical
```

---

## 12. Lệnh Index Dữ Liệu CLI

Lệnh tạo vector embeddings bằng Gemini API và nạp vào ChromaDB persistent storage:

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe rag_foundation/buoi_07/rag.py index --strategy hierarchical
```

---

## 13. Lệnh Reset Collection Đích CLI

Lệnh xóa riêng collection cũ của strategy tương ứng trước khi nạp lại dữ liệu:

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe rag_foundation/buoi_07/rag.py index --strategy hierarchical --reset
```

---

## 14. Lệnh Query Hỏi-Đáp CLI

Lệnh thực hiện truy vấn Hỏi-Đáp trực tiếp từ giao diện dòng lệnh:

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe rag_foundation/buoi_07/rag.py query --strategy hierarchical --top-k 5 --question "Cơ cấu lại thời hạn trả nợ được quy định như thế nào?"
```

---

## 15. Lệnh Chạy Bộ Kiểm Thử Tự Động (Unit Tests)

Lệnh khởi chạy bộ unit test suite tự động 37 test methods (offline, mock API, temporary storage):

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe -m unittest discover -s rag_foundation/buoi_07/tests -v
```

---

## 16. Lệnh Chạy Giao Diện Streamlit UI

Khởi chạy ứng dụng web tương tác Streamlit:

```powershell
.\rag_foundation\buoi_05\.venv\Scripts\python.exe -m streamlit run rag_foundation/buoi_07/app.py
```

---

## 17. Giải Thích Chi Tiết Khái Niệm Cốt Lõi

- **Strategy**: Chiến lược cắt phân đoạn tài liệu (`hierarchical`, `semantic`, `fixed-size`).
- **Embedding Model & Dimension**: Mô hình và kích thước vector biểu diễn ngữ cảnh toán học.
- **Collection Identity**: Tên định danh duy nhất của bộ nhớ lưu trữ dựa trên công thức `nhnn-<strategy>-<dimension>-<model_hash>`.
- **Top-K**: Số lượng kết quả truy xuất gần nhất theo khoảng cách toán học.
- **Cosine Distance**: Đo lường độ sai lệch vector. Giá trị càng nhỏ càng tương đồng ngữ nghĩa.
- **RAG_MAX_DISTANCE & Confidence Gate**: Cánh cổng lọc chỉ chấp nhận các đoạn văn bản có `distance <= RAG_MAX_DISTANCE` đưa vào prompt.
- **Retrieval-Only**: Trạng thái truy xuất được ngữ cảnh nhưng quá trình sinh câu trả lời từ LLM bị gián đoạn hoặc trả về rỗng.
- **Citation Mapping**: Mã nguồn tự động thay thế nhãn `[E1]`, `[E2]` bằng chuỗi hiển thị trích dẫn thực tế `[Nguồn: ..., tr. N-M, chunk: ...]`.

---

## 18. Cách Dừng Ứng Dụng Streamlit

Để ngắt tiến trình Streamlit server đang chạy trên terminal, nhấn tổ hợp phím **`Ctrl + C`**.

---

## 19. Hướng Dẫn Xử Lý Lỗi (Troubleshooting)

1. **Thiếu package**: Chạy lại lệnh `pip install -r requirements.txt`.
2. **Sai interpreter**: Kiểm tra đường dẫn python đảm bảo trỏ đúng `.venv` của Buổi 05.
3. **Thiếu API Key**: Mở file `rag_foundation/buoi_07/.env` và thêm `GEMINI_API_KEY=your_key`.
4. **Collection rỗng / không tồn tại**: Chạy lệnh `index` trước khi gọi `query`.
5. **Model / Dimension Mismatch**: Chạy lệnh `index --reset` để làm sạch và khởi tạo lại collection tương thích.
6. **Lỗi JSON cấu trúc**: Chạy lệnh `validate` để xem chi tiết record và file gây lỗi.
7. **Lỗi Rate Limit API (HTTP 429)**: Chờ 30-60 giây để quota Free Tier của Gemini tự khôi phục.

---

## 20. Giới Hạn Của Hệ Thống Demo

- Chưa tích hợp mô hình đánh giá lại Reranker hay tìm kiếm lai (Hybrid Search BM25 + Vector).
- Chưa hỗ trợ xử lý OCR tài liệu hình ảnh trực tiếp.
- Chưa có phân quyền người dùng (RBAC) hay lưu trữ lịch sử hội thoại đa lượt (Multi-turn Chat).

---

## 21. Cảnh Báo An Toàn & Bảo Mật

- **Pháp lý**: Câu trả lời của hệ thống mang tính chất tham khảo kỹ thuật, **không** có giá trị thay thế tư vấn pháp lý chính thức.
- **Hiệu chỉnh Ngưỡng**: Giá trị `RAG_MAX_DISTANCE` (0.45) cần được tinh chỉnh thực nghiệm theo từng tập dữ liệu cụ thể.
- **Bảo mật Dữ liệu**: Dữ liệu gửi tới Gemini API khi embedding/generation sẽ chuyển qua dịch vụ đám mây của Google. Chỉ sử dụng dữ liệu được phép chia sẻ public theo chính sách tổ chức.

---

## 22. Kế Hoạch Kiểm Thử Thủ Công (Manual Test Plan)

### Câu A (Trong phạm vi tài liệu):
> *"Cơ cấu lại thời hạn trả nợ được quy định như thế nào?"*

### Câu B (Trong phạm vi tài liệu):
> *"Việc phân loại nợ và trích lập dự phòng được thực hiện như thế nào?"*

### Câu C (Ngoài phạm vi tài liệu):
> *"Ngân hàng nào có lãi suất tiết kiệm cao nhất hôm nay?"*

**Kết quả ghi nhận thực tế cho Câu C (Thực tế thực thi)**:
- Ngữ cảnh truy xuất thu được các đoạn văn bản có khoảng cách `distance >= 0.4497` gần ngưỡng.
- Mô hình Gemini được cô lập bởi Grounding Prompt giữa hai dấu `<<< UNTRUSTED CONTEXT DATA >>>` đã tuân thủ hướng dẫn và trả lời chính xác: *"Không đủ thông tin để trả lời câu hỏi về ngân hàng có lãi suất tiết kiệm cao nhất hôm nay dựa trên dữ liệu được cung cấp."*
- **Xác nhận**: Hệ thống không bịa đặt tên ngân hàng hay lãi suất tiết kiệm ngoài phạm vi.
