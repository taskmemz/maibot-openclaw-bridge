# MCP Bridge Server

推荐用 `uv run` 执行，不需要手动管理文件：

```toml
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

`uv run` 会自动从 GitHub 下载脚本并安装依赖。没有 uv 的话：

```bash
pip install websockets
python server.py
```
