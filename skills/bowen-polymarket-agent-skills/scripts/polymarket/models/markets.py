"""Market and event models."""

from datetime import datetime

from pydantic import BaseModel, Field


class MarketToken(BaseModel):
    """Token information for a market outcome."""

    token_id: str = Field(alias="token_id")
    outcome: str
    price: str | None = None
    winner: bool | None = None

    model_config = {"populate_by_name": True}


class Market(BaseModel):
    """A prediction market."""

    id: str | None = None
    question: str | None = None
    condition_id: str | None = Field(default=None, alias="conditionId")
    slug: str | None = None
    resolution_source: str | None = Field(default=None, alias="resolutionSource")
    end_date: datetime | None = Field(default=None, alias="endDate")
    liquidity: str | None = None
    volume: str | None = None
    volume_24hr: str | None = Field(default=None, alias="volume24hr")
    active: bool | None = None
    closed: bool | None = None
    market_maker_address: str | None = Field(default=None, alias="marketMakerAddress")
    outcomes: list[str] | None = None
    outcome_prices: list[str] | None = Field(default=None, alias="outcomePrices")
    tokens: list[MarketToken] | None = None
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None

    model_config = {"populate_by_name": True}


class Event(BaseModel):
    """An event containing multiple markets."""

    id: str | None = None
    slug: str | None = None
    title: str | None = None
    description: str | None = None
    start_date: datetime | None = Field(default=None, alias="startDate")
    end_date: datetime | None = Field(default=None, alias="endDate")
    active: bool | None = None
    closed: bool | None = None
    liquidity: str | None = None
    volume: str | None = None
    markets: list[Market] | None = None
    tags: list[str] | None = None

    model_config = {"populate_by_name": True}


class Series(BaseModel):
    """A series containing multiple events."""

    id: str | None = None
    ticker: str | None = None
    slug: str | None = None
    title: str | None = None
    subtitle: str | None = None
    series_type: str | None = Field(default=None, alias="seriesType")
    recurrence: str | None = None
    description: str | None = None
    image: str | None = None
    icon: str | None = None
    layout: str | None = None
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    featured: bool | None = None
    volume: float | None = None
    volume_24hr: float | None = Field(default=None, alias="volume24hr")
    liquidity: float | None = None
    start_date: datetime | None = Field(default=None, alias="startDate")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    events: list[Event] | None = None
    tags: list[str] | None = None

    model_config = {"populate_by_name": True}


class Tag(BaseModel):
    """A market tag."""

    id: str | None = None
    label: str | None = None
    slug: str | None = None
    force_show: bool | None = Field(default=None, alias="forceShow")
    force_hide: bool | None = Field(default=None, alias="forceHide")
    is_carousel: bool | None = Field(default=None, alias="isCarousel")
    published_at: str | None = Field(default=None, alias="publishedAt")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class Team(BaseModel):
    """Sports team."""

    id: str | None = None
    name: str | None = None
    short_name: str | None = Field(default=None, alias="shortName")
    logo: str | None = None
    sport: str | None = None
    league: str | None = None

    model_config = {"populate_by_name": True}


class Comment(BaseModel):
    """User comment."""

    id: str | None = None
    text: str | None = None
    user: str | None = None
    created_at: datetime | None = Field(default=None, alias="createdAt")
    likes: int | None = None
    replies: int | None = None

    model_config = {"populate_by_name": True}


class ProfileUser(BaseModel):
    """User reference in profile."""

    id: str | None = None
    creator: bool | None = None
    mod: bool | None = None


class PublicProfile(BaseModel):
    """Public user profile."""

    created_at: datetime | None = Field(default=None, alias="createdAt")
    proxy_wallet: str | None = Field(default=None, alias="proxyWallet")
    profile_image: str | None = Field(default=None, alias="profileImage")
    display_username_public: bool | None = Field(
        default=None, alias="displayUsernamePublic"
    )
    bio: str | None = None
    pseudonym: str | None = None
    name: str | None = None
    x_username: str | None = Field(default=None, alias="xUsername")
    verified_badge: bool | None = Field(default=None, alias="verifiedBadge")
    users: list[ProfileUser] | None = None

    model_config = {"populate_by_name": True}


class SearchTagResult(BaseModel):
    """Tag result from search."""

    id: str | None = None
    label: str | None = None
    slug: str | None = None
    event_count: int | None = Field(default=None, alias="event_count")

    model_config = {"populate_by_name": True}


class SearchPagination(BaseModel):
    """Pagination info for search results."""

    has_more: bool | None = Field(default=None, alias="hasMore")
    total_results: int | None = Field(default=None, alias="totalResults")

    model_config = {"populate_by_name": True}


class SearchResults(BaseModel):
    """Search results."""

    events: list[Event] | None = None
    tags: list[SearchTagResult] | None = None
    profiles: list[PublicProfile] | None = None
    pagination: SearchPagination | None = None

    model_config = {"populate_by_name": True}
