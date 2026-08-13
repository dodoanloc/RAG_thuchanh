"""Router adapter contract: 9router OpenAI endpoints behave like required RAG client."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def test_router_client_exposes_embedding_and_generation_methods():
    from rag import RouterClient

    client = RouterClient(base_url="http://127.0.0.1:20128/v1", api_key="router")
    embedding = client.models.embed_content(
        model="gemini-embedding-001", contents="xin chào", config=None
    )
    assert len(embedding.embeddings) == 1
    assert len(embedding.embeddings[0].values) >= 128

    answer = client.models.generate_content(
        model="openclaw0", contents="Trả lời đúng: RAG OK"
    )
    assert answer.text.strip()
