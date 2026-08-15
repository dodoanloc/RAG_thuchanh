from pathlib import Path
import pandas as pd, re
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'outputs'; WIKI=BASE/'wiki'
def main():
 e=pd.read_csv(OUT/'entities.csv',dtype=str).fillna(''); rel=pd.read_csv(OUT/'relations.csv',dtype=str).fillna(''); files=list(WIKI.rglob('*.md')); known={p.stem for p in files}; broken=[]; orphan=[]; ids=e.id.tolist();
 for p in files:
  text=p.read_text(encoding='utf-8');
  for target in re.findall(r'\[\[([^\]|]+)',text):
   target=target.split('|')[0].split('/')[-1]
   if target not in known and target not in {'risks','controls','events'}: broken.append((str(p.relative_to(WIKI)),target))
  if p.name!='Home.md' and not re.search(r'\[\[',text): orphan.append(str(p.relative_to(WIKI)))
 missing=rel[~rel.source_id.isin(set(e.id))|~rel.target_id.isin(set(e.id))]
 unlinked=[]
 for rid in e[e.type=='RuiRo'].id:
  if not ((rel.source_id==rid)|(rel.target_id==rid)).any(): unlinked.append(rid)
 report=['# Wiki Validation Report\n','',f'- Markdown files: {len(files)}',f'- Entities: {len(e)}',f'- Relations: {len(rel)}',f'- Broken links: {len(broken)}',f'- Orphan pages: {len(orphan)}',f'- Duplicate entity IDs: {int(e.id.duplicated().sum())}',f'- Missing relation targets: {len(missing)}',f'- Risks without relations: {len(unlinked)}','', '## Details\n']
 if broken: report += [f'- broken: `{x}` -> `{y}`\n' for x,y in broken]
 if orphan: report += [f'- orphan: `{x}`\n' for x in orphan]
 if unlinked: report += [f'- risk without relation: `{x}`\n' for x in unlinked]
 (OUT/'wiki_validation_report.md').write_text('\n'.join(report),encoding='utf-8'); print('\n'.join(report)); return 1 if broken or missing.shape[0] or e.id.duplicated().any() else 0
if __name__=='__main__': raise SystemExit(main())
