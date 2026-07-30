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


# ==========================================
# 1. AI 챗봇 대화 API (/api/chat)
# ==========================================
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")

    try:
        # 1차 AI 호출 (Message + Tools 전달)
        response = openai_client.chat.completions.create(
            model="qwen3.5",
            messages=[
                {"role": "system", "content": "너는 유능한 차량 전장 및 AI 비서다. 필요한 툴을 적절히 사용해서 답변해라."},
                {"role": "user", "content": request.message}
            ],
            tools=ALL_TOOLS
        )

        ai_message = response.choices[0].message

        # AI가 Tool Call을 요청한 경우
        if ai_message.tool_calls:
            tool_call = ai_message.tool_calls[0]
            function_name = tool_call.function.name

            # 1. AI가 넘겨준 arguments(JSON string) 파싱
            raw_args = tool_call.function.arguments
            arguments = json.loads(raw_args) if raw_args else {}

            # 2. Tools 모듈에서 SQL/RAG 실행
            db_result = execute_tool(function_name, arguments)

            # 3. 2차 AI 호출 (DB/RAG 결과를 전달하여 최종 답변 생성)
            second_response = openai_client.chat.completions.create(
                model="qwen3.5",
                messages=[
                    {"role": "system", "content": "너는 유능한 차량 전장 및 AI 비서다."},
                    {"role": "user", "content": request.message},
                    ai_message,  # model_dump() 대신 raw ai_message 객체 사용
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(db_result, ensure_ascii=False) if isinstance(db_result, (dict, list)) else str(db_result)
                    }
                ]
            )

            reply_content = second_response.choices[0].message.content or "요청하신 처리를 완료했습니다."
            return {"reply": reply_content}

        # 일반 대화 응답
        return {"reply": ai_message.content or "응답을 생성하지 못했습니다."}

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
        cursor.execute("SELECT * FROM ecu_nodes ORDER BY node_id ASC")
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
    # 8000번 포트로 실행
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)