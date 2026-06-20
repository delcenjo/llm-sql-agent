# LLM SQL Agent

A Claude-powered agent that answers natural-language questions about a SQL
database. Instead of hard-coding queries, the model is given a set of **tools**
and decides which to call — inspecting the schema, writing SQL and doing
arithmetic — until it can answer the question.

## How it works

```
question ─▶ Claude ─▶ tool call (get_schema / run_sql / calculator)
                ▲                         │
                └──── tool result ◀───────┘   (loop until the model answers)
```

The agent runs a tool-use loop: Claude proposes a tool call, the toolbox
executes it locally, the result is fed back, and the cycle repeats until the
model produces a final answer (bounded by `MAX_STEPS`).

## Tools

| Tool          | Purpose                                             |
| ------------- | --------------------------------------------------- |
| `list_tables` | list the tables in the database                     |
| `get_schema`  | return a table's columns and types                  |
| `run_sql`     | run a **read-only** SELECT and return rows as JSON  |
| `calculator`  | evaluate an arithmetic expression                   |

### Safety

`run_sql` is read-only by design: the connection is opened in SQLite read-only
mode, only single `SELECT`/`WITH` statements are allowed, write keywords are
rejected, and the result set is capped. The calculator evaluates a restricted
arithmetic AST rather than using `eval`.

## The database

A small shop database seeded with deterministic demo data: `customers`,
`products`, `orders` and `order_items` (20 customers, 15 products, 80 orders).

## Project structure

```
src/sqlagent/
  config.py     paths, model and limits
  database.py   connection and read-only query guard
  seed.py       build the demo database
  tools.py      tool definitions, dispatch and the calculator
  agent.py      Claude tool-use loop
  cli.py        command-line interface
tests/          guards, tools and calculator
```

## Usage

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python -m sqlagent.seed                                   # build the database
python -m sqlagent.cli "Which category brings the most revenue?" --verbose
pytest
```

## Example

The toolbox works without an API key. Running `run_sql` directly:

```
tables: ["customers", "order_items", "orders", "products"]

revenue by category (completed orders):
  Home         8947.78
  Electronics  4674.24
  Sports       2919.71
  Books        2031.03
  Toys         1395.00

UPDATE products SET price=0  ->  Error: Only SELECT queries are allowed.
```

With an `ANTHROPIC_API_KEY`, asking *"Which category brings the most revenue?"*
makes the agent inspect the schema, run the aggregation above and report **Home**
as the top category — without the query being written by hand.

## Possible improvements

- Stream intermediate steps and add conversation memory.
- A query-cost guard (row/time limits) and automatic `LIMIT` injection.
- A self-correction step when a query returns an error.
