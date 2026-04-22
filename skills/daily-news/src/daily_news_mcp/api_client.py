"""6551 新闻 API 的 HTTP 客户端。"""

import logging
from typing import Optional

import httpx

from daily_news_mcp.config import API_BASE_URL

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


class NewsAPIClient:
    """异步 HTTP 客户端，用于访问 6551 新闻 REST API。"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
            )
        return self._client

    async def _reset_client(self):
        """强制关闭并重建 HTTP 客户端。"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def close(self):
        await self._reset_client()

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """执行 HTTP 请求，连接错误时自动重试。"""
        last_exc = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                client = await self._get_client()
                resp = await client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
                last_exc = e
                logger.warning(
                    "连接错误 (第 %d/%d 次尝试): %s",
                    attempt + 1, MAX_RETRIES + 1, repr(e),
                )
                await self._reset_client()
            except httpx.HTTPStatusError:
                raise
        raise last_exc  # type: ignore[misc]

    # ---------- 新闻接口 ----------

    async def get_free_categories(self) -> dict:
        """GET /open/free_categories — 获取所有新闻分类"""
        resp = await self._request("GET", f"{self.base_url}/open/free_categories")
        return resp.json()

    async def get_free_hot(
        self,
        category: str,
        subcategory: str = "",
    ) -> dict:
        """GET /open/free_hot — 获取热点新闻和推文"""
        params: dict = {"category": category}
        if subcategory:
            params["subcategory"] = subcategory
        resp = await self._request("GET", f"{self.base_url}/open/free_hot", params=params)
        return resp.json()
