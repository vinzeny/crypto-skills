# Order Constraints: Minimums, Precision, and Tick Sizes

**Edge Case IDs:** EDGE-02, EDGE-03, EDGE-08

This guide covers the three most common order rejection causes: minimum order requirements, FOK precision requirements, and dynamic tick size changes.

## Overview

| Constraint | Error Message | Quick Fix |
|------------|---------------|-----------|
| FOK Precision | "invalid amounts" | Round size to 2 decimals |
| Tick Size | "INVALID_ORDER_MIN_TICK_SIZE" | Fetch current tick size |
| Price Range | "price out of range" | Use 0.01-0.99 |

## Order Minimums (EDGE-02)

### No Enforced Minimum

The Polymarket orderbook has **no enforced minimum order size**. Any positive amount can be submitted.

However, there are practical considerations:

| Factor | Consideration |
|--------|---------------|
| **Gas costs** | Very small orders may have gas > value |
| **Dust orders** | Orders < $0.10 provide little utility |
| **Rewards threshold** | Polymarket rewards have minimum share requirements |

### Practical Recommendations

```python
def validate_order_size(size: float, price: float) -> dict:
    """
    Check if order size is practical.

    Args:
        size: Number of shares
        price: Price per share (0.01-0.99)

    Returns:
        Validation result with warnings
    """
    notional = size * price

    result = {
        "valid": True,
        "warnings": []
    }

    # Gas efficiency warning
    if notional < 1.0:
        result["warnings"].append(
            f"Order value ${notional:.2f} is very small - gas may exceed value"
        )

    # Dust order warning
    if size < 1.0:
        result["warnings"].append(
            f"Size {size} shares is very small - consider larger position"
        )

    return result
```

### Gas Cost Context

- Typical order gas: 0.001-0.01 POL
- At POL = $0.50, gas = ~$0.005
- Orders < $0.10 may have 5%+ gas overhead

## FOK Precision Requirements (EDGE-03)

### The Problem

FOK (Fill or Kill) orders have **stricter precision requirements** than GTC orders. The same parameters that work with GTC may fail with FOK.

### Precision Rules

| Amount | Maximum Decimals | Example Valid | Example Invalid |
|--------|-----------------|---------------|-----------------|
| Maker amount (size) | 2 decimal places | 100.00, 50.25 | 100.123 |
| Taker amount | 4 decimal places | - | - |
| Size x Price product | 2 decimal places | 100 x 0.45 = 45.00 | 100 x 0.333 = 33.3 |

### Error Message

```
"invalid amounts, the sell orders maker amount supports a max accuracy of 2 decimals"
```

### FOK Precision Helper

```python
from decimal import Decimal, ROUND_DOWN

def prepare_fok_order(price: float, size: float) -> dict:
    """
    Prepare price and size for FOK order precision requirements.

    FOK Requirements:
    - Maker amount (size): max 2 decimal places
    - Taker amount: max 4 decimal places
    - Size x Price product: max 2 decimal places

    Args:
        price: Order price (0.01-0.99)
        size: Desired order size

    Returns:
        Dict with adjusted values or error

    Raises:
        ValueError: If precision cannot be satisfied
    """
    # Use Decimal for precise arithmetic
    price_d = Decimal(str(price))
    size_d = Decimal(str(size))

    # Round size to 2 decimals
    size_rounded = size_d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    # Check if product has clean 2-decimal result
    product = size_rounded * price_d
    product_rounded = product.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    if product != product_rounded:
        # Try adjusting size to make product clean
        adjusted_size = (product_rounded / price_d).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )

        # Verify adjustment worked
        new_product = adjusted_size * price_d
        if new_product != new_product.quantize(Decimal("0.01")):
            raise ValueError(
                f"Cannot satisfy FOK precision at price {price}. "
                f"Consider using GTC order type instead."
            )

        size_rounded = adjusted_size
        product_rounded = new_product

    return {
        "price": float(price_d),
        "size": float(size_rounded),
        "notional": float(product_rounded),
        "original_size": size,
        "size_adjusted": float(size_rounded) != size
    }
```

### Usage Example

```python
# Example: User wants 100.123 shares at $0.45

try:
    params = prepare_fok_order(0.45, 100.123)
    print(f"Adjusted size: {params['size']}")  # 100.0
    print(f"Notional: ${params['notional']}")  # $45.00

    if params['size_adjusted']:
        print(f"Note: Size reduced from {params['original_size']}")

except ValueError as e:
    print(f"Use GTC instead: {e}")
```

### Precision Fallback Pattern

When FOK precision cannot be satisfied, fall back to GTC:

```python
from py_clob_client.clob_types import OrderArgs, OrderType

def place_order_with_fallback(client, token_id, price, size, side):
    """
    Try FOK first, fall back to GTC if precision impossible.
    """
    try:
        # Attempt FOK
        params = prepare_fok_order(price, size)

        order_args = OrderArgs(
            price=params['price'],
            size=params['size'],
            side=side,
            token_id=token_id
        )

        signed = client.create_order(order_args)
        response = client.post_order(signed, OrderType.FOK)

        return {
            "order_type": "FOK",
            "response": response,
            "size_adjusted": params['size_adjusted']
        }

    except ValueError:
        # FOK precision impossible, use GTC
        order_args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id
        )

        signed = client.create_order(order_args)
        response = client.post_order(signed, OrderType.GTC)

        return {
            "order_type": "GTC",
            "response": response,
            "fallback_reason": "FOK precision requirements not satisfiable"
        }
```

## Dynamic Tick Size (EDGE-08)

### The Problem

Tick sizes change dynamically based on market price. Orders that worked yesterday may fail today if the market moved to a price extreme.

### Tick Size Rules

| Price Range | Tick Size | Price Decimals |
|-------------|-----------|----------------|
| 0.04 - 0.96 | 0.01 | 2 |
| 0.96+ or < 0.04 | 0.001 | 3 |
| Near 0.99 or 0.01 | 0.0001 | 4 |

### ROUNDING_CONFIG

The py-clob-client uses this configuration for precision at different tick sizes:

```python
ROUNDING_CONFIG = {
    "0.1": {"price": 1, "size": 2, "amount": 3},
    "0.01": {"price": 2, "size": 2, "amount": 4},
    "0.001": {"price": 3, "size": 2, "amount": 5},
    "0.0001": {"price": 4, "size": 2, "amount": 6}
}
```

**Key insight:** Size is always 2 decimals, but price and amount decimals vary with tick size.

### Always Fetch Current Tick Size

```python
def get_validated_price(client, token_id: str, desired_price: float) -> float:
    """
    Validate and round price to current tick size.

    CRITICAL: Always call this before placing orders.
    Do NOT cache tick sizes for more than a few seconds.

    Args:
        client: Authenticated ClobClient
        token_id: Token to trade
        desired_price: User's desired price

    Returns:
        Price rounded to valid tick size
    """
    # Fetch current tick size (DO NOT use cached value)
    tick_size = client.get_tick_size(token_id)
    tick_float = float(tick_size)

    # Round to nearest tick
    ticks = round(desired_price / tick_float)
    validated_price = ticks * tick_float

    # Ensure within valid range
    validated_price = max(0.01, min(0.99, validated_price))

    return round(validated_price, len(str(tick_size).split('.')[-1]))

# Usage
price = get_validated_price(client, token_id, 0.455)
print(f"Validated price: {price}")  # 0.46 (if tick_size = 0.01)
```

### WebSocket Tick Size Changes

If using WebSocket for real-time data, handle `tick_size_change` events:

```python
async def handle_websocket_message(message: dict):
    """Handle incoming WebSocket message."""
    event_type = message.get("event_type")

    if event_type == "tick_size_change":
        token_id = message.get("asset_id")
        new_tick_size = message.get("tick_size")

        # Update local cache
        tick_size_cache[token_id] = {
            "tick_size": new_tick_size,
            "updated_at": time.time()
        }

        # Log for monitoring
        print(f"Tick size changed for {token_id}: {new_tick_size}")

        # Cancel orders that may now be invalid
        await review_open_orders(token_id, new_tick_size)
```

### Tick Size Change Detection

```python
def needs_tick_refresh(token_id: str, current_price: float) -> bool:
    """
    Determine if tick size should be refreshed.

    Refresh when:
    - Price is near extremes (< 0.04 or > 0.96)
    - Cache is more than 5 seconds old
    - Price has moved significantly since last check
    """
    # Always refresh at price extremes
    if current_price < 0.04 or current_price > 0.96:
        return True

    # Check cache age
    if token_id in tick_size_cache:
        cached = tick_size_cache[token_id]
        age = time.time() - cached.get("updated_at", 0)
        if age > 5:  # More than 5 seconds old
            return True
    else:
        return True  # Not in cache

    return False
```

## Decision Tree: Handling Precision

```
Order placement attempt
|
+-- Is this a FOK order?
|   |
|   +-- YES: Apply FOK precision rules
|   |   |
|   |   +-- Round size to 2 decimals
|   |   +-- Check size x price has 2 decimals
|   |   |
|   |   +-- Precision satisfied?
|   |       |
|   |       +-- YES: Submit FOK
|   |       +-- NO: Fall back to GTC
|   |
|   +-- NO: Continue
|
+-- Fetch current tick size
|   (NEVER use cached tick size for orders)
|
+-- Round price to tick size
|
+-- Submit order
```

## Pre-Order Checklist

Before every order:

```python
def pre_order_validation(client, token_id, price, size, order_type):
    """
    Complete pre-order validation.

    Returns dict with validated parameters or raises on error.
    """
    issues = []

    # 1. Fetch current tick size
    tick_size = client.get_tick_size(token_id)

    # 2. Validate price against tick size
    ticks = round(price / float(tick_size))
    validated_price = ticks * float(tick_size)

    if abs(validated_price - price) > 0.0001:
        issues.append(f"Price adjusted for tick size: {price} -> {validated_price}")
        price = validated_price

    # 3. FOK-specific precision
    if order_type == "FOK":
        try:
            fok_params = prepare_fok_order(price, size)
            size = fok_params['size']
            if fok_params['size_adjusted']:
                issues.append(f"Size adjusted for FOK: {fok_params['original_size']} -> {size}")
        except ValueError as e:
            raise ValueError(f"Cannot place FOK order: {e}")

    # 4. Price range check
    if price < 0.01 or price > 0.99:
        raise ValueError(f"Price {price} outside valid range 0.01-0.99")

    return {
        "price": price,
        "size": size,
        "tick_size": float(tick_size),
        "issues": issues,
        "valid": True
    }
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "invalid amounts, the sell orders maker amount supports a max accuracy of 2 decimals" | FOK size has > 2 decimals | Use `prepare_fok_order()` |
| "INVALID_ORDER_MIN_TICK_SIZE" | Price not aligned to current tick | Fetch and apply tick size |
| "price out of range" | Price < 0.01 or > 0.99 | Clamp to valid range |
| "order crosses book" | Limit order would execute immediately | Adjust price or use FAK |

## Recovery Patterns

### From "invalid amounts" Error

```python
from py_clob_client.exceptions import PolyApiException

try:
    response = client.post_order(signed_order, OrderType.FOK)
except PolyApiException as e:
    if "invalid amounts" in str(e.error_msg):
        # Retry with GTC
        response = client.post_order(signed_order, OrderType.GTC)
        print("Retried as GTC due to FOK precision")
```

### From "INVALID_ORDER_MIN_TICK_SIZE" Error

```python
try:
    response = client.post_order(signed_order, order_type)
except PolyApiException as e:
    if "INVALID_ORDER_MIN_TICK_SIZE" in str(e.error_msg):
        # Refetch tick size and retry
        tick_size = client.get_tick_size(token_id)
        validated_price = round(price / float(tick_size)) * float(tick_size)

        # Rebuild and retry order with corrected price
        new_order = OrderArgs(
            price=validated_price,
            size=size,
            side=side,
            token_id=token_id
        )
        signed_order = client.create_order(new_order)
        response = client.post_order(signed_order, order_type)
```

## Related Documentation

- [Order Types](../trading/order-types.md) - GTC, GTD, FOK, FAK selection and characteristics
- [Order Lifecycle](../trading/order-lifecycle.md) - Placement, fills, and cancellation
- [CLOB API Overview](../trading/clob-api-overview.md) - API architecture

## Navigation

- [Back to Edge Cases Index](./README.md)
- [USDC Token Confusion](./usdc-token-confusion.md)
