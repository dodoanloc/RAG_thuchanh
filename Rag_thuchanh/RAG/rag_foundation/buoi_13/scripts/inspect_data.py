from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
FILES = ["risk_profiles_seed.csv", "controls_seed.csv", "risk_events_seed.csv", "relationships_seed.csv"]

def main():
    frames = {}
    for name in FILES:
        p = DATA / name
        df = pd.read_csv(p, dtype=str).fillna("")
        frames[name] = df
        print(f"\n{name}: rows={len(df)} columns={list(df.columns)}")
        print(f"null_or_empty={int(df.eq('').sum().sum())} duplicate_rows={int(df.duplicated().sum())}")
        if "id" in df: print(f"duplicate_id={int(df.id.duplicated().sum())}")
    entities = set(frames["risk_profiles_seed.csv"].id) | set(frames["controls_seed.csv"].id) | set(frames["risk_events_seed.csv"].id)
    rel = frames["relationships_seed.csv"]
    missing = rel[~rel.source_id.isin(entities) | ~rel.target_id.isin(entities)]
    print("\nrelationship_types", dict(rel.relationship_type.value_counts()))
    print("entity_types", {"RuiRo": len(frames["risk_profiles_seed.csv"]), "KiemSoat": len(frames["controls_seed.csv"]), "SuKienRuiRo": len(frames["risk_events_seed.csv"])})
    print("orphan_references", len(missing))
    print("owner_unit_master", "MISSING")
    print("owner_role_master", "MISSING")

if __name__ == "__main__": main()
