"""The adapter interface.

An adapter is the only part that talks to a real system (or, here, to demo
data). The tools only ever call these four read methods, so adding a new
source such as an MDM or identity provider means writing one new class.
Adapters must be read-only: there are no write methods on purpose.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import AppAccess, Device, Group, User


@runtime_checkable
class ITAdapter(Protocol):
    name: str

    def list_users(self) -> list[User]: ...

    def list_devices(self) -> list[Device]: ...

    def list_groups(self) -> list[Group]: ...

    def list_app_access(self) -> list[AppAccess]: ...
