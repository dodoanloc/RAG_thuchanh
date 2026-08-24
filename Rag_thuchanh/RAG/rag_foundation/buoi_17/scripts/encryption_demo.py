from __future__ import annotations
from pathlib import Path
from cryptography.fernet import Fernet
ROOT=Path(__file__).resolve().parents[1]
def run():
    key_path=ROOT/'outputs/demo.key'; plain=ROOT/'outputs/audit_demo.txt'; enc=ROOT/'outputs/audit_demo.txt.enc'; dec=ROOT/'outputs/audit_demo.decrypted.txt'
    key=Fernet.generate_key(); key_path.write_bytes(key); plain.write_text('training audit event; no secret',encoding='utf-8'); enc.write_bytes(Fernet(key).encrypt(plain.read_bytes())); dec.write_bytes(Fernet(key).decrypt(enc.read_bytes()))
    report=ROOT/'outputs/encryption_demo_report.md'; report.write_text(f'# Encryption Demo\n\nENCRYPT: PASS\nDECRYPT MATCH: {"PASS" if plain.read_bytes()==dec.read_bytes() else "FAIL"}\nPRODUCTION READY: NO\n\nDemo only. Production needs TLS, KMS, rotation, backup and IAM.\n',encoding='utf-8'); key_path.unlink(missing_ok=True); return report
if __name__=='__main__': print(run())
