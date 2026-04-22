# Polymarket Wallet Types: Detection and Configuration

## Overview

Polymarket supports three wallet architectures, each requiring different configuration parameters when initializing the API client. Using the wrong `signature_type` or `funder` parameter is the most common cause of authentication failures.

**Why this matters:**
- Wrong `signature_type` → "Invalid signature" (400) or "Unauthorized/Invalid api key" (401) errors
- Wrong `funder` address → Orders fail even after successful authentication
- Checking allowances on the wrong address → Confusion about token setup

This guide helps you identify your wallet type and configure the client correctly.

## Wallet Type Reference

| Wallet Type | signature_type | funder Parameter | Common Use Cases |
|-------------|----------------|------------------|------------------|
| **EOA (Externally Owned Account)** | `0` | Your wallet address (same as signing key) | MetaMask, hardware wallets, direct private key control |
| **Proxy Wallet (Magic/Email)** | `1` | Proxy contract address (different from signing key) | Polymarket.com email login, Magic Link wallets |
| **Gnosis Safe** | `2` | Safe contract address | Multi-signature wallets, organizational accounts |

## Detection Method

### Quick Check: Compare Your Addresses

**Step 1: Find your EOA address**
- MetaMask: Copy address from wallet
- Hardware wallet: Check device display
- Private key: Derive using `web3.eth.account.from_key(private_key).address`

**Step 2: Find your Polymarket profile address**
- Go to polymarket.com and log in
- Click profile → Your profile address appears in the URL or profile section
- Or use the Polymarket API to query your profile

**Step 3: Compare**

```python
def detect_wallet_type(eoa_address: str, profile_address: str) -> tuple[int, str]:
    """
    Determine signature_type and funder based on address comparison.

    Returns:
        (signature_type, funder_address)
    """
    if eoa_address.lower() == profile_address.lower():
        # Addresses match → Direct EOA wallet
        return (0, eoa_address)
    else:
        # Addresses differ → Proxy wallet
        # Your EOA controls the proxy, but funds sit in the proxy
        return (1, profile_address)
```

### Decision Tree

```
Do you control the private key directly?
├─ YES → Do you log in to Polymarket with email/Magic Link?
│  ├─ NO → EOA wallet (signature_type=0, funder=your_address)
│  └─ YES → Proxy wallet (signature_type=1, funder=proxy_address)
└─ NO → Multi-sig/Gnosis Safe (signature_type=2, funder=safe_address)
```

## Proxy Wallet Architecture

### How Proxy Wallets Work

Proxy wallets use a **two-address architecture**:

1. **Signing Key (EOA)**: The private key you control
   - Signs API requests and transactions
   - Does NOT hold funds
   - Used for `key` parameter in client initialization

2. **Funding Address (Proxy Contract)**: Where your funds actually live
   - Deployed smart contract wallet
   - Holds USDC.e and positions
   - Used for `funder` parameter in client initialization

**Why this design?**
- Security: Your private key can be rotated without moving funds
- Gas abstraction: Proxy handles complex operations
- Compatibility: Works with email/social login (Magic Link)

### Finding Your Proxy Address

**Method 1: Polymarket UI (Recommended)**
1. Log in to polymarket.com
2. Go to your profile
3. The address shown is your proxy address (if different from EOA)

**Method 2: Derive Using CREATE2 (Advanced)**

Polymarket uses deterministic proxy deployment. TypeScript implementation available:

```typescript
// Source: https://github.com/Polymarket/magic-proxy-builder-example
import { keccak256, getCreate2Address, encodePacked } from "viem";

const PROXY_FACTORY = "0xaB45c5A4B0c941a2F231C04C3f49182e1A254052";
const PROXY_INIT_CODE_HASH = "0x..."; // Proxy bytecode hash

export function deriveProxyAddress(eoaAddress: string): string {
  return getCreate2Address({
    bytecodeHash: PROXY_INIT_CODE_HASH,
    from: PROXY_FACTORY,
    salt: keccak256(encodePacked(["address"], [eoaAddress])),
  });
}
```

**Python Note:** No official Python implementation exists for proxy derivation. Use the Polymarket UI or the TypeScript library.

## Client Initialization Examples

### EOA Wallet

```python
from py_clob_client.client import ClobClient

# Your EOA address (MetaMask, hardware wallet, etc.)
private_key = "0x..."
wallet_address = "0xYourEOAAddress"

client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,  # Polygon mainnet
    signature_type=0,  # EOA
    funder=wallet_address  # Same as EOA address
)
```

### Proxy Wallet (Email/Magic)

```python
from py_clob_client.client import ClobClient

# Your signing key (EOA that controls the proxy)
private_key = "0x..."

# Your proxy contract address (different from EOA)
proxy_address = "0xYourProxyAddress"

client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,  # Polygon mainnet
    signature_type=1,  # Proxy wallet
    funder=proxy_address  # Proxy address, NOT EOA address
)
```

### Gnosis Safe

```python
from py_clob_client.client import ClobClient

# Safe signer key
private_key = "0x..."

# Gnosis Safe contract address
safe_address = "0xYourSafeAddress"

client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,  # Polygon mainnet
    signature_type=2,  # Gnosis Safe
    funder=safe_address  # Safe contract address
)
```

## Common Errors and Solutions

### Error: "Invalid signature" (400)

**Cause:** Wrong `signature_type` for your wallet architecture

**Solution:**
1. Verify your wallet type using the detection method above
2. Ensure `signature_type` matches:
   - `0` for EOA
   - `1` for Proxy/Magic wallets
   - `2` for Gnosis Safe

### Error: Using EOA address for proxy wallet funder

**Symptom:** Authentication succeeds, but orders fail or balance shows $0.00

**Cause:** Using `funder=eoa_address` when funds are in proxy contract

**Solution:**
1. Find your proxy address (see "Finding Your Proxy Address" above)
2. Update client initialization: `funder=proxy_address`

### Error: Checking allowances on wrong address

**Symptom:** Token allowances appear missing even after setting them

**Cause:** Checking allowances on EOA instead of proxy address

**Solution:**
- For EOA wallets: Check allowances on your EOA address
- For proxy wallets: Check allowances on your proxy address (where funds actually sit)
- See [token-allowances.md](./token-allowances.md) for allowance setup

### Error: Orders fail after successful authentication

**Symptom:** API credentials work, but trade submission fails

**Possible causes:**
1. Wrong `funder` address (using EOA instead of proxy)
2. Missing token allowances (EOA wallets only - see [token-allowances.md](./token-allowances.md))
3. Insufficient USDC.e balance (check correct token type)

## Next Steps

After determining your wallet type:

1. **Initialize the client** with correct `signature_type` and `funder`
2. **Set up token allowances** (EOA wallets only) - see [token-allowances.md](./token-allowances.md)
3. **Verify your setup** by checking API key creation and balance visibility

## References

- Polymarket Wallet Detection: Based on address comparison logic
- Proxy Architecture: CREATE2 deterministic deployment pattern
- Signature Types: Polymarket API client specification
