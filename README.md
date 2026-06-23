# LLM SQL Agent

![CI](https://github.com/delcenjo/llm-sql-agent/actions/workflows/ci.yml/badge.svg)
[![Live demo](https://img.shields.io/badge/Live_demo-Spaces-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/delcenjo/sql-agent-demo)

Try it live: ask a question at the [interactive demo](https://huggingface.co/spaces/delcenjo/sql-agent-demo).

You ask a question in plain English, and the agent figures out the SQL on its own. There are no hand-written queries behind it: the model is handed a few tools and left to inspect the schema, write a SELECT, maybe do a bit of arithmetic, and come back with an answer.

## A quick walk-through

Say you ask:

```
Which category brings the most revenue?
```

With `--verbose` on, you can watch the agent feel its way to the answer. It does not know the column names up front, so it looks first:

```
  -> list_tables({})
  -> get_schema({'table': 'order_items'})
  -> run_sql({'query': "SELECT p.category, SUM(p.price * oi.quantity) AS revenue
                        FROM order_items oi
                        JOIN orders o ON o.id = oi.order_id
                        JOIN products p ON p.id = oi.product_id
                        WHERE o.status = 'completed'
                        GROUP BY p.category ORDER BY revenue DESC"})
```

and then replies, in this case, that **Home** is the top category. The exact query the model writes will vary from run to run; what stays fixed is that every number in the answer comes from a real tool result, not from the model's imagination.

The underlying numbers, if you run that aggregation by hand against the seeded data, look like this:

```
Home         8947.78
Electronics  4674.24
Sports       2919.71
Books        2031.03
Toys         1395.00
```

## The loop

The whole thing is a small back-and-forth. The model gets the question plus the list of tools. It either answers directly or asks to call a tool. If it asks for a tool, the toolbox runs it locally and feeds the result back, and the model gets another turn. That repeats until it produces a final answer or hits `MAX_STEPS` (6 by default), at which point the agent stops and says so rather than looping forever.

```
question -> model -> tool call -> local execution -> result -> model -> ... -> answer
```

The four tools available to it:

- `list_tables` returns the table names.
- `get_schema` returns one table's columns and their types.
- `run_sql` runs a single read-only SELECT and hands back the rows as JSON.
- `calculator` evaluates a plain arithmetic expression.

## Keeping it read-only

`run_sql` is the tool that touches the database, so it is deliberately fenced in. The connection itself is opened in SQLite read-only mode (`mode=ro`), which means a write would fail at the driver level even if everything else slipped through. On top of that, `run_select` does its own checking: it strips a trailing semicolon, rejects anything with a second statement, only accepts queries that begin with `SELECT` or `WITH`, turns away a list of write keywords (INSERT, UPDATE, DELETE, DROP, ALTER, PRAGMA and friends), and caps the result at `MAX_ROWS` (50) rows. So a query like `UPDATE products SET price = 0` never runs:

```
Error: Only SELECT queries are allowed.
```

The calculator is fenced off in a similar spirit. Instead of calling `eval`, it parses the expression into an AST and walks it, allowing only numeric constants and a handful of arithmetic operators. Something like `__import__('os').system('ls')` does not parse as arithmetic and is rejected outright.

## The sample database

There is a tiny shop schema to play against, seeded with a fixed random seed so the data is the same every time you build it: `customers`, `products`, `orders` and `order_items`, holding 20 customers, 15 products and 80 orders. Order statuses are weighted toward `completed`, with a few `shipped` and the occasional `cancelled`, which is why the revenue example above filters on completed orders.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python -m sqlagent.seed                                       # build data/shop.db
python -m sqlagent.cli "Which category brings the most revenue?" --verbose
```

The agent calls an LLM, so the CLI expects an LLM API key in your environment (copy `.env.example` to `.env` and drop your key in). If the key is missing the CLI tells you so instead of failing halfway through. The tools and the database, on the other hand, need no key at all, which is handy for the tests:

```bash
pytest
```

## Where the code lives

```
src/sqlagent/
  config.py     paths, model name and the limits (MAX_STEPS, MAX_ROWS)
  database.py   connection handling and the read-only query guard
  seed.py       builds the demo database
  tools.py      the tool definitions, the dispatcher and the calculator
  agent.py      the tool-use loop
  cli.py        command-line entry point
tests/          cover the SQL guard, the toolbox and the calculator
```

A few things that would be worth doing next: streaming the intermediate steps so you see the reasoning as it happens, letting the agent retry when a query comes back with an error, and adding automatic `LIMIT` injection as a second line of defence on query cost.
