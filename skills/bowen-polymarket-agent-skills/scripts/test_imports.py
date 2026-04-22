#!/usr/bin/env python3
"""Test that all SDK imports work correctly."""

import sys
sys.path.insert(0, ".")

def test_imports():
    """Test all imports."""
    print("Testing SDK imports...\n")

    # Test basic imports
    from polymarket.config import PolymarketConfig
    from polymarket.exceptions import PolymarketError, AuthenticationError
    from polymarket.utils import to_wei, from_wei, generate_salt
    print("[OK] Foundation modules imported")

    # Test model imports
    from polymarket.models.auth import ApiCredentials, Credentials
    from polymarket.models.orders import SignedOrder, OrderSide, OrderType
    from polymarket.models.markets import Market, Event
    from polymarket.models.positions import Position
    from polymarket.models.orderbook import OrderBookSummary
    from polymarket.models.bridge import QuoteRequest
    from polymarket.models.websocket import WsBookMessage
    print("[OK] All model modules imported")

    # Test service imports
    from polymarket.services.base import BaseService
    from polymarket.services.gamma import GammaService
    from polymarket.services.data import DataService
    from polymarket.services.bridge import BridgeService
    from polymarket.services.clob.orderbook import OrderbookService
    from polymarket.services.clob.orders import OrderService
    print("[OK] All service modules imported")

    # Test websocket imports
    from polymarket.websocket.base import BaseWebSocket
    from polymarket.websocket.market import MarketStream
    from polymarket.websocket.user import UserStream
    print("[OK] WebSocket modules imported")

    # Test main client
    from polymarket.client import PolymarketClient
    print("[OK] PolymarketClient imported")

    # Test utilities
    config = PolymarketConfig()
    print(f"[OK] Config: {config.clob_url}")

    wei = to_wei(100.50)
    back = from_wei(wei)
    print(f"[OK] Wei: 100.50 -> {wei} -> {back}")

    salt = generate_salt()
    print(f"[OK] Salt: {salt[:20]}...")

    print("\n=== ALL TESTS PASSED ===")


if __name__ == "__main__":
    test_imports()
