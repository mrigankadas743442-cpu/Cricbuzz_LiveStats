"""Create the database from the SQL files."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.connection import DB_PATH, get_connection


def run_sql_file(conn, name: str) -> None:
    sql = (ROOT / "sql" / name).read_text(encoding="utf-8")
    conn.executescript(sql)
    print(f"Executed {name}")


def main() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()  # rebuild from scratch (dev only)
    with get_connection() as conn:
        for f in ("schema.sql", "views.sql", "seed_data.sql"):
            run_sql_file(conn, f)
    print(f"Database ready at {DB_PATH}")


if __name__ == "__main__":
    main()