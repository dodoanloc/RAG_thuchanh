# Dependency Report — Buổi 17

## Environment
- Python: 3.11.15 system; reusable Buổi 14 venv: Python 3.13
- pandas, rank_bm25, streamlit, neo4j, cryptography: import PASS
- `.env`: template created; secrets not committed
- Required Buổi 16 path: `../buoi_16/...` **NOT FOUND**
- Actual compatible source used: `../buoi_14/data/processed/`

## Source data
| File | Rows | Columns |
|---|---:|---:|
| chunks_normalized.csv | 720 | 13 |
| chunks_secure.csv | 720 | 14 |

`chunks_secure.csv` equals `chunks_normalized.csv` plus `allowed_roles` exactly. No source files modified.

## SecureRetriever
- Reusable module: `../buoi_14/src/secure_retriever.py`
- Main function: `retrieve(query, user_roles, method, top_k, candidate_k)`
- Input role: list of validated roles
- Output: ranked chunks retaining `chunk_id`, `document_id`, `citation`, `text`, `allowed_roles`
- Enforcement: role subset CSV generated **before** BM25/dense/hybrid/rerank; defense-in-depth check after retrieval.

## Final
- SOURCE DATA: PASS (actual previous corpus found; Buoi 16 path absent)
- RBAC DATA AVAILABLE: YES
- SECURE RETRIEVER REUSABLE: YES
- REUSE PLAN: adapter in `scripts/secure_retrieval_adapter.py` imports and calls previous SecureRetriever; no copy/rebuild.
- DATA PATH NOTE: replace `LCA_DATA_ROOT` with `../buoi_16` when that folder is restored.
