# Order Management Guide

Complete documentation for managing orders on Polymarket, including cancellation, status checking, open orders retrieval, and batch operations.

**Covers:** CLOB-02 (Cancellation), CLOB-03 (Order Status), CLOB-06 (Batch Operations)

## Order Lifecycle Overview

```
                                 ┌─────────────┐
                                 │ create_order│
                                 │   (sign)    │
                                 └──────┬──────┘
                                        │
                                        v
                                 ┌─────────────┐
                                 │ post_order  │
                                 │  (submit)   │
                                 └──────┬──────┘
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │
                        v               v               v
                   ┌────────┐      ┌────────┐     ┌──────────┐
                   │  LIVE  │      │MATCHED │     │ DELAYED  │
                   │(on book)│     │(filled)│     │(pending) │
                   └────┬───┘      └────────┘     └────┬─────┘
                        │                              │
         ┌──────────────┼──────────────┐               │
         │              │              │               v
         v              v              v          ┌────────┐
    ┌────────┐    ┌──────────┐   ┌─────────┐     │  LIVE  │
    │cancel()│    │expiration│   │ fills   │     │or fail │
    └────┬───┘    │ (GTD)    │   │(partial)│     └────────┘
         │        └────┬─────┘   └────┬────┘
         v             v              v
    ┌─────────┐   ┌─────────┐   ┌─────────┐
    │CANCELLED│   │CANCELLED│   │MATCHED  │
    └─────────┘   └─────────┘   └─────────┘
```

## Order Cancellation (CLOB-02)

### Cancel Single Order

```python
def cancel_order(client, order_id: str) -> dict:
    """Cancel a specific order by ID.

    Args:
        client: Authenticated ClobClient
        order_id: Order ID to cancel (from post_order response)

    Returns:
        Cancel result with status
    """
    try:
        response = client.cancel(order_id)

        if response.get("canceled"):
            print(f"Order {order_id} cancelled successfully")
            return {"success": True, "order_id": order_id}
        elif response.get("not_canceled"):
            reason = response["not_canceled"].get(order_id, "Unknown reason")
            print(f"Cancel failed: {reason}")
            return {"success": False, "reason": reason}
        else:
            return {"success": False, "reason": "Unexpected response", "response": response}

    except Exception as e:
        return {"success": False, "error": str(e)}

# Usage
result = cancel_order(client, "0x7c3e9f0a8b2d4e1c5f6a7b8c9d0e1f2a3b4c5d6e")
```

### Cancel Response Schema

```python
# Success response
{
    "canceled": ["0x7c3e9f0a..."]  # List of cancelled order IDs
}

# Partial failure response
{
    "canceled": ["0x7c3e9f0a..."],
    "not_canceled": {
        "0x8d4f0a1b...": "Order not found",
        "0x9e5g1b2c...": "Order already matched"
    }
}

# Full failure response
{
    "not_canceled": {
        "0x7c3e9f0a...": "Order not found"
    }
}
```

### Cancel All Orders

```python
def cancel_all_orders(client) -> dict:
    """Cancel all open orders for the authenticated user.

    Returns:
        Cancel result with count of cancelled orders
    """
    try:
        response = client.cancel_all()

        canceled_count = len(response.get("canceled", []))
        not_canceled = response.get("not_canceled", {})

        print(f"Cancelled {canceled_count} orders")
        if not_canceled:
            print(f"Failed to cancel {len(not_canceled)} orders")

        return {
            "success": True,
            "canceled_count": canceled_count,
            "not_canceled_count": len(not_canceled),
            "details": response
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# Usage
result = cancel_all_orders(client)
print(f"Cancelled {result['canceled_count']} orders")
```

### Cancel Orders by Market

```python
def cancel_market_orders(client, market_id: str) -> dict:
    """Cancel all orders for a specific market.

    Args:
        client: Authenticated ClobClient
        market_id: Market/condition ID (not token_id)

    Returns:
        Cancel result
    """
    # Get all open orders for this market
    orders = client.get_orders(market=market_id)
    live_orders = [o for o in orders if o.get("status") == "LIVE"]

    if not live_orders:
        return {"success": True, "message": "No open orders in market"}

    order_ids = [o["id"] for o in live_orders]
    response = client.cancel_orders(order_ids)

    return {
        "success": True,
        "attempted": len(order_ids),
        "canceled": len(response.get("canceled", [])),
        "failed": len(response.get("not_canceled", {}))
    }

# Usage
result = cancel_market_orders(client, condition_id)
```

## Order Status Checking (CLOB-03)

### Get Single Order

```python
def get_order_status(client, order_id: str) -> dict:
    """Get detailed status for a specific order.

    Args:
        client: Authenticated ClobClient
        order_id: Order ID to query

    Returns:
        Order details including status, fills, and remaining size
    """
    try:
        order = client.get_order(order_id)

        original_size = float(order.get("original_size", 0))
        size_matched = float(order.get("size_matched", 0))
        remaining = original_size - size_matched

        return {
            "id": order.get("id"),
            "status": order.get("status"),
            "side": order.get("side"),
            "price": float(order.get("price", 0)),
            "original_size": original_size,
            "size_matched": size_matched,
            "remaining": remaining,
            "fill_percent": (size_matched / original_size * 100) if original_size > 0 else 0,
            "created_at": order.get("created_at"),
            "token_id": order.get("asset_id"),
            "market_id": order.get("market")
        }

    except Exception as e:
        return {"error": str(e)}

# Usage
status = get_order_status(client, order_id)
print(f"Status: {status['status']}")
print(f"Filled: {status['size_matched']}/{status['original_size']} ({status['fill_percent']:.1f}%)")
```

### Order Response Schema

```python
{
    "id": "0x7c3e9f0a8b2d4e1c5f6a7b8c9d0e1f2a3b4c5d6e",
    "status": "LIVE",              # LIVE, MATCHED, CANCELED
    "maker_address": "0x...",      # Your trading address
    "market": "0x...",             # Condition ID
    "asset_id": "71321045...",     # Token ID
    "side": "BUY",                 # BUY or SELL
    "original_size": "100.0",      # Initial order size
    "size_matched": "25.0",        # Amount filled so far
    "price": "0.45",               # Order price
    "outcome": "Yes",              # Token outcome side
    "created_at": "2024-01-15T10:30:00Z",
    "expiration": 0                # Unix timestamp or 0 for GTC
}
```

### Order Status Values

| Status | Description | Can Cancel | Can Fill |
|--------|-------------|------------|----------|
| `LIVE` | Order is resting on the orderbook | Yes | Yes |
| `MATCHED` | Order has been partially or fully filled | Partial only | If size remains |
| `CANCELED` | Order was cancelled (by user or expiration) | No | No |

### Get Open Orders

```python
def get_open_orders(client, market_id: str = None) -> list:
    """Get all open (LIVE) orders, optionally filtered by market.

    Args:
        client: Authenticated ClobClient
        market_id: Optional market/condition ID to filter

    Returns:
        List of open order dicts
    """
    params = {"state": "LIVE"}
    if market_id:
        params["market"] = market_id

    orders = client.get_orders(**params)

    # Process and return
    result = []
    for order in orders:
        result.append({
            "id": order.get("id"),
            "side": order.get("side"),
            "price": float(order.get("price", 0)),
            "original_size": float(order.get("original_size", 0)),
            "size_matched": float(order.get("size_matched", 0)),
            "remaining": float(order.get("original_size", 0)) - float(order.get("size_matched", 0)),
            "token_id": order.get("asset_id"),
            "market": order.get("market"),
            "created_at": order.get("created_at")
        })

    return result

# Usage
open_orders = get_open_orders(client)
print(f"You have {len(open_orders)} open orders")

for order in open_orders:
    print(f"{order['side']} {order['remaining']:.2f} @ {order['price']:.2f}")
```

### Get All Orders (Any Status)

```python
def get_all_orders(client, limit: int = 100) -> dict:
    """Get all orders with categorization by status.

    Returns:
        Dict with orders grouped by status
    """
    all_orders = client.get_orders()

    # Group by status
    grouped = {
        "live": [],
        "matched": [],
        "canceled": []
    }

    for order in all_orders[:limit]:
        status = order.get("status", "").upper()
        if status == "LIVE":
            grouped["live"].append(order)
        elif status == "MATCHED":
            grouped["matched"].append(order)
        elif status == "CANCELED":
            grouped["canceled"].append(order)

    print(f"Live: {len(grouped['live'])}")
    print(f"Matched: {len(grouped['matched'])}")
    print(f"Canceled: {len(grouped['canceled'])}")

    return grouped

# Usage
orders = get_all_orders(client)
```

### Monitor Order Until Filled

```python
import time

def wait_for_fill(client, order_id: str, timeout_seconds: int = 300, check_interval: int = 5) -> dict:
    """Wait for an order to be filled or cancelled.

    Args:
        client: Authenticated ClobClient
        order_id: Order ID to monitor
        timeout_seconds: Maximum time to wait
        check_interval: Seconds between status checks

    Returns:
        Final order status
    """
    start_time = time.time()

    while (time.time() - start_time) < timeout_seconds:
        order = client.get_order(order_id)
        status = order.get("status", "").upper()

        original = float(order.get("original_size", 0))
        matched = float(order.get("size_matched", 0))

        print(f"Status: {status}, Filled: {matched}/{original}")

        if status == "CANCELED":
            return {"status": "canceled", "order": order}

        if matched >= original:
            return {"status": "filled", "order": order}

        if status != "LIVE":
            # Order is no longer active but not fully filled
            return {"status": "partial", "filled": matched, "order": order}

        time.sleep(check_interval)

    return {"status": "timeout", "message": f"Order not filled within {timeout_seconds}s"}

# Usage
result = wait_for_fill(client, order_id, timeout_seconds=60)
if result["status"] == "filled":
    print("Order completely filled!")
```

## Batch Order Operations (CLOB-06)

### Batch Order Placement

Place multiple orders in a single API call (maximum 15 orders per batch).

```python
from py_clob_client.clob_types import OrderArgs, OrderType

def place_batch_orders(
    client,
    orders_data: list,
    order_type: OrderType = OrderType.GTC
) -> list:
    """Place multiple orders in a single batch.

    Args:
        client: Authenticated ClobClient
        orders_data: List of dicts with {token_id, price, size, side}
        order_type: Order type for all orders in batch

    Returns:
        List of results for each order

    Note:
        Maximum 15 orders per batch. Failed orders don't affect others.
    """
    if len(orders_data) > 15:
        raise ValueError("Maximum 15 orders per batch")

    # Build and sign all orders
    signed_orders = []
    for data in orders_data:
        tick_size = float(client.get_tick_size(data["token_id"]))
        validated_price = round(data["price"] / tick_size) * tick_size

        order_args = OrderArgs(
            price=validated_price,
            size=data["size"],
            side=data["side"],
            token_id=data["token_id"]
        )
        signed = client.create_order(order_args)
        signed_orders.append(signed)

    # Post batch
    responses = client.post_orders(signed_orders, order_type)

    # Process results
    results = []
    for i, resp in enumerate(responses):
        if resp.get("success"):
            results.append({
                "index": i,
                "success": True,
                "order_id": resp.get("orderID") or resp.get("orderId"),
                "status": resp.get("status")
            })
        else:
            results.append({
                "index": i,
                "success": False,
                "error": resp.get("errorMsg", "Unknown error")
            })

    # Summary
    succeeded = sum(1 for r in results if r["success"])
    print(f"Batch complete: {succeeded}/{len(results)} orders placed")

    return results

# Usage
from py_clob_client.order_builder.constants import BUY

orders_data = [
    {"token_id": token_id, "price": 0.40, "size": 20.0, "side": BUY},
    {"token_id": token_id, "price": 0.41, "size": 20.0, "side": BUY},
    {"token_id": token_id, "price": 0.42, "size": 20.0, "side": BUY},
    {"token_id": token_id, "price": 0.43, "size": 20.0, "side": BUY},
    {"token_id": token_id, "price": 0.44, "size": 20.0, "side": BUY},
]

results = place_batch_orders(client, orders_data)
```

### Batch Order Cancellation

```python
def cancel_batch_orders(client, order_ids: list) -> dict:
    """Cancel multiple orders in a single call.

    Args:
        client: Authenticated ClobClient
        order_ids: List of order IDs to cancel

    Returns:
        Cancel results
    """
    if not order_ids:
        return {"success": True, "message": "No orders to cancel"}

    response = client.cancel_orders(order_ids)

    canceled = response.get("canceled", [])
    not_canceled = response.get("not_canceled", {})

    return {
        "success": len(not_canceled) == 0,
        "canceled": len(canceled),
        "failed": len(not_canceled),
        "canceled_ids": canceled,
        "failed_details": not_canceled
    }

# Usage
order_ids = ["0x123...", "0x456...", "0x789..."]
result = cancel_batch_orders(client, order_ids)
print(f"Cancelled: {result['canceled']}, Failed: {result['failed']}")
```

### Ladder Order Creation

Create multiple orders at different price levels:

```python
from py_clob_client.order_builder.constants import BUY, SELL

def create_order_ladder(
    client,
    token_id: str,
    start_price: float,
    end_price: float,
    total_size: float,
    num_orders: int,
    side: str
) -> list:
    """Create a ladder of orders at evenly spaced price levels.

    Args:
        client: Authenticated ClobClient
        token_id: Token to trade
        start_price: First price level
        end_price: Last price level
        total_size: Total size split across orders
        num_orders: Number of orders (max 15 for single batch)
        side: "BUY" or "SELL"

    Returns:
        List of order results
    """
    if num_orders > 15:
        raise ValueError("Max 15 orders per batch")

    tick_size = float(client.get_tick_size(token_id))

    # Calculate price levels
    price_step = (end_price - start_price) / (num_orders - 1) if num_orders > 1 else 0
    size_per_order = total_size / num_orders

    orders_data = []
    for i in range(num_orders):
        price = start_price + (price_step * i)
        validated_price = round(price / tick_size) * tick_size
        validated_price = max(0.01, min(0.99, validated_price))

        orders_data.append({
            "token_id": token_id,
            "price": validated_price,
            "size": size_per_order,
            "side": BUY if side == "BUY" else SELL
        })

    return place_batch_orders(client, orders_data)

# Usage: Create 5 buy orders from 0.40 to 0.44, total 100 shares
results = create_order_ladder(
    client,
    token_id=token_id,
    start_price=0.40,
    end_price=0.44,
    total_size=100.0,
    num_orders=5,
    side="BUY"
)
```

### Batch Limits

| Operation | Limit | Notes |
|-----------|-------|-------|
| Batch POST | 15 orders | Per single API call |
| Batch DELETE | No strict limit | Use reasonable batch sizes (50-100) |
| Independent failures | Yes | One failure doesn't affect others |

**Important:** Each order in a batch is processed independently. A failure in one order does not prevent other orders from being placed or cancelled.

## Order Management Patterns

### Pattern 1: Cancel and Replace

```python
def cancel_and_replace(
    client,
    old_order_id: str,
    new_price: float,
    new_size: float = None
) -> dict:
    """Cancel an existing order and place a new one.

    Args:
        client: Authenticated ClobClient
        old_order_id: Order to cancel
        new_price: New order price
        new_size: New size (optional, uses old order size if not provided)

    Returns:
        New order result
    """
    # Get old order details
    old_order = client.get_order(old_order_id)
    token_id = old_order.get("asset_id")
    side = old_order.get("side")

    if new_size is None:
        # Use remaining size from old order
        original = float(old_order.get("original_size", 0))
        matched = float(old_order.get("size_matched", 0))
        new_size = original - matched

    # Cancel old order
    cancel_result = client.cancel(old_order_id)
    if not cancel_result.get("canceled"):
        return {"success": False, "error": "Failed to cancel old order"}

    # Place new order
    order_args = OrderArgs(
        price=new_price,
        size=new_size,
        side=BUY if side == "BUY" else SELL,
        token_id=token_id
    )
    order = client.create_order(order_args)
    response = client.post_order(order, OrderType.GTC)

    return {
        "success": response.get("success"),
        "old_order_canceled": old_order_id,
        "new_order_id": response.get("orderID") or response.get("orderId"),
        "new_price": new_price,
        "new_size": new_size
    }

# Usage
result = cancel_and_replace(client, old_order_id, new_price=0.46)
```

### Pattern 2: Cleanup Stale Orders

```python
from datetime import datetime, timedelta, timezone

def cleanup_stale_orders(client, max_age_hours: int = 24) -> dict:
    """Cancel orders older than specified age.

    Args:
        client: Authenticated ClobClient
        max_age_hours: Maximum order age in hours

    Returns:
        Cleanup results
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    orders = client.get_orders(state="LIVE")

    stale_orders = []
    for order in orders:
        created_str = order.get("created_at", "")
        if created_str:
            try:
                created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                if created < cutoff:
                    stale_orders.append(order["id"])
            except:
                pass

    if not stale_orders:
        return {"success": True, "message": "No stale orders found"}

    result = cancel_batch_orders(client, stale_orders)
    return {
        "success": True,
        "stale_found": len(stale_orders),
        "canceled": result["canceled"]
    }

# Usage: Cancel orders older than 48 hours
result = cleanup_stale_orders(client, max_age_hours=48)
```

### Pattern 3: Position-Aware Cancellation

```python
def cancel_losing_side_orders(client, token_id: str, current_price: float) -> dict:
    """Cancel orders on the wrong side of current price.

    For BUY orders: Cancel if price > current (overpaying)
    For SELL orders: Cancel if price < current (underselling)

    Args:
        client: Authenticated ClobClient
        token_id: Token to check
        current_price: Current market price

    Returns:
        Cancellation results
    """
    orders = get_open_orders(client)
    token_orders = [o for o in orders if o["token_id"] == token_id]

    to_cancel = []
    for order in token_orders:
        order_price = order["price"]
        if order["side"] == "BUY" and order_price > current_price:
            # BUY order above market - bad value
            to_cancel.append(order["id"])
        elif order["side"] == "SELL" and order_price < current_price:
            # SELL order below market - bad value
            to_cancel.append(order["id"])

    if to_cancel:
        result = cancel_batch_orders(client, to_cancel)
        return {"canceled": result["canceled"], "reason": "wrong side of market"}

    return {"canceled": 0, "message": "No orders to cancel"}

# Usage
midpoint = float(client.get_midpoint(token_id))
result = cancel_losing_side_orders(client, token_id, midpoint)
```

## Error Handling

### Common Cancellation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Order not found" | Order ID doesn't exist | Verify order ID, may already be cancelled |
| "Order already matched" | Order fully filled | No action needed |
| "Order already cancelled" | Duplicate cancel request | No action needed |
| "Unauthorized" | Not order owner | Check API credentials |

### Robust Error Handling

```python
def safe_cancel_order(client, order_id: str, max_retries: int = 3) -> dict:
    """Cancel order with retry logic and error handling.

    Args:
        client: Authenticated ClobClient
        order_id: Order to cancel
        max_retries: Retry attempts on transient errors

    Returns:
        Cancel result
    """
    import time

    for attempt in range(max_retries):
        try:
            response = client.cancel(order_id)

            if response.get("canceled"):
                return {"success": True, "order_id": order_id}

            not_canceled = response.get("not_canceled", {})
            reason = not_canceled.get(order_id, "Unknown")

            # Check if already done (not a real failure)
            if "not found" in reason.lower() or "already" in reason.lower():
                return {"success": True, "note": "Order already cancelled/filled"}

            return {"success": False, "reason": reason}

        except Exception as e:
            error_str = str(e)
            if "429" in error_str:  # Rate limited
                time.sleep(2 ** attempt)
                continue
            elif "5" in error_str[:1]:  # Server error
                time.sleep(1)
                continue
            else:
                return {"success": False, "error": error_str}

    return {"success": False, "error": f"Failed after {max_retries} attempts"}

# Usage
result = safe_cancel_order(client, order_id)
```

## Complete Management Example

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

class OrderManager:
    """Manage orders with convenient methods."""

    def __init__(self, client: ClobClient):
        self.client = client

    def get_open_orders(self, token_id: str = None) -> list:
        """Get all open orders, optionally filtered by token."""
        orders = self.client.get_orders(state="LIVE")
        if token_id:
            orders = [o for o in orders if o.get("asset_id") == token_id]
        return orders

    def cancel_all(self, token_id: str = None) -> dict:
        """Cancel all orders, optionally for specific token."""
        if token_id:
            orders = self.get_open_orders(token_id)
            if not orders:
                return {"canceled": 0}
            order_ids = [o["id"] for o in orders]
            response = self.client.cancel_orders(order_ids)
        else:
            response = self.client.cancel_all()

        return {
            "canceled": len(response.get("canceled", [])),
            "failed": len(response.get("not_canceled", {}))
        }

    def get_order_summary(self) -> dict:
        """Get summary of all orders by status."""
        all_orders = self.client.get_orders()

        live = [o for o in all_orders if o.get("status") == "LIVE"]
        matched = [o for o in all_orders if o.get("status") == "MATCHED"]

        # Calculate totals
        live_value = sum(
            float(o.get("original_size", 0)) * float(o.get("price", 0))
            for o in live
        )

        return {
            "live_count": len(live),
            "matched_count": len(matched),
            "live_value": live_value,
            "live_orders": live
        }

    def place_ladder(self, token_id: str, prices: list, size_each: float, side: str) -> list:
        """Place orders at multiple price levels."""
        orders_data = [
            {"token_id": token_id, "price": p, "size": size_each, "side": BUY if side == "BUY" else SELL}
            for p in prices
        ]
        return place_batch_orders(self.client, orders_data)

# Usage
manager = OrderManager(client)

# Get summary
summary = manager.get_order_summary()
print(f"Open orders: {summary['live_count']}")
print(f"Total value: ${summary['live_value']:.2f}")

# Cancel all for a token
result = manager.cancel_all(token_id)
print(f"Cancelled {result['canceled']} orders")

# Place a ladder
prices = [0.40, 0.41, 0.42, 0.43, 0.44]
results = manager.place_ladder(token_id, prices, size_each=20.0, side="BUY")
```

## Related Documentation

- [Order Placement](./order-placement.md) - Creating and submitting orders
- [Order Types](./order-types.md) - GTC, GTD, FOK, FAK order types
- [Positions and Balances](./positions-and-balances.md) - Checking positions before trading
- [CLOB API Overview](./clob-api-overview.md) - API architecture

## References

- [Polymarket CLOB Orders](https://docs.polymarket.com/developers/CLOB/orders) - Official documentation
- [py-clob-client](https://github.com/Polymarket/py-clob-client) - Python client library
