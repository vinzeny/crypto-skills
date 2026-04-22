"""HTTP client with rate limiting and retry logic."""

import asyncio
from typing import Any

import httpx

from polymarket.config import PolymarketConfig
from polymarket.exceptions import (
    AuthenticationError,
    PolymarketError,
    RateLimitError,
    ValidationError,
)


class RateLimitedClient:
    """Async HTTP client with rate limiting and retry logic."""

    def __init__(self, config: PolymarketConfig | None = None):
        self.config = config or PolymarketConfig()
        self._semaphore = asyncio.Semaphore(int(self.config.requests_per_second))
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "RateLimitedClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an HTTP request with rate limiting and retry logic.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            url: Full URL to request
            headers: Optional headers to include
            params: Optional query parameters
            json: Optional JSON body

        Returns:
            HTTP response

        Raises:
            RateLimitError: If rate limit exceeded after retries
            AuthenticationError: If authentication fails
            ValidationError: If request validation fails
            PolymarketError: For other API errors
        """
        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries):
            async with self._semaphore:
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json,
                    )

                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after = float(
                            response.headers.get("Retry-After", 2**attempt)
                        )
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise RateLimitError(
                            message="Rate limit exceeded",
                            retry_after=retry_after,
                        )

                    # Handle auth errors
                    if response.status_code == 401:
                        raise AuthenticationError(
                            message="Authentication failed",
                            details=self._parse_error(response),
                        )

                    # Handle validation errors
                    if response.status_code == 400:
                        raise ValidationError(
                            message="Request validation failed",
                            details=self._parse_error(response),
                        )

                    # Handle not found
                    if response.status_code == 404:
                        raise PolymarketError(
                            message="Resource not found",
                            details=self._parse_error(response),
                        )

                    # Handle server errors with retry
                    if response.status_code >= 500:
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(2**attempt)
                            continue
                        raise PolymarketError(
                            message=f"Server error: {response.status_code}",
                            details=self._parse_error(response),
                        )

                    return response

                except httpx.TimeoutException as e:
                    last_error = e
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(2**attempt)
                        continue
                    raise PolymarketError(
                        message="Request timeout",
                        details={"timeout": self.config.timeout},
                    ) from e

                except httpx.RequestError as e:
                    last_error = e
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(2**attempt)
                        continue
                    raise PolymarketError(
                        message=f"Request failed: {str(e)}",
                    ) from e

        # Should not reach here, but just in case
        raise PolymarketError(
            message="Request failed after retries",
            details={"last_error": str(last_error)},
        )

    def _parse_error(self, response: httpx.Response) -> dict[str, Any]:
        """Parse error details from response."""
        try:
            data = response.json()
            return {
                "status_code": response.status_code,
                "error": data.get("error"),
                "code": data.get("code"),
                "body": data,
            }
        except Exception:
            return {
                "status_code": response.status_code,
                "body": response.text[:500],
            }

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a GET request."""
        return await self.request("GET", url, headers=headers, params=params)

    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a POST request."""
        return await self.request("POST", url, headers=headers, json=json)

    async def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a DELETE request."""
        return await self.request("DELETE", url, headers=headers, json=json)
