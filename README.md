# MaiBot ↔ OpenClaw Bridge

让 MaiBot 将复杂任务委托给远程 OpenClaw 智能体执行。

## 一句话让 OpenClaw 自助安装

告诉你的 OpenClaw：

> 读一下 https://github.com/taskmemz/maibot-openclaw-bridge 的 openclaw-skill/，然后按 INSTALL.md 完成安装

## MaiBot 安装（插件方式）

插件已独立为 [taskmemz/openclaw-skills-plugin](https://github.com/taskmemz/openclaw-skills-plugin)。在 MaiBot 上部署：

```bash
git clone --filter=blob:none --sparse https://github.com/taskmemz/openclaw-skills-plugin.git /MaiMBot/plugins/openclaw-skills
cd /MaiMBot/plugins/openclaw-skills && rm -rf .git
uv pip install websockets
```

然后在 WebUI 中配置：

**系统设置 → 插件 → openclaw-skills → 配置**：

| 字段 | 值 |
|---|---|
| 网关地址 | `ws://你的OpenClaw地址:18789` |
| 认证令牌 | 你的 OpenClaw gateway 密钥 |
| 任务超时 | `300` |

或修改插件配置页的 `config.toml`：

```toml
[gateway]
url = "ws://你的OpenClaw地址:18789"
token = "你的OpenClaw密钥"
timeout_seconds = 300

[skills]
investigate_enabled = true
ceo_review_enabled = true
office_hours_enabled = true
retro_enabled = true
```

重启后插件自动加载。

## 架构

```
MaiBot (plugin_runtime)
  │  @Tool 组件 (openclaw_investigate/ceo_review/...)
  ▼
plugin.py
  │  WebSocket (Gateway 协议 v4)
  ▼
OpenClaw Gateway
  │  sessions.create → sessions.send → agent.wait
  ▼
OpenClaw Agent     ← 被 openclaw-skill/SKILL.md 引导
```

## 技能清单

| 插件 Tool | 用途 |
|---|---|
| `openclaw_investigate` | 错误根因分析 |
| `openclaw_ceo_review` | 计划审查 |
| `openclaw_office_hours` | 产品想法评估 |
| `openclaw_retro` | 工程回顾 |

## 目录结构

```
maibot-openclaw-bridge/
├── README.md
├── maibot-plugin/ → https://github.com/taskmemz/openclaw-skills-plugin.git
├── mcp-server/                    # 备选：MCP server 方式
└── openclaw-skill/                # OpenClaw 侧文件
    ├── SKILL.md                   # → OpenClaw 技能目录
    └── INSTALL.md                 # OpenClaw 安装说明
```
