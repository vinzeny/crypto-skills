# Price vs Odds Interpretation

Understanding the difference between midpoint prices and executable prices to avoid common trading mistakes.

## The Confusion

When viewing Polymarket markets, you see a price displayed (e.g., "50%"). This is typically the **midpoint** - the average of best bid and best ask. Users commonly expect to buy at this price, but the actual execution price is different.

**Common mistake:** Expecting to buy at 50% (midpoint) but actually paying 52% (ask).

## Key Concepts

| Concept | Definition | Use Case |
|---------|------------|----------|
| **Midpoint** | (best_bid + best_ask) / 2 | Display, analytics, position valuation |
| **Executable buy price** | Best ask (what you pay to buy now) | Calculating actual purchase cost |
| **Executable sell price** | Best bid (what you receive selling now) | Calculating actual sale proceeds |
| **Spread** | ask - bid | Actual roundtrip trading cost |

### Price Hierarchy

```
Best Ask (0.52) <-- You pay this to BUY immediately
    |
Midpoint (0.50) <-- Display price (NOT tradable)
    |
Best Bid (0.48) <-- You receive this when SELLING immediately
```

## Code Examples

### Getting Different Price Types

```python
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(host="https://clob.polymarket.com", chain_id=137)

# Midpoint: display only (NOT executable)
midpoint = client.get_midpoint(token_id)  # e.g., 0.50

# Executable prices
buy_price = client.get_price(token_id, side="BUY")   # e.g., 0.52 (ask)
sell_price = client.get_price(token_id, side="SELL") # e.g., 0.48 (bid)

# Spread = actual trading cost per roundtrip
spread = buy_price - sell_price  # 0.04 = 4 cents per share roundtrip
```

### Calculating Actual Trading Costs

```python
def calculate_trade_cost(client, token_id, size):
    """Calculate actual cost to buy and potential sale proceeds."""
    buy_price = float(client.get_price(token_id, side="BUY"))
    sell_price = float(client.get_price(token_id, side="SELL"))
    midpoint = float(client.get_midpoint(token_id))

    spread = buy_price - sell_price

    return {
        "size": size,
        "midpoint": midpoint,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "spread": spread,
        "spread_pct": f"{(spread / midpoint * 100):.2f}%",
        "buy_cost": size * buy_price,
        "sell_proceeds": size * sell_price,
        "roundtrip_cost": size * spread
    }

# Example output:
# {
#     "size": 100,
#     "midpoint": 0.50,
#     "buy_price": 0.52,
#     "sell_price": 0.48,
#     "spread": 0.04,
#     "spread_pct": "8.00%",
#     "buy_cost": 52.00,
#     "sell_proceeds": 48.00,
#     "roundtrip_cost": 4.00  # Cost to buy and immediately sell
# }
```

### Checking Order Book Depth for Large Orders

```python
def estimate_execution_price(client, token_id, side, size):
    """
    Estimate average execution price for a large order.

    Large orders may "walk the book" - consuming liquidity at
    progressively worse prices.
    """
    book = client.get_order_book(token_id)

    if side == "BUY":
        levels = book.get("asks", [])  # Buy from asks
    else:
        levels = book.get("bids", [])  # Sell to bids

    if not levels:
        return None

    remaining_size = size
    total_cost = 0
    fills = []

    for level in levels:
        level_price = float(level["price"])
        level_size = float(level["size"])

        fill_size = min(remaining_size, level_size)
        total_cost += fill_size * level_price
        remaining_size -= fill_size

        fills.append({
            "price": level_price,
            "size": fill_size
        })

        if remaining_size <= 0:
            break

    if remaining_size > 0:
        return {
            "error": "Insufficient liquidity",
            "unfilled_size": remaining_size,
            "available_size": size - remaining_size
        }

    avg_price = total_cost / size

    return {
        "average_price": avg_price,
        "total_cost": total_cost,
        "fills": fills,
        "slippage_from_best": avg_price - float(levels[0]["price"])
    }
```

## When to Use What

| Purpose | Method | Example |
|---------|--------|---------|
| Display probability | `get_midpoint()` | "Market at 50%" |
| Calculate buy cost | `get_price(side="BUY")` | "Buying at $0.52/share" |
| Calculate sell proceeds | `get_price(side="SELL")` | "Selling at $0.48/share" |
| Analyze liquidity | `get_order_book()` | Full depth view for large orders |
| Estimate large order impact | Walk the book | Average execution price |

## Warning Signs of Price Confusion

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Expecting fills at displayed price | Using midpoint as execution price | Use `get_price()` for actual execution price |
| PnL calculations are off | Calculating with midpoint instead of fills | Track actual fill prices from order responses |
| Surprised by trading costs | Ignoring spread | Always check spread before trading |
| Large orders cost more than expected | Not accounting for slippage | Check order book depth for size |

## Spread Analysis

### Understanding Spread Impact

```python
def analyze_spread(client, token_id):
    """Analyze spread and liquidity conditions."""
    buy_price = float(client.get_price(token_id, side="BUY"))
    sell_price = float(client.get_price(token_id, side="SELL"))
    midpoint = float(client.get_midpoint(token_id))

    spread = buy_price - sell_price
    spread_pct = (spread / midpoint) * 100 if midpoint > 0 else 0

    # Classify liquidity
    if spread_pct < 2:
        liquidity = "HIGH - tight spread, low trading cost"
    elif spread_pct < 5:
        liquidity = "MEDIUM - moderate spread"
    elif spread_pct < 10:
        liquidity = "LOW - wide spread, consider limit orders"
    else:
        liquidity = "VERY LOW - avoid market orders"

    return {
        "midpoint": midpoint,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "spread": spread,
        "spread_pct": f"{spread_pct:.2f}%",
        "liquidity_assessment": liquidity
    }
```

### Spread Thresholds

| Spread % | Liquidity | Trading Recommendation |
|----------|-----------|----------------------|
| < 2% | High | Market orders acceptable |
| 2-5% | Medium | Limit orders preferred |
| 5-10% | Low | Use limit orders, be patient |
| > 10% | Very Low | Avoid large positions, wait for liquidity |

## Best Practices

1. **Always check order book for actual depth**, especially for orders > $100
2. **Use limit orders in low-liquidity markets** to avoid paying wide spreads
3. **Track actual fill prices**, not midpoint, for PnL calculations
4. **Monitor spread changes** - spreads widen during volatility
5. **Consider slippage for large orders** - check book depth before executing

## Common Mistakes

### Mistake 1: Using Midpoint for Order Placement

```python
# WRONG - may result in unfilled order
midpoint = client.get_midpoint(token_id)
order_args = OrderArgs(price=midpoint, ...)  # Limit at midpoint won't fill

# CORRECT - use executable price
buy_price = client.get_price(token_id, side="BUY")
order_args = OrderArgs(price=buy_price, ...)  # Will execute immediately
```

### Mistake 2: Calculating PnL with Midpoint

```python
# WRONG - overstates actual value
position_value = shares * midpoint

# CORRECT - use executable sell price for realistic value
position_value = shares * client.get_price(token_id, side="SELL")
```

### Mistake 3: Ignoring Spread in Low-Liquidity Markets

```python
# WRONG - assuming displayed price reflects trading cost
expected_cost = shares * displayed_price

# CORRECT - factor in spread
spread_info = analyze_spread(client, token_id)
if float(spread_info["spread_pct"].rstrip('%')) > 5:
    print(f"Warning: Wide spread ({spread_info['spread_pct']})")
    print("Consider using limit orders or smaller size")
```

## Related Documentation

- [CLOB API Overview](../trading/clob-api-overview.md) - Full order book and price endpoints
- [Order Types](../trading/order-types.md) - GTC, GTD, FOK, FAK selection
- [Order Lifecycle](../trading/order-lifecycle.md) - Order states and fill tracking

---

**Last updated:** 2026-01-31
**Covers:** EDGE-04 (Price vs Odds Interpretation)
