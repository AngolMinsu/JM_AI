import sqlite3
from typing import Any, Dict, List, Optional
from tools.db.connection import get_db_connection


class Repository:
    """SQLite 전용 범용 CRUD 리포지토리"""

    def __init__(self, table: str, pk_col: str):
        self.table = table
        self.pk_col = pk_col

    def find_one(self, cursor: sqlite3.Cursor, pk_val: Optional[Any] = None, **kwargs) -> Optional[sqlite3.Row]:
        if pk_val is not None:
            cursor.execute(f"SELECT * FROM {self.table} WHERE {self.pk_col} = ?", (pk_val,))
            return cursor.fetchone()
        
        # 키-값 기반 개별 검색 (예: name="김철수")
        for key, val in kwargs.items():
            if val is not None:
                cursor.execute(f"SELECT * FROM {self.table} WHERE {key} = ?", (str(val).strip(),))
                return cursor.fetchone()
        return None

    def find_all(self, cursor: sqlite3.Cursor, limit: int = 100, order_by: Optional[str] = None) -> List[sqlite3.Row]:
        order_clause = f"ORDER BY {order_by}" if order_by else f"ORDER BY {self.pk_col} DESC"
        cursor.execute(f"SELECT * FROM {self.table} {order_clause} LIMIT ?", (limit,))
        return cursor.fetchall()

    def insert(self, cursor: sqlite3.Cursor, data: Dict[str, Any]) -> int:
        columns = list(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO {self.table} ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(sql, list(data.values()))
        return cursor.lastrowid

    def update(self, cursor: sqlite3.Cursor, pk_val: Any, data: Dict[str, Any]) -> bool:
        if not data:
            return False
        
        set_clauses = [f"{k} = ?" for k in data.keys()]
        values = list(data.values()) + [pk_val]
        sql = f"UPDATE {self.table} SET {', '.join(set_clauses)} WHERE {self.pk_col} = ?"
        cursor.execute(sql, values)
        return cursor.rowcount > 0

    def delete(self, cursor: sqlite3.Cursor, pk_val: Any) -> bool:
        cursor.execute(f"SELECT 1 FROM {self.table} WHERE {self.pk_col} = ?", (pk_val,))
        if not cursor.fetchone():
            return False
        cursor.execute(f"DELETE FROM {self.table} WHERE {self.pk_col} = ?", (pk_val,))
        return cursor.rowcount > 0