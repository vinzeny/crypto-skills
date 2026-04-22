"""L1 and L2 authentication for Polymarket API."""

import base64
import hashlib
import hmac
import time
from dataclasses import dataclass

from eth_account.signers.local import LocalAccount

from polymarket.signing import EIP712Signer


@dataclass
class Credentials:
    """API credentials for L2 authentication."""

    api_key: str
    secret: str
    passphrase: str


class L1Authenticator:
    """L1 (EIP-712) authentication for creating/deriving API keys.

    L1 auth requires a wallet signature and is used for:
    - Creating new API credentials
    - Deriving existing API credentials
    """

    def __init__(self, signer: LocalAccount, chain_id: int = 137):
        """Initialize L1 authenticator.

        Args:
            signer: Ethereum account for signing
            chain_id: Polygon chain ID
        """
        self.signer = signer
        self.eip712 = EIP712Signer(chain_id)

    def build_headers(self, nonce: int = 0) -> dict[str, str]:
        """Build L1 authentication headers.

        Args:
            nonce: Nonce value (default 0). Use the same nonce to derive
                   existing credentials.

        Returns:
            Dictionary of headers for L1 authenticated requests
        """
        timestamp = int(time.time())
        signature = self.eip712.sign_l1_auth(self.signer, timestamp, nonce)

        return {
            "POLY_ADDRESS": self.signer.address,
            "POLY_SIGNATURE": signature,
            "POLY_TIMESTAMP": str(timestamp),
            "POLY_NONCE": str(nonce),
        }


class L2Authenticator:
    """L2 (HMAC-SHA256) authentication for trading endpoints.

    L2 auth uses API credentials and is used for:
    - Placing orders
    - Cancelling orders
    - Getting trade history
    - Balance/allowance queries
    """

    def __init__(self, credentials: Credentials, address: str):
        """Initialize L2 authenticator.

        Args:
            credentials: API credentials from L1 authentication
            address: Polygon wallet address
        """
        self.credentials = credentials
        self.address = address

    def build_headers(
        self,
        method: str,
        path: str,
        body: str = "",
    ) -> dict[str, str]:
        """Build L2 authentication headers.

        Args:
            method: HTTP method (GET, POST, DELETE)
            path: Request path (e.g., "/order")
            body: Request body as JSON string (empty for GET)

        Returns:
            Dictionary of headers for L2 authenticated requests
        """
        timestamp = str(int(time.time()))

        # Create signature message: timestamp + method + path + body
        message = timestamp + method.upper() + path + body

        # HMAC-SHA256 signature
        secret_bytes = base64.urlsafe_b64decode(self.credentials.secret)
        signature = hmac.new(
            secret_bytes,
            message.encode("utf-8"),
            hashlib.sha256,
        )
        signature_b64 = base64.urlsafe_b64encode(signature.digest()).decode("utf-8")

        return {
            "POLY_ADDRESS": self.address,
            "POLY_SIGNATURE": signature_b64,
            "POLY_TIMESTAMP": timestamp,
            "POLY_API_KEY": self.credentials.api_key,
            "POLY_PASSPHRASE": self.credentials.passphrase,
        }


class AuthManager:
    """Manages both L1 and L2 authentication."""

    def __init__(
        self,
        signer: LocalAccount | None = None,
        credentials: Credentials | None = None,
        chain_id: int = 137,
    ):
        """Initialize auth manager.

        Args:
            signer: Ethereum account for L1 auth and order signing
            credentials: API credentials for L2 auth
            chain_id: Polygon chain ID
        """
        self.signer = signer
        self.credentials = credentials
        self.chain_id = chain_id

        self._l1: L1Authenticator | None = None
        self._l2: L2Authenticator | None = None

    @property
    def l1(self) -> L1Authenticator:
        """Get L1 authenticator (requires signer)."""
        if self._l1 is None:
            if self.signer is None:
                raise ValueError("Signer required for L1 authentication")
            self._l1 = L1Authenticator(self.signer, self.chain_id)
        return self._l1

    @property
    def l2(self) -> L2Authenticator:
        """Get L2 authenticator (requires credentials)."""
        if self._l2 is None:
            if self.credentials is None:
                raise ValueError("Credentials required for L2 authentication")
            if self.signer is None:
                raise ValueError("Signer required for L2 authentication (address)")
            self._l2 = L2Authenticator(self.credentials, self.signer.address)
        return self._l2

    @property
    def address(self) -> str | None:
        """Get the wallet address."""
        return self.signer.address if self.signer else None

    def set_credentials(self, credentials: Credentials) -> None:
        """Set API credentials.

        Args:
            credentials: API credentials from L1 authentication
        """
        self.credentials = credentials
        self._l2 = None  # Reset L2 authenticator
