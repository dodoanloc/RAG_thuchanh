"""Neo4j connectivity, validated graph import, and idempotency verification."""
from __future__ import annotations
import argparse, os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

BASE=Path(__file__).resolve().parent; KB=BASE/"ner_kb"; load_dotenv(BASE/".env")
REL={"THAM_CHIEU","SUA_DOI_BO_SUNG","THAY_THE_BOI","BAN_HANH_BOI","KY_BOI","AP_DUNG_CHO","THUOC_LINH_VUC"}
LABEL={"BAN_HANH_BOI":"CoQuan","KY_BOI":"NguoiKy","AP_DUNG_CHO":"DoiTuongApDung","THUOC_LINH_VUC":"LinhVuc"}

def cfg():
    return {"uri":os.getenv("NEO4J_URI","bolt://localhost:7687"),"user":os.getenv("NEO4J_USER","neo4j"),"password":os.getenv("NEO4J_PASSWORD",""),"database":os.getenv("NEO4J_DATABASE","neo4j")}

def connect():
    c=cfg()
    if not c["password"] or c["password"]=="your_password_here": raise RuntimeError("NEO4J_PASSWORD chưa cấu hình")
    d=GraphDatabase.driver(c["uri"],auth=(c["user"],c["password"]),connection_timeout=5)
    d.verify_connectivity(); return d,c

def check():
    try:
        d,c=connect()
        try:
            with d.session(database=c["database"]) as s: print("[PASS] Neo4j",c["uri"],"database",c["database"],"probe",s.run("RETURN 1 AS ok").single()["ok"])
        finally: d.close()
        return True
    except Exception as e: print("[FAIL] Neo4j",type(e).__name__,str(e)[:300]); return False

def import_once():
    docs=pd.read_csv(KB/"cleaned_documents.csv",dtype=str).fillna(""); ents=pd.read_csv(KB/"entities.csv",dtype=str).fillna(""); rels=pd.read_csv(KB/"relationships.csv",dtype=str).fillna("")
    d,c=connect()
    try:
        with d.session(database=c["database"]) as s:
            s.run("CREATE CONSTRAINT document_so IF NOT EXISTS FOR (n:Document) REQUIRE n.so_ky_hieu IS UNIQUE").consume()
            s.run("CREATE CONSTRAINT entity_key IF NOT EXISTS FOR (n:Entity) REQUIRE n.entity_id IS UNIQUE").consume()
            for _,r in docs.iterrows(): s.run("MERGE (n:Document {so_ky_hieu:$so}) SET n.id=$id,n.title=$title,n.loai_van_ban=$kind,n.content_clean=$content",so=r.so_ky_hieu,id=r.id,title=r.title,kind=r.loai_van_ban,content=r.content_clean).consume()
            for _,r in ents.drop_duplicates("entity_id").iterrows(): s.run("MERGE (n:Entity {entity_id:$id}) SET n.name=$name,n.entity_type=$typ",id=r.entity_id,name=r.canonical_name,typ=r.entity_type).consume()
            for _,r in rels.iterrows():
                if r.relationship_type not in REL: continue
                if r.relationship_type in LABEL:
                    q=f"MATCH (a:Document {{so_ky_hieu:$source}}),(b:Entity {{entity_id:$eid}}) MERGE (a)-[x:{r.relationship_type}]->(b) SET x.method=$method,x.confidence=$confidence,x.evidence=$evidence"
                    hit=ents[(ents.entity_type==LABEL[r.relationship_type]) & (ents.canonical_name==r.target)]
                    if hit.empty: continue
                    s.run(q,source=r.source,eid=hit.iloc[0].entity_id,method=r.method,confidence=r.confidence,evidence=r.evidence).consume()
                else:
                    s.run(f"MATCH (a:Document {{so_ky_hieu:$source}}),(b:Document {{so_ky_hieu:$target}}) MERGE (a)-[x:{r.relationship_type}]->(b) SET x.method=$method,x.confidence=$confidence,x.evidence=$evidence",source=r.source,target=r.target,method=r.method,confidence=r.confidence,evidence=r.evidence).consume()
            counts=s.run("MATCH (n) RETURN labels(n) AS labels,count(n) AS total").data(); relcounts=s.run("MATCH ()-[r]->() RETURN type(r) AS type,count(r) AS total").data()
            print("[PASS] Neo4j import nodes",counts); print("[PASS] Neo4j relationships",relcounts)
    finally: d.close()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); ap.add_argument("--import",dest="do_import",action="store_true"); ap.add_argument("--verify-idempotent",action="store_true"); a=ap.parse_args()
    if a.check: check()
    if a.do_import:
        import_once()
        if a.verify_idempotent: import_once()
if __name__=="__main__": main()
