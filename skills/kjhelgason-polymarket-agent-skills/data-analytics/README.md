# Data Analytics Skill

Retrieve and analyze portfolio data from Polymarket: positions, PnL, trade history, and price timeseries.

## Quick Start

```python
import requests

DATA_URL = "https://data-api.polymarket.com"

# Get your positions - no authentication required
wallet_address = "0xYourWalletAddress"

response = requests.get(f"{DATA_URL}/positions", params={
    "user": wallet_address,
    "sortBy": "CASHPNL",
    "sortDirection": "DESC"
})

positions = response.json()

for pos in positions[:5]:
    print(f"{pos['title'][:40]}... | {pos['outcome']}: ${pos['cashPnl']:.2f} PnL")
```

## Prerequisites

- **Python 3.7+** with requests library (`pip install requests`)
- **Wallet address** to query (your Polymarket wallet or any public address)
- **No API keys required** - Data API uses public wallet addresses

Optional for advanced usage:
- pandas (`pip install pandas`) - For DataFrame manipulation
- matplotlib (`pip install matplotlib`) - For price charting

## Documentation Index

| Document | Description | Key Topics |
|----------|-------------|------------|
| [data-api-overview.md](./data-api-overview.md) | API architecture and endpoints | Base URL, query patterns, when to use |
| [positions-and-history.md](./positions-and-history.md) | Positions, balances, trade history | PnL fields, activity types, pagination |
| [historical-prices.md](./historical-prices.md) | Price timeseries | Intervals, DataFrame conversion, charting |
| [portfolio-export.md](./portfolio-export.md) | Export data for accounting | CSV/JSON export, PnL aggregation, tax lots |

## Common Use Cases

### 1. Portfolio Tracking Dashboard

```python
def portfolio_summary(wallet_address: str):
    """Get portfolio overview with total PnL."""
    positions = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address,
        "sizeThreshold": 1
    }).json()

    total_value = sum(p.get("currentValue", 0) for p in positions)
    total_pnl = sum(p.get("cashPnl", 0) for p in positions)

    print(f"Total positions: {len(positions)}")
    print(f"Portfolio value: ${total_value:.2f}")
    print(f"Total PnL: ${total_pnl:+.2f}")

    return positions
```

### 2. PnL Calculation

```python
def calculate_pnl_breakdown(wallet_address: str):
    """Break down PnL by market."""
    positions = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address,
        "sortBy": "CASHPNL",
        "sortDirection": "DESC"
    }).json()

    winners = [p for p in positions if p.get("cashPnl", 0) > 0]
    losers = [p for p in positions if p.get("cashPnl", 0) < 0]

    print(f"Winning positions: {len(winners)}")
    print(f"Losing positions: {len(losers)}")

    if winners:
        print(f"\nTop winner: {winners[0]['title'][:50]}")
        print(f"  PnL: ${winners[0]['cashPnl']:.2f}")
```

### 3. Trade History Export

```python
def export_trades_csv(wallet_address: str, filename: str = "trades.csv"):
    """Export trade history to CSV."""
    import csv

    activity = requests.get(f"{DATA_URL}/activity", params={
        "user": wallet_address,
        "type": "TRADE",
        "limit": 1000,
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC"
    }).json()

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "type", "side", "size", "price", "asset"
        ])
        writer.writeheader()
        for trade in activity:
            writer.writerow({
                "timestamp": trade.get("timestamp"),
                "type": trade.get("type"),
                "side": trade.get("side"),
                "size": trade.get("size"),
                "price": trade.get("price"),
                "asset": trade.get("asset")
            })

    print(f"Exported {len(activity)} trades to {filename}")
```

### 4. Performance Analytics

```python
def analyze_performance(wallet_address: str):
    """Calculate win rate and average PnL."""
    positions = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address
    }).json()

    if not positions:
        print("No positions found")
        return

    pnls = [p.get("cashPnl", 0) for p in positions]
    wins = sum(1 for p in pnls if p > 0)

    print(f"Total trades: {len(positions)}")
    print(f"Win rate: {wins/len(positions)*100:.1f}%")
    print(f"Average PnL: ${sum(pnls)/len(pnls):.2f}")
    print(f"Best trade: ${max(pnls):.2f}")
    print(f"Worst trade: ${min(pnls):.2f}")
```

## API Quick Reference

| Endpoint | Purpose | Key Parameters |
|----------|---------|----------------|
| `GET /positions` | Current positions | user, sortBy, sizeThreshold |
| `GET /activity` | Trade history | user, type, limit, offset |
| `GET /balances` | Token balances | user |

**Data API Base URL:** `https://data-api.polymarket.com`

**Price History (via CLOB):** `https://clob.polymarket.com/prices-history`

## Related Documentation

Data analytics connects to these modules:

- **[Trading Operations](../trading/README.md)** - Source of positions and trades
- **[Market Discovery](../market-discovery/README.md)** - Market context and metadata
- **[Authentication](../auth/README.md)** - Not required for Data API (uses public wallet addresses)
- **[Real-Time Data](../real-time/README.md)** - Live updates vs historical analysis
- **[Library Reference](../library/README.md)** - Production patterns, error handling

[Back to Polymarket Skills](../SKILL.md)

## Troubleshooting

### Empty positions response
- Verify wallet address format (0x...)
- Check if address has any positions (new wallets may have none)
- Lower `sizeThreshold` parameter (default may filter small positions)

### Rate limiting (429 errors)
- Add delays between requests: `time.sleep(0.5)`
- Batch queries instead of rapid individual calls
- Cache results when possible

### Missing PnL fields
- Some positions may lack PnL if market is very new
- Check `curPrice` exists before calculating
