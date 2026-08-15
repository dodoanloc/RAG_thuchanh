from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'outputs'; load_dotenv(BASE/'.env')
REL={'MITIGATES':('KiemSoat','RuiRo'),'OBSERVED_AS':('RuiRo','SuKienRuiRo')}
def main():
 c={k:os.getenv(k,'') for k in ['NEO4J_URI','NEO4J_USER','NEO4J_PASSWORD','NEO4J_DATABASE']}
 if not all(c.values()): print('[FAIL] missing Neo4j config'); return 1
 e=pd.read_csv(OUT/'entities.csv',dtype=str).fillna(''); r=pd.read_csv(OUT/'relations.csv',dtype=str).fillna(''); d=GraphDatabase.driver(c['NEO4J_URI'],auth=(c['NEO4J_USER'],c['NEO4J_PASSWORD']))
 try:
  d.verify_connectivity()
  with d.session(database=c['NEO4J_DATABASE']) as s:
   for label in ['RuiRo','KiemSoat','SuKienRuiRo']: s.run(f'CREATE CONSTRAINT {label.lower()}_id_b13 IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE').consume()
   for _,x in e.iterrows():
    props={k:str(v) for k,v in x.to_dict().items() if k not in {'id','type'} and str(v)}; s.run(f'MERGE (n:{x.type} {{id:$id}}) SET n += $props',id=x.id,props=props).consume()
   for _,x in r.iterrows():
    if x.relationship_type not in REL: continue
    src,tgt=REL[x.relationship_type]; props={k:str(x[k]) for k in ['source','evidence_quote','confidence','verification_status','data_origin'] if k in x}
    s.run(f'MATCH (a:{src} {{id:$source_id}}),(b:{tgt} {{id:$target_id}}) MERGE (a)-[rel:{x.relationship_type}]->(b) SET rel += $props',source_id=x.source_id,target_id=x.target_id,props=props).consume()
   print('nodes',s.run('MATCH (n) RETURN count(n) AS c').single()['c'],'relationships',s.run('MATCH ()-[r]->() RETURN count(r) AS c').single()['c'])
 finally: d.close()
 return 0
if __name__=='__main__': raise SystemExit(main())
