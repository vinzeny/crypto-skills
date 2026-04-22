# Gamma API Overview

## Introduction

The Gamma API is Polymarket's read-only REST service for accessing market metadata, events, and categories. It provides the entry point for discovering tradable markets and understanding their structure before interacting with the CLOB (Central Limit Order Book) API.

**Base URL**: `https://gamma-api.polymarket.com`

**Key Characteristics**:
- Read-only API (no trading operations)
- No authentication required for read operations
- JSON response format
- RESTful endpoint design
- Rate limiting applies (implement conservative delays between requests)

## Events vs Markets Hierarchy

Understanding the relationship between events and markets is fundamental to working with Polymarket.

### Conceptual Model

```
Event (Question/Proposition)
├── Market 1 (Tradable Outcome)
│   ├── YES Token
│   └── NO Token
├── Market 2 (Tradable Outcome)
│   ├── YES Token
│   └── NO Token
└── Market N...
```

### Events

An **event** represents a proposition or question that will resolve to a specific outcome.

**Examples of events**:
- "2024 US Presidential Election Winner"
- "Will Bitcoin reach $100k by end of 2024?"
- "Super Bowl LVIII Winner"

**Event characteristics**:
- Contains one or more markets
- Has a resolution date when outcomes are determined
- Can be active (trading enabled) or closed (trading disabled)
- May be archived after resolution

### Markets

A **market** represents a specific tradable outcome within an event.

**Examples of markets** (within "2024 US Presidential Election Winner" event):
- "Biden" market
- "Trump" market
- "Other" market

**Market characteristics**:
- Each market has exactly 2 tokens: YES and NO
- YES + NO prices always sum to approximately $1.00
- Prices represent implied probability (e.g., $0.60 YES = 60% implied probability)
- Each market has a unique `conditionId` used for CLOB trading

### Key Identifiers

| Identifier | Level | Purpose | Example |
|------------|-------|---------|---------|
| `event.id` | Event | Internal event ID | `"12345"` |
| `event.slug` | Event | URL-friendly identifier | `"2024-presidential-election"` |
| `market.conditionId` | Market | Primary market identifier for CLOB | `"0x1234...abcd"` |
| `market.clobTokenIds` | Market | Trading token IDs [YES, NO] | `["12345", "67890"]` |

### Multi-Outcome Events (negRisk)

Events with the `negRisk: true` flag are multi-outcome events where multiple outcomes are mutually exclusive.

**Example**: "2024 Presidential Election Winner" with Biden, Trump, and Other markets.
- Only one outcome can resolve YES
- All other outcomes resolve NO
- Uses the Neg Risk Exchange contract for trading

```python
# Check if event is multi-outcome
event = events[0]
if event.get("negRisk", False):
    print("Multi-outcome event - uses Neg Risk Exchange")
else:
    print("Binary event - uses CTF Exchange")
```

## API Endpoints Overview

### Events Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/events` | GET | List events with pagination and filters |
| `/events/{id}` | GET | Get single event by internal ID |
| `/events/slug/{slug}` | GET | Get event by URL slug |

### Markets Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/markets` | GET | List markets with pagination and filters |
| `/markets/{conditionId}` | GET | Get single market by condition ID |

## Events Response Structure

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

response = requests.get(f"{GAMMA_URL}/events", params={"active": "true", "limit": 1})
event = response.json()[0]
```

### Event Fields Reference

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Internal event ID |
| `slug` | string | URL-friendly identifier for web links |
| `title` | string | Display title of the event |
| `description` | string | Detailed description (may contain HTML/markdown) |
| `active` | boolean | Whether trading is currently enabled |
| `closed` | boolean | Whether event has finished trading |
| `archived` | boolean | Whether event is archived (hidden from main UI) |
| `negRisk` | boolean | True for multi-outcome events |
| `markets` | array | Array of market objects within this event |
| `volume` | string | Total trading volume in USDC |
| `liquidity` | string | Current liquidity in USDC |
| `startDate` | string | When the event started (ISO 8601) |
| `endDate` | string | Expected resolution date (ISO 8601) |
| `createdAt` | string | Event creation timestamp |
| `updatedAt` | string | Last update timestamp |

### Example Event Response

```json
{
  "id": "12345",
  "slug": "will-btc-reach-100k-2024",
  "title": "Will Bitcoin reach $100k by end of 2024?",
  "description": "This market will resolve to Yes if...",
  "active": true,
  "closed": false,
  "archived": false,
  "negRisk": false,
  "markets": [...],
  "volume": "1234567.89",
  "liquidity": "456789.12",
  "startDate": "2024-01-01T00:00:00Z",
  "endDate": "2024-12-31T23:59:59Z",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-06-15T12:00:00Z"
}
```

## Markets Response Structure

Markets are nested within events or can be queried directly.

### Market Fields Reference

| Field | Type | Description |
|-------|------|-------------|
| `conditionId` | string | Primary identifier for CLOB trading |
| `clobTokenIds` | array | Token IDs [YES at index 0, NO at index 1] |
| `question` | string | Market question/title |
| `description` | string | Detailed description |
| `outcomes` | array | Outcome names (typically ["Yes", "No"]) |
| `outcomePrices` | array | Current prices as strings (e.g., ["0.65", "0.35"]) |
| `active` | boolean | Whether trading is enabled |
| `closed` | boolean | Whether market is closed |
| `endDate` | string | Resolution date (ISO 8601) |
| `resolutionSource` | string | Source used for resolution |
| `volume` | string | Trading volume in USDC |
| `liquidity` | string | Current liquidity in USDC |
| `bestBid` | string | Best bid price |
| `bestAsk` | string | Best ask price |
| `spread` | string | Bid-ask spread |

### Example Market Response

```json
{
  "conditionId": "0x1234567890abcdef1234567890abcdef12345678",
  "clobTokenIds": ["71321045679123456789", "71321045679123456790"],
  "question": "Will Bitcoin reach $100k by end of 2024?",
  "description": "This market resolves to Yes if Bitcoin...",
  "outcomes": ["Yes", "No"],
  "outcomePrices": ["0.65", "0.35"],
  "active": true,
  "closed": false,
  "endDate": "2024-12-31T23:59:59Z",
  "resolutionSource": "CoinGecko",
  "volume": "1234567.89",
  "liquidity": "456789.12",
  "bestBid": "0.64",
  "bestAsk": "0.66",
  "spread": "0.02"
}
```

## Basic Usage Examples

### Fetching Active Events

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def get_active_events(limit: int = 50, offset: int = 0) -> list:
    """Fetch active, non-closed events from Polymarket."""
    response = requests.get(
        f"{GAMMA_URL}/events",
        params={
            "active": "true",
            "closed": "false",
            "limit": limit,
            "offset": offset
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
events = get_active_events(limit=10)
for event in events:
    print(f"{event['title']} - {len(event.get('markets', []))} markets")
```

### Fetching Single Event by Slug

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def get_event_by_slug(slug: str) -> dict:
    """Fetch a specific event by its URL slug."""
    response = requests.get(f"{GAMMA_URL}/events/slug/{slug}")
    response.raise_for_status()
    return response.json()

# Usage - slug from URL like polymarket.com/event/2024-presidential-election
event = get_event_by_slug("2024-presidential-election")
print(f"Event: {event['title']}")
print(f"Markets: {len(event.get('markets', []))}")
```

### Fetching Single Market

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def get_market(condition_id: str) -> dict:
    """Fetch a specific market by condition ID."""
    response = requests.get(f"{GAMMA_URL}/markets/{condition_id}")
    response.raise_for_status()
    return response.json()

# Usage
market = get_market("0x1234567890abcdef1234567890abcdef12345678")
print(f"Question: {market['question']}")
print(f"Current prices: YES={market['outcomePrices'][0]}, NO={market['outcomePrices'][1]}")
```

## Error Handling

The Gamma API returns standard HTTP status codes:

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid query parameters |
| 404 | Not Found | Event/market ID does not exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Gamma API internal error |

### Error Handling Example

```python
import requests
from requests.exceptions import RequestException, HTTPError

GAMMA_URL = "https://gamma-api.polymarket.com"

def safe_get_events(params: dict) -> list:
    """Fetch events with proper error handling."""
    try:
        response = requests.get(f"{GAMMA_URL}/events", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    except HTTPError as e:
        if e.response.status_code == 404:
            return []  # No matching events
        elif e.response.status_code == 429:
            print("Rate limited - implement backoff")
            raise
        else:
            print(f"HTTP error: {e.response.status_code}")
            raise

    except RequestException as e:
        print(f"Network error: {e}")
        raise

# Usage
events = safe_get_events({"active": "true", "limit": 10})
```

## Relationship to CLOB API

The Gamma API provides **discovery** - finding markets and understanding their structure.

The CLOB API provides **trading** - placing orders and managing positions.

**Workflow**:
1. Use Gamma API to discover active markets
2. Extract `conditionId` and `clobTokenIds` from markets
3. Use these IDs with CLOB API to place trades

```python
# Discovery (Gamma API)
event = get_event_by_slug("2024-presidential-election")
market = event["markets"][0]

# Extract trading identifiers
condition_id = market["conditionId"]
yes_token_id = market["clobTokenIds"][0]
no_token_id = market["clobTokenIds"][1]

# Trading (CLOB API) - covered in trading-operations skill
# client.create_order(token_id=yes_token_id, ...)
```

## Best Practices

### 1. Implement Rate Limiting

```python
import time
import requests

def fetch_with_delay(url: str, params: dict, delay: float = 0.5) -> dict:
    """Fetch with conservative rate limiting."""
    time.sleep(delay)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
```

### 2. Cache Event/Market Data

Event and market metadata changes infrequently. Cache responses to reduce API calls:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_event_cached(event_id: str, cache_ttl: int = 300) -> dict:
    """Cache event data for 5 minutes."""
    # TTL is included in cache key to force refresh
    cache_key = int(time.time() / cache_ttl)
    return get_event_by_id(event_id)
```

### 3. Use Pagination for Large Queries

```python
def get_all_active_events() -> list:
    """Fetch all active events with pagination."""
    all_events = []
    offset = 0
    limit = 50

    while True:
        events = get_active_events(limit=limit, offset=offset)
        if not events:
            break
        all_events.extend(events)
        offset += limit

    return all_events
```

## Related Documentation

- [Fetching Markets](./fetching-markets.md) - Detailed query patterns and response schemas
- [Search and Filtering](./search-and-filtering.md) - Advanced search patterns (Phase 2)
- [Trading Operations](../trading-operations/) - Using market data for trading (Phase 2)

---

**Last updated**: 2026-01-31 (Phase 2)
**Status**: In Progress - Phase 2 Core API Documentation
