# Search and Filtering Markets

Advanced patterns for searching, filtering, and paginating through Polymarket markets using the Gamma API.

## Overview

The Gamma API provides powerful query capabilities for finding specific markets. This guide covers:

- **Keyword search** - Find markets by text in title, description, or slug
- **Category filtering** - Filter by topic tags (Politics, Sports, Crypto, etc.)
- **Status filtering** - Find active, closed, or archived markets
- **Sorting** - Order results by volume, liquidity, date, etc.
- **Pagination** - Handle large result sets efficiently

**Base URL:** `https://gamma-api.polymarket.com`

**Authentication:** None required for read operations

## Keyword Search

Search across event titles, descriptions, and slugs using the `q` parameter.

### Basic Search

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

# Search for events containing "election"
response = requests.get(f"{GAMMA_URL}/events", params={
    "q": "election",
    "active": "true"
})
response.raise_for_status()

events = response.json()
for event in events:
    print(f"{event['title']}")
    print(f"  Markets: {len(event.get('markets', []))}")
    print(f"  Volume: ${float(event.get('volume', 0)):,.2f}")
```

### Search Behavior

| Aspect | Behavior |
|--------|----------|
| **Fields searched** | title, description, slug |
| **Case sensitivity** | Case-insensitive |
| **Word matching** | Partial matches included |
| **Multi-word** | Matches any word (OR logic) |

### Search Tips

```python
# Search for specific topics
crypto_events = requests.get(f"{GAMMA_URL}/events", params={
    "q": "bitcoin",
    "active": "true"
}).json()

# Search with multiple terms (matches either)
fed_events = requests.get(f"{GAMMA_URL}/events", params={
    "q": "federal reserve rate",
    "active": "true"
}).json()

# Search markets directly (not events)
markets = requests.get(f"{GAMMA_URL}/markets", params={
    "q": "trump",
    "active": "true"
}).json()
```

## Category Filtering

Filter markets by topic category using tag IDs.

### Filtering by Tag

```python
# Filter by category tag
response = requests.get(f"{GAMMA_URL}/markets", params={
    "tag_id": 15,  # Politics category
    "active": "true",
    "limit": 50
})
markets = response.json()
```

### Common Tag Categories

The Gamma API uses numeric tag IDs for categories. Common categories include:

| Category | Tag ID | Description |
|----------|--------|-------------|
| Politics | 15 | Elections, government, policy |
| Sports | 3 | Sports events and outcomes |
| Crypto | 4 | Cryptocurrency prices and events |
| Pop Culture | 12 | Entertainment, celebrities |
| Business | 7 | Companies, finance, economics |
| Science | 8 | Science and technology |

**Note:** Tag IDs may change. Verify current tags via the `/tags` endpoint if available, or by inspecting market responses.

### Discovering Tags

```python
# Get available tags (if endpoint exists)
try:
    tags_response = requests.get(f"{GAMMA_URL}/tags")
    if tags_response.status_code == 200:
        tags = tags_response.json()
        for tag in tags:
            print(f"ID: {tag['id']}, Name: {tag.get('name', tag.get('label'))}")
except Exception:
    print("Tags endpoint may not be available - use known tag IDs")
```

### Combining Category with Search

```python
# Find sports events about basketball
response = requests.get(f"{GAMMA_URL}/events", params={
    "tag_id": 3,  # Sports
    "q": "basketball",
    "active": "true"
})
sports_basketball = response.json()
```

## Status Filtering

Filter markets by their current state.

### Status Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `active` | `true`/`false` | Market is currently tradeable |
| `closed` | `true`/`false` | Market trading has ended |
| `archived` | `true`/`false` | Market hidden from main UI |

### Status Combinations

```python
# Active and tradeable markets
active_markets = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "closed": "false"
}).json()

# Closed but not yet resolved (pending resolution)
pending_resolution = requests.get(f"{GAMMA_URL}/events", params={
    "active": "false",
    "closed": "true"
}).json()

# All markets (no status filter)
all_markets = requests.get(f"{GAMMA_URL}/events", params={
    "limit": 100
}).json()
```

### Understanding Status States

Markets progress through these states:

```
OPEN (active=true, closed=false)
  Trading is live, prices fluctuate

  |
  v

CLOSED (active=false, closed=true)
  Trading ended, awaiting resolution
  Positions locked, no new trades

  |
  v

RESOLVED (active=false, closed=true, resolved)
  Outcome determined, positions can be redeemed
  Winner field populated
```

## Sorting Options

Control the order of results.

### Sort Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `order` | Field to sort by | `id` |
| `ascending` | Sort direction | `false` (descending) |

### Available Sort Fields

| Field | Description | Use Case |
|-------|-------------|----------|
| `id` | Event/market ID | Consistent ordering |
| `created` | Creation timestamp | Find newest markets |
| `updated` | Last update time | Recently changed |
| `volume` | Total trading volume | Most popular |
| `liquidity` | Current liquidity | Best tradeable |

### Sorting Examples

```python
# Highest volume markets (most popular)
popular = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "order": "volume",
    "ascending": "false",  # Highest first
    "limit": 20
}).json()

# Newest markets
newest = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "order": "created",
    "ascending": "false",  # Most recent first
    "limit": 20
}).json()

# Most liquid markets (best for trading)
liquid = requests.get(f"{GAMMA_URL}/events", params={
    "active": "true",
    "order": "liquidity",
    "ascending": "false",
    "limit": 20
}).json()
```

## Pagination

Handle large result sets efficiently with offset-based pagination.

### Basic Pagination

```python
def fetch_events_page(offset=0, limit=50, **filters):
    """Fetch a single page of events."""
    params = {
        "limit": limit,
        "offset": offset,
        **filters
    }
    response = requests.get(f"{GAMMA_URL}/events", params=params)
    response.raise_for_status()
    return response.json()

# Fetch first page
page1 = fetch_events_page(offset=0, limit=50, active="true")
print(f"Page 1: {len(page1)} events")

# Fetch second page
page2 = fetch_events_page(offset=50, limit=50, active="true")
print(f"Page 2: {len(page2)} events")
```

### Generator Pattern for Large Datasets

```python
import time

def fetch_all_events(limit=50, delay=0.5, **filters):
    """
    Generator that handles pagination automatically.

    Args:
        limit: Items per page (max 100, default 50)
        delay: Seconds between requests (rate limiting)
        **filters: Additional query parameters

    Yields:
        dict: Individual event objects
    """
    offset = 0

    while True:
        params = {
            "limit": limit,
            "offset": offset,
            **filters
        }

        response = requests.get(f"{GAMMA_URL}/events", params=params)
        response.raise_for_status()

        batch = response.json()

        # No more results
        if not batch:
            break

        # Yield individual events
        yield from batch

        # Last page (incomplete batch)
        if len(batch) < limit:
            break

        offset += limit

        # Rate limiting delay
        if delay > 0:
            time.sleep(delay)

# Usage: Process all active events
for event in fetch_all_events(active="true", closed="false"):
    print(f"Processing: {event['title']}")
```

### Collecting All Results

```python
def fetch_all_events_list(limit=50, delay=0.5, **filters):
    """Fetch all events into a list (use for smaller datasets)."""
    return list(fetch_all_events(limit=limit, delay=delay, **filters))

# Get all active events
all_active = fetch_all_events_list(active="true", closed="false")
print(f"Total active events: {len(all_active)}")
```

### Pagination Best Practices

| Practice | Reason |
|----------|--------|
| Use reasonable limit (50) | Balances throughput and reliability |
| Add delay between pages | Avoid rate limiting |
| Check batch size | Detect last page efficiently |
| Handle empty responses | API may return empty for invalid offset |
| Use generators for large sets | Memory efficient |

## Combined Query Examples

Real-world search patterns combining multiple filters.

### Find High-Volume Political Markets

```python
def find_popular_political_markets(min_volume=100000):
    """Find high-volume political markets for trading."""
    events = []

    for event in fetch_all_events(
        active="true",
        closed="false",
        tag_id=15,  # Politics
        order="volume",
        ascending="false"
    ):
        volume = float(event.get("volume", 0))
        if volume >= min_volume:
            events.append({
                "title": event["title"],
                "volume": volume,
                "markets": len(event.get("markets", [])),
                "id": event["id"]
            })

    return events

popular_politics = find_popular_political_markets(min_volume=500000)
for p in popular_politics[:10]:
    print(f"${p['volume']:,.0f} - {p['title']}")
```

### Search and Extract Token IDs

```python
def search_and_get_tokens(query, active_only=True):
    """Search for markets and extract trading token IDs."""
    params = {"q": query}
    if active_only:
        params["active"] = "true"
        params["closed"] = "false"

    response = requests.get(f"{GAMMA_URL}/events", params=params)
    response.raise_for_status()
    events = response.json()

    results = []
    for event in events:
        for market in event.get("markets", []):
            token_ids = market.get("clobTokenIds", [])
            if len(token_ids) >= 2:
                results.append({
                    "event": event["title"],
                    "question": market.get("question", ""),
                    "yes_token": token_ids[0],
                    "no_token": token_ids[1],
                    "yes_price": market.get("outcomePrices", ["?", "?"])[0],
                    "no_price": market.get("outcomePrices", ["?", "?"])[1]
                })

    return results

# Find bitcoin markets with token IDs
btc_markets = search_and_get_tokens("bitcoin")
for m in btc_markets[:5]:
    print(f"{m['question']}")
    print(f"  YES: {m['yes_price']} (token: {m['yes_token'][:20]}...)")
```

### Monitor Recently Updated Markets

```python
from datetime import datetime, timedelta

def get_recently_updated(hours=24):
    """Get markets updated in the last N hours."""
    recent = []

    for event in fetch_all_events(
        active="true",
        order="updated",
        ascending="false",
        limit=100
    ):
        # Check update time if available
        updated = event.get("updatedAt")
        if updated:
            # Parse and check timestamp
            recent.append({
                "title": event["title"],
                "updated": updated,
                "volume": float(event.get("volume", 0))
            })

        # Stop after collecting enough
        if len(recent) >= 50:
            break

    return recent

recently_changed = get_recently_updated(hours=24)
for r in recently_changed[:10]:
    print(f"{r['updated']}: {r['title']}")
```

## Rate Limiting Considerations

The Gamma API has rate limits. Implement these protections:

### Rate Limiting Patterns

```python
import time
from functools import wraps

class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_second=2):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0

    def wait(self):
        """Wait if needed to respect rate limit."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

# Usage
rate_limiter = RateLimiter(calls_per_second=2)

def rate_limited_get(url, **kwargs):
    """Make rate-limited GET request."""
    rate_limiter.wait()
    return requests.get(url, **kwargs)
```

### Caching Frequently Accessed Data

```python
from datetime import datetime, timedelta

class SimpleCache:
    """Cache for API responses."""

    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

# Usage
cache = SimpleCache(ttl_seconds=60)

def get_event_cached(event_id):
    """Get event with caching."""
    cache_key = f"event_{event_id}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    response = requests.get(f"{GAMMA_URL}/events/{event_id}")
    response.raise_for_status()
    event = response.json()

    cache.set(cache_key, event)
    return event
```

### Best Practices Summary

| Practice | Implementation |
|----------|---------------|
| **Rate limiting** | 2 requests/second max, add delays |
| **Caching** | Cache events for 1-5 minutes |
| **Bulk queries** | Use pagination instead of many single requests |
| **Error handling** | Implement exponential backoff on 429 errors |
| **Efficient queries** | Use filters to reduce response size |

## Error Handling

Handle common API errors gracefully.

```python
import time

def fetch_with_retry(url, params, max_retries=3, initial_delay=1):
    """Fetch with exponential backoff retry."""
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:  # Rate limited
                print(f"Rate limited, waiting {delay}s...")
                time.sleep(delay)
                delay *= 2
                continue

            if response.status_code >= 500:  # Server error
                print(f"Server error {response.status_code}, retrying...")
                time.sleep(delay)
                delay *= 2
                continue

            # Client error (4xx) - don't retry
            response.raise_for_status()

        except requests.exceptions.Timeout:
            print(f"Timeout, retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
        except requests.exceptions.ConnectionError:
            print(f"Connection error, retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2

    raise Exception(f"Failed after {max_retries} retries")

# Usage
events = fetch_with_retry(
    f"{GAMMA_URL}/events",
    params={"active": "true", "limit": 50}
)
```

## Related Documentation

- **[Fetching Markets](./fetching-markets.md)** - Basic market query patterns this builds upon
- **[Events and Metadata](./events-and-metadata.md)** - Complete field reference for response data
- **[Gamma API Overview](./gamma-api-overview.md)** - API architecture and endpoints

---

**Last updated:** 2026-01-31
**Covers:** GAMMA-03 (Search and Filtering), GAMMA-04 (Pagination)
