"""Gamma API service (public endpoints)."""

from typing import Literal

from polymarket.models.markets import (
    Comment,
    Event,
    Market,
    PublicProfile,
    SearchResults,
    Series,
    Tag,
    Team,
)
from polymarket.services.base import BaseService


class GammaService(BaseService):
    """Service for Gamma API endpoints (markets, events, metadata).

    All endpoints are public and do not require authentication.
    """

    # ==================== Markets ====================

    async def list_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        active: bool | None = None,
        closed: bool | None = None,
        order: Literal["volume", "liquidity", "startDate", "endDate"] | None = None,
        ascending: bool = False,
    ) -> list[Market]:
        """Get a list of all available markets.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            active: Filter by active status
            closed: Filter by closed status
            order: Sort order field
            ascending: Sort ascending

        Returns:
            List of markets
        """
        data = await self._get(
            self.config.gamma_url,
            "/markets",
            params={
                "limit": limit,
                "offset": offset,
                "active": active,
                "closed": closed,
                "order": order,
                "ascending": ascending,
            },
        )
        return self._parse_list(data, Market)

    async def get_market(self, condition_id: str) -> Market:
        """Get detailed information about a specific market.

        Args:
            condition_id: Market condition ID

        Returns:
            Market details
        """
        data = await self._get(
            self.config.gamma_url,
            f"/markets/{condition_id}",
        )
        return self._parse(data, Market)

    async def get_market_by_slug(self, slug: str) -> Market:
        """Get a market by its URL slug.

        Args:
            slug: Market URL slug

        Returns:
            Market details
        """
        data = await self._get(
            self.config.gamma_url,
            f"/markets/slug/{slug}",
        )
        return self._parse(data, Market)

    # ==================== Events ====================

    async def list_events(
        self,
        limit: int = 100,
        offset: int = 0,
        active: bool | None = None,
        slug: str | None = None,
    ) -> list[Event]:
        """Get a list of all events.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            active: Filter by active status
            slug: Filter by event slug

        Returns:
            List of events
        """
        data = await self._get(
            self.config.gamma_url,
            "/events",
            params={
                "limit": limit,
                "offset": offset,
                "active": active,
                "slug": slug,
            },
        )
        return self._parse_list(data, Event)

    async def get_event(self, event_id: str) -> Event:
        """Get detailed information about a specific event.

        Args:
            event_id: Event ID

        Returns:
            Event details
        """
        data = await self._get(
            self.config.gamma_url,
            f"/events/{event_id}",
        )
        return self._parse(data, Event)

    async def get_event_by_slug(self, slug: str) -> Event:
        """Get an event by its URL slug.

        Args:
            slug: Event URL slug

        Returns:
            Event details
        """
        data = await self._get(
            self.config.gamma_url,
            f"/events/slug/{slug}",
        )
        return self._parse(data, Event)

    # ==================== Series ====================

    async def list_series(
        self,
        limit: int | None = None,
        offset: int | None = None,
        slug: list[str] | None = None,
        closed: bool | None = None,
        recurrence: str | None = None,
    ) -> list[Series]:
        """Get a list of all series.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            slug: Filter by slugs
            closed: Filter by closed status
            recurrence: Filter by recurrence type

        Returns:
            List of series
        """
        params = {
            "limit": limit,
            "offset": offset,
            "closed": closed,
            "recurrence": recurrence,
        }
        if slug:
            params["slug"] = ",".join(slug)

        data = await self._get(
            self.config.gamma_url,
            "/series",
            params=params,
        )
        return self._parse_list(data, Series)

    async def get_series(self, series_id: str) -> Series:
        """Get detailed information about a specific series.

        Args:
            series_id: Series ID

        Returns:
            Series details
        """
        data = await self._get(
            self.config.gamma_url,
            f"/series/{series_id}",
        )
        return self._parse(data, Series)

    # ==================== Tags ====================

    async def list_tags(
        self,
        limit: int | None = None,
        offset: int | None = None,
        include_template: bool | None = None,
        is_carousel: bool | None = None,
    ) -> list[Tag]:
        """Get a list of all tags.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            include_template: Include template tags
            is_carousel: Filter carousel tags

        Returns:
            List of tags
        """
        data = await self._get(
            self.config.gamma_url,
            "/tags",
            params={
                "limit": limit,
                "offset": offset,
                "include_template": include_template,
                "is_carousel": is_carousel,
            },
        )
        return self._parse_list(data, Tag)

    async def get_tag(self, tag_id: str) -> Tag:
        """Get a specific tag by ID.

        Args:
            tag_id: Tag ID

        Returns:
            Tag details
        """
        data = await self._get(
            self.config.gamma_url,
            f"/tags/{tag_id}",
        )
        return self._parse(data, Tag)

    async def get_tag_by_slug(self, slug: str) -> Tag:
        """Get a specific tag by slug.

        Args:
            slug: Tag slug

        Returns:
            Tag details
        """
        data = await self._get(
            self.config.gamma_url,
            f"/tags/slug/{slug}",
        )
        return self._parse(data, Tag)

    # ==================== Search ====================

    async def search(
        self,
        query: str,
        events_status: str | None = None,
        limit_per_type: int | None = None,
        page: int | None = None,
        events_tag: list[str] | None = None,
        sort: str | None = None,
        ascending: bool | None = None,
        search_tags: bool | None = None,
        search_profiles: bool | None = None,
    ) -> SearchResults:
        """Search across markets, events, and user profiles.

        Args:
            query: Search query
            events_status: Filter event status
            limit_per_type: Max results per type
            page: Page number
            events_tag: Filter by event tags
            sort: Sort field
            ascending: Sort ascending
            search_tags: Include tags in search
            search_profiles: Include profiles in search

        Returns:
            Search results
        """
        params = {
            "q": query,
            "events_status": events_status,
            "limit_per_type": limit_per_type,
            "page": page,
            "sort": sort,
            "ascending": ascending,
            "search_tags": search_tags,
            "search_profiles": search_profiles,
        }
        if events_tag:
            params["events_tag"] = ",".join(events_tag)

        data = await self._get(
            self.config.gamma_url,
            "/public-search",
            params=params,
        )
        return self._parse(data, SearchResults)

    # ==================== Profiles ====================

    async def get_public_profile(self, address: str) -> PublicProfile:
        """Get public profile by wallet address.

        Args:
            address: Wallet address (proxy wallet or user address)

        Returns:
            Public profile
        """
        data = await self._get(
            self.config.gamma_url,
            "/public-profile",
            params={"address": address},
        )
        return self._parse(data, PublicProfile)

    # ==================== Sports ====================

    async def get_sports_metadata(self) -> dict:
        """Get sports metadata information.

        Returns:
            Sports metadata
        """
        return await self._get(self.config.gamma_url, "/sports")

    async def list_teams(
        self,
        limit: int | None = None,
        offset: int | None = None,
        sport: str | None = None,
        league: str | None = None,
    ) -> list[Team]:
        """Get a list of sports teams.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            sport: Filter by sport
            league: Filter by league

        Returns:
            List of teams
        """
        data = await self._get(
            self.config.gamma_url,
            "/teams",
            params={
                "limit": limit,
                "offset": offset,
                "sport": sport,
                "league": league,
            },
        )
        return self._parse_list(data, Team)

    # ==================== Comments ====================

    async def list_comments(
        self,
        market: str | None = None,
        event: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Comment]:
        """Get comments for a market or event.

        Args:
            market: Market condition ID
            event: Event ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of comments
        """
        data = await self._get(
            self.config.gamma_url,
            "/comments",
            params={
                "market": market,
                "event": event,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._parse_list(data, Comment)
