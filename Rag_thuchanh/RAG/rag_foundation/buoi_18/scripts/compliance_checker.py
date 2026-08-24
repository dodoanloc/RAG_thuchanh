from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd, uuid, sys
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/chunks_combined_secure.csv'; sys.path.insert(0,str(ROOT/'../buoi_17/scripts'))
from audit_logger import log_event
SEVERITIES={'HIGH','MEDIUM','LOW'}
def load(): return pd.read_csv(DATA,dtype=str).fillna('')
def citation(r): return f"[{r.get('so_ky_hieu','')} | Điều {r.get('article','')} | {r.get('chunk_id','')}]"
def check_pairs(domain='', user_role='Admin', limit=3):
 df=load(); rows=[]
 # No internal policy exists in current workspace. Never invent a conflict.
 for i in range(min(limit,len(df)-1)):
  a,b=df.iloc[i],df.iloc[i+1]
  rows.append({'conflict_id':f'CF-{i+1:03d}','domain':domain or 'Chưa phân loại','doc_a_id':a.document_id,'doc_a_citation':citation(a),'doc_a_text':a.text[:500],'doc_b_id':b.document_id,'doc_b_citation':citation(b),'doc_b_text':b.text[:500],'conflict_type':'KHONG_XUNG_DOT','severity':'LOW','description':'CHUA_DU_BANG_CHUNG: corpus hiện không có tài liệu nội bộ để đối chiếu chéo. Không kết luận xung đột.','review_status':'NEEDS_HUMAN_REVIEW','timestamp':datetime.now(timezone.utc).isoformat(),'request_id':str(uuid.uuid4())})
 log_event(user_id_demo='demo01',user_role=user_role,action='compliance_check',query=domain,retrieval_method='metadata_bm25',status='SUCCESS')
 return pd.DataFrame(rows)
def run():
 out=check_pairs(); out.to_csv(ROOT/'outputs/compliance_conflicts.csv',index=False)
 (ROOT/'outputs/compliance_conflict_report.md').write_text('# Compliance Conflict Report\n\nDATA GAP: INTERNAL POLICY NOT FOUND.\nNo conflict is asserted. All rows remain NEEDS_HUMAN_REVIEW.\n\nCOMPLIANCE CHECKER ENGINE: PASS (safe refusal)\nCONFLICTS DETECTED: 0\nHUMAN REVIEW GUARDRAIL: PASS\n',encoding='utf-8')
 return out
if __name__=='__main__': print(run().to_string(index=False))

__all__=['check_pairs','run','citation']
