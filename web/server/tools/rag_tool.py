import os
import requests
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings


# ==========================================
# 1. 8081번 Qwen Embedding 서버 연동 클래스
# ==========================================
class QwenLocalEmbeddings(Embeddings):
    """8081번 포트의 local Qwen Embedding 서버를 사용하는 LangChain 용 클래스"""
    def __init__(self, base_url: str = "http://localhost:8081/v1"):
        self.base_url = base_url

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = requests.post(
                f"{self.base_url}/embeddings",
                json={"input": text, "model": "qwen3-embedding"}
            )
            if response.status_code == 200:
                embeddings.append(response.json()["data"][0]["embedding"])
            else:
                raise Exception(f"Embedding API Error: {response.text}")
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


# ==========================================
# 2. AI에 전달할 RAG Tool 스펙 (OpenAI Schema)
# ==========================================
RAG_TOOL_SPEC: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_company_documents",
        "description": "자룡모빌리티솔루션의 채용공고, 연봉, 복리후생, 직무 자격요건, 사내 규정 등 PDF 문서 정보를 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 질문이나 주요 키워드 (예: 'BMS 자격요건', '신입 연봉', '복리후생')"
                }
            },
            "required": ["query"]
        }
    }
}


# ==========================================
# 3. 실제 ChromaDB 벡터 검색 실행 함수
# ==========================================
def execute_rag_search(query: str) -> str:
    """
    ai/data/vectorized_db 경로에 생성된 ChromaDB 인덱스에서 
    질문(query)과 가장 유사한 문서 조각 top-3를 찾아 텍스트로 반환합니다.
    """
    # web/server/tools 위치 기준으로 ai/data/vectorized_db 절대 경로 계산
    vector_db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../ai/data/vectorized_db")
    )

    if not os.path.exists(vector_db_path):
        return "시스템 안내: 아직 ai/data/vectorized_db 에 벡터 DB가 생성되지 않았습니다."

    try:
        embeddings = QwenLocalEmbeddings()
        vectorstore = Chroma(
            persist_directory=vector_db_path,
            embedding_function=embeddings
        )

        # 유사도가 높은 문서 조각 top 3개 추출
        docs = vectorstore.similarity_search(query, k=3)

        if not docs:
            return "문서 검색 결과: 관련된 사내 문서 내용을 찾을 수 없습니다."

        # 검색된 문서 조각들을 보기 좋게 묶기
        retrieved_texts = [
            f"[검색 문서 조각 {i+1}]\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ]
        return "\n\n".join(retrieved_texts)

    except Exception as e:
        print(f"RAG Search Error: {e}")
        return f"문서 검색 수행 중 오류 발생: {str(e)}"