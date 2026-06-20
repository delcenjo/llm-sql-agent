import random

from . import database
from .config import DATA_DIR, DB_PATH

SCHEMA = """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    signup_date TEXT NOT NULL
);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL
);
"""

COUNTRIES = ["Spain", "France", "Germany", "Italy", "Portugal", "United Kingdom"]
NAMES = [
    "Ana", "Luis", "Marta", "Carlos", "Sofia", "Diego", "Elena", "Pablo", "Lucia",
    "Mario", "Nora", "Ivan", "Clara", "Hugo", "Sara", "Jorge", "Eva", "Raul", "Lola", "Tomas",
]
PRODUCTS = [
    ("Wireless Mouse", "Electronics", 24.99),
    ("Mechanical Keyboard", "Electronics", 79.99),
    ("USB-C Hub", "Electronics", 34.50),
    ("Noise-Cancelling Headphones", "Electronics", 149.00),
    ("Python Crash Course", "Books", 29.99),
    ("Clean Code", "Books", 33.50),
    ("The Pragmatic Programmer", "Books", 39.99),
    ("Desk Lamp", "Home", 19.99),
    ("Office Chair", "Home", 119.00),
    ("Standing Desk", "Home", 249.00),
    ("Yoga Mat", "Sports", 22.00),
    ("Dumbbell Set", "Sports", 89.99),
    ("Running Shoes", "Sports", 74.99),
    ("Board Game", "Toys", 29.50),
    ("Building Blocks", "Toys", 44.00),
]


def seed_database(connection):
    connection.executescript(SCHEMA)
    rng = random.Random(42)

    customers = [
        (i, f"{name} {chr(65 + (i % 26))}.", rng.choice(COUNTRIES),
         f"2023-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}")
        for i, name in enumerate(NAMES, start=1)
    ]
    connection.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)

    products = [(i, *product) for i, product in enumerate(PRODUCTS, start=1)]
    connection.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)

    orders, items, item_id = [], [], 0
    for order_id in range(1, 81):
        status = rng.choices(["completed", "shipped", "cancelled"], weights=[7, 2, 1])[0]
        orders.append(
            (order_id, rng.randint(1, len(customers)),
             f"2023-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}", status)
        )
        for _ in range(rng.randint(1, 4)):
            item_id += 1
            items.append((item_id, order_id, rng.randint(1, len(products)), rng.randint(1, 3)))
    connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
    connection.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", items)
    connection.commit()


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    connection = database.connect(DB_PATH)
    seed_database(connection)
    connection.close()
    print(f"Seeded database -> {DB_PATH}")


if __name__ == "__main__":
    main()
