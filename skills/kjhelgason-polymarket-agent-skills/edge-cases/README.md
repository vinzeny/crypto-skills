# Edge Cases & Common Pitfalls

Quick reference for diagnosing and resolving Polymarket integration issues. These edge cases cover the most common failure points that cause hours of debugging.

## Quick Troubleshooting

Find your symptom, get your solution:

| Symptom | See |
|---------|-----|
| Polymarket shows $0.00 balance but Polygon wallet has USDC | [USDC Token Confusion](./usdc-token-confusion.md) |
| "invalid amounts" error on FOK orders | [Order Constraints](./order-constraints.md#fok-precision) |
| Order rejected after tick size check passed | [Order Constraints](./order-constraints.md#dynamic-tick-size) |
| Expected midpoint fill, got worse price | [Price Interpretation](./price-interpretation.md) |
| Market ended but no payout available | [Resolution Mechanics](./resolution-mechanics.md) |
| Confused about negRisk outcome trading | [NegRisk Trading](./negrisk-trading.md) |
| Need to track partial fills and reconcile | [Partial Fills](./partial-fills.md) |
| API returns error with status code | [Error Handling](../library/error-handling.md) |

## Edge Case Documents

### Token & Funding Issues

| Document | Issue | When You Need It |
|----------|-------|------------------|
| [USDC Token Confusion](./usdc-token-confusion.md) | Native USDC vs USDC.e | Balance shows on Polygon but not Polymarket |

### Order Placement Issues

| Document | Issue | When You Need It |
|----------|-------|------------------|
| [Order Constraints](./order-constraints.md) | Minimums, precision, tick sizes | Order rejections, "invalid amounts" errors |
| [Partial Fills](./partial-fills.md) | Tracking and reconciling fills | Order reconciliation, fill tracking |

### Price & Resolution Issues

| Document | Issue | When You Need It |
|----------|-------|------------------|
| [Price Interpretation](./price-interpretation.md) | Midpoint vs executable prices | Trading cost confusion, unexpected fills |
| [Resolution Mechanics](./resolution-mechanics.md) | UMA disputes, redemption delays | Market resolved but no payout |

### Multi-Outcome Markets

| Document | Issue | When You Need It |
|----------|-------|------------------|
| [NegRisk Trading](./negrisk-trading.md) | Multi-outcome patterns | Trading negRisk markets, share conversion |

## Library Reference

For py-clob-client specific patterns:

| Document | Description |
|----------|-------------|
| [Library Overview](../library/README.md) | py-clob-client reference |
| [Error Handling](../library/error-handling.md) | Exception types, error recovery patterns |

## Symptom-to-Solution Quick Reference

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Polygon shows USDC, Polymarket shows $0.00 | Wrong USDC token (Native vs USDC.e) | [USDC Token Confusion](./usdc-token-confusion.md) |
| FOK order rejected with "invalid amounts" | Precision requirements not met | [Order Constraints](./order-constraints.md#fok-precision) |
| Order rejected with "INVALID_ORDER_MIN_TICK_SIZE" | Tick size changed at price extremes | [Order Constraints](./order-constraints.md#dynamic-tick-size) |
| Order works as GTC but fails as FOK | FOK has stricter precision rules | [Order Constraints](./order-constraints.md#precision-fallback) |
| Orders failing after successful auth | Missing token allowances | [Token Allowances](../auth/token-allowances.md) |
| Fills at worse price than displayed | Midpoint vs executable price confusion | [Price Interpretation](./price-interpretation.md) |
| Market ended but no payout available | Resolution pending or disputed | [Resolution Mechanics](./resolution-mechanics.md) |
| Resolution taking days | UMA dispute in progress | [Resolution Mechanics](./resolution-mechanics.md#uma-oracle-resolution-process) |
| NegRisk outcome prices sum > 1.0 | Normal market edge/overround | [NegRisk Trading](./negrisk-trading.md#price-behavior) |
| Partial fill but order still live | GTC/GTD allows partial fills | [Partial Fills](./partial-fills.md) |
| 401 Unauthorized on order placement | API credentials expired | [Error Handling](../library/error-handling.md#pattern-1-401-unauthorized-recovery) |

## Troubleshooting Flow

```
Issue encountered
|
+-- Is it a funding/balance issue?
|   |
|   +-- Check USDC token type: usdc-token-confusion.md
|   +-- Check allowances: ../auth/token-allowances.md
|
+-- Is it an order rejection?
|   |
|   +-- "invalid amounts" --> order-constraints.md (precision)
|   +-- "INVALID_ORDER_MIN_TICK_SIZE" --> order-constraints.md (tick size)
|   +-- "insufficient balance" --> Check USDC.e balance
|   +-- "401 Unauthorized" --> ../library/error-handling.md
|
+-- Is it a price/fill issue?
|   |
|   +-- Unexpected fill price --> price-interpretation.md
|   +-- Partial fill tracking --> partial-fills.md
|
+-- Is it a resolution issue?
|   |
|   +-- Market ended, no payout --> resolution-mechanics.md
|   +-- UMA dispute in progress --> resolution-mechanics.md
|
+-- Is it a multi-outcome market?
    |
    +-- NegRisk confusion --> negrisk-trading.md
```

## Prevention Checklist

Before placing orders, verify:

- [ ] USDC.e balance (not Native USDC) - `check_usdc_balances()`
- [ ] Token allowances set - `check_polymarket_allowances()`
- [ ] Current tick size fetched - `client.get_tick_size(token_id)`
- [ ] FOK orders rounded to 2 decimals
- [ ] GTD expiration in seconds (not milliseconds)
- [ ] For negRisk: trading only named outcomes

## Related Documentation

When troubleshooting, you may need these related modules:

- **[Authentication](../auth/README.md)** - Credentials, allowances, wallet types
- **[Trading Operations](../trading/README.md)** - Order placement workflows
- **[Market Discovery](../market-discovery/README.md)** - Finding markets, token IDs
- **[Real-Time Data](../real-time/README.md)** - WebSocket connection issues
- **[Data Analytics](../data-analytics/README.md)** - Position queries, PnL tracking
- **[Library Reference](../library/README.md)** - Error handling, production patterns

[Back to Polymarket Skills](../SKILL.md)
