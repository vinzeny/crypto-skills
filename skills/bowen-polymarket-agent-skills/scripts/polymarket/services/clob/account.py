"""CLOB account service (L2 authenticated endpoints)."""

from typing import Literal

from polymarket.models.orderbook import BalanceAllowance
from polymarket.services.base import BaseService


class AccountService(BaseService):
    """Service for account-related endpoints (requires L2 authentication)."""

    async def get_balance_allowance(
        self,
        asset_type: Literal["COLLATERAL", "CONDITIONAL"],
        token_id: str | None = None,
        signature_type: int | None = None,
    ) -> BalanceAllowance:
        """Get the user's balance and contract allowance.

        Args:
            asset_type: Asset type (COLLATERAL for USDC, CONDITIONAL for tokens)
            token_id: Token ID (required for CONDITIONAL)
            signature_type: Signature type (0=EOA, 1=POLY_PROXY, 2=GNOSIS_SAFE)

        Returns:
            Balance and allowance information
        """
        data = await self._get(
            self.config.clob_url,
            "/balance-allowance",
            params={
                "asset_type": asset_type,
                "token_id": token_id,
                "signature_type": signature_type,
            },
            authenticated=True,
        )
        return self._parse(data, BalanceAllowance)
