# MaiBot ↔ OpenClaw Bridge

让 MaiBot 把复杂任务丢给 OpenClaw 处理。

## 最佳方案：OpenClaw MCP Bridge（零认证问题）

在 OpenClaw 机器上跑一个简单 HTTP server，用 `openclaw agent` CLI 执行任务，CLI 自己处理认证。

**OpenClaw 做：**

```bash
wget https://raw.githubusercontent.com/taskmemz/maibot-openclaw-bridge/main/openclaw-mcp-server/server.py
python3 server.py
```

**MaiBot 做：**

```toml
[[mcp.servers]]
name = "openclaw"
enabled = true
transport = "streamable_http"
url = "http://你的OpenClaw地址:18790/message"
```

不需要处理 Gateway 协议、设备认证、scope 权限——全部绕过。

## 备选：MaiBot 插件

网关协议认证复杂且需要设备密钥，不推荐。详见 [taskmemz/openclaw-skills-plugin](https://github.com/taskmemz/openclaw-skills-plugin)。

## 结构

```
maibot-openclaw-bridge/
├── README.md
├── openclaw-mcp-server/          # [推荐] 最简方案
│   ├── server.py                 #   零依赖 HTTP MCP server
│   └── README.md                 #   使用说明
├── maibot-plugin/ → openclaw-skills-plugin  # [备选] 插件方式
├── mcp-server/                   # [归档] MCP server 桥接
└── openclaw-skill/               # OpenClaw 侧技能
```
