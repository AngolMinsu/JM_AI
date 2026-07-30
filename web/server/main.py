import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from tools import get_db_connection
from tools.langchain_tools import AGENT_TOOLS

load_dotenv(dotenv_path=".env")

app = FastAPI(title="Jaryong Mobility Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """너는 자룡모빌리티의 차량 전장 및 AI 비서다.
사원과 ECU의 조회·등록·수정·삭제는 반드시 해당 도구를 사용하고, 수정/삭제 전에는 ID를 확인한다.
BMS CSV는 전용 도구로만 CRUD한다. 의미 기반 BMS 질문은 search_bms_log_documents를 사용한다.
채용공고 PDF는 search_job_posting으로 읽기/검색만 하며 절대 수정·삭제하지 않는다.
등록·수정·삭제는 사용자의 요청이 명확할 때만 수행하고, 도구 결과에 없는 사실은 만들지 않는다."""

llm = ChatOpenAI(
    model=os.getenv("AI_MODEL", "qwen3.5"),
    api_key=os.getenv("AI_API_KEY", "no-need"),
    base_url=os.getenv("AI_SERVER_URL", "http://localhost:8080/v1"),
    temperature=0.3,
    max_tokens=8192,
)
agent = create_agent(model=llm, system_prompt=SYSTEM_PROMPT, tools=AGENT_TOOLS)


class ChatRequest(BaseModel):
    # prompt is the new API field; message keeps the existing Vue client compatible.
    prompt: str | None = None
    message: str | None = None


def _answer(prompt: str) -> str:
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")
    try:
        response = agent.invoke({"messages": [("user", prompt)]})
        content = response["messages"][-1].content
        return content if isinstance(content, str) else str(content)
    except Exception as exc:
        print(f"Chat API Error: {exc}")
        raise HTTPException(status_code=500, detail=f"AI 처리 중 오류가 발생했습니다: {exc}") from exc


@app.post("/api/v1/chat")
def chat_v1_endpoint(request: ChatRequest):
    """LangChain-agent chat endpoint using the `prompt` request field."""
    return {"answer": _answer(request.prompt or request.message or "")}


@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    """Backward-compatible endpoint used by the existing Vue client."""
    return {"reply": _answer(request.message or request.prompt or "")}


@app.get("/api/ecu-nodes")
def get_ecu_nodes():
    try:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM ecu_nodes ORDER BY node_id ASC").fetchall()
        return [dict(row) for row in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail="ECU 노드 정보를 가져오는 데 실패했습니다.") from exc


@app.get("/api/bms-logs")
def get_bms_logs_endpoint():
    try:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM bms_cell_logs ORDER BY timestamp DESC LIMIT 50").fetchall()
        return [dict(row) for row in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail="BMS 셀 로그 정보를 가져오는 데 실패했습니다.") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
