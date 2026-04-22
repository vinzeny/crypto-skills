# py-clob-client Library Reference

Reference documentation for the official Polymarket Python client library.

## Installation

```bash
pip install py-clob-client
```

**Recommended companion packages:**

```bash
pip install web3 python-dotenv
```

## Quick Start

```python
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=os.getenv("POLYMARKET_PRIVATE_KEY"),
    chain_id=137,
    signature_type=0,  # 0=EOA, 1=Magic, 2=Safe
    funder=os.getenv("WALLET_ADDRESS")
)

# Set up credentials
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)

# Ready to trade
print(client.get_ok())
```

See [Client Initialization Guide](../auth/client-initialization.md) for complete setup instructions.

## When to Use This Section

This library reference helps when you need to:

- **Handle errors from API calls** - Exception types, status codes, recovery patterns
- **Implement rate limiting** - Burst and sustained limits, RateLimiter class
- **Deploy to production** - WebSocket reliability, balance tracking, checklists
- **Look up method signatures** - Common py-clob-client method reference

## Library Documentation

| Document | Description |
|----------|-------------|
| [Error Handling](./error-handling.md) | Exception types, common errors, and recovery patterns |
| [Production Patterns](./production-patterns.md) | Rate limiting, WebSocket reliability, balance tracking |

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Library** | `py-clob-client` |
| **Version** | 0.34.5+ |
| **GitHub** | [github.com/Polymarket/py-clob-client](https://github.com/Polymarket/py-clob-client) |
| **PyPI** | `pip install py-clob-client` |

### Related Guides

| Topic | Location | Description |
|-------|----------|-------------|
| Client Setup | [auth/client-initialization.md](../auth/client-initialization.md) | Complete ClobClient initialization |
| Authentication | [auth/api-credentials.md](../auth/api-credentials.md) | API credential management |
| Order Placement | [trading/order-placement.md](../trading/order-placement.md) | Order creation and submission |
| Edge Cases | [edge-cases/README.md](../edge-cases/README.md) | Common pitfalls and solutions |

## Key Imports

```python
# Client
from py_clob_client.client import ClobClient

# Order types
from py_clob_client.clob_types import OrderArgs, OrderType

# Side constants
from py_clob_client.order_builder.constants import BUY, SELL

# Exceptions
from py_clob_client.exceptions import PolyException, PolyApiException
```

## Related Documentation

The library module connects to all skill areas:

- **[Authentication](../auth/README.md)** - Client initialization patterns
- **[Trading Operations](../trading/README.md)** - Order placement, error recovery
- **[Real-Time Data](../real-time/README.md)** - WebSocket connection patterns
- **[Edge Cases](../edge-cases/README.md)** - Troubleshooting, common pitfalls
- **[Market Discovery](../market-discovery/README.md)** - API query patterns
- **[Data Analytics](../data-analytics/README.md)** - Data retrieval patterns

[Back to Polymarket Skills](../SKILL.md)
