"""Daily News MCP 服务配置。

从 config.json 读取配置，环境变量优先级更高。
"""

import json
import os
from pathlib import Path

# ---------- 加载 config.json ----------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config.json"

_cfg: dict = {}
if _CONFIG_PATH.exists():
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        _cfg = json.load(f)

# ---------- API 配置（环境变量优先） ----------
API_BASE_URL = (
    os.environ.get("DAILY_NEWS_API_BASE")
    or _cfg.get("api_base_url", "https://ai.6551.io")
)

# ---------- 安全限制 ----------
MAX_ROWS = int(
    os.environ.get("DAILY_NEWS_MAX_ROWS", 0)
    or _cfg.get("max_rows", 100)
)


def clamp_limit(limit: int) -> int:
    """将用户传入的 limit 限制在 [1, MAX_ROWS] 范围内。"""
    return min(max(1, limit), MAX_ROWS)
