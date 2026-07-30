"""AI function tools for the local mobility SQLite database."""
import os
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable

try:
    from tools.rag_tool import RAG_TOOL_SPEC, execute_rag_search
except ImportError:  # Allows DB-only startup when optional RAG packages are absent.
    RAG_TOOL_SPEC = None
    execute_rag_search = None

SERVER_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = SERVER_DIR / "db" / "database.sqlite"


def get_db_connection() -> sqlite3.Connection:
    """Return a connection independent of the process working directory."""
    db_path = Path(os.getenv("DB_FILE_PATH", str(DEFAULT_DB_PATH))).expanduser()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _schema(properties: Dict[str, Any], required: Iterable[str] = ()) -> Dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}


EMPLOYEE_FIELDS = {
    "name": {"type": "string", "description": "사원 이름"},
    "department": {"type": "string", "description": "부서명"},
    "role": {"type": "string", "description": "담당 업무"},
    "join_date": {"type": "string", "description": "입사일(YYYY-MM-DD)"},
    "certifications": {"type": "string", "description": "보유 자격증"},
}
ECU_FIELDS = {
    "node_name": {"type": "string", "description": "ECU 노드명"},
    "mcu_model": {"type": "string", "description": "MCU 모델"},
    "can_baudrate": {"type": "integer", "description": "CAN 통신 속도(bps)"},
    "fw_version": {"type": "string", "description": "펌웨어 버전"},
    "status": {"type": "string", "description": "상태(예: ACTIVE, TESTING, INACTIVE)"},
}

ALL_TOOLS = [
    {"type": "function", "function": {"name": "get_employee_info", "description": "사원 정보를 조회합니다. emp_id 또는 이름으로 좁힐 수 있습니다.", "parameters": _schema({"emp_id": {"type": "integer"}, "name": {"type": "string"}})}},
    {"type": "function", "function": {"name": "add_employee", "description": "신규 사원을 등록합니다.", "parameters": _schema(EMPLOYEE_FIELDS, ("name", "department", "role"))}},
    {"type": "function", "function": {"name": "update_employee", "description": "emp_id로 사원 정보를 수정합니다. 변경할 필드만 보냅니다.", "parameters": _schema({"emp_id": {"type": "integer"}, **EMPLOYEE_FIELDS}, ("emp_id",))}},
    {"type": "function", "function": {"name": "delete_employee", "description": "emp_id로 사원을 삭제합니다.", "parameters": _schema({"emp_id": {"type": "integer"}}, ("emp_id",))}},
    {"type": "function", "function": {"name": "get_ecu_info", "description": "ECU 노드 정보를 조회합니다. node_id 또는 node_name으로 좁힐 수 있습니다.", "parameters": _schema({"node_id": {"type": "integer"}, "node_name": {"type": "string"}})}},
    {"type": "function", "function": {"name": "add_ecu", "description": "신규 ECU 노드를 등록합니다.", "parameters": _schema(ECU_FIELDS, ("node_name", "mcu_model"))}},
    {"type": "function", "function": {"name": "update_ecu", "description": "node_id로 ECU 정보를 수정합니다. 변경할 필드만 보냅니다.", "parameters": _schema({"node_id": {"type": "integer"}, **ECU_FIELDS}, ("node_id",))}},
    {"type": "function", "function": {"name": "delete_ecu", "description": "node_id로 ECU 노드를 삭제합니다.", "parameters": _schema({"node_id": {"type": "integer"}}, ("node_id",))}},
]
if RAG_TOOL_SPEC:
    ALL_TOOLS.append(RAG_TOOL_SPEC)


def _select_one(cursor: sqlite3.Cursor, table: str, id_column: str, args: Dict[str, Any], name_column: str):
    item_id = args.get(id_column)
    if item_id is not None:
        cursor.execute(f"SELECT * FROM {table} WHERE {id_column} = ?", (item_id,))
    elif args.get(name_column):
        cursor.execute(f"SELECT * FROM {table} WHERE {name_column} = ?", (str(args[name_column]).strip(),))
    else:
        return None
    return cursor.fetchone()


def _changed_fields(arguments: Dict[str, Any], allowed: Dict[str, Any]) -> tuple[list[str], list[Any]]:
    fields, values = [], []
    for field in allowed:
        if field in arguments and arguments[field] is not None:
            value = str(arguments[field]).strip() if isinstance(arguments[field], str) else arguments[field]
            if value != "":
                fields.append(f"{field} = ?")
                values.append(value)
    return fields, values


def execute_tool(function_name: str, arguments: Dict[str, Any] | None = None) -> Any:
    arguments = arguments or {}
    if function_name == "search_company_documents":
        return execute_rag_search(str(arguments.get("query", ""))) if execute_rag_search else {"status": "error", "message": "RAG 모듈을 불러올 수 없습니다."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if function_name == "get_employee_info":
            row = _select_one(cursor, "employees", "emp_id", arguments, "name")
            if arguments.get("emp_id") is not None or arguments.get("name"):
                return dict(row) if row else {"status": "not_found", "message": "사원을 찾을 수 없습니다."}
            cursor.execute("SELECT * FROM employees ORDER BY emp_id DESC LIMIT 100")
            return [dict(r) for r in cursor.fetchall()]
        if function_name == "get_ecu_info":
            row = _select_one(cursor, "ecu_nodes", "node_id", arguments, "node_name")
            if arguments.get("node_id") is not None or arguments.get("node_name"):
                return dict(row) if row else {"status": "not_found", "message": "ECU 노드를 찾을 수 없습니다."}
            cursor.execute("SELECT * FROM ecu_nodes ORDER BY node_id ASC LIMIT 100")
            return [dict(r) for r in cursor.fetchall()]
        if function_name == "add_employee":
            fields = {key: arguments.get(key) for key in EMPLOYEE_FIELDS}
            fields["join_date"] = fields["join_date"] or date.today().isoformat()
            fields["certifications"] = fields["certifications"] or "없음"
            if not all(str(fields[key] or "").strip() for key in ("name", "department", "role")):
                return {"status": "error", "message": "name, department, role은 필수입니다."}
            cursor.execute("INSERT INTO employees (name, department, role, join_date, certifications) VALUES (?, ?, ?, ?, ?)", (fields["name"].strip(), fields["department"].strip(), fields["role"].strip(), fields["join_date"], fields["certifications"]))
            conn.commit()
            return {"status": "success", "emp_id": cursor.lastrowid, "message": "사원을 등록했습니다."}
        if function_name == "add_ecu":
            fields = {key: arguments.get(key) for key in ECU_FIELDS}
            fields["status"] = fields["status"] or "ACTIVE"
            if not all(str(fields[key] or "").strip() for key in ("node_name", "mcu_model")):
                return {"status": "error", "message": "node_name, mcu_model은 필수입니다."}
            cursor.execute("INSERT INTO ecu_nodes (node_name, mcu_model, can_baudrate, fw_version, status) VALUES (?, ?, ?, ?, ?)", (fields["node_name"].strip(), fields["mcu_model"].strip(), fields["can_baudrate"], fields["fw_version"], fields["status"].strip()))
            conn.commit()
            return {"status": "success", "node_id": cursor.lastrowid, "message": "ECU 노드를 등록했습니다."}
        if function_name in ("update_employee", "update_ecu"):
            table, id_col, name_col, allowed = ("employees", "emp_id", "name", EMPLOYEE_FIELDS) if function_name == "update_employee" else ("ecu_nodes", "node_id", "node_name", ECU_FIELDS)
            target = _select_one(cursor, table, id_col, arguments, name_col)
            if not target:
                return {"status": "not_found", "message": f"수정할 {('사원' if table == 'employees' else 'ECU 노드')}을 찾을 수 없습니다. ID를 확인하세요."}
            fields, values = _changed_fields(arguments, allowed)
            if not fields:
                return {"status": "error", "message": "변경할 필드를 하나 이상 지정하세요."}
            values.append(target[id_col])
            cursor.execute(f"UPDATE {table} SET {', '.join(fields)} WHERE {id_col} = ?", values)
            conn.commit()
            return {"status": "success", id_col: target[id_col], "message": "정보를 수정했습니다."}
        if function_name in ("delete_employee", "delete_ecu"):
            table, id_col = ("employees", "emp_id") if function_name == "delete_employee" else ("ecu_nodes", "node_id")
            item_id = arguments.get(id_col)
            if item_id is None:
                return {"status": "error", "message": f"{id_col}는 필수입니다."}
            cursor.execute(f"DELETE FROM {table} WHERE {id_col} = ?", (item_id,))
            if cursor.rowcount == 0:
                return {"status": "not_found", "message": "삭제할 항목을 찾을 수 없습니다."}
            conn.commit()
            return {"status": "success", id_col: item_id, "message": "정보를 삭제했습니다."}
        return {"status": "error", "message": f"알 수 없는 도구: {function_name}"}
    except sqlite3.Error as exc:
        conn.rollback()
        return {"status": "error", "message": f"DB 작업 오류: {exc}"}
    finally:
        conn.close()
