import threading
import urllib.request
from http.server import ThreadingHTTPServer

from mcp_it_tools.viewer import Handler


def test_viewer_pages():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        for path, text in [("/", "non-compliant"), ("/access?app=CRM&days=30", "katherine"),
                           ("/groups", "prod-db-readers"), ("/offboarding", "DRAFT")]:
            body = urllib.request.urlopen(base + path).read().decode()
            assert text in body, path
    finally:
        srv.shutdown()


def test_viewer_access_query_params():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        # app and days arrive as separate parameters; lower-case app still matches
        body = urllib.request.urlopen(base + "/access?app=cloudconsole&days=60").read().decode()
        assert "Who has CloudConsole but has not signed in for 60+ days" in body
        assert "<option selected>CloudConsole</option>" in body
        assert "alan.turing@example.com" in body and "pill bad'>inactive" in body
        # an unknown app (e.g. a mis-encoded URL) says so instead of an empty table
        body = urllib.request.urlopen(base + "/access?app=CloudConsole%26days%3D60").read().decode()
        assert "Unknown app" in body
        assert "<td>" in body  # falls back to a real app's rows
    finally:
        srv.shutdown()
