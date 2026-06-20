# MCP Server — 推荐方式

零依赖（标准库）MCP stdio 服务器。MaiBot 通过原生 MCP 协议调用此服务器，服务器将请求转发给远程 OpenClaw Gateway 执行。

```
MaiBot (mcp_module)
  │  MCP stdio (JSON-RPC 2.0 over stdin/stdout)
  ▼
server.py
  │  WebSocket (OpenClaw Gateway 协议 v4)
  ▼
OpenClaw Gateway (远程)
  │  sessions.create → sessions.send → agent.wait
  ▼
OpenClaw Agent
```

## 依赖

```bash
pip install websockets
```

MaiBot 侧不需要额外依赖，MaiBot 内置 `mcp_module` 原生支持 MCP stdio 协议。

## 用法

```bash
# 连接本地 Gateway
python server.py --token 你的Gateway令牌

# 指定远程 Gateway
python server.py --gateway ws://192.168.1.100:18789 --token 你的令牌

# 通过环境变量传 token
export OPENCLAW_GATEWAY_TOKEN=你的令牌
python server.py
```

## 在 MaiBot 中配置

在 `bot_config.toml` 的 `[mcp]` 段添加服务器配置：

```toml
[mcp]
enable = true

[[mcp.servers]]
name = "openclaw"
enabled = true
transport = "stdio"
command = "python"
args = [
    "/path/to/maibot-openclaw-bridge/mcp-server/server.py",
    "--gateway", "ws://你的OpenClaw地址:18789",
    "--timeout", "300",
]
env = { OPENCLAW_GATEWAY_TOKEN = "你的Gateway令牌" }
```

配置字段说明（与 MaiBot MCP 配置文档一致）：

| 字段 | 说明 |
|---|---|
| `name` | 服务器名称，在同一配置中不可重复 |
| `enabled` | 是否启用 |
| `transport` | `"stdio"` — 本地子进程通信 |
| `command` | 启动命令，`"python"` |
| `args` | 传给 server.py 的参数 |
| `env` | 环境变量，用于传入 `OPENCLAW_GATEWAY_TOKEN` |

## 验证

重启 MaiBot，启动日志中应看到：

```
✓ MCP 服务器 'openclaw' 已连接 (工具 4 / Prompt 0 / 资源 0 / 模板 0)
```

如果连接失败，会输出：

```
⚠️ MCP 服务器 'openclaw' 连接失败: ...
```

连接成功后，MaiBot 的 `openclaw_*` 工具会自动注册到 Maisaka 的工具注册表，与内置工具（`reply`、`wait`、`finish` 等）一样由规划器决策调用。

## 工具清单

连接后 MaiBot 可获得以下 4 个 MCP 工具：

| MCP 工具 | 功能 |
|---|---|
| `openclaw_investigate` | 错误根因分析 |
| `openclaw_ceo_review` | 规划审查 |
| `openclaw_office_hours` | 产品想法评估 |
| `openclaw_retro` | 工程回顾 |

## 命令行参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--gateway` | `ws://127.0.0.1:18789` | OpenClaw Gateway WebSocket 地址 |
| `--token` | `OPENCLAW_GATEWAY_TOKEN` 环境变量 | 认证令牌 |
| `--timeout` | `300` | 任务超时秒数 |
