# OpenClaw Switcher Plugin

Hermes Agent 插件 — 在 Gateway 中无缝切换 Hermes ↔ OpenClaw。

## 安装

```bash
cp -r plugin ~/.hermes/plugins/openclaw-switcher
```

## 配置

在 `~/.hermes/config.yaml` 中添加：

```yaml
plugins:
  openclaw-switcher:
    enabled: true
    openclaw_base_url: "http://localhost:18789"
    openclaw_api_key: "your-api-key"
    openclaw_model: "openclaw/bot2-agent"
```

## 命令

| 命令 | 别名 | 功能 |
|:-----|:-----|:-----|
| `/openclaw` | `/oc` | 切换到 OpenClaw 模式 |
| `/hermes` | `/back` | 切回 Hermes 模式 |
| `/status` | — | 查看当前模式 |

## 重启

```bash
hermes gateway restart
```
