"""OpenClaw MCP Bridge — runs on the OpenClaw machine.

Calls 'openclaw agent --message' CLI (auth handled by CLI).
MaiBot connects via streamable_http transport.

No Gateway protocol, no device auth, no scope stuff.

Usage:
    python3 server.py

Dependencies: none (stdlib only + openclaw CLI)
"""

import json
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

MCP_PROTOCOL = "2025-03-26"
HOST = "0.0.0.0"
PORT = 18790


TOOLS = [
    {
        "name": "openclaw_task",
        "description": "Send a complex task to OpenClaw for processing",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_description": {"type": "string", "description": "What you need OpenClaw to do"},
            },
            "required": ["task_description"],
        },
    },
]


def run_agent(task: str) -> dict:
    try:
        r = subprocess.run(
            ["openclaw", "agent", "--agent", "main", "--message", task, "--json"],
            capture_output=True, text=True, timeout=600,
        )
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "agent timeout"}
    except FileNotFoundError:
        return {"success": False, "error": "openclaw CLI not found"}

    if r.returncode != 0:
        return {"success": False, "error": r.stderr[:500] or f"exit {r.returncode}"}

    try:
        data = json.loads(r.stdout)
        texts = [p.get("text", "") for p in data.get("payloads", []) if p.get("text")]
        return {"success": True, "response": "\n".join(texts)}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"bad JSON: {e}"}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        resp = self._handle(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(resp, ensure_ascii=False).encode())

    def _handle(self, body: dict) -> dict:
        mid = body.get("id")
        method = body.get("method", "")
        params = body.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0", "id": mid,
                "result": {
                    "protocolVersion": MCP_PROTOCOL,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "openclaw-bridge", "version": "1.0.0"},
                },
            }
        elif method in ("notifications/initialized",):
            return {"jsonrpc": "2.0", "id": mid, "result": {}}
        elif method == "tools/list":
            return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {})
            if name != "openclaw_task":
                return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"unknown tool: {name}"}}
            task = args.get("task_description", "")
            result = run_agent(task)
            if result["success"]:
                return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": result["response"]}]}}
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": f"error: {result['error']}"}], "isError": True}}
        return {"jsonrpc": "2.0", "id": mid, "result": {}}

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[MCP] {args[0]} {args[1]} {args[2]}\n")


def main():
    server = HTTPServer((HOST, PORT), Handler)
    print(f"OpenClaw MCP bridge running on http://{HOST}:{PORT}/message", flush=True)
    print(f"Agent: main | Timeout: 600s | Dependencies: none (stdlib only)", flush=True)
    print(f"MaiBot config:", flush=True)
    print(f"  [[mcp.servers]]", flush=True)
    print(f'  name = "openclaw"', flush=True)
    print(f"  enabled = true", flush=True)
    print(f'  transport = "streamable_http"', flush=True)
    print(f'  url = "http://<this_ip>:{PORT}/message"', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...", flush=True)
        server.server_close()


if __name__ == "__main__":
    main()
