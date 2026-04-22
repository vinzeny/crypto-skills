# Market Channel - Orderbook & Price Streaming

Complete guide to streaming real-time orderbook and price data from Polymarket's market WebSocket channel.

## Overview

The market channel provides:
- **Orderbook snapshots** - Full depth on subscription
- **Price changes** - Incremental orderbook updates
- **Trade executions** - Last trade price notifications
- **Tick size changes** - Dynamic pricing precision updates

**Endpoint:** `wss://ws-subscriptions-clob.polymarket.com/ws/market`

**Authentication:** Not required (public data)

## Connection & Subscription

### Basic Connection

```python
import asyncio
import websockets
import json

MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

async def subscribe_to_market(token_ids: list, callback):
    """Subscribe to market channel for orderbook updates.

    Args:
        token_ids: List of token IDs (asset_ids) to subscribe to
        callback: Async function to process incoming data
    """
    async with websockets.connect(MARKET_WS) as ws:
        # Send subscription message
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": token_ids
        }))

        # Process messages
        async for message in ws:
            data = json.loads(message)
            await callback(data)
```

### Subscription Message Format

```python
{
    "type": "market",
    "assets_ids": [
        "71321045679252212594626385532706912750332728571942532289631379312455583992563",
        "72549165387050808959290263609189958849215668938434754142373413659789425508885"
    ]
}
```

**Key points:**
- Use `assets_ids` (token IDs), not condition IDs
- Each market has two tokens: YES and NO
- Subscribe to both tokens to see full market activity
- Get token IDs from the REST API `/markets` endpoint

## Event Types

### 1. Orderbook Snapshot (`book`)

Received immediately after subscription and periodically for resync:

```python
# "book" event - Full orderbook snapshot
{
    "event_type": "book",
    "asset_id": "71321045679252212594626385532706912750332728571942532289631379312455583992563",
    "market": "0x...",  # Condition ID
    "timestamp": 1705320000,
    "bids": [
        {"price": "0.45", "size": "1000.0"},
        {"price": "0.44", "size": "500.0"},
        {"price": "0.43", "size": "2500.0"}
    ],
    "asks": [
        {"price": "0.46", "size": "800.0"},
        {"price": "0.47", "size": "600.0"},
        {"price": "0.48", "size": "1200.0"}
    ],
    "hash": "abc123..."  # Book state hash for sync verification
}
```

**Processing guidance:**
- Replace your entire local orderbook with this snapshot
- `bids` are sorted highest price first
- `asks` are sorted lowest price first
- Prices and sizes are strings (avoid float precision issues)
- Use `hash` to verify sync state if needed

### 2. Price Change (`price_change`)

Incremental updates to individual orderbook levels:

```python
# "price_change" event - Incremental update
{
    "event_type": "price_change",
    "asset_id": "71321045679252212594626385532706912750332728571942532289631379312455583992563",
    "market": "0x...",
    "timestamp": 1705320001,
    "price": "0.46",
    "side": "ask",    # "ask" or "bid"
    "size": "1200.0"  # New size at this level
}
```

**Processing guidance:**
- `size = "0.0"` means the level was removed
- `size > 0` means update or add this level
- Side indicates which book to update
- Apply incrementally to maintain local orderbook

### 3. Last Trade Price (`last_trade_price`)

Notification when a trade executes:

```python
# "last_trade_price" event - Trade executed
{
    "event_type": "last_trade_price",
    "asset_id": "71321045679252212594626385532706912750332728571942532289631379312455583992563",
    "market": "0x...",
    "timestamp": 1705320002,
    "price": "0.455",
    "size": "50.0",
    "side": "buy"  # Taker side: "buy" or "sell"
}
```

**Processing guidance:**
- `side` indicates the taker's direction
- `buy` = taker bought (lifted ask)
- `sell` = taker sold (hit bid)
- Use for trade tape display or volume tracking

### 4. Tick Size Change (`tick_size_change`)

Dynamic tick size adjustment when price crosses thresholds:

```python
# "tick_size_change" event - Tick size updated
{
    "event_type": "tick_size_change",
    "asset_id": "71321045679252212594626385532706912750332728571942532289631379312455583992563",
    "market": "0x...",
    "timestamp": 1705320003,
    "old_tick_size": "0.01",
    "new_tick_size": "0.001"
}
```

**Tick size rules:**
| Price Range | Tick Size |
|-------------|-----------|
| 0.04 - 0.96 | 0.01 |
| < 0.04 | 0.001 |
| > 0.96 | 0.001 |

**Processing guidance:**
- Adjust order price validation to new tick size
- Smaller tick size allows finer price granularity
- Existing orders at invalid prices may be cancelled

## Maintaining a Local Orderbook

### OrderbookManager Class

A complete implementation for managing local orderbook state:

```python
from typing import Dict, Optional, List
from decimal import Decimal

class OrderbookManager:
    """Manages local orderbook state with WebSocket updates."""

    def __init__(self):
        # asset_id -> {"bids": {price: size}, "asks": {price: size}}
        self.books: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.last_update: Dict[str, int] = {}  # asset_id -> timestamp

    async def handle_message(self, data: dict):
        """Process incoming WebSocket message."""
        event_type = data.get("event_type")
        asset_id = data.get("asset_id")

        if not event_type or not asset_id:
            return

        if event_type == "book":
            self._handle_snapshot(data)
        elif event_type == "price_change":
            self._handle_update(data)
        elif event_type == "last_trade_price":
            self._handle_trade(data)
        elif event_type == "tick_size_change":
            self._handle_tick_change(data)

    def _handle_snapshot(self, data: dict):
        """Process full orderbook snapshot."""
        asset_id = data["asset_id"]

        # Replace entire book
        self.books[asset_id] = {
            "bids": {b["price"]: b["size"] for b in data.get("bids", [])},
            "asks": {a["price"]: a["size"] for a in data.get("asks", [])}
        }
        self.last_update[asset_id] = data.get("timestamp", 0)

    def _handle_update(self, data: dict):
        """Process incremental price change."""
        asset_id = data["asset_id"]
        side = "bids" if data["side"] == "bid" else "asks"
        price = data["price"]
        size = data["size"]

        # Initialize book if needed
        if asset_id not in self.books:
            self.books[asset_id] = {"bids": {}, "asks": {}}

        # Update or remove level
        if Decimal(size) == 0:
            self.books[asset_id][side].pop(price, None)
        else:
            self.books[asset_id][side][price] = size

        self.last_update[asset_id] = data.get("timestamp", 0)

    def _handle_trade(self, data: dict):
        """Process trade notification (for logging/display)."""
        # Trade doesn't change orderbook state directly
        # (the orderbook changes come via price_change events)
        pass

    def _handle_tick_change(self, data: dict):
        """Process tick size change notification."""
        # Log for awareness - may need to adjust order validation
        asset_id = data["asset_id"]
        old = data.get("old_tick_size")
        new = data.get("new_tick_size")
        print(f"Tick size changed for {asset_id[:20]}...: {old} -> {new}")

    def get_best_bid(self, asset_id: str) -> Optional[str]:
        """Get highest bid price."""
        bids = self.books.get(asset_id, {}).get("bids", {})
        if bids:
            return max(bids.keys(), key=lambda x: Decimal(x))
        return None

    def get_best_ask(self, asset_id: str) -> Optional[str]:
        """Get lowest ask price."""
        asks = self.books.get(asset_id, {}).get("asks", {})
        if asks:
            return min(asks.keys(), key=lambda x: Decimal(x))
        return None

    def get_mid_price(self, asset_id: str) -> Optional[Decimal]:
        """Calculate mid price."""
        best_bid = self.get_best_bid(asset_id)
        best_ask = self.get_best_ask(asset_id)

        if best_bid and best_ask:
            return (Decimal(best_bid) + Decimal(best_ask)) / 2
        return None

    def get_spread(self, asset_id: str) -> Optional[Decimal]:
        """Calculate bid-ask spread."""
        best_bid = self.get_best_bid(asset_id)
        best_ask = self.get_best_ask(asset_id)

        if best_bid and best_ask:
            return Decimal(best_ask) - Decimal(best_bid)
        return None

    def get_depth(self, asset_id: str, side: str, levels: int = 5) -> List[tuple]:
        """Get top N levels of depth for a side.

        Returns list of (price, size) tuples sorted appropriately.
        """
        book_side = self.books.get(asset_id, {}).get(side, {})

        if side == "bids":
            # Bids sorted highest first
            sorted_levels = sorted(
                book_side.items(),
                key=lambda x: Decimal(x[0]),
                reverse=True
            )
        else:
            # Asks sorted lowest first
            sorted_levels = sorted(
                book_side.items(),
                key=lambda x: Decimal(x[0])
            )

        return sorted_levels[:levels]

    def get_total_liquidity(self, asset_id: str, side: str) -> Decimal:
        """Calculate total size on one side of the book."""
        book_side = self.books.get(asset_id, {}).get(side, {})
        return sum(Decimal(size) for size in book_side.values())
```

### Using the OrderbookManager

```python
import asyncio
import websockets
import json

MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

async def stream_with_orderbook(token_ids: list):
    """Stream and maintain orderbook state."""
    manager = OrderbookManager()

    async with websockets.connect(MARKET_WS) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": token_ids
        }))

        async for message in ws:
            data = json.loads(message)
            await manager.handle_message(data)

            # Example: Print current state after each update
            for token_id in token_ids:
                bid = manager.get_best_bid(token_id)
                ask = manager.get_best_ask(token_id)
                spread = manager.get_spread(token_id)

                if bid and ask:
                    print(f"[{token_id[:12]}...] Bid: {bid} | Ask: {ask} | Spread: {spread}")
```

## Multiple Market Subscription

### Subscribing to Multiple Markets

You can subscribe to multiple markets in a single connection:

```python
async def subscribe_multiple_markets(token_ids: list):
    """Subscribe to multiple markets in one connection.

    Args:
        token_ids: List of token IDs (can include both YES and NO tokens)
    """
    async with websockets.connect(MARKET_WS) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": token_ids  # Up to ~100 markets recommended
        }))

        async for message in ws:
            data = json.loads(message)
            asset_id = data.get("asset_id")
            event_type = data.get("event_type")

            # Route to appropriate handler based on asset
            print(f"[{asset_id[:12]}...] {event_type}")
```

**Recommendations:**
- Subscribe to both YES and NO tokens for complete market view
- Limit to ~100 markets per connection for performance
- Use multiple connections for larger portfolios
- Consider separate connections for different update frequencies

### Market Routing Example

```python
class MultiMarketHandler:
    """Handle updates for multiple markets with callbacks."""

    def __init__(self):
        self.handlers = {}  # asset_id -> callback

    def register(self, asset_id: str, callback):
        """Register handler for specific asset."""
        self.handlers[asset_id] = callback

    async def handle(self, data: dict):
        """Route message to appropriate handler."""
        asset_id = data.get("asset_id")
        if asset_id and asset_id in self.handlers:
            await self.handlers[asset_id](data)

# Usage
handler = MultiMarketHandler()
handler.register("token_1", my_callback_1)
handler.register("token_2", my_callback_2)
```

## Practical Price Streaming Examples

### Time-Limited Streaming

```python
import time

async def stream_prices(token_id: str, duration_seconds: int = 60):
    """Stream price updates for a specified duration.

    Args:
        token_id: The token ID to stream
        duration_seconds: How long to stream (default 60 seconds)
    """
    end_time = time.time() + duration_seconds

    async with websockets.connect(MARKET_WS) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": [token_id]
        }))

        print(f"Streaming {token_id[:20]}... for {duration_seconds}s")

        async for message in ws:
            if time.time() > end_time:
                break

            data = json.loads(message)
            event_type = data.get("event_type")

            if event_type == "last_trade_price":
                print(f"TRADE: {data['price']} x {data['size']} ({data['side']})")

            elif event_type == "price_change":
                action = "DEL" if data['size'] == "0.0" else "UPD"
                print(f"BOOK:  {data['side'].upper()} {data['price']} = {data['size']} [{action}]")

            elif event_type == "book":
                print(f"SNAPSHOT: {len(data['bids'])} bids, {len(data['asks'])} asks")

    print("Streaming complete")
```

### Price Aggregation

```python
from collections import deque
from decimal import Decimal
from statistics import mean, stdev

class PriceTracker:
    """Track and analyze price movements."""

    def __init__(self, window_size: int = 100):
        self.trades = deque(maxlen=window_size)
        self.mid_prices = deque(maxlen=window_size)

    def add_trade(self, price: str, size: str, side: str):
        """Record a trade."""
        self.trades.append({
            "price": Decimal(price),
            "size": Decimal(size),
            "side": side,
            "time": time.time()
        })

    def add_mid_price(self, mid: Decimal):
        """Record mid price."""
        self.mid_prices.append(mid)

    def get_vwap(self) -> Optional[Decimal]:
        """Calculate volume-weighted average price."""
        if not self.trades:
            return None

        total_value = sum(t["price"] * t["size"] for t in self.trades)
        total_volume = sum(t["size"] for t in self.trades)

        if total_volume > 0:
            return total_value / total_volume
        return None

    def get_volatility(self) -> Optional[float]:
        """Calculate mid price volatility (std dev)."""
        if len(self.mid_prices) < 2:
            return None

        prices = [float(p) for p in self.mid_prices]
        return stdev(prices)

    def get_trade_count(self) -> int:
        """Count trades in window."""
        return len(self.trades)

    def get_volume(self) -> Decimal:
        """Calculate total volume in window."""
        return sum(t["size"] for t in self.trades)
```

### Alert on Price Movement

```python
from decimal import Decimal

async def price_alert(token_id: str, threshold: Decimal):
    """Alert when price moves more than threshold from baseline.

    Args:
        token_id: Token to monitor
        threshold: Price movement threshold (e.g., Decimal("0.05") for 5 cents)
    """
    manager = OrderbookManager()
    baseline_mid = None

    async with websockets.connect(MARKET_WS) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": [token_id]
        }))

        async for message in ws:
            data = json.loads(message)
            await manager.handle_message(data)

            current_mid = manager.get_mid_price(token_id)

            if current_mid:
                if baseline_mid is None:
                    baseline_mid = current_mid
                    print(f"Baseline mid price: {baseline_mid}")
                else:
                    movement = abs(current_mid - baseline_mid)
                    if movement >= threshold:
                        direction = "UP" if current_mid > baseline_mid else "DOWN"
                        print(f"ALERT: Price moved {direction} by {movement}")
                        print(f"  Baseline: {baseline_mid}")
                        print(f"  Current:  {current_mid}")
                        baseline_mid = current_mid  # Reset baseline
```

## Best Practices

### 1. Use Decimal for Prices

Always use `Decimal` instead of `float` for price calculations:

```python
from decimal import Decimal

# Good
price = Decimal("0.45")
size = Decimal("100.0")
value = price * size

# Bad - floating point errors
price = 0.45
size = 100.0
value = price * size  # May have precision issues
```

### 2. Handle Disconnections

WebSocket connections can drop. Implement reconnection:

```python
async def resilient_stream(token_ids: list, max_retries: int = 5):
    """Stream with automatic reconnection."""
    retries = 0

    while retries < max_retries:
        try:
            async with websockets.connect(MARKET_WS) as ws:
                await ws.send(json.dumps({
                    "type": "market",
                    "assets_ids": token_ids
                }))

                retries = 0  # Reset on successful connection

                async for message in ws:
                    data = json.loads(message)
                    yield data

        except websockets.exceptions.ConnectionClosed:
            retries += 1
            print(f"Connection closed. Retry {retries}/{max_retries}")
            await asyncio.sleep(2 ** retries)  # Exponential backoff

    print("Max retries exceeded")
```

### 3. Validate Orderbook Integrity

Occasionally verify your local state matches server:

```python
def validate_book(self, asset_id: str) -> bool:
    """Check orderbook makes sense."""
    best_bid = self.get_best_bid(asset_id)
    best_ask = self.get_best_ask(asset_id)

    if best_bid and best_ask:
        # Bid should always be less than ask
        if Decimal(best_bid) >= Decimal(best_ask):
            print(f"WARNING: Crossed book! Bid {best_bid} >= Ask {best_ask}")
            return False

    return True
```

### 4. Process Messages Quickly

Don't block the message loop with slow operations:

```python
# Good - Non-blocking processing
async def handle_message(self, data):
    event_type = data.get("event_type")
    if event_type == "book":
        # Quick update
        self._handle_snapshot(data)
        # Schedule slow work separately
        asyncio.create_task(self._analyze_book(data))

# Bad - Blocking the loop
async def handle_message(self, data):
    event_type = data.get("event_type")
    if event_type == "book":
        self._handle_snapshot(data)
        await self._slow_database_write(data)  # Blocks other messages!
```

## Common Issues

### Messages Stop Arriving

**Symptom:** Data streams initially but stops after ~20 minutes

**Cause:** Connection timeout or server-side disconnect

**Solution:** Implement heartbeat pings and reconnection logic. See [Connection Management](./connection-management.md) for patterns.

### Orderbook Gets Out of Sync

**Symptom:** Local orderbook diverges from actual market state

**Cause:** Missed `price_change` messages

**Solution:**
1. Track message sequence/timestamps
2. If gap detected, wait for next `book` snapshot
3. Consider periodic full refresh

### High Memory Usage

**Symptom:** Memory grows over time

**Cause:** Storing too much history or not cleaning up old data

**Solution:**
1. Use bounded data structures (`deque(maxlen=N)`)
2. Clear old data periodically
3. Only store what you need

## Related Documentation

- **[WebSocket Overview](./websocket-overview.md)** - Architecture and connection basics
- **[User Channel](./user-channel.md)** - Order notifications (coming in Plan 08)
- **[Connection Management](./connection-management.md)** - Reconnection patterns (coming in Plan 08)
- **[Market Discovery](../market-discovery/)** - Get token IDs to subscribe

---

**Last updated:** 2026-01-31
**Status:** Phase 2 - Core API Documentation
