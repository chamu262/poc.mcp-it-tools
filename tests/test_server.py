"""End-to-end: start the real MCP server over stdio and call its tools."""
import json
import os
import sys

import pytest

mcp = pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402
import anyio  # noqa: E402


async def _run():
    params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_it_tools.server"],
                                    env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            names = {t.name for t in (await s.list_tools()).tools}
            res = await s.call_tool("get_user_groups", {"email": "tim.berners@example.com"})
            return names, json.loads(res.content[0].text)


def test_server_lists_and_calls_tools():
    names, groups = anyio.run(_run)
    assert names == {"list_noncompliant_devices", "find_inactive_app_users",
                     "get_user_groups", "draft_offboarding_checklist"}
    assert {g["group"] for g in groups["groups"]} == {"all-staff", "it-admins"}
