# Data API Overview

The Data API provides access to user-specific data including positions, balances, trade history, and PnL calculations. It complements the CLOB API (trading) and Gamma API (market discovery).

## API Basics

**Base URL:** `https://data-api.polymarket.com`

**Purpose:** User-specific data retrieval:
- Current positions with PnL
- Token balances
- Trade and activity history
- Portfolio analytics

**Authentication:** None required. Queries use public wallet addresses.

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/positions` | GET | User positions with PnL data |
| `/activity` | GET | Trade history and events |
| `/balances` | GET | Token balances |

## When to Use Data API vs CLOB API

| Need | Use | Why |
|------|-----|-----|
| Quick position check during trading | CLOB `get_positions()` | Lower latency, same session |
| Detailed PnL and portfolio analytics | Data API `/positions` | Rich PnL fields, sortable |
| Trade history for accounting | Data API `/activity` | Complete records with types |
| Historical price charts | CLOB `/prices-history` | Part of CLOB API |
| Token balances | Data API `/balances` | Comprehensive balance view |

## API Architecture

```
+---------------------+     +---------------------+     +---------------------+
|                     |     |                     |     |                     |
|  Gamma API          |     |  CLOB API           |     |  Data API           |
|  (Discovery)        |     |  (Trading)          |     |  (Analytics)        |
|                     |     |                     |     |                     |
|  - Market search    |     |  - Order placement  |     |  - Positions/PnL    |
|  - Event metadata   |     |  - Order book       |     |  - Trade history    |
|  - Categories       |     |  - Price history    |     |  - Balances         |
|                     |     |  - Quick positions  |     |  - Activity types   |
+---------------------+     +---------------------+     +---------------------+
```

## Basic Query Pattern

```python
import requests

DATA_URL = "https://data-api.polymarket.com"

def query_data_api(endpoint: str, params: dict):
    """Generic Data API query function."""
    response = requests.get(f"{DATA_URL}/{endpoint}", params=params)
    response.raise_for_status()
    return response.json()

# Example: Get positions for a wallet
def get_positions(wallet_address: str, **kwargs):
    """Get user positions with PnL data."""
    response = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address,
        **kwargs
    })
    response.raise_for_status()
    return response.json()

# Example: Get activity history
def get_activity(wallet_address: str, **kwargs):
    """Get trade and activity history."""
    response = requests.get(f"{DATA_URL}/activity", params={
        "user": wallet_address,
        **kwargs
    })
    response.raise_for_status()
    return response.json()

# Example: Get balances
def get_balances(wallet_address: str):
    """Get token balances."""
    response = requests.get(f"{DATA_URL}/balances", params={
        "user": wallet_address
    })
    response.raise_for_status()
    return response.json()
```

## Common Query Parameters

Most Data API endpoints support these parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `user` | string | Wallet address (required) |
| `limit` | int | Maximum results to return |
| `offset` | int | Skip N results (pagination) |
| `sortBy` | string | Field to sort by |
| `sortDirection` | string | ASC or DESC |

## Response Format

All endpoints return JSON arrays or objects:

```python
# Positions response
[
    {
        "proxyWallet": "0x...",
        "asset": "71321...",
        "conditionId": "0x...",
        "size": 100.0,
        "avgPrice": 0.45,
        "cashPnl": 5.0,
        # ... more fields
    }
]

# Activity response
[
    {
        "id": "...",
        "type": "TRADE",
        "user": "0x...",
        "timestamp": "2024-01-15T10:30:00Z",
        # ... more fields
    }
]
```

## Error Handling

```python
import requests
from requests.exceptions import HTTPError

def safe_query(endpoint: str, params: dict):
    """Query with error handling."""
    try:
        response = requests.get(f"{DATA_URL}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        if e.response.status_code == 400:
            print("Bad request - check parameters")
        elif e.response.status_code == 404:
            print("Endpoint not found")
        elif e.response.status_code == 429:
            print("Rate limited - slow down requests")
        raise
```

## Rate Limits

The Data API has rate limits. Implement appropriate delays:

```python
import time

def batch_query(wallet_addresses: list, delay: float = 0.5):
    """Query multiple wallets with rate limiting."""
    results = {}
    for wallet in wallet_addresses:
        results[wallet] = get_positions(wallet)
        time.sleep(delay)  # Respect rate limits
    return results
```

## Related Documentation

- [Positions and History](./positions-and-history.md) - Detailed position and trade history queries
- [Historical Prices](./historical-prices.md) - Price timeseries via CLOB API
- [Trading Skill](../trading/) - Place and manage orders
- [Market Discovery](../market-discovery/) - Find and explore markets
