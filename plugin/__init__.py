"""
OpenClaw Switcher Plugin for Hermes Agent
==========================================
Routes messages to OpenClaw API when mode is active.

Usage:
  /openclaw or /oc  — Switch to OpenClaw mode
  /hermes or /back  — Switch back to Hermes mode
  /status           — Show current mode

Flow:
  1. /openclaw command sets state file
  2. pre_gateway_dispatch hook intercepts messages
  3. Calls OpenClaw API synchronously, stores response
  4. Returns {"action": "skip"} to prevent Hermes processing
  5. Gateway picks up stored response and sends it
"""

import json
import logging
import os
import threading
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
STATE_FILE = HERMES_HOME / "openclaw-mode.txt"
PENDING_RESPONSE = HERMES_HOME / "openclaw-pending-response.txt"

_lock = threading.Lock()

# ─── Aliases ──────────────────────────────────────────────────────────────────
OPENCLAW_ALIASES = {"/openclaw", "/oc"}
HERMES_ALIASES = {"/hermes", "/back"}
STATUS_ALIASES = {"/status"}


# ─── Config ───────────────────────────────────────────────────────────────────
def _load_config():
    """Load plugin config from Hermes config.yaml."""
    try:
        from hermes_cli.config import load_config
        config = load_config()
        return config.get("plugins", {}).get("openclaw-switcher", {})
    except Exception as e:
        logger.warning("Failed to load config: %s", e)
        return {}


def _get_api_key(config):
    """Get API key from config or environment variable."""
    # Environment variable takes priority
    key = os.environ.get("OPENCLAW_API_KEY", "")
    if key:
        return key
    return config.get("openclaw_api_key", "")


def _get_base_url(config):
    return os.environ.get(
        "OPENCLAW_BASE_URL",
        config.get("openclaw_base_url", "http://localhost:18789")
    )


def _get_model(config):
    return os.environ.get(
        "OPENCLAW_MODEL",
        config.get("openclaw_model", "openclaw/bot2-agent")
    )


def _get_timeout(config):
    return int(os.environ.get(
        "OPENCLAW_TIMEOUT",
        config.get("openclaw_timeout", 120)
    ))


# ─── State ────────────────────────────────────────────────────────────────────
def _is_openclaw_mode():
    """Check if OpenClaw mode is currently active."""
    return STATE_FILE.exists()


def _set_mode(active=True):
    """Set or clear OpenClaw mode."""
    if active:
        STATE_FILE.write_text("active")
    else:
        STATE_FILE.unlink(missing_ok=True)


def _send_pending_response():
    """Pick up and send any pending OpenClaw response."""
    if not PENDING_RESPONSE.exists():
        return False
    try:
        reply = PENDING_RESPONSE.read_text().strip()
        PENDING_RESPONSE.unlink(missing_ok=True)
        if reply:
            # Write to a location the gateway can pick up
            # The gateway checks for this file after skip action
            return True
    except Exception as e:
        logger.warning("Failed to read pending response: %s", e)
    return False


# ─── API Call ──────────────────────────────────────────────────────────────────
def _call_openclaw_api(message_text, api_key, base_url, model, timeout=120):
    """Call OpenClaw API synchronously and return response text.

    Args:
        message_text: User message to send
        api_key: OpenClaw API key
        base_url: OpenClaw server URL
        model: Model ID to use
        timeout: Request timeout in seconds

    Returns:
        Response text or error message
    """
    url = f"{base_url}/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": message_text}],
        "max_tokens": 4096,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return content
    except urllib.error.URLError as e:
        logger.error("OpenClaw API connection failed: %s", e)
        return f"❌ OpenClaw 连接失败: {e}"
    except Exception as e:
        logger.error("OpenClaw API call failed: %s", e)
        return f"❌ OpenClaw 调用失败: {e}"


# ─── Hook Handlers ────────────────────────────────────────────────────────────
def _on_command(event, gateway, session_store):
    """Handle /openclaw, /hermes, /status commands."""
    text = (event.text or "").strip().lower()

    # /status — show current mode
    if text in STATUS_ALIASES:
        mode = "🔵 OpenClaw" if _is_openclaw_mode() else "🟢 Hermes"
        PENDING_RESPONSE.write_text(f"当前模式: {mode}")
        return {"action": "skip", "reason": "status check"}

    # /openclaw — enable OpenClaw mode
    if text in OPENCLAW_ALIASES:
        _set_mode(active=True)
        PENDING_RESPONSE.write_text("✅ OpenClaw 模式已开启。后续消息将由 OpenClaw 处理。发送 /hermes 切回。")
        logger.info("OpenClaw mode activated")
        return {"action": "skip", "reason": "openclaw mode activated"}

    # /hermes — disable OpenClaw mode
    if text in HERMES_ALIASES:
        _set_mode(active=False)
        PENDING_RESPONSE.write_text("✅ Hermes 模式已恢复。")
        logger.info("Hermes mode restored")
        return {"action": "skip", "reason": "hermes mode restored"}

    return None


def _on_message_dispatch(event, gateway, session_store):
    """Intercept messages when OpenClaw mode is active."""
    text = (event.text or "").strip()

    # Skip empty messages
    if not text:
        return None

    # Skip commands — let them through to the command handler
    if text.startswith("/"):
        return None

    # Skip if not in OpenClaw mode
    if not _is_openclaw_mode():
        return None

    # Load config
    config = _load_config()
    api_key = _get_api_key(config)
    base_url = _get_base_url(config)
    model = _get_model(config)
    timeout = _get_timeout(config)

    if not api_key:
        PENDING_RESPONSE.write_text("❌ OpenClaw API key 未配置。请在 config.yaml 或 OPENCLAW_API_KEY 环境变量中设置。")
        logger.warning("OpenClaw API key not configured")
        return {"action": "skip", "reason": "api key missing"}

    # Call OpenClaw API
    logger.info("Routing to OpenClaw [%s]: %r", model, text[:50])
    response = _call_openclaw_api(text, api_key, base_url, model, timeout)
    logger.info("OpenClaw response: %r", response[:80])

    # Store response for gateway to pick up
    PENDING_RESPONSE.write_text(response)

    return {"action": "skip", "reason": "routed to openclaw"}


# ─── Plugin Registration ──────────────────────────────────────────────────────
def register(ctx):
    """Register plugin hooks with Hermes Gateway.

    This function is called by the Hermes plugin system when the plugin is loaded.
    """
    ctx.register_hook("pre_gateway_dispatch", _on_command)
    ctx.register_hook("pre_gateway_dispatch", _on_message_dispatch)
    logger.info("OpenClaw Switcher plugin registered (v1.0.0)")
