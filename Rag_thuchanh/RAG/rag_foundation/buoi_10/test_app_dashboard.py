from pathlib import Path


def test_buoi_10_has_runnable_graph_dashboard():
    app = Path(__file__).with_name("app.py")
    assert app.exists(), "Buổi 10 cần app.py để hiển thị kết quả Neo4j trực quan"
    source = app.read_text(encoding="utf-8")
    assert "streamlit" in source
    assert "MATCH (d:Document)" in source
    assert "Neo4j" in source
    assert "THAY_THE" in source
    assert "st.dataframe" in source
