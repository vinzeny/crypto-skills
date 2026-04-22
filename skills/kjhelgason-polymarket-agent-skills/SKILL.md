---
name: polymarket
description: Polymarket prediction market API expertise. Use when implementing Polymarket trading bots, authentication flows, market discovery, WebSocket connections, or debugging py-clob-client issues. Covers CLOB API, Gamma API, Data API, edge cases like USDC.e vs native USDC, order constraints, and production patterns.
---

# Polymarket API Skills

Complete knowledge base for Polymarket API integration using py-clob-client.

## Quick Navigation

Navigate to the right module based on what you need:

| Need | Go To |
|------|-------|
| **First time setup?** | [auth/README.md](./auth/README.md) - Credentials, wallet types, allowances |
| **Finding markets?** | [market-discovery/README.md](./market-discovery/README.md) - Gamma API, search, token IDs |
| **Placing orders?** | [trading/README.md](./trading/README.md) - CLOB API, order types, management |
| **Real-time data?** | [real-time/README.md](./real-time/README.md) - WebSocket streams, orderbook |
| **Analytics/positions?** | [data-analytics/README.md](./data-analytics/README.md) - PnL, history, export |
| **Something not working?** | [edge-cases/README.md](./edge-cases/README.md) - Common pitfalls, solutions |
| **Library patterns?** | [library/README.md](./library/README.md) - Error handling, production code |

## Essential Context

Always-relevant reference information for Polymarket integration.

### API Base URLs

| API | URL | Purpose |
|-----|-----|---------|
| **CLOB** | `https://clob.polymarket.com` | Trading, orders, orderbook |
| **Gamma** | `https://gamma-api.polymarket.com` | Market discovery, metadata |
| **Data** | `https://data-api.polymarket.com` | Positions, balances, history |
| **WebSocket** | `wss://ws-subscriptions-clob.polymarket.com/ws/` | Real-time streams |

### Key Contract Addresses

| Contract | Address | Purpose |
|----------|---------|---------|
| **USDC.e** | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | Trading currency |
| **Conditional Tokens** | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` | Position tokens (ERC-1155) |
| **CTF Exchange** | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` | Primary exchange |
| **Neg Risk Exchange** | `0xC5d563A36AE78145C45a50134d48A1215220f80a` | Multi-outcome exchange |
| **Neg Risk Adapter** | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` | NegRisk adapter |

### Network

- **Chain:** Polygon Mainnet
- **Chain ID:** 137
- **RPC:** `https://polygon-rpc.com`

## Critical Warnings

The top 3 pitfalls that cause the most debugging time:

### 1. USDC.e, Not Native USDC

Polymarket uses **USDC.e** (bridged USDC), not Polygon's native USDC.

```
USDC.e:      0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174  <- Use this
Native USDC: 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359  <- Wrong token
```

**Symptom:** Polygon wallet shows USDC balance, Polymarket shows $0.00
**Solution:** Swap native USDC to USDC.e via Polymarket or QuickSwap

See: [edge-cases/usdc-token-confusion.md](./edge-cases/usdc-token-confusion.md)

### 2. FOK Order Precision

Fill-or-Kill orders require **max 2 decimal places** for size.

```python
# Wrong - will fail with "invalid amounts"
order = OrderArgs(price=0.45, size=100.123, side=BUY, token_id=token_id)

# Correct
order = OrderArgs(price=0.45, size=100.12, side=BUY, token_id=token_id)
```

**Fallback:** If FOK fails on precision, use GTC which has no precision limits.

See: [edge-cases/order-constraints.md](./edge-cases/order-constraints.md)

### 3. Proxy Wallet Funder Address

For proxy wallets (Magic/email login), use the **proxy address** as funder, not your EOA.

```python
# Wrong - using EOA address
client = ClobClient(host, key, chain_id=137, signature_type=1, funder=eoa_address)

# Correct - using proxy address (from Polymarket profile)
client = ClobClient(host, key, chain_id=137, signature_type=1, funder=proxy_address)
```

**Finding proxy address:** Check your Polymarket profile - if the address differs from your EOA, that's your proxy.

See: [auth/wallet-types.md](./auth/wallet-types.md)

## Quick Start Workflow

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
import requests

# 1. Initialize and authenticate
client = ClobClient(
    host="https://clob.polymarket.com",
    key="YOUR_PRIVATE_KEY",
    chain_id=137,
    signature_type=0,  # 0=EOA, 1=Proxy, 2=Safe
    funder="YOUR_WALLET_ADDRESS"
)
client.set_api_creds(client.create_or_derive_api_creds())

# 2. Discover markets (Gamma API - no auth needed)
events = requests.get("https://gamma-api.polymarket.com/events", params={
    "active": "true", "closed": "false", "limit": 10
}).json()
market = events[0]["markets"][0]
token_id = market["clobTokenIds"][0]  # YES token

# 3. Place order (CLOB API - authenticated)
order = client.create_order(OrderArgs(
    price=0.45, size=100.0, side=BUY, token_id=token_id
))
response = client.post_order(order, OrderType.GTC)
print(f"Order: {response.get('orderID')}")
```

## Skill Modules

| Module | Files | Topics |
|--------|-------|--------|
| **auth/** | 5 docs | Wallet types, credentials, allowances, client setup |
| **market-discovery/** | 4 docs | Gamma API, events, markets, search |
| **trading/** | 5 docs | CLOB API, order types, placement, management |
| **real-time/** | 4 docs | WebSocket, market/user channels, connection |
| **data-analytics/** | 4 docs | Positions, history, prices, export |
| **edge-cases/** | 6 docs | USDC, constraints, pricing, resolution, negRisk |
| **library/** | 2 docs | Error handling, production patterns |

## Version

See [VERSION.md](./VERSION.md) for version history and API compatibility notes.
