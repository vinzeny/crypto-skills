"""Fluent order builder for Polymarket orders."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Literal

from eth_account.signers.local import LocalAccount

from polymarket.models.orders import OrderSide, OrderType, SignatureType, SignedOrder
from polymarket.signing import CLOB_OPERATOR, EIP712Signer
from polymarket.utils import (
    calculate_maker_amount,
    calculate_taker_amount,
    current_timestamp,
    generate_salt,
    round_price,
)


@dataclass
class OrderParams:
    """Internal order parameters."""

    token_id: str | None = None
    price: Decimal | None = None
    size: Decimal | None = None
    side: OrderSide | None = None
    expiration: int = 0  # 0 = no expiration
    nonce: int = 0
    fee_rate_bps: int = 0
    tick_size: Decimal = field(default_factory=lambda: Decimal("0.01"))
    neg_risk: bool = False


class OrderBuilder:
    """Fluent builder for creating signed Polymarket orders.

    Example:
        >>> from polymarket.signing import create_signer
        >>> signer = create_signer("0x...")
        >>> builder = OrderBuilder(signer)
        >>> order = (
        ...     builder
        ...     .buy("71321045...", price=0.55, size=100)
        ...     .with_tick_size("0.01")
        ...     .build()
        ... )
    """

    def __init__(
        self,
        signer: LocalAccount,
        signature_type: SignatureType = SignatureType.GNOSIS_SAFE,
        chain_id: int = 137,
    ):
        """Initialize order builder.

        Args:
            signer: Ethereum account for signing orders
            signature_type: Signature type (default GNOSIS_SAFE)
            chain_id: Polygon chain ID
        """
        self.signer = signer
        self.signature_type = signature_type
        self.eip712 = EIP712Signer(chain_id)
        self._params = OrderParams()

    def _reset(self) -> "OrderBuilder":
        """Reset order parameters for building another order."""
        self._params = OrderParams()
        return self

    def buy(
        self,
        token_id: str,
        price: Decimal | float | str,
        size: Decimal | float | str,
    ) -> "OrderBuilder":
        """Configure a buy order.

        Args:
            token_id: ERC1155 token ID for the outcome
            price: Price per share (0-1 for binary markets)
            size: Number of shares to buy

        Returns:
            Self for chaining
        """
        self._params.token_id = token_id
        self._params.price = Decimal(str(price))
        self._params.size = Decimal(str(size))
        self._params.side = OrderSide.BUY
        return self

    def sell(
        self,
        token_id: str,
        price: Decimal | float | str,
        size: Decimal | float | str,
    ) -> "OrderBuilder":
        """Configure a sell order.

        Args:
            token_id: ERC1155 token ID for the outcome
            price: Price per share (0-1 for binary markets)
            size: Number of shares to sell

        Returns:
            Self for chaining
        """
        self._params.token_id = token_id
        self._params.price = Decimal(str(price))
        self._params.size = Decimal(str(size))
        self._params.side = OrderSide.SELL
        return self

    def with_expiration(self, expires_at: datetime | int) -> "OrderBuilder":
        """Set order expiration (for GTD orders).

        Args:
            expires_at: Expiration as datetime or Unix timestamp

        Returns:
            Self for chaining
        """
        if isinstance(expires_at, datetime):
            self._params.expiration = int(expires_at.timestamp())
        else:
            self._params.expiration = expires_at
        return self

    def with_nonce(self, nonce: int) -> "OrderBuilder":
        """Set order nonce.

        Args:
            nonce: Nonce value (get from exchange)

        Returns:
            Self for chaining
        """
        self._params.nonce = nonce
        return self

    def with_fee_rate(self, fee_rate_bps: int) -> "OrderBuilder":
        """Set fee rate in basis points.

        Args:
            fee_rate_bps: Fee rate (100 = 1%)

        Returns:
            Self for chaining
        """
        self._params.fee_rate_bps = fee_rate_bps
        return self

    def with_tick_size(self, tick_size: Decimal | str) -> "OrderBuilder":
        """Set minimum tick size for price rounding.

        Args:
            tick_size: Minimum price increment (e.g., "0.01")

        Returns:
            Self for chaining
        """
        self._params.tick_size = Decimal(str(tick_size))
        return self

    def with_neg_risk(self, neg_risk: bool = True) -> "OrderBuilder":
        """Mark as negative risk market.

        Args:
            neg_risk: Whether this is a negative risk market

        Returns:
            Self for chaining
        """
        self._params.neg_risk = neg_risk
        return self

    def build(self) -> SignedOrder:
        """Build and sign the order.

        Returns:
            Signed order ready for submission

        Raises:
            ValueError: If required parameters are missing
        """
        params = self._params

        # Validate required fields
        if params.token_id is None:
            raise ValueError("token_id is required")
        if params.price is None:
            raise ValueError("price is required")
        if params.size is None:
            raise ValueError("size is required")
        if params.side is None:
            raise ValueError("side is required (use buy() or sell())")

        # Round price to tick size
        price = round_price(params.price, params.tick_size)

        # Calculate amounts
        maker_amount = calculate_maker_amount(price, params.size, params.side)
        taker_amount = calculate_taker_amount(price, params.size, params.side)

        # Generate salt
        salt = generate_salt()

        # Convert side to int for signing
        side_int = 0 if params.side == OrderSide.BUY else 1

        # Sign the order
        signature = self.eip712.sign_order(
            signer=self.signer,
            salt=salt,
            maker=self.signer.address,
            taker=CLOB_OPERATOR,
            token_id=params.token_id,
            maker_amount=str(maker_amount),
            taker_amount=str(taker_amount),
            expiration=str(params.expiration),
            nonce=str(params.nonce),
            fee_rate_bps=str(params.fee_rate_bps),
            side=side_int,
            signature_type=self.signature_type,
            neg_risk=params.neg_risk,
        )

        # Build signed order
        order = SignedOrder(
            salt=salt,
            maker=self.signer.address,
            signer=self.signer.address,
            taker=CLOB_OPERATOR,
            token_id=params.token_id,
            maker_amount=str(maker_amount),
            taker_amount=str(taker_amount),
            expiration=str(params.expiration),
            nonce=str(params.nonce),
            fee_rate_bps=str(params.fee_rate_bps),
            side=params.side,
            signature_type=self.signature_type,
            signature=signature,
        )

        # Reset for next order
        self._reset()

        return order

    def build_request(
        self,
        order_type: OrderType = OrderType.GTC,
        post_only: bool = False,
    ) -> dict:
        """Build a complete order request for the API.

        Args:
            order_type: Order type (GTC, GTD, FOK, FAK)
            post_only: If true, order only rests on book

        Returns:
            Dictionary ready to POST to /order endpoint
        """
        order = self.build()

        return {
            "order": order.model_dump(by_alias=True),
            "owner": "",  # Will be set by the service with API key
            "orderType": order_type.value,
            "postOnly": post_only,
        }
