import express from "express";
import morgan from "morgan";
import http from "http";
import sqlite3Module from "sqlite3";
import { promisify } from "node:util";
import cors from "cors";
import OpenAI from "openai"; // npm i openai 설치 필요
import dotenv from "dotenv";

dotenv.config({ path: ".env" });

const sqlite3 = sqlite3Module.verbose();

// DB 설정 (.env의 DB_FILE_PATH 활용)
const foundDB = new sqlite3.Database(process.env.DB_FILE_PATH || "./db/database.sqlite");
const db = promisify(foundDB.all.bind(foundDB));

const app = express();
const PORT = 8000;

// 8080번 Qwen AI 서버를 바라보는 OpenAI 클라이언트 생성
const openai = new OpenAI({
  baseURL: process.env.AI_SERVER_URL || "http://localhost:8080/v1",
  apiKey: "no-need" // 로컬 AI 서버는 API Key가 필요 없음
});

app.use(morgan("dev"));
app.use(express.json());
app.use(cors());

// ==========================================
// AI 챗봇 대화 API (Node.js <-> Qwen 8080)
// ==========================================
app.post("/api/chat", async (req, res) => {
  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ error: "메시지를 입력해주세요." });
    }

    // AI에게 제공할 Tools (DB 조회 함수) 정의
    const tools = [
      {
        type: "function",
        function: {
          name: "get_employee_info",
          description: "사원 정보(employees)를 조회합니다.",
          parameters: { type: "object", properties: {} }
        }
      },
      {
        type: "function",
        function: {
          name: "get_ecu_info",
          description: "ECU 노드 정보(ecu_nodes)를 조회합니다.",
          parameters: { type: "object", properties: {} }
        }
      }
    ];

    // 1. Qwen AI 서버(8080)로 메시지 전달
    const response = await openai.chat.completions.create({
      model: "qwen3.5",
      messages: [
        { role: "system", content: "너는 유능한 차량 전장 및 AI 비서다. 필요한 툴을 적절히 사용해서 답변해라." },
        { role: "user", content: message }
      ],
      tools: tools
    });

    const aiMessage = response.choices[0].message;

    // 2. AI가 DB 조회를 요청(Tool Call)했는지 판단
    if (aiMessage.tool_calls && aiMessage.tool_calls.length > 0) {
      const toolCall = aiMessage.tool_calls[0];
      const functionName = toolCall.function.name;
      let dbResult = [];

      // 백엔드가 직접 SQLite DB 쿼리 실행
      if (functionName === "get_employee_info") {
        dbResult = await db("SELECT * FROM employees LIMIT 20");
      } else if (functionName === "get_ecu_info") {
        dbResult = await db("SELECT * FROM ecu_nodes LIMIT 20");
      }

      // 3. DB 조회 결과를 AI에 다시 보내서 최종 답변 생성
      const secondResponse = await openai.chat.completions.create({
        model: "qwen3.5",
        messages: [
          { role: "system", content: "너는 유능한 차량 전장 및 AI 비서다." },
          { role: "user", content: message },
          aiMessage,
          {
            role: "tool",
            tool_call_id: toolCall.id,
            content: JSON.stringify(dbResult)
          }
        ]
      });

      return res.json({
        reply: secondResponse.choices[0].message.content
      });
    }

    // 일반 대화 응답 전달
    return res.json({
      reply: aiMessage.content
    });

  } catch (error) {
    console.error("Chat API Error:", error?.message || error);
    res.status(500).json({ error: "AI 처리 중 오류가 발생했습니다." });
  }
});

const server = http.createServer(app);
server.listen(PORT, () => console.log(`Node Backend Server listening on port ${PORT}`));