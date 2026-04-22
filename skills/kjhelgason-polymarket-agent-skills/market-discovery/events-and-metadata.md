# Events and Metadata Reference

Complete field reference for Polymarket events and markets from the Gamma API.

## Overview

Polymarket uses a hierarchical data model:

```
Event (proposition/question)
  |
  +-- Market (tradable outcome)
        |
        +-- Token (YES or NO position)
```

**Example:**
- **Event:** "2024 US Presidential Election Winner"
- **Markets:** "Biden", "Trump", "Other"
- **Tokens:** Each market has YES and NO tokens

This guide documents all fields returned by the Gamma API for events and markets.

## Event Fields Reference

Events are the top-level entities representing questions or propositions.

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique event identifier | `"16085"` |
| `slug` | string | URL-friendly name | `"fed-decision-october-2024"` |
| `title` | string | Human-readable title | `"Fed Rate Decision October 2024"` |
| `description` | string | Full event description | `"Will the Federal Reserve..."` |
| `ticker` | string | Short identifier | `"FED-OCT-24"` |

### Status Fields

| Field | Type | Description | Values/Example |
|-------|------|-------------|----------------|
| `active` | boolean | Currently tradeable | `true` / `false` |
| `closed` | boolean | Trading has ended | `true` / `false` |
| `archived` | boolean | Hidden from main UI | `true` / `false` |
| `restricted` | boolean | Geographic restrictions | `true` / `false` |

### Market Relationship Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `markets` | array | Nested market objects | `[{...}, {...}]` |
| `negRisk` | boolean | Multi-outcome market flag | `true` / `false` |
| `negRiskMarketId` | string | ID for negRisk coordination | `"0x123..."` |

### Volume and Liquidity Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `volume` | string | Total volume traded (USD) | `"1234567.89"` |
| `liquidity` | string | Current liquidity (USD) | `"50000.00"` |
| `volume24hr` | string | 24-hour volume | `"12345.67"` |

**Note:** Volume and liquidity are returned as strings to preserve decimal precision. Convert to float for calculations.

### Time Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `createdAt` | string | Event creation timestamp (ISO 8601) | `"2024-10-01T12:00:00Z"` |
| `updatedAt` | string | Last update timestamp | `"2024-10-15T08:30:00Z"` |
| `endDate` | string | When event concludes | `"2024-12-31T23:59:59Z"` |
| `startDate` | string | When trading opened | `"2024-10-01T00:00:00Z"` |

### Resolution Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resolvedAt` | string | Resolution timestamp | `"2024-11-05T12:00:00Z"` |
| `resolution` | string | Resolution outcome | `"YES"` / `"NO"` |
| `resolutionSource` | string | Authority for resolution | `"Official announcement"` |

### Metadata Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `category` | string | Event category | `"Politics"` |
| `tags` | array | Category tags | `[{"id": 15, "label": "Politics"}]` |
| `image` | string | Event image URL | `"https://..."` |

## Market Fields Reference

Markets are tradable outcomes nested within events.

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `conditionId` | string | CLOB condition identifier | `"0x1234abcd..."` |
| `clobTokenIds` | array | Token IDs: [YES, NO] | `["71321...", "72541..."]` |
| `question` | string | Market question | `"Will the Fed raise rates?"` |
| `description` | string | Detailed description | `"This market resolves..."` |
| `marketSlug` | string | URL-friendly market name | `"will-fed-raise-rates"` |

### Token ID Mapping

The `clobTokenIds` array maps to outcomes:

```python
# clobTokenIds structure
token_ids = market["clobTokenIds"]
yes_token_id = token_ids[0]  # First element is YES
no_token_id = token_ids[1]   # Second element is NO

# Use these for CLOB trading
# Example:
# ["71321456789012345678901234567890123456789012345678901234567890123456",
#  "72541234567890123456789012345678901234567890123456789012345678901234"]
```

### Outcome Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `outcomes` | array | Outcome names | `["Yes", "No"]` |
| `outcomePrices` | array | Current prices (decimal) | `["0.65", "0.35"]` |
| `outcomeWeights` | array | Liquidity weights | `[65, 35]` |

### Price Interpretation

```python
# outcomePrices are decimal probabilities
prices = market["outcomePrices"]
yes_price = float(prices[0])  # e.g., 0.65 = 65% implied probability
no_price = float(prices[1])   # e.g., 0.35 = 35% implied probability

# Prices should sum to approximately 1.0
# (may differ slightly due to spread)

# Converting to implied probability percentage
yes_probability = yes_price * 100  # 65%
no_probability = no_price * 100    # 35%

# Converting to American odds (approximate)
def price_to_american_odds(price):
    if price >= 0.5:
        return int(-100 * price / (1 - price))  # Negative odds
    else:
        return int(100 * (1 - price) / price)   # Positive odds
```

### Market Status Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `active` | boolean | Trading is open | `true` |
| `closed` | boolean | Trading has ended | `false` |
| `acceptingOrders` | boolean | New orders accepted | `true` |
| `enableOrderBook` | boolean | Order book is active | `true` |

### Resolution Status Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resolved` | boolean | Market has resolved | `false` |
| `resolvedAt` | string | Resolution timestamp | `null` or ISO 8601 |
| `winner` | string | Winning outcome | `"Yes"` or `"No"` |
| `winningOutcome` | string | Alternative winner field | `"Yes"` |

### Time Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `endDate` | string | Market end timestamp | `"2024-12-31T00:00:00Z"` |
| `createdAt` | string | Creation timestamp | `"2024-10-01T12:00:00Z"` |
| `updatedAt` | string | Last update | `"2024-10-15T08:30:00Z"` |

### Volume and Liquidity

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `volume` | string | Total volume traded | `"500000.00"` |
| `liquidity` | string | Current liquidity | `"25000.00"` |
| `orderMinSize` | number | Minimum order size | `5.0` |

## Resolution Status Detection

Detect the current state of a market using multiple fields.

### State Detection Logic

```python
def get_market_state(market):
    """
    Determine market state from API fields.

    Returns: 'open', 'closed_pending', 'resolved'
    """
    # Check resolved first
    if market.get("resolved") or market.get("resolvedAt"):
        return "resolved"

    # Check if closed but not resolved
    if market.get("closed") or not market.get("active"):
        return "closed_pending"

    # Otherwise open for trading
    return "open"

def get_resolution_details(market):
    """Extract resolution information if available."""
    if not market.get("resolved"):
        return None

    return {
        "winner": market.get("winner") or market.get("winningOutcome"),
        "resolved_at": market.get("resolvedAt"),
        "resolution": market.get("resolution")
    }
```

### State Descriptions

| State | Characteristics | Trading | Redemption |
|-------|-----------------|---------|------------|
| **Open** | `active=true`, `closed=false` | Yes | No |
| **Closed Pending** | `active=false`, `closed=true`, `resolved=false` | No | No |
| **Resolved** | `resolved=true`, `winner` populated | No | Yes |

### Complete Example

```python
def analyze_market_status(market):
    """Complete market status analysis."""
    state = get_market_state(market)

    print(f"Question: {market['question']}")
    print(f"State: {state}")

    if state == "open":
        prices = market.get("outcomePrices", [])
        if len(prices) >= 2:
            print(f"YES: {float(prices[0]):.1%}")
            print(f"NO: {float(prices[1]):.1%}")
        print(f"End date: {market.get('endDate')}")

    elif state == "closed_pending":
        print("Trading closed, awaiting resolution")
        print(f"Closed at: {market.get('updatedAt')}")

    elif state == "resolved":
        details = get_resolution_details(market)
        print(f"Winner: {details['winner']}")
        print(f"Resolved at: {details['resolved_at']}")
```

## NegRisk Multi-Outcome Markets

Markets with `negRisk: true` have special mechanics.

### What is NegRisk?

NegRisk (Negative Risk) markets allow capital-efficient trading on mutually exclusive outcomes. In a negRisk event, only ONE market can resolve YES - all others resolve NO.

**Example:** "2024 Election Winner" with markets for Biden, Trump, and Others. Only one can win.

### Identifying NegRisk Markets

```python
def is_negrisk_event(event):
    """Check if event uses negRisk mechanics."""
    return event.get("negRisk", False)

def get_negrisk_markets(event):
    """Get all markets in a negRisk event."""
    if not is_negrisk_event(event):
        return None

    return {
        "event_id": event["id"],
        "neg_risk_market_id": event.get("negRiskMarketId"),
        "markets": [
            {
                "question": m["question"],
                "condition_id": m["conditionId"],
                "yes_price": m.get("outcomePrices", [0])[0]
            }
            for m in event.get("markets", [])
        ]
    }
```

### NegRisk Fields

| Field | Type | Description |
|-------|------|-------------|
| `negRisk` | boolean | Event uses negRisk mechanics |
| `negRiskMarketId` | string | Coordination ID for the event |
| `negRiskRequestId` | string | Request ID for negRisk operations |

### Capital Efficiency

In negRisk events:

- Buying YES in ALL outcomes costs 1.0 (guaranteed $1 payout)
- Holding NO shares can be converted to YES in all other outcomes
- This creates arbitrage and hedging opportunities

```python
# Check prices across negRisk event
def analyze_negrisk_prices(event):
    """Analyze prices across negRisk event markets."""
    if not is_negrisk_event(event):
        return None

    total_yes_price = 0
    markets_info = []

    for market in event.get("markets", []):
        prices = market.get("outcomePrices", ["0", "0"])
        yes_price = float(prices[0])
        total_yes_price += yes_price
        markets_info.append({
            "question": market["question"],
            "yes_price": yes_price
        })

    return {
        "total_yes_prices": total_yes_price,  # Should be ~1.0
        "overround": total_yes_price - 1.0,   # Market edge
        "markets": markets_info
    }
```

### Trading Considerations

| Aspect | Standard Markets | NegRisk Markets |
|--------|-----------------|-----------------|
| Max outcomes | 2 (YES/NO) | Many (one winner) |
| Price sum | YES + NO = ~1.0 | All YES = ~1.0 |
| Capital for all YES | 2.0 | 1.0 |
| Conversion | Not applicable | NO to YES available |

**Note:** Full negRisk trading strategies are covered in Phase 3 (Trading Operations).

## Outcome Interpretation

Understanding how outcomes map to tokens and prices.

### Outcome to Token Mapping

```python
def get_outcome_tokens(market):
    """
    Map outcomes to their token IDs.

    outcomes[0] -> clobTokenIds[0] (typically YES)
    outcomes[1] -> clobTokenIds[1] (typically NO)
    """
    outcomes = market.get("outcomes", ["Yes", "No"])
    token_ids = market.get("clobTokenIds", [])
    prices = market.get("outcomePrices", [])

    if len(token_ids) < 2:
        return None

    return {
        outcomes[0]: {
            "token_id": token_ids[0],
            "price": float(prices[0]) if prices else None
        },
        outcomes[1]: {
            "token_id": token_ids[1],
            "price": float(prices[1]) if len(prices) > 1 else None
        }
    }

# Usage
mapping = get_outcome_tokens(market)
# {
#     "Yes": {"token_id": "71321...", "price": 0.65},
#     "No": {"token_id": "72541...", "price": 0.35}
# }
```

### Price to Probability

```python
def interpret_prices(market):
    """
    Interpret market prices as probabilities.

    outcomePrices are decimals representing:
    - Implied probability of that outcome
    - Cost to buy 1 share (before fees)
    - Payout multiplier: 1 / price
    """
    prices = market.get("outcomePrices", [])
    outcomes = market.get("outcomes", ["Yes", "No"])

    interpretations = []
    for i, outcome in enumerate(outcomes):
        if i < len(prices):
            price = float(prices[i])
            interpretations.append({
                "outcome": outcome,
                "price": price,
                "probability": f"{price:.1%}",
                "payout_if_win": f"${1.0:.2f}",  # Always $1 per share
                "cost_per_share": f"${price:.2f}",
                "profit_per_share": f"${1.0 - price:.2f}"
            })

    return interpretations
```

## Time Field Handling

All timestamps are ISO 8601 format in UTC.

### Parsing Timestamps

```python
from datetime import datetime, timezone

def parse_polymarket_timestamp(ts_string):
    """Parse Polymarket timestamp to datetime."""
    if not ts_string:
        return None

    # Handle various formats
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(ts_string, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None

def time_until_end(market):
    """Calculate time remaining until market end."""
    end_date = parse_polymarket_timestamp(market.get("endDate"))
    if not end_date:
        return None

    now = datetime.now(timezone.utc)
    delta = end_date - now

    if delta.total_seconds() < 0:
        return "Ended"

    days = delta.days
    hours = delta.seconds // 3600
    return f"{days}d {hours}h"
```

### Resolution Timing Patterns

```python
def estimate_resolution_time(market):
    """
    Estimate when resolution might occur.

    Markets typically resolve shortly after endDate,
    but depends on resolution source.
    """
    end_date = parse_polymarket_timestamp(market.get("endDate"))
    resolution_source = market.get("resolutionSource", "")

    if not end_date:
        return "Unknown"

    # Source-based estimates
    if "official" in resolution_source.lower():
        estimate = "Within hours of official announcement"
    elif "unanimous" in resolution_source.lower():
        estimate = "May take 24-48 hours for consensus"
    else:
        estimate = "Typically within 24 hours of end date"

    return {
        "end_date": end_date,
        "resolution_source": resolution_source,
        "estimate": estimate
    }
```

## Complete Example: Market Analysis

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def analyze_event(event_id):
    """Complete analysis of an event and its markets."""
    response = requests.get(f"{GAMMA_URL}/events/{event_id}")
    response.raise_for_status()
    event = response.json()

    print(f"Event: {event['title']}")
    print(f"ID: {event['id']}")
    print(f"Status: {'Active' if event.get('active') else 'Inactive'}")
    print(f"NegRisk: {'Yes' if event.get('negRisk') else 'No'}")
    print(f"Total Volume: ${float(event.get('volume', 0)):,.2f}")
    print()

    for market in event.get("markets", []):
        print(f"  Market: {market['question']}")
        print(f"  Condition ID: {market['conditionId'][:20]}...")

        state = get_market_state(market)
        print(f"  State: {state}")

        if state == "open":
            prices = market.get("outcomePrices", [])
            if len(prices) >= 2:
                print(f"  YES: {float(prices[0]):.1%} | NO: {float(prices[1]):.1%}")

            remaining = time_until_end(market)
            print(f"  Time remaining: {remaining}")

        elif state == "resolved":
            winner = market.get("winner") or market.get("winningOutcome")
            print(f"  Winner: {winner}")

        print()

# Usage
# analyze_event("16085")
```

## Related Documentation

- **[Gamma API Overview](./gamma-api-overview.md)** - API architecture and endpoints
- **[Fetching Markets](./fetching-markets.md)** - Basic query patterns
- **[Search and Filtering](./search-and-filtering.md)** - Advanced query parameters

---

**Last updated:** 2026-01-31
**Covers:** GAMMA-02 (Market Metadata and Resolution Status)
