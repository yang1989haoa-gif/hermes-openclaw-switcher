# OpenClaw Switcher for Hermes Agent

> 🔀 一键切换 Hermes ↔ OpenClaw 模式的 Gateway 插件

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-v0.12+-green.svg)](https://github.com/NousResearch/hermes-agent)

---

## 🎯 这是什么？

你同时跑了 **Hermes Agent** 和 **OpenClaw** 两个 AI 后端，但每次想切换都要改配置、重启服务？

这个插件让你 **在聊天里发一条命令就切换**，不用碰配置文件，不用重启。

---

## 💡 使用场景

| 场景 | 说明 |
|:-----|:-----|
| **Hermes 做日常助手** | 股票分析、文件管理、自动化任务 → 用 Hermes |
| **OpenClaw 做专项任务** | 需要 OpenClaw 特有的 agent 能力时 → 一键切过去 |
| **对比两个模型** | 同一个问题，分别用两个后端回答，对比效果 |
| **团队协作** | 不同成员用不同后端，按需切换 |
| **开发测试** | 开发插件时快速切换到 OpenClaw 测试 |

---

## ✨ 核心功能

- **`/openclaw`** — 一条命令，后续所有消息走 OpenClaw
- **`/hermes`** — 一条命令，切回 Hermes
- **`/status`** — 随时查看当前在用哪个后端
- **状态持久化** — 重启不丢失，切换一次一直生效
- **零配置安装** — 复制插件 → 填 API Key → 重启，三步搞定

---

## 📱 支持平台

QQ、微信、Telegram、Discord、Slack、WhatsApp 等所有 Hermes Gateway 支持的平台。

---

## 🚀 快速开始（3 步）

### 第 1 步：安装插件

```bash
git clone https://github.com/yang1989haoa-gif/hermes-openclaw-switcher.git
cp -r hermes-openclaw-switcher/plugin ~/.hermes/plugins/openclaw-switcher
```

### 第 2 步：配置 API Key

编辑 `~/.hermes/config.yaml`：

```yaml
plugins:
  openclaw-switcher:
    enabled: true
    openclaw_base_url: "http://localhost:18789"
    openclaw_api_key: "your-openclaw-api-key"
    openclaw_model: "openclaw/bot2-agent"
```

或用环境变量（推荐，更安全）：

```bash
echo "OPENCLAW_API_KEY=your-key" >> ~/.hermes/.env
```

### 第 3 步：重启

```bash
hermes gateway restart
```

---

## 💬 实际效果

```
你: /oc
Bot: ✅ OpenClaw 模式已开启。后续消息将由 OpenClaw 处理。

你: 帮我分析一下最近的市场趋势
Bot: (OpenClaw 的回复)

你: /back
Bot: ✅ Hermes 模式已恢复。

你: 查一下我的持仓
Bot: (Hermes 的回复)
```

---

## 📋 命令速查

| 命令 | 别名 | 作用 |
|:-----|:-----|:-----|
| `/openclaw` | `/oc` | 切到 OpenClaw |
| `/hermes` | `/back` | 切回 Hermes |
| `/status` | — | 查看当前模式 |

---

## 🏗️ 工作原理

```
用户消息 → Gateway → pre_gateway_dispatch hook
                          ↓
                    ┌─────────────────┐
                    │ 检查 mode 文件    │
                    └────────┬────────┘
                       ╱           ╲
                  /openclaw        /hermes
                    ↓                 ↓
              写入 state         删除 state
              返回提示           返回提示
                    ↓                 ↓
              后续消息 →         正常路由 →
              OpenClaw API      Hermes Agent
```

- **状态持久化**：写入 `~/.hermes/openclaw-mode.txt`，重启不丢失
- **零侵入**：不修改 Hermes 核心代码，纯插件实现

---

## 📁 项目结构

```
hermes-openclaw-switcher/
├── README.md              # 本文件
├── LICENSE                # MIT 协议
├── plugin/                # 插件代码
│   ├── plugin.yaml        # 插件清单
│   ├── __init__.py        # 主逻辑
│   └── README.md          # 快速参考
├── examples/
│   └── config.yaml        # 配置示例
└── docs/
    └── ARCHITECTURE.md    # 技术架构详解
```

---

## ⚙️ 配置参考

| 配置项 | 环境变量 | 默认值 | 说明 |
|:-------|:---------|:-------|:-----|
| `openclaw_api_key` | `OPENCLAW_API_KEY` | `""` | API 密钥（必填） |
| `openclaw_base_url` | `OPENCLAW_BASE_URL` | `http://localhost:18789` | OpenClaw 地址 |
| `openclaw_model` | `OPENCLAW_MODEL` | `openclaw/bot2-agent` | 模型 ID |
| `openclaw_timeout` | `OPENCLAW_TIMEOUT` | `120` | 超时（秒） |

---

## ❓ FAQ

**重启后模式会丢失吗？**
不会。状态保存在磁盘，重启自动恢复。

**OpenClaw 没运行会怎样？**
返回错误提示，不影响 Hermes 正常使用。

**支持多个 OpenClaw agent 吗？**
支持。修改 `openclaw_model` 配置切换不同 agent。

**需要什么版本？**
Hermes Agent v0.12+（支持 `pre_gateway_dispatch` hook）。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT

## 🙏 致谢

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — 强大的 AI Agent 框架
- [OpenClaw](https://openclaw.ai) — 多 Agent 协作平台
