# Positions and Trade History

This document covers retrieving positions, balances, and trade history from the Data API.

**Covers:** DATA-01 (Positions/Balances), DATA-02 (Trade History)

## Fetching Positions (DATA-01)

### Basic Position Query

```python
import requests

DATA_URL = "https://data-api.polymarket.com"

def get_positions(wallet_address: str, limit: int = 100, sort_by: str = "TOKENS"):
    """Get current positions with PnL data.

    Args:
        wallet_address: The wallet to query
        limit: Maximum positions to return
        sort_by: Sort field (CURRENT, INITIAL, TOKENS, CASHPNL, PERCENTPNL)

    Returns:
        List of position objects with PnL data
    """
    response = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address,
        "limit": limit,
        "sortBy": sort_by,
        "sortDirection": "DESC",
        "sizeThreshold": 1  # Minimum position size
    })
    response.raise_for_status()
    return response.json()
```

### Position Query Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `user` | string | Wallet address (required) | - |
| `limit` | int | Maximum results | varies |
| `sortBy` | string | Sort field | - |
| `sortDirection` | string | ASC or DESC | - |
| `sizeThreshold` | float | Minimum position size | 0 |

**Sort Options:**
- `CURRENT` - By current value
- `INITIAL` - By initial investment
- `TOKENS` - By number of shares
- `CASHPNL` - By dollar PnL
- `PERCENTPNL` - By percentage PnL

### Position Response Schema

Each position object contains:

```python
{
    "proxyWallet": "0x...",     # Trading wallet (proxy)
    "asset": "71321045...",     # Token ID
    "conditionId": "0x...",     # Market condition ID
    "size": 100.0,              # Number of shares held
    "avgPrice": 0.45,           # Average entry price
    "initialValue": 45.0,       # Entry value (size * avgPrice)
    "currentValue": 50.0,       # Current value (size * curPrice)
    "cashPnl": 5.0,             # Unrealized PnL in dollars
    "percentPnl": 11.11,        # Unrealized PnL in percent
    "curPrice": 0.50,           # Current market price
    "title": "Will X happen?",  # Market question
    "outcome": "Yes",           # Position side (Yes/No)
    "endDate": "2026-12-31T00:00:00Z",  # Market end date
    "closed": false,            # Whether position is closed
    "redeemed": false           # Whether winnings redeemed
}
```

### Position Analysis Examples

```python
def analyze_positions(wallet_address: str):
    """Comprehensive position analysis."""
    positions = get_positions(wallet_address, sort_by="CASHPNL")

    if not positions:
        print("No positions found")
        return

    # Calculate totals
    total_invested = sum(p.get("initialValue", 0) for p in positions)
    total_current = sum(p.get("currentValue", 0) for p in positions)
    total_pnl = sum(p.get("cashPnl", 0) for p in positions)

    print(f"Total positions: {len(positions)}")
    print(f"Total invested: ${total_invested:.2f}")
    print(f"Current value: ${total_current:.2f}")
    print(f"Total PnL: ${total_pnl:+.2f} ({total_pnl/total_invested*100:+.1f}%)")

    # Winners vs losers
    winners = [p for p in positions if p.get("cashPnl", 0) > 0]
    losers = [p for p in positions if p.get("cashPnl", 0) < 0]
    breakeven = [p for p in positions if p.get("cashPnl", 0) == 0]

    print(f"\nWinners: {len(winners)}")
    print(f"Losers: {len(losers)}")
    print(f"Breakeven: {len(breakeven)}")

    return positions


def get_positions_by_outcome(wallet_address: str, outcome: str = "Yes"):
    """Get positions filtered by outcome side."""
    positions = get_positions(wallet_address)
    return [p for p in positions if p.get("outcome") == outcome]


def get_open_positions(wallet_address: str):
    """Get only open (non-closed) positions."""
    positions = get_positions(wallet_address)
    return [p for p in positions if not p.get("closed", False)]


def get_redeemable_positions(wallet_address: str):
    """Get positions that can be redeemed (closed but not redeemed)."""
    positions = get_positions(wallet_address)
    return [
        p for p in positions
        if p.get("closed", False) and not p.get("redeemed", False)
    ]
```

## Balance Retrieval

### Get Token Balances

```python
def get_balances(wallet_address: str):
    """Get token balances for a wallet.

    Returns balances of outcome tokens and USDC.e.
    """
    response = requests.get(f"{DATA_URL}/balances", params={
        "user": wallet_address
    })
    response.raise_for_status()
    return response.json()
```

### Balance Response

```python
[
    {
        "asset": "71321045...",    # Token ID
        "balance": "100000000",    # Raw balance (needs decimals)
        "name": "Yes Token",       # Token name
        "symbol": "YES"            # Token symbol
    }
]
```

### USDC Balance Check

```python
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC.e on Polygon

def get_usdc_balance(wallet_address: str):
    """Get USDC.e balance specifically."""
    balances = get_balances(wallet_address)

    for balance in balances:
        if balance.get("asset", "").lower() == USDC_ADDRESS.lower():
            # USDC has 6 decimals
            raw_balance = int(balance.get("balance", "0"))
            return raw_balance / 1_000_000

    return 0.0
```

## Trade History (DATA-02)

### Basic Trade History Query

```python
def get_trade_history(
    wallet_address: str,
    activity_types: list = None,
    limit: int = 100
):
    """Get trade and activity history.

    Args:
        wallet_address: Wallet to query
        activity_types: Filter by types (TRADE, SPLIT, MERGE, etc.)
        limit: Maximum results

    Returns:
        List of activity records
    """
    params = {
        "user": wallet_address,
        "limit": limit,
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC"
    }

    if activity_types:
        # TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION, MAKER_REBATE
        params["type"] = ",".join(activity_types)

    response = requests.get(f"{DATA_URL}/activity", params=params)
    response.raise_for_status()
    return response.json()
```

### Activity Types

| Type | Description | When It Occurs |
|------|-------------|----------------|
| `TRADE` | Order fills | Buy/sell execution |
| `SPLIT` | Token split | Split collateral into Yes+No |
| `MERGE` | Token merge | Merge Yes+No into collateral |
| `REDEEM` | Market resolution | Claim winnings after resolution |
| `REWARD` | Liquidity rewards | Maker rewards credited |
| `CONVERSION` | NegRisk conversion | Convert NegRisk tokens |
| `MAKER_REBATE` | Maker fee rebate | Fee rebate for providing liquidity |

### Activity Response Schema

```python
{
    "id": "abc123...",                    # Unique activity ID
    "type": "TRADE",                      # Activity type
    "user": "0x...",                      # User wallet
    "proxyWallet": "0x...",               # Proxy wallet used
    "timestamp": "2024-01-15T10:30:00Z",  # When it occurred
    "market": "0x...",                    # Market/condition ID
    "asset": "71321...",                  # Token ID
    "title": "Will X happen?",            # Market title
    "outcome": "Yes",                     # Token side
    "side": "BUY",                        # BUY or SELL
    "size": 100.0,                        # Number of shares
    "price": 0.45,                        # Execution price
    "fee": 0.0,                           # Fee paid
    "transactionHash": "0x..."            # On-chain transaction
}
```

### Filtered Activity Queries

```python
def get_trades_only(wallet_address: str, limit: int = 100):
    """Get only trade fills (no splits, merges, etc.)."""
    return get_trade_history(wallet_address, ["TRADE"], limit)


def get_redemptions(wallet_address: str):
    """Get market resolution payouts."""
    return get_trade_history(wallet_address, ["REDEEM"])


def get_rewards(wallet_address: str):
    """Get liquidity rewards received."""
    return get_trade_history(wallet_address, ["REWARD", "MAKER_REBATE"])


def get_activity_by_market(wallet_address: str, market_id: str):
    """Get all activity for a specific market."""
    all_activity = get_trade_history(wallet_address, limit=1000)
    return [a for a in all_activity if a.get("market") == market_id]
```

## Pagination for Large Histories

The Data API uses offset-based pagination for large result sets.

### Paginated Query Generator

```python
def fetch_all_activity(wallet_address: str, limit: int = 100):
    """Generator for paginated activity history.

    Yields individual activity records, fetching more as needed.
    """
    offset = 0

    while True:
        params = {
            "user": wallet_address,
            "limit": limit,
            "offset": offset,
            "sortBy": "TIMESTAMP",
            "sortDirection": "DESC"
        }

        response = requests.get(f"{DATA_URL}/activity", params=params)
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break

        yield from batch

        if len(batch) < limit:
            break  # Last page

        offset += limit
```

### Complete History Fetch

```python
def get_complete_history(wallet_address: str):
    """Fetch complete trade history (all pages)."""
    all_activity = list(fetch_all_activity(wallet_address))
    print(f"Fetched {len(all_activity)} total activities")
    return all_activity
```

### Paginated Position Query

```python
def fetch_all_positions(wallet_address: str, limit: int = 100):
    """Fetch all positions with pagination."""
    offset = 0
    all_positions = []

    while True:
        response = requests.get(f"{DATA_URL}/positions", params={
            "user": wallet_address,
            "limit": limit,
            "offset": offset
        })
        batch = response.json()

        if not batch:
            break

        all_positions.extend(batch)

        if len(batch) < limit:
            break

        offset += limit

    return all_positions
```

## Trade History Analysis

### Calculate Trading Stats

```python
def calculate_trading_stats(wallet_address: str):
    """Calculate comprehensive trading statistics."""
    trades = get_trades_only(wallet_address, limit=1000)

    if not trades:
        print("No trades found")
        return

    buys = [t for t in trades if t.get("side") == "BUY"]
    sells = [t for t in trades if t.get("side") == "SELL"]

    total_bought = sum(t.get("size", 0) * t.get("price", 0) for t in buys)
    total_sold = sum(t.get("size", 0) * t.get("price", 0) for t in sells)

    print(f"Total trades: {len(trades)}")
    print(f"Buy orders: {len(buys)}")
    print(f"Sell orders: {len(sells)}")
    print(f"Total bought: ${total_bought:.2f}")
    print(f"Total sold: ${total_sold:.2f}")

    return {
        "total_trades": len(trades),
        "buys": len(buys),
        "sells": len(sells),
        "total_bought": total_bought,
        "total_sold": total_sold
    }
```

### Export to CSV

```python
import csv
from datetime import datetime

def export_activity_csv(wallet_address: str, filename: str = "activity.csv"):
    """Export complete activity history to CSV."""
    all_activity = list(fetch_all_activity(wallet_address))

    if not all_activity:
        print("No activity to export")
        return

    fieldnames = [
        "timestamp", "type", "title", "outcome", "side",
        "size", "price", "fee", "transactionHash"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for activity in all_activity:
            writer.writerow({
                "timestamp": activity.get("timestamp"),
                "type": activity.get("type"),
                "title": activity.get("title", "")[:100],  # Truncate long titles
                "outcome": activity.get("outcome"),
                "side": activity.get("side"),
                "size": activity.get("size"),
                "price": activity.get("price"),
                "fee": activity.get("fee"),
                "transactionHash": activity.get("transactionHash")
            })

    print(f"Exported {len(all_activity)} records to {filename}")
```

### Activity Timeline

```python
from collections import defaultdict

def activity_by_day(wallet_address: str):
    """Group activity by day for timeline view."""
    all_activity = list(fetch_all_activity(wallet_address))

    by_day = defaultdict(list)
    for activity in all_activity:
        timestamp = activity.get("timestamp", "")
        if timestamp:
            day = timestamp[:10]  # YYYY-MM-DD
            by_day[day].append(activity)

    for day in sorted(by_day.keys(), reverse=True)[:10]:
        activities = by_day[day]
        trades = sum(1 for a in activities if a.get("type") == "TRADE")
        print(f"{day}: {len(activities)} activities ({trades} trades)")

    return dict(by_day)
```

## Error Handling

```python
from requests.exceptions import HTTPError
import time

def safe_get_positions(wallet_address: str, retries: int = 3):
    """Get positions with retry logic."""
    for attempt in range(retries):
        try:
            return get_positions(wallet_address)
        except HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.response.status_code >= 500:
                # Server error - retry
                time.sleep(1)
            else:
                raise

    raise Exception(f"Failed after {retries} retries")
```

## Related Documentation

- [Data API Overview](./data-api-overview.md) - API architecture
- [Historical Prices](./historical-prices.md) - Price timeseries
- [Trading Skill](../trading/) - Place orders
