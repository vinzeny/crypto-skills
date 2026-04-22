"""Base service class for API clients."""

import json
from typing import Any, TypeVar

from pydantic import BaseModel

from polymarket.auth import AuthManager
from polymarket.config import PolymarketConfig
from polymarket.http import RateLimitedClient

T = TypeVar("T", bound=BaseModel)


class BaseService:
    """Base class for API service clients.

    Provides common functionality for making authenticated and
    unauthenticated requests to Polymarket APIs.
    """

    def __init__(
        self,
        http: RateLimitedClient,
        config: PolymarketConfig,
        auth: AuthManager | None = None,
    ):
        """Initialize service.

        Args:
            http: HTTP client instance
            config: SDK configuration
            auth: Authentication manager (optional for public endpoints)
        """
        self.http = http
        self.config = config
        self.auth = auth

    def _url(self, base: str, path: str) -> str:
        """Build full URL from base and path."""
        return f"{base.rstrip('/')}/{path.lstrip('/')}"

    async def _get(
        self,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
        authenticated: bool = False,
    ) -> dict[str, Any] | list[Any]:
        """Make a GET request.

        Args:
            base_url: Base URL for the API
            path: Request path
            params: Query parameters
            authenticated: Whether to include L2 auth headers

        Returns:
            Parsed JSON response
        """
        url = self._url(base_url, path)
        headers = {}

        if authenticated and self.auth:
            headers = self.auth.l2.build_headers("GET", path)

        # Filter None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = await self.http.get(url, headers=headers, params=params)
        return response.json()

    async def _post(
        self,
        base_url: str,
        path: str,
        body: dict[str, Any] | None = None,
        authenticated: bool = False,
    ) -> dict[str, Any] | list[Any]:
        """Make a POST request.

        Args:
            base_url: Base URL for the API
            path: Request path
            body: JSON body
            authenticated: Whether to include L2 auth headers

        Returns:
            Parsed JSON response
        """
        url = self._url(base_url, path)
        headers = {"Content-Type": "application/json"}

        body_str = json.dumps(body) if body else ""

        if authenticated and self.auth:
            auth_headers = self.auth.l2.build_headers("POST", path, body_str)
            headers.update(auth_headers)

        response = await self.http.post(url, headers=headers, json=body)
        return response.json()

    async def _delete(
        self,
        base_url: str,
        path: str,
        body: dict[str, Any] | None = None,
        authenticated: bool = False,
    ) -> dict[str, Any] | list[Any]:
        """Make a DELETE request.

        Args:
            base_url: Base URL for the API
            path: Request path
            body: JSON body
            authenticated: Whether to include L2 auth headers

        Returns:
            Parsed JSON response
        """
        url = self._url(base_url, path)
        headers = {"Content-Type": "application/json"}

        body_str = json.dumps(body) if body else ""

        if authenticated and self.auth:
            auth_headers = self.auth.l2.build_headers("DELETE", path, body_str)
            headers.update(auth_headers)

        response = await self.http.delete(url, headers=headers, json=body)
        return response.json()

    async def _post_l1(
        self,
        base_url: str,
        path: str,
        nonce: int = 0,
    ) -> dict[str, Any]:
        """Make a POST request with L1 authentication.

        Args:
            base_url: Base URL for the API
            path: Request path
            nonce: Nonce for credential derivation

        Returns:
            Parsed JSON response
        """
        if not self.auth:
            raise ValueError("Auth manager required for L1 requests")

        url = self._url(base_url, path)
        headers = self.auth.l1.build_headers(nonce)

        response = await self.http.post(url, headers=headers)
        return response.json()

    async def _get_l1(
        self,
        base_url: str,
        path: str,
        nonce: int = 0,
    ) -> dict[str, Any]:
        """Make a GET request with L1 authentication.

        Args:
            base_url: Base URL for the API
            path: Request path
            nonce: Nonce for credential derivation

        Returns:
            Parsed JSON response
        """
        if not self.auth:
            raise ValueError("Auth manager required for L1 requests")

        url = self._url(base_url, path)
        headers = self.auth.l1.build_headers(nonce)

        response = await self.http.get(url, headers=headers)
        return response.json()

    def _parse(self, data: dict[str, Any] | list[Any], model: type[T]) -> T:
        """Parse response data into a Pydantic model."""
        return model.model_validate(data)

    def _parse_list(
        self, data: list[dict[str, Any]], model: type[T]
    ) -> list[T]:
        """Parse response data into a list of Pydantic models."""
        return [model.model_validate(item) for item in data]
