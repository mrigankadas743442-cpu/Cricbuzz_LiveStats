
"""Run analytics queries from .sql files; safe custom-SQL runner."""

import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from database.connection import get_readonly_connection
from utils.exceptions import ValidationError

QUERY_DIR = Path(__file__).resolve().parent.parent / "sql" / "queries"
MAX_ROWS = 1000


@dataclass(frozen=True)
class QueryInfo:
    key: str
    title: str
    level: str


QUERIES: list[QueryInfo] = [
    QueryInfo("q01", "Q1 · Players representing India", "Beginner"),
    QueryInfo("q02", "Q2 · Matches in the last 30 days", "Beginner"),
    QueryInfo("q03", "Q3 · Top 10 ODI run scorers", "Beginner"),
    QueryInfo("q04", "Q4 · Venues over 50,000 capacity", "Beginner"),
    QueryInfo("q05", "Q5 · Wins per team", "Beginner"),
    QueryInfo("q06", "Q6 · Players per role", "Beginner"),
    QueryInfo("q07", "Q7 · Highest score per format", "Beginner"),
    QueryInfo("q08", "Q8 · Series starting in 2024", "Beginner"),
    QueryInfo("q09", "Q9 · All-rounders: 1000+ runs and 50+ wickets", "Intermediate"),
    QueryInfo("q10", "Q10 · Last 20 completed matches", "Intermediate"),
    QueryInfo("q11", "Q11 · Runs across formats", "Intermediate"),
    QueryInfo("q12", "Q12 · Home vs away wins", "Intermediate"),
    QueryInfo("q13", "Q13 · 100+ run partnerships", "Intermediate"),
    QueryInfo("q14", "Q14 · Bowling at venues", "Intermediate"),
    QueryInfo("q15", "Q15 · Close-match performers", "Intermediate"),
    QueryInfo("q16", "Q16 · Yearly batting trend since 2020", "Intermediate"),
    QueryInfo("q17", "Q17 · Toss advantage", "Advanced"),
    QueryInfo("q18", "Q18 · Most economical limited-overs bowlers", "Advanced"),
    QueryInfo("q19", "Q19 · Most consistent batsmen", "Advanced"),
    QueryInfo("q20", "Q20 · Matches and averages by format", "Advanced"),
    QueryInfo("q21", "Q21 · Weighted performance ranking", "Advanced"),
    QueryInfo("q22a", "Q22 · Head-to-head summary", "Advanced"),
    QueryInfo("q22b", "Q22 · Head-to-head: bat first vs bowl first", "Advanced"),
    QueryInfo("q23", "Q23 · Recent player form", "Advanced"),
    QueryInfo("q24", "Q24 · Best batting partnerships", "Advanced"),
    QueryInfo("q25a", "Q25 · Quarterly trend per player", "Advanced"),
    QueryInfo("q25b", "Q25 · Career phase", "Advanced"),
]

_BY_KEY = {query.key: query for query in QUERIES}



def load_sql(key: str) -> str:
    """Load exactly one registered SQL query."""
    if key not in _BY_KEY:
        raise ValidationError(f"Unknown query '{key}'.")

    # Prefer the exact individual query file.
    exact_path = QUERY_DIR / f"{key}.sql"
    if exact_path.is_file():
        return exact_path.read_text(encoding="utf-8")

    # Support descriptive filenames only for single-number queries.
    matches = sorted(QUERY_DIR.glob(f"{key}_*.sql"))
    matches = [p for p in matches if p.name != "q09_to_q25.sql"]

    if matches:
        return matches[0].read_text(encoding="utf-8")

    raise ValidationError(
        f"Individual query file missing: {key}.sql. "
        f"Expected it in {QUERY_DIR}"
    )


def _run(sql: str) -> pd.DataFrame:
    """Execute a saved query using a read-only database connection."""
    with get_readonly_connection() as conn:
        return pd.read_sql_query(sql, conn)


def run_named_query(key: str) -> tuple[pd.DataFrame, float]:
    """Run a saved query. Returns (DataFrame, execution time in seconds)."""
    sql = load_sql(key)

    start = time.perf_counter()
    df = _run(sql)
    elapsed = time.perf_counter() - start

    return df, elapsed


# -------------------------------------------------------------------
# Custom SQL safety
# -------------------------------------------------------------------

_BLOCKED = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|"
    r"pragma|vacuum|reindex|truncate)\b",
    re.IGNORECASE,
)


def validate_custom_sql(sql: str) -> str:
    """Allow one SELECT or WITH statement only."""
    cleaned = re.sub(r"--[^\n]*", "", sql)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip().rstrip(";").strip()

    if not cleaned:
        raise ValidationError("Please enter a query.")

    if ";" in cleaned:
        raise ValidationError("Only one SQL statement is allowed.")

    if not re.match(r"(?i)^(select|with)\b", cleaned):
        raise ValidationError("Only SELECT queries are allowed.")

    if _BLOCKED.search(cleaned):
        raise ValidationError("That statement type is not allowed here.")

    return cleaned


def run_custom_sql(sql: str) -> tuple[pd.DataFrame, float]:
    """Validate and execute custom SQL with read-only access and limits."""
    safe_sql = validate_custom_sql(sql)
    start = time.perf_counter()

    with get_readonly_connection() as conn:
        # Interrupt expensive queries after approximately five seconds.
        deadline = time.perf_counter() + 5

        conn.set_progress_handler(
            lambda: 1 if time.perf_counter() > deadline else 0,
            10000,
        )

        try:
            cursor = conn.execute(safe_sql)
            rows = cursor.fetchmany(MAX_ROWS)
            columns = [item[0] for item in cursor.description or []]

        except sqlite3.OperationalError as exc:
            raise ValidationError(f"Query failed: {exc}") from exc

    df = pd.DataFrame(
        [tuple(row) for row in rows],
        columns=columns,
    )

    elapsed = time.perf_counter() - start
    return df, elapsed
