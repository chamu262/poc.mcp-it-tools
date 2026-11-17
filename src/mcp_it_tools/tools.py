"""The four IT tools, as plain functions over an adapter.

Kept separate from the MCP wiring so they are easy to test and reuse.
Every function only reads; nothing here changes any system.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .adapters.base import ITAdapter


def _version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split(".") if p.isdigit())


def _now(adapter: ITAdapter) -> datetime:
    return getattr(adapter, "now", None) or datetime.now(timezone.utc)


def list_noncompliant_devices(adapter: ITAdapter, max_check_in_days: int = 30) -> list[dict]:
    """Devices that break at least one rule: disk encryption, firewall,
    minimum OS version, or not checked in for more than `max_check_in_days`."""
    now = _now(adapter)
    out = []
    for d in adapter.list_devices():
        reasons = []
        if not d.disk_encrypted:
            reasons.append("disk not encrypted")
        if not d.firewall_on:
            reasons.append("firewall off")
        if _version_tuple(d.os_version) < _version_tuple(d.min_os_version):
            reasons.append(f"OS {d.os_version} is below minimum {d.min_os_version}")
        age = (now - d.last_check_in).days
        if age > max_check_in_days:
            reasons.append(f"last check-in {age} days ago")
        if reasons:
            out.append({"device": d.name, "serial": d.serial, "owner": d.owner,
                        "platform": d.platform, "reasons": reasons})
    return out


def find_inactive_app_users(adapter: ITAdapter, app: str, days: int = 90) -> dict:
    """Users who have access to `app` but have not signed in for `days` days
    (or never). These are candidates for an access review, not automatic removal."""
    now = _now(adapter)
    known_apps = sorted({a.app for a in adapter.list_app_access()})
    match = next((a for a in known_apps if a.lower() == app.lower()), None)
    if match is None:
        return {"error": f"Unknown app '{app}'", "known_apps": known_apps}
    inactive = []
    for a in adapter.list_app_access():
        if a.app != match:
            continue
        if a.last_login is None:
            inactive.append({"user": a.user, "last_login": None, "days_since_login": None, "note": "never signed in"})
        elif (now - a.last_login).days >= days:
            inactive.append({"user": a.user, "last_login": a.last_login.date().isoformat(),
                             "days_since_login": (now - a.last_login).days})
    return {"app": match, "threshold_days": days, "inactive_users": inactive}


def get_user_groups(adapter: ITAdapter, email: str) -> dict:
    """The groups a user belongs to, with each group's description."""
    email = email.lower()
    user = next((u for u in adapter.list_users() if u.email == email), None)
    if user is None:
        return {"error": f"No user with email '{email}'"}
    groups = [{"group": g.name, "description": g.description}
              for g in adapter.list_groups() if email in g.members]
    return {"user": user.email, "name": user.name, "groups": groups}


def draft_offboarding_checklist(adapter: ITAdapter, email: str) -> dict:
    """A draft checklist for a leaver, built from their groups, app access and
    devices. It is a draft for a person to review and act on; this tool does
    not disable or remove anything."""
    email = email.lower()
    user = next((u for u in adapter.list_users() if u.email == email), None)
    if user is None:
        return {"error": f"No user with email '{email}'"}
    groups = [g.name for g in adapter.list_groups() if email in g.members]
    apps = sorted({a.app for a in adapter.list_app_access() if a.user == email})
    devices = [d for d in adapter.list_devices() if d.owner == email]
    reports = [u.email for u in adapter.list_users() if u.manager == email]

    steps = [
        f"Confirm last working day and approval with manager ({user.manager or 'none on record'})",
        "Suspend the account and sign out all active sessions",
        "Reset multi-factor authentication methods",
        "Set an out-of-office reply and forward mail to the manager",
        "Transfer ownership of files and shared drives to the manager",
    ]
    steps += [f"Remove from group '{g}'" for g in groups if g != "all-staff"]
    steps += [f"Revoke access to app '{a}'" for a in apps]
    for d in devices:
        steps.append(f"Collect device {d.name} (serial {d.serial}) and wipe it after return")
    if reports:
        steps.append("Reassign direct reports: " + ", ".join(reports))
    steps.append("Remove from 'all-staff' and delete the account after the retention period")

    return {
        "user": user.email, "name": user.name, "department": user.department,
        "status": "DRAFT - review before acting",
        "checklist": [{"step": i + 1, "action": s, "done": False} for i, s in enumerate(steps)],
    }
