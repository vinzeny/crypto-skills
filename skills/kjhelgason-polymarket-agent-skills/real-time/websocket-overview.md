# WebSocket Architecture & Setup

Complete guide to Polymarket's WebSocket infrastructure for real-time market data streaming.

## Overview

Polymarket provides two WebSocket endpoints for real-time data:

1. **Market Channel** - Public orderbook and price data (no authentication required)
2. **User Channel** - Private order and trade notifications (authentication required)

WebSocket streaming is essential for:
- Live price displays
- Orderbook depth visualization
- Order fill notifications
- Real-time trading dashboards

## WebSocket Endpoints

| Channel | URL | Auth Required | Purpose |
|---------|-----|---------------|---------|
| **Market** | `wss://ws-subscriptions-clob.polymarket.com/ws/market` | No | Orderbook updates, price changes, trade executions |
| **User** | `wss://ws-subscriptions-clob.polymarket.com/ws/user` | Yes | Order placements, matches, cancellations |

```python
# Endpoint constants
MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
USER_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/user"
```

## Dependencies

Install the required Python packages:

```bash
pip install websockets asyncio
```

**Note:** `asyncio` is included in Python 3.4+ standard library, but `websockets` must be installed separately.

## Basic Connection Setup

### Market Channel (Public - No Auth)

The market channel requires no authentication and is the simplest way to get real-time data:

```python
import asyncio
import websockets
import json

MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

async def connect_market():
    """Basic market channel connection."""
    async with websockets.connect(MARKET_WS) as ws:
        # Subscribe to specific markets using token IDs
        subscribe_msg = {
            "type": "market",
            "assets_ids": [
                "71321045679252212594626385532706912750332728571942532289631379312455583992563",
                "72549165387050808959290263609189958849215668938434754142373413659789425508885"
            ]
        }
        await ws.send(json.dumps(subscribe_msg))

        print("Subscribed to market channel")

        # Receive and process messages
        async for message in ws:
            data = json.loads(message)
            event_type = data.get("event_type")
            print(f"Received {event_type}: {data}")

# Run the connection
# asyncio.run(connect_market())
```

### User Channel (Private - Auth Required)

The user channel requires API credentials for authentication:

```python
import asyncio
import websockets
import json

USER_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/user"

async def connect_user(api_key: str, api_secret: str, api_passphrase: str, markets: list):
    """Authenticated user channel connection."""
    async with websockets.connect(USER_WS) as ws:
        # Subscribe with authentication
        subscribe_msg = {
            "type": "user",
            "auth": {
                "apiKey": api_key,
                "secret": api_secret,
                "passphrase": api_passphrase
            },
            "markets": markets  # List of condition IDs (not token IDs)
        }
        await ws.send(json.dumps(subscribe_msg))

        print("Subscribed to user channel")

        # Receive order/trade notifications
        async for message in ws:
            data = json.loads(message)
            print(f"User event: {data}")

# Run with your credentials
# asyncio.run(connect_user(API_KEY, API_SECRET, API_PASSPHRASE, ["condition_id_1"]))
```

## Subscription Message Formats

### Market Channel Subscription

Subscribe to receive orderbook and price updates for specific tokens:

```python
# Market channel subscription message
{
    "type": "market",
    "assets_ids": [
        "token_id_1",  # YES token ID
        "token_id_2"   # NO token ID (or other markets)
    ]
}
```

**Important:** Use **token IDs** (also called `asset_ids`), not condition IDs. Each market has two tokens (YES and NO). Get token IDs from:
- REST API: `GET /markets` endpoint
- Market discovery skill documentation

### User Channel Subscription

Subscribe to receive order and trade notifications:

```python
# User channel subscription message (authenticated)
{
    "type": "user",
    "auth": {
        "apiKey": "your-api-key",
        "secret": "your-api-secret",
        "passphrase": "your-passphrase"
    },
    "markets": [
        "condition_id_1",  # Market condition ID (NOT token ID)
        "condition_id_2"
    ]
}
```

**Important:** User channel uses **condition IDs** (market identifiers), not token IDs. This is different from the market channel.

## Message Types Reference

### Market Channel Events

| Event Type | Description | When Sent |
|------------|-------------|-----------|
| `book` | Full orderbook snapshot | On subscription, periodically for sync |
| `price_change` | Incremental orderbook update | When order added/removed/modified |
| `tick_size_change` | Tick size changed | When price crosses 0.04 or 0.96 threshold |
| `last_trade_price` | Trade executed | When a trade occurs |

### User Channel Events

| Event Type | Description | When Sent |
|------------|-------------|-----------|
| `PLACEMENT` | Order placed successfully | After order submission |
| `MATCHED` | Order matched (full or partial) | When your order executes |
| `CANCELLATION` | Order cancelled | After cancellation request |

## When to Use WebSocket vs REST

| Use Case | WebSocket | REST API |
|----------|-----------|----------|
| Live price display | Yes - continuous updates | No - polling inefficient |
| Orderbook depth | Yes - incremental updates | Yes - initial snapshot only |
| Order fill notifications | Yes - instant | No - requires polling |
| Trade confirmations | Yes - real-time | No - requires polling |
| Initial data fetch | No - subscribe gets snapshot | Yes - on-demand query |
| Historical queries | No - not available | Yes - historical endpoints |
| High-frequency updates | Yes - designed for this | No - rate limited |
| Batch operations | No - streaming only | Yes - single requests |

**General guidance:**
- Use WebSocket for anything requiring real-time updates
- Use REST API for one-time queries and historical data
- Combine both: REST for initial state, WebSocket for updates

## Connection Lifecycle

### Connection States

```
CONNECTING -> CONNECTED -> SUBSCRIBED -> STREAMING -> CLOSED
                 |             |            |
                 v             v            v
              AUTH FAIL    SUB FAIL    DISCONNECTED
```

### Handling Connection Events

```python
import asyncio
import websockets
import json

MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

async def robust_connection(token_ids: list):
    """Connection with basic error handling."""
    try:
        async with websockets.connect(MARKET_WS) as ws:
            # Subscribe
            await ws.send(json.dumps({
                "type": "market",
                "assets_ids": token_ids
            }))

            # Process messages
            async for message in ws:
                try:
                    data = json.loads(message)
                    yield data
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {message}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e.code} - {e.reason}")
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Complete Working Example

A full example combining connection, subscription, and message handling:

```python
import asyncio
import websockets
import json
from datetime import datetime

MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

class MarketStreamer:
    """Simple market data streamer."""

    def __init__(self, token_ids: list):
        self.token_ids = token_ids
        self.ws = None
        self.running = False

    async def start(self):
        """Start streaming market data."""
        self.running = True

        async with websockets.connect(MARKET_WS) as ws:
            self.ws = ws

            # Subscribe to markets
            await ws.send(json.dumps({
                "type": "market",
                "assets_ids": self.token_ids
            }))

            print(f"[{datetime.now()}] Subscribed to {len(self.token_ids)} markets")

            # Process incoming messages
            async for message in ws:
                if not self.running:
                    break

                data = json.loads(message)
                await self.handle_message(data)

    async def handle_message(self, data: dict):
        """Process incoming market data."""
        event_type = data.get("event_type")
        asset_id = data.get("asset_id", "unknown")[:20] + "..."

        if event_type == "book":
            bids = len(data.get("bids", []))
            asks = len(data.get("asks", []))
            print(f"[BOOK] {asset_id} - {bids} bids, {asks} asks")

        elif event_type == "price_change":
            side = data.get("side")
            price = data.get("price")
            size = data.get("size")
            print(f"[PRICE] {asset_id} - {side} {price} x {size}")

        elif event_type == "last_trade_price":
            price = data.get("price")
            size = data.get("size")
            print(f"[TRADE] {asset_id} - {price} x {size}")

        elif event_type == "tick_size_change":
            old = data.get("old_tick_size")
            new = data.get("new_tick_size")
            print(f"[TICK] {asset_id} - {old} -> {new}")

    def stop(self):
        """Stop streaming."""
        self.running = False

# Usage example
async def main():
    # Example token IDs (replace with actual IDs from market discovery)
    token_ids = [
        "71321045679252212594626385532706912750332728571942532289631379312455583992563"
    ]

    streamer = MarketStreamer(token_ids)

    # Run for 60 seconds
    try:
        await asyncio.wait_for(streamer.start(), timeout=60)
    except asyncio.TimeoutError:
        streamer.stop()
        print("Streaming stopped after 60 seconds")

# Run: asyncio.run(main())
```

## Key Concepts Summary

1. **Two channels:** Market (public) and User (private)
2. **Market channel:** Uses token IDs (`assets_ids`), no auth required
3. **User channel:** Uses condition IDs (`markets`), requires API auth
4. **Initial snapshot:** `book` event provides full orderbook on subscribe
5. **Incremental updates:** `price_change` events update individual levels
6. **Combine with REST:** Use REST for initial data, WebSocket for live updates

## Related Documentation

- **[Market Channel](./market-channel.md)** - Detailed orderbook and price streaming
- **[User Channel](./user-channel.md)** - Order notifications (coming in Plan 08)
- **[Connection Management](./connection-management.md)** - Reconnection patterns (coming in Plan 08)
- **[Authentication](../auth/)** - API credential setup for user channel

---

**Last updated:** 2026-01-31
**Status:** Phase 2 - Core API Documentation
