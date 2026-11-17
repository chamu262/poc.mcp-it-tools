"""Demo adapter: serves made-up data from a bundled JSON file."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from importlib import resources
from pathlib import Path

from ..models import AppAccess, Device, Group, User


class DemoAdapter:
    name = "demo"

    def __init__(self, path: str | Path | None = None, now: datetime | None = None):
        if path is None:
            text = resources.files("mcp_it_tools").joinpath("demo_data.json").read_text()
        else:
            text = Path(path).read_text()
        self._raw = json.loads(text)
        self._now = now or datetime.now(timezone.utc)

    def _ago(self, days: int | None) -> datetime | None:
        return None if days is None else self._now - timedelta(days=days)

    def list_users(self) -> list[User]:
        return [User(active=u.get("active", True), **{k: u[k] for k in ("email", "name", "department", "title", "manager")})
                for u in self._raw["users"]]

    def list_devices(self) -> list[Device]:
        mins = self._raw["policy"]["min_os_version"]
        return [
            Device(
                serial=d["serial"], name=d["name"], owner=d["owner"], platform=d["platform"],
                os_version=d["os_version"], disk_encrypted=d["disk_encrypted"],
                firewall_on=d["firewall_on"], last_check_in=self._ago(d["check_in_days_ago"]),
                min_os_version=mins[d["platform"]],
            )
            for d in self._raw["devices"]
        ]

    def list_groups(self) -> list[Group]:
        return [Group(g["name"], g["description"], tuple(g["members"])) for g in self._raw["groups"]]

    def list_app_access(self) -> list[AppAccess]:
        return [AppAccess(a["app"], a["user"], self._ago(a["last_login_days_ago"])) for a in self._raw["app_access"]]

    @property
    def max_check_in_age_days(self) -> int:
        return self._raw["policy"]["max_check_in_age_days"]

    @property
    def now(self) -> datetime:
        return self._now
