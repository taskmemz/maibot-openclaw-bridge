# MaiBot Bridge — OpenClaw 安装说明

你需要做以下三件事：

1. 确保你的 Gateway 在运行中，MaiBot 需要通过 WebSocket 连过来
2. 准备一个认证 token，MaiBot 连接时需要带上
3. 将本仓库中的 `openclaw-skill/SKILL.md` 安装为你的技能

完成这些后，当 MaiBot 通过 MCP 调用你时，你会收到以下类型的任务：

| 工具 | 你会收到 | 你需要做的 |
|---|---|---|
| `openclaw_investigate` | 错误描述、栈追踪等 | 根因分析，输出结构化结果 |
| `openclaw_ceo_review` | 计划内容 | 全面审查，输出评估 |
| `openclaw_office_hours` | 产品想法 | YC 式评估 |
| `openclaw_retro` | 工作数据 | 回顾分析 |

处理完返回结构化 Markdown 结果即可。MaiBot 那边的部署由 MaiBot 自己负责。
