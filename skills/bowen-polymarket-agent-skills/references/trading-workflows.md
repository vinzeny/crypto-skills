# Trading Workflows

## Order Lifecycle

### 1. Build and Sign Order

```python
# Using OrderBuilder
order = (
    client.order_builder
    .buy(token_id="71321...", price=0.55, size=100)
    .with_tick_size("0.01")
    .build()
)
```

### 2. Place Order

```python
result = await client.orders.place_order(
    order=order,
    order_type=OrderType.GTC,
    post_only=False,  # True = maker only (rests on book)
)

if result.success:
    print(f"Order ID: {result.order_id}")
    print(f"Status: {result.status}")  # matched/live/delayed/unmatched
```

### 3. Monitor Order

```python
# Get all open orders
orders = await client.orders.get_orders()

# Filter by market
orders = await client.orders.get_orders(market="condition_id")

# Stream updates via WebSocket
async for event in client.user_stream.subscribe(["condition_id"]):
    if isinstance(event, WsOrderMessage):
        if event.type == "UPDATE":
            print(f"Partial fill: {event.size_matched}/{event.original_size}")
```

### 4. Cancel Order

```python
# Cancel single order
result = await client.orders.cancel_order("order_id")

# Cancel multiple
result = await client.orders.cancel_orders(["id1", "id2"])

# Cancel all for a market
result = await client.orders.cancel_market_orders("condition_id")

# Cancel everything
result = await client.orders.cancel_all()
```

---

## Market Order Simulation

Polymarket only supports limit orders, but you can simulate market orders:

```python
# Get current best price
spread = await client.orderbook.get_spread(token_id)

# For immediate execution, use best ask for buys
if side == "BUY":
    price = Decimal(spread.ask) + Decimal("0.01")  # Slightly above ask
else:
    price = Decimal(spread.bid) - Decimal("0.01")  # Slightly below bid

# Use FAK (Fill-And-Kill) for partial fills
order = client.order_builder.buy(token_id, price, size).build()
await client.orders.place_order(order, order_type=OrderType.FAK)
```

---

## Position Management

### Check Position

```python
positions = await client.positions.get_positions(
    user=client.address,
    market="condition_id",
)

for pos in positions:
    print(f"{pos.outcome}: {pos.size} @ {pos.avg_price}")
    print(f"P&L: ${pos.cash_pnl} ({pos.percent_pnl:.1%})")
```

### Close Position

```python
# Get current position
positions = await client.positions.get_positions(user=client.address)
position = positions[0]

# Sell entire position
order = (
    client.order_builder
    .sell(position.asset, price=current_price, size=position.size)
    .build()
)
await client.orders.place_order(order)
```

---

## Risk Patterns

### Check Balance Before Trading

```python
# Check USDC balance
balance = await client.account.get_balance_allowance(
    asset_type="COLLATERAL",
    signature_type=2,  # GNOSIS_SAFE
)

usdc_available = from_wei(int(balance.balance))
print(f"Available: ${usdc_available:.2f}")

# Ensure sufficient balance for order
order_cost = price * size
if order_cost > usdc_available:
    raise InsufficientBalanceError("Not enough USDC")
```

### Validate Token Exists

```python
# Check tick size (validates token exists)
try:
    tick_info = await client.orderbook.get_tick_size(token_id)
    tick_size = tick_info["minimum_tick_size"]
except PolymarketError:
    print("Invalid token ID")
```

### Handle Order Errors

```python
try:
    result = await client.orders.place_order(order)
    if not result.success:
        print(f"Order failed: {result.error_msg}")
except InsufficientBalanceError:
    print("Add more USDC")
except OrderError as e:
    print(f"Order error ({e.error_code}): {e.message}")
```

---

## Negative Risk Markets

Some markets use negative risk (multi-outcome events):

```python
# Check if market uses negative risk
is_neg_risk = await client.orderbook.get_neg_risk(token_id)

# Build order with neg_risk flag
order = (
    client.order_builder
    .buy(token_id, price, size)
    .with_neg_risk(is_neg_risk)
    .build()
)
```

---

## Price History

```python
# Get price history for analysis
history = await client.orderbook.get_price_history(
    market=token_id,
    interval="1d",  # 1m, 1h, 6h, 1d, 1w, max
    fidelity=60,    # Resolution in minutes
)

for point in history.history:
    print(f"{point.t}: {point.p}")
```
