#!/usr/bin/env python3
"""Example: Place and manage orders on Polymarket.

This example demonstrates:
- Creating API credentials
- Building and signing orders
- Placing orders
- Monitoring order status
- Cancelling orders

REQUIRES AUTHENTICATION:
- Set POLY_PRIVATE_KEY environment variable
- Or create credentials first and set POLY_API_KEY, POLY_API_SECRET, POLY_API_PASSPHRASE
"""

import asyncio
import os
import sys
from decimal import Decimal

from polymarket import PolymarketClient
from polymarket.auth import Credentials
from polymarket.models.orders import OrderType


async def main(token_id: str, side: str, price: str, size: str):
    # Load credentials from environment
    private_key = os.environ.get("POLY_PRIVATE_KEY")
    api_key = os.environ.get("POLY_API_KEY")
    api_secret = os.environ.get("POLY_API_SECRET")
    api_passphrase = os.environ.get("POLY_API_PASSPHRASE")

    if not private_key:
        print("Error: POLY_PRIVATE_KEY environment variable required")
        sys.exit(1)

    # Build credentials if provided
    credentials = None
    if api_key and api_secret and api_passphrase:
        credentials = Credentials(
            api_key=api_key,
            secret=api_secret,
            passphrase=api_passphrase,
        )

    async with PolymarketClient(
        private_key=private_key,
        credentials=credentials,
    ) as client:
        print(f"Wallet: {client.address}")

        # Create credentials if not provided
        if credentials is None:
            print("\nCreating API credentials...")
            credentials = await client.create_api_credentials()
            print(f"API Key: {credentials.api_key}")
            print(f"Secret: {credentials.secret}")
            print(f"Passphrase: {credentials.passphrase}")
            print("\nSave these for future use!")

        # Check balance
        balance = await client.account.get_balance_allowance(
            asset_type="COLLATERAL",
            signature_type=2,
        )
        print(f"\nUSDC Balance: {balance.balance}")
        print(f"Allowance: {balance.allowance}")

        # Get tick size for price rounding
        tick_info = await client.orderbook.get_tick_size(token_id)
        tick_size = tick_info.get("minimum_tick_size", "0.01")
        print(f"\nTick size: {tick_size}")

        # Build order
        builder = client.order_builder
        if builder is None:
            print("Error: Could not create order builder")
            sys.exit(1)

        if side.upper() == "BUY":
            order = (
                builder
                .buy(token_id, Decimal(price), Decimal(size))
                .with_tick_size(tick_size)
                .build()
            )
        else:
            order = (
                builder
                .sell(token_id, Decimal(price), Decimal(size))
                .with_tick_size(tick_size)
                .build()
            )

        print(f"\nOrder Details:")
        print(f"  Side: {order.side}")
        print(f"  Maker Amount: {order.maker_amount}")
        print(f"  Taker Amount: {order.taker_amount}")

        # Place order
        print("\nPlacing order...")
        result = await client.orders.place_order(
            order=order,
            order_type=OrderType.GTC,
        )

        if result.success:
            print(f"Order placed successfully!")
            print(f"  Order ID: {result.order_id}")
            print(f"  Status: {result.status}")
        else:
            print(f"Order failed: {result.error_msg}")
            return

        # List open orders
        print("\nOpen orders:")
        orders = await client.orders.get_orders()
        for o in orders:
            print(f"  {o.id}: {o.side} {o.original_size} @ {o.price}")

        # Cancel the order
        if result.order_id:
            print(f"\nCancelling order {result.order_id}...")
            cancel_result = await client.orders.cancel_order(result.order_id)
            print(f"Cancelled: {cancel_result.canceled}")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python place_order.py <token_id> <side> <price> <size>")
        print("\nExample: python place_order.py 71321... BUY 0.55 10")
        print("\nRequired environment variables:")
        print("  POLY_PRIVATE_KEY - Your wallet private key")
        print("\nOptional (if you already have API credentials):")
        print("  POLY_API_KEY")
        print("  POLY_API_SECRET")
        print("  POLY_API_PASSPHRASE")
        sys.exit(1)

    asyncio.run(main(
        token_id=sys.argv[1],
        side=sys.argv[2],
        price=sys.argv[3],
        size=sys.argv[4],
    ))
