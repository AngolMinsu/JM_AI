from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 여기에 필요한 툴을 계속 추가하면 됩니다.
@tool
def sample_tool() -> str:
    """테스트용 툴입니다. 시스템이 정상적으로 툴을 호출하는지 확인합니다."""
    return "툴 시스템이 정상 작동 중입니다."

# 2. LLM 및 에이전트 세팅
llm = ChatOpenAI(
    model="no-need",
    api_key="no-need",
    base_url="http://localhost:8080/v1",
    temperature=0.7,
    max_tokens=8192,
)

agent = create_agent(
    model=llm,
    system_prompt="너는 유능한 AI 비서다. 필요한 툴을 적절히 사용해서 답변해라.",
    tools=[sample_tool] # 툴 추가 위치
)

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/v1/chat")
def chat_endpoint(request: ChatRequest):
    response = agent.invoke({"messages": [("user", request.prompt)]})
    final_answer = response["messages"][-1].content
    return {"answer": final_answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)