"""Adapter registry. Pick one with the MCP_IT_ADAPTER environment variable."""
from __future__ import annotations

import os
from typing import Callable

from .base import ITAdapter
from .demo import DemoAdapter

# To add a real system, write a class that satisfies ITAdapter and register it
# here, e.g. "jamf": JamfAdapter, "intune": IntuneAdapter,
# "entra": EntraAdapter, "google": GoogleWorkspaceAdapter.
REGISTRY: dict[str, Callable[[], ITAdapter]] = {
    "demo": DemoAdapter,
}


def get_adapter(name: str | None = None) -> ITAdapter:
    name = (name or os.environ.get("MCP_IT_ADAPTER") or "demo").lower()
    try:
        return REGISTRY[name]()
    except KeyError:
        known = ", ".join(sorted(REGISTRY))
        raise ValueError(f"Unknown adapter '{name}'. Known adapters: {known}") from None


__all__ = ["ITAdapter", "DemoAdapter", "REGISTRY", "get_adapter"]
