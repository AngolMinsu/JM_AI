from datetime import date
from typing import Any, Dict
from tools.db.repository import Repository

emp_repo = Repository(table="employees", pk_col="emp_id")

def handle_get_employee(cursor, args: Dict[str, Any]):
    emp_id, name = args.get("emp_id"), args.get("name")
    if emp_id is not None or name:
        row = emp_repo.find_one(cursor, pk_val=emp_id, name=name)
        return dict(row) if row else {"status": "not_found", "message": "사원을 찾을 수 없습니다."}
    return [dict(r) for r in emp_repo.find_all(cursor, limit=100)]

def handle_add_employee(cursor, args: Dict[str, Any]):
    name = str(args.get("name") or "").strip()
    department = str(args.get("department") or "").strip()
    role = str(args.get("role") or "").strip()

    if not all([name, department, role]):
        return {"status": "error", "message": "name, department, role은 필수입니다."}

    data = {
        "name": name,
        "department": department,
        "role": role,
        "join_date": args.get("join_date") or date.today().isoformat(),
        "certifications": args.get("certifications") or "없음",
    }
    new_id = emp_repo.insert(cursor, data)
    return {"status": "success", "emp_id": new_id, "message": "사원을 등록했습니다."}

def handle_update_employee(cursor, args: Dict[str, Any]):
    emp_id = args.get("emp_id")
    target = emp_repo.find_one(cursor, pk_val=emp_id, name=args.get("name"))
    if not target:
        return {"status": "not_found", "message": "수정할 사원을 찾을 수 없습니다."}

    # 수정할 데이터만 필터링
    update_data = {
        k: str(v).strip() if isinstance(v, str) else v
        for k, v in args.items()
        if k in ("name", "department", "role", "join_date", "certifications") and v is not None and str(v).strip() != ""
    }
    if not update_data:
        return {"status": "error", "message": "변경할 필드를 지정하세요."}

    emp_repo.update(cursor, target["emp_id"], update_data)
    return {"status": "success", "emp_id": target["emp_id"], "message": "사원 정보를 수정했습니다."}

def handle_delete_employee(cursor, args: Dict[str, Any]):
    emp_id = args.get("emp_id")
    if emp_id is None:
        return {"status": "error", "message": "emp_id는 필수입니다."}
    
    if not emp_repo.delete(cursor, emp_id):
        return {"status": "not_found", "message": "삭제할 사원을 찾을 수 없습니다."}
    return {"status": "success", "emp_id": emp_id, "message": "사원 정보를 삭제했습니다."}