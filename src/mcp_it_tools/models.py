"""Plain data shapes shared by every adapter."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class User:
    email: str
    name: str
    department: str
    title: str
    manager: str | None
    active: bool = True


@dataclass(frozen=True)
class Device:
    serial: str
    name: str
    owner: str  # user email
    platform: str  # "macOS" | "Windows"
    os_version: str
    disk_encrypted: bool
    firewall_on: bool
    last_check_in: datetime
    min_os_version: str  # the lowest OS version the policy allows


@dataclass(frozen=True)
class Group:
    name: str
    description: str
    members: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AppAccess:
    app: str
    user: str
    last_login: datetime | None  # None means the user never signed in
