from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json,re,uuid
ROOT=Path(__file__).resolve().parents[1]; LOG=ROOT/'outputs/audit_log.jsonl'; SECRET=re.compile(r'(?i)(api[_-]?key|password|secret|token|private[_-]?key)')
def safe(v):
 if isinstance(v,dict): return {k:safe(x) for k,x in v.items() if not SECRET.search(str(k))}
 if isinstance(v,list): return [safe(x) for x in v]
 if isinstance(v,str) and SECRET.search(v): return '[REDACTED]'
 return v
def log_event(**kwargs):
 e={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'request_id':kwargs.pop('request_id',str(uuid.uuid4())),**kwargs}; e=safe(e); LOG.parent.mkdir(exist_ok=True); LOG.open('a',encoding='utf-8').write(json.dumps(e,ensure_ascii=False)+'\n'); return e

def read_events(): return [json.loads(x) for x in LOG.read_text(encoding='utf-8').splitlines() if x.strip()] if LOG.exists() else []
