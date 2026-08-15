# Buổi 13 — Wiki Risk Graph

MVP pipeline:

```text
CSV → inspect → entities.csv + relations.csv → Wiki Markdown → validate → Neo4j
```

## Cài đặt

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

## Chạy từng bước

```bash
.venv/bin/python scripts/inspect_data.py
.venv/bin/python scripts/build_entities.py
.venv/bin/python scripts/build_wiki.py
.venv/bin/python scripts/validate_wiki.py
```

Mở thư mục `wiki/` như Obsidian vault, bắt đầu từ `wiki/Home.md`.

## Neo4j

`.env` là file local, không commit. Cần có:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j
```

Load graph:

```bash
.venv/bin/python scripts/load_neo4j.py
.venv/bin/python scripts/load_neo4j.py
```

Lần chạy thứ hai dùng `MERGE`, không tạo duplicate.

Neo4j Browser: `http://127.0.0.1:7474`.

## Phạm vi và nguồn

Dữ liệu seed là dữ liệu mô phỏng cho lab. Không dùng `loss_amount_vnd` làm báo cáo nghiệp vụ. `owner_unit_id` và `owner_role_id` chỉ là mã; project không tự bịa tên master data.

Mọi relation giữ `source`, `evidence_quote`, `confidence`, `verification_status`, `data_origin`. Không tự chuyển `PROPOSED` thành `VERIFIED`.

## Kiểm tra

Output chính:

```text
outputs/entities.csv
outputs/relations.csv
outputs/wiki_validation_report.md
```

Cypher mẫu nằm tại `cypher/schema.cypher` và `cypher/demo_queries.cypher`.
