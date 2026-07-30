import os
import sqlite3
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

from tools.db_tools import ALL_TOOLS, execute_tool, get_db_connection

# .env 로드
load_dotenv(dotenv_path=".env")

app = FastAPI(title="Jaryong Mobility Backend")

# CORS 설정 (Vue 5173 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 8080번 Qwen AI 서버 클라이언트
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8080/v1")
openai_client = OpenAI(
    base_url=AI_SERVER_URL,
    api_key="no-need"
)

# Request Body 스키마
class ChatRequest(BaseModel):
    message: str


SYSTEM_PROMPT = """너는 자룡모빌리티의 차량 전장 및 AI 비서다.
사원/ECU DB 질의와 변경은 반드시 제공된 도구를 사용하고, 조회 결과의 ID를 함께 안내한다.
채용공고 PDF는 search_job_posting, BMS CSV의 의미 기반 질문은 search_bms_log_documents를 사용한다.
BMS CSV는 전용 도구로만 CRUD하고, PDF는 어떤 경우에도 읽기/검색만 한다.
등록·수정·삭제는 사용자의 요청이 명확할 때만 수행한다. 도구 결과에 없는 사실을 만들지 말고 한국어로 간결하게 답한다."""


# ==========================================
# 1. AI 챗봇 대화 API (/api/chat)
# ==========================================
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")

    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.message},
        ]
        # A model can ask for several tools at once, or use a second tool after
        # seeing the first result.  Keep the complete tool-call conversation.
        for _ in range(6):
            response = openai_client.chat.completions.create(
                model=os.getenv("AI_MODEL", "qwen3.5"), messages=messages, tools=ALL_TOOLS
            )
            ai_message = response.choices[0].message
            if not ai_message.tool_calls:
                return {"reply": ai_message.content or "응답을 생성하지 못했습니다."}

            messages.append(ai_message)
            for tool_call in ai_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    result = {"status": "error", "message": "도구 인자 형식이 올바른 JSON이 아닙니다."}
                else:
                    result = execute_tool(function_name, arguments)
                print(f"[Tool] {function_name}: {result}")
                messages.append({
                    "role": "tool", "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False),
                })
        return {"reply": "도구 호출 횟수가 제한을 초과했습니다. 요청을 나누어 다시 시도해주세요."}

    except Exception as e:
        print(f"Chat API Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 처리 중 오류가 발생했습니다: {str(e)}")


# ==========================================
# 2. ECU 노드 목록 전체 조회 API (/api/ecu-nodes)
# ==========================================
@app.get("/api/ecu-nodes")
async def get_ecu_nodes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ecu_nodes ORDER BY rowid ASC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"ECU Nodes Fetch Error: {e}")
        raise HTTPException(status_code=500, detail="ECU 노드 정보를 가져오는 데 실패했습니다.")


# ==========================================
# 3. BMS 셀 로그 전체 조회 API (/api/bms-logs)
# ==========================================
@app.get("/api/bms-logs")
async def get_bms_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bms_cell_logs ORDER BY timestamp DESC LIMIT 50")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"BMS Logs Fetch Error: {e}")
        raise HTTPException(status_code=500, detail="BMS 셀 로그 정보를 가져오는 데 실패했습니다.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
