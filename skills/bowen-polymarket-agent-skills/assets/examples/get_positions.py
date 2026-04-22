#!/usr/bin/env python3
"""Example: Track user positions and P&L.

This example demonstrates:
- Getting user positions
- Calculating P&L
- Viewing closed positions
- Checking activity history

No authentication required - all Data API endpoints are public.
Just provide a wallet address.
"""

import asyncio
import sys

from polymarket import PolymarketClient


async def main(wallet_address: str):
    async with PolymarketClient() as client:
        # Get current positions
        print(f"=== Positions for {wallet_address[:10]}... ===\n")

        positions = await client.positions.get_positions(
            user=wallet_address,
            limit=10,
        )

        if not positions:
            print("No open positions found.")
        else:
            total_value = 0
            total_pnl = 0

            for pos in positions:
                print(f"{pos.title}")
                print(f"  Outcome: {pos.outcome}")
                print(f"  Size: {pos.size}")
                print(f"  Avg Price: ${pos.avg_price:.4f}")
                print(f"  Current Value: ${pos.current_value:.2f}")
                print(f"  P&L: ${pos.cash_pnl:.2f} ({pos.percent_pnl:.1%})")
                print()

                total_value += pos.current_value or 0
                total_pnl += pos.cash_pnl or 0

            print(f"Total Value: ${total_value:.2f}")
            print(f"Total P&L: ${total_pnl:.2f}")

        # Get total position value
        value = await client.positions.get_position_value(wallet_address)
        print(f"\nPortfolio Value: ${value:.2f}")

        # Get closed positions
        print("\n=== Recent Closed Positions ===\n")
        closed = await client.positions.get_closed_positions(
            user=wallet_address,
            limit=5,
            sort_by="TIMESTAMP",
            sort_direction="DESC",
        )

        for pos in closed:
            print(f"{pos.title}")
            print(f"  Outcome: {pos.outcome}")
            print(f"  Realized P&L: ${pos.realized_pnl:.2f}")
            print()

        # Get recent activity
        print("=== Recent Activity ===\n")
        activity = await client.positions.get_activity(
            user=wallet_address,
            limit=5,
        )

        for act in activity:
            print(f"{act.type}: {act.title}")
            print(f"  Size: {act.size}, USDC: ${act.usdc_size:.2f}")
            print()

        # How many markets traded
        count = await client.positions.get_markets_traded(wallet_address)
        print(f"Total markets traded: {count}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_positions.py <wallet_address>")
        print("\nExample: python get_positions.py 0x...")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
