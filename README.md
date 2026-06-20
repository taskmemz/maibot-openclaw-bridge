# MaiBot ↔ OpenClaw Bridge

让 MaiBot 的推理引擎 Maisaka 将复杂任务委托给远程 OpenClaw 智能体执行。

## 架构

### MCP Server 桥接（推荐）

```
MaiBot (mcp_module)
  │  MCP stdio (JSON-RPC 2.0)
  ▼  MaiBot 原生支持，零额外依赖
mcp-server/server.py
  │  WebSocket (OpenClaw Gateway 协议 v4)
  ▼
OpenClaw Gateway (远程)
  │  sessions.create → sessions.send → agent.wait
  ▼
OpenClaw Agent         ← 被 openclaw-skill/SKILL.md 引导
```

MCP 工具通过 `MCPToolProvider` 注册到 MaiBot 的统一 `ToolRegistry`，Maisaka 规划器调用 MCP 工具与调用内置工具（`reply`、`wait`、`finish`）完全一致，无需区分来源。

### MaiBot 插件桥接（备选）

```
MaiBot (plugin_runtime)
  │  @Tool 组件
  ▼
maiot-plugin/plugin.py  ← plugins/ 目录安装
  │  WebSocket
  ▼
OpenClaw Gateway (远程)
```

## 快速开始

### 前提条件

- OpenClaw Gateway 运行中且可通过 WebSocket 访问（默认端口 `18789`）
- OpenClaw 的 auth token
- `pip install websockets`

### 步骤

**1. 安装 OpenClaw Skill**

```bash
cp openclaw-skill/SKILL.md ~/.openclaw/workspace/skills/maibot/SKILL.md
openclaw gateway reload
```

告诉 OpenClaw 如何与 MaiBot 协作处理任务。

**2. 配置 MCP Server（推荐）**

在 MaiBot 的 `bot_config.toml` 中添加：

```toml
[mcp]
enable = true

[[mcp.servers]]
name = "openclaw"
enabled = true
transport = "stdio"
command = "python"
args = [
    "/绝对路径/maibot-openclaw-bridge/mcp-server/server.py",
    "--gateway", "ws://你的OpenClaw地址:18789",
    "--timeout", "300",
]
env = { OPENCLAW_GATEWAY_TOKEN = "你的Gateway令牌" }
```

> 参数通过 `env` 环境变量传入，避免 token 出现在进程列表或日志中。
> 如 OpenClaw 与 MaiBot 同机，`--gateway` 可省略（默认 `ws://127.0.0.1:18789`）。

**备选：使用插件方式**

将 `maiot-plugin/` 整体复制为 MaiBot 的 `plugins/openclaw-skills/`，重启后在 WebUI 插件配置页填写 Gateway 地址和 token。

**3. 重启 MaiBot**

启动日志中应看到：

```
✓ MCP 服务器 'openclaw' 已连接 (工具 4 / Prompt 0 / 资源 0 / 模板 0)
```

## 技能清单

连接后 MaiBot 获得 4 个 MCP 工具（或 4 个插件 Tool），统一由 Maisaka 规划器调度：

| 工具 | 技能 | 用途 |
|---|---|---|
| `openclaw_investigate` | 调试分析 | 传入错误栈/复现步骤，OpenClaw 进行根因分析 |
| `openclaw_ceo_review` | 规划审查 | 传入计划/方案，OpenClaw 进行 CEO 级审查 |
| `openclaw_office_hours` | 头脑风暴 | 传入产品想法，OpenClaw 进行 YC 式评估 |
| `openclaw_retro` | 工程回顾 | 传入工作数据，OpenClaw 进行回顾分析 |

## 目录结构

```
maibot-openclaw-bridge/
├── README.md                        # 本文档
├── mcp-server/                      # [推荐] MCP Server 桥接
│   ├── server.py                    #   MCP stdio 服务端
│   └── README.md                    #   配置说明
├── maiot-plugin/                    # [备选] MaiBot 插件桥接
│   ├── _manifest.json               #   插件清单
│   ├── plugin.py                    #   插件入口
│   ├── config.toml                  #   配置模版
│   └── .gitignore
└── openclaw-skill/                  # OpenClaw 侧文件
    ├── SKILL.md                     #   → ~/.openclaw/workspace/skills/maibot/
    └── INSTALL.md                   #   OpenClaw 自助安装指南（步骤式）
```

## 配置参考

### MCP Server 命令行参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--gateway` | `ws://127.0.0.1:18789` | OpenClaw Gateway WebSocket 地址 |
| `--token` | `OPENCLAW_GATEWAY_TOKEN` 环境变量 | 认证令牌 |
| `--timeout` | `300` | 单次任务超时秒数 |

### bot_config.toml 配置字段

| 字段 | 说明 |
|---|---|
| `[mcp].enable` | MCP 总开关 |
| `[[mcp.servers]].name` | 服务器名称，不可重复 |
| `enabled` | 是否启用此服务 |
| `transport` | `"stdio"` — 本地子进程模式 |
| `command` | `"python"` |
| `args` | `server.py` 路径 + 参数 |
| `env` | 环境变量，用于传入敏感信息 |
| `http_timeout_seconds` | HTTP 请求超时，默认 30s |
| `read_timeout_seconds` | 会话读取超时，默认 300s |
