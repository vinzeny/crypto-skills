"""CLOB order service (L2 authenticated endpoints)."""

from polymarket.models.orders import (
    CancelResponse,
    OpenOrder,
    OrderRequest,
    OrderResponse,
    OrderType,
    SignedOrder,
)
from polymarket.services.base import BaseService


class OrderService(BaseService):
    """Service for order management endpoints (requires L2 authentication)."""

    async def place_order(
        self,
        order: SignedOrder,
        order_type: OrderType = OrderType.GTC,
        post_only: bool = False,
    ) -> OrderResponse:
        """Place a single order.

        Args:
            order: Signed order from OrderBuilder
            order_type: Order type (GTC, GTD, FOK, FAK)
            post_only: If true, order only rests on book

        Returns:
            Order response with status and order ID
        """
        if not self.auth or not self.auth.credentials:
            raise ValueError("L2 authentication required for placing orders")

        body = {
            "order": order.model_dump(by_alias=True),
            "owner": self.auth.credentials.api_key,
            "orderType": order_type.value,
            "postOnly": post_only,
        }

        data = await self._post(
            self.config.clob_url,
            "/order",
            body=body,
            authenticated=True,
        )
        return self._parse(data, OrderResponse)

    async def get_orders(
        self,
        market: str | None = None,
        asset_id: str | None = None,
    ) -> list[OpenOrder]:
        """Get all open orders for the authenticated user.

        Args:
            market: Filter by market condition ID
            asset_id: Filter by token ID

        Returns:
            List of open orders
        """
        data = await self._get(
            self.config.clob_url,
            "/orders",
            params={"market": market, "asset_id": asset_id},
            authenticated=True,
        )
        return self._parse_list(data, OpenOrder)

    async def cancel_order(self, order_id: str) -> CancelResponse:
        """Cancel a specific order by ID.

        Args:
            order_id: ID of the order to cancel

        Returns:
            Cancel response with cancelled order IDs
        """
        data = await self._delete(
            self.config.clob_url,
            "/cancel",
            body={"orderID": order_id},
            authenticated=True,
        )
        return self._parse(data, CancelResponse)

    async def cancel_orders(self, order_ids: list[str]) -> CancelResponse:
        """Cancel multiple orders by ID.

        Args:
            order_ids: List of order IDs to cancel

        Returns:
            Cancel response with cancelled order IDs
        """
        data = await self._delete(
            self.config.clob_url,
            "/cancel-orders",
            body={"orderIDs": order_ids},
            authenticated=True,
        )
        return self._parse(data, CancelResponse)

    async def cancel_all(self) -> CancelResponse:
        """Cancel all open orders for the authenticated user.

        Returns:
            Cancel response with cancelled order IDs
        """
        data = await self._delete(
            self.config.clob_url,
            "/cancel-all",
            authenticated=True,
        )
        return self._parse(data, CancelResponse)

    async def cancel_market_orders(
        self,
        market: str,
        asset_id: str | None = None,
    ) -> CancelResponse:
        """Cancel all orders for a specific market.

        Args:
            market: Market condition ID
            asset_id: Optional token ID filter

        Returns:
            Cancel response with cancelled order IDs
        """
        body = {"market": market}
        if asset_id:
            body["asset_id"] = asset_id

        data = await self._delete(
            self.config.clob_url,
            "/cancel-market-orders",
            body=body,
            authenticated=True,
        )
        return self._parse(data, CancelResponse)
