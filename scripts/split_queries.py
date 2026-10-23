
"""Split q09_to_q25.sql into individual SQL query files."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERY_DIR = ROOT / "sql" / "queries"
SOURCE_FILE = QUERY_DIR / "q09_to_q25.sql"

if not SOURCE_FILE.is_file():
    raise FileNotFoundError(
        f"Combined SQL file not found: {SOURCE_FILE}"
    )

source = SOURCE_FILE.read_text(encoding="utf-8")
QUERY_DIR.mkdir(parents=True, exist_ok=True)

blocks = re.split(r"^-- ==== ", source, flags=re.MULTILINE)[1:]

if not blocks:
    raise ValueError(
        "No query blocks found. Check the '-- ==== Qnn ====' markers."
    )

for block in blocks:
    header, separator, body = block.partition("\n")

    if not separator:
        continue

    match = re.match(r"(Q\d+[a-z]?)\b", header.strip(), re.IGNORECASE)

    if not match:
        continue

    name = match.group(1).lower()
    output_file = QUERY_DIR / f"{name}.sql"
    output_file.write_text(body.strip() + "\n", encoding="utf-8")
    print(f"Created: {output_file.name}")

print("Finished splitting SQL queries.")
