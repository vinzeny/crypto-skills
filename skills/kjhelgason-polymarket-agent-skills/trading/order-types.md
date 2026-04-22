# Polymarket Order Types Guide

Complete documentation of order types available on the Polymarket CLOB, covering GTC, GTD, FOK, and FAK orders with precision requirements and selection guidance.

## Order Type Overview

Polymarket supports four order types, each designed for specific trading scenarios:

| Type | Name | Execution | Partial Fills | Use Case |
|------|------|-----------|---------------|----------|
| **GTC** | Good Till Cancelled | Rests on book | Allowed | Limit orders, patient trading |
| **GTD** | Good Till Date | Rests until expiry | Allowed | Time-sensitive limits |
| **FOK** | Fill or Kill | Immediate only | **NOT** allowed | All-or-nothing execution |
| **FAK** | Fill and Kill | Immediate only | Allowed | Market orders, best effort |

### Quick Selection Guide

```
Do you need immediate execution?
|
+-- No --> Use GTC or GTD
|          |
|          +-- Time limit needed? --> GTD (with expiration)
|          +-- No time limit? --> GTC
|
+-- Yes --> Use FOK or FAK
           |
           +-- Must fill completely? --> FOK (strict precision!)
           +-- Partial fills OK? --> FAK
```

## GTC Orders (Good Till Cancelled)

**CLOB-01 Requirement:** Standard limit order functionality

GTC is the default order type for limit orders. Orders rest on the order book until fully filled or explicitly cancelled.

### Characteristics

- **Persistence:** Remains active until filled or cancelled
- **Partial fills:** Allowed - can fill incrementally over time
- **Book placement:** Rests on order book at specified price
- **Precision:** Standard decimal precision (no special requirements)

### Code Example

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

# Standard limit order - rests on book until filled or cancelled
order_args = OrderArgs(
    price=0.45,      # Limit price (0.01 to 0.99)
    size=100.0,      # Number of shares
    side=BUY,        # BUY or SELL
    token_id=token_id
)

# Create signed order
signed_order = client.create_order(order_args)

# Post as GTC order
response = client.post_order(signed_order, OrderType.GTC)
print(f"Order ID: {response.get('orderID')}")
```

### When to Use GTC

- **Limit orders:** You want a specific price and can wait
- **Patient trading:** No urgency to fill immediately
- **Price improvement:** Willing to wait for better execution
- **Market making:** Providing liquidity at specific levels

### GTC Response

```python
{
    "success": True,
    "orderID": "0x123...",
    "status": "live",        # Order placed on book
    "transactTime": 1234567890,
    "size_matched": 0.0,     # Nothing matched yet
    "price_average": None,
    "errorMsg": None
}
```

## GTD Orders (Good Till Date)

GTD orders are limit orders with an expiration timestamp. They automatically cancel at the specified time if not filled.

### Characteristics

- **Expiration:** Auto-cancelled at specified Unix timestamp
- **Minimum duration:** Must be at least 1 minute in the future
- **Partial fills:** Allowed before expiration
- **Book placement:** Rests on order book until filled or expired

### Code Example

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
import time

# Limit order with expiration
expiration = int(time.time()) + 3600  # Expires in 1 hour

order_args = OrderArgs(
    price=0.45,
    size=100.0,
    side=BUY,
    token_id=token_id,
    expiration=expiration  # Unix timestamp (seconds)
)

signed_order = client.create_order(order_args)
response = client.post_order(signed_order, OrderType.GTD)
```

### Expiration Time Patterns

```python
import time

# Common expiration patterns
now = int(time.time())

# Short-term expirations
one_minute = now + 60
five_minutes = now + 300
one_hour = now + 3600

# Longer expirations
one_day = now + 86400
one_week = now + 604800

# End of day (example: 11:59 PM UTC)
from datetime import datetime, timezone
end_of_day = datetime.now(timezone.utc).replace(
    hour=23, minute=59, second=59
)
expiration_eod = int(end_of_day.timestamp())
```

### When to Use GTD

- **News trading:** Order only valid until announcement
- **Earnings plays:** Cancel automatically after event
- **Day trading:** Clean up orders at end of session
- **Time-sensitive arbitrage:** Opportunity has expiration

### GTD Constraints

| Constraint | Value |
|------------|-------|
| Minimum duration | 60 seconds in future |
| Timestamp format | Unix seconds (not milliseconds) |
| Precision | Integer seconds |

**Common mistake:** Using milliseconds instead of seconds.

```python
# WRONG - milliseconds
expiration = int(time.time() * 1000) + 3600000

# CORRECT - seconds
expiration = int(time.time()) + 3600
```

## FOK Orders (Fill or Kill)

**CLOB-05 Requirement:** Immediate execution order types

FOK orders demand complete immediate execution. If the full order cannot be filled at once, the entire order is rejected.

### Characteristics

- **Execution:** Immediate - either fills completely or fails
- **Partial fills:** **NOT allowed** - all or nothing
- **Book placement:** Never rests on book
- **Precision:** **STRICT requirements** (see below)

### CRITICAL - Precision Requirements

**FOK orders have strict precision requirements. Violating these causes immediate rejection.**

| Amount | Maximum Decimals |
|--------|-----------------|
| Maker amount | 2 decimal places |
| Taker amount | 4 decimal places |
| Size x Price product | 2 decimal places |

**If precision requirements are not met, the order is rejected with "invalid amounts" error.**

### Code Example

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# All-or-nothing immediate execution
# NOTE: Size MUST round to 2 decimal places!
order_args = OrderArgs(
    price=0.45,
    size=100.0,  # 2 decimal max: 100.0, 100.25 OK; 100.123 BAD
    side=BUY,
    token_id=token_id
)

signed_order = client.create_order(order_args)
response = client.post_order(signed_order, OrderType.FOK)
```

### Ensuring FOK Precision

```python
def prepare_fok_order(price: float, size: float) -> tuple:
    """
    Prepare price and size for FOK order precision requirements.

    Returns (rounded_price, rounded_size) or raises if impossible.
    """
    # Round size to 2 decimal places
    rounded_size = round(size, 2)

    # Check size x price product has max 2 decimals
    product = rounded_size * price
    if round(product, 2) != round(product, 10):
        # Try adjusting size to make product clean
        rounded_size = round(product, 2) / price
        rounded_size = round(rounded_size, 2)

    # Verify final product
    final_product = rounded_size * price
    if abs(round(final_product, 2) - final_product) > 0.0001:
        raise ValueError(
            f"Cannot satisfy FOK precision: size={rounded_size}, "
            f"price={price}, product={final_product}"
        )

    return price, rounded_size

# Usage
try:
    price, size = prepare_fok_order(0.45, 100.123)
    order_args = OrderArgs(price=price, size=size, side=BUY, token_id=token_id)
except ValueError as e:
    print(f"Use GTC instead: {e}")
```

### When to Use FOK

- **Guaranteed execution size:** Must get exact amount or nothing
- **Arbitrage:** Complete execution required for profit
- **Large orders:** Don't want partial fills at worse prices
- **Atomic operations:** Position sizing must be exact

### When NOT to Use FOK

- **General trading:** GTC is simpler and more flexible
- **Imprecise amounts:** If size doesn't round cleanly
- **Low liquidity markets:** Unlikely to fill completely
- **Price discovery:** Better to use GTC and adjust

### FOK Error Response

```python
# Precision error
{
    "success": False,
    "errorMsg": "invalid amounts",
    "orderID": None
}

# Insufficient liquidity
{
    "success": False,
    "errorMsg": "insufficient liquidity for FOK order",
    "orderID": None
}
```

## FAK Orders (Fill and Kill)

**CLOB-05 Requirement:** Immediate execution order types

FAK orders execute immediately at the best available prices. Unlike FOK, partial fills are accepted - any unfilled portion is cancelled.

### Characteristics

- **Execution:** Immediate - best effort at available prices
- **Partial fills:** **Allowed** - takes what's available
- **Book placement:** Never rests on book
- **Unfilled portion:** Automatically cancelled

### Code Example

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# Best-effort immediate execution
order_args = OrderArgs(
    price=0.45,
    size=100.0,
    side=BUY,
    token_id=token_id
)

signed_order = client.create_order(order_args)
response = client.post_order(signed_order, OrderType.FAK)

# Check how much actually filled
print(f"Requested: {order_args.size}")
print(f"Filled: {response.get('size_matched', 0)}")
```

### FAK as Market Order

FAK is the closest equivalent to a "market order" on Polymarket:

```python
def market_buy(client, token_id: str, max_price: float, size: float):
    """
    Execute a market-like buy using FAK order.

    Args:
        client: Authenticated ClobClient
        token_id: Token to buy
        max_price: Maximum price willing to pay
        size: Number of shares to buy

    Returns:
        Fill result with actual execution details
    """
    order_args = OrderArgs(
        price=max_price,  # Set high to ensure fill
        size=size,
        side=BUY,
        token_id=token_id
    )

    signed_order = client.create_order(order_args)
    response = client.post_order(signed_order, OrderType.FAK)

    return {
        "requested_size": size,
        "filled_size": response.get("size_matched", 0),
        "avg_price": response.get("price_average"),
        "unfilled": size - response.get("size_matched", 0)
    }

# Usage: Buy up to 100 shares at any price up to 0.55
result = market_buy(client, token_id, max_price=0.55, size=100)
print(f"Filled {result['filled_size']} at avg price {result['avg_price']}")
```

### When to Use FAK

- **Market orders:** Want immediate execution at best prices
- **Best effort fills:** OK with partial execution
- **Quick entry/exit:** Speed more important than price
- **Liquidity taking:** Consuming available liquidity

### FAK Response

```python
# Full fill
{
    "success": True,
    "orderID": "0x123...",
    "status": "matched",
    "size_matched": 100.0,
    "price_average": 0.45,
    "errorMsg": None
}

# Partial fill
{
    "success": True,
    "orderID": "0x123...",
    "status": "matched",
    "size_matched": 75.0,      # Only 75 of 100 filled
    "price_average": 0.4533,   # Weighted average price
    "errorMsg": None
}

# No fill (no liquidity)
{
    "success": True,
    "orderID": "0x123...",
    "status": "delayed",  # Nothing matched
    "size_matched": 0.0,
    "price_average": None,
    "errorMsg": None
}
```

## Order Type Decision Tree

Use this decision tree to select the appropriate order type:

```
START: What kind of execution do you need?
|
+-- I want to specify a price and wait
|   |
|   +-- Does my order need to expire automatically?
|       |
|       +-- YES --> Use GTD with expiration timestamp
|       +-- NO --> Use GTC (standard limit order)
|
+-- I need immediate execution
    |
    +-- Must the entire order fill, or is partial OK?
        |
        +-- ENTIRE order must fill (all-or-nothing)
        |   |
        |   +-- Can my size round to 2 decimal places?
        |       |
        |       +-- YES --> Use FOK
        |       +-- NO --> Use GTC (FOK will reject)
        |
        +-- Partial fills are acceptable
            |
            +-- Use FAK (market-style order)
```

### Quick Reference Table

| Scenario | Order Type | Why |
|----------|------------|-----|
| Standard limit order, no rush | **GTC** | Patient, flexible, no precision issues |
| Limit order for specific event | **GTD** | Auto-cancels after event passes |
| Arbitrage requiring exact fill | **FOK** | All-or-nothing, atomic execution |
| Market order, best effort | **FAK** | Immediate, accepts partial fills |
| Order with unusual size decimals | **GTC** | FOK precision too restrictive |
| Day trading, clean up at EOD | **GTD** | Set expiration to end of day |

## Order Response Schema

All order types return a similar response structure:

```python
{
    # Always present
    "success": bool,           # Whether order was accepted
    "orderID": str | None,     # Order ID (None if rejected)
    "status": str,             # "live", "matched", "delayed"

    # Execution details
    "size_matched": float,     # Amount filled immediately
    "price_average": float,    # Average fill price (None if no fill)

    # Error information
    "errorMsg": str | None,    # Error message if failed

    # Timing
    "transactTime": int        # Unix timestamp of transaction
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `live` | Order resting on book (GTC/GTD) |
| `matched` | Order fully or partially filled |
| `delayed` | Order processed but not yet confirmed |

### Checking Order Execution

```python
def analyze_order_response(response, original_size):
    """Analyze order response to understand execution."""

    if not response.get("success"):
        return {
            "status": "rejected",
            "reason": response.get("errorMsg", "Unknown error")
        }

    size_matched = response.get("size_matched", 0)

    if size_matched == 0:
        return {
            "status": "unfilled",
            "order_id": response.get("orderID"),
            "resting": response.get("status") == "live"
        }

    if size_matched >= original_size:
        return {
            "status": "filled",
            "size": size_matched,
            "avg_price": response.get("price_average"),
            "order_id": response.get("orderID")
        }

    return {
        "status": "partial",
        "filled": size_matched,
        "remaining": original_size - size_matched,
        "avg_price": response.get("price_average"),
        "order_id": response.get("orderID")
    }
```

## Common Issues and Solutions

### Issue: FOK Order Rejected with "invalid amounts"

**Cause:** Size or price doesn't meet precision requirements.

**Solution:**
```python
# Round size to 2 decimal places
size = round(desired_size, 2)

# Verify product has max 2 decimals
product = size * price
if round(product, 2) != round(product, 6):
    # Use GTC instead
    order_type = OrderType.GTC
else:
    order_type = OrderType.FOK
```

### Issue: GTD Order Rejected Immediately

**Cause:** Expiration time too close or in the past.

**Solution:**
```python
# Ensure at least 1 minute in future
import time
min_expiration = int(time.time()) + 60
expiration = max(desired_expiration, min_expiration)
```

### Issue: FAK Order Returns 0 Filled

**Cause:** No liquidity at the specified price.

**Solution:**
```python
# Check available liquidity first
book = client.get_order_book(token_id)
best_ask = float(book['asks'][0]['price']) if book['asks'] else None

if best_ask:
    # Set price at or above best ask to ensure fill
    order_args = OrderArgs(
        price=best_ask,
        size=size,
        side=BUY,
        token_id=token_id
    )
```

### Issue: Order Rejected After Tick Size Check

**Cause:** Price not a multiple of tick size.

**Solution:**
```python
tick_size = client.get_tick_size(token_id)
price = round(desired_price / tick_size) * tick_size
```

## Complete Example: Order Type Selection

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
import time

def place_order_smart(
    client,
    token_id: str,
    price: float,
    size: float,
    side: str,
    immediate: bool = False,
    all_or_nothing: bool = False,
    expires_in_seconds: int = None
):
    """
    Place an order with automatic type selection.

    Args:
        client: Authenticated ClobClient
        token_id: Token to trade
        price: Order price
        size: Order size
        side: BUY or SELL
        immediate: If True, use FAK/FOK (no resting)
        all_or_nothing: If True and immediate, use FOK
        expires_in_seconds: If set, use GTD with this duration

    Returns:
        Order response dict
    """
    # Determine order type
    if immediate:
        if all_or_nothing:
            # Try FOK, fall back to GTC if precision issues
            rounded_size = round(size, 2)
            product = rounded_size * price
            if abs(round(product, 2) - product) < 0.0001:
                order_type = OrderType.FOK
                size = rounded_size
            else:
                print("Warning: FOK precision not possible, using GTC")
                order_type = OrderType.GTC
        else:
            order_type = OrderType.FAK
    elif expires_in_seconds:
        order_type = OrderType.GTD
    else:
        order_type = OrderType.GTC

    # Build order args
    order_args_dict = {
        "price": price,
        "size": size,
        "side": BUY if side == "BUY" else SELL,
        "token_id": token_id
    }

    # Add expiration for GTD
    if order_type == OrderType.GTD:
        order_args_dict["expiration"] = int(time.time()) + expires_in_seconds

    order_args = OrderArgs(**order_args_dict)
    signed_order = client.create_order(order_args)

    response = client.post_order(signed_order, order_type)

    return {
        "order_type": order_type.name,
        "response": response
    }

# Usage examples:

# Standard limit order
result = place_order_smart(client, token_id, 0.45, 100, "BUY")

# Market-style immediate fill
result = place_order_smart(client, token_id, 0.55, 100, "BUY", immediate=True)

# All-or-nothing
result = place_order_smart(client, token_id, 0.45, 100, "BUY",
                          immediate=True, all_or_nothing=True)

# Order expires in 1 hour
result = place_order_smart(client, token_id, 0.45, 100, "BUY",
                          expires_in_seconds=3600)
```

## Related Documentation

- [CLOB API Overview](./clob-api-overview.md) - API architecture and endpoints
- [Order Placement Guide](./order-placement.md) - Detailed placement workflows (coming soon)
- [Order Management](./order-management.md) - Cancellation and modification (coming soon)

## References

- [Polymarket CLOB Orders](https://docs.polymarket.com/developers/CLOB/orders) - Official order documentation
- [py-clob-client Order Types](https://github.com/Polymarket/py-clob-client/blob/main/py_clob_client/clob_types.py) - Type definitions
