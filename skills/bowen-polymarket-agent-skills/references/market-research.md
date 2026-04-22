# Market Research Workflows

## Discovering Markets

### List Active Markets

```python
# Get active markets sorted by volume
markets = await client.markets.list_markets(
    active=True,
    order="volume",
    ascending=False,
    limit=100,
)

for market in markets:
    print(f"{market.question}")
    print(f"  Volume: ${market.volume}")
    print(f"  Outcomes: {market.outcomes}")
```

### Search Markets

```python
# Search by keyword
results = await client.markets.search(
    query="election",
    limit_per_type=10,
)

for event in results.events or []:
    print(f"{event.title}")
    for market in event.markets or []:
        print(f"  - {market.question}")
```

### Browse by Category/Tag

```python
# List all tags
tags = await client.markets.list_tags()
for tag in tags:
    print(f"{tag.label} ({tag.slug})")

# Search with tag filter
results = await client.markets.search(
    query="",
    events_tag=["politics"],
)
```

---

## Market Analysis

### Get Market Details

```python
# By condition ID
market = await client.markets.get_market("0xabc123...")

# By URL slug
market = await client.markets.get_market_by_slug("will-x-happen")

print(f"Question: {market.question}")
print(f"End Date: {market.end_date}")
print(f"Resolution Source: {market.resolution_source}")

# Get token info
for token in market.tokens or []:
    print(f"  {token.outcome}: {token.price} (ID: {token.token_id})")
```

### Get Order Book Depth

```python
# Get full order book
book = await client.orderbook.get_book(token_id)

print(f"Bids ({len(book.bids or [])} levels):")
for level in (book.bids or [])[:5]:
    print(f"  {level.price}: {level.size}")

print(f"Asks ({len(book.asks or [])} levels):")
for level in (book.asks or [])[:5]:
    print(f"  {level.price}: {level.size}")

print(f"Tick size: {book.tick_size}")
print(f"Min order: {book.min_order_size}")
```

### Price Analysis

```python
# Current prices
midpoint = await client.orderbook.get_midpoint(token_id)
spread = await client.orderbook.get_spread(token_id)

print(f"Midpoint: {midpoint}")
print(f"Bid: {spread.bid}, Ask: {spread.ask}")
print(f"Spread: {spread.spread}")

# Historical prices
history = await client.orderbook.get_price_history(
    market=token_id,
    interval="1w",
)
```

---

## Event Research

### Get Event with Markets

```python
# Get event with all its markets
event = await client.markets.get_event("event_123")

print(f"Event: {event.title}")
print(f"Volume: ${event.volume}")

for market in event.markets or []:
    print(f"\n  Market: {market.question}")
    for price, outcome in zip(market.outcome_prices or [], market.outcomes or []):
        print(f"    {outcome}: {price}")
```

### Browse Series

```python
# Get recurring event series
series_list = await client.markets.list_series(
    recurrence="weekly",
)

for series in series_list:
    print(f"{series.title}")
    print(f"  Type: {series.series_type}")
    print(f"  Events: {len(series.events or [])}")
```

---

## User Analytics

### Top Holders

```python
# Who holds the most of this outcome?
holders = await client.positions.get_top_holders(
    market="condition_id",
    limit=10,
)

for holder in holders:
    print(f"{holder.pseudonym or holder.user[:8]}: {holder.size} shares")
```

### Market Activity

```python
# Open interest
oi_list = await client.positions.get_open_interest(market="condition_id")
for oi in oi_list:
    print(f"Market {oi.market}: ${oi.value}")

# Live volume (for events)
volume = await client.positions.get_live_volume(event_id=123)
print(f"Total volume: ${volume.total}")
```

### Leaderboard

```python
# Top traders
leaders = await client.positions.get_leaderboard(
    time_period="WEEK",
    limit=10,
)

for entry in leaders:
    print(f"#{entry.rank} {entry.pseudonym}: ${entry.pnl:.2f} P&L")
```

---

## Real-time Monitoring

### Stream Price Updates

```python
async with client.market_stream as stream:
    async for event in stream.subscribe([token_id]):
        if isinstance(event, WsPriceChangeMessage):
            for change in event.price_changes:
                print(f"{change.side}: {change.price} x {change.size}")
```

### Monitor Multiple Markets

```python
# Get tokens for multiple markets
token_ids = []
for market in markets[:5]:
    for token in market.tokens or []:
        token_ids.append(token.token_id)

# Subscribe to all
async with MarketStream(config) as stream:
    async for event in stream.subscribe(token_ids):
        print(f"Update for {event.asset_id}")
```
