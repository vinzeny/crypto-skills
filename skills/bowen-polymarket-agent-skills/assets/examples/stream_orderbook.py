#!/usr/bin/env python3
"""Example: Stream real-time order book updates.

This example demonstrates:
- Connecting to WebSocket market channel
- Receiving order book snapshots
- Processing price change events
- Building a local order book

No authentication required - market channel is public.
"""

import asyncio
import sys

from polymarket import PolymarketClient, PolymarketConfig
from polymarket.models.websocket import (
    WsBookMessage,
    WsLastTradePriceMessage,
    WsPriceChangeMessage,
)
from polymarket.websocket import MarketStream


class LocalOrderBook:
    """Maintains a local copy of the order book."""

    def __init__(self):
        self.bids: dict[str, str] = {}
        self.asks: dict[str, str] = {}
        self.last_trade_price: str | None = None

    def update(self, event):
        """Update book from WebSocket event."""
        if isinstance(event, WsBookMessage):
            # Full snapshot
            self.bids = {b.price: b.size for b in event.bids}
            self.asks = {a.price: a.size for a in event.asks}
            print(f"[SNAPSHOT] {len(self.bids)} bids, {len(self.asks)} asks")

        elif isinstance(event, WsPriceChangeMessage):
            # Incremental update
            for change in event.price_changes:
                book = self.bids if change.side.value == "BUY" else self.asks
                if change.size == "0":
                    book.pop(change.price, None)
                else:
                    book[change.price] = change.size
                print(
                    f"[PRICE] {change.side.value} {change.price}: "
                    f"{change.size} (best: {change.best_bid}/{change.best_ask})"
                )

        elif isinstance(event, WsLastTradePriceMessage):
            self.last_trade_price = event.price
            print(
                f"[TRADE] {event.side.value} {event.size} @ {event.price}"
            )

    def best_bid(self) -> str | None:
        """Get best bid price."""
        return max(self.bids.keys()) if self.bids else None

    def best_ask(self) -> str | None:
        """Get best ask price."""
        return min(self.asks.keys()) if self.asks else None

    def spread(self) -> float | None:
        """Calculate current spread."""
        bid = self.best_bid()
        ask = self.best_ask()
        if bid and ask:
            return float(ask) - float(bid)
        return None


async def main(token_id: str):
    config = PolymarketConfig()
    book = LocalOrderBook()

    print(f"Streaming order book for token: {token_id[:20]}...")
    print("Press Ctrl+C to stop\n")

    stream = MarketStream(config, custom_features=True)

    try:
        async with stream:
            async for event in stream.subscribe([token_id]):
                book.update(event)

                # Print current state periodically
                if isinstance(event, WsBookMessage):
                    bid = book.best_bid()
                    ask = book.best_ask()
                    spread = book.spread()
                    print(
                        f"\n>>> Best: {bid} / {ask} "
                        f"(spread: {spread:.4f})\n" if spread else ""
                    )

    except KeyboardInterrupt:
        print("\nStopping...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to a sample token ID if none provided
        print("Usage: python stream_orderbook.py <token_id>")
        print("\nTo find a token_id, run market_scanner.py first.")
        print("Example: python stream_orderbook.py 71321045679...")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
