"""Bridge API service (public endpoints)."""

from polymarket.models.bridge import (
    DepositResponse,
    QuoteRequest,
    QuoteResponse,
    SupportedAssetsResponse,
    TransactionStatusResponse,
)
from polymarket.services.base import BaseService


class BridgeService(BaseService):
    """Service for Bridge API endpoints (deposits, withdrawals).

    All endpoints are public and do not require authentication.
    """

    async def get_supported_assets(self) -> SupportedAssetsResponse:
        """Get all supported chains and tokens for deposits and withdrawals.

        Returns:
            Supported assets response with chain and token information
        """
        data = await self._get(
            self.config.bridge_url,
            "/supported-assets",
        )
        return self._parse(data, SupportedAssetsResponse)

    async def create_deposit_address(self, address: str) -> DepositResponse:
        """Generate unique deposit addresses for depositing assets.

        Args:
            address: Your Polymarket wallet address

        Returns:
            Deposit addresses for EVM, Solana, and Bitcoin networks
        """
        data = await self._post(
            self.config.bridge_url,
            "/deposit",
            body={"address": address},
        )
        return self._parse(data, DepositResponse)

    async def create_withdrawal_address(self, address: str) -> DepositResponse:
        """Generate addresses for withdrawing USDC.e from Polymarket.

        Args:
            address: Destination wallet address

        Returns:
            Withdrawal addresses
        """
        data = await self._post(
            self.config.bridge_url,
            "/withdraw",
            body={"address": address},
        )
        return self._parse(data, DepositResponse)

    async def get_quote(self, request: QuoteRequest) -> QuoteResponse:
        """Get an estimated quote for a deposit or withdrawal.

        Args:
            request: Quote request with chain and token details

        Returns:
            Quote response with fees and estimated output
        """
        data = await self._post(
            self.config.bridge_url,
            "/quote",
            body=request.model_dump(by_alias=True),
        )
        return self._parse(data, QuoteResponse)

    async def get_transaction_status(self, address: str) -> TransactionStatusResponse:
        """Get transaction status for deposits/withdrawals associated with an address.

        Args:
            address: Deposit/withdrawal address (EVM, SVM, or BTC)

        Returns:
            Transaction status response with all associated transactions
        """
        data = await self._get(
            self.config.bridge_url,
            f"/status/{address}",
        )
        return self._parse(data, TransactionStatusResponse)
