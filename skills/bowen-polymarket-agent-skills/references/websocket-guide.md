# WebSocket Streaming Guide

## Connection

WebSocket URL: `wss://ws-subscriptions-clob.polymarket.com/ws/`

```python
from polymarket import PolymarketClient

async with PolymarketClient() as client:
    # Market stream (public)
    async with client.market_stream as stream:
        async for event in stream.subscribe(["token_id"]):
            print(event)
```

---

## Market Channel (Public)

No authentication required. Streams public market data.

### Subscription

```python
from polymarket.websocket import MarketStream

stream = MarketStream(config, custom_features=True)

async with stream:
    async for event in stream.subscribe(["token_id_1", "token_id_2"]):
        handle_event(event)
```

### Events

#### `book` - Full Orderbook Snapshot
Sent on subscription and periodically.

```python
if isinstance(event, WsBookMessage):
    print(f"Market: {event.market}")
    print(f"Bids: {len(event.bids)}")
    for bid in event.bids[:3]:
        print(f"  {bid.price}: {bid.size}")
```

#### `price_change` - Price Level Updates
Sent when orders are placed or cancelled.

```python
if isinstance(event, WsPriceChangeMessage):
    for change in event.price_changes:
        print(f"{change.side} {change.price}: {change.size}")
        print(f"Best bid: {change.best_bid}, Best ask: {change.best_ask}")
```

#### `last_trade_price` - Trade Executions
Sent when trades execute.

```python
if isinstance(event, WsLastTradePriceMessage):
    print(f"Trade: {event.size} @ {event.price}")
    print(f"Side: {event.side}")
```

#### `tick_size_change` - Tick Size Updates

```python
if isinstance(event, WsTickSizeChangeMessage):
    print(f"New tick size: {event.tick_size}")
    print(f"New min order: {event.min_order_size}")
```

#### `best_bid_ask` - Best Prices (requires custom_features)

```python
if isinstance(event, WsBestBidAskMessage):
    print(f"Best bid: {event.best_bid}")
    print(f"Best ask: {event.best_ask}")
```

#### `new_market` - Market Created (requires custom_features)

```python
if isinstance(event, WsNewMarketMessage):
    print(f"New market: {event.market}")
```

#### `market_resolved` - Market Resolved (requires custom_features)

```python
if isinstance(event, WsMarketResolvedMessage):
    print(f"Market {event.market} resolved: {event.winning_outcome}")
```

---

## User Channel (Authenticated)

Requires API credentials. Streams private user data.

### Subscription

```python
from polymarket.websocket import UserStream
from polymarket.auth import Credentials

credentials = Credentials(
    api_key="...",
    secret="...",
    passphrase="...",
)

stream = UserStream(config, credentials)

async with stream:
    async for event in stream.subscribe(["condition_id_1"]):
        handle_event(event)
```

### Events

#### `order` - Order Updates

```python
if isinstance(event, WsOrderMessage):
    print(f"Order {event.id}")
    print(f"Type: {event.type}")  # PLACEMENT, UPDATE, CANCELLATION
    print(f"Matched: {event.size_matched}/{event.original_size}")
    print(f"Associated trades: {event.associate_trades}")
```

Order types:
- `PLACEMENT`: New order placed
- `UPDATE`: Order partially filled
- `CANCELLATION`: Order cancelled

#### `trade` - Trade Updates

```python
if isinstance(event, WsTradeMessage):
    print(f"Trade {event.id}")
    print(f"Status: {event.status}")
    print(f"{event.side} {event.size} @ {event.price}")
```

Trade statuses:
- `MATCHED`: Trade matched on orderbook
- `MINED`: Transaction included in block
- `CONFIRMED`: Transaction confirmed on-chain
- `RETRYING`: Transaction being retried
- `FAILED`: Transaction failed

---

## Dynamic Subscriptions

Add or remove subscriptions on an existing connection.

### Market Channel

```python
async with client.market_stream as stream:
    # Initial subscription
    async for event in stream.subscribe(["token_1"]):
        # Add more tokens
        await stream.add_tokens(["token_2", "token_3"])

        # Remove tokens
        await stream.remove_tokens(["token_1"])

        handle_event(event)
```

### User Channel

```python
async with UserStream(config, credentials) as stream:
    async for event in stream.subscribe(["market_1"]):
        await stream.add_markets(["market_2"])
        await stream.remove_markets(["market_1"])
        handle_event(event)
```

---

## Building a Local Order Book

```python
class LocalOrderBook:
    def __init__(self):
        self.bids: dict[str, str] = {}  # price -> size
        self.asks: dict[str, str] = {}

    def handle_event(self, event):
        if isinstance(event, WsBookMessage):
            # Full snapshot
            self.bids = {b.price: b.size for b in event.bids}
            self.asks = {a.price: a.size for a in event.asks}

        elif isinstance(event, WsPriceChangeMessage):
            # Incremental update
            for change in event.price_changes:
                book = self.bids if change.side == "BUY" else self.asks
                if change.size == "0":
                    book.pop(change.price, None)
                else:
                    book[change.price] = change.size

# Usage
book = LocalOrderBook()
async for event in stream.subscribe([token_id]):
    book.handle_event(event)
    print(f"Best bid: {max(book.bids.keys())}")
```

---

## Reconnection Handling

The SDK handles reconnection automatically with exponential backoff.

```python
# Configure reconnection
stream = MarketStream(
    config,
    max_reconnect_attempts=5,  # Default
    reconnect_delay=1.0,        # Initial delay in seconds
)

# Stream handles disconnects transparently
async for event in stream.subscribe(["token_id"]):
    # Will automatically reconnect and re-subscribe
    handle_event(event)
```

---

## Error Handling

```python
from polymarket.exceptions import WebSocketError, ConnectionError

try:
    async with client.market_stream as stream:
        async for event in stream.subscribe(["token_id"]):
            handle_event(event)
except ConnectionError as e:
    print(f"Connection failed: {e.message}")
except WebSocketError as e:
    print(f"WebSocket error: {e.message}")
```
