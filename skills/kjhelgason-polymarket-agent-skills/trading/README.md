# Polymarket Trading Operations

Complete guide to trading on Polymarket via the CLOB API, covering order types, placement, management, and position tracking.

## Quick Start

**Fastest path to placing your first order:**

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
import os

# 1. Initialize authenticated client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=os.getenv("POLYMARKET_PRIVATE_KEY"),
    chain_id=137,
    signature_type=0,  # 0=EOA, 1=Proxy, 2=Safe
    funder=os.getenv("WALLET_ADDRESS")
)
client.set_api_creds(client.create_or_derive_api_creds())

# 2. Get token ID (from market discovery)
token_id = "your_token_id"  # See ../market-discovery/

# 3. Place a GTC limit order
order_args = OrderArgs(
    price=0.45,      # Limit price
    size=100.0,      # Number of shares
    side=BUY,        # BUY or SELL
    token_id=token_id
)
order = client.create_order(order_args)
response = client.post_order(order, OrderType.GTC)

print(f"Order placed: {response.get('orderID')}")
```

**Need a different order type?** See [order-types.md](./order-types.md) for GTC, GTD, FOK, and FAK options.

## Prerequisites

Before trading, ensure you have:

### 1. Authenticated ClobClient

Your client must be initialized and have API credentials set:

```python
client = ClobClient(host, key, chain_id, signature_type, funder)
client.set_api_creds(client.create_or_derive_api_creds())
```

**See:** [../auth/](../auth/) for complete authentication setup.

### 2. Token ID from Market Discovery

Token IDs identify what you're trading (YES or NO outcome):

```python
# Get from Gamma API
import requests
market = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"slug": "market-slug"}
).json()[0]

yes_token_id = market['clobTokenIds'][0]  # YES token
no_token_id = market['clobTokenIds'][1]   # NO token
```

**See:** [../market-discovery/](../market-discovery/) for finding markets and token IDs.

### 3. USDC.e Balance (for buying)

- Must have **USDC.e** (not native USDC) in your funder address
- Balance available: check via web3 or Polymarket UI
- Contract: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`

### 4. Position (for selling)

To sell, you must hold shares in that outcome:

```python
# Check your positions before selling
positions = client.get_orders()  # Or use positions endpoint
```

## Documentation Index

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[clob-api-overview.md](./clob-api-overview.md)** | CLOB API architecture, endpoints, client setup | First time using CLOB API |
| **[order-types.md](./order-types.md)** | GTC, GTD, FOK, FAK order documentation | Choosing the right order type |
| **[order-placement.md](./order-placement.md)** | Order creation and submission workflows | Placing orders |
| **[order-management.md](./order-management.md)** | Cancellation, status, batch operations | Managing active orders |
| **[positions-and-balances.md](./positions-and-balances.md)** | Position tracking and balance queries | Portfolio management |

### Reading Order

**For first-time traders:**
1. Start with [clob-api-overview.md](./clob-api-overview.md) - understand API structure
2. Read [order-types.md](./order-types.md) - learn order type selection
3. Read [order-placement.md](./order-placement.md) - detailed placement workflow
4. Follow the Quick Start above to place your first order

**For specific tasks:**
- "Which order type should I use?" --> [order-types.md](./order-types.md)
- "How do I place an order?" --> [order-placement.md](./order-placement.md)
- "How do I cancel orders?" --> [order-management.md](./order-management.md)
- "How do I check my balance?" --> [positions-and-balances.md](./positions-and-balances.md)
- "How does authentication work?" --> [../auth/](../auth/)
- "Where do I get token IDs?" --> [../market-discovery/](../market-discovery/)

## Order Type Quick Reference

| Scenario | Order Type | Why |
|----------|------------|-----|
| Limit order, wait for price | **GTC** | Standard, patient execution |
| Time-limited opportunity | **GTD** | Auto-expires at specified time |
| Must fill completely NOW | **FOK** | All-or-nothing (strict precision!) |
| Market order, any fill OK | **FAK** | Best effort, partial fills OK |

### Decision Flowchart

```
Need immediate execution?
|
+-- NO --> Need expiration?
|          |
|          +-- YES --> GTD
|          +-- NO --> GTC (recommended default)
|
+-- YES --> Must fill completely?
            |
            +-- YES --> FOK (watch precision!)
            +-- NO --> FAK
```

### Precision Warning for FOK

**FOK orders have strict precision requirements:**
- Size: max 2 decimal places
- Size x Price product: max 2 decimal places

**If precision fails:** Order rejected with "invalid amounts" error. Use GTC instead.

```python
# Safe FOK order
size = round(desired_size, 2)  # e.g., 100.0, not 100.123
```

## Common Issues

### FOK Order Rejected: "invalid amounts"

**Problem:** FOK precision requirements not met.

**Solution:**
```python
# Round size to 2 decimal places
size = round(original_size, 2)

# Or use GTC which has no precision restrictions
response = client.post_order(order, OrderType.GTC)
```

### Order Rejected: "Invalid price"

**Problem:** Price not a multiple of tick size.

**Solution:**
```python
tick_size = client.get_tick_size(token_id)
price = round(desired_price / tick_size) * tick_size
```

### Authentication Failed (401)

**Problem:** API credentials not set or expired.

**Solution:**
```python
# Regenerate and set credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
```

### Balance Shows $0.00

**Problem:** Wrong USDC type or wrong funder address.

**Diagnosis:**
```python
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

abi = '[{"name":"balanceOf","inputs":[{"type":"address"}],"outputs":[{"type":"uint256"}],"type":"function"}]'
contract = web3.eth.contract(address=USDC_E, abi=abi)

balance = contract.functions.balanceOf("0xYourFunderAddress").call()
print(f"USDC.e balance: ${balance / 1e6:.2f}")
```

**Solutions:**
1. If $0: You have native USDC, need to swap to USDC.e
2. If balance shows: You're checking wrong address (check funder, not EOA for proxy wallets)

### Order Placement Fails After Authentication

**Problem:** Missing token allowances (EOA wallets only).

**Solution:** Set allowances per [../auth/token-allowances.md](../auth/token-allowances.md)

```python
# Quick check
def check_allowance(wallet_address):
    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

    abi = '[{"name":"allowance","inputs":[{"type":"address"},{"type":"address"}],"outputs":[{"type":"uint256"}],"type":"function"}]'
    contract = web3.eth.contract(address=USDC_E, abi=abi)

    allowance = contract.functions.allowance(wallet_address, EXCHANGE).call()
    return allowance > 0
```

### FAK/FOK Order Shows 0 Filled

**Problem:** No liquidity available at your price.

**Solution:**
```python
# Check orderbook first
book = client.get_order_book(token_id)
if book['asks']:
    best_ask = float(book['asks'][0]['price'])
    print(f"Best ask: {best_ask}")
    # Set your price at or above best_ask for immediate fill
```

## Related Documentation

Trading connects to other Polymarket modules:

**Prerequisites:**
- **[Authentication](../auth/README.md)** - Client setup, credentials, allowances
- **[Market Discovery](../market-discovery/README.md)** - Finding markets and token IDs

**During Trading:**
- **[Real-Time Data](../real-time/README.md)** - Live price updates via WebSocket
- **[Data Analytics](../data-analytics/README.md)** - Position tracking, P&L

**Troubleshooting:**
- **[Edge Cases](../edge-cases/README.md)** - Order constraints, precision issues
- **[Library Reference](../library/README.md)** - Error handling patterns

[Back to Polymarket Skills](../SKILL.md)

## API Quick Reference

### Public Endpoints (no auth)

| Method | Endpoint | py-clob-client |
|--------|----------|----------------|
| GET | /price | `client.get_price(token_id, side)` |
| GET | /midpoint | `client.get_midpoint(token_id)` |
| GET | /book | `client.get_order_book(token_id)` |
| GET | /tick-size | `client.get_tick_size(token_id)` |

### Authenticated Endpoints

| Method | Endpoint | py-clob-client |
|--------|----------|----------------|
| POST | /order | `client.post_order(order, type)` |
| DELETE | /order/{id} | `client.cancel(order_id)` |
| GET | /orders | `client.get_orders()` |
| POST | /orders | `client.post_orders(orders, type)` |
| DELETE | /orders | `client.cancel_orders(ids)` |

**Full endpoint documentation:** [clob-api-overview.md](./clob-api-overview.md)

## Key Concepts

### Token IDs

Each market has two tokens:
- **YES token** (index 0): Pays $1 if outcome is YES
- **NO token** (index 1): Pays $1 if outcome is NO

Prices are 0.01 to 0.99, representing probability.

### Order Book

The CLOB maintains bids (buy orders) and asks (sell orders):
- **Bid:** Offer to buy at a specific price
- **Ask:** Offer to sell at a specific price
- **Spread:** Difference between best bid and best ask

### Order Lifecycle

```
CREATE --> SUBMIT --> [LIVE on book] --> MATCHED --> SETTLED
                           |
                           +--> CANCELLED (user or GTD expiry)
```

### Tick Size

Minimum price increment. Always check before placing orders:

```python
tick_size = client.get_tick_size(token_id)  # Usually 0.01
```

---

**Last updated:** 2026-01-31 (Phase 2)
**Status:** Complete - All trading documentation available (CLOB-01 through CLOB-06)
