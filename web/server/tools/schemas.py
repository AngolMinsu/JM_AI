"""OpenAI function schemas exposed by the tools package."""
from typing import Any, Dict, Iterable

from tools.csv_tool import CSV_TOOL_SPECS
from tools.pdf_tool import PDF_TOOL_SPEC


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
    "status": {"type": "string", "description": "상태(ACTIVE/TESTING/INACTIVE)"},
}

ALL_TOOLS = [
    {"type": "function", "function": {"name": "get_employee_info", "description": "사원 정보를 조회합니다.", "parameters": _schema({"emp_id": {"type": "integer"}, "name": {"type": "string"}})}},
    {"type": "function", "function": {"name": "add_employee", "description": "신규 사원을 등록합니다.", "parameters": _schema(EMPLOYEE_FIELDS, ("name", "department", "role"))}},
    {"type": "function", "function": {"name": "update_employee", "description": "emp_id로 사원 정보를 수정합니다.", "parameters": _schema({"emp_id": {"type": "integer"}, **EMPLOYEE_FIELDS}, ("emp_id",))}},
    {"type": "function", "function": {"name": "delete_employee", "description": "emp_id로 사원을 삭제합니다.", "parameters": _schema({"emp_id": {"type": "integer"}}, ("emp_id",))}},
    {"type": "function", "function": {"name": "get_ecu_info", "description": "ECU 노드 정보를 조회합니다.", "parameters": _schema({"node_id": {"type": "integer"}, "node_name": {"type": "string"}})}},
    {"type": "function", "function": {"name": "add_ecu", "description": "신규 ECU 노드를 등록합니다.", "parameters": _schema(ECU_FIELDS, ("node_name", "mcu_model"))}},
    {"type": "function", "function": {"name": "update_ecu", "description": "node_id로 ECU 정보를 수정합니다.", "parameters": _schema({"node_id": {"type": "integer"}, **ECU_FIELDS}, ("node_id",))}},
    {"type": "function", "function": {"name": "delete_ecu", "description": "node_id로 ECU 노드를 삭제합니다.", "parameters": _schema({"node_id": {"type": "integer"}}, ("node_id",))}},
    *CSV_TOOL_SPECS,
    PDF_TOOL_SPEC,
]
