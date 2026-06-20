import pytest

from sqlagent import database
from sqlagent.seed import seed_database
from sqlagent.tools import Toolbox, calculate


def test_calculate_respects_precedence():
    assert calculate("2 + 3 * 4") == 14
    assert calculate("(10 - 2) / 4") == 2


def test_calculate_rejects_non_arithmetic():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('ls')")


def test_toolbox_lists_tables_and_blocks_writes(tmp_path):
    db_path = tmp_path / "shop.db"
    connection = database.connect(db_path)
    seed_database(connection)
    connection.close()

    toolbox = Toolbox(db_path)
    assert "customers" in toolbox.execute("list_tables", {})
    assert toolbox.execute("run_sql", {"query": "DROP TABLE customers"}).startswith("Error")
