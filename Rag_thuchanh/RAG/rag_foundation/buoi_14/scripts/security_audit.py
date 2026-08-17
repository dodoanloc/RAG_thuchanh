"""Offline security integration audit for Buổi 15 RBAC tags."""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd
BASE_DIR = Path(__file__).resolve().parent.parent
CSV = BASE_DIR / "data/processed/chunks_secure.csv"

CASES = [
    ("Guest cannot read HR", ["Guest"], ["Admin", "HR"]),
    ("Staff cannot read HR", ["Staff"], ["Admin", "HR"]),
    ("Guest cannot read risk", ["Guest"], ["Admin", "Risk_Manager", "Staff"]),
    ("Staff can read risk", ["Staff"], ["Admin", "Risk_Manager", "Staff"]),
    ("Guest can read general", ["Guest"], ["Admin", "HR", "Risk_Manager", "Staff", "Guest"]),
]

def main() -> None:
    if not CSV.exists(): raise FileNotFoundError(f"Run assign_security_tags.py first: {CSV}")
    df = pd.read_csv(CSV, dtype=str).fillna("")
    parsed = df.allowed_roles.map(json.loads)
    lines=["# Security Audit Report — Buổi 15", "", f"Corpus: {len(df)} chunks", ""]
    passed=0
    for name, user, expected in CASES:
        visible = parsed.map(lambda roles: bool(set(roles) & set(user)))
        actual = int(visible.sum())
        matching = parsed.map(lambda roles: roles == expected)
        target_count=int(matching.sum())
        target_visible=int((matching & visible).sum())
        should_allow=bool(set(user) & set(expected))
        ok=(target_visible > 0) if should_allow and target_count else (target_visible == 0)
        passed += int(ok)
        lines += [f"## {'PASS' if ok else 'FAIL'} — {name}", f"- Roles: {user}", f"- Target tags: {expected}", f"- Target chunks: {target_count}; visible target chunks: {target_visible}; all visible chunks: {actual}", ""]
    lines += [f"## Kết luận", f"{passed}/{len(CASES)} test PASS.", "Không rò rỉ tag cấp cao trong các test vai trò thấp." if passed == len(CASES) else "Có lỗi kiểm tra; không được công nhận an toàn."]
    out=BASE_DIR / "outputs/security_audit_report.md"; out.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"SECURITY AUDIT: {passed}/{len(CASES)} PASS; {out}")
    if passed != len(CASES): raise SystemExit(1)
if __name__ == '__main__': main()
