"""LangChain adapters for the application's domain tools.

The domain implementations remain in ``handlers/``, ``csv_tool.py`` and
``pdf_tool.py``.  This module only exposes typed, agent-friendly tools.
"""
from typing import Any

from langchain.tools import tool

from tools import execute_tool


def _call(name: str, **arguments: Any) -> Any:
    return execute_tool(name, {key: value for key, value in arguments.items() if value is not None})


@tool
def get_employee_info(emp_id: int | None = None, name: str | None = None) -> Any:
    """사원 정보를 조회한다. 특정 사원은 emp_id 또는 이름으로 조회한다."""
    return _call("get_employee_info", emp_id=emp_id, name=name)


@tool
def add_employee(name: str, department: str, role: str, join_date: str | None = None, certifications: str | None = None) -> Any:
    """신규 사원을 등록한다. name, department, role은 필수다."""
    return _call("add_employee", name=name, department=department, role=role, join_date=join_date, certifications=certifications)


@tool
def update_employee(emp_id: int, name: str | None = None, department: str | None = None, role: str | None = None, join_date: str | None = None, certifications: str | None = None) -> Any:
    """emp_id로 사원 정보를 수정한다. 변경할 필드만 전달한다."""
    return _call("update_employee", emp_id=emp_id, name=name, department=department, role=role, join_date=join_date, certifications=certifications)


@tool
def delete_employee(emp_id: int) -> Any:
    """emp_id로 사원을 삭제한다."""
    return _call("delete_employee", emp_id=emp_id)


@tool
def get_ecu_info(node_id: int | None = None, node_name: str | None = None) -> Any:
    """ECU 노드 정보를 조회한다. 특정 노드는 node_id 또는 node_name으로 조회한다."""
    return _call("get_ecu_info", node_id=node_id, node_name=node_name)


@tool
def add_ecu(node_name: str, mcu_model: str, can_baudrate: int | None = None, fw_version: str | None = None, status: str | None = None) -> Any:
    """신규 ECU 노드를 등록한다. node_name과 mcu_model은 필수다."""
    return _call("add_ecu", node_name=node_name, mcu_model=mcu_model, can_baudrate=can_baudrate, fw_version=fw_version, status=status)


@tool
def update_ecu(node_id: int, node_name: str | None = None, mcu_model: str | None = None, can_baudrate: int | None = None, fw_version: str | None = None, status: str | None = None) -> Any:
    """node_id로 ECU 노드 정보를 수정한다. 변경할 필드만 전달한다."""
    return _call("update_ecu", node_id=node_id, node_name=node_name, mcu_model=mcu_model, can_baudrate=can_baudrate, fw_version=fw_version, status=status)


@tool
def delete_ecu(node_id: int) -> Any:
    """node_id로 ECU 노드를 삭제한다."""
    return _call("delete_ecu", node_id=node_id)


@tool
def get_bms_logs(timestamp: str | None = None, pack_id: str | None = None, limit: int = 50) -> Any:
    """BMS CSV 로그를 조회한다. timestamp 또는 pack_id로 필터링할 수 있다."""
    return _call("get_bms_logs", timestamp=timestamp, pack_id=pack_id, limit=limit)


@tool
def add_bms_log(timestamp: str, pack_id: str, cell_volt_min: float, cell_volt_max: float, disparity_mv: int, temp_celsius: float, status: str) -> Any:
    """BMS CSV 로그를 추가하고 SQLite 조회 테이블을 동기화한다."""
    return _call("add_bms_log", timestamp=timestamp, pack_id=pack_id, cell_volt_min=cell_volt_min, cell_volt_max=cell_volt_max, disparity_mv=disparity_mv, temp_celsius=temp_celsius, status=status)


@tool
def update_bms_log(timestamp: str, pack_id: str, cell_volt_min: float | None = None, cell_volt_max: float | None = None, disparity_mv: int | None = None, temp_celsius: float | None = None, status: str | None = None) -> Any:
    """timestamp와 pack_id로 BMS CSV 로그를 수정한다."""
    return _call("update_bms_log", timestamp=timestamp, pack_id=pack_id, cell_volt_min=cell_volt_min, cell_volt_max=cell_volt_max, disparity_mv=disparity_mv, temp_celsius=temp_celsius, status=status)


@tool
def delete_bms_log(timestamp: str, pack_id: str) -> Any:
    """timestamp와 pack_id로 BMS CSV 로그를 삭제한다."""
    return _call("delete_bms_log", timestamp=timestamp, pack_id=pack_id)


@tool
def search_bms_log_documents(query: str) -> Any:
    """BMS CSV를 벡터 RAG로 의미 기반 검색한다. 이상 징후와 추세 질문에 사용한다."""
    return _call("search_bms_log_documents", query=query)


@tool
def search_job_posting(query: str) -> Any:
    """읽기 전용 채용공고 PDF를 벡터 RAG로 검색한다. 연봉, 복리후생, 직무, 자격요건 질문에 사용한다."""
    return _call("search_job_posting", query=query)


AGENT_TOOLS = [
    get_employee_info, add_employee, update_employee, delete_employee,
    get_ecu_info, add_ecu, update_ecu, delete_ecu,
    get_bms_logs, add_bms_log, update_bms_log, delete_bms_log,
    search_bms_log_documents, search_job_posting,
]
