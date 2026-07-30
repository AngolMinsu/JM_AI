"""Shared Chroma retrieval used by source-specific CSV/PDF tools."""
import os
from pathlib import Path
from typing import Any, Dict, List
import requests
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

VECTOR_DB_PATH = Path(os.getenv("VECTOR_DB_PATH", str(Path(__file__).resolve().parents[1] / "db" / "vector_db")))
COLLECTION_NAME = "jaryong_documents"

class QwenLocalEmbeddings(Embeddings):
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("EMBEDDING_SERVER_URL", "http://localhost:8081/v1")).rstrip("/")
        self.model = os.getenv("EMBEDDING_MODEL", "qwen3-embedding")

    def _embed(self, inputs: List[str]) -> List[List[float]]:
        response = requests.post(f"{self.base_url}/embeddings", json={"input": inputs, "model": self.model}, timeout=30)
        response.raise_for_status()
        data = response.json().get("data", [])
        if len(data) != len(inputs):
            raise RuntimeError("임베딩 서버가 예상한 개수의 벡터를 반환하지 않았습니다.")
        return [item["embedding"] for item in sorted(data, key=lambda item: item.get("index", 0))]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]

def execute_rag_search(query: str, k: int = 4, source: str | None = None) -> Dict[str, Any]:
    if not query.strip():
        return {"status": "error", "message": "검색어가 비어 있습니다."}
    if not VECTOR_DB_PATH.exists():
        return {"status": "not_ready", "message": f"RAG 인덱스가 없습니다. web/server에서 'python -m tools.ingest_documents'를 실행하세요."}
    try:
        store = Chroma(collection_name=COLLECTION_NAME, persist_directory=str(VECTOR_DB_PATH), embedding_function=QwenLocalEmbeddings())
        filter_metadata = {"source": source} if source else None
        docs_and_scores = store.similarity_search_with_relevance_scores(query, k=k, filter=filter_metadata)
        results = [{"content": doc.page_content, "source": doc.metadata.get("source", "unknown"), "chunk": doc.metadata.get("chunk", 0), "score": round(float(score), 4)} for doc, score in docs_and_scores]
        return {"status": "success", "query": query, "results": results} if results else {"status": "not_found", "message": "관련 문서를 찾지 못했습니다."}
    except Exception as exc:
        return {"status": "error", "message": f"RAG 검색 오류: {exc}"}
