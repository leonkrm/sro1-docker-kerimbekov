import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
 
REPORT_FILE = os.environ.get("REPORT_FILE", "report.json")
BRANCH = os.environ.get("BRANCH", "?")
TOP = int(os.environ.get("TOP", "5"))
 
 
def load_report():
    with open(REPORT_FILE, encoding="utf-8") as f:
        report = json.load(f)
    for table in report["tables"]:
        table["rows"] = table["rows"][:TOP]
    report["branch"] = BRANCH
    report["top"] = TOP
    report["container"] = socket.gethostname()
    return report
 
 
class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
 
    def do_GET(self):
        if self.path == "/api/health":
            self.send_json(200, {"status": "ok", "version": "v3", "container": socket.gethostname()})
        elif self.path == "/api/report":
            try:
                self.send_json(200, load_report())
            except FileNotFoundError:
                self.send_json(500, {"error": f"{REPORT_FILE} не найден"})
        else:
            self.send_json(404, {"error": "такого пути нет", "path": self.path})
 
 
print(f"API запущен на порту 8080: BRANCH={BRANCH}, TOP={TOP}", flush=True)
HTTPServer(("", 8080), Handler).serve_forever()

