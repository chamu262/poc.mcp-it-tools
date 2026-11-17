"""MCP server: exposes the read-only IT tools to AI agents over stdio."""
from __future__ import annotations

from mcp.types import ToolAnnotations

try:  # MCP Python SDK 2.x
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from . import tools
from .adapters import get_adapter

mcp = _Server("it-tools")

# Tell clients every tool only reads. Clients can use this to skip approval prompts.
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


@mcp.tool(annotations=READ_ONLY)
def list_noncompliant_devices(max_check_in_days: int = 30) -> dict:
    """List devices that fail a security rule (disk encryption, firewall,
    minimum OS version, or no check-in for more than max_check_in_days). Read-only."""
    devices = tools.list_noncompliant_devices(get_adapter(), max_check_in_days)
    return {"count": len(devices), "devices": devices}


@mcp.tool(annotations=READ_ONLY)
def find_inactive_app_users(app: str, days: int = 90) -> dict:
    """Find users who have access to an app but have not signed in for at
    least `days` days, or never. Read-only."""
    return tools.find_inactive_app_users(get_adapter(), app, days)


@mcp.tool(annotations=READ_ONLY)
def get_user_groups(email: str) -> dict:
    """Show the groups a user (by email) belongs to. Read-only."""
    return tools.get_user_groups(get_adapter(), email)


@mcp.tool(annotations=READ_ONLY)
def draft_offboarding_checklist(email: str) -> dict:
    """Draft an offboarding checklist for a leaver from their groups, apps and
    devices. Returns a draft only; it does not change anything."""
    return tools.draft_offboarding_checklist(get_adapter(), email)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
