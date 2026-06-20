# MaiBot Bridge — OpenClaw 安装说明

你需要完成以下三件事：

### 1. 确认 Gateway 可用

确保你的 Gateway 正在运行，MaiBot 需要通过 WebSocket 连接到你。记下 Gateway 的地址（默认 `ws://127.0.0.1:18789`）。

### 2. 准备好认证 token

MaiBot 连接你的 Gateway 时需要 token。如果你还没设置，配置一个。

### 3. 安装本技能

将本仓库中 `openclaw-skill/SKILL.md` 的内容安装为你的技能：

- 放入你的 skills 目录（通常是 `~/.openclaw/workspace/skills/maibot/SKILL.md`）
- 或者通过你的技能管理机制安装
- 然后重载配置使技能生效

---
告诉用户token，方便用户配置
安装完成后，当 MaiBot 通过 MCP 调用你时，你会收到任务消息，按 SKILL.md 中的说明处理即可。MaiBot 那边的部署由 MaiBot 自己负责。
