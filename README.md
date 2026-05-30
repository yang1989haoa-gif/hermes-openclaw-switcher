# OpenClaw Switcher for Hermes Agent

> 🔀 一键切换 Hermes ↔ OpenClaw 模式的 Gateway 插件

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-v0.12+-green.svg)](https://github.com/NousResearch/hermes-agent)

## 功能

在 Hermes Agent 的消息网关（Gateway）中无缝切换不同的 AI 后端：

| 命令 | 功能 |
|:-----|:-----|
| `/openclaw` 或 `/oc` | 切换到 OpenClaw 模式 |
| `/hermes` 或 `/back` | 切回 Hermes 模式 |
| `/status` | 查看当前使用模式 |

## 工作原理

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
                    ↓
              存储响应 →
              Gateway 发送
```

- **状态持久化**：模式状态写入磁盘，重启不丢失
- **零侵入**：不修改 Hermes 核心代码，纯插件实现
- **异步响应**：通过 `pre_gateway_dispatch` hook + pending response 机制实现

## 快速开始

### 1. 复制插件

```bash
# 克隆项目
git clone https://github.com/<your-username>/hermes-openclaw-switcher.git
cd hermes-openclaw-switcher

# 复制到 Hermes 插件目录
cp -r plugin ~/.hermes/plugins/openclaw-switcher
```

### 2. 配置 API

编辑 `~/.hermes/config.yaml`：

```yaml
plugins:
  openclaw-switcher:
    enabled: true
    openclaw_base_url: "http://localhost:18789"
    openclaw_api_key: "your-openclaw-api-key"
    openclaw_model: "openclaw/bot2-agent"
```

或使用环境变量（推荐）：

```bash
# 在 ~/.hermes/.env 中添加
OPENCLAW_API_KEY=your-openclaw-api-key
```

### 3. 重启 Gateway

```bash
hermes gateway restart
```

### 4. 使用

在 QQ/微信/Telegram 等连接的平台上：

```
你: /oc
Hermes: ✅ OpenClaw 模式已开启。后续消息将由 OpenClaw 处理。

你: 你好
OpenClaw: 你好！我是 OpenClaw 助手...

你: /back
Hermes: ✅ Hermes 模式已恢复。
```

## 项目结构

```
hermes-openclaw-switcher/
├── README.md              # 本文件
├── LICENSE                # MIT 协议
├── plugin/                # 插件代码
│   ├── plugin.yaml        # 插件清单
│   ├── __init__.py        # 主逻辑
│   └── README.md          # 插件内文档
├── examples/
│   └── config.yaml        # 配置示例
└── docs/
    └── ARCHITECTURE.md    # 技术架构详解
```

## 配置参考

| 配置项 | 默认值 | 说明 |
|:-------|:-------|:-----|
| `openclaw_base_url` | `http://localhost:18789` | OpenClaw API 地址 |
| `openclaw_api_key` | `""` | API 密钥（必填） |
| `openclaw_model` | `openclaw/bot2-agent` | 使用的模型 ID |
| `openclaw_timeout` | `120` | API 调用超时时间（秒） |

## 环境变量

优先级：环境变量 > config.yaml

| 变量名 | 对应配置 |
|:-------|:---------|
| `OPENCLAW_API_KEY` | `openclaw_api_key` |
| `OPENCLAW_BASE_URL` | `openclaw_base_url` |
| `OPENCLAW_MODEL` | `openclaw_model` |

## 系统要求

- Hermes Agent v0.12+（支持 `pre_gateway_dispatch` hook）
- OpenClaw 实例运行中（默认端口 18789）

## 常见问题

### Q: 重启后模式会丢失吗？

不会。模式状态保存在 `~/.hermes/openclaw-mode.txt`，重启后自动恢复。

### Q: OpenClaw 没运行时会怎样？

插件会返回错误提示 `[OpenClaw 调用失败: ...]`，不影响 Hermes 正常使用。

### Q: 能同时用多个 OpenClaw agent 吗？

可以。修改 `openclaw_model` 配置项切换不同的 agent ID。

### Q: 支持哪些平台？

支持所有 Hermes Gateway 支持的平台：QQ、微信、Telegram、Discord、Slack 等。

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT

## 致谢

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — 强大的 AI Agent 框架
- [OpenClaw](https://openclaw.ai) — 多 Agent 协作平台
