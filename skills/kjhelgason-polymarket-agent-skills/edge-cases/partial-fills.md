# Partial Fill Tracking and Reconciliation

Complete guide to tracking partial order fills and reconciling positions on Polymarket.

**Covers:** EDGE-09 (Partial Fill Tracking)

## Why Partial Fills Matter

Partial fills occur when orders execute incrementally rather than all at once:

- **GTC orders** fill incrementally over time as counterparties match
- **FAK orders** fill best-effort, with remainder cancelled immediately
- **Position tracking** requires accurate fill data for P&L calculation
- **Tax/accounting** needs complete fill history for cost basis

Understanding partial fills is essential for:
1. Accurate position management
2. Cost basis calculation for taxes
3. Order execution quality analysis
4. Portfolio reconciliation

For order status checking patterns, see [order-management.md](../trading/order-management.md).

## Order Response Fields

When querying order status, these fields track fill progress:

| Field | Type | Description |
|-------|------|-------------|
| `original_size` | float | Original order size requested |
| `size_matched` | float | Amount that has filled so far |
| `price_average` | float | Weighted average fill price |
| `status` | string | Current order status |
| `transactTime` | string | Last transaction timestamp |

### Status Values and Fill Implications

| Status | Partial Fills? | Meaning |
|--------|----------------|---------|
| `LIVE` | Yes, ongoing | Order resting on book, may have partial fills |
| `MATCHED` | Complete | Order fully filled |
| `CANCELED` | Possible | Order cancelled (may have partial fills before cancel) |

## Order Types and Partial Fill Behavior

| Order Type | Partial Fills? | Behavior |
|------------|----------------|----------|
| GTC (Good Till Cancel) | Yes | Fills incrementally over time, rests on book |
| GTD (Good Till Date) | Yes | Fills until expiration timestamp |
| FOK (Fill Or Kill) | No | All or nothing - full fill or rejection |
| FAK (Fill And Kill) | Yes | Best effort immediate fill, remainder cancelled |

### FOK vs FAK for Partial Fills

```python
# FOK: Never partial - all or nothing
# If you need 100 shares at 0.45, FOK either fills all 100 or rejects

# FAK: Immediate partial - remainder dies
# If book has 60 shares at 0.45, FAK fills 60, cancels the remaining 40

# GTC: Accumulating partial - remainder waits
# If book has 60 shares at 0.45, GTC fills 60, leaves 40 resting
```

## PartialFillTracker Class

Complete implementation for tracking partial fills across the order lifecycle:

```python
from datetime import datetime
from typing import Optional


class PartialFillTracker:
    """Track partial fills for order reconciliation.

    Key responsibilities:
    - Track original order size and filled amount
    - Record individual fill events with prices
    - Calculate weighted average fill price
    - Detect fill status (pending, partial, filled, cancelled)

    Usage:
        tracker = PartialFillTracker()
        tracker.track_order(order_id, original_size)
        # Later, on status updates:
        tracker.update_from_response(order_status_response)
        summary = tracker.get_fill_summary(order_id)
    """

    def __init__(self):
        self.orders = {}  # order_id -> order state

    def track_order(self, order_id: str, original_size: float) -> None:
        """Start tracking a new order.

        Args:
            order_id: Order ID from post_order response
            original_size: Original order size
        """
        self.orders[order_id] = {
            "original_size": original_size,
            "filled_size": 0.0,
            "remaining_size": original_size,
            "fills": [],  # List of fill records
            "weighted_price_sum": 0.0,  # For avg price calculation
            "avg_price": None,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": None
        }

    def update_from_response(self, response: dict) -> Optional[dict]:
        """Update tracking from order response.

        Args:
            response: Order status response from API

        Returns:
            Fill event dict if new fill occurred, None otherwise
        """
        # Handle both orderID and orderId formats
        order_id = response.get("orderID") or response.get("orderId") or response.get("id")
        if not order_id or order_id not in self.orders:
            return None

        order = self.orders[order_id]

        # Get current matched size
        size_matched = float(response.get("size_matched", 0))
        previous_filled = order["filled_size"]

        fill_event = None

        # Check for new fill
        if size_matched > previous_filled:
            new_fill_size = size_matched - previous_filled
            fill_price = float(response.get("price_average", response.get("price", 0)))

            # Record fill event
            fill_event = {
                "size": new_fill_size,
                "price": fill_price,
                "time": response.get("transactTime", datetime.utcnow().isoformat()),
                "cumulative_filled": size_matched
            }
            order["fills"].append(fill_event)

            # Update weighted price sum for average calculation
            order["weighted_price_sum"] += new_fill_size * fill_price

            # Update totals
            order["filled_size"] = size_matched
            order["remaining_size"] = order["original_size"] - size_matched

            # Calculate new average price
            if order["filled_size"] > 0:
                order["avg_price"] = order["weighted_price_sum"] / order["filled_size"]

        # Update status
        api_status = response.get("status", "").upper()
        if size_matched >= order["original_size"]:
            order["status"] = "filled"
        elif api_status == "LIVE":
            order["status"] = "partial" if size_matched > 0 else "pending"
        elif api_status == "CANCELED":
            order["status"] = "cancelled"
        elif api_status == "MATCHED":
            order["status"] = "filled"
        else:
            order["status"] = api_status.lower() if api_status else order["status"]

        order["last_updated"] = datetime.utcnow().isoformat()

        return fill_event

    def get_fill_summary(self, order_id: str) -> Optional[dict]:
        """Get comprehensive fill summary for an order.

        Args:
            order_id: Order ID to query

        Returns:
            Summary dict or None if order not tracked
        """
        if order_id not in self.orders:
            return None

        order = self.orders[order_id]

        return {
            "order_id": order_id,
            "original_size": order["original_size"],
            "filled_size": order["filled_size"],
            "remaining_size": order["remaining_size"],
            "fill_count": len(order["fills"]),
            "avg_price": order["avg_price"],
            "status": order["status"],
            "fill_percentage": (
                order["filled_size"] / order["original_size"] * 100
                if order["original_size"] > 0 else 0
            ),
            "fills": order["fills"],
            "created_at": order["created_at"],
            "last_updated": order["last_updated"]
        }

    def get_all_active(self) -> list:
        """Get all orders with pending fills.

        Returns:
            List of order IDs with status pending or partial
        """
        return [
            order_id for order_id, order in self.orders.items()
            if order["status"] in ["pending", "partial"]
        ]

    def get_total_exposure(self) -> dict:
        """Calculate total exposure across all tracked orders.

        Returns:
            Exposure summary by status
        """
        exposure = {
            "pending_size": 0.0,
            "filled_size": 0.0,
            "pending_count": 0,
            "filled_count": 0,
            "partial_count": 0
        }

        for order in self.orders.values():
            exposure["filled_size"] += order["filled_size"]
            exposure["pending_size"] += order["remaining_size"]

            if order["status"] == "pending":
                exposure["pending_count"] += 1
            elif order["status"] == "filled":
                exposure["filled_count"] += 1
            elif order["status"] == "partial":
                exposure["partial_count"] += 1

        return exposure

    def remove_order(self, order_id: str) -> bool:
        """Remove order from tracking (e.g., after reconciliation).

        Returns:
            True if removed, False if not found
        """
        if order_id in self.orders:
            del self.orders[order_id]
            return True
        return False
```

## Reconciliation Patterns

### Pattern 1: Real-time Tracking (WebSocket)

Subscribe to user channel for immediate fill notifications:

```python
import asyncio
import websockets
import json

class RealTimeFillTracker:
    """Track fills in real-time via WebSocket."""

    def __init__(self, tracker: PartialFillTracker):
        self.tracker = tracker
        self.ws = None

    async def connect_and_track(self, ws_url: str, api_key: str):
        """Connect to WebSocket and track fill events."""
        async with websockets.connect(ws_url) as ws:
            self.ws = ws

            # Subscribe to user channel
            subscribe_msg = {
                "auth": {"apiKey": api_key},
                "type": "subscribe",
                "channel": "user",
                "markets": []  # All markets
            }
            await ws.send(json.dumps(subscribe_msg))

            # Process messages
            async for message in ws:
                data = json.loads(message)
                await self.handle_message(data)

    async def handle_message(self, data: dict):
        """Handle incoming WebSocket message."""
        event_type = data.get("event_type")

        if event_type == "order":
            # Order update (creation, fill, cancel)
            for order in data.get("orders", []):
                fill_event = self.tracker.update_from_response(order)
                if fill_event:
                    print(f"Fill: {fill_event['size']} @ {fill_event['price']}")

        elif event_type == "order_fill":
            # Direct fill notification
            order_id = data.get("orderId")
            fill_event = self.tracker.update_from_response(data)
            if fill_event:
                summary = self.tracker.get_fill_summary(order_id)
                print(f"Fill update: {summary['filled_size']}/{summary['original_size']}")

# Usage
tracker = PartialFillTracker()
realtime = RealTimeFillTracker(tracker)

# Start order
response = client.post_order(signed_order, OrderType.GTC)
order_id = response.get("orderID")
tracker.track_order(order_id, original_size=100.0)

# Run WebSocket in background
asyncio.create_task(realtime.connect_and_track(WS_URL, api_key))
```

### Pattern 2: Polling-based Tracking

For simpler implementations, poll order status periodically:

```python
import time


def poll_order_fills(
    client,
    tracker: PartialFillTracker,
    poll_interval: float = 5.0,
    timeout: float = 300.0
) -> dict:
    """Poll for fill updates on all tracked orders.

    Args:
        client: Authenticated ClobClient
        tracker: PartialFillTracker instance
        poll_interval: Seconds between polls
        timeout: Maximum time to poll

    Returns:
        Final summary of all orders
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        active_orders = tracker.get_all_active()

        if not active_orders:
            print("All orders complete")
            break

        for order_id in active_orders:
            try:
                status = client.get_order(order_id)
                fill_event = tracker.update_from_response(status)

                if fill_event:
                    summary = tracker.get_fill_summary(order_id)
                    print(
                        f"[{order_id[:8]}] "
                        f"Filled: {summary['filled_size']:.2f}/{summary['original_size']:.2f} "
                        f"({summary['fill_percentage']:.1f}%)"
                    )

            except Exception as e:
                print(f"Error polling {order_id}: {e}")

        time.sleep(poll_interval)

    # Return final state
    return {
        order_id: tracker.get_fill_summary(order_id)
        for order_id in tracker.orders.keys()
    }

# Usage
tracker = PartialFillTracker()

# Place orders
for order in orders_to_place:
    response = client.post_order(order, OrderType.GTC)
    tracker.track_order(response["orderID"], order.size)

# Poll until filled
results = poll_order_fills(client, tracker, poll_interval=5.0, timeout=60.0)
```

### Pattern 3: End-of-day Reconciliation

Compare expected positions from fills against actual positions:

```python
import requests

DATA_API_URL = "https://data-api.polymarket.com"


def reconcile_positions(
    tracker: PartialFillTracker,
    address: str
) -> dict:
    """Reconcile tracked fills against actual positions.

    Args:
        tracker: PartialFillTracker with filled orders
        address: Trading wallet address

    Returns:
        Reconciliation results with discrepancies
    """
    # Get actual positions from Data API
    response = requests.get(
        f"{DATA_API_URL}/positions",
        params={"user": address}
    )
    response.raise_for_status()
    actual_positions = response.json()

    # Build position map from actual
    actual_by_token = {}
    for pos in actual_positions:
        token_id = pos.get("asset") or pos.get("tokenId")
        actual_by_token[token_id] = float(pos.get("size", 0))

    # Calculate expected from fills
    expected_by_token = {}
    for order_id, order in tracker.orders.items():
        if order["status"] in ["filled", "partial"]:
            # Would need token_id tracking - extend tracker as needed
            # For now, show the pattern
            pass

    # Compare and find discrepancies
    discrepancies = []
    for token_id in set(list(actual_by_token.keys()) + list(expected_by_token.keys())):
        actual = actual_by_token.get(token_id, 0.0)
        expected = expected_by_token.get(token_id, 0.0)

        if abs(actual - expected) > 0.01:  # 1 cent tolerance
            discrepancies.append({
                "token_id": token_id,
                "expected": expected,
                "actual": actual,
                "difference": actual - expected
            })

    return {
        "total_positions": len(actual_positions),
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
        "is_reconciled": len(discrepancies) == 0
    }
```

## Complete Example: Track and Reconcile

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
import time


def trade_with_tracking(client: ClobClient, token_id: str, size: float, price: float):
    """Complete example of placing order and tracking fills."""

    # Initialize tracker
    tracker = PartialFillTracker()

    # Create and place order
    order_args = OrderArgs(
        price=price,
        size=size,
        side=BUY,
        token_id=token_id
    )
    signed_order = client.create_order(order_args)
    response = client.post_order(signed_order, OrderType.GTC)

    order_id = response.get("orderID") or response.get("orderId")
    print(f"Order placed: {order_id}")

    # Start tracking
    tracker.track_order(order_id, size)

    # Poll for fills
    while True:
        status = client.get_order(order_id)
        fill_event = tracker.update_from_response(status)

        summary = tracker.get_fill_summary(order_id)
        print(f"Filled: {summary['filled_size']:.2f} / {summary['original_size']:.2f}")
        print(f"Remaining: {summary['remaining_size']:.2f}")

        if summary["avg_price"]:
            print(f"Avg Price: {summary['avg_price']:.4f}")

        if summary["status"] in ["filled", "cancelled"]:
            break

        time.sleep(5)

    # Final summary
    final = tracker.get_fill_summary(order_id)
    print("\n=== FINAL SUMMARY ===")
    print(f"Status: {final['status']}")
    print(f"Total Filled: {final['filled_size']:.2f}")
    print(f"Average Price: {final['avg_price']:.4f}" if final['avg_price'] else "No fills")
    print(f"Fill Count: {final['fill_count']}")

    # List individual fills
    if final['fills']:
        print("\nIndividual Fills:")
        for i, fill in enumerate(final['fills'], 1):
            print(f"  {i}. {fill['size']:.2f} @ {fill['price']:.4f}")

    return final


# Usage
# final = trade_with_tracking(client, token_id, size=100.0, price=0.45)
```

## Extended Tracker with Token Support

For multi-token position reconciliation:

```python
class ExtendedFillTracker(PartialFillTracker):
    """Extended tracker with token-level aggregation."""

    def track_order(
        self,
        order_id: str,
        original_size: float,
        token_id: str = None,
        side: str = None
    ) -> None:
        """Track order with token and side info."""
        super().track_order(order_id, original_size)
        self.orders[order_id]["token_id"] = token_id
        self.orders[order_id]["side"] = side

    def get_position_by_token(self, token_id: str) -> dict:
        """Get net position for a specific token.

        Returns:
            Position summary with buys, sells, and net
        """
        bought = 0.0
        sold = 0.0
        buy_cost = 0.0
        sell_proceeds = 0.0

        for order in self.orders.values():
            if order.get("token_id") != token_id:
                continue

            filled = order["filled_size"]
            avg_price = order.get("avg_price", 0)

            if order.get("side") == "BUY":
                bought += filled
                buy_cost += filled * avg_price
            elif order.get("side") == "SELL":
                sold += filled
                sell_proceeds += filled * avg_price

        net_position = bought - sold
        avg_cost = buy_cost / bought if bought > 0 else 0

        return {
            "token_id": token_id,
            "bought": bought,
            "sold": sold,
            "net_position": net_position,
            "buy_cost": buy_cost,
            "sell_proceeds": sell_proceeds,
            "avg_buy_price": avg_cost,
            "realized_pnl": sell_proceeds - (sold * avg_cost) if sold > 0 else 0
        }
```

## Common Issues

### Issue 1: Stale Fill Data

**Symptom:** Tracker shows different fill than actual position

**Cause:** Missed WebSocket event or polling gap

**Solution:**
```python
def force_sync(client, tracker: PartialFillTracker, order_id: str):
    """Force sync tracker with current API state."""
    status = client.get_order(order_id)
    # Reset and update
    if order_id in tracker.orders:
        tracker.orders[order_id]["filled_size"] = 0.0
        tracker.orders[order_id]["fills"] = []
        tracker.orders[order_id]["weighted_price_sum"] = 0.0
    tracker.update_from_response(status)
```

### Issue 2: Cancelled Order with Partial Fill

**Symptom:** Order cancelled but tracker shows "partial" not accurate

**Solution:** Check `size_matched` even for cancelled orders:
```python
# Even CANCELED orders can have size_matched > 0
if status["status"] == "CANCELED":
    matched = float(status.get("size_matched", 0))
    if matched > 0:
        print(f"Partial fill before cancel: {matched}")
```

### Issue 3: Price Average Confusion

**Symptom:** `price_average` differs from expected weighted average

**Cause:** API returns cumulative average, not per-fill price

**Solution:** Track individual fills for precise cost basis:
```python
# API price_average is cumulative - use fills list for precision
for fill in tracker.get_fill_summary(order_id)["fills"]:
    print(f"Fill: {fill['size']} @ {fill['price']}")
```

## Related Documentation

- [Order Management](../trading/order-management.md) - Order status and lifecycle
- [Order Types](../trading/order-types.md) - GTC, GTD, FOK, FAK behavior
- [Connection Management](../real-time/connection-management.md) - WebSocket user channel
- [Tax and Accounting](../trading/positions-and-balances.md) - Cost basis tracking

---

**Last updated:** 2026-01-31
**Covers:** EDGE-09 (Partial Fill Tracking)
