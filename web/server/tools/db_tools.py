import sqlite3
import json
import os

# DB 조회용 헬퍼 함수
def get_db_connection():
    db_path = os.getenv("DB_FILE_PATH", "./db/database.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Dict 형태로 변환하기 위함
    return conn

# 1. AI에 전달할 Tools 정의 (OpenAI Schema)
ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_employee_info",
            "description": "사원 정보(employees)를 조회합니다.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ecu_info",
            "description": "ECU 노드 정보(ecu_nodes)를 조회합니다.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# 2. Tool 실행 핸들러
def execute_tool(function_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if function_name == "get_employee_info":
        cursor.execute("SELECT * FROM employees LIMIT 20")
    elif function_name == "get_ecu_info":
        cursor.execute("SELECT * FROM ecu_nodes LIMIT 20")
    else:
        conn.close()
        return []

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows