# Polymarket API Credential Management

## Overview

API credentials enable L2 authentication for Polymarket CLOB API requests. These credentials consist of three components:

- **apiKey**: Unique identifier for your API access
- **secret**: Secret key used for HMAC signature generation
- **passphrase**: Additional authentication parameter

API credentials are derived from your wallet's private key using L1 authentication (EIP-712 signatures). Each wallet can have one active set of API credentials at a time.

**Key Principle**: Credentials are deterministic - given the same wallet and nonce, you'll always get the same credentials. This enables credential recovery if you save the nonce.

## Creating Credentials

### Method 1: create_or_derive_api_creds() (Recommended)

**Use case**: Initial setup or when you're unsure if credentials already exist

**Behavior**:
- Checks if credentials already exist for your wallet
- If exist: retrieves and returns existing credentials
- If not exist: creates new credentials
- Does NOT invalidate existing credentials

**Advantages**:
- Safe for repeated calls (won't accidentally invalidate credentials)
- Handles both first-time setup and subsequent loads
- No need to track whether credentials exist

**Disadvantages**:
- Does not return the nonce (limits recovery options)
- Uses library-managed default nonce

```python
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,
    signature_type=0,
    funder=wallet_address
)

# Create or retrieve credentials
creds = client.create_or_derive_api_creds()
# Returns: {"apiKey": "...", "secret": "...", "passphrase": "..."}

# Apply to client
client.set_api_creds(creds)

# Save securely (see Storage section)
```

### Method 2: create_api_key(nonce) (Explicit Creation)

**Use case**: When you need explicit control over credential creation with nonce tracking

**Behavior**:
- Always creates new credentials with specified nonce
- Invalidates any previous credentials for this wallet
- Returns credentials with the nonce you provided

**Advantages**:
- Explicit nonce tracking enables recovery
- Full control over when credentials are created
- Deterministic credential generation

**Disadvantages**:
- Invalidates previous credentials (all active orders may need cancellation)
- Requires manual nonce management
- Dangerous if called repeatedly without understanding implications

**When to use**:
- Initial setup where you want nonce-based recovery capability
- Credential rotation (intentional invalidation of old credentials)
- Recovery when you know the nonce

```python
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,
    signature_type=0,
    funder=wallet_address
)

# Create credentials with explicit nonce
nonce = 12345  # Choose a nonce you'll remember
creds = client.create_api_key(nonce)
# Returns: {"apiKey": "...", "secret": "...", "passphrase": "..."}

# IMPORTANT: Save the nonce along with credentials
creds['nonce'] = nonce

client.set_api_creds(creds)
```

### Method 3: derive_api_key(nonce) (Credential Recovery)

**Use case**: Recovering credentials when you know the nonce but lost the credentials

**Behavior**:
- Derives existing credentials using the specified nonce
- Does NOT create new credentials
- Does NOT invalidate existing credentials
- Returns the same credentials that were originally created with this nonce

**Advantages**:
- Recovers lost credentials without invalidation
- No impact on active orders
- Deterministic recovery

**Disadvantages**:
- Requires knowing the nonce (if lost, can't recover)

```python
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,
    signature_type=0,
    funder=wallet_address
)

# Recover credentials with known nonce
nonce = 12345  # The nonce you saved
creds = client.derive_api_key(nonce)
# Returns: {"apiKey": "...", "secret": "...", "passphrase": "..."}

client.set_api_creds(creds)
```

## Method Comparison Table

| Method | Creates New | Invalidates Old | Returns Nonce | Use Case |
|--------|-------------|-----------------|---------------|----------|
| `create_or_derive_api_creds()` | Only if needed | No | No | Initial setup (safest) |
| `create_api_key(nonce)` | Always | Yes | No (but you provide it) | Explicit creation/rotation |
| `derive_api_key(nonce)` | Never | No | No (but you provide it) | Recovery with known nonce |

## Storing Credentials Securely

### Important: What to Store

Always store:
1. `apiKey`
2. `secret`
3. `passphrase`
4. `nonce` (if using `create_api_key()`)

**Without the nonce, credential recovery is impossible if credentials are lost.**

### Storage Method 1: Environment Variables

**Best for**: Development environments, local scripts

```python
import os

# Save to .env file
with open('.env', 'w') as f:
    f.write(f"POLY_API_KEY={creds['apiKey']}\n")
    f.write(f"POLY_SECRET={creds['secret']}\n")
    f.write(f"POLY_PASSPHRASE={creds['passphrase']}\n")
    f.write(f"POLY_NONCE={creds.get('nonce', '')}\n")

# Load credentials
api_key = os.getenv("POLY_API_KEY")
secret = os.getenv("POLY_SECRET")
passphrase = os.getenv("POLY_PASSPHRASE")
nonce = os.getenv("POLY_NONCE")

creds = {
    "apiKey": api_key,
    "secret": secret,
    "passphrase": passphrase
}
client.set_api_creds(creds)
```

**Security considerations**:
- Add `.env` to `.gitignore` (never commit credentials)
- Use environment variable loading libraries like `python-dotenv`
- Restrict file permissions: `chmod 600 .env` (Unix/Linux)

### Storage Method 2: Secure JSON File

**Best for**: Local development with structured credential management

```python
import json
from pathlib import Path

def save_credentials(creds: dict, path: str = ".polymarket_creds.json"):
    """
    Save credentials to secure JSON file.
    WARNING: Protect this file appropriately for your OS.
    """
    creds_file = Path(path)
    creds_file.write_text(json.dumps(creds, indent=2))

    # Unix/Linux: Set restrictive permissions
    try:
        creds_file.chmod(0o600)  # Owner read/write only
    except:
        pass  # Windows doesn't support chmod

    print(f"Credentials saved to {path}")
    if 'nonce' in creds and creds['nonce']:
        print(f"IMPORTANT: Nonce {creds['nonce']} saved for recovery")

def load_credentials(path: str = ".polymarket_creds.json") -> dict:
    """Load saved credentials from file."""
    creds_file = Path(path)
    if not creds_file.exists():
        raise FileNotFoundError(f"Credentials file not found: {path}")
    return json.loads(creds_file.read_text())

# Usage
save_credentials(creds)
# Later...
loaded_creds = load_credentials()
client.set_api_creds(loaded_creds)
```

### Storage Method 3: Secrets Manager (Production)

**Best for**: Production deployments, cloud environments

```python
# Example: AWS Secrets Manager
import boto3
import json

def save_to_secrets_manager(creds: dict, secret_name: str):
    """Store credentials in AWS Secrets Manager"""
    client = boto3.client('secretsmanager')

    secret_value = {
        "apiKey": creds['apiKey'],
        "secret": creds['secret'],
        "passphrase": creds['passphrase'],
        "nonce": creds.get('nonce')
    }

    client.create_secret(
        Name=secret_name,
        SecretString=json.dumps(secret_value)
    )

def load_from_secrets_manager(secret_name: str) -> dict:
    """Retrieve credentials from AWS Secrets Manager"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
save_to_secrets_manager(creds, "polymarket/api-creds")
# Later...
loaded_creds = load_from_secrets_manager("polymarket/api-creds")
client.set_api_creds(loaded_creds)
```

**Similar patterns exist for**:
- Google Cloud Secret Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

## Credential Recovery

### Scenario 1: Credentials Lost, Nonce Known

**Situation**: You lost your credentials file/environment variables, but saved the nonce

**Solution**: Use `derive_api_key(nonce)` to recover

```python
# You have: wallet private key, nonce
# You need: API credentials

client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,
    signature_type=0,
    funder=wallet_address
)

# Recover with saved nonce
nonce = 12345  # Your saved nonce
recovered_creds = client.derive_api_key(nonce)
client.set_api_creds(recovered_creds)

# Save again to prevent future loss
save_credentials(recovered_creds)
```

**Result**: Original credentials recovered, no impact on active orders

### Scenario 2: Credentials Lost, Nonce Unknown

**Situation**: You lost credentials AND didn't save the nonce

**Solution**: Create new credentials (invalidates old ones)

```python
client = ClobClient(
    host="https://clob.polymarket.com",
    key=private_key,
    chain_id=137,
    signature_type=0,
    funder=wallet_address
)

# Must create new credentials
new_creds = client.create_or_derive_api_creds()
client.set_api_creds(new_creds)

# Save securely THIS TIME with nonce tracking
# If you want nonce for future recovery:
new_nonce = 67890  # Choose new nonce
new_creds_with_nonce = client.create_api_key(new_nonce)
new_creds_with_nonce['nonce'] = new_nonce
save_credentials(new_creds_with_nonce)
```

**Impact**:
- Old credentials invalidated
- Active orders placed with old credentials may need cancellation
- Need to update any automation using old credentials

### Scenario 3: Multiple Environments

**Situation**: Running scripts in multiple environments (dev, staging, prod)

**Solution**: Use same wallet but track credentials separately

```python
# Development
dev_client = ClobClient(key=private_key, ...)
dev_creds = client.create_or_derive_api_creds()
save_credentials(dev_creds, ".polymarket_creds_dev.json")

# Production (same wallet, same credentials)
prod_client = ClobClient(key=private_key, ...)
prod_creds = load_credentials(".polymarket_creds_dev.json")  # Reuse same creds
prod_client.set_api_creds(prod_creds)
```

**Note**: Using `create_or_derive_api_creds()` with same wallet will return same credentials across environments.

## Credential Rotation

### When to Rotate

Rotate credentials when:
1. **Security concern**: Credentials may have been compromised
2. **Operational change**: Switching to new system/environment
3. **Periodic policy**: Regular credential rotation for security
4. **Recovery failure**: Nonce lost and need fresh start

### Rotation Process

```python
from py_clob_client.client import ClobClient

def rotate_credentials(client: ClobClient, new_nonce: int):
    """
    Rotate API credentials.
    WARNING: Invalidates previous credentials.
    """
    # Step 1: Cancel active orders (optional but recommended)
    active_orders = client.get_orders()
    for order in active_orders:
        if order['status'] == 'LIVE':
            client.cancel(order['id'])

    # Step 2: Create new credentials with new nonce
    new_creds = client.create_api_key(new_nonce)
    new_creds['nonce'] = new_nonce

    # Step 3: Update client
    client.set_api_creds(new_creds)

    # Step 4: Save new credentials
    save_credentials(new_creds)

    # Step 5: Update any external systems using credentials

    print(f"Credentials rotated. New nonce: {new_nonce}")
    return new_creds

# Usage
client = ClobClient(...)
# Load old credentials
old_creds = load_credentials()
client.set_api_creds(old_creds)

# Rotate
new_creds = rotate_credentials(client, new_nonce=99999)
```

**What happens to old credentials**:
- Immediately invalidated
- API requests with old credentials return 401 "Unauthorized/Invalid api key"
- Old credentials cannot be recovered (even with old nonce)

## Anti-Patterns to Avoid

### Anti-Pattern 1: Using create_api_key() for Initial Setup

**Problem**: Calling `create_api_key()` invalidates previous credentials every time

```python
# BAD - Called on every script run
def setup():
    client = ClobClient(...)
    creds = client.create_api_key(12345)  # Invalidates previous!
    client.set_api_creds(creds)
```

**Solution**: Use `create_or_derive_api_creds()` for setup

```python
# GOOD - Safe for repeated calls
def setup():
    client = ClobClient(...)
    creds = client.create_or_derive_api_creds()  # Retrieves existing
    client.set_api_creds(creds)
```

### Anti-Pattern 2: Not Saving Nonce

**Problem**: Cannot recover credentials if lost

```python
# BAD - Nonce not saved
creds = client.create_api_key(12345)
save_credentials(creds)  # Only saves apiKey, secret, passphrase
```

**Solution**: Save nonce along with credentials

```python
# GOOD - Nonce saved for recovery
nonce = 12345
creds = client.create_api_key(nonce)
creds['nonce'] = nonce  # Add nonce to dict
save_credentials(creds)  # Now includes nonce
```

### Anti-Pattern 3: Hardcoding Credentials in Code

**Problem**: Security risk, credentials exposed in version control

```python
# BAD - Never do this
client.set_api_creds({
    "apiKey": "abc123...",
    "secret": "def456...",
    "passphrase": "ghi789..."
})
```

**Solution**: Load from environment or secure storage

```python
# GOOD - Load from environment
import os
client.set_api_creds({
    "apiKey": os.getenv("POLY_API_KEY"),
    "secret": os.getenv("POLY_SECRET"),
    "passphrase": os.getenv("POLY_PASSPHRASE")
})
```

### Anti-Pattern 4: Ignoring Credential Invalidation

**Problem**: Creating new credentials without handling active orders

```python
# BAD - Active orders become orphaned
def rotate():
    new_creds = client.create_api_key(new_nonce)
    client.set_api_creds(new_creds)
    # Old credentials invalidated, but orders still active!
```

**Solution**: Cancel or track active orders before rotation

```python
# GOOD - Handle active orders
def rotate():
    active_orders = client.get_orders()
    # Cancel or track orders as needed
    for order in active_orders:
        if order['status'] == 'LIVE':
            client.cancel(order['id'])

    new_creds = client.create_api_key(new_nonce)
    client.set_api_creds(new_creds)
```

## Complete Example: Initial Setup with Recovery Support

```python
from py_clob_client.client import ClobClient
import json
from pathlib import Path
import os

def initial_setup_with_recovery():
    """
    Complete setup pattern with credential recovery support.
    """
    # Step 1: Initialize client
    client = ClobClient(
        host="https://clob.polymarket.com",
        key=os.getenv("POLYMARKET_PRIVATE_KEY"),
        chain_id=137,
        signature_type=0,
        funder=os.getenv("WALLET_ADDRESS")
    )

    # Step 2: Check if credentials already exist
    creds_file = Path(".polymarket_creds.json")

    if creds_file.exists():
        # Load existing credentials
        print("Loading existing credentials...")
        creds = json.loads(creds_file.read_text())
        client.set_api_creds(creds)
        print("Credentials loaded successfully")
    else:
        # Create new credentials with nonce tracking
        print("Creating new credentials...")
        nonce = 12345  # Choose your nonce
        creds = client.create_api_key(nonce)
        creds['nonce'] = nonce

        # Save securely
        creds_file.write_text(json.dumps(creds, indent=2))
        try:
            creds_file.chmod(0o600)
        except:
            pass

        client.set_api_creds(creds)
        print(f"Credentials created and saved (nonce: {nonce})")

    # Step 3: Verify credentials work
    try:
        orders = client.get_orders()
        print(f"Credentials verified. Found {len(orders)} orders.")
    except Exception as e:
        print(f"Credential verification failed: {e}")
        raise

    return client

# Usage
if __name__ == "__main__":
    client = initial_setup_with_recovery()
    # Now ready to trade
```

## Troubleshooting

### Issue: 401 "Unauthorized/Invalid api key"

**Possible causes**:
1. Credentials were invalidated (new credentials created)
2. Wrong credentials loaded
3. Credentials file corrupted

**Solutions**:
1. Check if new credentials were created elsewhere
2. Verify correct credentials file loaded
3. Regenerate credentials using `create_or_derive_api_creds()`
4. If nonce known, use `derive_api_key(nonce)` to recover

### Issue: Cannot recover credentials

**Cause**: Nonce not saved when credentials were created

**Solution**: Create new credentials (will invalidate old ones)

**Prevention**: Always save nonce when using `create_api_key()`

### Issue: Credentials work locally but not in production

**Possible causes**:
1. Different credential files between environments
2. Environment variables not set in production
3. File permissions preventing credential file read

**Solutions**:
1. Use same credentials across environments (they're wallet-specific, not environment-specific)
2. Verify environment variables set correctly
3. Check file permissions and paths

## Related Documentation

- [Authentication Flow](authentication-flow.md) - L1/L2 authentication architecture
- [py-clob-client Documentation](https://github.com/Polymarket/py-clob-client) - Official Python client library
- [Polymarket L1 Methods](https://docs.polymarket.com/developers/CLOB/clients/methods-l1) - Official credential management docs
