"""Main Polymarket client facade."""

from typing import Any

from polymarket.auth import AuthManager, Credentials
from polymarket.config import PolymarketConfig
from polymarket.http import RateLimitedClient
from polymarket.models.auth import ApiCredentials
from polymarket.models.orders import SignatureType
from polymarket.order_builder import OrderBuilder
from polymarket.services.bridge import BridgeService
from polymarket.services.clob import AccountService, OrderbookService, OrderService, TradeService
from polymarket.services.data import DataService
from polymarket.services.gamma import GammaService
from polymarket.signing import create_signer
from polymarket.websocket.market import MarketStream
from polymarket.websocket.user import UserStream


class PolymarketClient:
    """Unified client for interacting with Polymarket APIs.

    Provides access to all Polymarket services through a single interface:
    - Markets: Market discovery, events, metadata (Gamma API)
    - Orderbook: Order book data, prices (CLOB API - public)
    - Orders: Order placement, cancellation (CLOB API - authenticated)
    - Trades: Trade history (CLOB API - authenticated)
    - Account: Balance, allowance (CLOB API - authenticated)
    - Positions: User positions, analytics (Data API)
    - Bridge: Deposits, withdrawals (Bridge API)
    - WebSocket: Real-time streaming

    Example (public endpoints only):
        >>> async with PolymarketClient() as client:
        ...     markets = await client.markets.list_markets(active=True)
        ...     for market in markets[:5]:
        ...         print(market.question)

    Example (with authentication):
        >>> from polymarket import PolymarketClient, Credentials
        >>> credentials = Credentials(api_key="...", secret="...", passphrase="...")
        >>> async with PolymarketClient(
        ...     private_key="0x...",
        ...     credentials=credentials,
        ... ) as client:
        ...     # Build and place an order
        ...     order = client.order_builder.buy("token_id", 0.55, 100).build()
        ...     result = await client.orders.place_order(order)
        ...     print(f"Order placed: {result.order_id}")
    """

    def __init__(
        self,
        config: PolymarketConfig | None = None,
        private_key: str | None = None,
        credentials: Credentials | None = None,
        signature_type: SignatureType = SignatureType.GNOSIS_SAFE,
    ):
        """Initialize Polymarket client.

        Args:
            config: SDK configuration (uses defaults if not provided)
            private_key: Hex-encoded private key for signing (optional)
            credentials: API credentials for L2 auth (optional)
            signature_type: Signature type for orders (default GNOSIS_SAFE)

        Note:
            - Public endpoints work without any credentials
            - Trading requires both private_key and credentials
            - Use create_api_credentials() to generate credentials from private_key
        """
        self.config = config or PolymarketConfig()
        self._http = RateLimitedClient(self.config)

        # Set up authentication
        self._signer = create_signer(private_key) if private_key else None
        self._auth = AuthManager(
            signer=self._signer,
            credentials=credentials,
            chain_id=self.config.chain_id,
        )
        self._signature_type = signature_type

        # Initialize services
        self._init_services()

    def _init_services(self) -> None:
        """Initialize all service instances."""
        # Public services (no auth required)
        self.markets = GammaService(self._http, self.config, self._auth)
        self.orderbook = OrderbookService(self._http, self.config, self._auth)
        self.positions = DataService(self._http, self.config, self._auth)
        self.bridge = BridgeService(self._http, self.config, self._auth)

        # Authenticated services (require L2 auth)
        self.orders = OrderService(self._http, self.config, self._auth)
        self.trades = TradeService(self._http, self.config, self._auth)
        self.account = AccountService(self._http, self.config, self._auth)

    @property
    def order_builder(self) -> OrderBuilder | None:
        """Get order builder for creating signed orders.

        Returns:
            OrderBuilder if private_key was provided, None otherwise
        """
        if self._signer is None:
            return None
        return OrderBuilder(
            self._signer,
            signature_type=self._signature_type,
            chain_id=self.config.chain_id,
        )

    @property
    def market_stream(self) -> MarketStream:
        """Get market data WebSocket stream (public).

        Returns:
            MarketStream for subscribing to market data
        """
        return MarketStream(self.config)

    @property
    def user_stream(self) -> UserStream | None:
        """Get user event WebSocket stream (authenticated).

        Returns:
            UserStream if credentials are available, None otherwise
        """
        if self._auth.credentials is None:
            return None
        return UserStream(self.config, self._auth.credentials)

    @property
    def address(self) -> str | None:
        """Get the wallet address.

        Returns:
            Wallet address if private_key was provided
        """
        return self._auth.address

    async def create_api_credentials(self) -> Credentials:
        """Create new API credentials using L1 authentication.

        Requires private_key to be set. Each wallet can only have
        one active API key at a time.

        Returns:
            New API credentials

        Raises:
            ValueError: If private_key not provided
        """
        if self._signer is None:
            raise ValueError("private_key required to create API credentials")

        # Make L1 authenticated request
        data = await self.orders._post_l1(
            self.config.clob_url,
            "/auth/api-key",
            nonce=0,
        )

        api_creds = ApiCredentials.model_validate(data)
        credentials = Credentials(
            api_key=api_creds.api_key,
            secret=api_creds.secret,
            passphrase=api_creds.passphrase,
        )

        # Update auth manager with new credentials
        self._auth.set_credentials(credentials)

        return credentials

    async def derive_api_credentials(self, nonce: int = 0) -> Credentials:
        """Derive existing API credentials using L1 authentication.

        Use the same nonce that was used to create the credentials.

        Args:
            nonce: Nonce value used when creating credentials

        Returns:
            Derived API credentials

        Raises:
            ValueError: If private_key not provided
        """
        if self._signer is None:
            raise ValueError("private_key required to derive API credentials")

        # Make L1 authenticated request
        data = await self.orders._get_l1(
            self.config.clob_url,
            "/auth/derive-api-key",
            nonce=nonce,
        )

        api_creds = ApiCredentials.model_validate(data)
        credentials = Credentials(
            api_key=api_creds.api_key,
            secret=api_creds.secret,
            passphrase=api_creds.passphrase,
        )

        # Update auth manager with derived credentials
        self._auth.set_credentials(credentials)

        return credentials

    async def health_check(self) -> bool:
        """Check if the CLOB API is operational.

        Returns:
            True if API is healthy
        """
        try:
            data = await self.orderbook._get(self.config.clob_url, "/ok")
            return data.get("status") == "ok"
        except Exception:
            return False

    async def get_server_time(self) -> int:
        """Get the current server timestamp.

        Returns:
            Unix timestamp in seconds
        """
        data = await self.orderbook._get(self.config.clob_url, "/time")
        return data.get("timestamp", 0)

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> "PolymarketClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        await self.close()
