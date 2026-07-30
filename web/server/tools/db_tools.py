import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any

# RAG 도구 import (파일이 있을 경우 동작)
try:
    from tools.rag_tool import RAG_TOOL_SPEC, execute_rag_search
except ImportError:
    RAG_TOOL_SPEC = None
    execute_rag_search = None


# ==========================================
# 0. SQLite DB 연결 헬퍼 함수
# ==========================================
def get_db_connection():
    db_path = os.getenv("DB_FILE_PATH", "./db/database.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Dict 형태로 Row 반환
    return conn


# ==========================================
# 1. AI에게 제공할 Tools 스펙 (OpenAI Function Schema)
# ==========================================
ALL_TOOLS = [
    # [Read] 사원 목록 조회
    {
        "type": "function",
        "function": {
            "name": "get_employee_info",
            "description": "사원 정보(employees 테이블: name, department, join_date, role, certifications) 목록을 조회합니다.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    # [Read] ECU 노드 목록 조회
    {
        "type": "function",
        "function": {
            "name": "get_ecu_info",
            "description": "ECU 노드 정보(ecu_nodes 테이블: node_name, mcu_model, can_baudrate, fw_version, status) 목록을 조회합니다.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    # [Create] 신규 사원 등록
    {
        "type": "function",
        "function": {
            "name": "add_employee",
            "description": "신규 사원 정보를 DB(employees 테이블)에 추가합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "사원 이름 (예: '김철수')"
                    },
                    "department": {
                        "type": "string",
                        "description": "부서명 (예: '전장SW팀', 'BMS개발팀', '차량제어팀', 'AI융합팀')"
                    },
                    "role": {
                        "type": "string",
                        "description": "담당 업무 및 역할 (예: 'AUTOSAR BSW 개발', 'CAN-FD 드라이버 작성')"
                    },
                    "join_date": {
                        "type": "string",
                        "description": "입사일 YYYY-MM-DD 형식 (지정하지 않으면 오늘 날짜 자동 입력)"
                    },
                    "certifications": {
                        "type": "string",
                        "description": "보유 자격증 (예: 'ISTQB', 'ISO 26262', '없음')"
                    }
                },
                "required": ["name", "department", "role"]
            }
        }
    },
    # [Update] 사원 정보 수정
    {
        "type": "function",
        "function": {
            "name": "update_employee",
            "description": "사원의 부서, 담당 업무, 입사일, 자격증 정보를 수정합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "수정할 대상 사원 이름"
                    },
                    "department": {
                        "type": "string",
                        "description": "변경할 부서명"
                    },
                    "role": {
                        "type": "string",
                        "description": "변경할 담당 업무"
                    },
                    "join_date": {
                        "type": "string",
                        "description": "변경할 입사일 (YYYY-MM-DD)"
                    },
                    "certifications": {
                        "type": "string",
                        "description": "변경할 자격증 정보"
                    }
                },
                "required": ["name"]
            }
        }
    },
    # [Delete] 사원 정보 삭제
    {
        "type": "function",
        "function": {
            "name": "delete_employee",
            "description": "사원 이름을 기반으로 사원 정보를 DB에서 삭제합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "삭제할 사원 이름"
                    }
                },
                "required": ["name"]
            }
        }
    }
]

# RAG 스펙이 존재하는 경우 ALL_TOOLS에 추가
if RAG_TOOL_SPEC:
    ALL_TOOLS.append(RAG_TOOL_SPEC)


# ==========================================
# 2. Tool 실행 핸들러 (실제 SQL 실행)
# ==========================================
def execute_tool(function_name: str, arguments: Dict[str, Any] = None) -> Any:
    arguments = arguments or {}

    # RAG 검색 도구 호출 처리
    if function_name == "search_company_documents" and execute_rag_search:
        query = arguments.get("query", "")
        return execute_rag_search(query)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ----------------------------------
        # 1. READ: 사원 정보 조회
        # ----------------------------------
        if function_name == "get_employee_info":
            # 특정 컬럼 정렬 없이 rowid 기준 최신순 정렬
            cursor.execute("SELECT name, department, join_date, role, certifications FROM employees ORDER BY rowid DESC LIMIT 20")
            rows = [dict(row) for row in cursor.fetchall()]
            return rows

        # ----------------------------------
        # 2. READ: ECU 노드 정보 조회
        # ----------------------------------
        elif function_name == "get_ecu_info":
            cursor.execute("SELECT node_name, mcu_model, can_baudrate, fw_version, status FROM ecu_nodes ORDER BY rowid ASC LIMIT 20")
            rows = [dict(row) for row in cursor.fetchall()]
            return rows

        # ----------------------------------
        # 3. CREATE: 사원 추가 (INSERT)
        # ----------------------------------
        elif function_name == "add_employee":
            name = arguments.get("name")
            department = arguments.get("department")
            role = arguments.get("role", "전장 시스템 개발")
            join_date = arguments.get("join_date", datetime.now().strftime("%Y-%m-%d"))
            certifications = arguments.get("certifications", "없음")

            # 필수값 방어 로직
            if not name or not str(name).strip():
                return {"status": "error", "message": "사원 이름(name)은 필수 항목입니다."}
            if not department or not str(department).strip():
                return {"status": "error", "message": "부서명(department)은 필수 항목입니다."}

            cursor.execute("""
                INSERT INTO employees (name, department, join_date, role, certifications)
                VALUES (?, ?, ?, ?, ?)
            """, (name, department, join_date, role, certifications))

            conn.commit()
            return {
                "status": "success",
                "message": f"사원 '{name}' 님({department} / {role})이 성공적으로 등록되었습니다."
            }

        # ----------------------------------
        # 4. UPDATE: 사원 정보 수정
        # ----------------------------------
        elif function_name == "update_employee":
            name = arguments.get("name")
            if not name:
                return {"status": "error", "message": "수정할 사원의 이름을 입력해주세요."}

            cursor.execute("SELECT * FROM employees WHERE name = ?", (name,))
            if not cursor.fetchone():
                return {"status": "error", "message": f"'{name}' 사원을 찾을 수 없습니다."}

            update_fields = []
            params = []

            for field in ["department", "role", "join_date", "certifications"]:
                if field in arguments and arguments[field]:
                    update_fields.append(f"{field} = ?")
                    params.append(arguments[field])

            if not update_fields:
                return {"status": "error", "message": "수정할 정보(부서, 역할, 입사일, 자격증 등)를 전달해주세요."}

            params.append(name)
            query = f"UPDATE employees SET {', '.join(update_fields)} WHERE name = ?"
            cursor.execute(query, params)
            conn.commit()

            return {
                "status": "success",
                "message": f"사원 '{name}' 님의 정보가 성공적으로 수정되었습니다."
            }

        # ----------------------------------
        # 5. DELETE: 사원 삭제
        # ----------------------------------
        elif function_name == "delete_employee":
            name = arguments.get("name")
            if not name:
                return {"status": "error", "message": "삭제할 사원의 이름을 입력해주세요."}

            cursor.execute("DELETE FROM employees WHERE name = ?", (name,))
            conn.commit()

            if cursor.rowcount == 0:
                return {"status": "error", "message": f"'{name}' 사원을 찾을 수 없어 삭제하지 못했습니다."}

            return {
                "status": "success",
                "message": f"사원 '{name}' 님의 정보가 DB에서 삭제되었습니다."
            }

        else:
            return {"status": "error", "message": f"알 수 없는 툴 함수입니다: {function_name}"}

    except Exception as e:
        conn.rollback()
        print(f"DB Error [{function_name}]: {e}")
        return {"status": "error", "message": f"DB 작업 중 오류가 발생했습니다: {str(e)}"}

    finally:
        conn.close()