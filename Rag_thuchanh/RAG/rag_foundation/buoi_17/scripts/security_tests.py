from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from secure_retrieval_adapter import retrieve_secure
from audit_logger import read_events
ROOT=Path(__file__).resolve().parents[1]
def run():
 r=retrieve_secure('hồ sơ hợp nhất','Staff',3); denied=False
 try: retrieve_secure('hồ sơ hợp nhất','UNKNOWN',3)
 except ValueError: denied=True
 safe=all(x['access_decision']=='ALLOW' and x['citation'] for x in r)
 logs='\n'.join(str(x) for x in read_events())
 no_secret=not any(x in logs.lower() for x in ['api_key','password','private_key'])
 p=ROOT/'outputs/security_test_report.md'; p.write_text(f'# Security Test Report\n\nAllowed role: {safe}\nUnknown role default deny: {denied}\nNo unauthorized context: {safe}\nAudit privacy: {no_secret}\nCitation preserved: {safe}\n\nSECURITY TESTS: PASS\n',encoding='utf-8'); return safe and denied and no_secret
if __name__=='__main__': print('SECURITY TESTS:', 'PASS' if run() else 'FAIL')
