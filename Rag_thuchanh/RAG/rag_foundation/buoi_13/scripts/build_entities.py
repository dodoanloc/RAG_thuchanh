from pathlib import Path
import pandas as pd

BASE=Path(__file__).resolve().parents[1]; DATA=BASE/'data'; OUT=BASE/'outputs'; OUT.mkdir(exist_ok=True)

def main():
    risks=pd.read_csv(DATA/'risk_profiles_seed.csv',dtype=str).fillna('')
    controls=pd.read_csv(DATA/'controls_seed.csv',dtype=str).fillna('')
    events=pd.read_csv(DATA/'risk_events_seed.csv',dtype=str).fillna('')
    entities=[]
    for _,r in risks.iterrows():
        entities.append({**r.to_dict(),'id':r.id,'type':'RuiRo','description':r.description,'source_file':'risk_profiles_seed.csv'})
    for _,r in controls.iterrows():
        entities.append({**r.to_dict(),'id':r.id,'type':'KiemSoat','description':r.name,'source_file':'controls_seed.csv'})
    for _,r in events.iterrows():
        entities.append({**r.to_dict(),'id':r.id,'type':'SuKienRuiRo','name':r.description,'description':r.description,'source_file':'risk_events_seed.csv'})
    edf=pd.DataFrame(entities).fillna('')
    cols=['id','type','name','description','source_file','data_origin','verification_status']
    extra=[c for c in edf.columns if c not in cols]
    edf[cols+extra].to_csv(OUT/'entities.csv',index=False,encoding='utf-8-sig')
    rel=pd.read_csv(DATA/'relationships_seed.csv',dtype=str).fillna('')
    ids=set(edf.id); orphan=rel[~rel.source_id.isin(ids)|~rel.target_id.isin(ids)]
    rel.to_csv(OUT/'relations.csv',index=False,encoding='utf-8-sig')
    print('entities_by_type',dict(edf.type.value_counts()))
    print('relations_by_type',dict(rel.relationship_type.value_counts()))
    print('orphan_references',len(orphan))
    if len(orphan): raise SystemExit(1)

if __name__=='__main__': main()
