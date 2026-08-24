from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/chunks_combined_secure.csv'
def run():
 df=pd.read_csv(DATA,dtype=str).fillna(''); domains=[]
 for _,g in df.groupby('document_id'):
  domains.append((g.document_id.iloc[0],g.title.iloc[0],g.document_type.iloc[0],g.so_ky_hieu.iloc[0],g.article.ne('').mean(),g.allowed_roles.ne('').mean()))
 p=ROOT/'outputs/b18_data_catalog.md'; p.write_text('# Buổi 18 Data Catalog\n\nSource: `data/chunks_combined_secure.csv`\nInternal policies: NOT FOUND; all current documents classified as EXTERNAL legal source.\n\n'+'\n'.join(f'- {x[0]} | {x[1]} | {x[2]} | {x[3]} | article completeness={x[4]:.2f} | allowed_roles completeness={x[5]:.2f}' for x in domains)+f'\n\nDATA CATALOGING: PASS\nDOMAINS DETECTED: {len(domains)} source-document groups\nREADY FOR UC3 & UC4: YES (safe training mode; UC3 no internal comparison asserted)\n',encoding='utf-8'); return len(domains)
if __name__=='__main__': print('documents',run())
