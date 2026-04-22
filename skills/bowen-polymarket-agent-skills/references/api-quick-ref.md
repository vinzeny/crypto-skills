# Polymarket API Quick Reference

## Base URLs

| Service | URL |
|---------|-----|
| CLOB API | `https://clob.polymarket.com` |
| Gamma API | `https://gamma-api.polymarket.com` |
| Data API | `https://data-api.polymarket.com` |
| Bridge API | `https://bridge.polymarket.com` |
| WebSocket | `wss://ws-subscriptions-clob.polymarket.com/ws/` |

---

## CLOB API Endpoints

### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/api-key` | POST | L1 | Create new API credentials |
| `/auth/derive-api-key` | GET | L1 | Derive existing API credentials |

### Orders (L2 Auth Required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/order` | POST | Place single order |
| `/orders` | GET | Get user's open orders |
| `/cancel` | DELETE | Cancel order by ID |
| `/cancel-orders` | DELETE | Cancel multiple orders |
| `/cancel-all` | DELETE | Cancel all orders |
| `/cancel-market-orders` | DELETE | Cancel all orders for market |

### Orderbook (Public)

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/book` | GET | `token_id` | Get order book |
| `/books` | GET | `token_ids` (comma-sep) | Get multiple books |
| `/price` | GET | `token_id`, `side` | Get market price |
| `/midpoint` | GET | `token_id` | Get midpoint price |
| `/spread` | GET | `token_id` | Get bid-ask spread |
| `/tick-size` | GET | `token_id` | Get min tick size |
| `/neg-risk` | GET | `token_id` | Check negative risk |
| `/prices-history` | GET | `market`, `interval` | Get price history |

### Trades (L2 Auth Required)

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/data/trades` | GET | `market`, `before`, `after` | Get trade history |

### Account (L2 Auth Required)

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/balance-allowance` | GET | `asset_type`, `token_id` | Get balance/allowance |

### Status (Public)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ok` | GET | Health check |
| `/time` | GET | Server timestamp |

---

## Gamma API Endpoints

All endpoints are **public** (no auth required).

### Markets

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/markets` | GET | `limit`, `offset`, `active`, `order` | List markets |
| `/markets/{conditionId}` | GET | - | Get market by ID |
| `/markets/slug/{slug}` | GET | - | Get market by slug |

### Events

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/events` | GET | `limit`, `offset`, `active` | List events |
| `/events/{eventId}` | GET | - | Get event by ID |
| `/events/slug/{slug}` | GET | - | Get event by slug |

### Series

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/series` | GET | `limit`, `offset`, `slug` | List series |
| `/series/{seriesId}` | GET | - | Get series by ID |

### Tags

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/tags` | GET | `limit`, `offset` | List tags |
| `/tags/{tagId}` | GET | - | Get tag by ID |
| `/tags/slug/{slug}` | GET | - | Get tag by slug |

### Search & Profiles

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/public-search` | GET | `q`, `limit_per_type` | Search markets/events |
| `/public-profile` | GET | `address` | Get user profile |

### Sports

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/sports` | GET | - | Get sports metadata |
| `/teams` | GET | `sport`, `league` | List teams |

### Comments

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/comments` | GET | `market`, `event` | Get comments |

---

## Data API Endpoints

All endpoints are **public** (no auth required).

### Positions

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/positions` | GET | `user`, `market` | Get user positions |
| `/closed-positions` | GET | `user`, `sortBy` | Get closed positions |
| `/value` | GET | `user` | Get total position value |

### Activity

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/activity` | GET | `user`, `type`, `side` | Get user activity |

### Leaderboards

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/v1/leaderboard` | GET | `timePeriod`, `limit` | Trader leaderboard |
| `/v1/builders/leaderboard` | GET | `timePeriod` | Builder leaderboard |

### Analytics

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/oi` | GET | `market` | Get open interest |
| `/live-volume` | GET | `id` (event) | Get live volume |
| `/holders` | GET | `market`, `limit` | Get top holders |
| `/traded` | GET | `user` | Get markets traded count |

---

## Bridge API Endpoints

All endpoints are **public** (no auth required).

| Endpoint | Method | Body/Params | Description |
|----------|--------|-------------|-------------|
| `/supported-assets` | GET | - | Get supported chains/tokens |
| `/deposit` | POST | `address` | Create deposit addresses |
| `/withdraw` | POST | `address` | Create withdrawal addresses |
| `/quote` | POST | Quote request body | Get bridge quote |
| `/status/{address}` | GET | - | Get transaction status |

---

## WebSocket Channels

### Market Channel (Public)

```json
{
  "type": "MARKET",
  "assets_ids": ["token_id_1", "token_id_2"],
  "custom_feature_enabled": true
}
```

**Events:** `book`, `price_change`, `last_trade_price`, `tick_size_change`, `best_bid_ask`, `new_market`, `market_resolved`

### User Channel (Authenticated)

```json
{
  "auth": {
    "apiKey": "your-api-key",
    "secret": "your-secret",
    "passphrase": "your-passphrase"
  },
  "type": "USER",
  "markets": ["condition_id_1"]
}
```

**Events:** `order` (PLACEMENT/UPDATE/CANCELLATION), `trade` (MATCHED/MINED/CONFIRMED/FAILED)

---

## Common Parameters

### Pagination
- `limit`: Max results (default varies)
- `offset`: Skip first N results

### Sorting
- `order`/`sortBy`: Field to sort by
- `ascending`/`sortDirection`: Sort direction

### Filtering
- `active`: Active only (bool)
- `closed`: Closed only (bool)
- `market`: Condition ID
- `user`: Wallet address

---

## Order Types

| Type | Description |
|------|-------------|
| GTC | Good-Til-Cancelled - active until filled or cancelled |
| GTD | Good-Til-Date - active until expiration timestamp |
| FOK | Fill-Or-Kill - must fill completely or cancel |
| FAK | Fill-And-Kill - partial fills allowed, rest cancelled |

## Signature Types

| Type | Value | Description |
|------|-------|-------------|
| EOA | 0 | Standard Ethereum wallet (MetaMask) |
| POLY_PROXY | 1 | Magic Link email/Google users |
| GNOSIS_SAFE | 2 | Gnosis Safe proxy wallet (most common) |
