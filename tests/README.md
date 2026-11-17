# tests/

Run with `uv run pytest -q`. All use the made-up demo data.

| File | What it checks |
|---|---|
| [test_tools.py](test_tools.py) | Each tool's results against known demo data (with a fixed "today" so answers don't drift), unknown inputs, the adapter registry, and that the adapter has no write methods. |
| [test_server.py](test_server.py) | End to end: starts the real MCP server, lists its tools and calls one, like an AI client would. |
| [test_viewer.py](test_viewer.py) | Starts the web viewer and loads every page. |
