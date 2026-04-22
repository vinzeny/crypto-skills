"""Bridge API models."""

from typing import Literal

from pydantic import BaseModel, Field


class TokenInfo(BaseModel):
    """Token information."""

    name: str | None = None
    symbol: str | None = None
    address: str | None = None
    decimals: int | None = None


class SupportedAsset(BaseModel):
    """Supported asset for deposit/withdrawal."""

    chain_id: str | None = Field(default=None, alias="chainId")
    chain_name: str | None = Field(default=None, alias="chainName")
    token: TokenInfo | None = None
    min_checkout_usd: float | None = Field(default=None, alias="minCheckoutUsd")

    model_config = {"populate_by_name": True}


class SupportedAssetsResponse(BaseModel):
    """Supported assets response."""

    supported_assets: list[SupportedAsset] | None = Field(
        default=None, alias="supportedAssets"
    )

    model_config = {"populate_by_name": True}


class DepositAddresses(BaseModel):
    """Deposit/withdrawal addresses."""

    evm: str | None = Field(default=None, description="EVM-compatible deposit address")
    svm: str | None = Field(default=None, description="Solana deposit address")
    btc: str | None = Field(default=None, description="Bitcoin deposit address")


class DepositResponse(BaseModel):
    """Deposit/withdrawal addresses response."""

    address: DepositAddresses | None = None
    note: str | None = None


class QuoteRequest(BaseModel):
    """Bridge quote request."""

    from_amount_base_unit: str = Field(alias="fromAmountBaseUnit")
    from_chain_id: str = Field(alias="fromChainId")
    from_token_address: str = Field(alias="fromTokenAddress")
    recipient_address: str = Field(alias="recipientAddress")
    to_chain_id: str = Field(alias="toChainId")
    to_token_address: str = Field(alias="toTokenAddress")

    model_config = {"populate_by_name": True}


class FeeBreakdown(BaseModel):
    """Fee breakdown in quote."""

    app_fee_label: str | None = Field(default=None, alias="appFeeLabel")
    app_fee_percent: float | None = Field(default=None, alias="appFeePercent")
    app_fee_usd: float | None = Field(default=None, alias="appFeeUsd")
    fill_cost_percent: float | None = Field(default=None, alias="fillCostPercent")
    fill_cost_usd: float | None = Field(default=None, alias="fillCostUsd")
    gas_usd: float | None = Field(default=None, alias="gasUsd")
    max_slippage: float | None = Field(default=None, alias="maxSlippage")
    min_received: float | None = Field(default=None, alias="minReceived")
    swap_impact: float | None = Field(default=None, alias="swapImpact")
    swap_impact_usd: float | None = Field(default=None, alias="swapImpactUsd")
    total_impact: float | None = Field(default=None, alias="totalImpact")
    total_impact_usd: float | None = Field(default=None, alias="totalImpactUsd")

    model_config = {"populate_by_name": True}


class QuoteResponse(BaseModel):
    """Bridge quote response."""

    est_checkout_time_ms: int | None = Field(default=None, alias="estCheckoutTimeMs")
    est_fee_breakdown: FeeBreakdown | None = Field(
        default=None, alias="estFeeBreakdown"
    )
    est_input_usd: float | None = Field(default=None, alias="estInputUsd")
    est_output_usd: float | None = Field(default=None, alias="estOutputUsd")
    est_to_token_base_unit: str | None = Field(
        default=None, alias="estToTokenBaseUnit"
    )
    quote_id: str | None = Field(default=None, alias="quoteId")

    model_config = {"populate_by_name": True}


BridgeStatus = Literal[
    "DEPOSIT_DETECTED",
    "PROCESSING",
    "ORIGIN_TX_CONFIRMED",
    "SUBMITTED",
    "COMPLETED",
    "FAILED",
]


class BridgeTransaction(BaseModel):
    """Bridge transaction."""

    from_chain_id: str | None = Field(default=None, alias="fromChainId")
    from_token_address: str | None = Field(default=None, alias="fromTokenAddress")
    from_amount_base_unit: str | None = Field(
        default=None, alias="fromAmountBaseUnit"
    )
    to_chain_id: str | None = Field(default=None, alias="toChainId")
    to_token_address: str | None = Field(default=None, alias="toTokenAddress")
    status: BridgeStatus | None = None
    tx_hash: str | None = Field(default=None, alias="txHash")
    created_time_ms: float | None = Field(default=None, alias="createdTimeMs")

    model_config = {"populate_by_name": True}


class TransactionStatusResponse(BaseModel):
    """Transaction status response."""

    transactions: list[BridgeTransaction] | None = None
