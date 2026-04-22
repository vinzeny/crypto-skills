# Order Placement Guide

Complete workflow for placing orders on Polymarket via the CLOB API, covering pre-placement validation, order creation, submission, and response handling.

**Covers:** CLOB-01 (Detailed order placement)

## Pre-Placement Checklist

Before placing any order, verify these requirements:

| Requirement | How to Check | Why It Matters |
|-------------|--------------|----------------|
| Authenticated client | `client.set_api_creds()` called | Orders require L2 authentication |
| Token ID obtained | From Gamma API `clobTokenIds` | Identifies which outcome to trade |
| Tick size known | `client.get_tick_size(token_id)` | Price must align with tick size |
| Sufficient balance | USDC.e for BUY, shares for SELL | Order will fail without funds |

### Quick Verification

```python
def verify_ready_to_trade(client, token_id: str, side: str, size: float):
    """Verify all requirements before placing an order.

    Returns True if ready, raises exception with details if not.
    """
    # 1. Check client has credentials (try authenticated call)
    try:
        client.get_orders()
    except Exception as e:
        raise ValueError(f"Client not authenticated: {e}")

    # 2. Verify token exists and get tick size
    try:
        tick_size = client.get_tick_size(token_id)
    except Exception as e:
        raise ValueError(f"Invalid token_id: {e}")

    # 3. Check market liquidity
    book = client.get_order_book(token_id)
    if side == "BUY" and not book.get("asks"):
        print("Warning: No asks in orderbook, may not fill immediately")
    elif side == "SELL" and not book.get("bids"):
        print("Warning: No bids in orderbook, may not fill immediately")

    return True

# Usage
verify_ready_to_trade(client, token_id, "BUY", 100.0)
```

## Getting Market Context

Always check market conditions before placing orders:

```python
def get_market_context(client, token_id: str):
    """Get complete market context before order placement.

    Returns dict with tick_size, midpoint, spread, and book depth.
    """
    tick_size = float(client.get_tick_size(token_id))
    midpoint = float(client.get_midpoint(token_id))
    book = client.get_order_book(token_id)

    best_bid = float(book['bids'][0]['price']) if book.get('bids') else None
    best_ask = float(book['asks'][0]['price']) if book.get('asks') else None

    bid_depth = sum(float(b['size']) for b in book.get('bids', []))
    ask_depth = sum(float(a['size']) for a in book.get('asks', []))

    spread = (best_ask - best_bid) if (best_ask and best_bid) else None

    return {
        "tick_size": tick_size,
        "midpoint": midpoint,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "bid_depth": bid_depth,
        "ask_depth": ask_depth
    }

# Usage
context = get_market_context(client, token_id)
print(f"Tick size: {context['tick_size']}")
print(f"Midpoint: {context['midpoint']}")
print(f"Best bid: {context['best_bid']}")
print(f"Best ask: {context['best_ask']}")
print(f"Spread: {context['spread']}")
print(f"Bid depth: {context['bid_depth']} shares")
print(f"Ask depth: {context['ask_depth']} shares")
```

## Complete Order Placement Flow

### Step-by-Step Process

```
1. Get market context      --> tick_size, book depth
2. Validate price          --> align to tick size
3. Build OrderArgs         --> price, size, side, token_id
4. Sign the order          --> client.create_order()
5. Post to CLOB            --> client.post_order()
6. Handle response         --> check success, status, fills
```

### Full Implementation

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

def place_limit_order(
    client: ClobClient,
    token_id: str,
    price: float,
    size: float,
    side: str,
    order_type: OrderType = OrderType.GTC
) -> dict:
    """Place a limit order with full validation.

    Args:
        client: Authenticated ClobClient
        token_id: Token to trade (from clobTokenIds)
        price: Limit price (0.01 to 0.99)
        size: Number of shares
        side: "BUY" or "SELL"
        order_type: GTC, GTD, FOK, or FAK

    Returns:
        Order response dict with order_id and status
    """
    # Step 1: Get tick size and validate price
    tick_size = float(client.get_tick_size(token_id))
    validated_price = round(price / tick_size) * tick_size

    if validated_price != price:
        print(f"Price adjusted: {price} -> {validated_price} (tick size: {tick_size})")

    # Step 2: Build order arguments
    order_args = OrderArgs(
        price=validated_price,
        size=size,
        side=BUY if side == "BUY" else SELL,
        token_id=token_id
    )

    # Step 3: Sign the order
    signed_order = client.create_order(order_args)

    # Step 4: Post to CLOB
    response = client.post_order(signed_order, order_type)

    # Step 5: Process response
    if response.get("success"):
        order_id = response.get("orderID") or response.get("orderId")
        status = response.get("status", "unknown")
        size_matched = response.get("size_matched", 0)

        print(f"Order placed successfully")
        print(f"  Order ID: {order_id}")
        print(f"  Status: {status}")
        print(f"  Size matched: {size_matched}")

        return {
            "success": True,
            "order_id": order_id,
            "status": status,
            "size_matched": size_matched,
            "price_average": response.get("price_average"),
            "response": response
        }
    else:
        error_msg = response.get("errorMsg", "Unknown error")
        print(f"Order failed: {error_msg}")

        return {
            "success": False,
            "error": error_msg,
            "response": response
        }

# Usage
result = place_limit_order(
    client=client,
    token_id=token_id,
    price=0.45,
    size=100.0,
    side="BUY",
    order_type=OrderType.GTC
)
```

## Request Schema: OrderArgs

The `OrderArgs` class defines the order parameters:

```python
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

order_args = OrderArgs(
    price=0.45,           # Limit price (required)
    size=100.0,           # Number of shares (required)
    side=BUY,             # BUY or SELL constant (required)
    token_id=token_id,    # From Gamma API clobTokenIds (required)
    expiration=None       # Unix timestamp for GTD orders (optional)
)
```

### Field Details

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `price` | float | Yes | Limit price | 0.01 to 0.99, must align with tick size |
| `size` | float | Yes | Number of shares | > 0, FOK orders max 2 decimals |
| `side` | constant | Yes | BUY or SELL | Import from order_builder.constants |
| `token_id` | string | Yes | Conditional token ID | From Gamma API clobTokenIds array |
| `expiration` | int | No | Unix timestamp (seconds) | For GTD orders, min 60s in future |

### Price Constraints

- **Range:** 0.01 to 0.99 (representing 1% to 99% probability)
- **Tick size:** Must be a multiple of the market's tick size (usually 0.01)
- **Validation:** Check tick size before every order

```python
def validate_price(price: float, tick_size: float) -> float:
    """Round price to valid tick size."""
    if price < 0.01 or price > 0.99:
        raise ValueError(f"Price {price} out of range [0.01, 0.99]")

    validated = round(price / tick_size) * tick_size
    # Ensure within bounds after rounding
    validated = max(0.01, min(0.99, validated))
    return round(validated, 4)  # Clean up floating point
```

### Size Constraints

- **Minimum:** Varies by market (typically > 0)
- **FOK orders:** Maximum 2 decimal places
- **Product constraint:** For FOK, size x price must have max 2 decimals

```python
def validate_size_for_fok(size: float, price: float) -> float:
    """Validate and adjust size for FOK precision requirements."""
    rounded_size = round(size, 2)
    product = rounded_size * price

    # Check product has max 2 decimals
    if round(product, 2) != round(product, 6):
        # Adjust size to make product clean
        rounded_size = round(product, 2) / price
        rounded_size = round(rounded_size, 2)

    return rounded_size
```

## Response Schema

### Successful Order Response

```python
{
    "success": True,
    "orderID": "0x7c3e9f0a8b2d4e1c5f6a7b8c9d0e1f2a3b4c5d6e",
    "status": "live",           # Order state (see below)
    "transactTime": 1705312200, # Unix timestamp
    "size_matched": 0.0,        # Amount filled immediately
    "price_average": None,      # Average fill price (if any fill)
    "errorMsg": None
}
```

### Order Status Values

| Status | Meaning | Next Steps |
|--------|---------|------------|
| `live` | Order resting on orderbook | Wait for fills or cancel |
| `matched` | Partially or fully matched | Check size_matched for fill amount |
| `delayed` | Processing, not yet confirmed | Check order status later |

### Error Response

```python
{
    "success": False,
    "orderID": None,
    "status": None,
    "errorMsg": "Invalid tick size",  # Reason for failure
    "transactTime": 1705312200
}
```

## Tick Size Validation

**Critical:** Prices must align with the market's tick size or orders will be rejected.

```python
def get_valid_price(client, token_id: str, desired_price: float) -> float:
    """Get a valid price aligned to tick size.

    Args:
        client: ClobClient instance
        token_id: Token to get tick size for
        desired_price: Your target price

    Returns:
        Price rounded to valid tick size
    """
    tick_size = float(client.get_tick_size(token_id))

    # Round to nearest tick
    valid_price = round(desired_price / tick_size) * tick_size

    # Clean up floating point errors
    valid_price = round(valid_price, 4)

    # Ensure within valid range
    valid_price = max(0.01, min(0.99, valid_price))

    return valid_price

# Usage
tick_size = float(client.get_tick_size(token_id))
print(f"Tick size: {tick_size}")

# These prices work (assuming 0.01 tick):
valid_prices = [0.45, 0.50, 0.01, 0.99]

# These fail (not multiples of tick):
invalid_prices = [0.455, 0.4567, 0.001]
```

## Common Errors and Solutions

### INVALID_ORDER_MIN_TICK_SIZE

**Cause:** Price is not a multiple of the tick size.

```python
# Error
{
    "success": False,
    "errorMsg": "INVALID_ORDER_MIN_TICK_SIZE"
}

# Solution: Always validate price before ordering
tick_size = float(client.get_tick_size(token_id))
price = round(desired_price / tick_size) * tick_size
```

### invalid amounts

**Cause:** FOK order precision requirements not met.

```python
# Error
{
    "success": False,
    "errorMsg": "invalid amounts"
}

# Solution: Use GTC instead or round size properly
# For FOK: size must have max 2 decimals, and size*price max 2 decimals
size = round(size, 2)

# Better: Just use GTC which has no precision restrictions
response = client.post_order(order, OrderType.GTC)
```

### insufficient balance

**Cause:** Not enough USDC.e (for BUY) or shares (for SELL).

```python
# Error
{
    "success": False,
    "errorMsg": "insufficient balance"
}

# Solution: Check balance before ordering
# For BUY orders: verify USDC.e balance
# For SELL orders: verify position size

# See: positions-and-balances.md for balance checking
```

### unauthorized / invalid api key

**Cause:** API credentials not set or expired.

```python
# Error
{
    "success": False,
    "errorMsg": "Invalid api key"
}

# Solution: Set or refresh credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
```

## Order Placement Patterns

### Pattern 1: Simple Limit Order

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# Basic GTC limit order
order_args = OrderArgs(
    price=0.45,
    size=100.0,
    side=BUY,
    token_id=token_id
)
order = client.create_order(order_args)
response = client.post_order(order, OrderType.GTC)
```

### Pattern 2: Market-Style Order (FAK)

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# Get best ask to ensure fill
book = client.get_order_book(token_id)
best_ask = float(book['asks'][0]['price']) if book.get('asks') else 0.99

# FAK at best ask = immediate fill (if liquidity exists)
order_args = OrderArgs(
    price=best_ask,
    size=100.0,
    side=BUY,
    token_id=token_id
)
order = client.create_order(order_args)
response = client.post_order(order, OrderType.FAK)

# Check how much actually filled
print(f"Filled: {response.get('size_matched', 0)} shares")
```

### Pattern 3: Time-Limited Order (GTD)

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
import time

# Order expires in 1 hour
expiration = int(time.time()) + 3600

order_args = OrderArgs(
    price=0.45,
    size=100.0,
    side=BUY,
    token_id=token_id,
    expiration=expiration
)
order = client.create_order(order_args)
response = client.post_order(order, OrderType.GTD)
```

### Pattern 4: All-or-Nothing Order (FOK)

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# IMPORTANT: FOK has strict precision requirements
# Size must round to 2 decimal places
size = round(100.123, 2)  # -> 100.12

order_args = OrderArgs(
    price=0.45,
    size=size,
    side=BUY,
    token_id=token_id
)
order = client.create_order(order_args)
response = client.post_order(order, OrderType.FOK)

# FOK either fills completely or fails entirely
if response.get("size_matched", 0) == 0:
    print("FOK order could not be filled - no execution")
```

## Complete Example: Robust Order Placement

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
import time

def place_order_robust(
    client: ClobClient,
    token_id: str,
    price: float,
    size: float,
    side: str,
    order_type: str = "GTC",
    expires_in_seconds: int = None,
    max_retries: int = 3
) -> dict:
    """Place an order with full validation and error handling.

    Args:
        client: Authenticated ClobClient
        token_id: Token to trade
        price: Desired price (will be aligned to tick size)
        size: Number of shares
        side: "BUY" or "SELL"
        order_type: "GTC", "GTD", "FOK", or "FAK"
        expires_in_seconds: For GTD orders, seconds until expiry
        max_retries: Number of retry attempts on transient errors

    Returns:
        Order result dict
    """
    # Map order type string to enum
    type_map = {
        "GTC": OrderType.GTC,
        "GTD": OrderType.GTD,
        "FOK": OrderType.FOK,
        "FAK": OrderType.FAK
    }
    ot = type_map.get(order_type.upper(), OrderType.GTC)

    # Validate and adjust price
    tick_size = float(client.get_tick_size(token_id))
    validated_price = round(price / tick_size) * tick_size
    validated_price = max(0.01, min(0.99, round(validated_price, 4)))

    # Validate size for FOK
    validated_size = size
    if ot == OrderType.FOK:
        validated_size = round(size, 2)
        product = validated_size * validated_price
        if round(product, 2) != round(product, 6):
            print(f"Warning: FOK precision issue, switching to GTC")
            ot = OrderType.GTC

    # Build order args
    order_kwargs = {
        "price": validated_price,
        "size": validated_size,
        "side": BUY if side.upper() == "BUY" else SELL,
        "token_id": token_id
    }

    # Add expiration for GTD
    if ot == OrderType.GTD:
        if expires_in_seconds:
            order_kwargs["expiration"] = int(time.time()) + expires_in_seconds
        else:
            # Default to 1 hour
            order_kwargs["expiration"] = int(time.time()) + 3600

    order_args = OrderArgs(**order_kwargs)

    # Attempt order with retries
    last_error = None
    for attempt in range(max_retries):
        try:
            signed_order = client.create_order(order_args)
            response = client.post_order(signed_order, ot)

            if response.get("success"):
                return {
                    "success": True,
                    "order_id": response.get("orderID") or response.get("orderId"),
                    "status": response.get("status"),
                    "size_matched": response.get("size_matched", 0),
                    "price_average": response.get("price_average"),
                    "order_type": order_type,
                    "validated_price": validated_price,
                    "validated_size": validated_size
                }
            else:
                # Non-retryable error
                return {
                    "success": False,
                    "error": response.get("errorMsg", "Unknown error"),
                    "response": response
                }

        except Exception as e:
            last_error = str(e)
            if "429" in str(e):  # Rate limited
                time.sleep(2 ** attempt)
                continue
            elif "5" in str(e)[:1]:  # Server error
                time.sleep(1)
                continue
            else:
                raise

    return {
        "success": False,
        "error": f"Failed after {max_retries} attempts: {last_error}"
    }

# Usage examples

# Simple limit order
result = place_order_robust(
    client, token_id,
    price=0.45, size=100, side="BUY"
)

# Market-style order
result = place_order_robust(
    client, token_id,
    price=0.55, size=50, side="BUY",
    order_type="FAK"
)

# Time-limited order (expires in 30 minutes)
result = place_order_robust(
    client, token_id,
    price=0.40, size=200, side="BUY",
    order_type="GTD",
    expires_in_seconds=1800
)
```

## Related Documentation

- [Order Types](./order-types.md) - GTC, GTD, FOK, FAK selection guide
- [Order Management](./order-management.md) - Cancellation and status checking
- [Positions and Balances](./positions-and-balances.md) - Balance verification before trading
- [CLOB API Overview](./clob-api-overview.md) - API architecture and endpoints

## References

- [Polymarket CLOB Orders](https://docs.polymarket.com/developers/CLOB/orders) - Official documentation
- [py-clob-client](https://github.com/Polymarket/py-clob-client) - Python client library
