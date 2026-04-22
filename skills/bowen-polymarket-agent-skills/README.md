# Polymarket Agent Skills

A comprehensive agent skill for interacting with the [Polymarket](https://polymarket.com) prediction markets platform. Works with Claude Code, Cursor, Windsurf, and other AI coding assistants.

## Features

- **Full API Coverage**: CLOB, Gamma, Data, and Bridge APIs
- **Real-time Streaming**: WebSocket support for market and user data
- **Trading**: Place, cancel, and manage orders
- **Research**: Discover markets, analyze prices, track positions
- **Authentication**: EIP-712 (L1) and HMAC-SHA256 (L2) support

## Installation

### Claude Code (Terminal)

```bash
# Clone the skill to your Claude Code skills directory
git clone https://github.com/bowen31337/polymarket-agent-skills.git ~/.claude/skills/polymarket

# Or add as a custom skill path in settings
claude config set skillsPath ~/.claude/skills
```

Then in any conversation:
```
Use the polymarket skill to find active markets about AI
```

### Cursor

1. Clone the repository:
   ```bash
   git clone https://github.com/bowen31337/polymarket-agent-skills.git
   ```

2. Add to your project's `.cursor/skills/` directory:
   ```bash
   mkdir -p .cursor/skills
   cp -r polymarket-agent-skills .cursor/skills/polymarket
   ```

3. Or reference in `.cursorrules`:
   ```
   Use the polymarket skill from .cursor/skills/polymarket for prediction market tasks.
   ```

### Windsurf

1. Clone to your Windsurf skills directory:
   ```bash
   git clone https://github.com/bowen31337/polymarket-agent-skills.git ~/.windsurf/skills/polymarket
   ```

2. Reference in your cascade:
   ```
   @skill polymarket
   Find markets about the 2024 election
   ```

### Cline / Continue / Other VS Code Extensions

1. Clone the repository to your project:
   ```bash
   git clone https://github.com/bowen31337/polymarket-agent-skills.git ./skills/polymarket
   ```

2. Add to your AI assistant's context:
   ```
   Use the skill defined in ./skills/polymarket/SKILL.md for Polymarket tasks
   ```

### Generic Setup (Any Agent)

Copy the `SKILL.md` file content into your agent's system prompt or knowledge base:

```bash
curl -s https://raw.githubusercontent.com/bowen31337/polymarket-agent-skills/main/SKILL.md
```

## Quick Start

### No Authentication Required

```python
from polymarket import PolymarketClient

async with PolymarketClient() as client:
    # Search for markets
    results = await client.markets.search(query="election", limit_per_type=10)
    for event in results.events:
        print(f"{event.title}: {event.volume}")

    # Get order book
    book = await client.orderbook.get_book(token_id)
    print(f"Best bid: {book.bids[0].price}, Best ask: {book.asks[0].price}")
```

### With Authentication (Trading)

```python
from polymarket import PolymarketClient, Credentials

credentials = Credentials(
    api_key="your-api-key",
    secret="your-secret",
    passphrase="your-passphrase",
)

async with PolymarketClient(
    private_key="0x...",
    credentials=credentials,
) as client:
    # Build and place an order
    order = client.order_builder.buy(token_id, price=0.55, size=100).build()
    result = await client.orders.place_order(order)
    print(f"Order ID: {result.order_id}")
```

## Environment Variables

For trading operations, set these environment variables:

```bash
# Required for trading
export POLY_PRIVATE_KEY="0x..."

# Optional (if you already have API credentials)
export POLY_API_KEY="..."
export POLY_API_SECRET="..."
export POLY_API_PASSPHRASE="..."
```

## SDK Structure

```
polymarket/
├── SKILL.md                 # Main skill file (for AI assistants)
├── scripts/polymarket/      # Python SDK
│   ├── client.py            # Main client facade
│   ├── models/              # Pydantic data models
│   ├── services/            # API service clients
│   └── websocket/           # WebSocket streaming
├── references/              # Detailed documentation
│   ├── api-quick-ref.md     # All endpoints
│   ├── trading-workflows.md # Order patterns
│   ├── market-research.md   # Discovery patterns
│   ├── authentication.md    # Auth flows
│   └── websocket-guide.md   # Streaming guide
└── assets/examples/         # Example scripts
    ├── market_scanner.py    # Discover markets
    ├── get_positions.py     # Track positions
    ├── stream_orderbook.py  # Real-time prices
    └── place_order.py       # Trading example
```

## API Services

| Service | Description | Auth Required |
|---------|-------------|---------------|
| `client.markets` | Market discovery, events, search | No |
| `client.orderbook` | Order book, prices, spreads | No |
| `client.positions` | User positions, P&L tracking | No |
| `client.bridge` | Deposits, withdrawals | No |
| `client.orders` | Place/cancel orders | Yes (L2) |
| `client.trades` | Trade history | Yes (L2) |
| `client.account` | Balance, allowance | Yes (L2) |

## Examples

### Market Research (No Auth)

```bash
# Run the market scanner
python assets/examples/market_scanner.py

# Track positions for a wallet
python assets/examples/get_positions.py 0x...

# Stream order book updates
python assets/examples/stream_orderbook.py <token_id>
```

### Trading (Requires Auth)

```bash
# Set your private key
export POLY_PRIVATE_KEY="0x..."

# Place an order
python assets/examples/place_order.py <token_id> BUY 0.55 10
```

## Dependencies

```bash
pip install httpx pydantic websockets eth-account
```

## Documentation

- [API Quick Reference](references/api-quick-ref.md) - All endpoints
- [Trading Workflows](references/trading-workflows.md) - Order lifecycle
- [Market Research](references/market-research.md) - Discovery patterns
- [Authentication Guide](references/authentication.md) - L1/L2 auth
- [WebSocket Guide](references/websocket-guide.md) - Real-time streaming

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
