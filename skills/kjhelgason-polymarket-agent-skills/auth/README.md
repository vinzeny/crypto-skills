# Polymarket Authentication & Setup

Complete guide to authenticating and configuring the Polymarket CLOB API client using py-clob-client.

## Quick Start

**Fastest path to a working client:**

1. **Determine your wallet type** - Are you using MetaMask (EOA), email login (proxy), or Gnosis Safe?
2. **Install dependencies** - `pip install py-clob-client web3`
3. **Follow the initialization guide** - [client-initialization.md](./client-initialization.md)
4. **Set token allowances** (EOA only) - [token-allowances.md](./token-allowances.md)
5. **Trade!**

**TL;DR Decision Tree:**

```
Which wallet do you use?
├─ MetaMask / Hardware wallet
│  └─ EOA wallet (signature_type=0)
│     └─ Need: allowances + EOA address as funder
│
├─ Polymarket email / Magic login
│  └─ Proxy wallet (signature_type=1)
│     └─ Need: proxy address as funder (no allowances)
│
└─ Gnosis Safe / Multi-sig
   └─ Safe wallet (signature_type=2)
      └─ Need: Safe address as funder (check allowances)
```

**See:** [Wallet Types Detection](./wallet-types.md)

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed
- **pip packages:** `pip install py-clob-client web3`
- **Private key** for your wallet (keep secure!)
- **POL/MATIC for gas** (EOA wallets only - ~0.1 POL for setup)
- **USDC.e (not native USDC!)** - Critical distinction

### USDC.e vs Native USDC

**IMPORTANT:** Polymarket exclusively uses **USDC.e** (bridged USDC on Polygon).

| Token | Contract Address | Polymarket Support |
|-------|------------------|-------------------|
| **USDC.e** | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | ✓ Required |
| Native USDC | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` | ✗ Not supported |

**Common issue:** Depositing native USDC from exchanges results in $0.00 balance in Polymarket. You must swap to USDC.e.

**See:** [Token Allowances Guide - USDC.e Detection](./token-allowances.md#usdc-e-vs-native-usdc-critical-distinction)

## Documentation Index

Complete authentication and setup documentation:

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[client-initialization.md](./client-initialization.md)** | Complete setup guide for all wallet types | **Start here** - First time setup |
| **[wallet-types.md](./wallet-types.md)** | EOA vs proxy vs Safe detection and configuration | Unsure which wallet type you have |
| **[authentication-flow.md](./authentication-flow.md)** | L1/L2 authentication architecture deep dive | Understanding how auth works or debugging auth issues |
| **[api-credentials.md](./api-credentials.md)** | Credential creation, storage, recovery, rotation | Setting up credentials or credential problems |
| **[token-allowances.md](./token-allowances.md)** | USDC.e setup and exchange approvals | EOA setup or allowance-related errors |

### Reading Order

**For first-time setup:**
1. Start with [client-initialization.md](./client-initialization.md) - complete walkthrough
2. Reference [wallet-types.md](./wallet-types.md) when determining wallet type
3. Follow [token-allowances.md](./token-allowances.md) for EOA allowance setup
4. Save [api-credentials.md](./api-credentials.md) for credential management later

**For troubleshooting:**
1. Check [Common Issues](#common-issues-quick-reference) section below
2. Follow referenced document for detailed solutions
3. Review [authentication-flow.md](./authentication-flow.md) for auth architecture understanding

## Common Issues Quick Reference

Fast solutions to the most common setup problems:

### "Invalid signature" Error (400)

**Symptom:** 400 error with "invalid signature" message when placing orders or creating credentials

**Cause:** Wrong `signature_type` for your wallet architecture

**Solution:**
1. Verify wallet type: Compare your EOA address to Polymarket profile address
2. If addresses differ → You have a proxy wallet (use `signature_type=1`)
3. If addresses match → You have an EOA wallet (use `signature_type=0`)

**See:** [Wallet Types Detection Guide](./wallet-types.md#detection-method)

---

### Balance Shows $0.00

**Symptom:** Polygon wallet shows USDC balance, but Polymarket shows $0.00

**Cause:** Either wrong USDC token type OR wrong funder address

**Diagnosis:**
```python
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

abi = '[{"name":"balanceOf","inputs":[{"type":"address"}],"outputs":[{"type":"uint256"}],"type":"function"}]'
contract = web3.eth.contract(address=USDC_E, abi=abi)

balance = contract.functions.balanceOf("0xYourAddress").call()
print(f"USDC.e balance: ${balance / 1e6:.2f}")
```

**Solution 1:** If balance is $0.00, you have native USDC instead of USDC.e
- Swap using Polymarket "Activate Funds" or QuickSwap

**Solution 2:** If balance shows correctly, you're checking the wrong address
- For proxy wallets, check balance on proxy address (NOT EOA address)

**See:** [Token Allowances - USDC.e vs Native](./token-allowances.md#usdc-e-vs-native-usdc-critical-distinction)

---

### "Unauthorized/Invalid api key" Error (401)

**Symptom:** 401 error with "Unauthorized" or "Invalid api key" message

**Cause:** API credentials not set, expired, or invalidated

**Solution:**
```python
# Regenerate and set credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
```

**If credentials were recently created elsewhere:** Old credentials were invalidated. Use the new credentials or regenerate.

**See:** [API Credentials Troubleshooting](./api-credentials.md#troubleshooting)

---

### Order Placement Fails After Successful Authentication

**Symptom:** Authentication works (can get orders, check markets), but placing orders fails

**Cause:** Missing token allowances (EOA wallets only)

**Solution:**
```python
# Check if allowances are set (EOA wallets)
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

abi = '[{"name":"allowance","inputs":[{"type":"address"},{"type":"address"}],"outputs":[{"type":"uint256"}],"type":"function"}]'
contract = web3.eth.contract(address=USDC_E, abi=abi)

allowance = contract.functions.allowance("0xYourEOA", EXCHANGE).call()
if allowance == 0:
    print("Allowances NOT set - need to run setup")
```

**See:** [Token Allowances Setup Guide](./token-allowances.md#setting-up-allowances)

---

### "Invalid L1 Request headers" Error (401)

**Symptom:** 401 error with "Invalid L1 Request headers" when creating API credentials

**Cause:** Malformed initialization parameters

**Solution:**
1. Verify `funder` parameter:
   - EOA wallets: Use your wallet address
   - Proxy wallets: Use proxy address (from Polymarket profile, NOT EOA)
2. Check private key format (valid hex string, with or without `0x` prefix)
3. Ensure `chain_id=137` for Polygon mainnet

**See:** [Authentication Flow - Common Errors](./authentication-flow.md#common-authentication-errors)

---

### Can't Find Proxy Address

**Symptom:** Need proxy address for `funder` parameter but don't know it

**Solution 1: Polymarket UI (Easiest)**
1. Log in to polymarket.com
2. Go to your profile
3. Address shown is your proxy address (if different from EOA)

**Solution 2: Address Comparison**
```python
from web3 import Web3

eoa = Web3().eth.account.from_key(PRIVATE_KEY).address
# Compare to address shown in Polymarket UI
# If different, Polymarket address is your proxy
```

**See:** [Wallet Types - Finding Proxy Address](./wallet-types.md#finding-your-proxy-address)

---

## Related Documentation

Authentication is the foundation for all Polymarket operations:

- **[Trading Operations](../trading/README.md)** - Place orders using authenticated client
- **[Market Discovery](../market-discovery/README.md)** - Find markets (no auth required)
- **[Real-Time Data](../real-time/README.md)** - WebSocket streaming (user channel needs auth)
- **[Data Analytics](../data-analytics/README.md)** - Portfolio tracking (public wallet queries)
- **[Edge Cases](../edge-cases/README.md)** - Authentication troubleshooting
- **[Library Reference](../library/README.md)** - Client initialization patterns

[Back to Polymarket Skills](../SKILL.md)

## Architecture Overview

### Two-Tier Authentication

Polymarket uses a split authentication architecture:

**L1 Authentication (Wallet-level):**
- Uses EIP-712 wallet signatures
- Creates API credentials
- Required for credential generation/rotation
- Handled by py-clob-client during `create_or_derive_api_creds()`

**L2 Authentication (Request-level):**
- Uses HMAC-SHA256 signatures
- Secures every API request
- Headers: POLY-ADDRESS, POLY-SIGNATURE, POLY-TIMESTAMP, POLY-NONCE, POLY-PASSPHRASE
- Handled automatically by py-clob-client after `set_api_creds()`

**See:** [Authentication Flow Architecture](./authentication-flow.md)

### Three Wallet Types

| Type | signature_type | Use Case | Allowances Needed |
|------|----------------|----------|-------------------|
| **EOA** | `0` | MetaMask, hardware wallets | Yes (manual) |
| **Proxy** | `1` | Email/Magic login | No (automatic) |
| **Safe** | `2` | Multi-sig wallets | Check status |

**See:** [Wallet Types Reference](./wallet-types.md)

### Token Architecture

**USDC.e (ERC-20):**
- Trading currency
- Must approve for 3 exchange contracts (EOA only)
- Address: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`

**Conditional Token Framework (ERC-1155):**
- Prediction market positions
- Must approve for 3 exchange contracts (EOA only)
- Address: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`

**See:** [Token Allowances - Architecture](./token-allowances.md#required-allowances)

## Support & Resources

### Official Resources

- [Polymarket Documentation](https://docs.polymarket.com/developers) - Official API docs
- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client) - Official Python client
- [Polymarket Discord](https://discord.gg/polymarket) - Community support

### Troubleshooting Resources

1. Check [Common Issues](#common-issues-quick-reference) above
2. Review relevant documentation guide
3. Search [py-clob-client issues](https://github.com/Polymarket/py-clob-client/issues)
4. Ask in Polymarket Discord #api-support channel

### Key Contract Addresses

**Tokens:**
- USDC.e: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- Conditional Tokens: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`

**Exchanges:**
- CTF Exchange: `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`
- Neg Risk Exchange: `0xC5d563A36AE78145C45a50134d48A1215220f80a`
- Neg Risk Adapter: `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296`

**Network:**
- Chain ID: 137 (Polygon mainnet)
- RPC: https://polygon-rpc.com (or other Polygon RPC)

## Complete Setup Checklist

Before attempting your first trade:

- [ ] Installed Python 3.9+
- [ ] Installed py-clob-client and web3: `pip install py-clob-client web3`
- [ ] Have private key stored securely
- [ ] Determined wallet type (EOA, proxy, or Safe)
- [ ] Have USDC.e (NOT native USDC) in correct address
- [ ] Have POL/MATIC for gas (if EOA wallet)
- [ ] Set token allowances (if EOA wallet)
- [ ] Initialized ClobClient with correct parameters
- [ ] Created and set API credentials
- [ ] Verified setup with test API calls

**Follow:** [Client Initialization Complete Guide](./client-initialization.md)

---

**Last updated:** 2026-01-31 (Phase 1)
**Status:** Complete - All authentication and setup documentation finalized
