# Authentication Guide

## Overview

Polymarket uses two authentication levels:

| Level | Method | Used For |
|-------|--------|----------|
| L1 | EIP-712 wallet signature | Creating/deriving API credentials |
| L2 | HMAC-SHA256 with API key | All trading operations |

---

## L1 Authentication (Wallet Signature)

L1 auth uses EIP-712 typed data signing to prove wallet ownership.

### When Required
- Creating new API credentials (`POST /auth/api-key`)
- Deriving existing credentials (`GET /auth/derive-api-key`)

### Headers Required
```
POLY_ADDRESS: 0x742d35Cc6634C0532925a3b844Bc9e7595f55555
POLY_SIGNATURE: <EIP-712 signature>
POLY_TIMESTAMP: 1699999999
POLY_NONCE: 0
```

### Message Structure
```python
domain = {
    "name": "ClobAuthDomain",
    "version": "1",
    "chainId": 137,  # Polygon
}

message = {
    "address": signer_address,
    "timestamp": str(timestamp),
    "nonce": nonce,
    "message": "This message attests that I control the given wallet",
}
```

### Creating Credentials

```python
from polymarket import PolymarketClient

async with PolymarketClient(private_key="0x...") as client:
    # Create new API key (invalidates previous)
    credentials = await client.create_api_credentials()

    print(f"API Key: {credentials.api_key}")
    print(f"Secret: {credentials.secret}")
    print(f"Passphrase: {credentials.passphrase}")
```

### Deriving Credentials

```python
# Use same nonce as when created
credentials = await client.derive_api_credentials(nonce=0)
```

---

## L2 Authentication (HMAC)

L2 auth uses HMAC-SHA256 signing with API credentials.

### When Required
- Placing orders (`POST /order`)
- Getting orders (`GET /orders`)
- Cancelling orders (`DELETE /cancel*`)
- Getting trades (`GET /data/trades`)
- Balance queries (`GET /balance-allowance`)

### Headers Required
```
POLY_ADDRESS: 0x742d35Cc6634C0532925a3b844Bc9e7595f55555
POLY_SIGNATURE: <HMAC-SHA256 signature>
POLY_TIMESTAMP: 1699999999
POLY_API_KEY: 550e8400-e29b-41d4-a716-446655440000
POLY_PASSPHRASE: randomPassphraseString
```

### Signature Calculation

```python
import base64
import hashlib
import hmac

# Message format: timestamp + method + path + body
message = f"{timestamp}POST/order{json_body}"

# Sign with base64-decoded secret
secret_bytes = base64.urlsafe_b64decode(credentials.secret)
signature = hmac.new(
    secret_bytes,
    message.encode("utf-8"),
    hashlib.sha256,
)
signature_b64 = base64.urlsafe_b64encode(signature.digest()).decode()
```

---

## Signature Types

When signing orders, you must specify the correct signature type:

| Type | Value | Use Case |
|------|-------|----------|
| EOA | 0 | Standard Ethereum wallet (MetaMask, hardware wallet) |
| POLY_PROXY | 1 | Magic Link email/Google login users |
| GNOSIS_SAFE | 2 | Most common - Gnosis Safe proxy wallet |

```python
from polymarket.models.orders import SignatureType

# Default for most users
client = PolymarketClient(
    private_key="0x...",
    credentials=credentials,
    signature_type=SignatureType.GNOSIS_SAFE,
)
```

---

## Environment Variables

Recommended setup for credentials:

```bash
# .env file
POLY_PRIVATE_KEY=0x...
POLY_API_KEY=550e8400-e29b-41d4-a716-446655440000
POLY_API_SECRET=base64EncodedSecret
POLY_API_PASSPHRASE=randomPassphrase
```

```python
import os
from polymarket import PolymarketClient, Credentials

credentials = Credentials(
    api_key=os.environ["POLY_API_KEY"],
    secret=os.environ["POLY_API_SECRET"],
    passphrase=os.environ["POLY_API_PASSPHRASE"],
)

async with PolymarketClient(
    private_key=os.environ.get("POLY_PRIVATE_KEY"),
    credentials=credentials,
) as client:
    ...
```

---

## Public Endpoints

These endpoints require **no authentication**:

### CLOB API
- `/book`, `/books` - Order book
- `/price`, `/midpoint`, `/spread` - Prices
- `/tick-size`, `/neg-risk` - Market info
- `/prices-history` - Historical prices
- `/ok`, `/time` - Health/status

### Gamma API (all endpoints)
- Markets, events, series, tags
- Search, profiles, comments
- Sports metadata

### Data API (all endpoints)
- Positions, activity
- Leaderboards, analytics

### Bridge API (all endpoints)
- Supported assets
- Deposit/withdrawal addresses
- Quotes, transaction status

---

## WebSocket Authentication

Market channel is **public**:
```json
{
  "type": "MARKET",
  "assets_ids": ["token_id"]
}
```

User channel requires **API credentials**:
```json
{
  "auth": {
    "apiKey": "your-api-key",
    "secret": "your-secret",
    "passphrase": "your-passphrase"
  },
  "type": "USER",
  "markets": ["condition_id"]
}
```
