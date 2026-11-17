from datetime import datetime, timezone

import pytest

from mcp_it_tools import tools
from mcp_it_tools.adapters import REGISTRY, DemoAdapter, ITAdapter, get_adapter

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def a():
    return DemoAdapter(now=NOW)


def test_demo_adapter_satisfies_interface(a):
    assert isinstance(a, ITAdapter)


def test_registry_and_unknown_adapter():
    assert "demo" in REGISTRY
    assert get_adapter("demo").name == "demo"
    with pytest.raises(ValueError, match="Known adapters: demo"):
        get_adapter("nope")


def test_noncompliant_devices(a):
    res = {d["device"]: d["reasons"] for d in tools.list_noncompliant_devices(a)}
    assert set(res) == {"MBP-GRACE", "MBA-ALAN", "LT-KATHERINE", "MBP-LINUS", "LT-ROSALIND"}
    assert res["MBA-ALAN"] == ["disk not encrypted"]
    assert res["LT-KATHERINE"] == ["firewall off"]
    assert "OS 14.2 is below minimum 15.0" in res["MBP-GRACE"]
    assert res["MBP-LINUS"] == ["last check-in 41 days ago"]
    assert len(res["LT-ROSALIND"]) == 2  # unencrypted and old OS


def test_check_in_threshold_is_configurable(a):
    names = [d["device"] for d in tools.list_noncompliant_devices(a, max_check_in_days=60)]
    assert "MBP-LINUS" not in names


def test_inactive_app_users(a):
    res = tools.find_inactive_app_users(a, "cloudconsole", 90)  # case-insensitive
    assert res["app"] == "CloudConsole"
    users = {u["user"]: u for u in res["inactive_users"]}
    assert set(users) == {"alan.turing@example.com", "linus.pauling@example.com"}
    assert users["linus.pauling@example.com"]["note"] == "never signed in"
    assert users["alan.turing@example.com"]["days_since_login"] == 120


def test_inactive_app_users_unknown_app(a):
    res = tools.find_inactive_app_users(a, "Nope")
    assert "error" in res and "CRM" in res["known_apps"]


def test_user_groups(a):
    res = tools.get_user_groups(a, "Ada.Lovelace@example.com")
    assert {g["group"] for g in res["groups"]} == {"all-staff", "engineering", "prod-db-readers", "billing-admins"}
    assert "error" in tools.get_user_groups(a, "ghost@example.com")


def test_offboarding_checklist(a):
    res = tools.draft_offboarding_checklist(a, "ada.lovelace@example.com")
    actions = [c["action"] for c in res["checklist"]]
    assert res["status"].startswith("DRAFT")
    assert "Remove from group 'billing-admins'" in actions
    assert "Revoke access to app 'PasswordVault'" in actions
    assert any("MBP-ADA" in s for s in actions)
    assert any("dennis.ritchie@example.com" in s for s in actions)  # direct report
    assert all(c["done"] is False for c in res["checklist"])
    assert [c["step"] for c in res["checklist"]] == list(range(1, len(actions) + 1))


def test_adapter_has_no_write_methods():
    public = {m for m in dir(DemoAdapter) if not m.startswith("_")}
    assert public <= {"name", "list_users", "list_devices", "list_groups", "list_app_access", "max_check_in_age_days", "now"}
