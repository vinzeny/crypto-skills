# Polymarket CLOB API Overview

Complete guide to the Polymarket Central Limit Order Book (CLOB) API architecture, endpoints, and client library usage.

## API Basics

### Base URL

```
https://clob.polymarket.com
```

### Purpose

The CLOB API is Polymarket's Central Limit Order Book for trading operations. It handles:
- Order placement and cancellation
- Order book and price data
- Trade execution
- Position management

### Authentication Requirements

| Operation Type | Authentication Required | Description |
|---------------|------------------------|-------------|
| **Read operations** | None | Prices, orderbook, market data |
| **Write operations** | L2 Authentication | Order placement, cancellation, position queries |

**Read operations** (no auth needed):
- Get current prices
- Get order book depth
- Get tick sizes
- Get historical prices

**Write operations** (L2 auth required):
- Place orders
- Cancel orders
- Get your orders
- Get your positions

**Authentication setup:** See [../auth/client-initialization.md](../auth/client-initialization.md) for complete setup.

## Authentication Reference

### Quick Setup Reminder

Before making authenticated API calls, ensure:

```python
from py_clob_client.client import ClobClient

client = ClobClient(
    host="https://clob.polymarket.com",
    key=PRIVATE_KEY,
    chain_id=137,
    signature_type=0,  # or 1 for proxy, 2 for Safe
    funder=WALLET_ADDRESS
)

# CRITICAL: Must set API credentials for authenticated calls
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
```

### Authenticated Request Headers

Authenticated endpoints use POLY-* headers (handled automatically by py-clob-client):

| Header | Purpose |
|--------|---------|
| `POLY-ADDRESS` | Your funder address |
| `POLY-SIGNATURE` | HMAC-SHA256 signature of request |
| `POLY-TIMESTAMP` | Unix timestamp |
| `POLY-NONCE` | Request nonce |
| `POLY-PASSPHRASE` | API passphrase |

**See:** [../auth/authentication-flow.md](../auth/authentication-flow.md) for detailed L1/L2 auth architecture.

## Key Endpoints Overview

### Public Endpoints (No Authentication)

These endpoints are available without authentication:

#### GET /price
Get current price for a token.

```python
# Using py-clob-client
price = client.get_price(token_id, side="BUY")
```

**Parameters:**
- `token_id` (required): The conditional token ID
- `side` (required): "BUY" or "SELL"

**Response:** Current best price for the specified side.

---

#### GET /midpoint
Get midpoint price between best bid and ask.

```python
midpoint = client.get_midpoint(token_id)
```

**Use case:** Fair value estimation, position valuation.

---

#### GET /book
Get full order book for a token.

```python
book = client.get_order_book(token_id)
# Returns: {"bids": [...], "asks": [...]}
```

**Response structure:**
```python
{
    "market": "token_id",
    "asset_id": "token_id",
    "hash": "orderbook_hash",
    "bids": [{"price": "0.45", "size": "100.0"}, ...],
    "asks": [{"price": "0.55", "size": "50.0"}, ...]
}
```

---

#### GET /tick-size
Get minimum price increment for a token.

```python
tick_size = client.get_tick_size(token_id)
# Returns: 0.01 (typical value)
```

**Important:** Order prices must be multiples of the tick size.

---

#### GET /prices-history
Get historical price data.

```python
history = client.get_prices_history(
    market_id=market_id,
    interval="1h",  # 1m, 5m, 15m, 1h, 4h, 1d
    start_ts=start_timestamp,
    end_ts=end_timestamp
)
```

---

### Authenticated Endpoints (L2 Auth Required)

These endpoints require `set_api_creds()` to be called first.

#### POST /order
Place a single order.

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

order_args = OrderArgs(
    price=0.45,
    size=100.0,
    side=BUY,
    token_id=token_id
)
signed_order = client.create_order(order_args)
response = client.post_order(signed_order, OrderType.GTC)
```

**See:** [order-types.md](./order-types.md) for complete order type documentation.

---

#### DELETE /order/{orderId}
Cancel a specific order.

```python
result = client.cancel(order_id)
```

**Response:**
```python
{"canceled": ["order_id"]}  # Success
{"not_canceled": {"order_id": "reason"}}  # Failure
```

---

#### GET /orders
Get all orders for the authenticated user.

```python
orders = client.get_orders()

# With filters
orders = client.get_orders(
    market=token_id,  # Filter by market
    state="LIVE"      # LIVE, MATCHED, CANCELLED
)
```

---

#### GET /order/{orderId}
Get a specific order by ID.

```python
order = client.get_order(order_id)
```

---

#### POST /orders
Batch order placement.

```python
# Create multiple orders
orders = [
    client.create_order(OrderArgs(price=0.45, size=100, side=BUY, token_id=token_id)),
    client.create_order(OrderArgs(price=0.46, size=100, side=BUY, token_id=token_id)),
]

# Post batch
responses = client.post_orders(orders, OrderType.GTC)
```

---

#### DELETE /orders
Batch order cancellation.

```python
# Cancel multiple orders
result = client.cancel_orders(order_ids=["order_id_1", "order_id_2"])

# Cancel all orders for a market
result = client.cancel_market_orders(market=token_id)

# Cancel ALL orders
result = client.cancel_all()
```

## Client Library Usage

### Complete Client Setup

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
import os

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=os.getenv("POLYMARKET_PRIVATE_KEY"),
    chain_id=137,
    signature_type=0,  # 0=EOA, 1=Proxy, 2=Safe
    funder=os.getenv("WALLET_ADDRESS")
)

# Set API credentials (required for authenticated endpoints)
client.set_api_creds(client.create_or_derive_api_creds())
```

### Public Methods (No Auth Needed)

```python
# Get current price
price = client.get_price(token_id, side="BUY")
print(f"Best bid: {price}")

# Get full order book
book = client.get_order_book(token_id)
print(f"Bids: {len(book['bids'])}, Asks: {len(book['asks'])}")

# Get tick size
tick_size = client.get_tick_size(token_id)
print(f"Tick size: {tick_size}")

# Get midpoint price
midpoint = client.get_midpoint(token_id)
print(f"Midpoint: {midpoint}")
```

### Authenticated Methods

```python
# Create and place an order
order_args = OrderArgs(
    price=0.45,
    size=100.0,
    side=BUY,
    token_id=token_id
)
order = client.create_order(order_args)
response = client.post_order(order, OrderType.GTC)
print(f"Order placed: {response}")

# Get your orders
my_orders = client.get_orders()
print(f"Active orders: {len(my_orders)}")

# Cancel an order
if my_orders:
    result = client.cancel(my_orders[0]['id'])
    print(f"Cancelled: {result}")
```

## Token ID Context

### Where Token IDs Come From

Token IDs are obtained from the Gamma API (market discovery):

```python
import requests

# Get market details from Gamma API
response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"slug": "market-slug"}
)
market = response.json()[0]

# Extract token IDs
token_ids = market['clobTokenIds']
yes_token_id = token_ids[0]  # YES token at index 0
no_token_id = token_ids[1]   # NO token at index 1
```

### Token ID Mapping

| Index | Token | Description |
|-------|-------|-------------|
| 0 | YES | Outcome = Yes/True |
| 1 | NO | Outcome = No/False |

**Cross-reference:** See [../market-discovery/](../market-discovery/) for complete market discovery documentation.

### Using Token IDs with CLOB API

```python
# Example: Get YES token price and place order
yes_token_id = market['clobTokenIds'][0]

# Get current price
yes_price = client.get_price(yes_token_id, side="BUY")
print(f"YES token price: {yes_price}")

# Place order on YES outcome
order_args = OrderArgs(
    price=float(yes_price),
    size=50.0,
    side=BUY,
    token_id=yes_token_id
)
```

## Error Response Patterns

### HTTP Status Codes

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| **400** | Bad Request | Invalid parameters, precision errors, invalid amounts |
| **401** | Unauthorized | Missing/invalid credentials, expired API key |
| **404** | Not Found | Order doesn't exist, invalid order ID |
| **429** | Rate Limited | Too many requests, implement backoff |

### Error Response Structure

```python
# Error response format
{
    "error": "error_type",
    "message": "Human-readable description"
}
```

### Common Error Scenarios

#### 400 - Bad Request

```python
# Invalid precision (FOK/FAK orders)
{
    "error": "invalid_amounts",
    "message": "Order amounts must satisfy precision requirements"
}
# Solution: Round size to 2 decimal places for FOK orders

# Invalid tick size
{
    "error": "invalid_price",
    "message": "Price must be a multiple of tick size"
}
# Solution: Use client.get_tick_size() and round price appropriately
```

#### 401 - Authentication Failed

```python
# Missing credentials
{
    "error": "unauthorized",
    "message": "Invalid api key"
}
# Solution: Call client.set_api_creds() before authenticated operations

# Expired credentials
{
    "error": "unauthorized",
    "message": "Credentials expired"
}
# Solution: Regenerate with client.create_or_derive_api_creds()
```

#### 429 - Rate Limited

```python
# Too many requests
{
    "error": "rate_limited",
    "message": "Rate limit exceeded"
}
# Solution: Implement exponential backoff

import time

def rate_limited_request(func, *args, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

## Best Practices

### 1. Always Check Tick Size Before Ordering

```python
tick_size = client.get_tick_size(token_id)
# Ensure price is a multiple of tick size
price = round(desired_price / tick_size) * tick_size
```

### 2. Handle Rate Limits Gracefully

```python
import time
from functools import wraps

def with_retry(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        time.sleep(base_delay * (2 ** attempt))
                        continue
                    raise
        return wrapper
    return decorator

@with_retry(max_retries=3)
def place_order(client, order_args):
    order = client.create_order(order_args)
    return client.post_order(order, OrderType.GTC)
```

### 3. Verify Credentials Before Trading

```python
def verify_client_ready(client):
    """Verify client is properly configured before trading."""
    try:
        # Test public endpoint
        client.get_ok()

        # Test authenticated endpoint
        client.get_orders()

        return True
    except Exception as e:
        print(f"Client verification failed: {e}")
        return False
```

### 4. Use Appropriate Order Types

- **Patient trading:** Use GTC (Good Till Cancelled)
- **Time-sensitive:** Use GTD (Good Till Date)
- **Immediate execution:** Use FAK (partial fills OK) or FOK (all-or-nothing)

**See:** [order-types.md](./order-types.md) for detailed guidance.

## Related Documentation

- [Order Types Guide](./order-types.md) - GTC, GTD, FOK, FAK order documentation
- [Authentication Setup](../auth/client-initialization.md) - Complete client initialization
- [Market Discovery](../market-discovery/) - Finding markets and token IDs

## References

- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client) - Official Python client
- [Polymarket CLOB Docs](https://docs.polymarket.com/developers/CLOB) - Official API documentation
- [CLOB API Reference](https://docs.polymarket.com/developers/CLOB/orders) - Endpoint reference
