import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const categories = [
  {
    slug: "binance",
    label: "Binance",
    sources: [
      {
        dir: "binance-skills-hub",
        url: "https://github.com/binance/binance-skills-hub",
        install: "npx skills add https://github.com/binance/binance-skills-hub"
      }
    ]
  },
  {
    slug: "okx",
    label: "OKX",
    sources: [
      {
        dir: "okx-onchainos-skills",
        url: "https://github.com/okx/onchainos-skills",
        install: "npx skills add okx/onchainos-skills"
      },
      {
        dir: "okx-agent-skills",
        url: "https://github.com/okx/agent-skills",
        install: "npm install -g @okx_ai/okx-trade-mcp @okx_ai/okx-trade-cli"
      }
    ]
  },
  {
    slug: "bybit",
    label: "Bybit",
    sources: [
      {
        dir: "bybit-skills",
        url: "https://github.com/bybit-exchange/skills",
        install: "直接使用仓库根目录 SKILL.md"
      }
    ]
  },
  {
    slug: "crypto-com",
    label: "Crypto.com",
    sources: [
      {
        dir: "crypto-agent-trading",
        url: "https://github.com/crypto-com/crypto-agent-trading",
        install: "npx skills add crypto-com/crypto-agent-trading/crypto-com-app -g -y"
      }
    ]
  },
  {
    slug: "coinbase",
    label: "Coinbase",
    sources: [
      {
        dir: "coinbase-agentic-wallet-skills",
        url: "https://github.com/coinbase/agentic-wallet-skills",
        install: "npx skills add coinbase/agentic-wallet-skills"
      }
    ]
  },
  {
    slug: "uniswap",
    label: "Uniswap",
    sources: [
      {
        dir: "uniswap-ai",
        url: "https://github.com/Uniswap/uniswap-ai",
        install: "npx skills add Uniswap/uniswap-ai"
      }
    ]
  },
  {
    slug: "jupiter",
    label: "Jupiter",
    sources: [
      {
        dir: "jupiter-agent-skills",
        url: "https://github.com/jup-ag/agent-skills",
        install: "npx skills add jup-ag/agent-skills"
      }
    ]
  },
  {
    slug: "polymarket",
    label: "Polymarket",
    sources: [
      {
        dir: "polymarket-agent-skills",
        url: "https://github.com/Polymarket/agent-skills",
        install: "直接读取仓库 SKILL.md"
      },
      {
        dir: "polymarket-agents",
        url: "https://github.com/Polymarket/agents",
        install: "pip install -r requirements.txt 后按 README 配置"
      },
      {
        dir: "poly-skills-website",
        url: "https://github.com/DevAgarwal2/poly-skills-website",
        install: "目录站，未见标准安装命令"
      },
      {
        dir: "mjunaidca-polymarket-skills",
        url: "https://github.com/mjunaidca/polymarket-skills",
        install: "npx skills add mjunaidca/polymarket-skills"
      },
      {
        dir: "bowen-polymarket-agent-skills",
        url: "https://github.com/bowen31337/polymarket-agent-skills",
        install: "git clone https://github.com/bowen31337/polymarket-agent-skills.git ~/.claude/skills/polymarket"
      },
      {
        dir: "kjhelgason-polymarket-agent-skills",
        url: "https://github.com/KJHelgason/Polymarket_Agent_skills",
        install: "git clone 后复制到 .claude/skills/polymarket"
      },
      {
        dir: "openclaw-decker-polymarket",
        url: "https://github.com/openclaw/skills/blob/main/skills/gigshow/decker-polymarket/SKILL.md",
        install: "OpenClaw skill 路径"
      },
      {
        dir: "cloddsbot-trading-polymarket",
        url: "https://github.com/alsk1992/CloddsBot/blob/main/src/skills/bundled/trading-polymarket/SKILL.md",
        install: "CloddsBot bundled skill"
      }
    ],
    skipped: [
      {
        title: "SkillsAuth: nousresearch/polymarket",
        reason: "README only provides a SkillsAuth page, not a GitHub repository URL.",
        url: "https://skillsauth.com/skills/nousresearch/polymarket",
        install: "npx skillsauth add nousresearch/hermes-agent polymarket"
      }
    ]
  },
  {
    slug: "gmgn",
    label: "GMGN",
    sources: [
      {
        dir: "gmgn-skills",
        url: "https://github.com/GMGNAI/gmgn-skills",
        install: "npx skills add GMGNAI/gmgn-skills"
      }
    ]
  },
  {
    slug: "surf",
    label: "Surf",
    sources: [
      {
        dir: "surf-skills",
        url: "https://github.com/asksurf-ai/surf-skills",
        install: "npx skills add asksurf-ai/surf-skills --skill surf"
      }
    ]
  },
  {
    slug: "solana",
    label: "Solana",
    sources: [
      {
        dir: "awesome-solana-ai",
        url: "https://github.com/solana-foundation/awesome-solana-ai",
        install: "目录型资源"
      },
      {
        dir: "solana-clawd",
        url: "https://github.com/x402agent/solana-clawd",
        install: "npx skills add x402agent/solana-clawd"
      }
    ]
  },
  {
    slug: "bnb-chain",
    label: "BNB Chain",
    sources: [
      {
        dir: "bnbchain-skills",
        url: "https://github.com/bnb-chain/bnbchain-skills",
        install: "npx skills add bnb-chain/bnbchain-skills"
      }
    ]
  },
  {
    slug: "bankr",
    label: "Bankr",
    sources: [
      {
        dir: "bankr-skills",
        url: "https://github.com/BankrBot/skills",
        install: "install the [skill-name] skill from https://github.com/BankrBot/skills/tree/main/[skill-name]"
      }
    ]
  },
  {
    slug: "panews",
    label: "PANews",
    sources: [
      {
        dir: "panews-skills",
        url: "https://github.com/panewslab/skills",
        install: "npx skills add https://github.com/panewslab/skills --skill panews-creator 等"
      }
    ]
  },
  {
    slug: "6551",
    label: "6551 Daily News",
    sources: [
      {
        dir: "daily-news",
        url: "https://github.com/6551Team/daily-news",
        install: "OpenClaw: cp -r openclaw-skill/daily-news ~/.openclaw/skills/6551-daily-news"
      }
    ]
  },
  {
    slug: "slowmist",
    label: "SlowMist",
    sources: [
      {
        dir: "misttrack-skills",
        url: "https://github.com/slowmist/misttrack-skills",
        install: "npx skills add slowmist/misttrack-skills"
      }
    ]
  },
  {
    slug: "byreal",
    label: "Byreal",
    sources: [
      {
        dir: "byreal-agent-skills",
        url: "https://github.com/byreal-git/byreal-agent-skills",
        install: "npx skills add byreal-git/byreal-agent-skills"
      }
    ]
  },
  {
    slug: "coinank",
    label: "CoinAnk",
    sources: [
      {
        dir: "coinank-openapi-skill",
        url: "https://github.com/coinank/coinank-openapi-skill",
        install: "git clone https://github.com/coinank/coinank-openapi-skill.git ~/.openclaw/skills/coinank-openapi-skill"
      }
    ]
  }
];

const usageHeadings = [
  /when to use/i,
  /use cases?/i,
  /command index/i,
  /commands?/i,
  /how to use/i,
  /quick start/i,
  /getting started/i,
  /client setup/i,
  /usage/i,
  /install/i,
  /setup/i
];

const report = {
  generated_at: new Date().toISOString(),
  categories: [],
  skipped_sources: []
};

for (const category of categories) {
  const categoryReport = {
    slug: category.slug,
    label: category.label,
    sources: [],
    skill_count: 0
  };

  for (const source of category.sources) {
    const fullSourceDir = path.join(root, "skills", source.dir);
    const skillPaths = fs.existsSync(fullSourceDir) ? findSkillFiles(fullSourceDir) : [];
    const items = [];

    categoryReport.sources.push({
      dir: source.dir,
      path: path.relative(root, fullSourceDir),
      data: path.join("skills", source.dir, "data.json"),
      url: source.url,
      install: source.install,
      found_skill_files: skillPaths.length
    });

    for (const skillPath of skillPaths) {
      const markdown = fs.readFileSync(skillPath, "utf8");
      const parsed = parseSkill(markdown);
      const relativeSkillPath = path.relative(root, skillPath);
      const title = parsed.name || parsed.h1 || path.basename(path.dirname(skillPath));
      const id = toId(`${category.slug}-${source.dir}-${path.dirname(path.relative(fullSourceDir, skillPath)) || title}`);

      items.push({
        id,
        title,
        summary: parsed.description || parsed.firstParagraph || "",
        usage: parsed.usage || parsed.firstParagraph || parsed.description || "",
        category: category.slug,
        category_title: category.label,
        source: {
          name: source.dir,
          repository: source.url,
          install: source.install
        },
        skill_path: relativeSkillPath
      });
    }

    items.sort((a, b) => a.title.localeCompare(b.title));
    categoryReport.skill_count += items.length;

    if (fs.existsSync(fullSourceDir)) {
      fs.writeFileSync(
        path.join(fullSourceDir, "data.json"),
        `${JSON.stringify(items, null, 2)}\n`
      );
    }
  }

  report.categories.push(categoryReport);

  for (const skipped of category.skipped || []) {
    report.skipped_sources.push({ category: category.slug, ...skipped });
  }
}

fs.writeFileSync(
  path.join(root, "skills", "manifest.json"),
  `${JSON.stringify({
    generated_at: report.generated_at,
    categories: categories.map((category) => ({
      slug: category.slug,
      label: category.label,
      sources: category.sources.map((source) => ({
        dir: source.dir,
        path: `skills/${source.dir}`,
        data: `skills/${source.dir}/data.json`,
        url: source.url,
        install: source.install
      })),
      skipped: category.skipped || []
    }))
  }, null, 2)}\n`
);

fs.writeFileSync(
  path.join(root, "skills", "download-report.json"),
  `${JSON.stringify(report, null, 2)}\n`
);

const generatedSourceFiles = report.categories.reduce((count, category) => count + category.sources.length, 0);
console.log(`Generated ${generatedSourceFiles} source data files across ${report.categories.length} categories.`);
for (const category of report.categories) {
  console.log(`${category.slug}: ${category.skill_count} skills`);
}
if (report.skipped_sources.length > 0) {
  console.log(`Skipped ${report.skipped_sources.length} non-GitHub source(s).`);
}

function findSkillFiles(dir) {
  const results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (shouldSkipDirectory(entry.name)) continue;
      results.push(...findSkillFiles(fullPath));
    } else if (entry.isFile() && entry.name === "SKILL.md") {
      results.push(fullPath);
    }
  }

  return results.sort();
}

function shouldSkipDirectory(name) {
  return name.startsWith(".") ||
    name === "node_modules" ||
    name === "dist" ||
    name === "build" ||
    name === "coverage";
}

function parseSkill(markdown) {
  const { frontmatter, body } = splitFrontmatter(markdown);
  const meta = parseFrontmatter(frontmatter);
  const h1 = body.match(/^#\s+(.+)$/m)?.[1]?.trim();
  const firstParagraph = cleanText(extractFirstParagraph(body));
  const usage = cleanText(extractUsage(body));

  return {
    name: meta.name,
    description: cleanText(meta.description),
    h1,
    firstParagraph,
    usage
  };
}

function splitFrontmatter(markdown) {
  if (!markdown.startsWith("---\n")) {
    return { frontmatter: "", body: markdown };
  }

  const end = markdown.indexOf("\n---", 4);
  if (end === -1) {
    return { frontmatter: "", body: markdown };
  }

  return {
    frontmatter: markdown.slice(4, end).trim(),
    body: markdown.slice(end + 4).trim()
  };
}

function parseFrontmatter(frontmatter) {
  const meta = {};
  const lines = frontmatter.split(/\r?\n/);

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;

    const key = match[1];
    let value = match[2].trim();

    if (value === "|" || value === ">") {
      const block = [];
      i += 1;
      while (i < lines.length && (/^\s+/.test(lines[i]) || lines[i].trim() === "")) {
        block.push(lines[i].replace(/^\s{2}/, ""));
        i += 1;
      }
      i -= 1;
      value = block.join("\n").trim();
    }

    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }

    meta[key] = value;
  }

  return meta;
}

function extractFirstParagraph(body) {
  const withoutHeading = body.replace(/^#\s+.+$/m, "").trim();
  const paragraphs = withoutHeading.split(/\n\s*\n/);
  const paragraph = paragraphs.find((value) => {
    const trimmed = value.trim();
    return trimmed && !trimmed.startsWith("|") && !trimmed.startsWith("```") && !trimmed.startsWith("<");
  });
  return paragraph || "";
}

function extractUsage(body) {
  const lines = body.split(/\r?\n/);

  for (const pattern of usageHeadings) {
    for (let i = 0; i < lines.length; i += 1) {
      const heading = lines[i].match(/^(#{2,4})\s+(.+)$/);
      if (!heading || !pattern.test(heading[2])) continue;

      const level = heading[1].length;
      const chunk = [];

      for (let j = i + 1; j < lines.length; j += 1) {
        const nextHeading = lines[j].match(/^(#{1,4})\s+(.+)$/);
        if (nextHeading && nextHeading[1].length <= level) break;
        chunk.push(lines[j]);
      }

      const text = chunk.join("\n").trim();
      if (isUsefulUsage(text)) return limitText(text, 1400);
    }
  }

  return "";
}

function isUsefulUsage(value) {
  const compact = value
    .replace(/```[a-zA-Z]*\n?/g, "")
    .replace(/`/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return compact.length >= 40;
}

function cleanText(value) {
  return limitText(String(value || "")
    .replace(/\r/g, "")
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<IMPORTANT>/g, "")
    .replace(/<\/IMPORTANT>/g, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim(), 1600);
}

function limitText(value, limit) {
  if (value.length <= limit) return value;
  return `${value.slice(0, limit - 1).trim()}…`;
}

function toId(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
