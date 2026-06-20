# MaiBot ↔ OpenClaw Bridge

让 MaiBot 的推理引擎 Maisaka 将复杂任务委托给远程 OpenClaw 智能体执行。

## 一句话让 OpenClaw 自助安装

告诉你的 OpenClaw：

> 读一下 https://github.com/taskmemz/maibot-openclaw-bridge 的 openclaw-skill/，然后按 INSTALL.md 完成安装

OpenClaw 会自动完成它那边需要做的 3 件事：确认 Gateway 可用、准备 token、安装 skill。

MaiBot 侧的配置需要你手动完成，见下方。

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
