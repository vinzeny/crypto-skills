# Fetching Markets from Polymarket

Complete guide to querying active markets, understanding response schemas, and extracting token IDs for trading.

## Quick Start

Fetch active markets in under 10 lines:

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

# Get active, non-closed events with their markets
response = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "closed": "false",
    "limit": 50
})
events = response.json()

# Each event contains markets
for event in events[:3]:
    print(f"\n{event['title']}")
    for market in event.get('markets', []):
        print(f"  - {market['question']}: YES={market['outcomePrices'][0]}")
```

## Fetching Active Events

The primary endpoint for discovering tradable markets is `/events`.

### Basic Request

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def get_active_events(
    limit: int = 50,
    offset: int = 0,
    order: str = "volume",
    ascending: bool = False
) -> list:
    """
    Fetch active events from Polymarket.

    Args:
        limit: Maximum number of events to return (max 100)
        offset: Pagination offset
        order: Sort field (id, created, volume)
        ascending: Sort direction

    Returns:
        List of event dictionaries
    """
    response = requests.get(
        f"{GAMMA_URL}/events",
        params={
            "active": "true",
            "closed": "false",
            "limit": limit,
            "offset": offset,
            "order": order,
            "ascending": str(ascending).lower()
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
events = get_active_events(limit=50, order="volume")
print(f"Found {len(events)} active events")
```

## Query Parameters Reference

### Events Endpoint Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active` | string | - | Filter by active status (`"true"` or `"false"`) |
| `closed` | string | - | Filter by closed status (`"true"` or `"false"`) |
| `archived` | string | - | Filter by archived status (`"true"` or `"false"`) |
| `order` | string | `"id"` | Sort field: `"id"`, `"created"`, `"volume"` |
| `ascending` | string | `"false"` | Sort direction: `"true"` or `"false"` |
| `limit` | integer | 50 | Maximum results (1-100) |
| `offset` | integer | 0 | Pagination offset |
| `slug` | string | - | Filter by event slug (partial match) |
| `tag` | string | - | Filter by category tag |

### Markets Endpoint Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active` | string | - | Filter by active status |
| `closed` | string | - | Filter by closed status |
| `order` | string | `"id"` | Sort field |
| `ascending` | string | `"false"` | Sort direction |
| `limit` | integer | 50 | Maximum results (1-100) |
| `offset` | integer | 0 | Pagination offset |

### Query Examples

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

# Get highest volume events
high_volume = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "order": "volume",
    "ascending": "false",
    "limit": 20
}).json()

# Get recently created events
newest = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "order": "created",
    "ascending": "false",
    "limit": 20
}).json()

# Get closed events (for historical analysis)
closed = requests.get(f"{GAMMA_URL}/events", params={
    "closed": "true",
    "limit": 50
}).json()

# Get events by category tag
politics = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "tag": "politics",
    "limit": 50
}).json()
```

## Event Response Schema

### Complete Event Object

```python
{
    # Identification
    "id": "12345",                              # Internal event ID
    "slug": "will-btc-reach-100k-2024",         # URL-friendly identifier
    "ticker": "BTC100K",                        # Short ticker symbol

    # Display content
    "title": "Will Bitcoin reach $100k by end of 2024?",
    "description": "This market will resolve to Yes if...",

    # Status flags
    "active": True,                             # Trading enabled
    "closed": False,                            # Event finished trading
    "archived": False,                          # Hidden from main UI
    "new": False,                               # Recently created
    "featured": True,                           # Featured on homepage
    "restricted": False,                        # Geographic restrictions

    # Event type
    "negRisk": False,                           # Multi-outcome event flag

    # Nested markets
    "markets": [...],                           # Array of market objects

    # Metrics
    "volume": "1234567.89",                     # Total volume (USDC)
    "liquidity": "456789.12",                   # Current liquidity (USDC)
    "volume24hr": "12345.67",                   # 24-hour volume

    # Timestamps
    "startDate": "2024-01-01T00:00:00Z",        # Event start
    "endDate": "2024-12-31T23:59:59Z",          # Expected resolution
    "createdAt": "2024-01-01T00:00:00Z",        # Creation timestamp
    "updatedAt": "2024-06-15T12:00:00Z",        # Last update

    # Categories
    "tags": ["crypto", "bitcoin"],              # Category tags
    "category": "Crypto"                        # Primary category
}
```

### Event Field Descriptions

| Field | Description | Usage |
|-------|-------------|-------|
| `id` | Internal identifier | Use for `/events/{id}` endpoint |
| `slug` | URL slug | Use for `/events/slug/{slug}` endpoint |
| `title` | Display title | Show in UI |
| `description` | Detailed description | May contain resolution criteria |
| `active` | Trading enabled | Filter for tradable events |
| `closed` | Trading finished | Exclude from active trading |
| `negRisk` | Multi-outcome flag | Determines which exchange contract to use |
| `markets` | Nested markets | Contains tradable outcomes |
| `volume` | Total trading volume | Indicator of market activity |
| `liquidity` | Current liquidity | Indicator of trading depth |
| `endDate` | Resolution date | When outcome will be determined |

## Market Response Schema

### Complete Market Object

```python
{
    # Primary identifiers for trading
    "conditionId": "0x1234567890abcdef1234567890abcdef12345678",
    "clobTokenIds": [
        "71321045679123456789",    # YES token (index 0)
        "71321045679123456790"     # NO token (index 1)
    ],

    # Display content
    "question": "Will Bitcoin reach $100k by end of 2024?",
    "description": "This market resolves to Yes if Bitcoin...",
    "outcomes": ["Yes", "No"],                  # Outcome names

    # Current prices (as strings)
    "outcomePrices": ["0.65", "0.35"],          # [YES price, NO price]

    # Order book data
    "bestBid": "0.64",                          # Highest bid price
    "bestAsk": "0.66",                          # Lowest ask price
    "spread": "0.02",                           # Bid-ask spread

    # Status
    "active": True,                             # Trading enabled
    "closed": False,                            # Market closed

    # Resolution
    "endDate": "2024-12-31T23:59:59Z",          # Resolution date
    "resolutionSource": "CoinGecko",            # Resolution oracle
    "winningOutcome": None,                     # Set after resolution

    # Metrics
    "volume": "1234567.89",                     # Total volume (USDC)
    "liquidity": "456789.12",                   # Current liquidity (USDC)
    "volume24hr": "12345.67",                   # 24-hour volume

    # Timestamps
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-06-15T12:00:00Z",

    # Token metadata
    "image": "https://...",                     # Market image URL
    "icon": "https://..."                       # Market icon URL
}
```

### Market Field Descriptions

| Field | Description | Trading Usage |
|-------|-------------|---------------|
| `conditionId` | Primary market ID | Use for order placement |
| `clobTokenIds` | Token IDs [YES, NO] | Use for trading specific outcomes |
| `question` | Market question | Display to user |
| `outcomes` | Outcome names | Usually ["Yes", "No"] |
| `outcomePrices` | Current prices | Strings, convert to float for calculations |
| `bestBid` | Highest bid | Check before selling |
| `bestAsk` | Lowest ask | Check before buying |
| `spread` | Bid-ask spread | Indicates liquidity/cost |
| `active` | Trading enabled | Must be True to trade |
| `closed` | Trading finished | Cannot trade if True |
| `endDate` | Resolution date | Check before trading near expiry |
| `resolutionSource` | Resolution oracle | Understand how market resolves |

## Extracting Token IDs for Trading

The most critical data for trading are the token IDs. These are required for CLOB API order placement.

### Token ID Structure

```
clobTokenIds = [YES_TOKEN_ID, NO_TOKEN_ID]
                    ^              ^
                 index 0       index 1
```

**Important**: The order is always [YES, NO]. Index 0 is the YES outcome, index 1 is the NO outcome.

### Extraction Pattern

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def get_market_tokens(event_slug: str) -> list:
    """
    Get all token IDs for markets in an event.

    Returns:
        List of dicts with market info and token IDs
    """
    response = requests.get(f"{GAMMA_URL}/events/slug/{event_slug}")
    response.raise_for_status()
    event = response.json()

    tokens = []
    for market in event.get("markets", []):
        tokens.append({
            "question": market["question"],
            "condition_id": market["conditionId"],
            "yes_token_id": market["clobTokenIds"][0],
            "no_token_id": market["clobTokenIds"][1],
            "yes_price": float(market["outcomePrices"][0]),
            "no_price": float(market["outcomePrices"][1]),
            "active": market["active"]
        })
    return tokens

# Usage
tokens = get_market_tokens("2024-presidential-election")
for t in tokens:
    print(f"{t['question']}")
    print(f"  YES token: {t['yes_token_id']} @ ${t['yes_price']:.2f}")
    print(f"  NO token: {t['no_token_id']} @ ${t['no_price']:.2f}")
```

### Using Token IDs with CLOB API

```python
# After extracting tokens from Gamma API
market_tokens = get_market_tokens("some-event-slug")[0]

# Use with CLOB API for trading (covered in trading-operations skill)
# Example: Buy YES tokens
order_params = {
    "token_id": market_tokens["yes_token_id"],
    "price": 0.65,
    "size": 10,
    "side": "BUY"
}
# client.create_order(**order_params)
```

## Working with Multi-Outcome Events

Multi-outcome events (`negRisk: true`) have multiple markets representing mutually exclusive outcomes.

### Identifying Multi-Outcome Events

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def get_multi_outcome_events(limit: int = 20) -> list:
    """Fetch multi-outcome (negRisk) events."""
    response = requests.get(f"{GAMMA_URL}/events", params={
        "active": "true",
        "closed": "false",
        "limit": limit
    })
    response.raise_for_status()

    return [e for e in response.json() if e.get("negRisk", False)]

# Usage
multi_outcome = get_multi_outcome_events()
for event in multi_outcome[:3]:
    print(f"\n{event['title']} ({len(event['markets'])} outcomes)")
    for market in event['markets']:
        price = float(market['outcomePrices'][0])
        print(f"  {market['question']}: {price:.0%}")
```

### Multi-Outcome Price Interpretation

For multi-outcome events, YES prices represent probability of each outcome:

```python
# Example: Election with 3 candidates
# Market 1 (Biden):  YES = $0.45 (45% chance)
# Market 2 (Trump):  YES = $0.50 (50% chance)
# Market 3 (Other):  YES = $0.05 (5% chance)
# Total: 100% (approximately, may vary due to market dynamics)

def analyze_multi_outcome(event: dict):
    """Analyze probabilities in multi-outcome event."""
    probabilities = []
    for market in event.get("markets", []):
        yes_price = float(market["outcomePrices"][0])
        probabilities.append({
            "outcome": market["question"],
            "probability": yes_price,
            "token_id": market["clobTokenIds"][0]
        })

    # Sort by probability
    probabilities.sort(key=lambda x: x["probability"], reverse=True)

    total = sum(p["probability"] for p in probabilities)
    print(f"Total probability: {total:.2%}")

    for p in probabilities:
        print(f"  {p['outcome']}: {p['probability']:.2%}")

    return probabilities
```

## Pagination for Large Queries

When fetching all events or markets, use pagination:

```python
import requests
import time

GAMMA_URL = "https://gamma-api.polymarket.com"

def get_all_active_events(delay: float = 0.5) -> list:
    """
    Fetch all active events with pagination and rate limiting.

    Args:
        delay: Seconds to wait between requests

    Returns:
        Complete list of active events
    """
    all_events = []
    offset = 0
    limit = 100  # Max allowed per request

    while True:
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
        events = response.json()

        if not events:
            break

        all_events.extend(events)
        print(f"Fetched {len(all_events)} events so far...")

        if len(events) < limit:
            break  # Last page

        offset += limit
        time.sleep(delay)  # Rate limiting

    return all_events

# Usage
all_events = get_all_active_events()
print(f"Total active events: {len(all_events)}")
```

## Error Handling

### Complete Error Handling Pattern

```python
import requests
from requests.exceptions import RequestException, HTTPError, Timeout
import time

GAMMA_URL = "https://gamma-api.polymarket.com"

class GammaAPIError(Exception):
    """Custom exception for Gamma API errors."""
    pass

def fetch_events_safely(
    params: dict,
    max_retries: int = 3,
    timeout: int = 30
) -> list:
    """
    Fetch events with comprehensive error handling.

    Args:
        params: Query parameters
        max_retries: Number of retry attempts
        timeout: Request timeout in seconds

    Returns:
        List of events

    Raises:
        GammaAPIError: If all retries fail
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{GAMMA_URL}/events",
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()

        except Timeout:
            print(f"Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue

        except HTTPError as e:
            status = e.response.status_code

            if status == 404:
                return []  # No results

            elif status == 429:
                # Rate limited - wait and retry
                wait_time = int(e.response.headers.get("Retry-After", 60))
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            elif status >= 500:
                # Server error - retry with backoff
                print(f"Server error {status} on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            else:
                # Client error - don't retry
                raise GammaAPIError(f"Client error: {status} - {e.response.text}")

        except RequestException as e:
            print(f"Network error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue

    raise GammaAPIError(f"Failed after {max_retries} attempts")

# Usage
try:
    events = fetch_events_safely({"active": "true", "limit": 50})
    print(f"Fetched {len(events)} events")
except GammaAPIError as e:
    print(f"API error: {e}")
```

### Handling Empty Responses

```python
def get_event_safe(event_id: str) -> dict | None:
    """
    Safely fetch an event, returning None if not found.
    """
    try:
        response = requests.get(
            f"{GAMMA_URL}/events/{event_id}",
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise

    except RequestException:
        return None

# Usage
event = get_event_safe("nonexistent-id")
if event is None:
    print("Event not found")
else:
    print(f"Found: {event['title']}")
```

## Common Patterns

### Get High-Volume Active Markets

```python
def get_top_markets_by_volume(limit: int = 20) -> list:
    """Get the most actively traded markets."""
    events = requests.get(f"{GAMMA_URL}/events", params={
        "active": "true",
        "closed": "false",
        "order": "volume",
        "ascending": "false",
        "limit": limit
    }).json()

    markets = []
    for event in events:
        for market in event.get("markets", []):
            if market.get("active", False):
                markets.append({
                    "event": event["title"],
                    "question": market["question"],
                    "volume": float(market.get("volume", 0)),
                    "yes_price": float(market["outcomePrices"][0]),
                    "condition_id": market["conditionId"],
                    "yes_token": market["clobTokenIds"][0]
                })

    # Sort by volume
    markets.sort(key=lambda x: x["volume"], reverse=True)
    return markets[:limit]

# Usage
top_markets = get_top_markets_by_volume(10)
for m in top_markets:
    print(f"${m['volume']:,.0f} - {m['question']} @ {m['yes_price']:.2%}")
```

### Find Markets by Price Range

```python
def find_markets_by_price(
    min_price: float = 0.10,
    max_price: float = 0.90
) -> list:
    """Find markets with YES price in specified range."""
    events = requests.get(f"{GAMMA_URL}/events", params={
        "active": "true",
        "closed": "false",
        "limit": 100
    }).json()

    matching = []
    for event in events:
        for market in event.get("markets", []):
            if not market.get("active"):
                continue

            yes_price = float(market["outcomePrices"][0])
            if min_price <= yes_price <= max_price:
                matching.append({
                    "question": market["question"],
                    "yes_price": yes_price,
                    "condition_id": market["conditionId"],
                    "yes_token": market["clobTokenIds"][0]
                })

    return matching

# Usage - find "underdog" bets (10-30% implied probability)
underdogs = find_markets_by_price(0.10, 0.30)
print(f"Found {len(underdogs)} underdog markets")
```

### Check Market Status Before Trading

```python
def is_market_tradable(condition_id: str) -> tuple[bool, str]:
    """
    Check if a market is currently tradable.

    Returns:
        Tuple of (is_tradable, reason)
    """
    try:
        response = requests.get(
            f"{GAMMA_URL}/markets/{condition_id}",
            timeout=30
        )
        response.raise_for_status()
        market = response.json()

        if not market.get("active", False):
            return False, "Market is not active"

        if market.get("closed", False):
            return False, "Market is closed"

        # Check if near expiry (within 1 hour)
        from datetime import datetime, timezone
        end_date = market.get("endDate")
        if end_date:
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            hours_remaining = (end - now).total_seconds() / 3600
            if hours_remaining < 1:
                return False, f"Market expires in {hours_remaining:.1f} hours"

        return True, "Market is tradable"

    except Exception as e:
        return False, f"Error checking market: {e}"

# Usage
tradable, reason = is_market_tradable("0x1234...")
if tradable:
    print("Ready to trade")
else:
    print(f"Cannot trade: {reason}")
```

## Related Documentation

- [Gamma API Overview](./gamma-api-overview.md) - API architecture and concepts
- [Search and Filtering](./search-and-filtering.md) - Advanced query patterns (Phase 2)
- [Trading Operations](../trading-operations/) - Placing orders with CLOB API (Phase 2)

---

**Last updated**: 2026-01-31 (Phase 2)
**Status**: In Progress - Phase 2 Core API Documentation
