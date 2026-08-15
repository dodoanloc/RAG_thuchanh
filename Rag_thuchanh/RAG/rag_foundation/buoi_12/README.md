# Buổi 12 — Legal metadata and knowledge graph

Pipeline follows `buoi_12.md` and never modifies `ner_kb/metadata.csv` or `ner_kb/content.csv`.

## Run

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env
# Edit Neo4j values only when Neo4j is available.
.venv/bin/python run_pipeline.py
```

LLM extraction uses OpenAI-compatible `ROUTER_BASE_URL` with model `openclaw0`; no Gemini key is required. If router is unavailable, document-level extraction is recorded as an error and deterministic metadata remains intact.

Outputs are written under `ner_kb/`: cleaned documents, candidates, raw entities, enriched metadata, canonical entities, raw/validated relationships, and validation report.

Neo4j import is opt-in after connection check. Docker setup:

```bash
# .env already contains generated local password; keep file chmod 600.
docker compose up -d
.venv/bin/python neo4j_import.py --check
.venv/bin/python neo4j_import.py --import --verify-idempotent
```

Neo4j Browser: `http://127.0.0.1:7474`
