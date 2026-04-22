"""Data API service (public endpoints)."""

from typing import Literal

from polymarket.models.positions import (
    Activity,
    ActivityType,
    BuilderLeaderboardEntry,
    ClosedPosition,
    Holder,
    LeaderboardEntry,
    LiveVolume,
    OpenInterestItem,
    Position,
)
from polymarket.services.base import BaseService


class DataService(BaseService):
    """Service for Data API endpoints (positions, analytics, leaderboards).

    All endpoints are public and do not require authentication.
    """

    # ==================== Positions ====================

    async def get_positions(
        self,
        user: str,
        market: str | None = None,
        size_threshold: float | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Position]:
        """Get current positions for a user.

        Args:
            user: User wallet address
            market: Filter by market ID
            size_threshold: Minimum position size
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of positions
        """
        data = await self._get(
            self.config.data_url,
            "/positions",
            params={
                "user": user,
                "market": market,
                "sizeThreshold": size_threshold,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._parse_list(data, Position)

    async def get_closed_positions(
        self,
        user: str,
        market: str | None = None,
        title: str | None = None,
        event_id: str | None = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: Literal[
            "REALIZEDPNL", "TITLE", "PRICE", "AVGPRICE", "TIMESTAMP"
        ] = "REALIZEDPNL",
        sort_direction: Literal["ASC", "DESC"] = "DESC",
    ) -> list[ClosedPosition]:
        """Get closed positions for a user.

        Args:
            user: User wallet address
            market: Comma-separated condition IDs
            title: Filter by market title
            event_id: Comma-separated event IDs
            limit: Maximum number of results
            offset: Offset for pagination
            sort_by: Sort field
            sort_direction: Sort direction

        Returns:
            List of closed positions
        """
        data = await self._get(
            self.config.data_url,
            "/closed-positions",
            params={
                "user": user,
                "market": market,
                "title": title,
                "eventId": event_id,
                "limit": limit,
                "offset": offset,
                "sortBy": sort_by,
                "sortDirection": sort_direction,
            },
        )
        return self._parse_list(data, ClosedPosition)

    async def get_position_value(self, user: str) -> float:
        """Get total value of a user's positions.

        Args:
            user: User wallet address

        Returns:
            Total position value in USDC
        """
        data = await self._get(
            self.config.data_url,
            "/value",
            params={"user": user},
        )
        return data.get("value", 0.0)

    # ==================== Activity ====================

    async def get_activity(
        self,
        user: str,
        market: str | None = None,
        event_id: str | None = None,
        activity_type: list[ActivityType] | None = None,
        start: int | None = None,
        end: int | None = None,
        sort_by: Literal["TIMESTAMP", "TOKENS", "CASH"] = "TIMESTAMP",
        sort_direction: Literal["ASC", "DESC"] = "DESC",
        side: Literal["BUY", "SELL"] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Activity]:
        """Get on-chain activity for a user.

        Args:
            user: User wallet address
            market: Comma-separated condition IDs
            event_id: Comma-separated event IDs
            activity_type: Activity types filter
            start: Start timestamp
            end: End timestamp
            sort_by: Sort field
            sort_direction: Sort direction
            side: Filter by side
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of activity items
        """
        params = {
            "user": user,
            "market": market,
            "eventId": event_id,
            "start": start,
            "end": end,
            "sortBy": sort_by,
            "sortDirection": sort_direction,
            "side": side,
            "limit": limit,
            "offset": offset,
        }
        if activity_type:
            params["type"] = ",".join(t.value for t in activity_type)

        data = await self._get(
            self.config.data_url,
            "/activity",
            params=params,
        )
        return self._parse_list(data, Activity)

    # ==================== Leaderboards ====================

    async def get_leaderboard(
        self,
        time_period: Literal["DAY", "WEEK", "MONTH", "ALL"] = "DAY",
        limit: int = 25,
        offset: int = 0,
    ) -> list[LeaderboardEntry]:
        """Get trader leaderboard rankings.

        Args:
            time_period: Time period for rankings
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of leaderboard entries
        """
        data = await self._get(
            self.config.data_url,
            "/v1/leaderboard",
            params={
                "timePeriod": time_period,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._parse_list(data, LeaderboardEntry)

    async def get_builder_leaderboard(
        self,
        time_period: Literal["DAY", "WEEK", "MONTH", "ALL"] = "DAY",
        limit: int = 25,
        offset: int = 0,
    ) -> list[BuilderLeaderboardEntry]:
        """Get builder leaderboard rankings.

        Args:
            time_period: Time period for rankings
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of builder leaderboard entries
        """
        data = await self._get(
            self.config.data_url,
            "/v1/builders/leaderboard",
            params={
                "timePeriod": time_period,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._parse_list(data, BuilderLeaderboardEntry)

    # ==================== Analytics ====================

    async def get_open_interest(
        self,
        market: str | None = None,
    ) -> list[OpenInterestItem]:
        """Get open interest for markets.

        Args:
            market: Comma-separated condition IDs

        Returns:
            List of open interest items
        """
        data = await self._get(
            self.config.data_url,
            "/oi",
            params={"market": market},
        )
        return self._parse_list(data, OpenInterestItem)

    async def get_live_volume(self, event_id: int) -> LiveVolume:
        """Get live trading volume for an event.

        Args:
            event_id: Event ID

        Returns:
            Live volume data
        """
        data = await self._get(
            self.config.data_url,
            "/live-volume",
            params={"id": event_id},
        )
        return self._parse(data, LiveVolume)

    async def get_top_holders(
        self,
        market: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Holder]:
        """Get top token holders for a market.

        Args:
            market: Condition ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of top holders
        """
        data = await self._get(
            self.config.data_url,
            "/holders",
            params={
                "market": market,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._parse_list(data, Holder)

    async def get_markets_traded(self, user: str) -> int:
        """Get total number of markets a user has traded.

        Args:
            user: User wallet address

        Returns:
            Number of markets traded
        """
        data = await self._get(
            self.config.data_url,
            "/traded",
            params={"user": user},
        )
        return data.get("count", 0)
