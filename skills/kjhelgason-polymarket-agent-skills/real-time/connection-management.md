# Connection Management - Robust WebSocket Lifecycle Handling

Patterns for maintaining reliable, long-running WebSocket connections to Polymarket.

## Overview

Polymarket WebSocket connections require active management for production reliability:

- **Heartbeat** - Keep connections alive with periodic pings
- **Timeout detection** - Detect stale connections (data stops without disconnect)
- **Reconnection** - Handle disconnects gracefully with exponential backoff
- **Subscription restoration** - Resubscribe after reconnection

## Known Connection Issues

Understanding these issues is critical for production deployments:

| Issue | Symptom | Detection | Solution |
|-------|---------|-----------|----------|
| Silent timeout | Data stops ~20 minutes | No data timeout | Force reconnect |
| Server disconnect | Connection closes | `ConnectionClosed` exception | Auto-reconnect |
| Subscription loss | Reconnects but no data | Events stop after reconnect | Resubscribe |
| Network hiccup | Brief data gap | Missing messages | Accept gaps or validate |

**Key insight:** The connection may appear open (no exception) but stop delivering data. You must track data freshness, not just connection state.

## Heartbeat Pattern

Send periodic pings to keep the connection alive and detect dead connections.

```python
import asyncio
import websockets

async def heartbeat(ws, interval: int = 5):
    """Send ping every N seconds to keep connection alive.

    Args:
        ws: WebSocket connection
        interval: Seconds between pings (default: 5)
    """
    while True:
        await asyncio.sleep(interval)
        try:
            await ws.ping()
        except websockets.ConnectionClosed:
            break
```

**Recommended interval:** 5 seconds

The websockets library handles pong responses automatically. If pong isn't received within timeout, the connection closes.

### Integrating Heartbeat with Connection

```python
async def stream_with_heartbeat(url: str, subscribe_msg: dict, callback):
    """Stream data with keepalive heartbeat."""
    async with websockets.connect(url) as ws:
        # Start heartbeat in background
        heartbeat_task = asyncio.create_task(heartbeat(ws))

        try:
            # Subscribe
            await ws.send(json.dumps(subscribe_msg))

            # Process messages
            async for message in ws:
                data = json.loads(message)
                await callback(data)

        finally:
            # Clean up heartbeat
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
```

## Data Timeout Detection

Detect when data stops flowing even if the connection remains open.

```python
from datetime import datetime

class ConnectionMonitor:
    """Monitor data freshness to detect stale connections."""

    def __init__(self, timeout_seconds: int = 300):
        """Initialize monitor.

        Args:
            timeout_seconds: Max seconds without data before stale (default: 5 min)
        """
        self.last_data_time = datetime.now()
        self.timeout_seconds = timeout_seconds

    def on_data_received(self):
        """Call whenever any data is received."""
        self.last_data_time = datetime.now()

    def is_data_stale(self) -> bool:
        """Check if data timeout exceeded."""
        elapsed = (datetime.now() - self.last_data_time).total_seconds()
        return elapsed > self.timeout_seconds

    def get_seconds_since_data(self) -> float:
        """Get seconds since last data received."""
        return (datetime.now() - self.last_data_time).total_seconds()
```

**Recommended timeout:** 5 minutes (300 seconds)

For high-activity markets, you might use a shorter timeout. For low-activity markets, use longer to avoid false positives.

### Periodic Staleness Check

```python
async def check_data_freshness(monitor: ConnectionMonitor, on_stale):
    """Periodically check for stale data.

    Args:
        monitor: ConnectionMonitor instance
        on_stale: Async callback when data is stale
    """
    while True:
        await asyncio.sleep(60)  # Check every minute
        if monitor.is_data_stale():
            await on_stale()
            return  # Exit after triggering stale callback
```

## Reconnection with Exponential Backoff

Handle disconnects gracefully with increasing delays to avoid hammering the server.

```python
import random
import json

async def connect_with_backoff(url: str, subscribe_msg: dict, callback):
    """Connect with automatic reconnection and exponential backoff.

    Args:
        url: WebSocket endpoint URL
        subscribe_msg: Subscription message dict
        callback: Async function to process each message
    """
    base_delay = 1      # Start with 1 second delay
    max_delay = 60      # Max delay of 60 seconds
    delay = base_delay

    while True:
        try:
            async with websockets.connect(url) as ws:
                # Reset delay on successful connection
                delay = base_delay
                print(f"Connected to {url}")

                # Subscribe
                await ws.send(json.dumps(subscribe_msg))

                # Start heartbeat
                heartbeat_task = asyncio.create_task(heartbeat(ws))

                try:
                    async for message in ws:
                        data = json.loads(message)
                        await callback(data)
                finally:
                    heartbeat_task.cancel()

        except websockets.ConnectionClosed as e:
            print(f"Connection closed (code {e.code}), reconnecting in {delay:.1f}s...")

        except Exception as e:
            print(f"Error: {e}, reconnecting in {delay:.1f}s...")

        # Wait before reconnecting
        await asyncio.sleep(delay)

        # Increase delay with jitter for next attempt
        delay = min(delay * 2 + random.random(), max_delay)
```

**Backoff strategy:**
- Start: 1 second
- Double each attempt
- Add random jitter (0-1 second) to prevent thundering herd
- Cap at 60 seconds

## Complete Robust Connection Class

Production-ready WebSocket manager combining all patterns:

```python
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polymarket_ws")


class DataTimeoutError(Exception):
    """Raised when no data received within timeout period."""
    pass


class RobustWebSocket:
    """Production-ready WebSocket with full lifecycle management."""

    def __init__(self, url: str, subscribe_msg: dict):
        """Initialize robust WebSocket manager.

        Args:
            url: WebSocket endpoint URL
            subscribe_msg: Subscription message to send on connect
        """
        self.url = url
        self.subscribe_msg = subscribe_msg
        self.running = False
        self.last_data_time = None
        self.data_timeout = 300          # 5 minutes
        self.heartbeat_interval = 5      # 5 seconds
        self.connect_count = 0

    async def connect(self, callback):
        """Connect with full lifecycle management.

        Args:
            callback: Async function called for each received message
        """
        self.running = True

        while self.running:
            self.connect_count += 1
            logger.info(f"Connection attempt #{self.connect_count}")

            try:
                async with websockets.connect(self.url) as ws:
                    logger.info(f"Connected to {self.url}")

                    # Subscribe
                    await ws.send(json.dumps(self.subscribe_msg))
                    self.last_data_time = datetime.now()

                    # Start background tasks
                    tasks = [
                        asyncio.create_task(self._heartbeat(ws)),
                        asyncio.create_task(self._check_data_timeout())
                    ]

                    try:
                        async for message in ws:
                            self.last_data_time = datetime.now()
                            data = json.loads(message)
                            await callback(data)

                    finally:
                        # Clean up background tasks
                        for task in tasks:
                            task.cancel()
                        await asyncio.gather(*tasks, return_exceptions=True)

            except websockets.ConnectionClosed as e:
                logger.warning(f"Connection closed: code={e.code}, reason={e.reason}")
                await asyncio.sleep(5)

            except DataTimeoutError:
                logger.warning("Data timeout, forcing reconnect...")
                # Loop will reconnect

            except Exception as e:
                logger.error(f"Connection error: {e}")
                await asyncio.sleep(10)

    async def _heartbeat(self, ws):
        """Periodic ping to keep connection alive."""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            try:
                await ws.ping()
            except websockets.ConnectionClosed:
                break

    async def _check_data_timeout(self):
        """Check for data timeout every minute."""
        while True:
            await asyncio.sleep(60)
            if self.last_data_time:
                elapsed = (datetime.now() - self.last_data_time).total_seconds()
                if elapsed > self.data_timeout:
                    raise DataTimeoutError(
                        f"No data received for {elapsed:.0f} seconds"
                    )

    def stop(self):
        """Stop the connection gracefully."""
        self.running = False
        logger.info("Stop requested, will disconnect after current message")


# Usage
async def main():
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    subscribe_msg = {
        "type": "market",
        "assets_ids": ["your_token_id"]
    }

    async def on_message(data):
        print(f"Received: {data.get('event_type', 'unknown')}")

    ws = RobustWebSocket(url, subscribe_msg)
    await ws.connect(on_message)
```

## Subscription State Restoration

Track subscriptions to restore after reconnection:

```python
class SubscriptionManager:
    """Track subscriptions for restoration after reconnect."""

    def __init__(self):
        self.market_tokens = set()    # Token IDs for market channel
        self.user_markets = set()     # Condition IDs for user channel
        self.api_creds = None         # For user channel auth

    def add_market_subscription(self, token_ids: list):
        """Add tokens to market channel subscription."""
        self.market_tokens.update(token_ids)

    def remove_market_subscription(self, token_ids: list):
        """Remove tokens from market channel subscription."""
        self.market_tokens.difference_update(token_ids)

    def add_user_subscription(self, market_ids: list):
        """Add markets to user channel subscription."""
        self.user_markets.update(market_ids)

    def set_user_credentials(self, api_creds: dict):
        """Set API credentials for user channel."""
        self.api_creds = api_creds

    def get_market_subscribe_msg(self) -> dict:
        """Get current market channel subscription message."""
        return {
            "type": "market",
            "assets_ids": list(self.market_tokens)
        }

    def get_user_subscribe_msg(self) -> dict:
        """Get current user channel subscription message."""
        if not self.api_creds:
            raise ValueError("API credentials not set")

        msg = {
            "type": "user",
            "auth": self.api_creds
        }
        if self.user_markets:
            msg["markets"] = list(self.user_markets)
        return msg

    def has_market_subscriptions(self) -> bool:
        """Check if any market subscriptions exist."""
        return len(self.market_tokens) > 0

    def has_user_subscriptions(self) -> bool:
        """Check if user channel is configured."""
        return self.api_creds is not None
```

### Using SubscriptionManager with RobustWebSocket

```python
class ManagedWebSocket:
    """WebSocket with subscription management."""

    def __init__(self, channel: str):
        """Initialize managed WebSocket.

        Args:
            channel: 'market' or 'user'
        """
        self.channel = channel
        self.subscriptions = SubscriptionManager()
        self.ws = None

        if channel == "market":
            self.url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        else:
            self.url = "wss://ws-subscriptions-clob.polymarket.com/ws/user"

    def _get_subscribe_msg(self) -> dict:
        """Get current subscription message."""
        if self.channel == "market":
            return self.subscriptions.get_market_subscribe_msg()
        else:
            return self.subscriptions.get_user_subscribe_msg()

    async def connect(self, callback):
        """Connect with subscription state restoration."""
        self.ws = RobustWebSocket(self.url, self._get_subscribe_msg())
        await self.ws.connect(callback)

    async def add_subscription(self, ids: list):
        """Add new subscriptions (requires reconnect or dynamic update)."""
        if self.channel == "market":
            self.subscriptions.add_market_subscription(ids)
        else:
            self.subscriptions.add_user_subscription(ids)
        # Note: To apply immediately, would need dynamic subscription support
        # Current implementation restores on next reconnect
```

## Graceful Shutdown

Clean up connections and tasks properly:

```python
import signal

class GracefulWebSocket(RobustWebSocket):
    """WebSocket with graceful shutdown support."""

    def __init__(self, url: str, subscribe_msg: dict):
        super().__init__(url, subscribe_msg)
        self._shutdown_event = asyncio.Event()

    async def connect(self, callback):
        """Connect with shutdown support."""
        # Set up signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._handle_shutdown)
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                pass

        # Run connection with shutdown check
        self.running = True

        while self.running and not self._shutdown_event.is_set():
            # ... connection logic from RobustWebSocket ...
            pass

        logger.info("Graceful shutdown complete")

    def _handle_shutdown(self):
        """Handle shutdown signal."""
        logger.info("Shutdown signal received")
        self._shutdown_event.set()
        self.running = False


async def run_with_cleanup(ws: GracefulWebSocket, callback):
    """Run WebSocket with proper cleanup on exit."""
    try:
        await ws.connect(callback)
    except asyncio.CancelledError:
        logger.info("Connection cancelled, cleaning up...")
        ws.stop()
    finally:
        logger.info("WebSocket connection closed")
```

## Monitoring and Logging

Track connection health for debugging and alerting:

```python
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ConnectionMetrics:
    """Track connection health metrics."""
    connect_count: int = 0
    disconnect_count: int = 0
    message_count: int = 0
    last_connect_time: Optional[float] = None
    last_disconnect_time: Optional[float] = None
    last_message_time: Optional[float] = None
    total_uptime_seconds: float = 0.0
    _session_start: Optional[float] = field(default=None, repr=False)

    def on_connect(self):
        """Record connection event."""
        self.connect_count += 1
        self.last_connect_time = time.time()
        self._session_start = time.time()

    def on_disconnect(self):
        """Record disconnection event."""
        self.disconnect_count += 1
        self.last_disconnect_time = time.time()
        if self._session_start:
            self.total_uptime_seconds += time.time() - self._session_start
            self._session_start = None

    def on_message(self):
        """Record message received."""
        self.message_count += 1
        self.last_message_time = time.time()

    def get_uptime_ratio(self) -> float:
        """Get ratio of connected time to total time."""
        if not self.last_connect_time:
            return 0.0
        total_time = time.time() - self.last_connect_time + self.total_uptime_seconds
        return self.total_uptime_seconds / total_time if total_time > 0 else 0.0


class MonitoredWebSocket(RobustWebSocket):
    """WebSocket with health metrics."""

    def __init__(self, url: str, subscribe_msg: dict):
        super().__init__(url, subscribe_msg)
        self.metrics = ConnectionMetrics()

    async def connect(self, callback):
        """Connect with metrics tracking."""
        self.running = True

        while self.running:
            try:
                async with websockets.connect(self.url) as ws:
                    self.metrics.on_connect()
                    logger.info(f"Connected (attempt #{self.metrics.connect_count})")

                    await ws.send(json.dumps(self.subscribe_msg))

                    async for message in ws:
                        self.metrics.on_message()
                        data = json.loads(message)
                        await callback(data)

            except websockets.ConnectionClosed:
                self.metrics.on_disconnect()
                logger.warning(
                    f"Disconnected. Uptime ratio: {self.metrics.get_uptime_ratio():.2%}"
                )
                await asyncio.sleep(5)

            except Exception as e:
                self.metrics.on_disconnect()
                logger.error(f"Error: {e}")
                await asyncio.sleep(10)

    def log_status(self):
        """Log current connection status."""
        logger.info(
            f"Status: connects={self.metrics.connect_count}, "
            f"messages={self.metrics.message_count}, "
            f"uptime={self.metrics.get_uptime_ratio():.2%}"
        )
```

## Best Practices Summary

| Practice | Recommendation | Why |
|----------|----------------|-----|
| Heartbeat | Ping every 5 seconds | Detect dead connections early |
| Data timeout | Reconnect after 5 min no data | Handle silent failures |
| Backoff | 1s -> 60s with jitter | Avoid server overload |
| Subscription tracking | Restore after reconnect | Don't lose subscriptions |
| Graceful shutdown | Cancel tasks, close cleanly | Prevent resource leaks |
| Metrics | Track connects, messages, uptime | Debug and alert on issues |

## Configuration Reference

```python
# Recommended production settings
HEARTBEAT_INTERVAL = 5        # seconds between pings
DATA_TIMEOUT = 300            # seconds without data before reconnect
BASE_RECONNECT_DELAY = 1      # initial reconnect delay
MAX_RECONNECT_DELAY = 60      # maximum reconnect delay
STALENESS_CHECK_INTERVAL = 60 # how often to check for stale data
```

Adjust these based on your use case:
- **High-frequency trading:** Shorter timeouts (60s), faster reconnect
- **Monitoring dashboard:** Longer timeouts (5min), standard reconnect
- **Low-activity markets:** Much longer timeouts (15min+) to avoid false positives

## Related Documentation

| Document | Purpose |
|----------|---------|
| [websocket-overview.md](./websocket-overview.md) | WebSocket architecture overview |
| [market-channel.md](./market-channel.md) | Market data streaming details |
| [user-channel.md](./user-channel.md) | Authenticated order notifications |

---

**Last updated:** 2026-01-31
