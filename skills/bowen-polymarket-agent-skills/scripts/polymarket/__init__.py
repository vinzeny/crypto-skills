"""Polymarket Python SDK.

A comprehensive async SDK for interacting with the Polymarket prediction market platform.

Example:
    >>> from polymarket import PolymarketClient
    >>> async with PolymarketClient() as client:
    ...     markets = await client.markets.list_markets(active=True, limit=10)
    ...     for market in markets:
    ...         print(f"{market.question}: {market.outcomes}")
"""

from polymarket.config import PolymarketConfig
from polymarket.exceptions import (
    AuthenticationError,
    ConnectionError,
    InsufficientAllowanceError,
    InsufficientBalanceError,
    MarketNotFoundError,
    OrderError,
    PolymarketError,
    RateLimitError,
    SubscriptionError,
    ValidationError,
    WebSocketError,
)

__version__ = "0.1.0"

__all__ = [
    # Main client (imported lazily to avoid circular imports)
    "PolymarketClient",
    # Configuration
    "PolymarketConfig",
    # Exceptions
    "PolymarketError",
    "AuthenticationError",
    "RateLimitError",
    "OrderError",
    "InsufficientBalanceError",
    "InsufficientAllowanceError",
    "ValidationError",
    "MarketNotFoundError",
    "WebSocketError",
    "ConnectionError",
    "SubscriptionError",
]


def __getattr__(name: str):
    """Lazy import for PolymarketClient to avoid circular imports."""
    if name == "PolymarketClient":
        from polymarket.client import PolymarketClient

        return PolymarketClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
