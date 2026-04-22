"""EIP-712 signing for Polymarket orders and authentication."""

from typing import Any

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount

from polymarket.models.orders import SignatureType


# EIP-712 Domain for Polymarket CLOB
CLOB_DOMAIN = {
    "name": "Polymarket CTF Exchange",
    "version": "1",
    "chainId": 137,  # Polygon
}

# Operator/taker address for CLOB orders
CLOB_OPERATOR = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

# Conditional Tokens Framework (CTF) Exchange address
CTF_EXCHANGE = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

# Neg Risk CTF Exchange address
NEG_RISK_CTF_EXCHANGE = "0xC5d563A36AE78145C45a50134d48A1215220f80a"


class EIP712Signer:
    """Handle EIP-712 typed data signing for Polymarket."""

    def __init__(self, chain_id: int = 137):
        """Initialize signer.

        Args:
            chain_id: Polygon chain ID (137 for mainnet)
        """
        self.chain_id = chain_id

    def sign_order(
        self,
        signer: LocalAccount,
        salt: str,
        maker: str,
        taker: str,
        token_id: str,
        maker_amount: str,
        taker_amount: str,
        expiration: str,
        nonce: str,
        fee_rate_bps: str,
        side: int,  # 0 = BUY, 1 = SELL
        signature_type: SignatureType,
        neg_risk: bool = False,
    ) -> str:
        """Sign an order using EIP-712.

        Args:
            signer: Ethereum account for signing
            salt: Random salt for order uniqueness
            maker: Maker/funder address
            taker: Taker address (operator)
            token_id: ERC1155 token ID
            maker_amount: Amount maker will spend (in wei)
            taker_amount: Amount taker pays maker (in wei)
            expiration: Unix expiration timestamp
            nonce: Maker's exchange nonce
            fee_rate_bps: Fee rate in basis points
            side: Order side (0=BUY, 1=SELL)
            signature_type: Signature type enum
            neg_risk: Whether this is a negative risk market

        Returns:
            Hex-encoded EIP-712 signature
        """
        exchange = NEG_RISK_CTF_EXCHANGE if neg_risk else CTF_EXCHANGE

        domain = {
            "name": "Polymarket CTF Exchange",
            "version": "1",
            "chainId": self.chain_id,
            "verifyingContract": exchange,
        }

        # Order type for EIP-712
        types = {
            "Order": [
                {"name": "salt", "type": "uint256"},
                {"name": "maker", "type": "address"},
                {"name": "signer", "type": "address"},
                {"name": "taker", "type": "address"},
                {"name": "tokenId", "type": "uint256"},
                {"name": "makerAmount", "type": "uint256"},
                {"name": "takerAmount", "type": "uint256"},
                {"name": "expiration", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "feeRateBps", "type": "uint256"},
                {"name": "side", "type": "uint8"},
                {"name": "signatureType", "type": "uint8"},
            ],
        }

        message = {
            "salt": int(salt),
            "maker": maker,
            "signer": signer.address,
            "taker": taker,
            "tokenId": int(token_id),
            "makerAmount": int(maker_amount),
            "takerAmount": int(taker_amount),
            "expiration": int(expiration),
            "nonce": int(nonce),
            "feeRateBps": int(fee_rate_bps),
            "side": side,
            "signatureType": int(signature_type),
        }

        # Create typed data
        typed_data = {
            "types": types,
            "primaryType": "Order",
            "domain": domain,
            "message": message,
        }

        # Sign
        signable = encode_typed_data(full_message=typed_data)
        signed = signer.sign_message(signable)

        return signed.signature.hex()

    def sign_l1_auth(
        self,
        signer: LocalAccount,
        timestamp: int,
        nonce: int = 0,
    ) -> str:
        """Sign L1 authentication message using EIP-712.

        Args:
            signer: Ethereum account for signing
            timestamp: Current Unix timestamp in seconds
            nonce: Nonce value (default 0)

        Returns:
            Hex-encoded EIP-712 signature
        """
        domain = {
            "name": "ClobAuthDomain",
            "version": "1",
            "chainId": self.chain_id,
        }

        types = {
            "ClobAuth": [
                {"name": "address", "type": "address"},
                {"name": "timestamp", "type": "string"},
                {"name": "nonce", "type": "uint256"},
                {"name": "message", "type": "string"},
            ],
        }

        message = {
            "address": signer.address,
            "timestamp": str(timestamp),
            "nonce": nonce,
            "message": "This message attests that I control the given wallet",
        }

        typed_data = {
            "types": types,
            "primaryType": "ClobAuth",
            "domain": domain,
            "message": message,
        }

        signable = encode_typed_data(full_message=typed_data)
        signed = signer.sign_message(signable)

        return signed.signature.hex()


def create_signer(private_key: str) -> LocalAccount:
    """Create a signer from a private key.

    Args:
        private_key: Hex-encoded private key (with or without 0x prefix)

    Returns:
        LocalAccount for signing
    """
    if not private_key.startswith("0x"):
        private_key = f"0x{private_key}"
    return Account.from_key(private_key)
