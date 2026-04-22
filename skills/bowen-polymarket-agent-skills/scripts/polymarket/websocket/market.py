"""Market WebSocket stream (public, no auth required)."""

from collections.abc import AsyncIterator
from typing import Union

from polymarket.config import PolymarketConfig
from polymarket.models.websocket import (
    WsBestBidAskMessage,
    WsBookMessage,
    WsLastTradePriceMessage,
    WsMarketResolvedMessage,
    WsNewMarketMessage,
    WsPriceChangeMessage,
    WsTickSizeChangeMessage,
)
from polymarket.websocket.base import BaseWebSocket

# Union of all market channel event types
MarketEvent = Union[
    WsBookMessage,
    WsPriceChangeMessage,
    WsLastTradePriceMessage,
    WsTickSizeChangeMessage,
    WsBestBidAskMessage,
    WsNewMarketMessage,
    WsMarketResolvedMessage,
]


class MarketStream(BaseWebSocket):
    """Real-time public market data stream.

    Streams orderbook snapshots, price changes, and trade executions
    for specified market tokens.

    Example:
        >>> async with MarketStream(config) as stream:
        ...     async for event in stream.subscribe(["token_id_1"]):
        ...         if isinstance(event, WsBookMessage):
        ...             print(f"Book update: {len(event.bids)} bids")
        ...         elif isinstance(event, WsPriceChangeMessage):
        ...             for change in event.price_changes:
        ...                 print(f"Price: {change.price} Size: {change.size}")
    """

    def __init__(
        self,
        config: PolymarketConfig,
        custom_features: bool = False,
    ):
        """Initialize market stream.

        Args:
            config: SDK configuration
            custom_features: Enable additional event types (best_bid_ask,
                           new_market, market_resolved)
        """
        super().__init__(config)
        self.custom_features = custom_features

    async def subscribe(
        self,
        token_ids: list[str],
    ) -> AsyncIterator[MarketEvent]:
        """Subscribe to market data for specified tokens.

        Args:
            token_ids: List of ERC1155 token IDs to subscribe

        Yields:
            Market events (book snapshots, price changes, trades, etc.)

        Events:
            - WsBookMessage: Full orderbook snapshot
            - WsPriceChangeMessage: Price level updates
            - WsLastTradePriceMessage: Trade execution prices
            - WsTickSizeChangeMessage: Tick size updates
            - WsBestBidAskMessage: Best bid/ask (requires custom_features)
            - WsNewMarketMessage: New market (requires custom_features)
            - WsMarketResolvedMessage: Market resolved (requires custom_features)
        """
        subscription = {
            "type": "MARKET",
            "assets_ids": token_ids,
        }
        if self.custom_features:
            subscription["custom_feature_enabled"] = True

        async for message in self.stream(subscription):
            event = self._parse_event(message)
            if event is not None:
                yield event

    async def add_tokens(self, token_ids: list[str]) -> None:
        """Subscribe to additional tokens on an existing connection.

        Args:
            token_ids: Additional token IDs to subscribe
        """
        await self.send({
            "assets_ids": token_ids,
            "operation": "subscribe",
        })

    async def remove_tokens(self, token_ids: list[str]) -> None:
        """Unsubscribe from tokens on an existing connection.

        Args:
            token_ids: Token IDs to unsubscribe
        """
        await self.send({
            "assets_ids": token_ids,
            "operation": "unsubscribe",
        })

    def _parse_event(self, message: dict) -> MarketEvent | None:
        """Parse raw message into typed event."""
        event_type = message.get("event_type")

        if event_type == "book":
            return WsBookMessage.model_validate(message)
        elif event_type == "price_change":
            return WsPriceChangeMessage.model_validate(message)
        elif event_type == "last_trade_price":
            return WsLastTradePriceMessage.model_validate(message)
        elif event_type == "tick_size_change":
            return WsTickSizeChangeMessage.model_validate(message)
        elif event_type == "best_bid_ask":
            return WsBestBidAskMessage.model_validate(message)
        elif event_type == "new_market":
            return WsNewMarketMessage.model_validate(message)
        elif event_type == "market_resolved":
            return WsMarketResolvedMessage.model_validate(message)

        # Unknown event type - skip
        return None
