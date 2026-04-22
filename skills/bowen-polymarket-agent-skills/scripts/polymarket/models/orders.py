"""Order-related models."""

from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class OrderSide(StrEnum):
    """Order side."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    """Order type for time-in-force behavior."""

    GTC = "GTC"  # Good-Til-Cancelled
    GTD = "GTD"  # Good-Til-Date
    FOK = "FOK"  # Fill-Or-Kill
    FAK = "FAK"  # Fill-And-Kill (Immediate-Or-Cancel)


class SignatureType(IntEnum):
    """Signature type for order signing."""

    EOA = 0  # Standard Ethereum wallet (MetaMask)
    POLY_PROXY = 1  # Magic Link email/Google users
    GNOSIS_SAFE = 2  # Gnosis Safe proxy wallet (most common)


class SignedOrder(BaseModel):
    """A signed order ready for submission to the CLOB."""

    salt: str = Field(description="Random salt for order uniqueness")
    maker: str = Field(description="Maker/funder address")
    signer: str = Field(description="Signing address")
    taker: str = Field(description="Taker address (operator)")
    token_id: str = Field(alias="tokenId", description="ERC1155 token ID")
    maker_amount: str = Field(
        alias="makerAmount", description="Maximum amount maker will spend (in wei)"
    )
    taker_amount: str = Field(
        alias="takerAmount", description="Minimum amount taker pays maker (in wei)"
    )
    expiration: str = Field(
        description="Unix expiration timestamp (0 for no expiration)"
    )
    nonce: str = Field(description="Maker's exchange nonce")
    fee_rate_bps: str = Field(alias="feeRateBps", description="Fee rate in basis points")
    side: OrderSide = Field(description="Order side")
    signature_type: SignatureType = Field(
        alias="signatureType", description="Signature type (0=EOA, 1=POLY_PROXY, 2=GNOSIS_SAFE)"
    )
    signature: str = Field(description="Hex-encoded EIP-712 signature")

    model_config = {"populate_by_name": True}


class OrderRequest(BaseModel):
    """Order placement request."""

    order: SignedOrder
    owner: str = Field(description="API key of order owner")
    order_type: OrderType = Field(alias="orderType", description="Order type")
    post_only: bool = Field(
        default=False, alias="postOnly", description="If true, order only rests on book"
    )

    model_config = {"populate_by_name": True}


class OrderResponse(BaseModel):
    """Response from order placement."""

    success: bool = Field(description="Whether the order was accepted")
    error_msg: str | None = Field(
        default=None, alias="errorMsg", description="Error message if unsuccessful"
    )
    order_id: str | None = Field(
        default=None, alias="orderId", description="Unique order identifier"
    )
    order_hashes: list[str] | None = Field(
        default=None, alias="orderHashes", description="Transaction hashes if matched"
    )
    status: Literal["matched", "live", "delayed", "unmatched"] | None = Field(
        default=None, description="Order status after placement"
    )

    model_config = {"populate_by_name": True}


class OpenOrder(BaseModel):
    """An open order on the book."""

    id: str
    status: str
    market: str = Field(description="Market condition ID")
    original_size: str = Field(alias="original_size")
    size_matched: str = Field(alias="size_matched")
    price: str
    side: OrderSide
    outcome: str
    maker_address: str = Field(alias="maker_address")
    owner: str = Field(description="API key")
    asset_id: str = Field(alias="asset_id", description="Token ID")
    expiration: str
    type: str
    created_at: datetime = Field(alias="created_at")

    model_config = {"populate_by_name": True}


class CancelResponse(BaseModel):
    """Response from order cancellation."""

    canceled: list[str] = Field(
        default_factory=list, description="List of cancelled order IDs"
    )
    not_canceled: list[str] = Field(
        default_factory=list, description="List of orders that could not be cancelled"
    )


class Trade(BaseModel):
    """A completed trade."""

    id: str
    taker_order_id: str = Field(alias="taker_order_id")
    market: str
    asset_id: str = Field(alias="asset_id")
    side: OrderSide
    size: str
    fee_rate_bps: str = Field(alias="fee_rate_bps")
    price: str
    status: str
    match_time: datetime = Field(alias="match_time")
    outcome: str
    maker_address: str = Field(alias="maker_address")
    owner: str
    transaction_hash: str | None = Field(default=None, alias="transaction_hash")
    type: Literal["TAKER", "MAKER"]

    model_config = {"populate_by_name": True}
