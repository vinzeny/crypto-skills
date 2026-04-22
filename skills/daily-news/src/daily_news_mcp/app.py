"""FastMCP 应用实例和生命周期管理。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from daily_news_mcp.api_client import NewsAPIClient


@dataclass
class AppContext:
    """所有工具通过 ctx 共享的应用状态。"""
    api: NewsAPIClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """管理 API 客户端生命周期。"""
    api = NewsAPIClient()
    try:
        yield AppContext(api=api)
    finally:
        await api.close()


# ---------- FastMCP 实例 ----------
mcp = FastMCP(
    "daily-news-6551",
    lifespan=app_lifespan,
    json_response=True,
)
