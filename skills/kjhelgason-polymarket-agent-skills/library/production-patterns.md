# Production Usage Patterns

Production-ready patterns for rate limiting, WebSocket reliability, and balance tracking.

**Covers:** LIB-02 (Common method signatures), LIB-04 (Production best practices)

## Rate Limiting

Polymarket enforces rate limits via Cloudflare throttling. Requests over the limit are QUEUED, not dropped. However, excessive queuing causes latency and potential timeouts.

### Rate Limits Reference

```python
RATE_LIMITS = {
    # General endpoints
    "general": {"per_10s": 15000},
    "health_check": {"per_10s": 100},

    # Data API
    "data_general": {"per_10s": 1000},
    "data_trades": {"per_10s": 200},
    "data_positions": {"per_10s": 150},

    # Gamma API
    "gamma_general": {"per_10s": 4000},
    "gamma_markets": {"per_10s": 300},  # up to 900 depending on operation
    "gamma_search": {"per_10s": 200},

    # CLOB API (trading)
    "clob_general": {"per_10s": 9000},
    "clob_book": {"per_10s": 1500},
    "clob_price": {"per_10s": 1500},

    # Trading operations - DUAL LIMITS (burst + sustained)
    "order_post": {
        "burst": {"per_10s": 3500, "per_second": 500},
        "sustained": {"per_10min": 36000, "per_second": 60}
    },
    "order_delete": {
        "burst": {"per_10s": 3000, "per_second": 300},
        "sustained": {"per_10min": 30000, "per_second": 50}
    },
    "batch_operations": {
        "burst": {"per_10s": 1000},
        "sustained": {"per_10min": 15000}
    },

    # Other
    "relayer_submit": {"per_1min": 25},

    # Batch size limit
    "batch_max_orders": 15  # Maximum orders per batch request
}
```

### Understanding Burst vs Sustained Limits

| Limit Type | Purpose | Example |
|------------|---------|---------|
| **Burst** | Short-term peak (10 seconds) | 3,500 orders in 10s = 350/s peak |
| **Sustained** | Long-term average (10 minutes) | 36,000 orders in 10min = 60/s average |

You can burst to 350 orders/second briefly, but must average 60/second over 10 minutes.

### RateLimiter Class

```python
import time
from threading import Lock
from collections import deque

class RateLimiter:
    """Rate limiter respecting Polymarket API limits.

    Implements sliding window rate limiting for burst + sustained limits.

    Usage:
        limiter = RateLimiter(max_calls=350, window_seconds=1)
        for order in orders:
            limiter.wait_if_needed()
            client.post_order(order)
    """

    def __init__(self, max_calls: int, window_seconds: float):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed in window
            window_seconds: Time window in seconds
        """
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = deque()
        self.lock = Lock()

    def wait_if_needed(self):
        """Block until call is allowed within rate limit."""
        with self.lock:
            now = time.time()

            # Remove old calls outside window
            while self.calls and self.calls[0] < now - self.window_seconds:
                self.calls.popleft()

            # Wait if at limit
            if len(self.calls) >= self.max_calls:
                sleep_time = self.calls[0] + self.window_seconds - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.calls.popleft()

            self.calls.append(time.time())

    def can_proceed(self) -> bool:
        """Check if a call can proceed without waiting.

        Returns:
            True if call would not block, False if rate limited
        """
        with self.lock:
            now = time.time()

            # Remove old calls outside window
            while self.calls and self.calls[0] < now - self.window_seconds:
                self.calls.popleft()

            return len(self.calls) < self.max_calls
```

### Recommended Limiter Configurations

```python
# Conservative limiters for production
# Stay under burst limits to avoid queuing

# Order placement: 350/s (10% buffer from 3500/10s burst)
order_limiter = RateLimiter(max_calls=350, window_seconds=1)

# Order cancellation: 300/s (from 3000/10s burst)
cancel_limiter = RateLimiter(max_calls=300, window_seconds=1)

# Batch operations: 100/s (from 1000/10s burst)
batch_limiter = RateLimiter(max_calls=100, window_seconds=1)

# General CLOB: 900/s (from 9000/10s)
clob_limiter = RateLimiter(max_calls=900, window_seconds=1)

# Price/book queries: 150/s (from 1500/10s)
price_limiter = RateLimiter(max_calls=150, window_seconds=1)
```

### High-Frequency Trading Setup

```python
class TradingRateLimits:
    """Coordinated rate limiters for trading operations."""

    def __init__(self, conservative: bool = True):
        """Initialize trading rate limiters.

        Args:
            conservative: If True, use 80% of limits for safety margin
        """
        factor = 0.8 if conservative else 1.0

        self.order = RateLimiter(
            max_calls=int(350 * factor),
            window_seconds=1
        )
        self.cancel = RateLimiter(
            max_calls=int(300 * factor),
            window_seconds=1
        )
        self.batch = RateLimiter(
            max_calls=int(100 * factor),
            window_seconds=1
        )
        self.price = RateLimiter(
            max_calls=int(150 * factor),
            window_seconds=1
        )

    def place_order(self, client, signed_order, order_type):
        """Place order respecting rate limits."""
        self.order.wait_if_needed()
        return client.post_order(signed_order, order_type)

    def cancel_order(self, client, order_id):
        """Cancel order respecting rate limits."""
        self.cancel.wait_if_needed()
        return client.cancel(order_id)

    def get_price(self, client, token_id, side):
        """Get price respecting rate limits."""
        self.price.wait_if_needed()
        return client.get_price(token_id, side)
```

## WebSocket Reconnection

For production WebSocket connections, see [Connection Management](../real-time/connection-management.md) for complete patterns.

### Key Reliability Parameters

| Parameter | Recommended Value | Purpose |
|-----------|-------------------|---------|
| Heartbeat interval | 5 seconds | Keep connection alive |
| Data timeout | 300 seconds (5 min) | Detect stale connections |
| Base reconnect delay | 1 second | Initial backoff |
| Max reconnect delay | 60 seconds | Maximum backoff |

### When to Use Which Timeout

| Use Case | Heartbeat | Data Timeout | Reconnect Delay |
|----------|-----------|--------------|-----------------|
| High-frequency trading | 5s | 60s | 1s base |
| Dashboard monitoring | 5s | 300s | 1s base |
| Low-activity markets | 5s | 900s | 5s base |
| Batch order monitoring | 5s | 120s | 1s base |

### Minimal Reconnection Pattern

```python
import asyncio
import websockets
import json
import random

async def robust_connect(url: str, subscribe_msg: dict, callback):
    """Connect with automatic reconnection.

    Features:
    - Exponential backoff (1s -> 60s)
    - Jitter to prevent thundering herd
    - Subscription restoration
    """
    base_delay = 1
    max_delay = 60
    delay = base_delay

    while True:
        try:
            async with websockets.connect(url) as ws:
                delay = base_delay  # Reset on success

                # Subscribe
                await ws.send(json.dumps(subscribe_msg))

                # Process messages
                async for message in ws:
                    data = json.loads(message)
                    await callback(data)

        except websockets.ConnectionClosed:
            pass  # Normal disconnect, reconnect

        except Exception as e:
            print(f"Connection error: {e}")

        # Exponential backoff with jitter
        jitter = random.uniform(0, 1)
        await asyncio.sleep(delay + jitter)
        delay = min(delay * 2, max_delay)
```

For full implementation with heartbeat, timeout detection, and metrics, see [Connection Management](../real-time/connection-management.md).

## Balance Tracking

Track USDC.e balance changes for position reconciliation.

### On-Chain Balance Check

```python
from web3 import Web3

# USDC.e on Polygon - the ONLY token Polymarket accepts
USDC_E_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
USDC_E_DECIMALS = 6

# Minimal ERC-20 ABI for balance check
ERC20_BALANCE_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

def get_usdc_e_balance(wallet_address: str, rpc_url: str = "https://polygon-rpc.com") -> float:
    """Get current USDC.e balance on-chain.

    Args:
        wallet_address: Wallet to check
        rpc_url: Polygon RPC endpoint

    Returns:
        Balance in USDC (float, 2 decimal precision)
    """
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    # Create contract instance
    usdc_contract = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_E_ADDRESS),
        abi=ERC20_BALANCE_ABI
    )

    # Get raw balance (in smallest units)
    raw_balance = usdc_contract.functions.balanceOf(
        Web3.to_checksum_address(wallet_address)
    ).call()

    # Convert to human-readable (6 decimals)
    return raw_balance / (10 ** USDC_E_DECIMALS)
```

### BalanceTracker Class

```python
import time
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class BalanceChange:
    """Record of a balance change."""
    timestamp: float
    balance: float
    change: float
    reason: Optional[str] = None

@dataclass
class BalanceTracker:
    """Track balance changes for reconciliation.

    Usage:
        tracker = BalanceTracker("0x...")
        tracker.update()  # Initial snapshot

        # After placing order
        tracker.update(reason="Placed order for 100 shares @ 0.45")

        # View history
        for change in tracker.history:
            print(f"{change.change:+.2f} - {change.reason}")
    """
    wallet_address: str
    rpc_url: str = "https://polygon-rpc.com"
    last_balance: Optional[float] = None
    history: List[BalanceChange] = field(default_factory=list)

    def update(self, reason: Optional[str] = None) -> float:
        """Record current balance and track change.

        Args:
            reason: Optional reason for expected change

        Returns:
            Current balance
        """
        current = get_usdc_e_balance(self.wallet_address, self.rpc_url)

        if self.last_balance is not None:
            change = current - self.last_balance
            self.history.append(BalanceChange(
                timestamp=time.time(),
                balance=current,
                change=change,
                reason=reason
            ))

        self.last_balance = current
        return current

    def get_net_change(self) -> float:
        """Get total balance change since tracking started."""
        if not self.history:
            return 0.0
        return sum(h.change for h in self.history)

    def get_recent_changes(self, count: int = 10) -> List[BalanceChange]:
        """Get most recent balance changes."""
        return self.history[-count:]

    def reconcile(self, expected_change: float, tolerance: float = 0.01) -> dict:
        """Check if actual change matches expected.

        Args:
            expected_change: Expected balance change
            tolerance: Acceptable difference (default: 1 cent)

        Returns:
            Dict with match status and discrepancy
        """
        if not self.history:
            return {"match": False, "error": "No history"}

        actual_change = self.history[-1].change
        discrepancy = abs(actual_change - expected_change)

        return {
            "match": discrepancy <= tolerance,
            "expected": expected_change,
            "actual": actual_change,
            "discrepancy": discrepancy
        }
```

### Reconciliation Example

```python
def trade_with_reconciliation(client, tracker, order_args, order_type):
    """Place trade with balance reconciliation.

    Tracks expected vs actual balance change.
    """
    # Snapshot before
    before = tracker.update(reason="Pre-trade snapshot")

    # Calculate expected cost
    expected_cost = order_args.size * order_args.price

    # Place order
    try:
        signed = client.create_order(order_args)
        response = client.post_order(signed, order_type)

        # Wait for settlement (short delay for on-chain)
        time.sleep(2)

        # Snapshot after
        after = tracker.update(reason=f"Order {response.get('orderID', 'unknown')}")

        # Reconcile
        result = tracker.reconcile(
            expected_change=-expected_cost,  # Negative for buy
            tolerance=0.05  # 5 cent tolerance for fees
        )

        if not result["match"]:
            print(f"Warning: Balance discrepancy of ${result['discrepancy']:.2f}")

        return {
            "order": response,
            "balance_before": before,
            "balance_after": after,
            "reconciliation": result
        }

    except Exception as e:
        tracker.update(reason=f"Order failed: {e}")
        raise
```

## Common Method Signatures

Quick reference for most-used py-clob-client methods.

### Trading Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `create_order` | `(order_args: OrderArgs)` | `SignedOrder` | Sign order locally |
| `post_order` | `(order: SignedOrder, type: OrderType)` | `dict` | Submit to exchange |
| `cancel` | `(order_id: str)` | `dict` | Cancel single order |
| `cancel_all` | `()` | `dict` | Cancel all open orders |
| `cancel_orders` | `(order_ids: list[str])` | `dict` | Cancel multiple orders |

### Order Query Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `get_order` | `(order_id: str)` | `dict` | Get order by ID |
| `get_orders` | `(OpenOrderParams)` | `list[dict]` | Get open orders |
| `get_trades` | `(TradeParams)` | `list[dict]` | Get trade history |

### Market Data Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `get_tick_size` | `(token_id: str)` | `float` | Get current tick size |
| `get_midpoint` | `(token_id: str)` | `float` | Get midpoint price (display only) |
| `get_price` | `(token_id: str, side: str)` | `float` | Get executable price |
| `get_order_book` | `(token_id: str)` | `dict` | Get full order book |
| `get_order_books` | `(params: list)` | `list[dict]` | Get multiple order books |

### Credential Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `create_or_derive_api_creds` | `(nonce: int = None)` | `ApiCreds` | Get/create API credentials |
| `set_api_creds` | `(creds: ApiCreds)` | `None` | Set credentials on client |

### OrderArgs Reference

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

order_args = OrderArgs(
    token_id="71321045...",     # Token ID from market
    price=0.45,                  # Price per share
    size=100.0,                  # Number of shares
    side=BUY,                    # BUY or SELL
    fee_rate_bps=0,             # Fee in basis points (optional)
    nonce=None,                  # Order nonce (optional, auto-generated)
    expiration=None              # GTD expiration in seconds (optional)
)
```

### OrderType Reference

```python
from py_clob_client.clob_types import OrderType

# Good-til-canceled (stays on book until filled/canceled)
OrderType.GTC

# Good-til-date (expires at specified time)
OrderType.GTD

# Fill-or-kill (immediate full fill or reject)
OrderType.FOK

# Fill-and-kill / Immediate-or-cancel (partial fill then cancel rest)
OrderType.FOK  # with different handling - actually use market order pattern
```

## Production Checklist

Before deploying to production:

### Rate Limiting

- [ ] Rate limiter configured for all trading endpoints
- [ ] Using conservative limits (80% of max)
- [ ] Separate limiters for orders, cancels, and queries
- [ ] Logging when rate limited

### WebSocket Reliability

- [ ] Heartbeat every 5 seconds
- [ ] Data timeout detection (5 min default)
- [ ] Exponential backoff with jitter (1s -> 60s)
- [ ] Subscription restoration after reconnect
- [ ] Graceful shutdown handling

### Error Handling

- [ ] PolyApiException caught and categorized
- [ ] 401 triggers credential refresh
- [ ] 429 waits and retries
- [ ] 5xx uses exponential backoff
- [ ] All errors logged with context

### Balance Tracking

- [ ] USDC.e balance checked (not Native USDC)
- [ ] Balance tracked before/after trades
- [ ] Reconciliation with tolerance for fees
- [ ] Discrepancies logged/alerted

### Logging & Monitoring

- [ ] All API calls logged with request/response
- [ ] Error rates tracked
- [ ] Connection uptime monitored
- [ ] Balance changes audited

### Graceful Shutdown

- [ ] WebSocket connections closed cleanly
- [ ] Pending orders handled (cancel or wait)
- [ ] Background tasks cancelled
- [ ] Final state logged

## Related Documentation

| Document | Description |
|----------|-------------|
| [Error Handling](./error-handling.md) | Exception types and recovery patterns |
| [Connection Management](../real-time/connection-management.md) | Full WebSocket implementation |
| [Client Initialization](../auth/client-initialization.md) | ClobClient setup |
| [Order Placement](../trading/order-placement.md) | Order creation workflow |

## References

- [Polymarket Rate Limits](https://docs.polymarket.com/quickstart/introduction/rate-limits) - Official documentation
- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client) - Library source

## Navigation

[Back to Library](./README.md) | [Error Handling](./error-handling.md) | [Trading](../trading/README.md)
