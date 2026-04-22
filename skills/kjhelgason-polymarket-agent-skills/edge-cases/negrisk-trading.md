# NegRisk Multi-Outcome Market Patterns

Trading safely on Polymarket's multi-outcome markets requires understanding NegRisk mechanics and avoiding the unnamed outcome pitfall.

**Covers:** EDGE-07 (NegRisk Multi-Outcome Patterns)

## What is NegRisk?

NegRisk (Negative Risk) markets enable capital-efficient trading on mutually exclusive outcomes. In a negRisk event, only ONE outcome can resolve YES - all others resolve NO.

**Example:** "2024 Election Winner" with markets for Biden, Trump, and Others. Only one can win.

**Key Properties:**
- Multiple mutually exclusive outcomes
- Only ONE can resolve YES
- Capital efficient: buying YES in all outcomes costs ~$1.00 (guaranteed $1 payout)
- NO shares can be converted to YES in all other outcomes

For basic negRisk field documentation, see [events-and-metadata.md](../market-discovery/events-and-metadata.md).

## Key Fields

| Field | Type | Meaning |
|-------|------|---------|
| `negRisk` | boolean | Basic negRisk event (mutually exclusive outcomes) |
| `enableNegRisk` | boolean | NegRisk trading mechanics enabled |
| `negRiskAugmented` | boolean | New outcomes can be added over time |
| `negRiskMarketId` | string | Coordination ID for the negRisk event |

### Field Combinations

| negRisk | enableNegRisk | negRiskAugmented | Meaning |
|---------|---------------|------------------|---------|
| true | false | false | Basic multi-outcome, fixed set |
| true | true | false | NegRisk with conversion, fixed outcomes |
| true | true | true | **AUGMENTED** - outcomes can be added |

## The Unnamed Outcome Pitfall

**CRITICAL WARNING:** Augmented negRisk events have placeholder/unnamed outcomes that should NOT be traded.

When `enableNegRisk=true` AND `negRiskAugmented=true`:
- New outcomes can be added over time as events unfold
- Unnamed outcomes are placeholders ("Other", empty string, or generic text)
- Unnamed outcome definitions can CHANGE when new named outcomes are added
- **ONLY trade named, specific outcomes**

### Why Unnamed Outcomes Are Dangerous

1. **Definition changes:** An "Other" outcome's meaning shifts when new candidates/options are added
2. **Price instability:** Unnamed outcome prices are volatile and unpredictable
3. **UI discrepancy:** Polymarket UI may hide unnamed outcomes that API returns
4. **Resolution uncertainty:** Unclear what "Other" means at resolution time

### Detection Function

```python
def is_tradable_negrisk_outcome(event: dict, market: dict) -> bool:
    """Check if a negRisk outcome should be traded.

    Args:
        event: Event object from Gamma API
        market: Market object (nested in event)

    Returns:
        True if outcome is safe to trade, False if unnamed/placeholder
    """
    if not event.get("negRisk"):
        return True  # Not negRisk, normal rules apply

    if event.get("negRiskAugmented"):
        # Only trade named outcomes in augmented events
        question = market.get("question", "")

        # Check for unnamed/placeholder indicators
        if not question:
            return False
        if question.lower() == "other":
            return False
        if question.lower().startswith("other"):
            return False
        if len(question) < 3:  # Too short to be meaningful
            return False

    return True

# Usage
event = gamma_api.get_event(event_id)
for market in event.get("markets", []):
    if is_tradable_negrisk_outcome(event, market):
        print(f"SAFE: {market['question']}")
    else:
        print(f"SKIP: {market['question']} (unnamed/placeholder)")
```

## Comprehensive NegRisk Analysis

```python
def analyze_negrisk_event(event: dict) -> dict:
    """Analyze a negRisk event for trading opportunities.

    Evaluates all markets in the event, filtering unnamed outcomes
    and calculating pricing metrics.

    Args:
        event: Event object from Gamma API

    Returns:
        Analysis dict with tradable markets, pricing info, and warnings
    """
    result = {
        "event_id": event.get("id"),
        "title": event.get("title"),
        "is_negrisk": event.get("negRisk", False),
        "is_augmented": (
            event.get("enableNegRisk", False) and
            event.get("negRiskAugmented", False)
        ),
        "tradable_markets": [],
        "skipped_markets": [],
        "total_yes_price": 0.0,
        "overround": 0.0,
        "warnings": []
    }

    if not result["is_negrisk"]:
        # Standard binary market - all markets tradable
        for market in event.get("markets", []):
            yes_price = float(market.get("outcomePrices", ["0"])[0])
            result["tradable_markets"].append({
                "question": market["question"],
                "condition_id": market["conditionId"],
                "yes_token": market["clobTokenIds"][0],
                "no_token": market["clobTokenIds"][1],
                "yes_price": yes_price
            })
        return result

    # NegRisk event - analyze each market
    for market in event.get("markets", []):
        question = market.get("question", "")
        yes_price = float(market.get("outcomePrices", ["0"])[0])

        # Check if tradable
        if result["is_augmented"]:
            # Skip unnamed outcomes
            if not question or question.lower() in ["other", "others"]:
                result["skipped_markets"].append({
                    "question": question or "(empty)",
                    "reason": "unnamed_outcome",
                    "yes_price": yes_price
                })
                continue
            if question.lower().startswith("other"):
                result["skipped_markets"].append({
                    "question": question,
                    "reason": "placeholder_outcome",
                    "yes_price": yes_price
                })
                continue

        # Tradable outcome
        result["tradable_markets"].append({
            "question": question,
            "condition_id": market["conditionId"],
            "yes_token": market["clobTokenIds"][0],
            "no_token": market["clobTokenIds"][1] if len(market["clobTokenIds"]) > 1 else None,
            "yes_price": yes_price
        })
        result["total_yes_price"] += yes_price

    # Calculate overround (market edge)
    # In a fair market, all YES prices sum to 1.0
    result["overround"] = result["total_yes_price"] - 1.0

    # Add warnings
    if result["is_augmented"]:
        result["warnings"].append("Augmented event - new outcomes may be added")

    if len(result["skipped_markets"]) > 0:
        result["warnings"].append(
            f"Skipped {len(result['skipped_markets'])} unnamed outcomes"
        )

    if result["overround"] > 0.05:
        result["warnings"].append(
            f"High overround ({result['overround']:.1%}) - check for mispricing"
        )

    if result["overround"] < -0.05:
        result["warnings"].append(
            f"Negative overround ({result['overround']:.1%}) - possible arbitrage"
        )

    return result

# Usage
event = gamma_api.get_event("16085")
analysis = analyze_negrisk_event(event)

print(f"Event: {analysis['title']}")
print(f"NegRisk: {analysis['is_negrisk']}, Augmented: {analysis['is_augmented']}")
print(f"Tradable markets: {len(analysis['tradable_markets'])}")
print(f"Skipped markets: {len(analysis['skipped_markets'])}")
print(f"Total YES prices: {analysis['total_yes_price']:.2f}")
print(f"Overround: {analysis['overround']:.1%}")

for warning in analysis["warnings"]:
    print(f"WARNING: {warning}")
```

## Trading Considerations

### Standard vs NegRisk Markets

| Aspect | Standard Markets | NegRisk Markets |
|--------|-----------------|-----------------|
| Max outcomes | 2 (YES/NO) | Many (one winner) |
| Price sum | YES + NO = ~1.0 | All YES = ~1.0 |
| Capital for all YES | 2.0 | 1.0 |
| Conversion | Not applicable | NO to YES available |
| Resolution | Any outcome resolves | Only one resolves YES |

### Price Analysis

In a properly priced negRisk market, the sum of all YES prices should equal approximately 1.0:

```python
def check_negrisk_pricing(event: dict) -> dict:
    """Check negRisk pricing for opportunities.

    Returns:
        Pricing analysis with arbitrage detection
    """
    if not event.get("negRisk"):
        return {"error": "Not a negRisk event"}

    total = 0.0
    markets = []

    for market in event.get("markets", []):
        yes_price = float(market.get("outcomePrices", ["0"])[0])
        total += yes_price
        markets.append({
            "question": market["question"][:30],
            "yes_price": yes_price
        })

    # Sort by price descending
    markets.sort(key=lambda m: m["yes_price"], reverse=True)

    overround = total - 1.0

    result = {
        "total_yes_prices": total,
        "overround": overround,
        "overround_percent": f"{overround:.1%}",
        "markets": markets
    }

    # Detect opportunities
    if overround > 0.05:
        result["opportunity"] = "HIGH_OVERROUND"
        result["interpretation"] = (
            "Market is expensive - consider selling YES across outcomes"
        )
    elif overround < -0.05:
        result["opportunity"] = "ARBITRAGE"
        result["interpretation"] = (
            "Buying YES in all outcomes costs < $1 for $1 payout"
        )
    else:
        result["opportunity"] = None
        result["interpretation"] = "Market is fairly priced"

    return result
```

### Conversion Mechanics

In negRisk events, NO shares can be converted to YES shares in all OTHER outcomes:

- Holding 1 NO share in outcome A = holding 1 YES share in all other outcomes
- This creates hedging opportunities
- Conversion happens via the NegRiskAdapter contract (on-chain operation)

```python
def calculate_conversion_value(event: dict, source_outcome: str) -> dict:
    """Calculate value of converting NO to YES in other outcomes.

    Args:
        event: NegRisk event
        source_outcome: Outcome where you hold NO shares

    Returns:
        Conversion analysis
    """
    other_yes_total = 0.0
    source_yes_price = 0.0

    for market in event.get("markets", []):
        question = market.get("question", "")
        yes_price = float(market.get("outcomePrices", ["0"])[0])

        if question == source_outcome:
            source_yes_price = yes_price
            source_no_price = 1.0 - yes_price
        else:
            other_yes_total += yes_price

    # Value of converting NO to YES in all others
    # If other_yes_total < source_no_price, conversion is profitable
    profit = source_no_price - other_yes_total

    return {
        "source_outcome": source_outcome,
        "source_no_price": source_no_price,
        "other_yes_total": other_yes_total,
        "conversion_profit": profit,
        "is_profitable": profit > 0
    }
```

## Warning Signs

Before trading any negRisk outcome, check for these warning signs:

| Warning Sign | Risk | Action |
|--------------|------|--------|
| Empty outcome name | High | Do not trade |
| Name is "Other" | High | Do not trade |
| `negRiskAugmented=true` | Medium | Only trade named outcomes |
| Outcome not in UI | High | Do not trade |
| Very low liquidity | Medium | Reduce position size |
| Overround > 5% | Low | Check for mispricing |

### Safe Trading Checklist

```python
def negrisk_trading_checklist(event: dict, market: dict) -> dict:
    """Pre-trade checklist for negRisk outcomes.

    Returns:
        Checklist results with pass/fail for each item
    """
    checks = {}

    # 1. Outcome has a name
    question = market.get("question", "")
    checks["has_name"] = bool(question and len(question) > 2)

    # 2. Not a placeholder name
    checks["not_placeholder"] = (
        question.lower() not in ["other", "others"] and
        not question.lower().startswith("other")
    )

    # 3. If augmented, extra caution
    is_augmented = event.get("negRiskAugmented", False)
    checks["augmented_safe"] = (
        not is_augmented or
        (checks["has_name"] and checks["not_placeholder"])
    )

    # 4. Has valid token IDs
    token_ids = market.get("clobTokenIds", [])
    checks["has_tokens"] = len(token_ids) >= 1

    # 5. Market is active
    checks["is_active"] = market.get("active", False)

    # Overall pass
    checks["all_passed"] = all(checks.values())

    return checks

# Usage
event = gamma_api.get_event(event_id)
for market in event.get("markets", []):
    checks = negrisk_trading_checklist(event, market)
    if checks["all_passed"]:
        print(f"SAFE TO TRADE: {market['question']}")
    else:
        failed = [k for k, v in checks.items() if not v and k != "all_passed"]
        print(f"DO NOT TRADE: {market['question']} - Failed: {failed}")
```

## Related Documentation

- [Events and Metadata](../market-discovery/events-and-metadata.md) - NegRisk field reference
- [Fetching Markets](../market-discovery/fetching-markets.md) - Querying negRisk events
- [Resolution Mechanics](./resolution-mechanics.md) - How negRisk events resolve

---

**Last updated:** 2026-01-31
**Covers:** EDGE-07 (NegRisk Multi-Outcome Patterns)
