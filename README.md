# MaiBot ↔ OpenClaw Bridge

让 MaiBot 的推理引擎 Maisaka 将复杂任务委托给远程 OpenClaw 智能体执行。

## 一句话让 OpenClaw 自助安装

告诉你的 OpenClaw：

> 读一下 https://github.com/taskmemz/maibot-openclaw-bridge 的 openclaw-skill/，然后按 INSTALL.md 完成安装

OpenClaw 会自动完成它那边需要做的 3 件事：确认 Gateway 可用、准备 token、安装 skill。

MaiBot 侧的配置需要你手动完成。

## MaiBot 配置

在 MaiBot 的 `bot_config.toml` 中添加：

```toml
[mcp]
enable = true

[[mcp.servers]]
name = "openclaw"
enabled = true
transport = "stdio"
command = "python"
args = ["你放server.py的路径/server.py"]
env = { OPENCLAW_GATEWAY_PASSWORD = "你的OpenClaw密码" }

# 如果 OpenClaw 是 token 模式，用这个:
# env = { OPENCLAW_GATEWAY_TOKEN = "你的OpenClaw token" }
```

或者在 MaiBot WebUI 中配置：**系统设置 → MCP → 服务器列表 → 添加服务器**，填入：

| 字段 | 值 |
|---|---|
| 名称 | `openclaw` |
| 启用 | 开 |
| 传输方式 | `stdio` |
| 命令 | `python` |
| 参数 | `["你放server.py的路径/server.py"]` |
| 环境变量 | `OPENCLAW_GATEWAY_PASSWORD=你的密码`（token 模式用 `OPENCLAW_GATEWAY_TOKEN`） |

然后重启 MaiBot，日志中看到以下内容就说明连上了：

```
✓ MCP 服务器 'openclaw' 已连接 (工具 4 / Prompt 0 / 资源 0 / 模板 0)
```

| 如果你 | 用这个 |
|---|---|
| 不知道 server.py 放哪 | 找一个你喜欢的位置，把 `mcp-server/server.py` 放进去就行 |
| 不知道 token 是什么 | 问你的 OpenClaw，它已经按 INSTALL.md 准备好了 |
| OpenClaw 是 password 模式 | 用 `OPENCLAW_GATEWAY_PASSWORD` 代替 `OPENCLAW_GATEWAY_TOKEN` |
| OpenClaw 不在本机 | 在 `args` 里加 `"--gateway", "ws://OpenClaw地址:18789"` |

不想用 MCP 的话，也可以把 `maiot-plugin/` 整个复制到 MaiBot 的 `plugins/` 目录下，然后在 WebUI 里配 Gateway 地址和 token。

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

## 技能清单

MaiBot 连接后可获得以下工具：

| 工具 | 用途 |
|---|---|
| `openclaw_investigate` | 传入错误栈/复现步骤，OpenClaw 进行根因分析 |
| `openclaw_ceo_review` | 传入计划/方案，OpenClaw 进行 CEO 级审查 |
| `openclaw_office_hours` | 传入产品想法，OpenClaw 进行 YC 式评估 |
| `openclaw_retro` | 传入工作数据，OpenClaw 进行回顾分析 |

## 目录结构

```
maibot-openclaw-bridge/
├── README.md
├── mcp-server/
│   ├── server.py
│   └── README.md
├── maiot-plugin/
│   ├── _manifest.json
│   ├── plugin.py
│   ├── config.toml
│   └── .gitignore
└── openclaw-skill/
    ├── SKILL.md
    └── INSTALL.md
```
