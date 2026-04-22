# Polymarket Skills Version

**Current Version:** 1.0.0
**Last Updated:** 2026-02-01
**API Compatibility:** Polymarket CLOB API v1, Gamma API, Data API

## py-clob-client Compatibility

| py-clob-client Version | Compatibility | Notes |
|------------------------|---------------|-------|
| v0.16+ | Fully compatible | Recommended minimum |
| v0.34+ | Fully compatible | Latest tested |

**Installation:**
```bash
pip install py-clob-client
```

## API Endpoints

Track these endpoints for API changes:

| API | Endpoint | Status |
|-----|----------|--------|
| CLOB | `https://clob.polymarket.com` | Stable |
| Gamma | `https://gamma-api.polymarket.com` | Stable |
| Data | `https://data-api.polymarket.com` | Stable |
| WebSocket Market | `wss://ws-subscriptions-clob.polymarket.com/ws/market` | Stable |
| WebSocket User | `wss://ws-subscriptions-clob.polymarket.com/ws/user` | Stable |

## Changelog

### v1.0.0 (2026-02-01)

Initial release of Polymarket API skills.

**Authentication & Setup (auth/)**
- Complete authentication documentation (L1/L2 architecture)
- Wallet types: EOA, Proxy, Safe detection and configuration
- API credentials: creation, storage, recovery, rotation
- Token allowances: USDC.e setup, exchange approvals
- Client initialization: complete setup guide

**Market Discovery (market-discovery/)**
- Gamma API overview and architecture
- Event/market hierarchy documentation
- Search, filtering, and pagination patterns
- Token ID extraction for trading

**Trading Operations (trading/)**
- CLOB API overview and endpoints
- Order types: GTC, GTD, FOK, FAK with decision tree
- Order placement workflow and verification
- Order management: cancellation, batch operations
- Positions and balances queries

**Data Analytics (data-analytics/)**
- Data API overview
- Positions and trade history queries
- Historical price timeseries (via CLOB /prices-history)
- Portfolio export patterns (CSV/JSON)

**Real-Time Data (real-time/)**
- WebSocket architecture and channels
- Market channel: orderbook, price changes, trades
- User channel: order notifications (authenticated)
- Connection management: reconnection, heartbeats

**Edge Cases (edge-cases/)**
- USDC.e vs native USDC confusion
- Order constraints: minimums, precision, tick sizes
- Price interpretation: midpoint vs executable
- Resolution mechanics: UMA disputes, redemption
- NegRisk trading: multi-outcome patterns
- Partial fills: tracking and reconciliation

**Library Reference (library/)**
- Error handling: exception types, recovery patterns
- Production patterns: rate limiting, WebSocket reliability, balance tracking

## Known Limitations

### Geographic Restrictions
- Trading functionality requires non-US access
- Market discovery (Gamma API) is publicly accessible

### Rate Limits
- Polymarket does not publish official rate limits
- Recommended: conservative 0.5-1 second delays between requests
- Burst limits: ~10 requests per 10-second window (observed)

### WebSocket Considerations
- Connections may drop after ~20 minutes of inactivity
- Heartbeat/ping required for long-running connections
- Reconnection logic required for production use

### API Stability
- CLOB API is stable but may add new fields
- Gamma API response schema may evolve
- Always handle unknown fields gracefully

## Checking for Updates

### From Git Repository

```bash
# Navigate to skills directory
cd your-polymarket-skills-location

# Check current version
head -5 VERSION.md

# Pull latest changes
git pull

# Review changelog
cat VERSION.md
```

### Version Comparison

Compare your local VERSION.md with the repository version to identify updates.

## Migration Notes

*No migrations required for v1.0.0 (initial release)*

Future versions will include migration notes for breaking changes.
