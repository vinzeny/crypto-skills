"""Position and activity models."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ActivityType(StrEnum):
    """Activity type."""

    TRADE = "TRADE"
    SPLIT = "SPLIT"
    MERGE = "MERGE"
    REDEEM = "REDEEM"
    REWARD = "REWARD"
    CONVERSION = "CONVERSION"
    MAKER_REBATE = "MAKER_REBATE"


class Position(BaseModel):
    """User's position in a market."""

    proxy_wallet: str | None = Field(default=None, alias="proxyWallet")
    asset: str | None = None
    condition_id: str | None = Field(default=None, alias="conditionId")
    size: float | None = None
    avg_price: float | None = Field(default=None, alias="avgPrice")
    current_value: float | None = Field(default=None, alias="currentValue")
    cash_pnl: float | None = Field(default=None, alias="cashPnl")
    percent_pnl: float | None = Field(default=None, alias="percentPnl")
    title: str | None = None
    outcome: str | None = None
    redeemable: bool | None = None
    mergeable: bool | None = None

    model_config = {"populate_by_name": True}


class ClosedPosition(BaseModel):
    """A closed position."""

    proxy_wallet: str | None = Field(default=None, alias="proxyWallet")
    asset: str | None = None
    condition_id: str | None = Field(default=None, alias="conditionId")
    avg_price: float | None = Field(default=None, alias="avgPrice")
    total_bought: float | None = Field(default=None, alias="totalBought")
    realized_pnl: float | None = Field(default=None, alias="realizedPnl")
    cur_price: float | None = Field(default=None, alias="curPrice")
    timestamp: int | None = None
    title: str | None = None
    slug: str | None = None
    icon: str | None = None
    event_slug: str | None = Field(default=None, alias="eventSlug")
    outcome: str | None = None
    outcome_index: int | None = Field(default=None, alias="outcomeIndex")
    opposite_outcome: str | None = Field(default=None, alias="oppositeOutcome")
    opposite_asset: str | None = Field(default=None, alias="oppositeAsset")
    end_date: str | None = Field(default=None, alias="endDate")

    model_config = {"populate_by_name": True}


class Activity(BaseModel):
    """User activity item."""

    proxy_wallet: str | None = Field(default=None, alias="proxyWallet")
    timestamp: int | None = None
    condition_id: str | None = Field(default=None, alias="conditionId")
    type: ActivityType | None = None
    size: float | None = None
    usdc_size: float | None = Field(default=None, alias="usdcSize")
    transaction_hash: str | None = Field(default=None, alias="transactionHash")
    price: float | None = None
    asset: str | None = None
    side: str | None = None
    outcome_index: int | None = Field(default=None, alias="outcomeIndex")
    title: str | None = None
    slug: str | None = None
    icon: str | None = None
    event_slug: str | None = Field(default=None, alias="eventSlug")
    outcome: str | None = None
    name: str | None = None
    pseudonym: str | None = None
    bio: str | None = None
    profile_image: str | None = Field(default=None, alias="profileImage")

    model_config = {"populate_by_name": True}


class LeaderboardEntry(BaseModel):
    """Trader leaderboard entry."""

    rank: str | None = None
    user: str | None = None
    volume: float | None = None
    pnl: float | None = None
    profit: float | None = None
    markets_traded: int | None = Field(default=None, alias="marketsTraded")
    name: str | None = None
    pseudonym: str | None = None
    profile_image: str | None = Field(default=None, alias="profileImage")

    model_config = {"populate_by_name": True}


class BuilderLeaderboardEntry(BaseModel):
    """Builder leaderboard entry."""

    rank: str | None = None
    builder: str | None = None
    volume: float | None = None
    active_users: int | None = Field(default=None, alias="activeUsers")
    verified: bool | None = None
    builder_logo: str | None = Field(default=None, alias="builderLogo")

    model_config = {"populate_by_name": True}


class MarketVolume(BaseModel):
    """Volume for a single market."""

    market: str | None = None
    value: float | None = None


class LiveVolume(BaseModel):
    """Live volume for an event."""

    total: float | None = None
    markets: list[MarketVolume] | None = None


class OpenInterestItem(BaseModel):
    """Open interest for a market."""

    market: str | None = None
    value: float | None = None


class Holder(BaseModel):
    """Token holder."""

    user: str | None = None
    size: float | None = None
    avg_price: float | None = Field(default=None, alias="avgPrice")
    name: str | None = None
    pseudonym: str | None = None
    profile_image: str | None = Field(default=None, alias="profileImage")

    model_config = {"populate_by_name": True}
