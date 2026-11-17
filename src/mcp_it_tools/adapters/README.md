# adapters/

An **adapter** is the only code that knows where data comes from. The tools
call the same four methods whatever the source, so adding a real system means
writing one class, with no changes to the tools.

| File | What it does |
|---|---|
| [base.py](base.py) | The `ITAdapter` interface: `list_users`, `list_devices`, `list_groups`, `list_app_access`. No write methods, on purpose. |
| [demo.py](demo.py) | `DemoAdapter`, which reads the bundled made-up data. The only adapter shipped. |
| [\_\_init\_\_.py](__init__.py) | The registry: maps a name to an adapter. `MCP_IT_ADAPTER` picks one (default `demo`). |

## Adding a new adapter

1. Create `myadapter.py` with a class that has `name` and the four `list_*`
   methods, each returning the shapes in [models.py](../models.py).
2. Register it in `REGISTRY` in `__init__.py`, e.g. `"jamf": JamfAdapter`.
3. Run the server with `MCP_IT_ADAPTER=jamf`.
4. Add a test like `test_demo_adapter_satisfies_interface`.

Likely sources: Jamf or Intune for devices; Entra ID or Google Workspace for
users, groups and sign-in times. Give the adapter read-only API credentials too,
so safety doesn't depend on the code alone. Read secrets from environment
variables; never commit them.
