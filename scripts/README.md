# scripts/

Helper scripts. Not part of the installed package.

| File | What it does |
|---|---|
| [demo_client.py](demo_client.py) | Starts the MCP server, lists its tools, and calls each one the way an AI agent would. Prints a Markdown transcript. CI runs it as a smoke test (a quick "does it start and answer" check). |

```bash
uv run python scripts/demo_client.py
```

Saved output: [docs/transcript.md](../docs/transcript.md).
