"""Utility functions for Polymarket SDK."""

import secrets
import time
from decimal import ROUND_DOWN, Decimal


# USDC uses 6 decimals on Polygon
USDC_DECIMALS = 6
WEI_PER_USDC = 10**USDC_DECIMALS


def to_wei(amount: Decimal | float | str, decimals: int = USDC_DECIMALS) -> int:
    """Convert a human-readable amount to wei (smallest unit).

    Args:
        amount: Amount in human-readable format (e.g., 100.50 USDC)
        decimals: Number of decimals (default 6 for USDC)

    Returns:
        Amount in wei as integer

    Example:
        >>> to_wei(100.50)
        100500000
        >>> to_wei("0.01")
        10000
    """
    if isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    elif isinstance(amount, str):
        amount = Decimal(amount)

    multiplier = Decimal(10**decimals)
    return int(amount * multiplier)


def from_wei(amount: int | str, decimals: int = USDC_DECIMALS) -> Decimal:
    """Convert wei (smallest unit) to human-readable amount.

    Args:
        amount: Amount in wei
        decimals: Number of decimals (default 6 for USDC)

    Returns:
        Human-readable Decimal amount

    Example:
        >>> from_wei(100500000)
        Decimal('100.5')
    """
    if isinstance(amount, str):
        amount = int(amount)

    divisor = Decimal(10**decimals)
    return Decimal(amount) / divisor


def generate_salt() -> str:
    """Generate a random 256-bit salt for order uniqueness.

    Returns:
        Salt as decimal string (not hex)

    Example:
        >>> salt = generate_salt()
        >>> len(salt) > 0
        True
    """
    # Generate 32 random bytes (256 bits)
    random_bytes = secrets.token_bytes(32)
    # Convert to integer and then to decimal string
    return str(int.from_bytes(random_bytes, byteorder="big"))


def current_timestamp() -> int:
    """Get current Unix timestamp in seconds.

    Returns:
        Current timestamp as integer
    """
    return int(time.time())


def current_timestamp_ms() -> int:
    """Get current Unix timestamp in milliseconds.

    Returns:
        Current timestamp in milliseconds
    """
    return int(time.time() * 1000)


def round_price(price: Decimal | float, tick_size: Decimal | str = "0.01") -> Decimal:
    """Round a price to the nearest tick size.

    Args:
        price: Price to round
        tick_size: Minimum price increment (default 0.01)

    Returns:
        Rounded price as Decimal

    Example:
        >>> round_price(0.567, "0.01")
        Decimal('0.56')
    """
    if isinstance(price, float):
        price = Decimal(str(price))
    if isinstance(tick_size, str):
        tick_size = Decimal(tick_size)

    # Round down to tick size
    return (price / tick_size).quantize(Decimal("1"), rounding=ROUND_DOWN) * tick_size


def calculate_maker_amount(
    price: Decimal, size: Decimal, side: str, decimals: int = USDC_DECIMALS
) -> int:
    """Calculate maker amount in wei for an order.

    For BUY orders: maker pays USDC, amount = price * size
    For SELL orders: maker pays tokens, amount = size

    Args:
        price: Order price (0-1 for binary markets)
        size: Order size in tokens
        side: "BUY" or "SELL"
        decimals: Token decimals

    Returns:
        Maker amount in wei
    """
    if side.upper() == "BUY":
        # Buying tokens: pay price * size in USDC
        return to_wei(price * size, decimals)
    else:
        # Selling tokens: pay size in tokens
        return to_wei(size, decimals)


def calculate_taker_amount(
    price: Decimal, size: Decimal, side: str, decimals: int = USDC_DECIMALS
) -> int:
    """Calculate taker amount in wei for an order.

    For BUY orders: taker receives tokens, amount = size
    For SELL orders: taker receives USDC, amount = price * size

    Args:
        price: Order price (0-1 for binary markets)
        size: Order size in tokens
        side: "BUY" or "SELL"
        decimals: Token decimals

    Returns:
        Taker amount in wei
    """
    if side.upper() == "BUY":
        # Buying tokens: receive size in tokens
        return to_wei(size, decimals)
    else:
        # Selling tokens: receive price * size in USDC
        return to_wei(price * size, decimals)
