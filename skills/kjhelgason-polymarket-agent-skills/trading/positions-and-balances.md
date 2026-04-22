# Positions and Balances Guide

Documentation for querying positions and balances via the CLOB API and on-chain methods, covering pre-order validation and position tracking.

**Covers:** CLOB-04 (Positions)

## Overview

Before trading, you need to verify:

| For Action | Check | Source |
|------------|-------|--------|
| BUY order | USDC.e balance | On-chain (Polygon) |
| SELL order | Position/shares | CLOB API or Data API |
| Any order | Allowances set | On-chain (Polygon) |

```
┌─────────────────────────────────────────────────────┐
│                  Balance Sources                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│   CLOB API                    On-Chain (Polygon)    │
│   ─────────                   ──────────────────    │
│   • Positions                 • USDC.e balance      │
│   • Open orders               • Allowances          │
│   • Quick checks              • Definitive source   │
│                                                      │
│   Data API                                          │
│   ─────────                                         │
│   • Detailed positions        Cross-reference:      │
│   • PnL calculations          ../data-analytics/    │
│   • Trade history             positions-and-history │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Understanding Positions

### What is a Position?

A position represents shares you hold in a market outcome:

- **YES position:** Shares that pay $1 if outcome is YES
- **NO position:** Shares that pay $1 if outcome is NO
- **Entry price:** Your average purchase price
- **Current value:** Current market price x shares

### How Positions are Created

```
BUY YES token  ──>  YES position (shares held)
BUY NO token   ──>  NO position (shares held)
SELL YES token ──>  Reduces YES position (or short)
SELL NO token  ──>  Reduces NO position (or short)
```

### Position Resolution

At market close:
- **Winning positions:** Pay $1.00 per share
- **Losing positions:** Pay $0.00 per share

## CLOB Position Methods

### Get Positions via CLOB Client

```python
def get_clob_positions(client, market_id: str = None, asset_id: str = None) -> list:
    """Get positions from CLOB API.

    Args:
        client: Authenticated ClobClient
        market_id: Optional condition ID filter
        asset_id: Optional token ID filter

    Returns:
        List of position objects
    """
    params = {}
    if market_id:
        params["market"] = market_id
    if asset_id:
        params["asset_id"] = asset_id

    # Note: Method may vary by py-clob-client version
    # Check client.get_positions() or similar
    try:
        positions = client.get_positions(**params)
        return positions
    except AttributeError:
        # Fallback: Use orders to infer positions
        print("Note: Using orders to estimate positions")
        return infer_positions_from_orders(client)

def infer_positions_from_orders(client) -> list:
    """Estimate positions from matched orders.

    This is a fallback when direct position endpoint unavailable.
    For accurate positions, use Data API.
    """
    orders = client.get_orders(state="MATCHED")

    # Aggregate by token
    positions = {}
    for order in orders:
        token_id = order.get("asset_id")
        side = order.get("side")
        size_matched = float(order.get("size_matched", 0))
        price = float(order.get("price", 0))

        if token_id not in positions:
            positions[token_id] = {"buys": 0, "sells": 0, "cost": 0}

        if side == "BUY":
            positions[token_id]["buys"] += size_matched
            positions[token_id]["cost"] += size_matched * price
        else:
            positions[token_id]["sells"] += size_matched

    # Calculate net positions
    result = []
    for token_id, data in positions.items():
        net = data["buys"] - data["sells"]
        if net > 0:
            avg_price = data["cost"] / data["buys"] if data["buys"] > 0 else 0
            result.append({
                "token_id": token_id,
                "size": net,
                "avg_price": avg_price
            })

    return result
```

### Position Schema

```python
{
    "market": "0x...",        # Condition ID
    "asset_id": "71321...",   # Token ID
    "size": "100.0",          # Number of shares
    "avg_price": "0.45",      # Average entry price
    "side": "BUY"             # Position side
}
```

## On-Chain Balance Verification

### USDC.e Balance Check

USDC.e is required for BUY orders. Check balance on Polygon:

```python
from web3 import Web3

# Polygon RPC endpoints
POLYGON_RPC = "https://polygon-rpc.com"  # Public
# Or use: Alchemy, Infura, QuickNode for better reliability

# USDC.e contract on Polygon
USDC_E_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
USDC_E_DECIMALS = 6  # CRITICAL: 6 decimals, not 18

# Minimal ABI for balance check
BALANCE_ABI = [
    {
        "name": "balanceOf",
        "inputs": [{"type": "address", "name": "account"}],
        "outputs": [{"type": "uint256"}],
        "type": "function",
        "stateMutability": "view"
    }
]

def get_usdc_balance(wallet_address: str) -> float:
    """Get USDC.e balance for a wallet.

    Args:
        wallet_address: Wallet to check (EOA or funder address)

    Returns:
        USDC.e balance in dollars
    """
    web3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

    contract = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_E_ADDRESS),
        abi=BALANCE_ABI
    )

    # Get raw balance (6 decimals)
    raw_balance = contract.functions.balanceOf(
        Web3.to_checksum_address(wallet_address)
    ).call()

    # Convert to dollars
    balance = raw_balance / (10 ** USDC_E_DECIMALS)

    return balance

# Usage
wallet = "0xYourWalletAddress"
balance = get_usdc_balance(wallet)
print(f"USDC.e balance: ${balance:.2f}")
```

### Check Multiple Addresses

For proxy wallets, check both EOA and funder:

```python
def check_all_balances(eoa_address: str, funder_address: str = None) -> dict:
    """Check balances for EOA and optional funder.

    Args:
        eoa_address: Your EOA wallet
        funder_address: Funder/proxy address if different

    Returns:
        Dict with balances for each address
    """
    result = {
        "eoa": {
            "address": eoa_address,
            "usdc_balance": get_usdc_balance(eoa_address)
        }
    }

    if funder_address and funder_address.lower() != eoa_address.lower():
        result["funder"] = {
            "address": funder_address,
            "usdc_balance": get_usdc_balance(funder_address)
        }

    return result

# Usage
balances = check_all_balances(eoa_address, funder_address)
print(f"EOA: ${balances['eoa']['usdc_balance']:.2f}")
if 'funder' in balances:
    print(f"Funder: ${balances['funder']['usdc_balance']:.2f}")
```

### Check Allowances

For EOA wallets, verify token allowances are set:

```python
# Allowance ABI
ALLOWANCE_ABI = [
    {
        "name": "allowance",
        "inputs": [
            {"type": "address", "name": "owner"},
            {"type": "address", "name": "spender"}
        ],
        "outputs": [{"type": "uint256"}],
        "type": "function",
        "stateMutability": "view"
    }
]

# Polymarket contract addresses
EXCHANGE_ADDRESS = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
NEG_RISK_EXCHANGE = "0xC5d563A36AE78145C45a50134d48A1215220f80a"
NEG_RISK_ADAPTER = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"

def check_allowances(wallet_address: str) -> dict:
    """Check all required allowances for trading.

    Args:
        wallet_address: Wallet to check

    Returns:
        Dict with allowance status for each spender
    """
    web3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

    contract = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_E_ADDRESS),
        abi=ALLOWANCE_ABI
    )

    spenders = {
        "Exchange": EXCHANGE_ADDRESS,
        "NegRiskExchange": NEG_RISK_EXCHANGE,
        "NegRiskAdapter": NEG_RISK_ADAPTER
    }

    result = {}
    for name, spender in spenders.items():
        allowance = contract.functions.allowance(
            Web3.to_checksum_address(wallet_address),
            Web3.to_checksum_address(spender)
        ).call()

        # MaxUint256 is "unlimited"
        MAX_UINT256 = 2**256 - 1
        is_unlimited = allowance >= MAX_UINT256 // 2

        result[name] = {
            "spender": spender,
            "allowance": allowance,
            "is_unlimited": is_unlimited,
            "needs_approval": allowance == 0
        }

    return result

# Usage
allowances = check_allowances(wallet_address)
for name, data in allowances.items():
    status = "OK" if not data["needs_approval"] else "NEEDS APPROVAL"
    print(f"{name}: {status}")
```

## Pre-Order Validation

### Validate Before BUY Order

```python
def can_place_buy_order(
    wallet_address: str,
    price: float,
    size: float,
    include_allowance_check: bool = True
) -> dict:
    """Check if wallet can place a BUY order.

    Args:
        wallet_address: Funder/trading wallet
        price: Order price
        size: Number of shares
        include_allowance_check: Whether to verify allowances

    Returns:
        Validation result with details
    """
    required_amount = price * size

    # Check USDC.e balance
    balance = get_usdc_balance(wallet_address)

    result = {
        "can_place": balance >= required_amount,
        "required": required_amount,
        "available": balance,
        "shortfall": max(0, required_amount - balance)
    }

    if include_allowance_check:
        allowances = check_allowances(wallet_address)
        needs_approval = any(a["needs_approval"] for a in allowances.values())
        result["allowances_ok"] = not needs_approval
        result["can_place"] = result["can_place"] and not needs_approval

    return result

# Usage
validation = can_place_buy_order(wallet_address, price=0.45, size=100)

if validation["can_place"]:
    print("Ready to place order")
else:
    if validation["shortfall"] > 0:
        print(f"Need ${validation['shortfall']:.2f} more USDC.e")
    if not validation.get("allowances_ok", True):
        print("Need to set token allowances")
```

### Validate Before SELL Order

```python
def can_place_sell_order(
    client,
    token_id: str,
    size: float
) -> dict:
    """Check if user can place a SELL order.

    Args:
        client: Authenticated ClobClient
        token_id: Token to sell
        size: Number of shares to sell

    Returns:
        Validation result
    """
    # Get current positions
    positions = get_clob_positions(client, asset_id=token_id)

    total_position = sum(float(p.get("size", 0)) for p in positions)

    # Account for open sell orders
    open_orders = client.get_orders(state="LIVE")
    pending_sells = sum(
        float(o.get("original_size", 0)) - float(o.get("size_matched", 0))
        for o in open_orders
        if o.get("asset_id") == token_id and o.get("side") == "SELL"
    )

    available = total_position - pending_sells

    return {
        "can_place": available >= size,
        "position": total_position,
        "pending_sells": pending_sells,
        "available": available,
        "shortfall": max(0, size - available)
    }

# Usage
validation = can_place_sell_order(client, token_id, size=50)

if validation["can_place"]:
    print("Ready to place sell order")
else:
    print(f"Only {validation['available']:.2f} shares available")
    print(f"Position: {validation['position']:.2f}, Pending: {validation['pending_sells']:.2f}")
```

## Cross-Reference to Data API

For detailed position tracking with PnL, use the Data API.

**See:** [../data-analytics/positions-and-history.md](../data-analytics/positions-and-history.md)

### When to Use Each API

| Need | Use | Why |
|------|-----|-----|
| Quick position check | CLOB API | Fast, simple |
| Detailed PnL | Data API | Rich analytics |
| Pre-order validation | CLOB + On-chain | Accurate availability |
| Historical positions | Data API | Complete history |

### Data API Position Query

```python
import requests

DATA_API_URL = "https://data-api.polymarket.com"

def get_detailed_positions(wallet_address: str) -> list:
    """Get detailed positions with PnL from Data API.

    See: ../data-analytics/positions-and-history.md for full documentation.
    """
    response = requests.get(
        f"{DATA_API_URL}/positions",
        params={
            "user": wallet_address,
            "sortBy": "CASHPNL",
            "sortDirection": "DESC",
            "sizeThreshold": 1
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
positions = get_detailed_positions(wallet_address)
for p in positions[:5]:
    print(f"{p['title'][:40]}...")
    print(f"  Size: {p['size']}, PnL: ${p['cashPnl']:+.2f}")
```

## Complete Validation Example

```python
from py_clob_client.client import ClobClient
from web3 import Web3

class TradingValidator:
    """Validate trading requirements before placing orders."""

    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    POLYGON_RPC = "https://polygon-rpc.com"

    def __init__(self, client: ClobClient, wallet_address: str):
        self.client = client
        self.wallet = wallet_address
        self.web3 = Web3(Web3.HTTPProvider(self.POLYGON_RPC))

    def get_usdc_balance(self) -> float:
        """Get USDC.e balance."""
        abi = [{"name": "balanceOf", "inputs": [{"type": "address"}],
                "outputs": [{"type": "uint256"}], "type": "function"}]
        contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(self.USDC_E), abi=abi
        )
        raw = contract.functions.balanceOf(
            Web3.to_checksum_address(self.wallet)
        ).call()
        return raw / 1e6

    def get_position(self, token_id: str) -> float:
        """Get position size for a token."""
        try:
            positions = self.client.get_positions(asset_id=token_id)
            return sum(float(p.get("size", 0)) for p in positions)
        except:
            return 0.0

    def get_pending_orders_size(self, token_id: str, side: str) -> float:
        """Get total pending order size for a token/side."""
        orders = self.client.get_orders(state="LIVE")
        return sum(
            float(o.get("original_size", 0)) - float(o.get("size_matched", 0))
            for o in orders
            if o.get("asset_id") == token_id and o.get("side") == side
        )

    def validate_buy(self, price: float, size: float) -> dict:
        """Validate a BUY order."""
        required = price * size
        balance = self.get_usdc_balance()

        return {
            "valid": balance >= required,
            "type": "BUY",
            "required_usdc": required,
            "available_usdc": balance,
            "message": "OK" if balance >= required else f"Need ${required - balance:.2f} more"
        }

    def validate_sell(self, token_id: str, size: float) -> dict:
        """Validate a SELL order."""
        position = self.get_position(token_id)
        pending = self.get_pending_orders_size(token_id, "SELL")
        available = position - pending

        return {
            "valid": available >= size,
            "type": "SELL",
            "position": position,
            "pending_sells": pending,
            "available": available,
            "message": "OK" if available >= size else f"Only {available:.2f} shares available"
        }

    def validate_order(self, token_id: str, price: float, size: float, side: str) -> dict:
        """Validate any order before placement."""
        if side.upper() == "BUY":
            return self.validate_buy(price, size)
        else:
            return self.validate_sell(token_id, size)

# Usage
validator = TradingValidator(client, wallet_address)

# Before BUY
buy_check = validator.validate_order(token_id, price=0.45, size=100, side="BUY")
print(f"BUY validation: {buy_check['message']}")

# Before SELL
sell_check = validator.validate_order(token_id, price=0.55, size=50, side="SELL")
print(f"SELL validation: {sell_check['message']}")
```

## Common Issues

### Issue: Balance Shows $0.00

**Causes:**
1. Checking wrong address (EOA vs funder for proxy wallets)
2. Have native USDC instead of USDC.e
3. Wrong network (mainnet Ethereum vs Polygon)

**Solution:**
```python
# Check both addresses
print(f"EOA balance: ${get_usdc_balance(eoa_address):.2f}")
print(f"Funder balance: ${get_usdc_balance(funder_address):.2f}")

# Verify you're on Polygon
web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
chain_id = web3.eth.chain_id
print(f"Chain ID: {chain_id}")  # Should be 137 for Polygon
```

### Issue: USDC vs USDC.e Confusion

| Token | Address | Decimals | Use |
|-------|---------|----------|-----|
| USDC.e (bridged) | 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 | 6 | Polymarket trading |
| Native USDC | 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359 | 6 | NOT for Polymarket |

**If you have native USDC:** Swap to USDC.e on a DEX (Uniswap, QuickSwap).

### Issue: Position Not Updating After Trade

**Cause:** Position data may cache. CLOB positions update faster than Data API.

**Solution:**
```python
import time

def get_position_with_retry(client, token_id: str, expected_change: float, max_wait: int = 30):
    """Wait for position to reflect expected change."""
    initial = get_clob_positions(client, asset_id=token_id)
    initial_size = sum(float(p.get("size", 0)) for p in initial)

    start = time.time()
    while (time.time() - start) < max_wait:
        current = get_clob_positions(client, asset_id=token_id)
        current_size = sum(float(p.get("size", 0)) for p in current)

        if abs((current_size - initial_size) - expected_change) < 0.01:
            return current

        time.sleep(2)

    return current  # Return latest even if not matching expected
```

## Related Documentation

- [Order Placement](./order-placement.md) - Place orders after validation
- [Order Management](./order-management.md) - Manage existing orders
- [Authentication](../auth/) - Set up trading wallet
- [Data Analytics - Positions](../data-analytics/positions-and-history.md) - Detailed PnL tracking

## References

- [Polymarket CLOB API](https://docs.polymarket.com/developers/CLOB) - Official documentation
- [USDC.e on PolygonScan](https://polygonscan.com/token/0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174) - Token contract
