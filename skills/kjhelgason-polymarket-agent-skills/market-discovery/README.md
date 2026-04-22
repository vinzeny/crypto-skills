# Polymarket Market Discovery

Complete guide to discovering and querying markets on Polymarket using the Gamma API.

## Quick Start

**Fastest path to discovering markets:**

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

# Fetch active markets
response = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "closed": "false",
    "order": "volume",
    "limit": 10
})
events = response.json()

# Get token IDs for trading
market = events[0]["markets"][0]
yes_token_id = market["clobTokenIds"][0]
no_token_id = market["clobTokenIds"][1]
current_price = float(market["outcomePrices"][0])

print(f"Market: {market['question']}")
print(f"YES token: {yes_token_id} @ ${current_price:.2f}")
```

**See:** [fetching-markets.md](./fetching-markets.md) for complete query patterns

## Prerequisites

**Authentication:** None required - Gamma API is fully public

**Dependencies:**
```bash
pip install requests
```

**No API keys needed** - The Gamma API provides read-only access to market metadata without authentication.

## Documentation Index

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[gamma-api-overview.md](./gamma-api-overview.md)** | API architecture, events vs markets hierarchy | Understanding how Polymarket data is structured |
| **[fetching-markets.md](./fetching-markets.md)** | Query patterns, response schemas, token extraction | Fetching and parsing market data |
| **[search-and-filtering.md](./search-and-filtering.md)** | Advanced search, category filtering, pagination | Finding specific markets efficiently |
| **[events-and-metadata.md](./events-and-metadata.md)** | Complete field reference for events and markets | Understanding all metadata fields |

### Reading Order

**For first-time users:**
1. Start with [gamma-api-overview.md](./gamma-api-overview.md) - understand events vs markets
2. Use [fetching-markets.md](./fetching-markets.md) - learn query patterns
3. Reference [events-and-metadata.md](./events-and-metadata.md) - understand all fields

**For quick reference:**
- Jump directly to [fetching-markets.md](./fetching-markets.md) for code examples
- Use [search-and-filtering.md](./search-and-filtering.md) for advanced queries

## Common Use Cases

### Find Active Markets in a Category

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

# Get politics markets
response = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "closed": "false",
    "tag": "politics",
    "limit": 20
})
politics_events = response.json()

for event in politics_events:
    print(f"{event['title']} - {len(event['markets'])} markets")
```

### Get Details for a Specific Market

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

# By event slug (from URL)
event = requests.get(f"{GAMMA_URL}/events/slug/2024-presidential-election").json()

# Or by market condition ID
market = requests.get(f"{GAMMA_URL}/markets/{condition_id}").json()
```

### Extract Token IDs for Trading

```python
# Token IDs are required for CLOB API trading
market = event["markets"][0]

# Index 0 = YES token, Index 1 = NO token
yes_token_id = market["clobTokenIds"][0]
no_token_id = market["clobTokenIds"][1]
condition_id = market["conditionId"]

# Use these with CLOB API for order placement
```

### Check Market Status and Resolution

```python
import requests
from datetime import datetime, timezone

GAMMA_URL = "https://gamma-api.polymarket.com"

def check_market_status(condition_id: str) -> dict:
    """Get market status and resolution info."""
    market = requests.get(f"{GAMMA_URL}/markets/{condition_id}").json()

    # Parse end date
    end_date = None
    if market.get("endDate"):
        end_date = datetime.fromisoformat(
            market["endDate"].replace("Z", "+00:00")
        )

    return {
        "question": market["question"],
        "active": market.get("active", False),
        "closed": market.get("closed", False),
        "end_date": end_date,
        "resolution_source": market.get("resolutionSource"),
        "winning_outcome": market.get("winningOutcome")
    }
```

## API Reference

### Base URL

```
https://gamma-api.polymarket.com
```

### Rate Limits

The Gamma API does not publish official rate limits. Implement conservative rate limiting:

```python
import time

# Recommended: 0.5-1 second delay between requests
time.sleep(0.5)
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/events` | GET | List events with markets |
| `/events/{id}` | GET | Get event by internal ID |
| `/events/slug/{slug}` | GET | Get event by URL slug |
| `/markets` | GET | List markets |
| `/markets/{conditionId}` | GET | Get market by condition ID |

### Common Query Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `active` | `"true"` / `"false"` | Filter by trading status |
| `closed` | `"true"` / `"false"` | Filter by closed status |
| `order` | `"id"`, `"created"`, `"volume"` | Sort field |
| `ascending` | `"true"` / `"false"` | Sort direction |
| `limit` | 1-100 | Results per page |
| `offset` | 0+ | Pagination offset |
| `tag` | string | Category filter |

### Response Overview

**Events contain:**
- `id`, `slug`, `title`, `description`
- `active`, `closed`, `archived`
- `negRisk` (multi-outcome flag)
- `markets[]` (nested market objects)
- `volume`, `liquidity`

**Markets contain:**
- `conditionId` (use for CLOB trading)
- `clobTokenIds[]` (YES at [0], NO at [1])
- `question`, `outcomes`, `outcomePrices`
- `endDate`, `resolutionSource`

**See:** [gamma-api-overview.md](./gamma-api-overview.md) for complete schema documentation

## Related Documentation

Market discovery feeds into trading workflows:

- **[Trading Operations](../trading/README.md)** - Use discovered token IDs for orders
- **[Real-Time Data](../real-time/README.md)** - Subscribe to discovered markets
- **[Authentication](../auth/README.md)** - Required for placing orders (not for discovery)
- **[Edge Cases](../edge-cases/README.md)** - NegRisk patterns, multi-outcome markets

### Workflow

```
Market Discovery (Gamma API)
    |
    +-- Find active events
    +-- Get market details
    +-- Extract token IDs
            |
            v
Trading Operations (CLOB API)
    |
    +-- Place orders with token IDs
    +-- Manage positions
    +-- Monitor order status
```

[Back to Polymarket Skills](../SKILL.md)

## Key Concepts Quick Reference

### Events vs Markets

```
Event = "2024 Presidential Election" (question)
    │
    ├── Market: "Biden" (outcome)
    │       ├── YES token ($0.45)
    │       └── NO token ($0.55)
    │
    ├── Market: "Trump" (outcome)
    │       ├── YES token ($0.50)
    │       └── NO token ($0.50)
    │
    └── Market: "Other" (outcome)
            ├── YES token ($0.05)
            └── NO token ($0.95)
```

### Key Identifiers

| Identifier | Source | Use For |
|------------|--------|---------|
| `event.id` | Gamma API | Fetching event details |
| `event.slug` | URL | Human-readable event lookup |
| `market.conditionId` | Gamma API | CLOB API trading |
| `market.clobTokenIds[0]` | Gamma API | Buying/selling YES |
| `market.clobTokenIds[1]` | Gamma API | Buying/selling NO |

### Price Interpretation

- Prices are in USDC (0.00 to 1.00)
- YES price = implied probability (e.g., $0.65 = 65% chance)
- YES + NO prices approximately equal $1.00
- `outcomePrices` returns strings, convert to float for calculations

## Troubleshooting

### Empty Response

**Symptom:** API returns empty array

**Causes:**
- No matching events for filters
- Invalid parameter values

**Solution:** Relax filters or check parameter spelling

### 404 Not Found

**Symptom:** Event or market not found

**Causes:**
- Invalid ID or slug
- Event/market archived or deleted

**Solution:** Verify ID exists using list endpoint first

### Slow Responses

**Symptom:** Requests take 5+ seconds

**Causes:**
- Large result sets without pagination
- Rate limiting

**Solution:** Use `limit` parameter and implement pagination

---

**Last updated:** 2026-01-31 (Phase 2)
**Status:** Complete - Market Discovery documentation finalized
