#!/usr/bin/env python3
"""Example: Discover and analyze Polymarket markets.

This example demonstrates:
- Listing active markets
- Searching by keyword
- Getting market details and prices
- Analyzing order book depth

No authentication required - all endpoints are public.
"""

import asyncio

from polymarket import PolymarketClient


async def main():
    async with PolymarketClient() as client:
        # Check API health
        healthy = await client.health_check()
        print(f"API Status: {'healthy' if healthy else 'unhealthy'}")
        print()

        # List top markets by volume
        print("=== Top Markets by Volume ===")
        markets = await client.markets.list_markets(
            active=True,
            order="volume",
            ascending=False,
            limit=5,
        )

        for market in markets:
            print(f"\n{market.question}")
            print(f"  Volume: ${market.volume}")
            print(f"  Liquidity: ${market.liquidity}")
            if market.tokens:
                for token in market.tokens:
                    print(f"  {token.outcome}: {token.price}")

        # Search for specific markets
        print("\n\n=== Search: 'election' ===")
        results = await client.markets.search(
            query="election",
            limit_per_type=3,
        )

        for event in results.events or []:
            print(f"\n{event.title}")
            for market in (event.markets or [])[:2]:
                print(f"  - {market.question}")

        # Get detailed market info
        if markets and markets[0].tokens:
            print("\n\n=== Order Book Analysis ===")
            token_id = markets[0].tokens[0].token_id
            market = markets[0]

            print(f"Market: {market.question}")

            # Get spread
            spread = await client.orderbook.get_spread(token_id)
            print(f"Bid: {spread.bid}, Ask: {spread.ask}, Spread: {spread.spread}")

            # Get midpoint
            midpoint = await client.orderbook.get_midpoint(token_id)
            print(f"Midpoint: {midpoint}")

            # Get order book
            book = await client.orderbook.get_book(token_id)
            print(f"\nTop 3 Bids:")
            for level in (book.bids or [])[:3]:
                print(f"  {level.price}: {level.size}")
            print(f"\nTop 3 Asks:")
            for level in (book.asks or [])[:3]:
                print(f"  {level.price}: {level.size}")


if __name__ == "__main__":
    asyncio.run(main())
