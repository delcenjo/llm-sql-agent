import sqlite3

from .config import MAX_ROWS

FORBIDDEN_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter", "create",
    "replace", "attach", "detach", "pragma", "vacuum", "reindex",
}


def connect(db_path, read_only=False):
    if read_only:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def list_tables(connection):
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return [row["name"] for row in rows]


def table_schema(connection, table):
    if table not in list_tables(connection):
        raise ValueError(f"Unknown table: {table}")
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return [{"column": row["name"], "type": row["type"]} for row in rows]


def run_select(connection, query, max_rows=MAX_ROWS):
    statement = query.strip().rstrip(";").strip()
    if not statement:
        raise ValueError("Empty query.")
    if ";" in statement:
        raise ValueError("Only a single statement is allowed.")
    tokens = statement.lower().split()
    if tokens[0] not in {"select", "with"}:
        raise ValueError("Only SELECT queries are allowed.")
    if FORBIDDEN_KEYWORDS.intersection(tokens):
        raise ValueError("Query contains a forbidden keyword.")
    rows = connection.execute(statement).fetchmany(max_rows)
    return [dict(row) for row in rows]
