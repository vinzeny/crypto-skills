"""Custom exceptions for Polymarket SDK."""

from typing import Any


class PolymarketError(Exception):
    """Base exception for all Polymarket SDK errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(PolymarketError):
    """Authentication failed (L1 or L2)."""

    pass


class RateLimitError(PolymarketError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float = 1.0,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details)
        self.retry_after = retry_after


class OrderError(PolymarketError):
    """Order placement or cancellation failed."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details)
        self.error_code = error_code


class InsufficientBalanceError(OrderError):
    """Insufficient USDC or token balance for order."""

    pass


class InsufficientAllowanceError(OrderError):
    """Insufficient contract allowance for order."""

    pass


class ValidationError(PolymarketError):
    """Request validation failed."""

    pass


class MarketNotFoundError(PolymarketError):
    """Market or event not found."""

    pass


class WebSocketError(PolymarketError):
    """WebSocket connection or subscription error."""

    pass


class ConnectionError(WebSocketError):
    """WebSocket connection failed."""

    pass


class SubscriptionError(WebSocketError):
    """WebSocket subscription failed."""

    pass
