# User Channel - Authenticated Order and Trade Notifications

Stream real-time notifications for your orders and trades using the authenticated user channel.

## Overview

The user channel provides private notifications for:

- **Order events** - placement, matches, cancellations
- **Trade notifications** - confirmation lifecycle from match to blockchain settlement

**Endpoint:** `wss://ws-subscriptions-clob.polymarket.com/ws/user`

**Authentication:** Required - uses API credentials (apiKey, secret, passphrase)

## Prerequisites

Before connecting to the user channel:

1. **API credentials** from py-clob-client (see [../auth/api-credentials.md](../auth/api-credentials.md))
2. **websockets library:** `pip install websockets`
3. **Market condition IDs** (optional - filter to specific markets)

## Getting API Credentials

```python
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137  # Polygon mainnet
)

# Get or create API credentials
creds = client.create_or_derive_api_creds()

# creds structure:
# {
#     "apiKey": "abc123...",
#     "secret": "xyz789...",
#     "passphrase": "pass123..."
# }
```

**Important:** Store credentials securely. See [../auth/api-credentials.md](../auth/api-credentials.md) for credential management.

## Authenticated Connection

```python
import asyncio
import websockets
import json

USER_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/user"

async def connect_user_channel(api_creds: dict, market_ids: list = None):
    """Connect to user channel for order notifications.

    Args:
        api_creds: Dict with apiKey, secret, passphrase
        market_ids: Optional list of condition IDs to filter
    """
    async with websockets.connect(USER_WS) as ws:
        # Build subscription message with authentication
        subscribe_msg = {
            "type": "user",
            "auth": {
                "apiKey": api_creds["apiKey"],
                "secret": api_creds["secret"],
                "passphrase": api_creds["passphrase"]
            }
        }

        # Optionally filter to specific markets
        if market_ids:
            subscribe_msg["markets"] = market_ids

        await ws.send(json.dumps(subscribe_msg))

        # Process events
        async for message in ws:
            data = json.loads(message)
            await handle_user_event(data)
```

## Order Event Types

### PLACEMENT - Order Placed on Book

Received when your order is accepted and placed on the order book.

```python
{
    "type": "PLACEMENT",
    "order_id": "0x123abc...",
    "market": "0xdef456...",      # Condition ID
    "asset_id": "71321045...",    # Token ID
    "side": "BUY",                # or "SELL"
    "price": "0.45",              # String decimal
    "size": "100.0",              # Total order size
    "timestamp": 1705320000
}
```

### MATCHED - Order (Partially) Filled

Received when your order matches with a counterparty.

```python
{
    "type": "MATCHED",
    "order_id": "0x123abc...",
    "market": "0xdef456...",
    "asset_id": "71321045...",
    "side": "BUY",
    "price": "0.45",
    "size_matched": "50.0",       # Amount filled this match
    "remaining": "50.0",          # Remaining unfilled size
    "status": "MATCHED",          # or "FILLED" if complete
    "timestamp": 1705320001
}
```

**Status values:**
- `MATCHED` - Partial fill, order still on book
- `FILLED` - Complete fill, order removed from book

### CANCELLATION - Order Cancelled

Received when your order is cancelled.

```python
{
    "type": "CANCELLATION",
    "order_id": "0x123abc...",
    "market": "0xdef456...",
    "reason": "USER_CANCELLED",   # Cancellation reason
    "timestamp": 1705320002
}
```

**Cancellation reasons:**
- `USER_CANCELLED` - You cancelled the order
- `EXPIRED` - GTD order past expiration time
- `NOT_ENOUGH_BALANCE` - Insufficient funds to execute
- `MARKET_EXPIRED` - Market resolved or closed

## Trade Notification Events

Trades progress through multiple states as they settle on the blockchain.

```python
{
    "type": "TRADE",
    "status": "MINED",            # Trade lifecycle status
    "trade_id": "0xabc...",
    "order_id": "0x123abc...",    # Your original order
    "market": "0xdef456...",
    "asset_id": "71321045...",
    "side": "BUY",
    "price": "0.45",
    "size": "50.0",               # Trade size
    "fee": "0.0",                 # Trading fee
    "transaction_hash": "0xtx...",
    "timestamp": 1705320003
}
```

### Trade Status Progression

```
MATCHED -> MINED -> CONFIRMED
              \-> RETRYING -> MINED -> CONFIRMED
                       \-> FAILED
```

| Status | Description |
|--------|-------------|
| `MATCHED` | Trade matched with counterparty, pending settlement |
| `MINED` | Transaction included in a block |
| `CONFIRMED` | Transaction confirmed, trade complete |
| `RETRYING` | Transaction failed, system retrying |
| `FAILED` | Trade failed after retries (rare) |

**Note:** Most trades reach `CONFIRMED` within seconds on Polygon.

## Event Handler Pattern

```python
async def handle_user_event(data: dict):
    """Route user events to appropriate handlers."""
    event_type = data.get("type")

    if event_type == "PLACEMENT":
        order_id = data["order_id"]
        side = data["side"]
        size = data["size"]
        price = data["price"]
        print(f"Order placed: {order_id}")
        print(f"  {side} {size} @ {price}")

    elif event_type == "MATCHED":
        order_id = data["order_id"]
        filled = data["size_matched"]
        remaining = data["remaining"]
        status = data.get("status", "MATCHED")
        print(f"Order matched: {order_id}")
        print(f"  Filled: {filled}, Remaining: {remaining}")
        if status == "FILLED":
            print("  Order completely filled!")

    elif event_type == "CANCELLATION":
        order_id = data["order_id"]
        reason = data.get("reason", "UNKNOWN")
        print(f"Order cancelled: {order_id}")
        print(f"  Reason: {reason}")

    elif event_type == "TRADE":
        trade_id = data["trade_id"]
        status = data["status"]
        print(f"Trade {status}: {trade_id}")
        if status == "CONFIRMED":
            tx_hash = data.get("transaction_hash", "N/A")
            print(f"  Transaction: {tx_hash}")
        elif status == "FAILED":
            print(f"  WARNING: Trade failed!")
```

## Subscribing to Multiple Markets

### Specific Markets Only

Filter notifications to only markets you care about:

```python
subscribe_msg = {
    "type": "user",
    "auth": {
        "apiKey": api_creds["apiKey"],
        "secret": api_creds["secret"],
        "passphrase": api_creds["passphrase"]
    },
    "markets": [
        "0xCondition1...",  # Market condition IDs
        "0xCondition2...",
        "0xCondition3..."
    ]
}
```

### All Markets

Receive notifications for all your orders across all markets:

```python
subscribe_msg = {
    "type": "user",
    "auth": {
        "apiKey": api_creds["apiKey"],
        "secret": api_creds["secret"],
        "passphrase": api_creds["passphrase"]
    }
    # Omit "markets" field for all markets
}
```

**Note:** If you trade actively on many markets, filtering can reduce message volume.

## Complete User Stream Example

```python
import asyncio
import websockets
import json

USER_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/user"

class UserStreamHandler:
    """Handle user channel events with state tracking."""

    def __init__(self, api_creds: dict):
        self.creds = api_creds
        self.orders = {}      # Track order states
        self.trades = {}      # Track trade states
        self.running = False

    async def start(self, market_ids: list = None):
        """Start the user stream with automatic reconnection."""
        self.running = True

        while self.running:
            try:
                async with websockets.connect(USER_WS) as ws:
                    # Build subscription
                    msg = {
                        "type": "user",
                        "auth": self.creds
                    }
                    if market_ids:
                        msg["markets"] = market_ids

                    await ws.send(json.dumps(msg))
                    print("Connected to user channel")

                    # Process events
                    async for message in ws:
                        data = json.loads(message)
                        await self.handle_event(data)

            except websockets.ConnectionClosed:
                print("Connection closed, reconnecting in 5s...")
                await asyncio.sleep(5)

            except Exception as e:
                print(f"Error: {e}, reconnecting in 10s...")
                await asyncio.sleep(10)

    async def handle_event(self, data: dict):
        """Process incoming event and update local state."""
        event_type = data.get("type")
        order_id = data.get("order_id")

        if event_type == "PLACEMENT":
            self.orders[order_id] = {
                "status": "OPEN",
                "side": data["side"],
                "price": data["price"],
                "size": data["size"],
                "filled": "0.0"
            }
            print(f"New order: {order_id[:16]}... {data['side']} {data['size']} @ {data['price']}")

        elif event_type == "MATCHED":
            if order_id in self.orders:
                self.orders[order_id]["filled"] = str(
                    float(self.orders[order_id]["size"]) - float(data["remaining"])
                )
                if data.get("status") == "FILLED":
                    self.orders[order_id]["status"] = "FILLED"
            print(f"Matched: {order_id[:16]}... +{data['size_matched']}")

        elif event_type == "CANCELLATION":
            if order_id in self.orders:
                self.orders[order_id]["status"] = "CANCELLED"
            print(f"Cancelled: {order_id[:16]}... ({data.get('reason', 'UNKNOWN')})")

        elif event_type == "TRADE":
            trade_id = data.get("trade_id")
            self.trades[trade_id] = {
                "status": data["status"],
                "order_id": order_id,
                "price": data["price"],
                "size": data["size"]
            }
            print(f"Trade {data['status']}: {trade_id[:16]}...")

    def get_open_orders(self) -> dict:
        """Return orders that are still open."""
        return {
            oid: order for oid, order in self.orders.items()
            if order["status"] == "OPEN"
        }

    def stop(self):
        """Stop the stream gracefully."""
        self.running = False


# Usage example
async def main():
    api_creds = {
        "apiKey": "your_api_key",
        "secret": "your_secret",
        "passphrase": "your_passphrase"
    }

    handler = UserStreamHandler(api_creds)

    # Run in background
    stream_task = asyncio.create_task(handler.start())

    # ... do other things, place orders, etc. ...

    # When done
    handler.stop()
    await stream_task


if __name__ == "__main__":
    asyncio.run(main())
```

## Integrating with Order Placement

Track orders from placement through settlement:

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs

class OrderTracker:
    """Place orders and track them via WebSocket."""

    def __init__(self, client: ClobClient, stream_handler: UserStreamHandler):
        self.client = client
        self.stream = stream_handler

    async def place_and_track(self, order_args: OrderArgs) -> str:
        """Place order and wait for confirmation."""
        # Place the order
        response = self.client.create_and_post_order(order_args)
        order_id = response.get("orderID")

        if not order_id:
            raise ValueError(f"Order failed: {response}")

        print(f"Order submitted: {order_id}")

        # Order events will arrive via stream_handler
        # Check stream_handler.orders[order_id] for updates
        return order_id
```

## Common Issues

### Authentication Errors

**Symptom:** Connection closes immediately or no events received

**Cause:** Invalid or expired API credentials

**Solution:**
1. Regenerate credentials: `client.create_or_derive_api_creds()`
2. Verify credentials are current
3. Check API key hasn't been revoked

### No Events Received

**Symptom:** Connected but no events arrive

**Cause:** No active orders in subscribed markets

**Solution:**
1. Place a test order to verify stream works
2. Check market_ids filter matches your orders
3. Try subscribing to all markets (omit markets field)

### Missing Order Updates

**Symptom:** Some order events not received

**Cause:** Reconnection during order processing

**Solution:** Query REST API for current order state after reconnection

```python
# After reconnection, sync state
orders = client.get_orders()
for order in orders:
    handler.orders[order["id"]] = {
        "status": order["status"],
        # ... sync other fields
    }
```

## Related Documentation

| Document | Purpose |
|----------|---------|
| [websocket-overview.md](./websocket-overview.md) | WebSocket architecture and channels |
| [market-channel.md](./market-channel.md) | Public market data streaming |
| [connection-management.md](./connection-management.md) | Reconnection and reliability patterns |
| [../auth/api-credentials.md](../auth/api-credentials.md) | API credential management |
| [../trading/](../trading/) | Order placement and management |

---

**Last updated:** 2026-01-31
