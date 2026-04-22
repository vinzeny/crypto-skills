"""Configuration for Polymarket SDK."""

from dataclasses import dataclass, field


@dataclass
class PolymarketConfig:
    """Configuration for Polymarket API connections.

    Attributes:
        clob_url: CLOB API base URL for orders, trades, orderbook
        gamma_url: Gamma API base URL for markets, events, metadata
        data_url: Data API base URL for positions, analytics
        bridge_url: Bridge API base URL for deposits, withdrawals
        ws_url: WebSocket URL for real-time streaming
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts for failed requests
        requests_per_second: Rate limit for API requests
    """

    clob_url: str = "https://clob.polymarket.com"
    gamma_url: str = "https://gamma-api.polymarket.com"
    data_url: str = "https://data-api.polymarket.com"
    bridge_url: str = "https://bridge.polymarket.com"
    ws_url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/"
    timeout: float = 30.0
    max_retries: int = 3
    requests_per_second: float = 10.0

    # Polygon chain ID for EIP-712 signing
    chain_id: int = field(default=137, repr=False)

    @classmethod
    def testnet(cls) -> "PolymarketConfig":
        """Create config for testnet (if available)."""
        # Polymarket doesn't have a public testnet, but this allows future extension
        return cls()
