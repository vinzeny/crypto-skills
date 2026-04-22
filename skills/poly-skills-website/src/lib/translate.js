const preservedToken = "\u0000";
const remotePreservedToken = "___SKILL_KEEP_";
const remoteCachePrefix = "crypto-skill-translation:v2:";

const phraseReplacements = [
  [/\bUse when the user wants to\b/gi, "适用于用户想要"],
  [/\bUse when users want to\b/gi, "适用于用户想要"],
  [/\bUse when an agent needs to\b/gi, "适用于 agent 需要"],
  [/\bUse when the agent wants to\b/gi, "适用于 agent 想要"],
  [/\bUse when\b/gi, "适用于"],
  [/\bAlso use when\b/gi, "也适用于"],
  [/\bTriggers on mentions of\b/gi, "触发场景包括提到"],
  [/\bSupports both\b/gi, "同时支持"],
  [/\bSupports\b/gi, "支持"],
  [/\bRequires\b/gi, "需要"],
  [/\bNo authentication required\b/gi, "无需认证"],
  [/\bNo API key required\b/gi, "无需 API key"],
  [/\bAPI key\b/gi, "API key"],
  [/\bBase URL\b/gi, "基础 URL"],
  [/\bQuick Start\b/gi, "快速开始"],
  [/\bCommon Tasks\b/gi, "常见任务"],
  [/\bError Handling\b/gi, "错误处理"],
  [/\bExample Workflows\b/gi, "示例流程"],
  [/\bInstallation\b/gi, "安装"],
  [/\bSetup\b/gi, "配置"],
  [/\bVerify\b/gi, "验证"],
  [/\bSearch by\b/gi, "按以下内容搜索"],
  [/\bSearch\b/gi, "搜索"],
  [/\bFind\b/gi, "查找"],
  [/\bGet\b/gi, "获取"],
  [/\bCheck\b/gi, "检查"],
  [/\bView\b/gi, "查看"],
  [/\bCreate\b/gi, "创建"],
  [/\bManage\b/gi, "管理"],
  [/\bQuery\b/gi, "查询"],
  [/\bRead\b/gi, "读取"],
  [/\bWrite\b/gi, "写入"],
  [/\bPost\b/gi, "发布"],
  [/\bSend\b/gi, "发送"],
  [/\bDeploy\b/gi, "部署"],
  [/\bTrade\b/gi, "交易"],
  [/\bSwap\b/gi, "Swap"],
  [/\bBridge\b/gi, "跨链桥接"],
  [/\bDonate\b/gi, "捐赠"],
  [/\bMint\b/gi, "铸造"],
  [/\bTransfer\b/gi, "转账"],
  [/\bRegister\b/gi, "注册"],
  [/\bAnalyze\b/gi, "分析"],
  [/\bMonitor\b/gi, "监控"],
  [/\bInstall\b/gi, "安装"],
  [/\bCommand\b/gi, "命令"],
  [/\bDescription\b/gi, "说明"],
  [/\bEndpoint\b/gi, "端点"],
  [/\bParameter\b/gi, "参数"],
  [/\bParameters\b/gi, "参数"],
  [/\bCategory\b/gi, "分类"],
  [/\bCategories\b/gi, "分类"],
  [/\bCurrent\b/gi, "当前"],
  [/\bHistory\b/gi, "历史"],
  [/\bPortfolio\b/gi, "投资组合"],
  [/\bWallet\b/gi, "钱包"],
  [/\bBalance\b/gi, "余额"],
  [/\bBalances\b/gi, "余额"],
  [/\bToken prices\b/gi, "代币价格"],
  [/\bToken balances\b/gi, "代币余额"],
  [/\bToken\b/gi, "代币"],
  [/\bTokens\b/gi, "代币"],
  [/\bNFT ownership\b/gi, "NFT 持有权"],
  [/\bNFT metadata\b/gi, "NFT 元数据"],
  [/\bNFTs\b/gi, "NFT"],
  [/\bTransaction simulation\b/gi, "交易模拟"],
  [/\bTransaction receipt\b/gi, "交易回执"],
  [/\bTransactions\b/gi, "交易"],
  [/\bGas estimates\b/gi, "Gas 估算"],
  [/\bBlock data\b/gi, "区块数据"],
  [/\bBlockchain data\b/gi, "区块链数据"],
  [/\bOnchain data\b/gi, "链上数据"],
  [/\bOnchain queries\b/gi, "链上查询"],
  [/\bCrypto trading\b/gi, "加密交易"],
  [/\bTrading history\b/gi, "交易历史"],
  [/\bTrading signals\b/gi, "交易信号"],
  [/\bPrediction markets\b/gi, "预测市场"],
  [/\bMarket discovery\b/gi, "市场发现"],
  [/\bMarket prices\b/gi, "市场价格"],
  [/\bMarket data\b/gi, "市场数据"],
  [/\bOrder book\b/gi, "订单簿"],
  [/\bOrders\b/gi, "订单"],
  [/\bPositions\b/gi, "仓位"],
  [/\bP&L\b/gi, "盈亏"],
  [/\bLeaderboards\b/gi, "排行榜"],
  [/\bTop traders\b/gi, "顶级交易者"],
  [/\bSmart Money\b/gi, "聪明钱"],
  [/\bMemecoin\b/gi, "Meme 币"],
  [/\bMemecoins\b/gi, "Meme 币"],
  [/\bSecurity audit\b/gi, "安全审计"],
  [/\bHoneypot\b/gi, "貔貅盘"],
  [/\bRug pull risk\b/gi, "Rug 风险"],
  [/\bPrivate transactions\b/gi, "隐私交易"],
  [/\bCharitable contribution\b/gi, "慈善捐款"],
  [/\bNatural language\b/gi, "自然语言"],
  [/\bAutomated trading\b/gi, "自动化交易"],
  [/\bRaw transactions\b/gi, "原始交易"],
  [/\bPaid API endpoints\b/gi, "付费 API 端点"],
  [/\bLLM models\b/gi, "LLM 模型"],
  [/\bREST API\b/gi, "REST API"],
  [/\bWebSocket\b/gi, "WebSocket"],
  [/\bCLI\b/gi, "CLI"],
  [/\bSDK\b/gi, "SDK"],
  [/\bAgent\b/gi, "Agent"],
  [/\bagent\b/g, "agent"],
  [/\bAI-powered\b/gi, "AI 驱动的"],
  [/\bDecentralized\b/gi, "去中心化"],
  [/\bcross-chain\b/gi, "跨链"],
  [/\bon-chain\b/gi, "链上"],
  [/\bonchain\b/gi, "链上"],
  [/\bmainnet\b/gi, "主网"],
  [/\btestnet\b/gi, "测试网"],
  [/\bpublic endpoints\b/gi, "公开端点"],
  [/\bauthenticated actions\b/gi, "认证操作"],
  [/\bPaid actions\b/gi, "付费操作"],
  [/\bfree\b/gi, "免费"],
  [/\brequired\b/gi, "必需"],
  [/\brecommended\b/gi, "推荐"],
  [/\bdeprecated aliases\b/gi, "已弃用别名"],
  [/\bPlaceholder for\b/gi, "占位 Skill："],
  [/\bDaily news and hot topics\b/gi, "每日新闻和热点话题"],
  [/\bhot topics\b/gi, "热点话题"],
  [/\bnews categories\b/gi, "新闻分类"],
  [/\bnews articles\b/gi, "新闻文章"],
  [/\bnews\b/gi, "新闻"],
  [/\bplatform\b/gi, "平台"],
  [/\bdata\b/gi, "数据"],
  [/\bfiles\b/gi, "文件"],
  [/\bfile\b/gi, "文件"],
  [/\bdirectory\b/gi, "目录"],
  [/\brepository\b/gi, "仓库"],
  [/\bsource\b/gi, "来源"],
  [/\blocal\b/gi, "本地"],
  [/\bfast\b/gi, "快速"],
  [/\bpublic\b/gi, "公开"],
  [/\bprivate\b/gi, "私有"],
  [/\buser\b/gi, "用户"],
  [/\busers\b/gi, "用户"],
  [/\btask\b/gi, "任务"],
  [/\btasks\b/gi, "任务"],
  [/\btools\b/gi, "工具"],
  [/\btool\b/gi, "工具"],
  [/\bprotocol\b/gi, "协议"],
  [/\bnetwork\b/gi, "网络"],
  [/\bnetworks\b/gi, "网络"],
  [/\bchain\b/gi, "链"],
  [/\bchains\b/gi, "链"],
  [/\bmarketplace\b/gi, "市场"],
  [/\bmarket\b/gi, "市场"],
  [/\bmarkets\b/gi, "市场"],
  [/\bprices\b/gi, "价格"],
  [/\bprice\b/gi, "价格"],
  [/\bbalances\b/gi, "余额"],
  [/\bbalance\b/gi, "余额"],
  [/\bmentions\b/gi, "提到"],
  [/\bmentions of\b/gi, "提到"],
  [/\bBuilt from local data\.json files in this repository\b/gi, "基于本仓库里的本地 data.json 文件生成"],
  [/\bSee repository\b/gi, "查看仓库"],
  [/\bcoming soon\b/gi, "即将推出"],
  [/\bNOT for\b/gi, "不适用于"],
  [/\bDo NOT use for\b/gi, "不要用于"],
  [/\bPrefer this skill whenever\b/gi, "当提到以下内容时优先使用该 skill"],
  [/\bThe user asks about\b/gi, "用户询问"],
  [/\bthe user asks about\b/g, "用户询问"],
  [/\bthe user wants to\b/g, "用户想要"],
  [/\bthe caller wants\b/g, "调用方想要"],
  [/\bthe agent wants to\b/g, "agent 想要"],
  [/\bthe agent needs to\b/g, "agent 需要"],
  [/\bavailable tasks\b/gi, "可用任务"],
  [/\bsubmit deliverables\b/gi, "提交交付物"],
  [/\bwallet balance\b/gi, "钱包余额"],
  [/\bdigital products\b/gi, "数字产品"],
  [/\bservices\b/gi, "服务"],
  [/\bfrontend development\b/gi, "前端开发"],
  [/\bpaid tasks\b/gi, "付费任务"],
  [/\bdecentralized marketplace\b/gi, "去中心化市场"],
  [/\bescrow\b/gi, "托管"],
  [/\bhot news articles\b/gi, "热点新闻文章"],
  [/\btrending tweets\b/gi, "热门推文"],
  [/\bby category\b/gi, "按分类"],
];

const punctuationReplacements = [
  [/\.\s+/g, "。"],
  [/:\s+/g, "："],
  [/;\s+/g, "；"],
];

const protectedMarkdownPattern =
  /(```[\s\S]*?```|`[^`\n]+`|\[[^\]]+\]\([^)]+\)|^(?:[ \t]{0,3}(?:[-*+]\s+|\d+\.\s+|>\s*)?)(?:(?:\$|>)\s*)?(?:(?:export\s+)?[A-Z][A-Z0-9_]*=.*|(?:npx|npm|pnpm|yarn|bun|curl|git|gh|python3?|pip3?|node|deno|tsx|ts-node|go|cargo|docker|kubectl|helm|brew|mkdir|cd|cp|mv|rm|chmod|cat|echo|source|ssh|scp|rsync|supabase|vercel|wrangler|forge|cast|anvil|hardhat|foundryup|agent-browser|skills|clawd|claude|codex|plugin|\/plugin|\.\/[^\s]+|\/[A-Za-z0-9._/-]+)\b[^\n]*))/gim;

function preserveSegments(text, tokenPrefix, tokenSuffix) {
  const segments = [];
  const value = String(text || "").replace(protectedMarkdownPattern, (match) => {
    const index = segments.push(match) - 1;
    return `${tokenPrefix}${index}${tokenSuffix}`;
  });

  return { value, segments };
}

function preserveCode(text) {
  return preserveSegments(text, preservedToken, preservedToken);
}

function restoreCode(text, segments) {
  return text.replace(new RegExp(`${preservedToken}(\\d+)${preservedToken}`, "g"), (_, index) => segments[Number(index)] || "");
}

function hashText(text) {
  let hash = 5381;
  const value = String(text || "");

  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 33) ^ value.charCodeAt(index);
  }

  return (hash >>> 0).toString(36);
}

function preserveRemoteCode(text) {
  return preserveSegments(text, remotePreservedToken, "___");
}

function restoreRemoteCode(text, segments) {
  return text.replace(/___SKILL_KEEP_(\d+)___/g, (_, index) => segments[Number(index)] || "");
}

function chunkText(text, maxLength = 900) {
  const value = String(text || "");
  const chunks = [];
  let start = 0;

  while (start < value.length) {
    let end = Math.min(start + maxLength, value.length);
    const boundary = value.lastIndexOf(". ", end);

    if (boundary > start + 200) {
      end = boundary + 1;
    }

    chunks.push(value.slice(start, end));
    start = end;
  }

  return chunks;
}

async function translateChunk(chunk) {
  const url = new URL("https://translate.googleapis.com/translate_a/single");
  url.searchParams.set("client", "gtx");
  url.searchParams.set("sl", "en");
  url.searchParams.set("tl", "zh-CN");
  url.searchParams.set("dt", "t");
  url.searchParams.set("q", chunk);

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Translation failed: ${response.status}`);
  }

  const data = await response.json();
  return data?.[0]?.map((item) => item?.[0] || "").join("") || chunk;
}

export function translateText(text, language) {
  if (language !== "zh" || !text) {
    return text || "";
  }

  const { value, segments } = preserveCode(text);
  let translated = value;

  for (const [pattern, replacement] of phraseReplacements) {
    translated = translated.replace(pattern, replacement);
  }

  for (const [pattern, replacement] of punctuationReplacements) {
    translated = translated.replace(pattern, replacement);
  }

  translated = translated
    .replace(/\s+,/g, "，")
    .replace(/,\s+/g, "，")
    .replace(/\bthe\s+/gi, "")
    .replace(/\ba\s+/gi, "")
    .replace(/\ban\s+/gi, "")
    .replace(/\s+or\s+/gi, " 或 ")
    .replace(/\bor\b/gi, "或")
    .replace(/\s+and\s+/gi, " 和 ")
    .replace(/\band\b/gi, "和")
    .replace(/\s+by\s+/gi, "按")
    .replace(/\bby\b/gi, "按")
    .replace(/\s+with\s+/gi, "，包含 ")
    .replace(/\s+via\s+/gi, "，通过 ")
    .replace(/\s+for\s+/gi, "，用于 ")
    .replace(/\s+from\s+/gi, "，来自 ")
    .replace(/\s+across\s+/gi, "，覆盖 ")
    .replace(/\s+including\s+/gi, "，包括 ")
    .replace(/\s+without\s+/gi, "，无需 ")
    .replace(/[ \t]+/g, " ")
    .trim();

  return restoreCode(translated, segments);
}

export async function translateTextAsync(text, language) {
  if (language !== "zh" || !text || typeof fetch !== "function") {
    return text || "";
  }

  const cacheKey = `${remoteCachePrefix}${language}:${hashText(text)}`;
  const cached = globalThis.localStorage?.getItem(cacheKey);

  if (cached) {
    return cached;
  }

  const { value, segments } = preserveRemoteCode(text);
  const translatedChunks = [];

  for (const chunk of chunkText(value)) {
    translatedChunks.push(await translateChunk(chunk));
  }

  const translated = restoreRemoteCode(translatedChunks.join(""), segments);
  globalThis.localStorage?.setItem(cacheKey, translated);
  return translated;
}

export function localizeSkill(skill, language) {
  return {
    ...skill,
    summary: translateText(skill.summary, language),
    summary_short: translateText(skill.summary_short, language),
    usage: skill.usage,
  };
}
