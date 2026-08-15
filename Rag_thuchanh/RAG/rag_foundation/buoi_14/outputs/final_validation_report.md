# Buổi 14 — Final Validation Report

**Validation date:** 2026-08-15

## Code and data

- [PASS] All Buổi 14 code and outputs stay under `buoi_14/`.
- [PASS] Source files under `../buoi_10/graph_rag_labs/kb+hops/` remain read-only.
- [PASS] `chunks_normalized.csv`: 720 unique retrieval chunks.
- [PASS] Citation fields retain document, article, and chunk identifiers.
- [PASS] No API key, password, database, or runtime cache committed.

## Retrieval

- [PASS] BM25-only executed on normalized corpus.
- [PASS] Dense-only executed with cached document embeddings.
- [PASS] Hybrid executed with BM25 + Dense and RRF fusion.
- [PASS] Reranker executed on Hybrid candidates only, not full corpus.
- [PASS] Evaluation executed for BM25, Dense, Hybrid, and Hybrid + Rerank.
- [PASS] Streamlit app imports and supports `BM25`, `Dense`, `Hybrid`, and `Hybrid + Rerank`.

Observed overall evaluation from the executed run:

| Method | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---:|---:|---:|
| BM25 | 58.3% | 75.0% | 75.0% | 0.6528 |
| Dense | 0.0% | 8.3% | 8.3% | 0.0278 |
| Hybrid | 41.7% | 66.7% | 66.7% | 0.5278 |
| Hybrid + Rerank | 66.7% | 75.0% | 75.0% | 0.7083 |

## Mini Knowledge Graph

- [PASS] Neo4j connection verified.
- [PASS] Buổi 14 loader completed with `lab_session = "buoi_14"`.
- [PASS] 15 `VanBan` nodes loaded.
- [PASS] 720 `DieuKhoan` nodes loaded.
- [PASS] 720 `CONTAINS` relationships loaded.
- [PASS] 705 `NEXT` relationships loaded.
- [PASS] 8 source-backed inter-document relationships loaded.
- [PASS] Cleanup is scoped to `lab_session = "buoi_14"`; no whole-database delete used.
- [PASS] Existing Buổi 12/13 graph data preserved.

## Final status

```text
READY FOR DEMO: YES
```

Known limitation: Dense and reranker models run on CPU in this environment. Exact retrieval quality depends on the model cache and corpus version.
