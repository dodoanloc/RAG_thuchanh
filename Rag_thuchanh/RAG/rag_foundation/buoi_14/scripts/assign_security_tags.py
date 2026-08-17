"""Assign property-based RBAC tags to normalized chunks for Buổi 15."""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from src.config import RBAC_CONFIG, VALID_ROLES  # noqa: E402

INPUT_PATH = BASE_DIR / "data" / "processed" / "chunks_normalized.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "chunks_secure.csv"

HR_KEYWORDS = [
    "nhân sự", "nhan su", "lương", "luong", "lương thưởng", "tuyển dụng",
    "tuyen dung", "bổ nhiệm", "bo nhiem", "kỷ luật", "ky luat", "lao động",
    "lao dong", "hợp đồng lao động", "hop dong lao dong",
]
RISK_KEYWORDS = [
    "tín dụng", "tin dung", "rủi ro", "rui ro", "hạn mức", "han muc",
    "phê duyệt", "phe duyet", "duyệt vay", "duyet vay", "cho vay",
    "nợ xấu", "no xau", "thu hồi nợ", "thu hoi no", "bảo đảm", "bao dam",
]


def norm(text: object) -> str:
    return str(text or "").lower()


def has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def assign_roles(row: pd.Series) -> list[str]:
    haystack = "\n".join(norm(row.get(col, "")) for col in [
        "document_id", "title", "so_ky_hieu", "document_type", "article", "clause", "text"
    ])
    if has_any(haystack, HR_KEYWORDS):
        return RBAC_CONFIG["rules"]["hr"]
    if has_any(haystack, RISK_KEYWORDS):
        return RBAC_CONFIG["rules"]["risk"]
    return RBAC_CONFIG["rules"]["general"]


def validate(df: pd.DataFrame) -> None:
    empty = df["allowed_roles"].isna() | (df["allowed_roles"].astype(str).str.len() == 0)
    if empty.any():
        raise ValueError(f"Có {int(empty.sum())} dòng thiếu allowed_roles")
    invalid_rows = []
    for idx, raw in df["allowed_roles"].items():
        roles = set(json.loads(raw))
        if not roles or not roles <= VALID_ROLES:
            invalid_rows.append((idx, sorted(roles)))
    if invalid_rows:
        raise ValueError(f"allowed_roles không hợp lệ: {invalid_rows[:5]}")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(INPUT_PATH)
    df = pd.read_csv(INPUT_PATH, dtype=str).fillna("")
    df["allowed_roles"] = df.apply(lambda row: json.dumps(assign_roles(row), ensure_ascii=False), axis=1)
    validate(df)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    combo_counter = Counter(df["allowed_roles"])
    role_counter = Counter(role for raw in df["allowed_roles"] for role in json.loads(raw))
    print("SECURITY TAGGING REPORT")
    print(f"Input rows: {len(df)}")
    print(f"Output: {OUTPUT_PATH}")
    print("Chunks per allowed_roles group:")
    for combo, count in combo_counter.most_common():
        print(f"- {combo}: {count}")
    print("Chunks visible per role:")
    for role, count in sorted(role_counter.items()):
        print(f"- {role}: {count}")
    print("Representative samples:")
    for combo in combo_counter:
        sample = df[df["allowed_roles"] == combo].iloc[0]
        preview = re.sub(r"\s+", " ", sample.get("text", ""))[:180]
        print(f"- {combo} | {sample.get('document_id')} | {sample.get('chunk_id')} | {preview}")


if __name__ == "__main__":
    main()
