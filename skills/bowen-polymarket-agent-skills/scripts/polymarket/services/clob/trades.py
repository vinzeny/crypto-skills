"""CLOB trade service (L2 authenticated endpoints)."""

from polymarket.models.orders import Trade
from polymarket.services.base import BaseService


class TradeService(BaseService):
    """Service for trade history endpoints (requires L2 authentication)."""

    async def get_trades(
        self,
        market: str | None = None,
        maker: str | None = None,
        before: int | None = None,
        after: int | None = None,
    ) -> list[Trade]:
        """Get trade history for the authenticated user.

        Args:
            market: Filter by market condition ID
            maker: Filter by maker address
            before: Unix timestamp cutoff (trades before this time)
            after: Unix timestamp cutoff (trades after this time)

        Returns:
            List of trades
        """
        data = await self._get(
            self.config.clob_url,
            "/data/trades",
            params={
                "market": market,
                "maker": maker,
                "before": before,
                "after": after,
            },
            authenticated=True,
        )
        return self._parse_list(data, Trade)
