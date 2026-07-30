"""SQLite connection factory shared by DB and CSV tools."""
import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "db" / "database.sqlite"


def get_db_connection() -> sqlite3.Connection:
    db_path = Path(os.getenv("DB_FILE_PATH", str(DEFAULT_DB_PATH))).expanduser()
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection
