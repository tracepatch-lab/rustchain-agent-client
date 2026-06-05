import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from rustchain_agent import AgentClient, AgentHttpError


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/agent/jobs?") or self.path == "/agent/jobs":
            self._send(200, {"ok": True, "jobs": [], "total": 0})
        elif self.path == "/agent/stats":
            self._send(200, {"ok": True, "stats": {"open_jobs": 0}})
        else:
            self._send(404, {"error": "missing"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if self.path == "/agent/jobs":
            self._send(200, {"ok": True, "job": {"title": payload["title"], "reward_rtc": payload["reward_rtc"]}})
        else:
            self._send(400, {"error": "bad request"})

    def log_message(self, *_):
        return


class ClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)

    def test_list_jobs(self):
        client = AgentClient(self.base_url)
        self.assertEqual(client.list_jobs()["total"], 0)

    def test_post_job(self):
        client = AgentClient(self.base_url)
        body = client.post_job("wallet", "Title", "Desc", "code", 1.5)
        self.assertEqual(body["job"]["title"], "Title")
        self.assertEqual(body["job"]["reward_rtc"], 1.5)

    def test_http_error_keeps_status_and_body(self):
        client = AgentClient(self.base_url)
        with self.assertRaises(AgentHttpError) as ctx:
            client.get_job("nope")
        self.assertEqual(ctx.exception.status, 404)
        self.assertEqual(ctx.exception.body["error"], "missing")


if __name__ == "__main__":
    unittest.main()
