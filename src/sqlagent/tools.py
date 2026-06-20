import ast
import json
import operator

from . import database
from .config import DB_PATH

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression):
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression")

    return _eval(ast.parse(expression, mode="eval").body)


class Toolbox:
    DEFINITIONS = [
        {
            "name": "list_tables",
            "description": "List all tables in the database.",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_schema",
            "description": "Return the columns and types of a given table.",
            "input_schema": {
                "type": "object",
                "properties": {"table": {"type": "string", "description": "Table name"}},
                "required": ["table"],
            },
        },
        {
            "name": "run_sql",
            "description": "Run a read-only SQL SELECT query and return the rows as JSON.",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "A single SELECT statement"}},
                "required": ["query"],
            },
        },
        {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression.",
            "input_schema": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    ]

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def execute(self, name, arguments):
        try:
            if name == "list_tables":
                return self._query(lambda c: json.dumps(database.list_tables(c)))
            if name == "get_schema":
                return self._query(lambda c: json.dumps(database.table_schema(c, arguments["table"])))
            if name == "run_sql":
                return self._query(
                    lambda c: json.dumps(database.run_select(c, arguments["query"]), default=str)
                )
            if name == "calculator":
                return str(calculate(arguments["expression"]))
            return f"Error: unknown tool '{name}'"
        except Exception as error:
            return f"Error: {error}"

    def _query(self, function):
        with database.connect(self.db_path, read_only=True) as connection:
            return function(connection)
