# Historical Prices

This document covers accessing historical price data for Polymarket tokens.

**Covers:** DATA-03 (Historical Prices)

**Note:** Historical prices are retrieved via the CLOB API, not the Data API.

## Prices History Endpoint

```python
import requests

CLOB_URL = "https://clob.polymarket.com"

def get_price_history(token_id: str, interval: str = "1d"):
    """Get historical price data for a token.

    Args:
        token_id: The outcome token ID (from market data)
        interval: Time interval (1m, 1h, 6h, 1d, 1w, max)

    Returns:
        Dict with "history" array of price points
    """
    response = requests.get(f"{CLOB_URL}/prices-history", params={
        "market": token_id,
        "interval": interval
    })
    response.raise_for_status()
    return response.json()
```

## Interval Options

| Interval | Description | Use Case |
|----------|-------------|----------|
| `1m` | 1 minute candles | Real-time trading, scalping |
| `1h` | 1 hour candles | Intraday analysis |
| `6h` | 6 hour candles | Multi-day trend analysis |
| `1d` | 1 day candles | Long-term charts |
| `1w` | 1 week candles | Historical overview |
| `max` | All available data points | Complete price history |

### Choosing the Right Interval

```python
def get_appropriate_interval(days_back: int) -> str:
    """Select interval based on desired history length."""
    if days_back <= 1:
        return "1m"  # Minute data for last 24h
    elif days_back <= 7:
        return "1h"  # Hourly for last week
    elif days_back <= 30:
        return "6h"  # 6-hour for last month
    elif days_back <= 90:
        return "1d"  # Daily for last quarter
    else:
        return "1w"  # Weekly for longer periods
```

## Response Schema

```python
{
    "history": [
        {
            "t": 1705320000,  # Unix timestamp (seconds)
            "p": "0.45"      # Price at that time (string)
        },
        {
            "t": 1705406400,
            "p": "0.48"
        },
        {
            "t": 1705492800,
            "p": "0.52"
        }
    ]
}
```

**Fields:**
- `t`: Unix timestamp in seconds
- `p`: Price as a string (convert to float for calculations)

## Converting to DataFrame

For analysis, convert the response to a pandas DataFrame.

```python
import pandas as pd
from datetime import datetime

def prices_to_dataframe(price_history: dict) -> pd.DataFrame:
    """Convert price history response to pandas DataFrame.

    Args:
        price_history: Response from get_price_history()

    Returns:
        DataFrame with timestamp index and price column
    """
    if not price_history.get("history"):
        return pd.DataFrame(columns=["price"])

    df = pd.DataFrame(price_history["history"])

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["t"], unit="s")

    # Convert price string to float
    df["price"] = df["p"].astype(float)

    # Drop original columns
    df = df.drop(columns=["t", "p"])

    # Set timestamp as index
    return df.set_index("timestamp")


# Usage example
history = get_price_history(token_id, "1d")
df = prices_to_dataframe(history)

print(df.head())
#                      price
# timestamp
# 2024-01-15 00:00:00   0.45
# 2024-01-16 00:00:00   0.48
# 2024-01-17 00:00:00   0.52

print(df.tail())
print(f"Date range: {df.index.min()} to {df.index.max()}")
print(f"Price range: {df['price'].min():.2f} to {df['price'].max():.2f}")
```

## Charting Examples

### Basic Price Chart

```python
import matplotlib.pyplot as plt

def plot_price_history(token_id: str, title: str = "Price History"):
    """Create a basic price chart."""
    history = get_price_history(token_id, "1d")
    df = prices_to_dataframe(history)

    if df.empty:
        print("No price data available")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["price"], linewidth=2)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)  # Prediction market prices are 0-1
    plt.tight_layout()
    plt.show()
```

### Price Chart with Moving Average

```python
def plot_with_moving_average(token_id: str, window: int = 7):
    """Price chart with moving average overlay."""
    history = get_price_history(token_id, "1d")
    df = prices_to_dataframe(history)

    if df.empty or len(df) < window:
        print("Insufficient price data")
        return

    df["ma"] = df["price"].rolling(window=window).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["price"], label="Price", alpha=0.7)
    plt.plot(df.index, df["ma"], label=f"{window}-day MA", linewidth=2)
    plt.title("Price with Moving Average")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.show()
```

### Volatility Chart

```python
def plot_volatility(token_id: str, window: int = 7):
    """Plot rolling volatility (standard deviation)."""
    history = get_price_history(token_id, "1d")
    df = prices_to_dataframe(history)

    if df.empty or len(df) < window:
        print("Insufficient data")
        return

    df["returns"] = df["price"].pct_change()
    df["volatility"] = df["returns"].rolling(window=window).std()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(df.index, df["price"])
    ax1.set_ylabel("Price")
    ax1.set_title("Price and Volatility")
    ax1.grid(True, alpha=0.3)

    ax2.fill_between(df.index, 0, df["volatility"], alpha=0.5)
    ax2.set_ylabel(f"{window}-day Volatility")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
```

## Multi-Market Comparison

Compare price movements across related markets.

```python
def compare_markets(token_ids: dict, interval: str = "1d"):
    """Fetch and align price history for multiple markets.

    Args:
        token_ids: Dict of {label: token_id}
        interval: Time interval for all markets

    Returns:
        DataFrame with aligned prices
    """
    dataframes = {}

    for label, token_id in token_ids.items():
        history = get_price_history(token_id, interval)
        df = prices_to_dataframe(history)
        dataframes[label] = df["price"]

    # Combine into single DataFrame
    combined = pd.concat(dataframes, axis=1)
    return combined


def plot_comparison(token_ids: dict, title: str = "Market Comparison"):
    """Plot multiple markets on same chart."""
    df = compare_markets(token_ids)

    plt.figure(figsize=(12, 6))

    for column in df.columns:
        plt.plot(df.index, df[column], label=column, linewidth=2)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.show()


# Example usage
# markets = {
#     "Candidate A": "token_id_a",
#     "Candidate B": "token_id_b",
#     "Candidate C": "token_id_c"
# }
# plot_comparison(markets, "Election Odds")
```

## Price Analytics

### Calculate Price Statistics

```python
def price_statistics(token_id: str, interval: str = "1d"):
    """Calculate comprehensive price statistics."""
    history = get_price_history(token_id, interval)
    df = prices_to_dataframe(history)

    if df.empty:
        return None

    stats = {
        "current": df["price"].iloc[-1],
        "high": df["price"].max(),
        "low": df["price"].min(),
        "mean": df["price"].mean(),
        "std": df["price"].std(),
        "start": df["price"].iloc[0],
        "change": df["price"].iloc[-1] - df["price"].iloc[0],
        "change_pct": (df["price"].iloc[-1] / df["price"].iloc[0] - 1) * 100,
        "data_points": len(df)
    }

    print(f"Current: {stats['current']:.2f}")
    print(f"High: {stats['high']:.2f}")
    print(f"Low: {stats['low']:.2f}")
    print(f"Mean: {stats['mean']:.2f}")
    print(f"Std Dev: {stats['std']:.4f}")
    print(f"Change: {stats['change']:+.2f} ({stats['change_pct']:+.1f}%)")

    return stats
```

### Detect Price Movements

```python
def detect_significant_moves(token_id: str, threshold: float = 0.05):
    """Find days with significant price movements.

    Args:
        token_id: Token to analyze
        threshold: Minimum price change to flag (e.g., 0.05 = 5%)
    """
    history = get_price_history(token_id, "1d")
    df = prices_to_dataframe(history)

    if df.empty:
        return []

    df["change"] = df["price"].diff()
    df["pct_change"] = df["price"].pct_change()

    significant = df[abs(df["pct_change"]) >= threshold].copy()

    moves = []
    for idx, row in significant.iterrows():
        moves.append({
            "date": idx,
            "price": row["price"],
            "change": row["change"],
            "pct_change": row["pct_change"] * 100
        })

    for move in moves:
        direction = "UP" if move["change"] > 0 else "DOWN"
        print(f"{move['date'].date()}: {direction} {abs(move['pct_change']):.1f}% to {move['price']:.2f}")

    return moves
```

## Data Availability Notes

- **History starts from market creation** - Older markets have more data
- **Max interval returns all data** - Use for complete history
- **No authentication required** - Public endpoint
- **Data freshness** - May have short delay from live prices

## Rate Limiting

Implement delays when fetching multiple markets.

```python
import time

def batch_price_history(token_ids: list, interval: str = "1d", delay: float = 0.3):
    """Fetch price history for multiple tokens with rate limiting."""
    results = {}

    for i, token_id in enumerate(token_ids):
        try:
            results[token_id] = get_price_history(token_id, interval)
            print(f"Fetched {i+1}/{len(token_ids)}")
        except Exception as e:
            print(f"Error fetching {token_id}: {e}")
            results[token_id] = None

        if i < len(token_ids) - 1:
            time.sleep(delay)

    return results
```

## Limitations

1. **Rate limits apply** - Add delays between requests
2. **Intervals are fixed** - Cannot request custom intervals
3. **Gaps possible** - Low-activity periods may have missing data
4. **Real-time needs WebSocket** - For live updates, use WebSocket feed
5. **Price is mid-market** - Not bid/ask, but indicative price

## Related Documentation

- [Data API Overview](./data-api-overview.md) - API architecture
- [Positions and History](./positions-and-history.md) - Portfolio data
- [Trading Skill](../trading/) - Order placement
- [Market Discovery](../market-discovery/) - Find markets to track
