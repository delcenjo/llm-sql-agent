import pytest

from sqlagent import database
from sqlagent.seed import seed_database


def make_db(tmp_path):
    db_path = tmp_path / "test.db"
    connection = database.connect(db_path)
    seed_database(connection)
    connection.close()
    return db_path


def test_lists_expected_tables(tmp_path):
    with database.connect(make_db(tmp_path), read_only=True) as connection:
        assert set(database.list_tables(connection)) == {
            "customers", "products", "orders", "order_items",
        }


def test_select_returns_rows(tmp_path):
    with database.connect(make_db(tmp_path), read_only=True) as connection:
        rows = database.run_select(connection, "SELECT COUNT(*) AS n FROM products")
    assert rows[0]["n"] == 15


def test_rejects_write_statements(tmp_path):
    with database.connect(make_db(tmp_path), read_only=True) as connection:
        with pytest.raises(ValueError):
            database.run_select(connection, "DELETE FROM products")


def test_rejects_multiple_statements(tmp_path):
    with database.connect(make_db(tmp_path), read_only=True) as connection:
        with pytest.raises(ValueError):
            database.run_select(connection, "SELECT 1; SELECT 2")
