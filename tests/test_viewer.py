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
