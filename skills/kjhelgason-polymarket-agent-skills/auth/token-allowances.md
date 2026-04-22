# Polymarket Token Allowances: USDC.e Setup Guide

## Overview

Before trading on Polymarket with an EOA wallet, you must approve two types of tokens for the exchange contracts:

1. **USDC.e (ERC-20)**: The stablecoin used for trading
2. **Conditional Token Framework (ERC-1155)**: The prediction market positions

**Who needs this?**
- **EOA wallets (MetaMask, hardware wallets)**: YES - must set allowances manually
- **Proxy wallets (Magic/email login)**: NO - allowances handled automatically
- **Gnosis Safe**: Depends on Safe configuration

**Why this matters:**
Skipping allowance setup is the second most common cause of setup failures. Symptoms include:
- Successful authentication but orders fail
- Balance shows $0.00 in Polymarket even though Polygon wallet shows USDC
- Errors: "insufficient allowance" or "transfer amount exceeds allowance"

## USDC.e vs Native USDC: Critical Distinction

### The Two USDC Tokens on Polygon

| Token | Contract Address | Status on Polymarket |
|-------|------------------|----------------------|
| **USDC.e (Bridged)** | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | **CORRECT** - Required for trading |
| **Native USDC** | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` | **WRONG** - Not supported |

### Why Confusion Exists

**Historical context:**
- USDC.e was the original USDC on Polygon (bridged from Ethereum)
- Native USDC launched later as Circle's official Polygon deployment
- Most exchanges (Coinbase, Binance) now default to native USDC for Polygon deposits
- Polymarket still uses USDC.e exclusively

**Common scenario:**
1. User withdraws "USDC" from exchange to Polygon
2. Receives native USDC (0x3c49...)
3. Polygon wallet shows USDC balance
4. Polymarket shows $0.00
5. User thinks funds are lost

### Detecting Which Token You Have

```python
from web3 import Web3

def check_usdc_balances(wallet_address: str) -> dict:
    """
    Check which USDC variant exists in wallet.

    Args:
        wallet_address: The address to check (EOA or proxy, depending on wallet type)

    Returns:
        Dictionary with balance info and recommended action
    """
    # Connect to Polygon
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

    # Contract addresses
    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    USDC_NATIVE = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"

    # ERC-20 ABI (balanceOf function)
    erc20_abi = '''[{
        "name": "balanceOf",
        "type": "function",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "balance", "type": "uint256"}],
        "stateMutability": "view"
    }]'''

    # Get balances
    usdc_e_contract = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_E),
        abi=erc20_abi
    )
    usdc_native_contract = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_NATIVE),
        abi=erc20_abi
    )

    balance_e = usdc_e_contract.functions.balanceOf(
        Web3.to_checksum_address(wallet_address)
    ).call()
    balance_native = usdc_native_contract.functions.balanceOf(
        Web3.to_checksum_address(wallet_address)
    ).call()

    # USDC has 6 decimals
    balance_e_formatted = balance_e / 1e6
    balance_native_formatted = balance_native / 1e6

    # Determine status
    if balance_e > 0:
        status = "Ready to trade"
        action = "None - you have the correct token"
    elif balance_native > 0:
        status = "Need to swap tokens"
        action = "Swap native USDC to USDC.e (see solutions below)"
    else:
        status = "No USDC found"
        action = "Deposit USDC.e to your wallet"

    return {
        "usdc_e_balance": balance_e_formatted,
        "usdc_native_balance": balance_native_formatted,
        "status": status,
        "action": action,
        "has_correct_token": balance_e > 0
    }

# Example usage
result = check_usdc_balances("0xYourAddress")
print(f"USDC.e: ${result['usdc_e_balance']:.2f}")
print(f"Native USDC: ${result['usdc_native_balance']:.2f}")
print(f"Status: {result['status']}")
print(f"Action: {result['action']}")
```

### Solutions for Native USDC Holders

**Option 1: Use Polymarket UI (Easiest)**
1. Log in to polymarket.com
2. Click "Activate Funds" or similar prompt
3. Polymarket automatically swaps native USDC to USDC.e

**Option 2: Manual Swap**
1. Use QuickSwap or Uniswap on Polygon
2. Swap native USDC (`0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`) to USDC.e (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`)
3. Rate is typically 1:1

**Option 3: Deposit Correctly Next Time**
- Check if your exchange offers USDC.e withdrawal option
- Or withdraw to Ethereum, then bridge to Polygon using official bridge

## Required Allowances

### Three Exchange Contracts

Polymarket uses three exchange contracts that all need token approval:

| Contract Name | Address | Purpose |
|---------------|---------|---------|
| **CTF Exchange** | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` | Main conditional token trading |
| **Neg Risk Exchange** | `0xC5d563A36AE78145C45a50134d48A1215220f80a` | Negative risk market trading |
| **Neg Risk Adapter** | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` | Negative risk position handling |

### Two Token Types

Each exchange contract needs approval for:

1. **USDC.e (ERC-20)**: Approve spending using `approve(spender, amount)`
2. **Conditional Token Framework (ERC-1155)**: Approve operator using `setApprovalForAll(operator, approved)`

**Total operations:** 3 exchanges × 2 token types = 6 approval transactions

## Setting Up Allowances

### Prerequisites

Before running the setup:
1. Confirm you have USDC.e (not native USDC) - see detection code above
2. Ensure you have POL (MATIC) for gas fees (0.01-0.1 POL typically sufficient)
3. Have your EOA private key ready

### Complete Setup Code

```python
from web3 import Web3
from web3.middleware import geth_poa_middleware

def setup_polymarket_allowances(private_key: str, wallet_address: str):
    """
    Set unlimited allowances for USDC.e and CTF tokens on all Polymarket exchanges.

    This needs to be run ONCE per EOA wallet. Proxy wallets skip this step.

    Args:
        private_key: Your EOA private key (with 0x prefix)
        wallet_address: Your EOA wallet address

    Requires:
        - USDC.e balance (not native USDC)
        - POL/MATIC for gas fees
    """
    # Connect to Polygon
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Verify connection
    if not web3.is_connected():
        raise Exception("Failed to connect to Polygon RPC")

    # Contract addresses
    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    CTF = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

    EXCHANGES = [
        "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",  # CTF Exchange
        "0xC5d563A36AE78145C45a50134d48A1215220f80a",  # Neg Risk Exchange
        "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296",  # Neg Risk Adapter
    ]

    # ABIs
    erc20_abi = '''[{
        "name": "approve",
        "type": "function",
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "outputs": [{"type": "bool"}],
        "stateMutability": "nonpayable"
    }]'''

    erc1155_abi = '''[{
        "name": "setApprovalForAll",
        "type": "function",
        "inputs": [
            {"name": "operator", "type": "address"},
            {"name": "approved", "type": "bool"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    }]'''

    # Create contract instances
    usdc = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_E),
        abi=erc20_abi
    )
    ctf = web3.eth.contract(
        address=Web3.to_checksum_address(CTF),
        abi=erc1155_abi
    )

    # Get starting nonce
    nonce = web3.eth.get_transaction_count(
        Web3.to_checksum_address(wallet_address)
    )

    # Maximum uint256 for unlimited approval
    max_approval = 2**256 - 1

    print(f"Setting up allowances for {wallet_address}")
    print(f"Starting nonce: {nonce}")
    print(f"This will send 6 transactions (3 exchanges × 2 token types)")

    for i, exchange in enumerate(EXCHANGES, 1):
        exchange_checksum = Web3.to_checksum_address(exchange)

        print(f"\n[{i}/3] Processing exchange: {exchange}")

        # 1. Approve USDC.e spending
        print("  → Approving USDC.e...")
        tx = usdc.functions.approve(
            exchange_checksum,
            max_approval
        ).build_transaction({
            "chainId": 137,
            "from": Web3.to_checksum_address(wallet_address),
            "nonce": nonce,
            "gas": 100000,
            "maxFeePerGas": web3.eth.gas_price,
            "maxPriorityFeePerGas": web3.to_wei(30, "gwei"),
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

        if receipt["status"] == 1:
            print(f"  ✓ USDC.e approved (tx: {tx_hash.hex()})")
        else:
            print(f"  ✗ USDC.e approval failed (tx: {tx_hash.hex()})")
            raise Exception("USDC.e approval failed")

        nonce += 1

        # 2. Approve CTF token operations
        print("  → Approving CTF tokens...")
        tx = ctf.functions.setApprovalForAll(
            exchange_checksum,
            True
        ).build_transaction({
            "chainId": 137,
            "from": Web3.to_checksum_address(wallet_address),
            "nonce": nonce,
            "gas": 100000,
            "maxFeePerGas": web3.eth.gas_price,
            "maxPriorityFeePerGas": web3.to_wei(30, "gwei"),
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

        if receipt["status"] == 1:
            print(f"  ✓ CTF approved (tx: {tx_hash.hex()})")
        else:
            print(f"  ✗ CTF approval failed (tx: {tx_hash.hex()})")
            raise Exception("CTF approval failed")

        nonce += 1

    print("\n✓ All allowances set successfully!")
    print("Your wallet is now ready to trade on Polymarket.")

# Example usage
if __name__ == "__main__":
    PRIVATE_KEY = "0x..."  # Your EOA private key
    WALLET_ADDRESS = "0x..."  # Your EOA address

    setup_polymarket_allowances(PRIVATE_KEY, WALLET_ADDRESS)
```

### Gas Cost Estimate

- Typical cost: 0.01-0.05 POL (MATIC) total for all 6 transactions
- Depends on network congestion
- Ensure you have 0.1 POL to be safe

## Checking Existing Allowances

Before setting up allowances (or to debug issues), check current approval status:

```python
from web3 import Web3

def check_polymarket_allowances(wallet_address: str) -> dict:
    """
    Check if all required allowances are set for Polymarket trading.

    Args:
        wallet_address: Address to check (EOA or proxy, depending on wallet type)

    Returns:
        Dictionary showing allowance status for each exchange
    """
    web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

    # Contract addresses
    USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    CTF = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

    EXCHANGES = {
        "CTF Exchange": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
        "Neg Risk Exchange": "0xC5d563A36AE78145C45a50134d48A1215220f80a",
        "Neg Risk Adapter": "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296",
    }

    # ABIs
    erc20_abi = '''[{
        "name": "allowance",
        "type": "function",
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view"
    }]'''

    erc1155_abi = '''[{
        "name": "isApprovedForAll",
        "type": "function",
        "inputs": [
            {"name": "account", "type": "address"},
            {"name": "operator", "type": "address"}
        ],
        "outputs": [{"type": "bool"}],
        "stateMutability": "view"
    }]'''

    usdc = web3.eth.contract(
        address=Web3.to_checksum_address(USDC_E),
        abi=erc20_abi
    )
    ctf = web3.eth.contract(
        address=Web3.to_checksum_address(CTF),
        abi=erc1155_abi
    )

    results = {}
    all_approved = True

    for name, exchange in EXCHANGES.items():
        exchange_checksum = Web3.to_checksum_address(exchange)
        wallet_checksum = Web3.to_checksum_address(wallet_address)

        # Check USDC.e allowance
        usdc_allowance = usdc.functions.allowance(
            wallet_checksum,
            exchange_checksum
        ).call()

        # Check CTF approval
        ctf_approved = ctf.functions.isApprovedForAll(
            wallet_checksum,
            exchange_checksum
        ).call()

        usdc_ok = usdc_allowance > 0
        needs_setup = not (usdc_ok and ctf_approved)

        results[name] = {
            "address": exchange,
            "usdc_approved": usdc_ok,
            "usdc_allowance": usdc_allowance,
            "ctf_approved": ctf_approved,
            "needs_setup": needs_setup
        }

        if needs_setup:
            all_approved = False

    results["summary"] = {
        "all_approved": all_approved,
        "ready_to_trade": all_approved
    }

    return results

# Example usage
result = check_polymarket_allowances("0xYourAddress")

print("Allowance Status:")
for exchange, status in result.items():
    if exchange == "summary":
        continue
    print(f"\n{exchange}:")
    print(f"  USDC.e: {'✓' if status['usdc_approved'] else '✗'}")
    print(f"  CTF: {'✓' if status['ctf_approved'] else '✗'}")
    print(f"  Status: {'Ready' if not status['needs_setup'] else 'Needs setup'}")

print(f"\nOverall: {'✓ Ready to trade' if result['summary']['all_approved'] else '✗ Setup required'}")
```

## Common Issues and Solutions

### Issue: "Polygon shows USDC, Polymarket shows $0.00"

**Diagnosis:**
```python
result = check_usdc_balances("0xYourAddress")
if result["usdc_native_balance"] > 0 and result["usdc_e_balance"] == 0:
    print("You have native USDC, need USDC.e")
```

**Solution:** Swap native USDC to USDC.e (see "Solutions for Native USDC Holders" above)

### Issue: "Order placement fails after successful authentication"

**Possible causes:**
1. Missing allowances (check with `check_polymarket_allowances`)
2. Wrong wallet address (using EOA when funds are in proxy - see [wallet-types.md](./wallet-types.md))
3. Insufficient USDC.e balance

**Diagnosis:**
```python
# Check allowances
allowances = check_polymarket_allowances("0xYourAddress")
print(f"Allowances set: {allowances['summary']['all_approved']}")

# Check USDC.e balance
balances = check_usdc_balances("0xYourAddress")
print(f"USDC.e balance: ${balances['usdc_e_balance']:.2f}")
```

### Issue: "Transfer amount exceeds allowance"

**Cause:** Allowances not set or expired

**Solution:** Run `setup_polymarket_allowances()` again (safe to run multiple times)

### Issue: "Insufficient POL for gas"

**Cause:** No MATIC in wallet to pay for approval transactions

**Solution:**
1. Bridge POL/MATIC to your Polygon wallet
2. Typically 0.1 POL is sufficient for allowance setup + several trades
3. Get from exchanges or use Polygon bridge

## Who Needs This Setup?

### EOA Wallets: YES

If you're using:
- MetaMask
- Hardware wallet (Ledger, Trezor)
- Direct private key control

**You must run the allowance setup code.**

### Proxy Wallets: NO

If you're using:
- Polymarket email/Magic login
- Social login wallets

**Allowances are handled automatically by the proxy contract.**

See [wallet-types.md](./wallet-types.md) to determine your wallet type.

### Gnosis Safe: Depends

Multi-sig wallets may need manual setup depending on configuration. Check with `check_polymarket_allowances()`.

## Verification Checklist

Before placing your first trade:

- [ ] Confirmed you have USDC.e (not native USDC)
- [ ] Ran `check_usdc_balances()` - shows correct token balance
- [ ] Ran `setup_polymarket_allowances()` - all 6 transactions succeeded
- [ ] Ran `check_polymarket_allowances()` - all exchanges show approved
- [ ] Have POL/MATIC for trade gas fees (keep 0.1+ POL in wallet)

## Contract Reference

### Token Contracts

| Token | Address | Type |
|-------|---------|------|
| USDC.e (Bridged USDC) | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | ERC-20 |
| Conditional Token Framework | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` | ERC-1155 |

### Exchange Contracts

| Exchange | Address | Function |
|----------|---------|----------|
| CTF Exchange | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` | Main trading |
| Neg Risk Exchange | `0xC5d563A36AE78145C45a50134d48A1215220f80a` | Negative risk markets |
| Neg Risk Adapter | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` | Position handling |

All contracts are on Polygon mainnet (Chain ID: 137).

## Security Notes

**Unlimited Approvals:**
The setup code uses `MaxUint256` for unlimited approval. This is standard practice but means:
- Exchanges can spend unlimited USDC.e from your wallet
- Only applies to the three official Polymarket contracts
- You can revoke by calling `approve(exchange, 0)` or `setApprovalForAll(exchange, False)`

**Alternative:** Set exact amounts, but you'll need to reapprove when allowance is exhausted.

## References

- USDC.e Token Contract: Polygon bridged USDC (original)
- Native USDC: Circle's official Polygon deployment (NOT supported)
- Token Allowances: Standard ERC-20/ERC-1155 approval pattern
- Exchange Contracts: Official Polymarket CLOB addresses
