from typing import Any, Dict

from tools.db.repository import Repository

ecu_repo = Repository(table="ecu_nodes", pk_col="node_id")
ECU_FIELDS = ("node_name", "mcu_model", "can_baudrate", "fw_version", "status")


def handle_get_ecu(cursor, args: Dict[str, Any]):
    node_id, node_name = args.get("node_id"), args.get("node_name")
    if node_id is not None or node_name:
        row = ecu_repo.find_one(cursor, pk_val=node_id, node_name=node_name)
        return dict(row) if row else {"status": "not_found", "message": "ECU 노드를 찾을 수 없습니다."}
    return [dict(row) for row in ecu_repo.find_all(cursor, limit=100, order_by="node_id ASC")]


def handle_add_ecu(cursor, args: Dict[str, Any]):
    node_name = str(args.get("node_name") or "").strip()
    mcu_model = str(args.get("mcu_model") or "").strip()
    if not node_name or not mcu_model:
        return {"status": "error", "message": "node_name, mcu_model은 필수입니다."}
    data = {"node_name": node_name, "mcu_model": mcu_model, "can_baudrate": args.get("can_baudrate"), "fw_version": args.get("fw_version"), "status": args.get("status") or "ACTIVE"}
    return {"status": "success", "node_id": ecu_repo.insert(cursor, data), "message": "ECU 노드를 등록했습니다."}


def handle_update_ecu(cursor, args: Dict[str, Any]):
    node_id = args.get("node_id")
    if node_id is None:
        return {"status": "error", "message": "node_id는 필수입니다."}
    if not ecu_repo.find_one(cursor, pk_val=node_id):
        return {"status": "not_found", "message": "수정할 ECU 노드를 찾을 수 없습니다."}
    data = {key: str(value).strip() if isinstance(value, str) else value for key, value in args.items() if key in ECU_FIELDS and value is not None and str(value).strip()}
    if not data:
        return {"status": "error", "message": "변경할 필드를 지정하세요."}
    ecu_repo.update(cursor, node_id, data)
    return {"status": "success", "node_id": node_id, "message": "ECU 정보를 수정했습니다."}


def handle_delete_ecu(cursor, args: Dict[str, Any]):
    node_id = args.get("node_id")
    if node_id is None:
        return {"status": "error", "message": "node_id는 필수입니다."}
    if not ecu_repo.delete(cursor, node_id):
        return {"status": "not_found", "message": "삭제할 ECU 노드를 찾을 수 없습니다."}
    return {"status": "success", "node_id": node_id, "message": "ECU 정보를 삭제했습니다."}
