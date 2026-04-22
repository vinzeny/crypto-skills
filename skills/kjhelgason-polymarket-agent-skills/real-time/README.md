# Polymarket Real-Time Data Streaming

Complete guide to streaming real-time market data from Polymarket using WebSocket connections.

## Quick Start

**Fastest path to streaming market data:**

```python
import asyncio
import websockets
import json

MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

async def stream_prices(token_id: str):
    """Stream live price updates for a market."""
    async with websockets.connect(MARKET_WS) as ws:
        # Subscribe to market
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": [token_id]
        }))

        # Process updates
        async for message in ws:
            data = json.loads(message)
            event = data.get("event_type")

            if event == "book":
                print(f"Orderbook: {len(data['bids'])} bids, {len(data['asks'])} asks")
            elif event == "price_change":
                print(f"Update: {data['side']} {data['price']} = {data['size']}")
            elif event == "last_trade_price":
                print(f"Trade: {data['price']} x {data['size']}")

# Get token_id from market discovery, then run:
# asyncio.run(stream_prices("your_token_id_here"))
```

**Next steps:**
1. Get token IDs from [Market Discovery](../market-discovery/)
2. Read [WebSocket Overview](./websocket-overview.md) for architecture
3. See [Market Channel](./market-channel.md) for orderbook patterns

## Prerequisites

Before streaming real-time data:

- **Python 3.7+** with asyncio support
- **websockets library:** `pip install websockets`
- **Token IDs** from Market Discovery skill (or REST API)
- **API credentials** (only for user channel - order notifications)

### Installation

```bash
pip install websockets
```

**Note:** `asyncio` is included in Python standard library since 3.4.

## Documentation Index

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[websocket-overview.md](./websocket-overview.md)** | Architecture, channels, connection setup | Understanding WebSocket system |
| **[market-channel.md](./market-channel.md)** | Orderbook snapshots, price changes, trades | Implementing market data streaming |
| **[user-channel.md](./user-channel.md)** | Order fills, trade confirmations | Tracking order status |
| **[connection-management.md](./connection-management.md)** | Reconnection, heartbeats, error handling | Production reliability |

### Reading Order

**For basic market streaming:**
1. Start with this README for quick start
2. Read [websocket-overview.md](./websocket-overview.md) for channel architecture
3. Implement using [market-channel.md](./market-channel.md) patterns

**For order tracking:**
1. Complete market channel setup first
2. Configure API credentials ([auth skill](../auth/))
3. Read [user-channel.md](./user-channel.md) for authenticated streams

**For production deployment:**
1. Implement basic streaming first
2. Add [connection-management.md](./connection-management.md) patterns
3. Test reconnection and error handling

## Channel Quick Reference

| Need | Channel | Auth Required | Documentation |
|------|---------|---------------|---------------|
| Live price updates | Market | No | [market-channel.md](./market-channel.md) |
| Orderbook depth | Market | No | [market-channel.md](./market-channel.md) |
| Trade executions | Market | No | [market-channel.md](./market-channel.md) |
| Order notifications | User | Yes | [user-channel.md](./user-channel.md) |
| Trade confirmations | User | Yes | [user-channel.md](./user-channel.md) |

### WebSocket Endpoints

```python
# Market channel - public, no auth required
MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

# User channel - private, auth required
USER_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/user"
```

## Common Use Cases

### 1. Price Display Widget

```python
async def price_widget(token_id: str):
    """Display current best bid/ask prices."""
    best_bid = None
    best_ask = None

    async with websockets.connect(MARKET_WS) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": [token_id]
        }))

        async for message in ws:
            data = json.loads(message)

            if data.get("event_type") == "book":
                if data["bids"]:
                    best_bid = data["bids"][0]["price"]
                if data["asks"]:
                    best_ask = data["asks"][0]["price"]

            elif data.get("event_type") == "price_change":
                price = data["price"]
                if data["side"] == "bid":
                    best_bid = price if data["size"] != "0.0" else None
                else:
                    best_ask = price if data["size"] != "0.0" else None

            print(f"Bid: {best_bid or 'N/A'} | Ask: {best_ask or 'N/A'}")
```

### 2. Trade Tape

```python
async def trade_tape(token_id: str):
    """Display recent trades."""
    async with websockets.connect(MARKET_WS) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": [token_id]
        }))

        async for message in ws:
            data = json.loads(message)

            if data.get("event_type") == "last_trade_price":
                side = "BUY " if data["side"] == "buy" else "SELL"
                print(f"{side} {data['price']} x {data['size']}")
```

### 3. Multi-Market Monitor

```python
async def monitor_markets(token_ids: list):
    """Monitor multiple markets simultaneously."""
    async with websockets.connect(MARKET_WS) as ws:
        await ws.send(json.dumps({
            "type": "market",
            "assets_ids": token_ids
        }))

        async for message in ws:
            data = json.loads(message)
            asset = data.get("asset_id", "")[:12]  # Truncate for display
            event = data.get("event_type")

            if event == "last_trade_price":
                print(f"[{asset}...] Trade at {data['price']}")
            elif event == "book":
                bids = len(data.get("bids", []))
                asks = len(data.get("asks", []))
                print(f"[{asset}...] Snapshot: {bids} bids, {asks} asks")
```

## Common Issues & Solutions

### Data Stops After ~20 Minutes

**Symptom:** Initially receives data, then stream goes silent

**Cause:** WebSocket connection timeout or server-side disconnect

**Solution:** Implement periodic ping and reconnection logic

```python
async def keep_alive(ws):
    """Send periodic pings to keep connection alive."""
    while True:
        await asyncio.sleep(15)  # Every 15 seconds
        try:
            await ws.ping()
        except:
            break
```

Full reconnection patterns in [connection-management.md](./connection-management.md).

---

### Missed Messages / Orderbook Drift

**Symptom:** Local orderbook state diverges from market

**Cause:** Network issues causing missed `price_change` events

**Solution:**
1. Rebuild from next `book` snapshot (sent periodically)
2. For critical applications, validate with REST API

---

### Connection Drops Unexpectedly

**Symptom:** `ConnectionClosed` exception during normal operation

**Cause:** Network instability, server maintenance, or idle timeout

**Solution:** Wrap connection in retry loop

```python
import asyncio
import websockets

async def robust_connect(token_ids: list, callback):
    """Connect with automatic reconnection."""
    while True:
        try:
            async with websockets.connect(MARKET_WS) as ws:
                await ws.send(json.dumps({
                    "type": "market",
                    "assets_ids": token_ids
                }))

                async for message in ws:
                    data = json.loads(message)
                    await callback(data)

        except websockets.exceptions.ConnectionClosed:
            print("Reconnecting in 5s...")
            await asyncio.sleep(5)
```

---

### High Memory Usage

**Symptom:** Memory grows continuously over time

**Cause:** Accumulating message history without bounds

**Solution:** Use bounded collections

```python
from collections import deque

# Keep only last 1000 trades
recent_trades = deque(maxlen=1000)

async def handle_trade(data):
    recent_trades.append(data)  # Automatically drops oldest
```

## WebSocket vs REST: When to Use Which

| Scenario | Use WebSocket | Use REST |
|----------|---------------|----------|
| Live dashboard | Yes | No |
| Initial page load | No | Yes |
| Historical analysis | No | Yes |
| Real-time alerts | Yes | No |
| One-time queries | No | Yes |
| Orderbook display | Yes | Yes (initial) |
| Trade notifications | Yes | No |

**Best practice:** Use REST to fetch initial state, WebSocket for ongoing updates.

## Related Documentation

Real-time data connects to these modules:

- **[Market Discovery](../market-discovery/README.md)** - Get token IDs for subscriptions
- **[Trading Operations](../trading/README.md)** - Live order tracking via user channel
- **[Data Analytics](../data-analytics/README.md)** - Historical data (REST, not WebSocket)
- **[Authentication](../auth/README.md)** - Required for user channel (not market channel)
- **[Edge Cases](../edge-cases/README.md)** - Connection issues, message handling
- **[Library Reference](../library/README.md)** - WebSocket reliability patterns

[Back to Polymarket Skills](../SKILL.md)

## Architecture Summary

```
                    Polymarket WebSocket Infrastructure
                    ==================================

User Application
       |
       v
  +------------+     +------------------+
  | websockets |---->| Market Channel   |  (Public)
  | library    |     | /ws/market       |
  +------------+     +------------------+
       |                    |
       |                    v
       |             +-------------+
       |             | Orderbook   |  book, price_change
       |             | Trade       |  last_trade_price
       |             | Tick Size   |  tick_size_change
       |             +-------------+
       |
       +------------>+------------------+
                     | User Channel     |  (Authenticated)
                     | /ws/user         |
                     +------------------+
                            |
                            v
                     +-------------+
                     | Orders      |  PLACEMENT, MATCHED
                     | Cancels     |  CANCELLATION
                     +-------------+
```

## Message Flow Example

```
1. Connect to wss://ws-subscriptions-clob.polymarket.com/ws/market

2. Send subscription:
   {"type": "market", "assets_ids": ["token_123..."]}

3. Receive snapshot:
   {"event_type": "book", "bids": [...], "asks": [...]}

4. Receive incremental updates:
   {"event_type": "price_change", "side": "bid", "price": "0.45", "size": "100"}
   {"event_type": "price_change", "side": "ask", "price": "0.46", "size": "0.0"}
   {"event_type": "last_trade_price", "price": "0.455", "size": "50"}

5. Repeat step 4 until disconnect
```

---

**Last updated:** 2026-01-31
**Status:** Complete - All WebSocket documentation available
