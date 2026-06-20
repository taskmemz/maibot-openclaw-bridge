# OpenClaw MCP Bridge

在 OpenClaw 机器上运行一个简单 MCP server，让 MaiBot 通过 HTTP 调用 OpenClaw Agent。

## 原理

用 `openclaw agent --message --json` CLI 执行任务，CLI 内部自己处理所有 Gateway 认证，插件完全不需要碰 Gateway 协议。

```
MaiBot (mcp_module)
  │  MCP streamable_http
  ▼
openclaw-mcp-server/server.py  (运行在 OpenClaw 机器上)
  │  subprocess: openclaw agent --message "..." --json
  ▼
OpenClaw Agent
```

## 安装（OpenClaw 做）

```bash
# 把 server.py 放到 OpenClaw 机器上
cd ~
wget https://raw.githubusercontent.com/taskmemz/maibot-openclaw-bridge/main/openclaw-mcp-server/server.py

# 启动（默认端口 18790）
python3 server.py
```

建议用 screen / systemd 保持后台运行。

## 配置（MaiBot 做）

```toml
[[mcp.servers]]
name = "openclaw"
enabled = true
transport = "streamable_http"
url = "http://你的OpenClaw地址:18790/message"
```

## 优点

- 不需要处理 Gateway WebSocket 协议
- 不需要设备认证（device auth）
- 不需要操心 scope/权限
- 零额外 Python 依赖（stdlib 即可）
- OpenClaw CLI 自己搞定一切认证
