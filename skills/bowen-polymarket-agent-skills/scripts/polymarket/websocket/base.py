"""Base WebSocket connection management."""

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

from polymarket.config import PolymarketConfig
from polymarket.exceptions import ConnectionError, WebSocketError


class BaseWebSocket:
    """Base class for WebSocket connections with auto-reconnection.

    Provides connection lifecycle management, heartbeat handling,
    and automatic reconnection with exponential backoff.
    """

    def __init__(
        self,
        config: PolymarketConfig,
        max_reconnect_attempts: int = 5,
        reconnect_delay: float = 1.0,
    ):
        """Initialize WebSocket base.

        Args:
            config: SDK configuration
            max_reconnect_attempts: Maximum reconnection attempts
            reconnect_delay: Initial delay between reconnection attempts
        """
        self.config = config
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self._ws: ClientConnection | None = None
        self._running = False

    @property
    def ws_url(self) -> str:
        """Get the WebSocket URL."""
        return self.config.ws_url

    async def connect(self) -> ClientConnection:
        """Establish WebSocket connection.

        Returns:
            WebSocket connection

        Raises:
            ConnectionError: If connection fails
        """
        attempt = 0
        last_error: Exception | None = None

        while attempt < self.max_reconnect_attempts:
            try:
                self._ws = await websockets.connect(
                    self.ws_url,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5,
                )
                self._running = True
                return self._ws

            except Exception as e:
                last_error = e
                attempt += 1
                if attempt < self.max_reconnect_attempts:
                    delay = self.reconnect_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

        raise ConnectionError(
            message=f"Failed to connect after {self.max_reconnect_attempts} attempts",
            details={"last_error": str(last_error)},
        )

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._running = False
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

    async def send(self, message: dict[str, Any]) -> None:
        """Send a message over the WebSocket.

        Args:
            message: Message to send as dictionary

        Raises:
            WebSocketError: If not connected
        """
        if self._ws is None:
            raise WebSocketError(message="Not connected")

        await self._ws.send(json.dumps(message))

    async def receive(self) -> dict[str, Any]:
        """Receive a message from the WebSocket.

        Returns:
            Parsed message as dictionary

        Raises:
            WebSocketError: If not connected or connection closed
        """
        if self._ws is None:
            raise WebSocketError(message="Not connected")

        try:
            raw = await self._ws.recv()
            return json.loads(raw)
        except websockets.ConnectionClosed as e:
            raise WebSocketError(
                message="Connection closed",
                details={"code": e.code, "reason": e.reason},
            ) from e

    async def _reconnect(self) -> None:
        """Attempt to reconnect after connection loss."""
        await self.disconnect()
        await self.connect()

    async def stream(
        self,
        subscription: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream messages from WebSocket with auto-reconnection.

        Args:
            subscription: Subscription message to send on connect

        Yields:
            Parsed messages from WebSocket

        Note:
            This method handles reconnection automatically. If the
            connection is lost, it will attempt to reconnect and
            re-subscribe.
        """
        while self._running:
            try:
                if self._ws is None:
                    await self.connect()
                    await self.send(subscription)

                while self._running and self._ws is not None:
                    try:
                        message = await self.receive()
                        yield message
                    except WebSocketError as e:
                        if "Connection closed" in str(e):
                            break
                        raise

            except (ConnectionError, WebSocketError):
                if not self._running:
                    break
                # Attempt reconnection
                await asyncio.sleep(self.reconnect_delay)
                self._ws = None

    async def __aenter__(self) -> "BaseWebSocket":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()
