import sqlite3
from typing import Any, Dict
from tools.db.connection import get_db_connection
from tools.schemas import ALL_TOOLS
from tools.handlers.employee import (
    handle_get_employee, handle_add_employee, 
    handle_update_employee, handle_delete_employee
)
from tools.handlers.ecu import (
    handle_get_ecu, handle_add_ecu, 
    handle_update_ecu, handle_delete_ecu
)
from tools.csv_tool import CSV_TOOL_SPECS, execute_csv_tool
from tools.pdf_tool import execute_pdf_tool

# 핸들러 레지스트리 (Strategy Pattern)
TOOL_HANDLERS = {
    "get_employee_info": handle_get_employee,
    "add_employee": handle_add_employee,
    "update_employee": handle_update_employee,
    "delete_employee": handle_delete_employee,
    "get_ecu_info": handle_get_ecu,
    "add_ecu": handle_add_ecu,
    "update_ecu": handle_update_ecu,
    "delete_ecu": handle_delete_ecu,
}
CSV_TOOL_NAMES = {spec["function"]["name"] for spec in CSV_TOOL_SPECS}

def execute_tool(function_name: str, arguments: Dict[str, Any] | None = None) -> Any:
    arguments = arguments or {}

    if function_name in CSV_TOOL_NAMES:
        return execute_csv_tool(function_name, arguments)
    if function_name == "search_job_posting":
        return execute_pdf_tool(arguments)

    handler = TOOL_HANDLERS.get(function_name)
    if not handler:
        return {"status": "error", "message": f"알 수 없는 도구: {function_name}"}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = handler(cursor, arguments)
        conn.commit()
        return result
    except sqlite3.Error as exc:
        conn.rollback()
        return {"status": "error", "message": f"DB 작업 오류: {exc}"}
    finally:
        conn.close()
