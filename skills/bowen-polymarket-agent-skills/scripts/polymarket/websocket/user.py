"""User WebSocket stream (requires authentication)."""

from collections.abc import AsyncIterator
from typing import Union

from polymarket.auth import Credentials
from polymarket.config import PolymarketConfig
from polymarket.models.websocket import WsOrderMessage, WsTradeMessage
from polymarket.websocket.base import BaseWebSocket

# Union of all user channel event types
UserEvent = Union[WsTradeMessage, WsOrderMessage]


class UserStream(BaseWebSocket):
    """Real-time private user data stream.

    Streams order updates and trade executions for the authenticated user.
    Requires API credentials from L1 authentication.

    Example:
        >>> credentials = Credentials(api_key="...", secret="...", passphrase="...")
        >>> async with UserStream(config, credentials) as stream:
        ...     async for event in stream.subscribe(["condition_id_1"]):
        ...         if isinstance(event, WsOrderMessage):
        ...             print(f"Order {event.type}: {event.id}")
        ...         elif isinstance(event, WsTradeMessage):
        ...             print(f"Trade {event.status}: {event.size} @ {event.price}")
    """

    def __init__(
        self,
        config: PolymarketConfig,
        credentials: Credentials,
    ):
        """Initialize user stream.

        Args:
            config: SDK configuration
            credentials: API credentials for authentication
        """
        super().__init__(config)
        self.credentials = credentials

    async def subscribe(
        self,
        market_ids: list[str],
    ) -> AsyncIterator[UserEvent]:
        """Subscribe to user events for specified markets.

        Args:
            market_ids: List of market condition IDs to subscribe

        Yields:
            User events (order updates, trade executions)

        Events:
            - WsOrderMessage: Order placement, update, or cancellation
            - WsTradeMessage: Trade matched, mined, confirmed, or failed

        Order event types:
            - PLACEMENT: New order placed
            - UPDATE: Order partially filled
            - CANCELLATION: Order cancelled

        Trade statuses:
            - MATCHED: Trade matched on orderbook
            - MINED: Transaction included in block
            - CONFIRMED: Transaction confirmed
            - RETRYING: Transaction being retried
            - FAILED: Transaction failed
        """
        subscription = {
            "auth": {
                "apiKey": self.credentials.api_key,
                "secret": self.credentials.secret,
                "passphrase": self.credentials.passphrase,
            },
            "type": "USER",
            "markets": market_ids,
        }

        async for message in self.stream(subscription):
            event = self._parse_event(message)
            if event is not None:
                yield event

    async def add_markets(self, market_ids: list[str]) -> None:
        """Subscribe to additional markets on an existing connection.

        Args:
            market_ids: Additional market condition IDs to subscribe
        """
        await self.send({
            "markets": market_ids,
            "operation": "subscribe",
        })

    async def remove_markets(self, market_ids: list[str]) -> None:
        """Unsubscribe from markets on an existing connection.

        Args:
            market_ids: Market condition IDs to unsubscribe
        """
        await self.send({
            "markets": market_ids,
            "operation": "unsubscribe",
        })

    def _parse_event(self, message: dict) -> UserEvent | None:
        """Parse raw message into typed event."""
        event_type = message.get("event_type")

        if event_type == "order":
            return WsOrderMessage.model_validate(message)
        elif event_type == "trade":
            return WsTradeMessage.model_validate(message)

        # Unknown event type - skip
        return None
