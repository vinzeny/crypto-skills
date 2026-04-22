# Polymarket Client Initialization Guide

## Overview

The `ClobClient` is your main interface for interacting with the Polymarket CLOB API. This guide covers complete initialization for all wallet types, from installation to verification.

**What you'll accomplish:**
- Install required packages
- Initialize ClobClient with correct parameters for your wallet type
- Set up token allowances (EOA wallets only)
- Create API credentials
- Verify everything works

**Time required:** 5-15 minutes (plus transaction confirmation time for EOA setup)

## Prerequisites

Before you begin:
- **Python 3.9+** installed
- **Private key** for your wallet
- **Polygon RPC endpoint** (e.g., `https://polygon-rpc.com`)
- **POL/MATIC for gas** (EOA wallets only, ~0.1 POL)
- **USDC.e** (not native USDC!) - see [Token Allowances Guide](./token-allowances.md)

## Installation

Install the required Python packages:

```bash
pip install py-clob-client web3
```

**Package versions:**
- `py-clob-client`: 0.34.5+ (latest recommended)
- `web3`: 6.14.0+ (for Polygon compatibility)

## Quick Start by Wallet Type

Choose your path based on wallet type:

### EOA Wallet (MetaMask, Hardware Wallet)

**Complete example:**

```python
from py_clob_client.client import ClobClient
import os

# Configuration
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon mainnet
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

# Initialize client
client = ClobClient(
    host=HOST,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    signature_type=0,  # EOA wallet
    funder=WALLET_ADDRESS  # Same as wallet address
)

# Create and set API credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)

# Verify setup
print("Client initialized successfully!")
print(f"Balance check: {client.get_ok()}")
```

**Next steps for EOA:**
1. Set token allowances (one-time) - see [Token Allowances Guide](./token-allowances.md)
2. Verify setup with test API call

### Magic/Email Wallet

**Complete example:**

```python
from py_clob_client.client import ClobClient
import os

# Configuration
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon mainnet
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")  # Magic wallet EOA key
PROXY_ADDRESS = os.getenv("PROXY_ADDRESS")  # Where funds actually sit

# Initialize client
client = ClobClient(
    host=HOST,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    signature_type=1,  # Magic/email wallet
    funder=PROXY_ADDRESS  # Proxy address, NOT EOA
)

# Create and set API credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)

# Verify setup
print("Client initialized successfully!")
print(f"Balance check: {client.get_ok()}")
```

**Finding your proxy address:**
1. Log in to polymarket.com
2. Go to your profile
3. The address shown is your proxy address (different from your EOA)

### Gnosis Safe

**Complete example:**

```python
from py_clob_client.client import ClobClient
import os

# Configuration
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon mainnet
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")  # Safe signer key
SAFE_ADDRESS = os.getenv("SAFE_ADDRESS")  # Safe contract address

# Initialize client
client = ClobClient(
    host=HOST,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    signature_type=2,  # Gnosis Safe
    funder=SAFE_ADDRESS  # Safe contract address
)

# Create and set API credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)

# Verify setup
print("Client initialized successfully!")
print(f"Balance check: {client.get_ok()}")
```

## ClobClient Parameters Reference

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `host` | `str` | API endpoint URL | `"https://clob.polymarket.com"` |
| `key` | `str` | Private key (with or without `0x` prefix) | `"0x123abc..."` or `"123abc..."` |
| `chain_id` | `int` | Blockchain network ID (137 = Polygon mainnet) | `137` |
| `signature_type` | `int` | Wallet architecture type (0=EOA, 1=Magic, 2=Safe) | `0`, `1`, or `2` |
| `funder` | `str` | Address where funds are held | Varies by wallet type |

### Signature Type Selection

| `signature_type` | Wallet Type | When to Use |
|------------------|-------------|-------------|
| `0` | EOA (Externally Owned Account) | MetaMask, hardware wallets, direct private key control |
| `1` | Proxy Wallet (Magic/Email) | Polymarket email login, Magic Link wallets |
| `2` | Gnosis Safe | Multi-signature wallets, organizational accounts |

**How to determine your wallet type:** See [Wallet Types Guide](./wallet-types.md)

### Funder Parameter

The `funder` parameter specifies where your funds (USDC.e) are located:

| Wallet Type | Funder Value |
|-------------|--------------|
| **EOA** | Same as your wallet address (signing key == funding address) |
| **Magic/Email** | Proxy contract address (different from EOA, found in Polymarket profile) |
| **Gnosis Safe** | Safe contract address |

**Common mistake:** Using EOA address for `funder` when funds are in a proxy wallet results in "$0.00 balance" even though you have USDC.e.

## Complete Setup Flow

Follow these steps for a complete, verified setup:

### Step 1: Determine Your Wallet Type

**Check if you have an EOA or proxy wallet:**

```python
from web3 import Web3

# Your EOA address (from private key)
eoa_address = Web3().eth.account.from_key(PRIVATE_KEY).address

# Your Polymarket profile address (from polymarket.com profile)
profile_address = "0x..."  # Get from Polymarket UI

# Compare
if eoa_address.lower() == profile_address.lower():
    print("You have an EOA wallet")
    signature_type = 0
    funder = eoa_address
else:
    print("You have a proxy wallet")
    signature_type = 1  # or 2 for Gnosis Safe
    funder = profile_address
```

**See also:** [Wallet Types Detection Guide](./wallet-types.md)

### Step 2: Set Token Allowances (EOA Only)

**If you have an EOA wallet, you MUST set token allowances before trading.**

Proxy wallets skip this step - allowances are handled automatically.

```python
from web3 import Web3
from web3.middleware import geth_poa_middleware

def setup_eoa_allowances(private_key: str, wallet_address: str):
    """
    One-time setup for EOA wallets.
    Sets unlimited allowances for USDC.e and CTF tokens.
    """
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Contract addresses
    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    CTF = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

    EXCHANGES = [
        "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",  # CTF Exchange
        "0xC5d563A36AE78145C45a50134d48A1215220f80a",  # Neg Risk Exchange
        "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296",  # Neg Risk Adapter
    ]

    # ABIs for approve and setApprovalForAll
    erc20_abi = '''[{
        "name": "approve",
        "type": "function",
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "outputs": [{"type": "bool"}]
    }]'''

    erc1155_abi = '''[{
        "name": "setApprovalForAll",
        "type": "function",
        "inputs": [
            {"name": "operator", "type": "address"},
            {"name": "approved", "type": "bool"}
        ],
        "outputs": []
    }]'''

    usdc = web3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=erc20_abi)
    ctf = web3.eth.contract(address=Web3.to_checksum_address(CTF), abi=erc1155_abi)

    nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(wallet_address))
    max_approval = 2**256 - 1

    print("Setting up token allowances (6 transactions)...")

    for exchange in EXCHANGES:
        # Approve USDC.e
        tx = usdc.functions.approve(
            Web3.to_checksum_address(exchange),
            max_approval
        ).build_transaction({
            "chainId": 137,
            "from": Web3.to_checksum_address(wallet_address),
            "nonce": nonce,
            "gas": 100000,
        })
        signed = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
        nonce += 1

        # Approve CTF tokens
        tx = ctf.functions.setApprovalForAll(
            Web3.to_checksum_address(exchange),
            True
        ).build_transaction({
            "chainId": 137,
            "from": Web3.to_checksum_address(wallet_address),
            "nonce": nonce,
            "gas": 100000,
        })
        signed = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
        nonce += 1

    print("Allowances set successfully!")

# Run once per EOA wallet
if signature_type == 0:  # EOA wallet
    setup_eoa_allowances(PRIVATE_KEY, WALLET_ADDRESS)
```

**See also:** [Token Allowances Complete Guide](./token-allowances.md)

### Step 3: Initialize ClobClient

```python
from py_clob_client.client import ClobClient

client = ClobClient(
    host="https://clob.polymarket.com",
    key=PRIVATE_KEY,
    chain_id=137,
    signature_type=signature_type,  # From Step 1
    funder=funder  # From Step 1
)

print("ClobClient initialized")
```

### Step 4: Create API Credentials

```python
# Create or retrieve API credentials
creds = client.create_or_derive_api_creds()

# Apply credentials to client
client.set_api_creds(creds)

print("API credentials created and set")
print(f"API Key: {creds['apiKey'][:10]}...")
```

**Credential storage:** Save these credentials securely for future use. See [API Credentials Guide](./api-credentials.md)

### Step 5: Verify Setup

```python
def verify_client_setup(client: ClobClient):
    """
    Test the client connection and credentials.
    """
    try:
        # Test 1: Check API connectivity
        ok_response = client.get_ok()
        print(f"API Status: {ok_response}")

        # Test 2: Get tick size (tests authentication)
        tick_size = client.get_tick_size("71321045679252212594626385532706912750332728571942532289631379312455583992563")
        print(f"Tick Size: {tick_size}")

        # Test 3: Get your orders (tests full auth flow)
        orders = client.get_orders()
        print(f"Active orders: {len(orders)}")

        print("\n✓ Setup verified - client is working correctly!")
        return True

    except Exception as e:
        print(f"\n✗ Setup verification failed: {e}")
        return False

# Verify everything works
verify_client_setup(client)
```

**Expected output:**
```
API Status: {'status': 'ok'}
Tick Size: 0.01
Active orders: 0
✓ Setup verified - client is working correctly!
```

## Environment Configuration

### Recommended .env File Pattern

Create a `.env` file in your project root:

```bash
# Wallet Configuration
POLYMARKET_PRIVATE_KEY=0x...
WALLET_ADDRESS=0x...  # EOA address
PROXY_ADDRESS=0x...  # Only needed for Magic/email wallets

# Network Configuration
POLYGON_RPC_URL=https://polygon-rpc.com

# API Credentials (optional - can be generated)
POLY_API_KEY=...
POLY_SECRET=...
POLY_PASSPHRASE=...
POLY_NONCE=...  # For credential recovery
```

**Security:** Add `.env` to `.gitignore` to prevent committing credentials.

### Loading Environment Variables

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PROXY_ADDRESS = os.getenv("PROXY_ADDRESS")  # If applicable
```

**Install python-dotenv:**
```bash
pip install python-dotenv
```

## Verification

### How to Verify Client is Working

After initialization, verify your setup:

#### Test 1: API Connectivity

```python
response = client.get_ok()
# Expected: {'status': 'ok'}
```

#### Test 2: Tick Size Query

```python
# Query a known market for tick size
tick_size = client.get_tick_size("71321045679252212594626385532706912750332728571942532289631379312455583992563")
# Expected: 0.01 (or similar value)
```

#### Test 3: Get Orders

```python
orders = client.get_orders()
# Expected: List of your orders (may be empty if no trades yet)
print(f"Found {len(orders)} orders")
```

#### Test 4: Get Market Data

```python
# Get market information
markets = client.get_markets()
print(f"Found {len(markets)} markets")
```

### Expected Responses

**Successful initialization should produce:**
- ✓ `get_ok()` returns `{'status': 'ok'}`
- ✓ `get_tick_size()` returns a numeric value
- ✓ `get_orders()` returns a list (may be empty)
- ✓ No 400/401 errors

**If you see errors, check:**
- Correct `signature_type` for your wallet
- Correct `funder` address (EOA vs proxy)
- API credentials set properly
- Token allowances (EOA wallets)

## Troubleshooting

### Error: "Invalid signature" (400)

**Cause:** Wrong `signature_type` for your wallet architecture

**Solution:**
1. Verify your wallet type using detection code in Step 1
2. Ensure `signature_type` matches:
   - `0` for EOA wallets
   - `1` for Magic/email wallets
   - `2` for Gnosis Safe

**See:** [Wallet Types Detection Guide](./wallet-types.md)

### Error: "Unauthorized/Invalid api key" (401)

**Cause:** API credentials not set or expired

**Solution:**
```python
# Regenerate credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
```

**See:** [API Credentials Troubleshooting](./api-credentials.md#troubleshooting)

### Error: "Invalid L1 Request headers" (401)

**Cause:** Malformed initialization parameters

**Solutions:**
1. Check `funder` parameter:
   - EOA: Use wallet address
   - Proxy: Use proxy address (NOT EOA)
2. Verify private key format (must be valid hex, with or without `0x`)
3. Ensure `chain_id=137` for Polygon mainnet

**See:** [Authentication Flow Errors](./authentication-flow.md#common-authentication-errors)

### Error: Balance shows $0.00

**Possible causes:**
1. **Wrong USDC type:** You have native USDC instead of USDC.e
2. **Wrong funder address:** Using EOA address when funds are in proxy

**Diagnosis:**
```python
from web3 import Web3

def check_usdc_balance(address: str):
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    abi = '''[{
        "name": "balanceOf",
        "type": "function",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"type": "uint256"}]
    }]'''

    contract = web3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=abi)
    balance = contract.functions.balanceOf(Web3.to_checksum_address(address)).call()

    print(f"USDC.e balance: ${balance / 1e6:.2f}")
    return balance

# Check balance on the address used in 'funder' parameter
check_usdc_balance(funder)
```

**See:** [Token Allowances Guide - USDC.e Detection](./token-allowances.md#usdc-e-vs-native-usdc-critical-distinction)

### Error: Order placement fails after successful authentication

**Cause:** Missing token allowances (EOA wallets only)

**Solution:**
```python
# Check if allowances are set
from web3 import Web3

def check_allowances(wallet_address: str):
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

    abi = '''[{
        "name": "allowance",
        "type": "function",
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "outputs": [{"type": "uint256"}]
    }]'''

    contract = web3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=abi)
    allowance = contract.functions.allowance(
        Web3.to_checksum_address(wallet_address),
        Web3.to_checksum_address(EXCHANGE)
    ).call()

    if allowance > 0:
        print(f"Allowance set: {allowance}")
    else:
        print("Allowance NOT set - run setup_eoa_allowances()")

check_allowances(WALLET_ADDRESS)
```

**See:** [Token Allowances Complete Setup](./token-allowances.md)

## Complete Working Example

Putting it all together:

```python
from py_clob_client.client import ClobClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_polymarket_client():
    """
    Complete initialization example with all checks.
    """
    # Configuration
    HOST = "https://clob.polymarket.com"
    CHAIN_ID = 137
    PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")

    # Step 1: Determine wallet type
    from web3 import Web3
    eoa_address = Web3().eth.account.from_key(PRIVATE_KEY).address

    # Get profile address from environment or Polymarket UI
    profile_address = os.getenv("PROXY_ADDRESS") or eoa_address

    if eoa_address.lower() == profile_address.lower():
        signature_type = 0  # EOA
        funder = eoa_address
        print(f"Wallet type: EOA ({eoa_address})")
    else:
        signature_type = 1  # Proxy (Magic/email)
        funder = profile_address
        print(f"Wallet type: Proxy (EOA: {eoa_address}, Proxy: {funder})")

    # Step 2: Initialize client
    client = ClobClient(
        host=HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=signature_type,
        funder=funder
    )
    print("ClobClient initialized")

    # Step 3: Create API credentials
    try:
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        print(f"API credentials set (key: {creds['apiKey'][:10]}...)")
    except Exception as e:
        print(f"Credential creation failed: {e}")
        raise

    # Step 4: Verify setup
    try:
        ok = client.get_ok()
        orders = client.get_orders()
        print(f"✓ Setup verified - API status: {ok}, orders: {len(orders)}")
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        raise

    return client

if __name__ == "__main__":
    client = initialize_polymarket_client()
    print("Ready to trade!")
```

## Next Steps

After successful client initialization:

1. **Start trading** - Place your first order
2. **Monitor markets** - Subscribe to market data updates
3. **Manage positions** - Track and close positions
4. **Set up strategies** - Implement automated trading logic

## Related Documentation

- [Wallet Types Detection](./wallet-types.md) - Determine your wallet type and correct configuration
- [Authentication Flow](./authentication-flow.md) - Understanding L1/L2 authentication architecture
- [API Credentials Management](./api-credentials.md) - Creating, storing, and recovering credentials
- [Token Allowances Setup](./token-allowances.md) - USDC.e allowances and troubleshooting

## References

- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client) - Official Python client library
- [Polymarket Documentation](https://docs.polymarket.com/developers/CLOB/authentication) - Official API documentation
- [Polymarket Market Makers Guide](https://docs.polymarket.com/developers/market-makers/setup) - Setup workflow
