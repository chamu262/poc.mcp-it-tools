"""Start the MCP server over stdio, call every tool like an AI agent would,
and print a Markdown transcript of the requests and responses.

    uv run python scripts/demo_client.py > docs/transcript.md
"""
import json
import os
import sys

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CALLS = [
    ("list_noncompliant_devices", {}),
    ("find_inactive_app_users", {"app": "CloudConsole", "days": 90}),
    ("get_user_groups", {"email": "ada.lovelace@example.com"}),
    ("draft_offboarding_checklist", {"email": "linus.pauling@example.com"}),
]


async def main():
    params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_it_tools.server"],
                                   env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print("# MCP transcript (demo data)\n")
            print("Tools the server advertises:\n")
            for t in tools:
                a = t.annotations
                ro = getattr(a, "read_only_hint", getattr(a, "readOnlyHint", None))
                description = " ".join((t.description or "").split())
                print(f"- `{t.name}` (read-only: {ro}) - {description}")
            for name, args in CALLS:
                res = await s.call_tool(name, args)
                text = "\n".join(c.text for c in res.content if hasattr(c, "text"))
                try:
                    text = json.dumps(json.loads(text), indent=2)
                except ValueError:
                    pass
                print(f"\n## `{name}({json.dumps(args)})`\n\n```json\n{text}\n```")


anyio.run(main)
