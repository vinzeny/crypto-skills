"""CLOB orderbook service (public endpoints)."""

from typing import Literal

from polymarket.models.orderbook import (
    OrderBookSummary,
    PriceHistoryResponse,
    SpreadInfo,
)
from polymarket.services.base import BaseService


class OrderbookService(BaseService):
    """Service for orderbook-related endpoints (public, no auth required)."""

    async def get_book(self, token_id: str) -> OrderBookSummary:
        """Get the order book summary for a specific token.

        Args:
            token_id: ERC1155 token ID

        Returns:
            Order book summary with bids and asks
        """
        data = await self._get(
            self.config.clob_url,
            "/book",
            params={"token_id": token_id},
        )
        return self._parse(data, OrderBookSummary)

    async def get_books(self, token_ids: list[str]) -> list[OrderBookSummary]:
        """Get order book summaries for multiple tokens.

        Args:
            token_ids: List of ERC1155 token IDs

        Returns:
            List of order book summaries
        """
        data = await self._get(
            self.config.clob_url,
            "/books",
            params={"token_ids": ",".join(token_ids)},
        )
        return self._parse_list(data, OrderBookSummary)

    async def get_price(
        self,
        token_id: str,
        side: Literal["BUY", "SELL"],
    ) -> str:
        """Get the current market price for a token.

        Args:
            token_id: ERC1155 token ID
            side: Order side (BUY or SELL)

        Returns:
            Current market price as string
        """
        data = await self._get(
            self.config.clob_url,
            "/price",
            params={"token_id": token_id, "side": side},
        )
        return data.get("price", "0")

    async def get_prices(self) -> dict[str, dict[str, str]]:
        """Get market prices for multiple tokens and sides.

        Returns:
            Map of token_id to {"BUY": price, "SELL": price}
        """
        data = await self._get(
            self.config.clob_url,
            "/prices",
        )
        return data

    async def get_midpoint(self, token_id: str) -> str:
        """Get the midpoint price between best bid and ask.

        Args:
            token_id: ERC1155 token ID

        Returns:
            Midpoint price as string
        """
        data = await self._get(
            self.config.clob_url,
            "/midpoint",
            params={"token_id": token_id},
        )
        return data.get("mid", "0")

    async def get_spread(self, token_id: str) -> SpreadInfo:
        """Get the bid-ask spread for a token.

        Args:
            token_id: ERC1155 token ID

        Returns:
            Spread information
        """
        data = await self._get(
            self.config.clob_url,
            "/spread",
            params={"token_id": token_id},
        )
        return self._parse(data, SpreadInfo)

    async def get_tick_size(self, token_id: str) -> dict[str, str]:
        """Get the minimum tick size for a token.

        Args:
            token_id: ERC1155 token ID

        Returns:
            Dict with minimum_tick_size and minimum_order_size
        """
        data = await self._get(
            self.config.clob_url,
            "/tick-size",
            params={"token_id": token_id},
        )
        return data

    async def get_neg_risk(self, token_id: str) -> bool:
        """Check if a market uses negative risk.

        Args:
            token_id: ERC1155 token ID

        Returns:
            True if negative risk market
        """
        data = await self._get(
            self.config.clob_url,
            "/neg-risk",
            params={"token_id": token_id},
        )
        return data.get("neg_risk", False)

    async def get_price_history(
        self,
        market: str,
        start_ts: float | None = None,
        end_ts: float | None = None,
        interval: Literal["1m", "1w", "1d", "6h", "1h", "max"] | None = None,
        fidelity: int | None = None,
    ) -> PriceHistoryResponse:
        """Get historical price data for a market token.

        Args:
            market: CLOB token ID
            start_ts: Start time (Unix timestamp UTC)
            end_ts: End time (Unix timestamp UTC)
            interval: Duration ending at current time (mutually exclusive with start_ts/end_ts)
            fidelity: Resolution in minutes

        Returns:
            Price history response
        """
        data = await self._get(
            self.config.clob_url,
            "/prices-history",
            params={
                "market": market,
                "startTs": start_ts,
                "endTs": end_ts,
                "interval": interval,
                "fidelity": fidelity,
            },
        )
        return self._parse(data, PriceHistoryResponse)
