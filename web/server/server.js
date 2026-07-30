import express from "express";
import morgan from "morgan";
import http from "http";
import sqlite3Module from "sqlite3";
import { promisify } from "node:util";
import cors from "cors";
import axios from "axios"; // npm i axios 설치 필요

// dotenv 설정
import dotenv from "dotenv";
dotenv.config({ path: ".env" });

const sqlite3 = sqlite3Module.verbose();

// DB 설정 (.env의 DB_FILE_PATH 활용)
const foundDB = new sqlite3.Database(process.env.DB_FILE_PATH);
const db = promisify(foundDB.all.bind(foundDB));

const app = express();
const PORT = 8000;

// AI 서버 URL 설정 (.env에 AI_SERVER_URL=http://localhost:8080/v1/chat/completions 등록 추천)
const AI_SERVER_URL = process.env.AI_SERVER_URL || "http://localhost:8080/v1/chat/completions";

app.use(morgan("dev"));
app.use(express.json());
app.use(cors());

// ==========================================
// AI 및 DB 연동 채팅 API
// ==========================================
app.post("/api/chat", async (req, res) => {
  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ error: "메시지를 입력해주세요." });
    }

    // AI에게 부여할 Tool(함수) 스펙 정의
    const tools = [
      {
        type: "function",
        function: {
          name: "get_employee_info",
          description: "사원 정보(mk_employee)를 조회합니다.",
          parameters: { type: "object", properties: {} }
        }
      },
      {
        type: "function",
        function: {
          name: "get_ecu_info",
          description: "ECU 전장 정보(mk_ecu)를 조회합니다.",
          parameters: { type: "object", properties: {} }
        }
      }
    ];

    // 1. AI 서버로 사용자 질문 + Tools 전달
    const ai1stResponse = await axios.post(AI_SERVER_URL, {
      model: "qwen3.5",
      messages: [{ role: "user", content: message }],
      tools: tools
    });

    const aiMessage = ai1stResponse.data.choices[0].message;

    // 2. AI가 DB 조회를 요청(Tool Call)했는지 판별
    if (aiMessage.tool_calls && aiMessage.tool_calls.length > 0) {
      const toolCall = aiMessage.tool_calls[0];
      const functionName = toolCall.function.name;
      let dbResult = [];

      // master가 promisify로 만든 db(...) 함수로 SQL 쿼리 실행
      if (functionName === "get_employee_info") {
        dbResult = await db("SELECT * FROM mk_employee LIMIT 20");
      } else if (functionName === "get_ecu_info") {
        dbResult = await db("SELECT * FROM mk_ecu LIMIT 20");
      }

      // 3. DB 조회 결과를 다시 AI에 던져서 최종 응답 생성
      const ai2ndResponse = await axios.post(AI_SERVER_URL, {
        model: "qwen3.5",
        messages: [
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
        reply: ai2ndResponse.data.choices[0].message.content
      });
    }

    // 일반 대화인 경우
    return res.json({
      reply: aiMessage.content
    });

  } catch (error) {
    console.error("Chat API Error:", error?.response?.data || error.message);
    res.status(500).json({ error: "서버 처리 중 에러가 발생했습니다." });
  }
});

const server = http.createServer(app);

server.listen(PORT, () => console.log(`This server is listening on ${PORT}`));