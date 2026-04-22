# Portfolio Export Patterns

Export Polymarket trading data for accounting, tax reporting, and portfolio analysis.

**Covers:** DATA-04 (Portfolio Export)

## Export Use Cases

| Use Case | Purpose | Key Data |
|----------|---------|----------|
| Tax reporting | Capital gains/losses calculation | Trade history, redemptions |
| Portfolio tracking | Performance dashboards | Positions, PnL metrics |
| Trade journal | Strategy analysis | All activity with timestamps |
| Accounting reconciliation | Match records with statements | Complete transaction log |

## Complete Portfolio Export

```python
import requests
import csv
import json
from datetime import datetime

DATA_URL = "https://data-api.polymarket.com"

def export_portfolio(wallet_address: str, output_format: str = "csv"):
    """Export complete portfolio data for accounting.

    Args:
        wallet_address: The Polymarket wallet address
        output_format: "csv" or "json"

    Returns:
        Filename of exported data
    """
    # 1. Fetch all positions
    positions = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address,
        "limit": 1000,
        "sizeThreshold": 0  # Include all positions, even small ones
    }).json()

    # 2. Fetch all activity (paginated)
    activity = []
    offset = 0
    while True:
        batch = requests.get(f"{DATA_URL}/activity", params={
            "user": wallet_address,
            "limit": 100,
            "offset": offset,
            "sortBy": "TIMESTAMP",
            "sortDirection": "ASC"
        }).json()

        if not batch:
            break
        activity.extend(batch)
        if len(batch) < 100:
            break
        offset += 100

    if output_format == "csv":
        return export_trades_csv(activity, wallet_address)
    else:
        return export_to_json(positions, activity, wallet_address)
```

## CSV Export for Trades

Export trade history in a format compatible with accounting software.

```python
def export_trades_csv(activity: list, wallet_address: str):
    """Export trade history to CSV for accounting software.

    Creates a file with standardized columns for tax software import.
    """
    fieldnames = [
        "date", "time", "type", "market_title", "outcome",
        "side", "quantity", "price", "total", "fee", "tx_hash"
    ]

    filename = f"polymarket_trades_{wallet_address[:8]}_{datetime.now().strftime('%Y%m%d')}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for trade in activity:
            if trade["type"] != "TRADE":
                continue

            # Parse ISO timestamp
            dt = datetime.fromisoformat(trade["timestamp"].replace("Z", "+00:00"))

            row = {
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "type": trade["type"],
                "market_title": trade.get("title", "")[:100],  # Truncate long titles
                "outcome": trade.get("outcome", ""),
                "side": trade["side"],
                "quantity": trade["size"],
                "price": trade["price"],
                "total": float(trade["size"]) * float(trade["price"]),
                "fee": trade.get("fee", 0),
                "tx_hash": trade.get("transactionHash", "")
            }
            writer.writerow(row)

    return filename
```

### CSV Output Format

The exported CSV uses accounting-standard formatting:

| Column | Format | Example |
|--------|--------|---------|
| date | YYYY-MM-DD (ISO 8601) | 2024-01-15 |
| time | HH:MM:SS (UTC) | 10:30:45 |
| type | String | TRADE |
| market_title | String (truncated) | Will candidate X win... |
| outcome | Yes/No | Yes |
| side | BUY/SELL | BUY |
| quantity | Decimal | 100.5 |
| price | Decimal (0-1) | 0.45 |
| total | Decimal (USD) | 45.225 |
| fee | Decimal (USD) | 0.0 |
| tx_hash | Hex string | 0xabc123... |

## Position Summary Export

Export current positions with PnL calculations.

```python
def export_positions_summary(positions: list, wallet_address: str):
    """Export current positions with PnL summary.

    Useful for portfolio snapshots and performance tracking.
    """
    fieldnames = [
        "market", "outcome", "shares", "avg_price", "current_price",
        "initial_value", "current_value", "unrealized_pnl", "pnl_percent",
        "end_date", "status"
    ]

    filename = f"polymarket_positions_{wallet_address[:8]}_{datetime.now().strftime('%Y%m%d')}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for pos in positions:
            status = "closed" if pos.get("closed", False) else "open"
            if pos.get("redeemed", False):
                status = "redeemed"

            row = {
                "market": pos.get("title", "")[:100],
                "outcome": pos.get("outcome", ""),
                "shares": pos["size"],
                "avg_price": pos["avgPrice"],
                "current_price": pos["curPrice"],
                "initial_value": pos["initialValue"],
                "current_value": pos["currentValue"],
                "unrealized_pnl": pos["cashPnl"],
                "pnl_percent": pos["percentPnl"],
                "end_date": pos.get("endDate", ""),
                "status": status
            }
            writer.writerow(row)

    return filename
```

## PnL Aggregation

Calculate aggregate profit and loss metrics for portfolio analysis.

```python
def calculate_pnl_summary(positions: list, activity: list):
    """Calculate aggregate PnL metrics.

    Returns comprehensive portfolio statistics.
    """
    # Unrealized PnL (open positions)
    unrealized_pnl = sum(float(p["cashPnl"]) for p in positions)
    total_position_value = sum(float(p["currentValue"]) for p in positions)
    total_initial_value = sum(float(p["initialValue"]) for p in positions)

    # Realized PnL (from redemptions)
    redemptions = [a for a in activity if a["type"] == "REDEEM"]
    realized_pnl = sum(float(r.get("amount", 0)) for r in redemptions)

    # Trade volume and counts
    trades = [a for a in activity if a["type"] == "TRADE"]
    total_volume = sum(
        float(t["size"]) * float(t["price"])
        for t in trades
    )

    buy_volume = sum(
        float(t["size"]) * float(t["price"])
        for t in trades if t["side"] == "BUY"
    )

    sell_volume = sum(
        float(t["size"]) * float(t["price"])
        for t in trades if t["side"] == "SELL"
    )

    return {
        "unrealized_pnl": unrealized_pnl,
        "realized_pnl": realized_pnl,
        "total_pnl": unrealized_pnl + realized_pnl,
        "total_position_value": total_position_value,
        "total_initial_value": total_initial_value,
        "total_trade_volume": total_volume,
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
        "total_trades": len(trades),
        "total_redemptions": len(redemptions),
        "open_positions": len([p for p in positions if not p.get("closed", False)]),
        "closed_positions": len([p for p in positions if p.get("closed", False)])
    }


def print_pnl_report(wallet_address: str):
    """Print formatted PnL report to console."""
    positions = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address,
        "limit": 1000
    }).json()

    activity = []
    offset = 0
    while True:
        batch = requests.get(f"{DATA_URL}/activity", params={
            "user": wallet_address,
            "limit": 100,
            "offset": offset
        }).json()
        if not batch:
            break
        activity.extend(batch)
        if len(batch) < 100:
            break
        offset += 100

    summary = calculate_pnl_summary(positions, activity)

    print("=" * 50)
    print("POLYMARKET PORTFOLIO SUMMARY")
    print("=" * 50)
    print(f"Open positions:      {summary['open_positions']}")
    print(f"Closed positions:    {summary['closed_positions']}")
    print(f"Total trades:        {summary['total_trades']}")
    print("-" * 50)
    print(f"Unrealized PnL:      ${summary['unrealized_pnl']:+.2f}")
    print(f"Realized PnL:        ${summary['realized_pnl']:+.2f}")
    print(f"Total PnL:           ${summary['total_pnl']:+.2f}")
    print("-" * 50)
    print(f"Portfolio value:     ${summary['total_position_value']:.2f}")
    print(f"Total invested:      ${summary['total_initial_value']:.2f}")
    print(f"Total volume:        ${summary['total_trade_volume']:.2f}")
    print("=" * 50)

    return summary
```

## JSON Export for Analysis

Export complete portfolio data as structured JSON for programmatic analysis.

```python
def export_to_json(positions: list, activity: list, wallet_address: str):
    """Export complete portfolio data as JSON.

    Includes positions, activity, and computed summary metrics.
    """
    summary = calculate_pnl_summary(positions, activity)

    export_data = {
        "metadata": {
            "wallet": wallet_address,
            "export_date": datetime.utcnow().isoformat() + "Z",
            "export_version": "1.0"
        },
        "summary": summary,
        "positions": positions,
        "activity": activity
    }

    filename = f"polymarket_portfolio_{wallet_address[:8]}_{datetime.now().strftime('%Y%m%d')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)

    return filename
```

### JSON Schema

```json
{
  "metadata": {
    "wallet": "0x1234...",
    "export_date": "2024-01-15T10:30:00Z",
    "export_version": "1.0"
  },
  "summary": {
    "unrealized_pnl": 150.50,
    "realized_pnl": 200.00,
    "total_pnl": 350.50,
    "total_position_value": 1500.00,
    "open_positions": 12,
    "total_trades": 45
  },
  "positions": [...],
  "activity": [...]
}
```

## Tax Lot Tracking

Calculate cost basis using FIFO (First-In-First-Out) method for tax reporting.

```python
def calculate_tax_lots(activity: list):
    """Calculate cost basis using FIFO method.

    Tracks individual lots for accurate capital gains calculation.

    Returns:
        Dictionary mapping token IDs to remaining lots
    """
    lots = {}  # token_id -> list of {quantity, price, date}
    realized_gains = []

    # Process trades chronologically
    for trade in sorted(activity, key=lambda x: x["timestamp"]):
        if trade["type"] != "TRADE":
            continue

        token = trade["asset"]
        if token not in lots:
            lots[token] = []

        if trade["side"] == "BUY":
            # Add new lot
            lots[token].append({
                "quantity": float(trade["size"]),
                "price": float(trade["price"]),
                "date": trade["timestamp"],
                "tx_hash": trade.get("transactionHash", "")
            })

        else:  # SELL
            # Match against oldest lots (FIFO)
            sell_qty = float(trade["size"])
            sell_price = float(trade["price"])
            sell_date = trade["timestamp"]

            while sell_qty > 0 and lots[token]:
                lot = lots[token][0]
                matched = min(lot["quantity"], sell_qty)

                # Calculate gain/loss for this lot
                cost_basis = matched * lot["price"]
                proceeds = matched * sell_price
                gain = proceeds - cost_basis

                # Determine holding period
                buy_date = datetime.fromisoformat(lot["date"].replace("Z", "+00:00"))
                sell_dt = datetime.fromisoformat(sell_date.replace("Z", "+00:00"))
                holding_days = (sell_dt - buy_date).days

                realized_gains.append({
                    "token": token,
                    "quantity": matched,
                    "cost_basis": cost_basis,
                    "proceeds": proceeds,
                    "gain": gain,
                    "buy_date": lot["date"],
                    "sell_date": sell_date,
                    "holding_days": holding_days,
                    "term": "long" if holding_days > 365 else "short"
                })

                # Update lot
                lot["quantity"] -= matched
                sell_qty -= matched

                if lot["quantity"] <= 0:
                    lots[token].pop(0)

    return {
        "remaining_lots": lots,
        "realized_gains": realized_gains
    }


def export_tax_report(wallet_address: str, tax_year: int):
    """Export tax report for a specific year.

    Generates capital gains report suitable for tax filing.
    """
    # Fetch all activity
    activity = []
    offset = 0
    while True:
        batch = requests.get(f"{DATA_URL}/activity", params={
            "user": wallet_address,
            "limit": 100,
            "offset": offset,
            "sortBy": "TIMESTAMP",
            "sortDirection": "ASC"
        }).json()
        if not batch:
            break
        activity.extend(batch)
        if len(batch) < 100:
            break
        offset += 100

    # Calculate tax lots
    tax_data = calculate_tax_lots(activity)

    # Filter to tax year
    year_start = f"{tax_year}-01-01"
    year_end = f"{tax_year}-12-31"

    year_gains = [
        g for g in tax_data["realized_gains"]
        if year_start <= g["sell_date"][:10] <= year_end
    ]

    # Calculate totals
    short_term = sum(g["gain"] for g in year_gains if g["term"] == "short")
    long_term = sum(g["gain"] for g in year_gains if g["term"] == "long")

    # Export to CSV
    filename = f"polymarket_tax_{tax_year}_{wallet_address[:8]}.csv"

    fieldnames = [
        "description", "buy_date", "sell_date", "holding_days",
        "quantity", "cost_basis", "proceeds", "gain_loss", "term"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for gain in year_gains:
            writer.writerow({
                "description": f"Polymarket Token {gain['token'][:16]}...",
                "buy_date": gain["buy_date"][:10],
                "sell_date": gain["sell_date"][:10],
                "holding_days": gain["holding_days"],
                "quantity": gain["quantity"],
                "cost_basis": f"{gain['cost_basis']:.2f}",
                "proceeds": f"{gain['proceeds']:.2f}",
                "gain_loss": f"{gain['gain']:.2f}",
                "term": gain["term"]
            })

    print(f"Tax Report for {tax_year}")
    print(f"Short-term gains/losses: ${short_term:+.2f}")
    print(f"Long-term gains/losses: ${long_term:+.2f}")
    print(f"Total: ${short_term + long_term:+.2f}")
    print(f"Exported to: {filename}")

    return filename
```

## Date Range Filtering

Export activity within a specific date range for quarterly or annual reporting.

```python
def export_date_range(wallet_address: str, start_date: str, end_date: str):
    """Export activity within a specific date range.

    Args:
        wallet_address: Wallet to query
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Filtered activity list
    """
    # Fetch all activity
    activity = []
    offset = 0
    while True:
        batch = requests.get(f"{DATA_URL}/activity", params={
            "user": wallet_address,
            "limit": 100,
            "offset": offset,
            "sortBy": "TIMESTAMP",
            "sortDirection": "ASC"
        }).json()
        if not batch:
            break
        activity.extend(batch)
        if len(batch) < 100:
            break
        offset += 100

    # Filter to date range
    filtered = []
    for a in activity:
        activity_date = a["timestamp"][:10]  # YYYY-MM-DD
        if start_date <= activity_date <= end_date:
            filtered.append(a)

    return filtered


def export_quarter(wallet_address: str, year: int, quarter: int):
    """Export activity for a specific quarter.

    Args:
        wallet_address: Wallet to query
        year: Year (e.g., 2024)
        quarter: Quarter number (1-4)

    Returns:
        Filename of exported CSV
    """
    quarter_dates = {
        1: ("01-01", "03-31"),
        2: ("04-01", "06-30"),
        3: ("07-01", "09-30"),
        4: ("10-01", "12-31")
    }

    start, end = quarter_dates[quarter]
    start_date = f"{year}-{start}"
    end_date = f"{year}-{end}"

    activity = export_date_range(wallet_address, start_date, end_date)

    # Export to CSV
    filename = f"polymarket_Q{quarter}_{year}_{wallet_address[:8]}.csv"

    fieldnames = [
        "date", "type", "market", "outcome", "side",
        "quantity", "price", "total", "tx_hash"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for a in activity:
            if a["type"] == "TRADE":
                writer.writerow({
                    "date": a["timestamp"][:10],
                    "type": a["type"],
                    "market": a.get("title", "")[:80],
                    "outcome": a.get("outcome", ""),
                    "side": a["side"],
                    "quantity": a["size"],
                    "price": a["price"],
                    "total": float(a["size"]) * float(a["price"]),
                    "tx_hash": a.get("transactionHash", "")
                })

    print(f"Exported Q{quarter} {year}: {len(activity)} activities to {filename}")
    return filename
```

## Accounting Software Compatibility

### Format Specifications

The export functions produce files compatible with common accounting software:

| Software | Supported Format | Date Format | Notes |
|----------|------------------|-------------|-------|
| QuickBooks | CSV | YYYY-MM-DD | Import as bank transactions |
| TurboTax | CSV | MM/DD/YYYY | Use tax lot export |
| Koinly | JSON | ISO 8601 | Full portfolio export |
| CoinTracker | CSV | YYYY-MM-DD | Trade history export |

### Custom Format Conversion

```python
def convert_to_turbotax_format(input_file: str, output_file: str):
    """Convert standard CSV to TurboTax-compatible format."""
    import csv

    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_file, "w", newline="", encoding="utf-8") as outfile:
            fieldnames = [
                "Date Acquired", "Date Sold", "Description",
                "Cost Basis", "Proceeds", "Gain/Loss"
            ]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                # Convert date format from YYYY-MM-DD to MM/DD/YYYY
                buy_parts = row["buy_date"].split("-")
                sell_parts = row["sell_date"].split("-")

                writer.writerow({
                    "Date Acquired": f"{buy_parts[1]}/{buy_parts[2]}/{buy_parts[0]}",
                    "Date Sold": f"{sell_parts[1]}/{sell_parts[2]}/{sell_parts[0]}",
                    "Description": row["description"],
                    "Cost Basis": row["cost_basis"],
                    "Proceeds": row["proceeds"],
                    "Gain/Loss": row["gain_loss"]
                })
```

## Complete Export Workflow

End-to-end example for annual tax preparation.

```python
def annual_tax_prep(wallet_address: str, tax_year: int):
    """Complete annual tax preparation workflow.

    Generates all files needed for tax filing.
    """
    print(f"Preparing {tax_year} tax documents for {wallet_address[:10]}...")

    # 1. Export full portfolio snapshot
    positions = requests.get(f"{DATA_URL}/positions", params={
        "user": wallet_address,
        "limit": 1000
    }).json()

    positions_file = export_positions_summary(positions, wallet_address)
    print(f"Positions snapshot: {positions_file}")

    # 2. Generate tax lot report
    tax_file = export_tax_report(wallet_address, tax_year)
    print(f"Tax lot report: {tax_file}")

    # 3. Export quarterly breakdowns
    for q in range(1, 5):
        q_file = export_quarter(wallet_address, tax_year, q)
        print(f"Q{q} activity: {q_file}")

    # 4. Generate JSON backup
    activity = []
    offset = 0
    while True:
        batch = requests.get(f"{DATA_URL}/activity", params={
            "user": wallet_address,
            "limit": 100,
            "offset": offset
        }).json()
        if not batch:
            break
        activity.extend(batch)
        if len(batch) < 100:
            break
        offset += 100

    json_file = export_to_json(positions, activity, wallet_address)
    print(f"Full backup: {json_file}")

    print("\nTax preparation complete!")
    return {
        "positions": positions_file,
        "tax_lots": tax_file,
        "quarterly": [f"Q{q}_{tax_year}" for q in range(1, 5)],
        "backup": json_file
    }
```

## Related Documentation

- [Positions and History](./positions-and-history.md) - Position and activity data sources
- [Historical Prices](./historical-prices.md) - Price data for cost basis
- [Data API Overview](./data-api-overview.md) - API architecture
