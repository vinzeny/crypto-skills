# Polymarket Skills for Claude Code

A knowledge package that gives Claude deep expertise in Polymarket integration — API patterns, WebSocket handling, edge cases, and troubleshooting.

## What This Does

When loaded, Claude knows Polymarket as well as someone who's built with it extensively:

- Correct authentication flows (L1/L2, API credentials, token approvals)
- All REST API endpoints with request/response schemas
- WebSocket subscription patterns for real-time data
- Edge cases that cause silent failures (tick sizes, minimum orders, precision limits)
- py-clob-client library patterns and gotchas

No more guessing at endpoints or making common mistakes.

## Installation

### Personal Use (all projects)

```bash
git clone https://github.com/KJHelgason/Polymarket_Agent_skills.git
mkdir -p ~/.claude/skills
cp -r Polymarket_Agent_skills ~/.claude/skills/polymarket
```

### Project Use (single project)

```bash
git clone https://github.com/KJHelgason/Polymarket_Agent_skills.git
mkdir -p .claude/skills
cp -r Polymarket_Agent_skills .claude/skills/polymarket
```

## Usage

**Explicit invocation:**
```
/polymarket
```

**Auto-triggers on questions like:**
- "How do I authenticate with Polymarket?"
- "What's the endpoint for placing orders?"
- "Why is my order getting rejected?"

## Modules

| Module | Coverage |
|--------|----------|
| **auth** | API credentials, L1/L2 signing, token approvals, client setup |
| **trading** | Order types, placement, cancellation, balance queries |
| **market-discovery** | Gamma API, market search, event structures |
| **real-time** | WebSocket connections, orderbook streaming, trade feeds |
| **data-analytics** | Portfolio tracking, P&L calculation, trade history |
| **edge-cases** | Troubleshooting, error recovery, common failures |
| **library** | py-clob-client patterns and reference |

## Requirements

- Claude Code (CLI or VS Code extension)
- Git (for installation)

No other dependencies — skills are documentation only.

## Updating

```bash
cd Polymarket_Agent_skills
git pull
cp -r . ~/.claude/skills/polymarket
```

## License

MIT
