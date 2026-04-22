import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(__dirname, "..");
const skillsRoot = path.resolve(appRoot, "..");
const outputPath = path.join(appRoot, "src", "data", "crypto-skills.json");

const accentByCategory = {
  Binance: "#f0b90b",
  OKX: "#ffffff",
  Bybit: "#f7a600",
  Coinbase: "#0052ff",
  Uniswap: "#ff4fb8",
  Polymarket: "#6b7cff",
  Solana: "#14f195",
  Jupiter: "#21c7a8",
  Bankr: "#8b5cf6",
  GMGN: "#f97316",
  "Crypto.com": "#1d4ed8",
  "BNB Chain": "#f0b90b",
  Byreal: "#ef4444",
  CoinAnk: "#22c55e",
  PANews: "#38bdf8",
  SlowMist: "#64748b",
  Surf: "#06b6d4",
  "6551 Daily News": "#eab308",
};

const categoryRank = [
  "Binance",
  "OKX",
  "Bybit",
  "Coinbase",
  "Crypto.com",
  "Uniswap",
  "Polymarket",
  "Solana",
  "Jupiter",
  "BNB Chain",
  "GMGN",
  "Bankr",
  "Byreal",
  "CoinAnk",
  "PANews",
  "SlowMist",
  "Surf",
  "6551 Daily News",
];

const categoryRankIndex = new Map(
  categoryRank.map((categoryTitle, index) => [categoryTitle, index]),
);

function compareCategoryTitle(a, b) {
  const aRank = categoryRankIndex.get(a) ?? Number.MAX_SAFE_INTEGER;
  const bRank = categoryRankIndex.get(b) ?? Number.MAX_SAFE_INTEGER;

  return aRank - bRank || a.localeCompare(b);
}

function firstSentence(text) {
  return String(text || "")
    .replace(/\s+/g, " ")
    .trim()
    .split(/(?<=\.)\s+/)[0];
}

function normalizeSkill(skill, sourceFile) {
  const categoryTitle = skill.category_title || skill.category || "Other";
  const repository = skill.source?.repository || "";
  const install = skill.source?.install || "";

  return {
    id: skill.id,
    title: skill.title,
    summary: String(skill.summary || "").trim(),
    summary_short: firstSentence(skill.summary),
    usage: String(skill.usage || "").trim(),
    category: skill.category || categoryTitle.toLowerCase(),
    category_title: categoryTitle,
    accent: accentByCategory[categoryTitle] || "#94a3b8",
    source: {
      name: skill.source?.name || path.basename(path.dirname(sourceFile)),
      repository,
      install,
    },
    skill_path: skill.skill_path,
    data_file: path.relative(skillsRoot, sourceFile),
  };
}

const dataFiles = fs
  .readdirSync(skillsRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => path.join(skillsRoot, entry.name, "data.json"))
  .filter((filePath) => fs.existsSync(filePath))
  .sort();

const skills = dataFiles.flatMap((filePath) => {
  const raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  return raw.map((skill) => normalizeSkill(skill, filePath));
});

const categories = Object.values(
  skills.reduce((acc, skill) => {
    const key = skill.category_title;
    acc[key] ||= {
      title: key,
      count: 0,
      accent: skill.accent,
      sources: new Set(),
    };
    acc[key].count += 1;
    acc[key].sources.add(skill.source.name);
    return acc;
  }, {}),
)
  .map((category) => ({
    ...category,
    sources: Array.from(category.sources).sort(),
  }))
  .sort((a, b) => compareCategoryTitle(a.title, b.title) || b.count - a.count);

const payload = {
  stats: {
    files: dataFiles.length,
    skills: skills.length,
    categories: categories.length,
  },
  categories,
  skills: skills.sort(
    (a, b) =>
      compareCategoryTitle(a.category_title, b.category_title) ||
      a.title.localeCompare(b.title),
  ),
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${JSON.stringify(payload, null, 2)}\n`);

console.log(
  `Built ${payload.stats.skills} skills from ${payload.stats.files} data files into ${path.relative(appRoot, outputPath)}`,
);
