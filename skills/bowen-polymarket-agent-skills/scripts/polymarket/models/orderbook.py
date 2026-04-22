"""Orderbook models."""

from datetime import datetime

from pydantic import BaseModel, Field


class OrderLevel(BaseModel):
    """A price level in the order book."""

    price: str
    size: str


class OrderBookSummary(BaseModel):
    """Order book summary for a token."""

    market: str | None = Field(default=None, description="Market condition ID")
    asset_id: str | None = Field(default=None, alias="asset_id", description="Token ID")
    timestamp: datetime | None = None
    hash: str | None = None
    bids: list[OrderLevel] | None = None
    asks: list[OrderLevel] | None = None
    min_order_size: str | None = Field(default=None, alias="min_order_size")
    tick_size: str | None = Field(default=None, alias="tick_size")
    neg_risk: bool | None = Field(default=None, alias="neg_risk")

    model_config = {"populate_by_name": True}


class SpreadInfo(BaseModel):
    """Bid-ask spread information."""

    asset_id: str | None = Field(default=None, alias="asset_id")
    bid: str | None = None
    ask: str | None = None
    spread: str | None = None

    model_config = {"populate_by_name": True}


class BalanceAllowance(BaseModel):
    """Balance and allowance response."""

    balance: str | None = None
    allowance: str | None = None


class PriceHistoryPoint(BaseModel):
    """A single point in price history."""

    t: float = Field(description="UTC timestamp")
    p: float = Field(description="Price")


class PriceHistoryResponse(BaseModel):
    """Price history response."""

    history: list[PriceHistoryPoint] | None = None
