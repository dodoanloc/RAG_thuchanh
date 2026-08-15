from pathlib import Path
import pandas as pd, re, shutil
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'outputs'; WIKI=BASE/'wiki'

def safe(s): return re.sub(r'[^\w\- ]+','',str(s),flags=re.UNICODE).strip().replace(' ','_')
def link(name, typ): return f'[[{typ}/{safe(name)}|{name}]]'
def front(r): return f"---\nid: {r.id}\ntype: {r.type}\nverification_status: {r.verification_status}\ndata_origin: {r.data_origin}\n---\n"
def main():
 if WIKI.exists(): shutil.rmtree(WIKI)
 for d in ['risks','controls','events']: (WIKI/d).mkdir(parents=True)
 e=pd.read_csv(OUT/'entities.csv',dtype=str).fillna(''); rel=pd.read_csv(OUT/'relations.csv',dtype=str).fillna('')
 by={r.id:r for _,r in e.iterrows()}; counts={'RuiRo':0,'KiemSoat':0,'SuKienRuiRo':0}; links=0
 for _,r in e.iterrows():
  typ=r.type; folder={'RuiRo':'risks','KiemSoat':'controls','SuKienRuiRo':'events'}[typ]; name=r.get('name') or r.id; lines=[front(r),f'# {name}\n',f'- ID: `{r.id}`\n']
  fields={'RuiRo':['category','description','cause','event','impact','inherent_level','residual_level','owner_unit_id'],'KiemSoat':['control_type','frequency','owner_role_id','effectiveness'],'SuKienRuiRo':['risk_id','occurred_at','discovered_at','severity','loss_amount_vnd','description']}.get(typ,[])
  for f in fields:
   if r.get(f,''): lines.append(f'- **{f}**: {r[f]}\n')
  related=[]
  for _,q in rel.iterrows():
   if typ=='KiemSoat' and q.source_id==r.id and q.relationship_type=='MITIGATES': related.append((q.target_id,q))
   if typ=='RuiRo' and q.target_id==r.id and q.relationship_type=='MITIGATES': related.append((q.source_id,q))
   if typ=='RuiRo' and q.source_id==r.id and q.relationship_type=='OBSERVED_AS': related.append((q.target_id,q))
   if typ=='SuKienRuiRo' and q.target_id==r.id and q.relationship_type=='OBSERVED_AS': related.append((q.source_id,q))
  lines.append('\n## Quan hệ\n')
  for target,q in related:
   tr=by.get(target); tn=(tr.get('name') or target) if tr is not None else target; tt=tr.type if tr is not None else 'unknown'; lines.append(f'- **{q.relationship_type}**: {link(tn, {"RuiRo":"risks","KiemSoat":"controls","SuKienRuiRo":"events"}.get(tt,tt))}\n  - evidence: {q.evidence_quote}\n  - verification_status: {q.verification_status}\n'); links+=1
  (WIKI/folder/(safe(name)+'.md')).write_text(''.join(lines),encoding='utf-8'); counts[typ]+=1
 home=['# Wiki Risk Graph\n','\n## Index\n','- [[risks/index|Rủi ro]]\n','- [[controls/index|Kiểm soát]]\n','- [[events/index|Sự kiện rủi ro]]\n',f'\nNodes: {len(e)}  Edges: {len(rel)}  Wikilinks: {links}\n']
 for typ,folder in [('RuiRo','risks'),('KiemSoat','controls'),('SuKienRuiRo','events')]:
  title={'RuiRo':'Rủi ro','KiemSoat':'Kiểm soát','SuKienRuiRo':'Sự kiện rủi ro'}[typ]; rows=[f'# {title}\n']
  for _,r in e[e.type==typ].iterrows(): rows.append(f'- {link(r.get("name") or r.id,folder)}\n')
  (WIKI/folder/'index.md').write_text(''.join(rows),encoding='utf-8')
 (WIKI/'Home.md').write_text(''.join(home),encoding='utf-8'); print('pages',sum(counts.values()),'wikilinks',links,'counts',counts)
if __name__=='__main__': main()
