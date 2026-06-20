# MaiBot ↔ OpenClaw Bridge

让 MaiBot 将复杂任务委托给远程 OpenClaw 智能体执行。

## 一句话让 OpenClaw 自助安装

告诉你的 OpenClaw：

> 读一下 https://github.com/taskmemz/maibot-openclaw-bridge 的 openclaw-skill/，然后按 INSTALL.md 完成安装

## MaiBot 配置

在 `bot_config.toml` 中添加：

```toml
[mcp]
enable = true

[[mcp.servers]]
name = "openclaw"
enabled = true
transport = "stdio"
command = "uv"
args = [
    "run", "--with", "websockets",
    "https://raw.githubusercontent.com/taskmemz/maibot-openclaw-bridge/main/mcp-server/server.py"
]
env = { OPENCLAW_GATEWAY_TOKEN = "你的密钥" }
```

或者用 WebUI **系统设置 → MCP → 服务器列表 → 添加服务器**：

| 字段 | 值 |
|---|---|
| 名称 | `openclaw` |
| 启用 | 开 |
| 传输方式 | `stdio` |
| 命令 | `uv` |
| 参数 | `["run", "--with", "websockets", "https://raw.githubusercontent.com/.../mcp-server/server.py"]` |
| 环境变量 | `OPENCLAW_GATEWAY_TOKEN=你的密钥` |

重启后日志显示 `✓ MCP 服务器 'openclaw' 已连接 (工具 4 / ...)` 即成功。

> `uv run` 会自动下载脚本和依赖，不需要手动下载 `server.py` 或安装 `websockets`。如果 MaiBot 没用 uv，也可以用 `python` + `pip install websockets` 的方式，`command = "python"` + `args = ["下载好的server.py路径"]`。

## 架构

```
MaiBot (mcp_module)
  │  MCP stdio
  ▼
uv run server.py         ← uv 自动管理依赖和脚本
  │  WebSocket (Gateway 协议 v4)
  ▼
OpenClaw Gateway
  │  sessions.create → sessions.send → agent.wait
  ▼
OpenClaw Agent           ← 被 openclaw-skill/SKILL.md 引导
```

## 技能清单

| MCP 工具 | 用途 |
|---|---|
| `openclaw_investigate` | 错误根因分析 |
| `openclaw_ceo_review` | 计划审查 |
| `openclaw_office_hours` | 产品想法评估 |
| `openclaw_retro` | 工程回顾 |

## 目录结构

```
maibot-openclaw-bridge/
├── README.md
├── pyproject.toml              # Python 包配置
├── src/maibot_openclaw_bridge/
│   ├── __init__.py
│   └── __main__.py             # MCP server 核心逻辑
├── mcp-server/
│   └── server.py               # 向后兼容入口
├── maiot-plugin/               # 备选：MaiBot 插件方式
└── openclaw-skill/
    ├── SKILL.md                # → OpenClaw 技能目录
    └── INSTALL.md              # OpenClaw 安装说明
```
