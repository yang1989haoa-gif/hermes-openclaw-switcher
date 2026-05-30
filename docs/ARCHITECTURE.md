# 技术架构

## 概述

OpenClaw Switcher 通过 Hermes Agent 的 `pre_gateway_dispatch` hook 实现消息路由。当用户发送 `/openclaw` 命令后，后续所有消息会被拦截并转发到 OpenClaw API。

## 核心组件

### 1. 状态管理

```
~/.hermes/openclaw-mode.txt    — 模式状态文件
~/.hermes/openclaw-pending-response.txt  — 待发送响应
```

- 模式状态通过文件存在性判断（存在 = OpenClaw 模式）
- 响应通过临时文件传递给 Gateway

### 2. Hook 注册

```python
def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", _on_command)
    ctx.register_hook("pre_gateway_dispatch", _on_message_dispatch)
```

两个 hook 按注册顺序执行：
1. `_on_command` — 处理命令（/openclaw, /hermes, /status）
2. `_on_message_dispatch` — 拦截普通消息并转发

### 3. 消息路由流程

```
用户消息
    ↓
pre_gateway_dispatch hook
    ↓
┌─ 是命令？ → 处理命令，返回 skip
│
└─ 非命令 → 检查 mode 文件
              ↓
         ┌─ OpenClaw 模式？
         │     ↓
         │  调用 OpenClaw API
         │     ↓
         │  存储响应 → 返回 skip
         │
         └─ Hermes 模式 → 返回 None（继续正常流程）
```

### 4. Gateway 集成

Gateway 在收到 `skip` action 后：
1. 检查 `~/.hermes/openclaw-pending-response.txt`
2. 读取响应内容
3. 通过 platform adapter 发送给用户
4. 删除临时文件

## 配置优先级

```
环境变量 > config.yaml > 默认值
```

| 配置项 | 环境变量 | config.yaml | 默认值 |
|:-------|:---------|:------------|:-------|
| API Key | `OPENCLAW_API_KEY` | `openclaw_api_key` | `""` |
| Base URL | `OPENCLAW_BASE_URL` | `openclaw_base_url` | `http://localhost:18789` |
| Model | `OPENCLAW_MODEL` | `openclaw_model` | `openclaw/bot2-agent` |
| Timeout | `OPENCLAW_TIMEOUT` | `openclaw_timeout` | `120` |

## 线程安全

- 使用 `threading.Lock` 保护状态文件操作
- Gateway 的 async 事件循环通过 `loop.create_task()` 发送响应

## 限制

- 同一时间只支持一个用户切换模式（共享状态文件）
- OpenClaw API 调用是同步的，会阻塞 Gateway 处理其他消息
- 超时默认 120 秒，复杂请求可能需要调整
