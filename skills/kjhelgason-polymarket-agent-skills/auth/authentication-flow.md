# Polymarket Authentication Flow

## Overview

Polymarket's CLOB API uses a two-tier authentication architecture:

- **L1 Authentication**: Ethereum wallet signatures (EIP-712) used to generate API credentials
- **L2 Authentication**: HMAC-SHA256 signatures for individual API requests

This split allows wallet-based identity verification (L1) while enabling fast, secure API operations (L2) without requiring wallet signatures for every request.

**Key Distinction:**
- **L1** = Wallet-level authentication (one-time or periodic)
- **L2** = Request-level authentication (every API call)

## L1 Authentication (Wallet Signatures)

### Purpose

L1 authentication establishes your identity using your Ethereum wallet. This is used for:

- Generating API credentials (initial setup)
- Creating API keys
- Rotating credentials
- Any operation requiring wallet-level authorization

### Technical Details

**Protocol**: EIP-712 structured data signing

**Domain Separator**: ClobAuthDomain (Polymarket-specific)

**Signature Types**: Three types corresponding to wallet architectures:
- `0` = EOA wallets (MetaMask, hardware wallets, direct private key)
- `1` = Email/Magic wallets (proxy wallet controlled by EOA)
- `2` = Gnosis Safe/proxy wallets (browser wallet proxies)

### When L1 is Used

L1 authentication occurs when:

1. **Initial Setup**: First-time credential generation
2. **Credential Creation**: Calling `create_api_key()` or `create_or_derive_api_creds()`
3. **Credential Recovery**: Using `derive_api_key(nonce)` to recover existing credentials
4. **Credential Rotation**: Generating new API credentials

### Implementation

The py-clob-client library handles L1 authentication internally:

```python
from py_clob_client.client import ClobClient

# Initialize client with wallet information
client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,
    signature_type=0,  # 0=EOA, 1=Magic, 2=Safe
    funder=wallet_address
)

# L1 authentication happens here - wallet signs EIP-712 message
api_creds = client.create_or_derive_api_creds()
```

## L2 Authentication (API Requests)

### Purpose

L2 authentication secures individual API requests to the CLOB. Every trading operation (place order, cancel order, get orders, etc.) requires L2 authentication.

### Technical Details

**Protocol**: HMAC-SHA256 signature scheme

**Required Headers**: Every authenticated request must include:
- `POLY-ADDRESS`: Your wallet address
- `POLY-SIGNATURE`: HMAC-SHA256 signature of the request
- `POLY-TIMESTAMP`: Unix timestamp (seconds)
- `POLY-NONCE`: Unique request identifier
- `POLY-PASSPHRASE`: API credential passphrase

**Timestamp Expiration**: 30 seconds

**Replay Attack Prevention**: Each request requires a unique nonce

### Security Constraints

1. **Time Window**: Requests with timestamps older than 30 seconds are rejected
2. **Nonce Uniqueness**: Reusing a nonce results in rejection
3. **Signature Validation**: HMAC signature must match request payload

### Implementation

The py-clob-client library handles L2 authentication automatically after credentials are set:

```python
# Set API credentials (from L1 authentication)
client.set_api_creds(api_creds)

# L2 authentication happens automatically on every call
orders = client.get_orders()  # Headers added automatically
client.post_order(order_args)  # Headers added automatically
```

## Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Initial Setup (One-time)                     │
└─────────────────────────────────────────────────────────────────┘

1. Initialize ClobClient
   ├─ Private key
   ├─ Signature type (0/1/2)
   └─ Funder address

2. L1 Authentication
   ├─ Wallet signs EIP-712 message
   ├─ Domain: ClobAuthDomain
   └─ Returns: API credentials

3. Store Credentials
   ├─ apiKey
   ├─ secret
   ├─ passphrase
   └─ (optional: nonce for recovery)

┌─────────────────────────────────────────────────────────────────┐
│                   Trading Operations (Ongoing)                   │
└─────────────────────────────────────────────────────────────────┘

4. Load Credentials
   └─ client.set_api_creds(creds)

5. L2 Authentication (Every Request)
   ├─ Generate timestamp
   ├─ Generate nonce
   ├─ Compute HMAC-SHA256 signature
   ├─ Add headers to request
   └─ Send to CLOB API

6. Server Validation
   ├─ Check timestamp < 30s old
   ├─ Verify nonce uniqueness
   ├─ Validate HMAC signature
   └─ Process request
```

## Common Authentication Errors

### Error: 400 "invalid signature"

**Cause**: Wrong `signature_type` for your wallet architecture

**Solution**: Verify your wallet type:
- If you created wallet on Polymarket.com via email/Magic → use `signature_type=1`
- If using Gnosis Safe or browser wallet proxy → use `signature_type=2`
- If using MetaMask/hardware wallet directly → use `signature_type=0`

**Detection**: Check if your Polymarket profile address differs from your EOA address. If different, you have a proxy wallet and need `signature_type=1` or `2`.

```python
# Check wallet type
from web3 import Web3
eoa_address = Web3().eth.account.from_key(private_key).address
profile_address = "0x..."  # From Polymarket profile

if eoa_address.lower() != profile_address.lower():
    # You have a proxy wallet
    signature_type = 1  # or 2 for Gnosis Safe
    funder = profile_address
else:
    # Direct EOA
    signature_type = 0
    funder = eoa_address
```

### Error: 401 "Unauthorized/Invalid api key"

**Cause**: Expired or incorrect API credentials

**Solutions**:
1. **Credentials expired**: API keys may expire after certain period
   - Regenerate using `create_or_derive_api_creds()`
2. **Wrong credentials loaded**: Verify you're using correct credentials
   - Check environment variables or credential file
3. **Credentials invalidated**: Previous credentials invalidated when new ones created
   - If you created new API key, old credentials no longer work

### Error: 401 "Invalid L1 Request headers"

**Cause**: Malformed L1 authentication request

**Solutions**:
1. **Wrong wallet address**: Verify `funder` parameter matches where funds actually sit
   - For EOA wallets: `funder = wallet_address`
   - For proxy wallets: `funder = proxy_address` (NOT EOA address)
2. **Invalid private key**: Ensure private key format is correct
   - Must start with "0x"
   - Must be valid hex string
3. **Wrong chain ID**: Must be `137` for Polygon mainnet

### Error: Request timestamp too old

**Cause**: System clock skew or request took > 30 seconds to reach server

**Solutions**:
1. Sync your system clock
2. Reduce network latency
3. Generate timestamp immediately before request (library handles this automatically)

### Error: Nonce already used

**Cause**: Attempted to reuse a nonce from previous request

**Solutions**:
- py-clob-client handles nonce generation automatically
- If implementing manually, ensure each request uses unique nonce
- Nonce collision can occur with concurrent requests

## Best Practices

1. **Use `create_or_derive_api_creds()` for initial setup**: Retrieves existing credentials or creates new ones, avoiding accidental invalidation

2. **Store credentials securely**: Save API credentials (key, secret, passphrase) in environment variables or secure file storage

3. **Save nonce for recovery**: When creating credentials explicitly with `create_api_key(nonce)`, save the nonce value for credential recovery

4. **Verify wallet type before initialization**: Check if you have EOA or proxy wallet to set correct `signature_type` and `funder`

5. **Keep system clock synchronized**: L2 authentication has 30-second timestamp window

6. **Let library handle L2 headers**: Don't attempt manual HMAC-SHA256 implementation - py-clob-client handles this correctly

## Related Documentation

- [API Credential Management](api-credentials.md) - Creating, storing, and recovering API credentials
- [py-clob-client Documentation](https://github.com/Polymarket/py-clob-client) - Official Python client library
- [Polymarket Authentication Docs](https://docs.polymarket.com/developers/CLOB/authentication) - Official API documentation
