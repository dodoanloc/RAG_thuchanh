"""RBAC helpers. Policy is training-only; source allowed_roles remains authority."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config/rbac_policy.json").read_text(encoding="utf-8"))
VALID_ROLES = frozenset(POLICY["roles"])

def normalize_role(role: str) -> str:
    role = str(role).strip()
    if role not in VALID_ROLES:
        raise ValueError(f"UNKNOWN_ROLE_DENY: {role}")
    return role

def validate_roles(roles: list[str] | str) -> set[str]:
    if isinstance(roles, str): roles = [roles]
    if not roles: raise ValueError("UNKNOWN_ROLE_DENY: empty role")
    result = {normalize_role(x) for x in roles if str(x).strip()}
    if not result: raise ValueError("UNKNOWN_ROLE_DENY: empty role")
    return result

def allowed(allowed_roles: object, roles: list[str] | str) -> bool:
    user = validate_roles(roles)
    if isinstance(allowed_roles, str):
        try: allowed_set = set(json.loads(allowed_roles))
        except (TypeError, json.JSONDecodeError): allowed_set = set()
    else: allowed_set = set(allowed_roles) if isinstance(allowed_roles, (list, tuple, set)) else set()
    return bool(user & allowed_set)

if __name__ == "__main__":
    print(json.dumps({"roles": sorted(VALID_ROLES), "unknown_role": "DENY"}, ensure_ascii=False, indent=2))

# Policy is illustrative only; never treat it as Agribank policy.
