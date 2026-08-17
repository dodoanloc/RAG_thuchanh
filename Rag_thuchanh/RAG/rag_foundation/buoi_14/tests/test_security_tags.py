import json
import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

BASE_DIR = Path(__file__).resolve().parent.parent

def test_chunks_secure_has_non_empty_allowed_roles():
    path = BASE_DIR / 'data/processed/chunks_secure.csv'
    assert path.exists()
    df = pd.read_csv(path, dtype=str).fillna('')
    assert len(df) > 0
    assert df['allowed_roles'].map(lambda raw: len(json.loads(raw)) > 0).all()


def test_guest_cannot_see_hr_only_chunks():
    df = pd.read_csv(BASE_DIR / 'data/processed/chunks_secure.csv', dtype=str).fillna('')
    roles = df['allowed_roles'].map(json.loads)
    hr_only = roles.map(lambda r: set(r) == {'Admin', 'HR'})
    guest_visible = roles.map(lambda r: 'Guest' in r)
    assert not (hr_only & guest_visible).any()


def test_secure_cypher_uses_access_filter():
    from src.secure_retriever import secure_cypher
    query, params = secure_cypher(['Guest'])
    assert 'any(role IN' in query
    assert params == {'user_roles': ['Guest']}
