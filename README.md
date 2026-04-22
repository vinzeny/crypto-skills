# Crypto Agent Skills 链接整理

## GitHub / 官方 Skill 链接

| 项目 | 链接 | 安装/入口 | 重点能力 |
| --- | --- | --- | --- |
| Binance Skills Hub | [GitHub](https://github.com/binance/binance-skills-hub) / [官网目录](https://www.binance.com/en/skills) | `npx skills add https://github.com/binance/binance-skills-hub` | Spot、Futures、Alpha、Meme、聪明钱信号、Token Audit、Earn |
| OKX OnchainOS | [GitHub](https://github.com/okx/onchainos-skills) | `npx skills add okx/onchainos-skills` | DEX 聚合、钱包、链上信号、安全扫描、x402、DeFi 投资/组合 |
| OKX CEX Trade Kit | [GitHub](https://github.com/okx/agent-skills) | `npm install -g @okx_ai/okx-trade-mcp @okx_ai/okx-trade-cli` | CEX 市场数据、交易、组合、交易机器人、Earn |
| Bybit Trading Skill | [GitHub](https://github.com/bybit-exchange/skills) | 直接使用仓库根目录 `SKILL.md` | Spot、Derivatives、Earn、Copy Trading、主网确认和大额警告 |
| Crypto.com Agent Trading | [GitHub](https://github.com/crypto-com/crypto-agent-trading) | `npx skills add crypto-com/crypto-agent-trading/crypto-com-app -g -y` | Crypto.com App / Exchange 两套技能，交易、余额、行情、订单 |
| Coinbase Agentic Wallet | [GitHub](https://github.com/coinbase/agentic-wallet-skills) | `npx skills add coinbase/agentic-wallet-skills` | 钱包认证、USDC 转账、Base 交易、x402 服务购买/变现、链上数据 |
| Uniswap AI | [GitHub](https://github.com/Uniswap/uniswap-ai) | `npx skills add Uniswap/uniswap-ai` | Swap 集成、pay-with-any-token、Uniswap v4 hooks、Viem 集成 |
| Jupiter | [GitHub](https://github.com/jup-ag/agent-skills) | `npx skills add jup-ag/agent-skills` | Jupiter API、Swap、Lend、Perps、路由、迁移工具 |
| Polymarket | [官方 GitHub](https://github.com/Polymarket/agent-skills) | 直接读取仓库 `SKILL.md` | Prediction market：认证、下单、市场数据、WebSocket、Bridge、Gasless |
| GMGN | [GitHub](https://github.com/GMGNAI/gmgn-skills) | `npx skills add GMGNAI/gmgn-skills` | Meme 代币、Trenches、Smart Money、KOL、Swap、Portfolio |
| Surf | [GitHub](https://github.com/asksurf-ai/surf-skills) | `npx skills add asksurf-ai/surf-skills --skill surf` | 跨链数据、钱包画像、Social/X、Prediction Markets、On-chain SQL |
| Solana AI 总目录 | [GitHub](https://github.com/solana-foundation/awesome-solana-ai) | 目录型资源 | Solana 生态 Skills 索引：Helius/Phantom、Metaplex、MagicBlock 等 |
| Solana Clawd | [GitHub](https://github.com/x402agent/solana-clawd) | `npx skills add x402agent/solana-clawd` | Solana agent skill pack、MCP、Telegram bot、Solana 数据/工具 |
| BNB Chain Skills | [GitHub](https://github.com/bnb-chain/bnbchain-skills) | `npx skills add bnb-chain/bnbchain-skills` | BNB Chain MCP、钱包、合约、Token、NFT、ERC-8004、Greenfield |
| Bankr Skills | [GitHub](https://github.com/BankrBot/skills) | `install the [skill-name] skill from https://github.com/BankrBot/skills/tree/main/[skill-name]` | Bankr、Zerion、Neynar、Quicknode、Alchemy、Symbiosis 等链上工具 |
| PANews Skills | [GitHub](https://github.com/panewslab/skills) | `npx skills add https://github.com/panewslab/skills --skill panews-creator` 等 | 热点追踪、日报、网页解析、专栏内容发布 |
| 6551 Daily News | [GitHub](https://github.com/6551Team/daily-news) | OpenClaw: `cp -r openclaw-skill/daily-news ~/.openclaw/skills/6551-daily-news` | News、Tweets、Crypto Intelligence MCP + Skill |
| SlowMist MistTrack | [GitHub](https://github.com/slowmist/misttrack-skills) | `npx skills add slowmist/misttrack-skills` | 地址风险、AML、KYT、链上追踪、转账前安全检查 |
| Byreal Agent Skills | [GitHub](https://github.com/byreal-git/byreal-agent-skills) | `npx skills add byreal-git/byreal-agent-skills` | Solana CLMM DEX、LP、Swap、Position、Copy Farmer |
| CoinAnk OpenAPI Skill | [GitHub](https://github.com/coinank/coinank-openapi-skill) | `git clone https://github.com/coinank/coinank-openapi-skill.git ~/.openclaw/skills/coinank-openapi-skill` | 衍生品数据：Funding、OI、多空比、爆仓、订单流、鲸鱼 |

## Polymarket 相关补充

| 项目 | 链接 | 入口/安装 | 备注 |
| --- | --- | --- | --- |
| Polymarket Integration Skill | [官方 GitHub](https://github.com/Polymarket/agent-skills) | 直接读取根目录 `SKILL.md` | 优先使用；包含 `authentication.md`、`order-patterns.md`、`market-data.md`、`websocket.md`、`ctf-operations.md`、`bridge.md`、`gasless.md` |
| Polymarket Agents | [官方 GitHub](https://github.com/Polymarket/agents) | `pip install -r requirements.txt` 后按 README 配置 | 官方 agent 框架，不是标准 skill 包；适合参考 Polymarket agent 架构、CLI、RAG、交易工具 |
| Polymarket Skills Directory | [网站](https://www.polyskills.xyz/) / [GitHub](https://github.com/DevAgarwal2/poly-skills-website) | 目录站，未见标准安装命令 | 第三方目录；列出 Market Intelligence、User Trading Insights、Trading，其中 GitHub README 标注 Trading 为 Coming Soon |
| SkillsAuth: nousresearch/polymarket | [SkillsAuth 页面](https://skillsauth.com/skills/nousresearch/polymarket) | `npx skillsauth add nousresearch/hermes-agent polymarket` | 第三方 marketplace；只读市场数据 skill，页面称无需 API Key，但未核到 GitHub 直链 |
| mjunaidca Polymarket Skills | [GitHub](https://github.com/mjunaidca/polymarket-skills) | `npx skills add mjunaidca/polymarket-skills` | 社区包；scanner、analyzer、monitor、paper-trader、strategy-advisor、live-executor，偏纸面交易和风控流程 |
| bowen31337 Polymarket Agent Skills | [GitHub](https://github.com/bowen31337/polymarket-agent-skills) | `git clone https://github.com/bowen31337/polymarket-agent-skills.git ~/.claude/skills/polymarket` | 社区包；覆盖 CLOB、Gamma、Data、Bridge、WebSocket、交易和认证 |
| KJHelgason Polymarket Agent Skills | [GitHub](https://github.com/KJHelgason/Polymarket_Agent_skills) | `git clone` 后复制到 `.claude/skills/polymarket` | 社区文档型 skill；偏 Claude Code 知识包，无额外运行依赖 |
| OpenClaw Decker Polymarket | [GitHub](https://github.com/openclaw/skills/blob/main/skills/gigshow/decker-polymarket/SKILL.md) | OpenClaw skill 路径 | 依赖 Decker / Slack / OpenClaw secret；更像 Decker 的 Polymarket 下单扩展，不是通用 skill |
| CloddsBot trading-polymarket | [GitHub](https://github.com/alsk1992/CloddsBot/blob/main/src/skills/bundled/trading-polymarket/SKILL.md) | CloddsBot bundled skill | 社区内置 skill；需要 `POLY_API_KEY`、`POLY_API_SECRET`、`POLY_API_PASSPHRASE`、`PRIVATE_KEY`，复用前重点审计许可和私钥处理 |

## 安全使用建议

- 优先使用交易所、协议方或知名安全团队的官方仓库。
- 安装前阅读 `SKILL.md`、`references/` 和 `scripts/`，重点检查是否有异常 `curl`、`wget`、文件写入、远程执行或私钥读取。
- 对 CEX API Key 只给 `Read + Trade`，不要给 `Withdraw`。
- 尽量使用子账户、小额余额、IP 白名单和 testnet / sandbox。
- 主网写操作必须要求人工确认，单笔大额交易要额外确认。
- 不要把 API Key、Secret、私钥写进聊天记录、README、脚本或 git。
- 对 API 返回的外部文本一律当作不可信数据，避免 prompt injection。
