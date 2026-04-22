"""WebSocket message models."""

from typing import Literal, Union

from pydantic import BaseModel, Field

from polymarket.models.orders import OrderSide


class WsAuth(BaseModel):
    """WebSocket authentication (required for user channel only)."""

    api_key: str = Field(alias="apiKey", description="API key from L1 authentication")
    secret: str = Field(description="API secret")
    passphrase: str = Field(description="API passphrase")

    model_config = {"populate_by_name": True}


class WsSubscription(BaseModel):
    """WebSocket subscription message."""

    auth: WsAuth | None = None
    type: Literal["MARKET", "USER"]
    assets_ids: list[str] | None = Field(
        default=None, description="Token IDs to subscribe (for market channel)"
    )
    markets: list[str] | None = Field(
        default=None, description="Condition IDs to subscribe (for user channel)"
    )
    custom_feature_enabled: bool | None = Field(
        default=None, description="Enable additional event types"
    )

    model_config = {"populate_by_name": True}


# Market channel messages


class WsOrderLevel(BaseModel):
    """Order level in WebSocket messages."""

    price: str
    size: str


class WsBookMessage(BaseModel):
    """Full orderbook snapshot (market channel)."""

    event_type: Literal["book"]
    asset_id: str = Field(description="Token ID")
    market: str = Field(description="Condition ID")
    timestamp: str = Field(description="Unix timestamp in milliseconds")
    hash: str = Field(description="Orderbook content hash")
    bids: list[WsOrderLevel]
    asks: list[WsOrderLevel]


class WsPriceChange(BaseModel):
    """Price change in WebSocket messages."""

    asset_id: str
    price: str
    size: str = Field(description="New aggregate size at price level")
    side: OrderSide
    hash: str | None = None
    best_bid: str | None = None
    best_ask: str | None = None


class WsPriceChangeMessage(BaseModel):
    """Price level update (market channel)."""

    event_type: Literal["price_change"]
    market: str = Field(description="Condition ID")
    timestamp: str = Field(description="Unix timestamp in milliseconds")
    price_changes: list[WsPriceChange]


class WsLastTradePriceMessage(BaseModel):
    """Trade execution price (market channel)."""

    event_type: Literal["last_trade_price"]
    asset_id: str
    market: str
    price: str
    size: str
    side: OrderSide
    fee_rate_bps: str
    timestamp: str


class WsTickSizeChangeMessage(BaseModel):
    """Tick size change (market channel)."""

    event_type: Literal["tick_size_change"]
    asset_id: str
    market: str
    tick_size: str
    min_order_size: str


class WsBestBidAskMessage(BaseModel):
    """Best bid/ask update (market channel, requires custom_feature_enabled)."""

    event_type: Literal["best_bid_ask"]
    asset_id: str
    market: str
    best_bid: str
    best_ask: str
    timestamp: str


class WsNewMarketMessage(BaseModel):
    """New market created (market channel, requires custom_feature_enabled)."""

    event_type: Literal["new_market"]
    market: str
    asset_id: str


class WsMarketResolvedMessage(BaseModel):
    """Market resolved (market channel, requires custom_feature_enabled)."""

    event_type: Literal["market_resolved"]
    market: str
    asset_id: str
    winning_outcome: str


# User channel messages


class WsMakerOrder(BaseModel):
    """Maker order in trade message."""

    order_id: str
    asset_id: str
    price: str
    matched_amount: str
    outcome: str
    owner: str


class WsTradeMessage(BaseModel):
    """Trade event (user channel)."""

    event_type: Literal["trade"]
    id: str = Field(description="Trade ID")
    taker_order_id: str
    market: str = Field(description="Condition ID")
    asset_id: str
    side: OrderSide
    price: str
    size: str
    status: Literal["MATCHED", "MINED", "CONFIRMED", "RETRYING", "FAILED"]
    matchtime: str
    timestamp: str
    owner: str = Field(description="API key of trade owner")
    maker_orders: list[WsMakerOrder] | None = None


class WsOrderMessage(BaseModel):
    """Order event (user channel)."""

    event_type: Literal["order"]
    type: Literal["PLACEMENT", "UPDATE", "CANCELLATION"]
    id: str = Field(description="Order ID")
    market: str = Field(description="Condition ID")
    asset_id: str
    side: OrderSide
    price: str
    original_size: str
    size_matched: str
    outcome: str
    owner: str = Field(description="API key")
    timestamp: str
    associate_trades: list[str] | None = Field(
        default=None, description="IDs of trades this order participated in"
    )


# Union types for event handling

MarketEvent = Union[
    WsBookMessage,
    WsPriceChangeMessage,
    WsLastTradePriceMessage,
    WsTickSizeChangeMessage,
    WsBestBidAskMessage,
    WsNewMarketMessage,
    WsMarketResolvedMessage,
]

UserEvent = Union[WsTradeMessage, WsOrderMessage]
