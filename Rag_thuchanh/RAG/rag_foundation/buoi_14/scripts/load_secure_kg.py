"""Idempotently add allowed_roles to Buoi 14 Neo4j nodes."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from src.config import RBAC_CONFIG  # noqa: E402

CSV = BASE_DIR / "data/processed/chunks_secure.csv"

def main() -> None:
    if not CSV.exists():
        raise FileNotFoundError(f"Chưa có {CSV}; chạy assign_security_tags.py trước.")
    load_dotenv(BASE_DIR / ".env")
    password = os.getenv("NEO4J_PASSWORD", "").strip()
    if not password or password == "YOUR_NEO4J_PASSWORD":
        raise RuntimeError("NEO4J_PASSWORD chưa được cấu hình trong buoi_14/.env")
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    df = pd.read_csv(CSV, dtype=str).fillna("")
    rows = [{"id": str(r.chunk_id), "document_id": str(r.document_id),
             "allowed_roles": json.loads(r.allowed_roles), "lab_session": "buoi_15"}
            for r in df.itertuples()]
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        with driver.session(database=database) as session:
            session.run("""
            UNWIND $rows AS row
            MERGE (d:DieuKhoan {id: row.id})
            SET d.document_id = row.document_id, d.allowed_roles = row.allowed_roles,
                d.lab_session = row.lab_session
            """, rows=rows)
            session.run("""
            UNWIND $rows AS row
            MATCH (v:VanBan {id: row.document_id})
            SET v.allowed_roles = coalesce(v.allowed_roles, row.allowed_roles),
                v.lab_session = row.lab_session
            """, rows=rows)
            count = session.run("MATCH (d:DieuKhoan) WHERE d.allowed_roles IS NOT NULL RETURN count(d) AS n").single()["n"]
        print(f"SECURE KG LOAD PASS: updated {len(rows)} chunks; tagged nodes={count}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
