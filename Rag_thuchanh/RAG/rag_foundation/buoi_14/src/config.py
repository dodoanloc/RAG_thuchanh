"""RBAC roles and access helpers for Buổi 15."""
from __future__ import annotations
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
with (BASE_DIR / "roles.json").open(encoding="utf-8") as _f:
    RBAC_CONFIG = json.load(_f)
VALID_ROLES = frozenset(RBAC_CONFIG["roles"])
DEFAULT_ROLE = RBAC_CONFIG["default_role"]


def validate_roles(user_roles: list[str]) -> set[str]:
    if not user_roles:
        raise ValueError("Phải chọn tối thiểu một vai trò.")
    roles = {str(role).strip() for role in user_roles if str(role).strip()}
    invalid = roles - VALID_ROLES
    if invalid:
        raise ValueError(f"Vai trò không hợp lệ: {sorted(invalid)}")
    return roles


def parse_allowed_roles(value: object) -> set[str]:
    if isinstance(value, list):
        return {str(x) for x in value}
    try:
        parsed = json.loads(str(value))
        return {str(x) for x in parsed} if isinstance(parsed, list) else set()
    except (TypeError, json.JSONDecodeError):
        return set()


def may_access(allowed_roles: object, user_roles: list[str]) -> bool:
    return bool(parse_allowed_roles(allowed_roles) & validate_roles(user_roles))
