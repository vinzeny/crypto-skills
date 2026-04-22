# USDC.e vs Native USDC Confusion

**Edge Case ID:** EDGE-01

The most common funding issue on Polymarket: depositing the wrong USDC token. This guide helps you diagnose and resolve the problem.

## Symptoms

- Polygon wallet (MetaMask, etc.) shows USDC balance
- Polymarket balance shows $0.00
- Recently withdrew "USDC" from an exchange to Polygon
- Funds appear "lost" but are actually in the wrong token

## Root Cause

Polygon has **two different USDC tokens**, and Polymarket only accepts one:

| Token | Contract Address | Polymarket Status |
|-------|------------------|-------------------|
| **USDC.e (Bridged)** | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | **CORRECT** - Required |
| **Native USDC** | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` | **WRONG** - Not supported |

### Why This Happens

1. **Historical context:** USDC.e was the original USDC on Polygon (bridged from Ethereum)
2. **Native USDC launch:** Circle later deployed official "Native USDC" on Polygon
3. **Exchange defaults:** Most exchanges (Coinbase, Binance, Kraken) now default to Native USDC for Polygon withdrawals
4. **Polymarket decision:** Polymarket still uses USDC.e exclusively

**Both tokens show as "USDC" in wallet interfaces** - there's no visual distinction without checking contract addresses.

## Diagnosis

### Quick Check Function

Use this to determine which token you have:

```python
from web3 import Web3

def check_usdc_balances(wallet_address: str) -> dict:
    """
    Check which USDC variant exists in wallet.

    Args:
        wallet_address: The address to check

    Returns:
        Dictionary with balance info and recommended action
    """
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

    # Determine status and action
    if balance_e > 0:
        status = "Ready to trade"
        action = "None - you have the correct token"
    elif balance_native > 0:
        status = "Need to swap tokens"
        action = "Swap Native USDC to USDC.e (see solutions below)"
    else:
        status = "No USDC found"
        action = "Deposit USDC.e to your wallet"

    return {
        "usdc_e_balance": balance_e_formatted,
        "usdc_native_balance": balance_native_formatted,
        "status": status,
        "action": action,
        "has_correct_token": balance_e > 0,
        "needs_swap": balance_native > 0 and balance_e == 0
    }
```

### Example Usage

```python
result = check_usdc_balances("0xYourWalletAddress")

print(f"USDC.e (Polymarket): ${result['usdc_e_balance']:.2f}")
print(f"Native USDC (wrong): ${result['usdc_native_balance']:.2f}")
print(f"Status: {result['status']}")
print(f"Action: {result['action']}")

# Common output when issue exists:
# USDC.e (Polymarket): $0.00
# Native USDC (wrong): $500.00
# Status: Need to swap tokens
# Action: Swap Native USDC to USDC.e (see solutions below)
```

### Manual Verification (PolygonScan)

1. Go to [PolygonScan](https://polygonscan.com/)
2. Enter your wallet address
3. Click "Token Holdings" dropdown
4. Look for USDC entries
5. Check which contract address your USDC is from:
   - `0x2791Bca1...` = USDC.e (correct)
   - `0x3c499c54...` = Native USDC (wrong)

## Solutions

### Solution 1: Polymarket UI "Activate Funds" (Easiest)

Polymarket's UI can automatically swap Native USDC to USDC.e:

1. Log in to [polymarket.com](https://polymarket.com)
2. Look for an "Activate Funds" or similar prompt
3. Polymarket will initiate a swap transaction
4. Approve the transaction in your wallet
5. Wait for confirmation (~10-30 seconds)

**Note:** This may not be available in all regions or for all account types.

### Solution 2: Manual DEX Swap

Swap Native USDC to USDC.e on a decentralized exchange:

**Using QuickSwap:**
1. Go to [QuickSwap](https://quickswap.exchange/)
2. Connect your wallet
3. Select swap:
   - From: USDC (`0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`)
   - To: USDC.e (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`)
4. Enter amount
5. Approve and swap
6. Rate is typically 1:1 (check before confirming)

**Using Uniswap:**
1. Go to [Uniswap](https://app.uniswap.org/)
2. Switch to Polygon network
3. Same swap process as QuickSwap

**Gas cost:** ~0.01-0.02 POL (MATIC)

### Solution 3: Correct Deposit Next Time

Prevent this issue on future deposits:

**Option A: Check exchange withdrawal options**
- Some exchanges offer both USDC.e and Native USDC
- Select USDC.e explicitly if available
- Check the contract address shown before confirming withdrawal

**Option B: Bridge through Ethereum**
1. Withdraw USDC to Ethereum mainnet
2. Use the official Polygon Bridge to bridge to Polygon
3. This always results in USDC.e

**Option C: Use exchanges that default to USDC.e**
- Check current exchange behavior before each withdrawal
- Exchange defaults change over time

## After Getting USDC.e

Once you have USDC.e, you still need to set up token allowances before trading:

```python
# Check if allowances are set
from skills.polymarket.auth.token_allowances import check_polymarket_allowances

result = check_polymarket_allowances("0xYourAddress")
if not result['summary']['all_approved']:
    print("Run setup_polymarket_allowances() before trading")
```

See [Token Allowances](../auth/token-allowances.md) for complete setup instructions.

## Contract Reference

| Contract | Address | Purpose |
|----------|---------|---------|
| USDC.e (correct) | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | Polymarket trading |
| Native USDC (wrong) | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` | Not supported |

## Related Issues

| Error | This Guide Helps? | See Also |
|-------|-------------------|----------|
| "Balance shows $0.00" | Yes | - |
| "insufficient balance" | Maybe | Also check order size vs actual balance |
| "not enough balance / allowance" | Maybe | Also check [Token Allowances](../auth/token-allowances.md) |
| "transfer amount exceeds allowance" | No | [Token Allowances](../auth/token-allowances.md) |

## Navigation

- [Back to Edge Cases Index](./README.md)
- [Token Allowances Setup](../auth/token-allowances.md)
- [Authentication Overview](../auth/README.md)
