"""CRUD and RAG helpers for the BMS CSV source of truth."""
import csv
from pathlib import Path
from typing import Any, Dict, Iterable

CSV_PATH = Path(__file__).resolve().parents[1] / "db" / "bms_cell_logs_2026.csv"
CSV_COLUMNS = ("timestamp", "pack_id", "cell_volt_min", "cell_volt_max", "disparity_mv", "temp_celsius", "status")


def _schema(properties: Dict[str, Any], required: Iterable[str] = ()) -> Dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}


BMS_FIELDS = {
    "timestamp": {"type": "string", "description": "측정 시각(YYYY-MM-DD HH:MM:SS)"},
    "pack_id": {"type": "string", "description": "배터리 팩 ID"},
    "cell_volt_min": {"type": "number", "description": "최저 셀 전압(V)"},
    "cell_volt_max": {"type": "number", "description": "최고 셀 전압(V)"},
    "disparity_mv": {"type": "integer", "description": "셀 전압 편차(mV)"},
    "temp_celsius": {"type": "number", "description": "온도(°C)"},
    "status": {"type": "string", "description": "상태(NORMAL/WARNING/CRITICAL)"},
}

CSV_TOOL_SPECS = [
    {"type": "function", "function": {"name": "get_bms_logs", "description": "BMS CSV 로그를 조회합니다. timestamp 또는 pack_id로 필터링할 수 있습니다.", "parameters": _schema({"timestamp": BMS_FIELDS["timestamp"], "pack_id": BMS_FIELDS["pack_id"], "limit": {"type": "integer", "description": "반환 최대 건수(기본 50)"}})}},
    {"type": "function", "function": {"name": "add_bms_log", "description": "BMS CSV에 로그를 추가하고 DB를 동기화합니다.", "parameters": _schema(BMS_FIELDS, CSV_COLUMNS)}},
    {"type": "function", "function": {"name": "update_bms_log", "description": "timestamp와 pack_id로 BMS CSV 로그를 수정합니다. 두 키 외 변경할 필드만 보냅니다.", "parameters": _schema(BMS_FIELDS, ("timestamp", "pack_id"))}},
    {"type": "function", "function": {"name": "delete_bms_log", "description": "timestamp와 pack_id로 BMS CSV 로그를 삭제하고 DB를 동기화합니다.", "parameters": _schema({"timestamp": BMS_FIELDS["timestamp"], "pack_id": BMS_FIELDS["pack_id"]}, ("timestamp", "pack_id"))}},
    {"type": "function", "function": {"name": "search_bms_log_documents", "description": "BMS CSV를 RAG로 의미 기반 검색합니다. 특정 이상 징후·추세 같은 질문에 사용합니다.", "parameters": _schema({"query": {"type": "string"}}, ("query",))}},
]


def load_csv_documents():
    """Return chunkable BMS documents without requiring Docling."""
    from langchain_core.documents import Document
    rows = _read_rows()
    return [Document(page_content="\n".join(" | ".join(f"{key}={value}" for key, value in row.items()) for row in rows[index:index + 100]), metadata={"source": CSV_PATH.name, "kind": "bms_log", "row_start": index + 1}) for index in range(0, len(rows), 100)]


def _read_rows() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"BMS CSV 파일이 없습니다: {CSV_PATH}")
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _write_rows(rows: list[dict[str, Any]]) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows({column: row.get(column, "") for column in CSV_COLUMNS} for row in rows)


def _sync_to_database(rows: list[dict[str, Any]]) -> None:
    """Keep the existing /api/bms-logs endpoint aligned with the CSV file."""
    from tools.db.connection import get_db_connection
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM bms_cell_logs")
        conn.executemany(
            "INSERT INTO bms_cell_logs (timestamp, pack_id, cell_volt_min, cell_volt_max, disparity_mv, temp_celsius, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [tuple(row.get(column, "") for column in CSV_COLUMNS) for row in rows],
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_csv_tool(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any] | list[Dict[str, Any]]:
    try:
        if function_name == "search_bms_log_documents":
            from tools.rag_tool import execute_rag_search
            return execute_rag_search(str(arguments.get("query", "")), source=CSV_PATH.name)

        rows = _read_rows()
        if function_name == "get_bms_logs":
            filtered = [row for row in rows if (not arguments.get("timestamp") or row["timestamp"] == arguments["timestamp"]) and (not arguments.get("pack_id") or row["pack_id"] == arguments["pack_id"])]
            return filtered[:max(1, min(int(arguments.get("limit", 50)), 500))]

        key = (str(arguments.get("timestamp", "")).strip(), str(arguments.get("pack_id", "")).strip())
        if function_name == "add_bms_log":
            if not all(str(arguments.get(field, "")).strip() for field in CSV_COLUMNS):
                return {"status": "error", "message": "모든 BMS 로그 필드는 필수입니다."}
            if any((row["timestamp"], row["pack_id"]) == key for row in rows):
                return {"status": "error", "message": "동일 timestamp와 pack_id의 로그가 이미 있습니다."}
            row = {field: str(arguments[field]).strip() for field in CSV_COLUMNS}
            rows.append(row)
            _write_rows(rows)
            _sync_to_database(rows)
            return {"status": "success", "message": "BMS CSV 로그를 추가했습니다. RAG 검색 반영을 위해 색인을 다시 생성하세요.", "log": row, "rag_index_stale": True}

        matches = [index for index, row in enumerate(rows) if (row["timestamp"], row["pack_id"]) == key]
        if not matches:
            return {"status": "not_found", "message": "대상 BMS 로그를 찾을 수 없습니다."}
        if function_name == "update_bms_log":
            changed = [field for field in CSV_COLUMNS if field not in ("timestamp", "pack_id") and field in arguments and arguments[field] is not None]
            if not changed:
                return {"status": "error", "message": "변경할 필드를 하나 이상 지정하세요."}
            for field in changed:
                rows[matches[0]][field] = str(arguments[field]).strip()
            _write_rows(rows)
            _sync_to_database(rows)
            return {"status": "success", "message": "BMS CSV 로그를 수정했습니다. RAG 검색 반영을 위해 색인을 다시 생성하세요.", "log": rows[matches[0]], "rag_index_stale": True}
        if function_name == "delete_bms_log":
            removed = rows.pop(matches[0])
            _write_rows(rows)
            _sync_to_database(rows)
            return {"status": "success", "message": "BMS CSV 로그를 삭제했습니다. RAG 검색 반영을 위해 색인을 다시 생성하세요.", "log": removed, "rag_index_stale": True}
        return {"status": "error", "message": f"알 수 없는 CSV 도구: {function_name}"}
    except (OSError, ValueError, KeyError) as exc:
        return {"status": "error", "message": f"BMS CSV 처리 오류: {exc}"}
