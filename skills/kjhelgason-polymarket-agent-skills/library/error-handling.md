# Error Handling and Exception Types

Comprehensive guide to py-clob-client exception handling, error categorization, and recovery patterns.

**Covers:** LIB-03 (Exception types and error recovery)

## Exception Hierarchy

The py-clob-client library uses two primary exception classes:

```python
from py_clob_client.exceptions import PolyException, PolyApiException
```

### PolyException (Base)

Base exception for all py-clob-client errors.

```python
class PolyException(Exception):
    """Base exception for py-clob-client.

    Attributes:
        msg: Error message describing what went wrong
    """
    def __init__(self, msg):
        self.msg = msg
```

### PolyApiException (API Errors)

API-specific errors with HTTP status codes and detailed messages.

```python
class PolyApiException(PolyException):
    """API error with status code and message.

    Attributes:
        status_code: HTTP status code (400, 401, 404, 429, 5xx)
        error_msg: Detailed error message from API
    """
    def __init__(self, resp=None, error_msg=None):
        self.status_code = resp.status_code if resp else None
        self.error_msg = self._get_message(resp) if resp else error_msg
```

## Status Code Reference

| Code | Meaning | Common Causes | Action |
|------|---------|---------------|--------|
| 400 | Bad Request | Invalid parameters, precision errors, insufficient balance | Check parameters, fix precision, verify balance |
| 401 | Unauthorized | Invalid/expired API key, wrong signature_type | Refresh credentials with `create_or_derive_api_creds()` |
| 404 | Not Found | Invalid endpoint, resource doesn't exist | Verify endpoint URL and resource ID |
| 429 | Rate Limited | Too many requests (requests are QUEUED, not dropped) | Wait before next request, or slow down |
| 5xx | Server Error | Polymarket API issues | Retry with exponential backoff |

**Important:** 429 errors on Polymarket mean requests are queued via Cloudflare throttling, not dropped. Your request will eventually process, but you should slow down.

## Error Categorization

Use this pattern to categorize and handle errors appropriately:

```python
from py_clob_client.exceptions import PolyApiException

def place_order_safely(client, order_args, order_type):
    """Place order with comprehensive error categorization.

    Returns dict with success status and error details if failed.
    """
    try:
        signed = client.create_order(order_args)
        response = client.post_order(signed, order_type)
        return {"success": True, "response": response}

    except PolyApiException as e:
        error_info = {
            "success": False,
            "status_code": e.status_code,
            "error_msg": e.error_msg
        }

        # Categorize by status code and message
        if e.status_code == 401:
            error_info["category"] = "authentication"
            error_info["action"] = "Refresh API credentials"

        elif e.status_code == 400:
            msg = str(e.error_msg).lower()

            if "balance" in msg or "allowance" in msg:
                error_info["category"] = "insufficient_funds"
                error_info["action"] = "Check USDC.e balance and allowances"

            elif "amounts" in msg or "precision" in msg:
                error_info["category"] = "precision"
                error_info["action"] = "Round FOK size to 2 decimals"

            elif "tick" in msg:
                error_info["category"] = "tick_size"
                error_info["action"] = "Fetch current tick size"

            else:
                error_info["category"] = "validation"
                error_info["action"] = "Check order parameters"

        elif e.status_code == 429:
            error_info["category"] = "rate_limit"
            error_info["action"] = "Wait and retry (requests are queued)"

        elif e.status_code and e.status_code >= 500:
            error_info["category"] = "server_error"
            error_info["action"] = "Retry with exponential backoff"

        else:
            error_info["category"] = "unknown"
            error_info["action"] = "Check full error message"

        return error_info
```

## Common Error Messages and Solutions

| Error Message | Category | Solution |
|---------------|----------|----------|
| `Invalid api key` | auth | Call `client.set_api_creds(client.create_or_derive_api_creds())` |
| `Invalid L1 Request headers` | auth | Check `signature_type` matches wallet type (0=EOA, 1=Magic, 2=Safe) |
| `not enough balance / allowance` | funds | Check USDC.e balance and token allowances are set |
| `insufficient balance` | funds | Verify funder address has USDC.e (check proxy vs EOA) |
| `invalid amounts` | precision | Round FOK size to 2 decimals, ensure size*price has max 2 decimals |
| `INVALID_ORDER_MIN_TICK_SIZE` | precision | Fetch current tick size with `client.get_tick_size(token_id)` |
| `order crosses book` | order | Post-only orders cannot be marketable; adjust price or use GTC |
| `FOK_ORDER_NOT_FILLED_ERROR` | order | Insufficient liquidity for full fill; use FAK or reduce size |
| `MARKET_NOT_READY` | market | Market not accepting orders yet; wait and retry |

### Complete Error Solutions Dictionary

```python
ERROR_SOLUTIONS = {
    # Authentication errors (401)
    "Invalid api key": {
        "category": "auth",
        "solution": "Call client.set_api_creds(client.create_or_derive_api_creds())"
    },
    "Invalid L1 Request headers": {
        "category": "auth",
        "solution": "Check signature_type: 0=EOA, 1=Magic, 2=Safe"
    },
    "Unauthorized": {
        "category": "auth",
        "solution": "Refresh API credentials"
    },

    # Balance/allowance errors (400)
    "not enough balance / allowance": {
        "category": "funds",
        "solution": "Check USDC.e balance and set token allowances"
    },
    "insufficient balance": {
        "category": "funds",
        "solution": "Verify funder address has USDC.e, not EOA if using proxy"
    },

    # Precision errors (400)
    "invalid amounts": {
        "category": "precision",
        "solution": "Round FOK size to 2 decimals, check size*price precision"
    },
    "INVALID_ORDER_MIN_TICK_SIZE": {
        "category": "precision",
        "solution": "Fetch current tick size - it may have changed at price extremes"
    },

    # Order errors (400)
    "order crosses book": {
        "category": "order",
        "solution": "Post-only orders cannot cross; adjust price or use GTC"
    },
    "FOK_ORDER_NOT_FILLED_ERROR": {
        "category": "order",
        "solution": "Insufficient liquidity; use FAK for partial fills or reduce size"
    },

    # Market errors
    "MARKET_NOT_READY": {
        "category": "market",
        "solution": "Market not accepting orders yet; wait and retry"
    }
}

def lookup_error_solution(error_msg: str) -> dict:
    """Look up solution for a known error message."""
    error_str = str(error_msg).lower()
    for key, value in ERROR_SOLUTIONS.items():
        if key.lower() in error_str:
            return value
    return {"category": "unknown", "solution": "Check full error message"}
```

## Recovery Patterns

### Pattern 1: 401 Unauthorized Recovery

When API credentials expire or become invalid:

```python
from py_clob_client.exceptions import PolyApiException

def post_order_with_auth_retry(client, signed_order, order_type, max_retries=2):
    """Post order with automatic credential refresh on 401."""
    for attempt in range(max_retries):
        try:
            response = client.post_order(signed_order, order_type)
            return response

        except PolyApiException as e:
            if e.status_code == 401 and attempt < max_retries - 1:
                print("Refreshing API credentials...")
                creds = client.create_or_derive_api_creds()
                client.set_api_creds(creds)
                continue
            raise

# Usage
try:
    response = post_order_with_auth_retry(client, signed_order, order_type)
except PolyApiException as e:
    print(f"Order failed after auth retry: {e.error_msg}")
```

See [Client Initialization](../auth/client-initialization.md) for full credential setup.

### Pattern 2: Precision Error Recovery

When FOK orders fail due to precision requirements:

```python
from py_clob_client.clob_types import OrderType
from py_clob_client.exceptions import PolyApiException
from decimal import Decimal, ROUND_DOWN

def post_order_with_precision_fallback(client, order_args, order_type):
    """Post order with fallback to GTC if FOK precision fails."""
    try:
        signed = client.create_order(order_args)
        response = client.post_order(signed, order_type)
        return response

    except PolyApiException as e:
        msg = str(e.error_msg).lower()

        if order_type == OrderType.FOK and "invalid amounts" in msg:
            print("FOK precision error, falling back to GTC...")
            # GTC has looser precision requirements
            response = client.post_order(signed, OrderType.GTC)
            return response

        raise

def prepare_fok_order_size(size: float, price: float) -> float:
    """Prepare size for FOK precision requirements.

    FOK Requirements:
    - Maker amount: max 2 decimal places
    - Size x Price product: max 2 decimal places
    """
    size_d = Decimal(str(size))
    price_d = Decimal(str(price))

    # Round size to 2 decimals
    size_d = size_d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    # Check product precision
    product = size_d * price_d
    product_rounded = product.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    if product != product_rounded:
        # Adjust size to make product clean
        size_d = (product_rounded / price_d).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )

    return float(size_d)
```

### Pattern 3: Rate Limit Handling

When hitting rate limits (429):

```python
import time
from py_clob_client.exceptions import PolyApiException

def post_order_with_rate_limit_handling(client, signed_order, order_type, max_retries=3):
    """Post order with rate limit handling.

    Note: Polymarket uses Cloudflare throttling.
    429 means requests are QUEUED, not dropped.
    """
    for attempt in range(max_retries):
        try:
            response = client.post_order(signed_order, order_type)
            return response

        except PolyApiException as e:
            if e.status_code == 429:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise

    raise Exception("Max retries exceeded due to rate limiting")
```

### Pattern 4: Server Error Retry

When Polymarket API has issues (5xx):

```python
import time
import random
from py_clob_client.exceptions import PolyApiException

def post_order_with_server_error_retry(client, signed_order, order_type, max_retries=3):
    """Post order with exponential backoff on server errors."""
    for attempt in range(max_retries):
        try:
            response = client.post_order(signed_order, order_type)
            return response

        except PolyApiException as e:
            if e.status_code and e.status_code >= 500:
                # Exponential backoff with jitter
                base_wait = 2 ** attempt
                jitter = random.uniform(0, 1)
                wait_time = base_wait + jitter
                print(f"Server error, retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue
            raise

    raise Exception("Max retries exceeded due to server errors")
```

### Pattern 5: Comprehensive Error Handler

Combines all patterns into a single robust handler:

```python
import time
import random
from py_clob_client.exceptions import PolyApiException
from py_clob_client.clob_types import OrderType

def post_order_robust(client, order_args, order_type, max_retries=3):
    """Post order with comprehensive error handling.

    Handles:
    - 401: Refreshes credentials
    - 429: Waits and retries
    - 5xx: Exponential backoff
    - FOK precision: Falls back to GTC
    """
    signed_order = None

    for attempt in range(max_retries):
        try:
            if signed_order is None:
                signed_order = client.create_order(order_args)

            response = client.post_order(signed_order, order_type)
            return {"success": True, "response": response}

        except PolyApiException as e:
            # 401: Refresh credentials
            if e.status_code == 401:
                print("Refreshing credentials...")
                creds = client.create_or_derive_api_creds()
                client.set_api_creds(creds)
                signed_order = None  # Re-sign after credential refresh
                continue

            # 429: Rate limited (requests queued)
            if e.status_code == 429:
                wait_time = 2 ** attempt
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            # 5xx: Server error
            if e.status_code and e.status_code >= 500:
                wait_time = 2 ** attempt + random.uniform(0, 1)
                print(f"Server error, retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue

            # FOK precision error: Fall back to GTC
            msg = str(e.error_msg).lower()
            if order_type == OrderType.FOK and "invalid amounts" in msg:
                print("FOK precision error, falling back to GTC...")
                response = client.post_order(signed_order, OrderType.GTC)
                return {"success": True, "response": response, "fallback": "GTC"}

            # Non-retryable error
            return {
                "success": False,
                "status_code": e.status_code,
                "error_msg": e.error_msg,
                "category": lookup_error_solution(e.error_msg)
            }

    return {"success": False, "error": "Max retries exceeded"}
```

## Basic Exception Handling

For simple use cases:

```python
from py_clob_client.exceptions import PolyApiException

try:
    response = client.post_order(signed_order, order_type)
    print(f"Order placed: {response.get('orderID')}")

except PolyApiException as e:
    print(f"API Error [{e.status_code}]: {e.error_msg}")

    if e.status_code == 401:
        print("Action: Refresh your API credentials")
    elif e.status_code == 400:
        print("Action: Check your order parameters")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Related Documentation

- [Client Initialization](../auth/client-initialization.md) - Credential setup and refresh
- [Order Placement](../trading/order-placement.md) - Order creation workflow
- [Order Types](../trading/order-types.md) - FOK precision requirements
- [Edge Cases](../edge-cases/README.md) - Common pitfalls and solutions

## References

- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client) - Source code and issues
- [Polymarket Rate Limits](https://docs.polymarket.com/quickstart/introduction/rate-limits) - Official limits

## Navigation

[Back to Library](./README.md) | [Edge Cases](../edge-cases/README.md) | [Trading](../trading/README.md)
