# Market Resolution Mechanics

Understanding how Polymarket markets resolve, including the UMA Oracle dispute process and why payouts may take days after an event concludes.

## Overview

Market resolution on Polymarket is **not instant**. After an event concludes, there is a multi-step verification process that can take hours to days depending on whether the outcome is disputed.

**Key insight:** Users expecting immediate payouts after an event will be disappointed. Understanding the resolution timeline manages expectations and prevents unnecessary support requests.

## Resolution States

Markets progress through distinct states from active trading to final resolution.

| State | API Fields | Trading | Redemption | Typical Duration |
|-------|-----------|---------|------------|------------------|
| **Open** | `active=true` | Yes | No | Until event concludes |
| **Closed (Pending)** | `closed=true`, `resolved=false` | No | No | Hours to days |
| **Proposed** | (on-chain) | No | No | 2 hours |
| **Disputed** | (on-chain) | No | No | 2+ hours (first), 48+ hours (DVM) |
| **Resolved** | `resolved=true` | No | Yes | Final |

### State Detection Code

```python
def get_market_resolution_status(market: dict) -> dict:
    """
    Get comprehensive resolution status for a market.

    States:
    - open: Trading active
    - closed_pending: Trading stopped, awaiting resolution
    - resolved: Final, redemption available

    Note: Proposed/Disputed states require on-chain queries
    to the UMA Oracle contract.
    """
    status = {
        "state": "unknown",
        "trading_allowed": False,
        "redemption_allowed": False,
        "details": {}
    }

    # Check resolved first (terminal state)
    if market.get("resolved") or market.get("resolvedAt"):
        status["state"] = "resolved"
        status["redemption_allowed"] = True
        status["details"] = {
            "winner": market.get("winner") or market.get("winningOutcome"),
            "resolved_at": market.get("resolvedAt")
        }
        return status

    # Check if closed but not resolved
    if market.get("closed") or not market.get("active"):
        status["state"] = "closed_pending"
        status["details"]["closed_at"] = market.get("updatedAt")
        status["details"]["note"] = "Awaiting UMA Oracle resolution"
        return status

    # Open for trading
    status["state"] = "open"
    status["trading_allowed"] = True
    status["details"]["end_date"] = market.get("endDate")

    return status


def analyze_resolution_readiness(market: dict) -> dict:
    """Analyze when a market might resolve."""
    from datetime import datetime, timezone

    status = get_market_resolution_status(market)

    result = {
        "current_state": status["state"],
        "can_trade": status["trading_allowed"],
        "can_redeem": status["redemption_allowed"]
    }

    if status["state"] == "resolved":
        result["message"] = "Market resolved. Redemption available."
        result["action"] = "Redeem winning positions"

    elif status["state"] == "closed_pending":
        result["message"] = "Market closed, awaiting resolution proposal."
        result["estimated_wait"] = "Hours to days depending on event type"
        result["action"] = "Monitor for resolution or disputes"

    elif status["state"] == "open":
        end_date = market.get("endDate")
        if end_date:
            result["end_date"] = end_date
            result["message"] = f"Market open until {end_date}"
        result["action"] = "Trade normally"

    return result
```

## UMA Oracle Resolution Process

Polymarket uses the UMA Optimistic Oracle for market resolution. This provides decentralized, dispute-resistant resolution but introduces timing delays.

### Resolution Timeline

```
Event Concludes
      |
      v
Market Closes (trading stops)
      |
      v
Proposal Submitted (by whitelisted proposer)
      |
      +-- 2-hour challenge window
      |
      v
No Dispute? ---------> Resolution Finalized
      |                       |
      v                       v
   Disputed              Redemption Enabled
      |
      v
New Proposal Submitted
      |
      +-- 2-hour challenge window
      |
      v
No Dispute? ---------> Resolution Finalized
      |
      v
Disputed Again
      |
      v
Escalates to UMA DVM (Decentralized Verification Mechanism)
      |
      +-- 48-hour voting period
      |
      v
DVM Vote Concludes
      |
      v
Resolution Finalized
      |
      v
Redemption Enabled
```

### Timeline Summary

| Scenario | Time from Event End | Common Causes |
|----------|---------------------|---------------|
| **Smooth resolution** | 2-4 hours | Clear outcome, no disputes |
| **Single dispute** | 4-8 hours | Ambiguous wording, edge case |
| **DVM escalation** | 48+ hours | Contentious outcome, large positions at stake |

### January 2026 Update: Whitelisted Proposers

As of January 2026, Polymarket uses whitelisted proposers for market resolution:

- Only approved addresses can submit initial resolution proposals
- This reduces spam proposals and speeds up typical resolution
- Disputes can still be submitted by anyone
- DVM escalation remains available for contentious outcomes

## Understanding Disputes

### Why Disputes Happen

1. **Ambiguous market wording** - Resolution criteria unclear
2. **Edge cases** - Event outcome falls between defined outcomes
3. **Information disagreement** - Different sources report different outcomes
4. **Gaming attempts** - Losing side disputes to delay payout (rare, costly)

### Dispute Process Details

**First Dispute:**
- Anyone can dispute a proposal within 2-hour window
- Must post bond (returned if dispute successful)
- Triggers new 2-hour proposal window

**Second Dispute (DVM Escalation):**
- If second proposal also disputed
- Escalates to UMA token holder vote
- 48-hour voting period
- UMA token holders vote on correct resolution
- Result is final and binding

### What Users Should Know

1. **Disputes are rare** - Most markets resolve within hours
2. **Large markets may attract more scrutiny** - Higher stakes = more attention to resolution
3. **Dispute doesn't mean your position is wrong** - Just that someone challenged the resolution
4. **You cannot speed up resolution** - Must wait for process to complete

## Redemption Process

### When Redemption is Available

```python
def can_redeem_position(market: dict) -> dict:
    """Check if position can be redeemed."""
    status = get_market_resolution_status(market)

    if status["state"] != "resolved":
        return {
            "can_redeem": False,
            "reason": f"Market not resolved (current state: {status['state']})",
            "action": "Wait for resolution to complete"
        }

    winner = status["details"].get("winner")
    if not winner:
        return {
            "can_redeem": False,
            "reason": "Winner not determined in resolution data",
            "action": "Check market details or contact support"
        }

    return {
        "can_redeem": True,
        "winning_outcome": winner,
        "payout_per_share": 1.00,  # $1 per winning share
        "action": "Redeem winning shares through UI or contract"
    }
```

### Redemption Mechanics

- **Winning shares:** Pay out $1.00 per share
- **Losing shares:** Worth $0.00, no redemption needed
- **Redemption method:** Through Polymarket UI or direct contract call
- **No time limit:** Can redeem anytime after resolution (but why wait?)

## Warning Signs

| Symptom | Likely Cause | What to Do |
|---------|--------------|------------|
| Market ended days ago, no payout | Pending resolution or dispute | Check resolution status |
| Status shows "pending" not "resolved" | Normal delay, awaiting proposal | Wait 24-48 hours |
| UMA shows active dispute | Resolution being contested | Wait for dispute resolution |
| Winner shows but can't redeem | Contract state may lag API | Retry after a few minutes |

## Checking Resolution Status

### Via API

```python
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"

def check_resolution_status(market_id):
    """Check resolution status for a specific market."""
    response = requests.get(f"{GAMMA_URL}/markets/{market_id}")
    response.raise_for_status()
    market = response.json()

    status = get_market_resolution_status(market)

    print(f"Market: {market.get('question', 'Unknown')}")
    print(f"State: {status['state']}")
    print(f"Can Trade: {status['trading_allowed']}")
    print(f"Can Redeem: {status['redemption_allowed']}")

    if status['redemption_allowed']:
        print(f"Winner: {status['details'].get('winner')}")
        print(f"Resolved At: {status['details'].get('resolved_at')}")
    elif status['state'] == 'closed_pending':
        print("Awaiting resolution - check back later")

    return status
```

### Via UMA Oracle (Advanced)

For real-time dispute status, query the UMA Optimistic Oracle contract directly:

```python
# Note: Requires web3 setup and contract ABI
# This is advanced usage - most users should rely on Gamma API

def check_uma_proposal_status(condition_id):
    """
    Check UMA Oracle for proposal/dispute status.

    Requires:
    - web3 connection to Polygon
    - UMA OptimisticOracle contract ABI
    - Knowledge of assertion ID for market
    """
    # Implementation depends on specific UMA contract version
    # and market structure
    pass
```

## Best Practices

### For Users

1. **Don't expect instant payouts** - Factor 2-48 hours into your planning
2. **Check resolution status before panicking** - Use API to see current state
3. **Understand dispute timeline** - If disputed, patience is required
4. **Redeem promptly once resolved** - No benefit to waiting

### For Developers

1. **Poll resolution status** - Check every few minutes for state changes
2. **Handle all states** - Don't assume market goes open -> resolved
3. **Display estimated timelines** - Help users understand expected wait
4. **Monitor for disputes** - Alert users if their positions are in disputed markets

### Resolution Polling Pattern

```python
import time

def wait_for_resolution(market_id, poll_interval=300, max_wait=86400):
    """
    Poll for market resolution.

    Args:
        market_id: Market to monitor
        poll_interval: Seconds between checks (default 5 minutes)
        max_wait: Maximum seconds to wait (default 24 hours)

    Returns:
        Resolution status when resolved, or timeout status
    """
    start_time = time.time()

    while (time.time() - start_time) < max_wait:
        status = check_resolution_status(market_id)

        if status["state"] == "resolved":
            return {
                "resolved": True,
                "winner": status["details"].get("winner"),
                "wait_time": time.time() - start_time
            }

        print(f"Still pending... checking again in {poll_interval}s")
        time.sleep(poll_interval)

    return {
        "resolved": False,
        "state": status["state"],
        "message": "Timeout waiting for resolution"
    }
```

## Related Documentation

- [Events and Metadata](../market-discovery/events-and-metadata.md) - Market state detection
- [Gamma API Overview](../market-discovery/gamma-api-overview.md) - Querying market data
- [NegRisk Trading](./negrisk-trading.md) - Multi-outcome resolution patterns (coming soon)

## References

- [UMA Optimistic Oracle](https://docs.uma.xyz/protocol-overview/how-does-umas-oracle-work) - Official UMA documentation
- [Polymarket Resolution](https://docs.polymarket.com/polymarket-learn/markets/how-are-markets-resolved) - How markets resolve
- [UMA Oracle Update (Jan 2026)](https://www.theblock.co/post/366507/polymarket-uma-oracle-update) - Whitelisted proposer system

---

**Last updated:** 2026-01-31
**Covers:** EDGE-05 (Resolution States), EDGE-06 (UMA Oracle Disputes)
