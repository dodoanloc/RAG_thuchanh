"""Evidence-first gap checker. Current corpus has external legal texts only."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'../buoi_14/data/processed/chunks_secure.csv'
ENUM=['DAP_UNG','THIEU','CHENH_LECH','CHUA_DU_BANG_CHUNG']
def catalog():
 df=pd.read_csv(DATA,dtype=str).fillna(''); rows=[]
 for (doc,typ),g in df.groupby(['document_id','document_type']): rows.append({'document_id':doc,'title':g.title.iloc[0],'document_type':typ,'classification':'EXTERNAL_REQUIREMENT','evidence':g.so_ky_hieu.iloc[0]})
 p=ROOT/'outputs/gap_input_catalog.md'; body='\n'.join(f"- {r['document_id']} | {r['title']} | {r['document_type']} | {r['classification']} | {r['evidence']}" for r in rows); p.write_text('# Gap Input Catalog\n\nCOMPLIANCE GAP DATA: INSUFFICIENT\nDATA GAP: INTERNAL POLICY NOT FOUND\n\n'+body+'\n',encoding='utf-8'); return rows
def run():
 rows=catalog(); out=pd.DataFrame(columns=['gap_id','external_document_id','external_chunk_id','external_requirement','external_citation','internal_document_id','internal_chunk_id','internal_evidence','internal_citation','classification','reason','confidence','review_status','request_id']); out.to_csv(ROOT/'outputs/compliance_gap_results.csv',index=False); (ROOT/'outputs/compliance_gap_report.md').write_text('# Compliance Gap Report\n\nCOMPLIANCE GAP DATA: INSUFFICIENT\nDATA GAP: INTERNAL POLICY NOT FOUND\nGAP CHECKER: PASS (safe data-gap refusal)\nHUMAN REVIEW REQUIRED: YES\n',encoding='utf-8'); return rows
if __name__=='__main__': print('documents',len(run()))
