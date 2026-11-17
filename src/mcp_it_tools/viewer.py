"""A tiny read-only web page that shows the demo data and tool results.

Run:  uv run mcp-it-viewer   then open http://127.0.0.1:8765
Uses only the Python standard library.
"""
from __future__ import annotations

import html
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import tools
from .adapters import get_adapter

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--fg:#1d2330;--muted:#667085;--line:#e4e7ec;--bad:#b42318;--badbg:#fef3f2;--ok:#067647;--okbg:#ecfdf3;--acc:#3b5bdb}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}
header{background:#1d2330;color:#fff;padding:14px 24px;display:flex;gap:24px;align-items:center}
header b{font-size:16px}header a{color:#c7d2fe;text-decoration:none}header a.on{color:#fff;font-weight:600}
main{max-width:1100px;margin:24px auto;padding:0 16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin-bottom:20px}
h2{margin:0 0 12px;font-size:16px}table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase}
.pill{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;margin:1px 2px}
.bad{background:var(--badbg);color:var(--bad)}.ok{background:var(--okbg);color:var(--ok)}
.muted{color:var(--muted)}form{display:flex;gap:8px;margin-bottom:12px}
input,select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;font:inherit}button{background:var(--acc);color:#fff;border:0;border-radius:6px;padding:6px 14px;font:inherit}
.banner{font-size:12px;color:var(--muted);margin-bottom:16px}
"""

PAGES = [("/", "Devices"), ("/access", "App access"), ("/groups", "Groups"), ("/offboarding", "Offboarding draft")]


def esc(v) -> str:
    return html.escape(str(v))


def page(path: str, body: str) -> str:
    nav = "".join(f'<a href="{p}" class="{"on" if p == path else ""}">{t}</a>' for p, t in PAGES)
    return (f"<!doctype html><html><head><meta charset=utf-8><title>IT Tools Viewer</title>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'><style>{CSS}</style></head>"
            f"<body><header><b>IT Tools Viewer</b>{nav}</header><main>"
            f"<div class=banner>Read-only view of made-up demo data. Same functions the MCP server exposes.</div>"
            f"{body}</main></body></html>")


def devices_view(a) -> str:
    bad = {d["serial"]: d["reasons"] for d in tools.list_noncompliant_devices(a)}
    rows = "".join(
        f"<tr><td>{esc(d.name)}</td><td>{esc(d.owner)}</td><td>{esc(d.platform)} {esc(d.os_version)}</td>"
        f"<td>{esc(d.last_check_in.date())}</td><td>"
        + ("".join(f"<span class='pill bad'>{esc(r)}</span>" for r in bad[d.serial]) if d.serial in bad
           else "<span class='pill ok'>compliant</span>")
        + "</td></tr>"
        for d in a.list_devices())
    return (f"<div class=card><h2>Devices &middot; {len(bad)} of {len(a.list_devices())} non-compliant</h2>"
            f"<table><tr><th>Device</th><th>Owner</th><th>OS</th><th>Last check-in</th><th>Status</th></tr>{rows}</table></div>")


def access_view(a, q) -> str:
    apps = sorted({x.app for x in a.list_app_access()})
    app = q.get("app", [apps[0]])[0]
    days = int(q.get("days", ["60"])[0])
    res = tools.find_inactive_app_users(a, app, days)
    if "error" in res:
        msg = f"Unknown app '{esc(app)}'. Pick one of: {esc(', '.join(apps))}"
        res = tools.find_inactive_app_users(a, apps[0], days)  # show a real app instead of an empty table
    else:
        msg = ""
    app = res["app"]  # canonical spelling, so the heading and dropdown match the table
    opts = "".join(f"<option {'selected' if x == app else ''}>{esc(x)}</option>" for x in apps)
    form = (f"<form><select name=app>{opts}</select><input name=days type=number value={days} style='width:90px'>"
            f"<button>Find inactive</button></form>")
    inactive = {u["user"] for u in res.get("inactive_users", [])}
    rows = "".join(
        f"<tr><td>{esc(x.user)}</td><td>{esc(x.last_login.date() if x.last_login else 'never')}</td><td>"
        + ("<span class='pill bad'>inactive</span>" if x.user in inactive else "<span class='pill ok'>active</span>")
        + "</td></tr>"
        for x in a.list_app_access() if x.app == res.get("app"))
    return (f"<div class=card><h2>Who has {esc(app)} but has not signed in for {days}+ days</h2>{form}"
            + (f"<div class='pill bad' style='margin-bottom:10px'>{msg}</div>" if msg else "")
            + f"<table><tr><th>User</th><th>Last login</th><th>Status</th></tr>{rows}</table></div>")


def groups_view(a) -> str:
    rows = "".join(f"<tr><td><b>{esc(g.name)}</b><div class=muted>{esc(g.description)}</div></td>"
                   f"<td>{len(g.members)}</td><td>{', '.join(esc(m.split('@')[0]) for m in g.members)}</td></tr>"
                   for g in a.list_groups())
    return f"<div class=card><h2>Groups</h2><table><tr><th>Group</th><th>Members</th><th>Who</th></tr>{rows}</table></div>"


def offboarding_view(a, q) -> str:
    users = a.list_users()
    email = q.get("email", ["ada.lovelace@example.com"])[0]
    opts = "".join(f"<option value='{esc(u.email)}' {'selected' if u.email == email else ''}>{esc(u.name)}</option>" for u in users)
    res = tools.draft_offboarding_checklist(a, email)
    items = "".join(f"<tr><td>{c['step']}</td><td>&#9744; {esc(c['action'])}</td></tr>" for c in res.get("checklist", []))
    return (f"<div class=card><h2>Offboarding draft &middot; {esc(res.get('name', ''))}</h2>"
            f"<form><select name=email>{opts}</select><button>Draft checklist</button></form>"
            f"<div class='pill bad' style='margin-bottom:10px'>{esc(res.get('status', res.get('error')))}</div>"
            f"<table><tr><th>#</th><th>Step</th></tr>{items}</table></div>")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        url = urlparse(self.path)
        q = parse_qs(url.query)
        a = get_adapter()
        try:
            if url.path == "/":
                body = devices_view(a)
            elif url.path == "/access":
                body = access_view(a, q)
            elif url.path == "/groups":
                body = groups_view(a)
            elif url.path == "/offboarding":
                body = offboarding_view(a, q)
            elif url.path == "/api/noncompliant":
                return self._send(json.dumps(tools.list_noncompliant_devices(a), indent=2), "application/json")
            else:
                return self._send("Not found", "text/plain", 404)
        except ValueError as e:
            return self._send(f"Bad request: {e}", "text/plain", 400)
        self._send(page(url.path, body), "text/html; charset=utf-8")

    def _send(self, text: str, ctype: str, status: int = 200):
        data = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"IT Tools Viewer on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
