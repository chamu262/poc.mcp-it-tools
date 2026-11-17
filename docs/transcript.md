# MCP transcript (demo data)

Tools the server advertises:

- `list_noncompliant_devices` (read-only: True) - List devices that fail a security rule (disk encryption, firewall, minimum OS version, or no check-in for more than max_check_in_days). Read-only.
- `find_inactive_app_users` (read-only: True) - Find users who have access to an app but have not signed in for at least `days` days, or never. Read-only.
- `get_user_groups` (read-only: True) - Show the groups a user (by email) belongs to. Read-only.
- `draft_offboarding_checklist` (read-only: True) - Draft an offboarding checklist for a leaver from their groups, apps and devices. Returns a draft only; it does not change anything.

## `list_noncompliant_devices({})`

```json
{
  "count": 5,
  "devices": [
    {
      "device": "MBP-GRACE",
      "serial": "C02DEMO0002",
      "owner": "grace.hopper@example.com",
      "platform": "macOS",
      "reasons": [
        "OS 14.2 is below minimum 15.0"
      ]
    },
    {
      "device": "MBA-ALAN",
      "serial": "C02DEMO0003",
      "owner": "alan.turing@example.com",
      "platform": "macOS",
      "reasons": [
        "disk not encrypted"
      ]
    },
    {
      "device": "LT-KATHERINE",
      "serial": "PF0DEMO0004",
      "owner": "katherine.johnson@example.com",
      "platform": "Windows",
      "reasons": [
        "firewall off"
      ]
    },
    {
      "device": "MBP-LINUS",
      "serial": "C02DEMO0006",
      "owner": "linus.pauling@example.com",
      "platform": "macOS",
      "reasons": [
        "last check-in 41 days ago"
      ]
    },
    {
      "device": "LT-ROSALIND",
      "serial": "PF0DEMO0009",
      "owner": "rosalind.franklin@example.com",
      "platform": "Windows",
      "reasons": [
        "disk not encrypted",
        "OS 10.0.19045 is below minimum 10.0.22631"
      ]
    }
  ]
}
```

## `find_inactive_app_users({"app": "CloudConsole", "days": 90})`

```json
{
  "app": "CloudConsole",
  "threshold_days": 90,
  "inactive_users": [
    {
      "user": "alan.turing@example.com",
      "last_login": "2026-07-20",
      "days_since_login": 120
    },
    {
      "user": "linus.pauling@example.com",
      "last_login": null,
      "days_since_login": null,
      "note": "never signed in"
    }
  ]
}
```

## `get_user_groups({"email": "ada.lovelace@example.com"})`

```json
{
  "user": "ada.lovelace@example.com",
  "name": "Ada Lovelace",
  "groups": [
    {
      "group": "all-staff",
      "description": "Everyone in the company"
    },
    {
      "group": "engineering",
      "description": "Engineering department"
    },
    {
      "group": "prod-db-readers",
      "description": "Read access to the production database"
    },
    {
      "group": "billing-admins",
      "description": "Can change billing settings"
    }
  ]
}
```

## `draft_offboarding_checklist({"email": "linus.pauling@example.com"})`

```json
{
  "user": "linus.pauling@example.com",
  "name": "Linus Pauling",
  "department": "Sales",
  "status": "DRAFT - review before acting",
  "checklist": [
    {
      "step": 1,
      "action": "Confirm last working day and approval with manager (hedy.lamarr@example.com)",
      "done": false
    },
    {
      "step": 2,
      "action": "Suspend the account and sign out all active sessions",
      "done": false
    },
    {
      "step": 3,
      "action": "Reset multi-factor authentication methods",
      "done": false
    },
    {
      "step": 4,
      "action": "Set an out-of-office reply and forward mail to the manager",
      "done": false
    },
    {
      "step": 5,
      "action": "Transfer ownership of files and shared drives to the manager",
      "done": false
    },
    {
      "step": 6,
      "action": "Remove from group 'sales'",
      "done": false
    },
    {
      "step": 7,
      "action": "Revoke access to app 'CRM'",
      "done": false
    },
    {
      "step": 8,
      "action": "Revoke access to app 'CloudConsole'",
      "done": false
    },
    {
      "step": 9,
      "action": "Collect device MBP-LINUS (serial C02DEMO0006) and wipe it after return",
      "done": false
    },
    {
      "step": 10,
      "action": "Remove from 'all-staff' and delete the account after the retention period",
      "done": false
    }
  ]
}
```
