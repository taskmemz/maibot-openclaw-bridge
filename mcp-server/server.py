"""MCP server: bridges MaiBot <-> OpenClaw Gateway.

Usage:
    python server.py [--gateway ws://host:port] (--token TOKEN | --password PASSWORD)

Configure in MaiBot's bot_config.toml:
    [[mcp.servers]]
    name = "openclaw"
    enabled = true
    transport = "stdio"
    command = "python"
    args = ["path/to/server.py"]
    env = { OPENCLAW_GATEWAY_TOKEN = "xxx" }

    # 如果 Gateway 是 password 模式，用 PASSWORD 环境变量:
    env = { OPENCLAW_GATEWAY_PASSWORD = "xxx" }
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from typing import Any

MCP_PROTOCOL_VERSION = "2025-03-26"


async def connect_gateway(url: str, secret: str, use_password: bool = False) -> Any:
    import websockets

    ws = await asyncio.wait_for(websockets.connect(url, ping_interval=30), timeout=15)
    challenge_raw = await asyncio.wait_for(ws.recv(), timeout=10)
    challenge = json.loads(challenge_raw)

    auth: dict[str, str] = {}
    if use_password:
        auth["password"] = secret
    else:
        auth["token"] = secret

    connect_req = {
        "type": "req",
        "id": "c1",
        "method": "connect",
        "params": {
            "minProtocol": 4,
            "maxProtocol": 4,
            "client": {
                "id": "maibot-mcp-bridge",
                "version": "1.0.0",
                "platform": "node",
                "mode": "operator",
            },
            "role": "operator",
            "scopes": ["operator.read", "operator.write"],
            "auth": auth,
        },
    }
    await ws.send(json.dumps(connect_req))
    resp_raw = await asyncio.wait_for(ws.recv(), timeout=10)
    resp = json.loads(resp_raw)
    if not resp.get("ok"):
        raise RuntimeError(f"Gateway auth failed: {resp}")
    return ws


def req_id() -> str:
    return uuid.uuid4().hex[:12]


async def gateway_call(ws: Any, method: str, params: dict[str, Any], timeout: float = 30) -> dict:
    req = {"type": "req", "id": req_id(), "method": method, "params": params}
    await ws.send(json.dumps(req))
    raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
    return json.loads(raw)


SKILL_PROMPTS: dict[str, str] = {
    "investigate": (
        "你是一个系统调试专家。请根据以下信息进行根因分析，"
        "输出包含：症状描述、根因分析、修复建议、复现步骤、相关注意事项。"
    ),
    "ceo_review": (
        "你是一个 CEO 级规划审查专家。请根据以下计划进行审查，"
        "输出包含：架构评估、错误处理映射、安全威胁模型、"
        "数据流与边界情况、性能与可观测性、部署与回滚策略、测试覆盖评估。"
    ),
    "office_hours": (
        "你是一个 YC 创业导师。请根据以下产品想法进行评估，"
        "输出包含：问题理解、需求真实性验证、目标用户画像、"
        "竞品分析、最小可行方案建议、潜在风险、下一步行动。"
    ),
    "retro": (
        "你是一个工程回顾专家。请根据以下工作数据进行分析，"
        "输出包含：工作总结、做得好的方面、需要改进的方面、行动项与优先级。"
    ),
}


async def execute_task(gateway_url: str, secret: str, skill: str, params: dict[str, str], timeout_s: int, use_password: bool = False) -> dict:
    prompt = SKILL_PROMPTS.get(skill, "")
    param_lines = "\n".join(f"{k}: {v}" for k, v in params.items() if v)
    task_msg = f"{prompt}\n\n## 输入数据\n\n{param_lines}"

    ws = None
    try:
        ws = await connect_gateway(gateway_url, secret, use_password)

        sess = await gateway_call(ws, "sessions.create", {
            "title": f"maibot-{skill}-{uuid.uuid4().hex[:8]}",
        })
        if not sess.get("ok"):
            return {"success": False, "error": f"session create failed: {sess}"}
        session_key = sess["payload"]["key"]

        send = await gateway_call(ws, "sessions.send", {
            "key": session_key, "message": task_msg, "deliver": False,
        })
        if not send.get("ok"):
            return {"success": False, "error": f"send failed: {send}"}
        run_id = send["payload"].get("runId", "")

        wait_params: dict[str, Any] = {
            "sessionKey": session_key,
            "timeoutMs": timeout_s * 1000,
        }
        if run_id:
            wait_params["runId"] = run_id

        wait_req = {"type": "req", "id": req_id(), "method": "agent.wait", "params": wait_params}
        await ws.send(json.dumps(wait_req))

        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=timeout_s + 10)
            msg = json.loads(raw)
            if msg.get("type") == "res" and msg.get("id") == wait_req["id"]:
                if not msg.get("ok"):
                    return {"success": False, "error": f"task failed: {msg}"}

                payload = msg.get("payload", {})

                response_text = (
                    payload.get("response")
                    or payload.get("text")
                    or payload.get("content")
                    or str(payload)
                )

                return {"success": True, "skill": skill, "response": response_text}

    except asyncio.TimeoutError:
        return {"success": False, "error": "gateway timeout"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
    finally:
        if ws:
            try:
                await ws.close()
            except Exception:
                pass


TOOL_DEFS: list[dict] = [
    {
        "name": "openclaw_investigate",
        "description": "发送错误信息到 OpenClaw 进行根因分析",
        "inputSchema": {
            "type": "object",
            "properties": {
                "error_description": {"type": "string", "description": "错误描述，用一句话概括问题"},
                "stack_trace": {"type": "string", "description": "错误栈追踪或完整错误日志"},
                "reproduction_steps": {"type": "string", "description": "复现步骤"},
                "additional_context": {"type": "string", "description": "额外上下文，如环境版本、最近改动"},
            },
            "required": ["error_description"],
        },
    },
    {
        "name": "openclaw_ceo_review",
        "description": "发送计划到 OpenClaw 进行 CEO 级审查",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plan_title": {"type": "string", "description": "计划标题"},
                "plan_content": {"type": "string", "description": "计划内容，包括背景、方案、技术选型"},
                "review_focus": {"type": "string", "description": "审查重点，如架构、安全、性能"},
            },
            "required": ["plan_title", "plan_content"],
        },
    },
    {
        "name": "openclaw_office_hours",
        "description": "发送产品想法到 OpenClaw 进行 YC 式评估",
        "inputSchema": {
            "type": "object",
            "properties": {
                "idea_title": {"type": "string", "description": "想法标题"},
                "idea_description": {"type": "string", "description": "想法详细描述"},
                "target_users": {"type": "string", "description": "目标用户群体"},
                "existing_solutions": {"type": "string", "description": "现有替代方案或竞品"},
            },
            "required": ["idea_title", "idea_description"],
        },
    },
    {
        "name": "openclaw_retro",
        "description": "发送工作数据到 OpenClaw 进行工程回顾",
        "inputSchema": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "回顾周期"},
                "work_summary": {"type": "string", "description": "工作总结，完成的功能、修复的 Bug"},
                "metrics": {"type": "string", "description": "量化指标，提交数、PR 数等"},
                "highlights": {"type": "string", "description": "亮点或特别事项"},
            },
            "required": ["period", "work_summary"],
        },
    },
]

SKILL_MAP: dict[str, int] = {t["name"]: i for i, t in enumerate(TOOL_DEFS)}


async def main() -> None:
    gateway_url = "ws://127.0.0.1:18789"
    secret = ""
    use_password = False
    timeout_s = 300

    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--gateway" and i + 1 < len(sys.argv):
            gateway_url = sys.argv[i + 1]
            i += 2
        elif a == "--token" and i + 1 < len(sys.argv):
            secret = sys.argv[i + 1]
            i += 2
        elif a == "--password" and i + 1 < len(sys.argv):
            secret = sys.argv[i + 1]
            use_password = True
            i += 2
        elif a == "--timeout" and i + 1 < len(sys.argv):
            timeout_s = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    if not secret:
        secret = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")
    if not secret:
        secret = os.environ.get("OPENCLAW_GATEWAY_PASSWORD", "")
        if secret:
            use_password = True

    stdin_reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(stdin_reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    async def write(msg: dict) -> None:
        line = json.dumps(msg, ensure_ascii=False)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

    init_raw = await stdin_reader.readline()
    init_msg = json.loads(init_raw)

    await write({
        "jsonrpc": "2.0",
        "id": init_msg.get("id"),
        "result": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "maibot-openclaw-bridge", "version": "1.0.0"},
        },
    })

    await stdin_reader.readline()

    while True:
        line = await stdin_reader.readline()
        if not line:
            break
        msg = json.loads(line)
        msg_id = msg.get("id")
        if msg_id is None:
            continue
        method = msg.get("method", "")
        params = msg.get("params", {})

        if method == "tools/list":
            await write({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOL_DEFS}})

        elif method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {})

            if name not in SKILL_MAP:
                await write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "error": {"code": -32602, "message": f"Unknown tool: {name}"},
                })
                continue

            secret = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "") or os.environ.get("OPENCLAW_GATEWAY_PASSWORD", "")
            skill_key = name.replace("openclaw_", "")
            result = await execute_task(gateway_url, secret, skill_key, args, timeout_s, use_password)

            if result["success"]:
                await write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": result["response"]}]},
                })
            else:
                await write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"错误: {result['error']}"}],
                        "isError": True,
                    },
                })

        else:
            pass


if __name__ == "__main__":
    asyncio.run(main())
