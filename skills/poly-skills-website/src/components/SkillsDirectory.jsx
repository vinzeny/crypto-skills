import React, { useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  Check,
  Copy,
  Cpu,
  Database,
  ExternalLink,
  Layers3,
  Search,
  Sparkles,
  X,
} from "lucide-react";
import { marked } from "marked";
import catalog from "../data/crypto-skills.json";
import { localizeSkill, translateTextAsync } from "../lib/translate";

const copy = {
  zh: {
    all: "全部",
    eyebrow: "AI Crypto Skills Navigator",
    title: "按交易所和协议浏览 AI Crypto Skills",
    subtitle:
      "聚合仓库里的 data.json，快速筛选交易所、协议和工具型 Skill，查看摘要、使用方法、安装来源和本地路径。",
    searchPlaceholder: "搜索 skill、交易所、命令或路径",
    skills: "Skills",
    groups: "分组",
    files: "data.json",
    installMethods: "安装方法",
    resultSuffix: "个技能",
    summary: "摘要",
    usage: "使用方法",
    expand: "展开",
    install: "安装",
    skillPath: "Skill 路径",
    repository: "Repository",
    noResults: "没有匹配的技能",
    backToDirectory: "Back to directory",
    language: "EN",
    close: "关闭",
    copyPath: "复制路径",
    copied: "已复制",
  },
  en: {
    all: "All",
    eyebrow: "AI Crypto Skills Navigator",
    title: "Browse AI Crypto Skills by exchange and protocol",
    subtitle:
      "A generated catalog from every data.json in the repo, built for filtering skills, reading usage notes, and jumping to install sources fast.",
    searchPlaceholder: "Search skill, exchange, command, or path",
    skills: "Skills",
    groups: "Groups",
    files: "data.json",
    installMethods: "Install",
    resultSuffix: "skills",
    summary: "Summary",
    usage: "Usage",
    expand: "Open",
    install: "Install",
    skillPath: "Skill path",
    repository: "Repository",
    noResults: "No matching skills",
    backToDirectory: "Back to directory",
    language: "中文",
    close: "Close",
    copyPath: "Copy path",
    copied: "Copied",
  },
};

function normalize(text) {
  return String(text || "").toLowerCase();
}

function MarkdownBlock({ className = "", markdown }) {
  const html = useMemo(
    () =>
      marked.parse(String(markdown || ""), {
        breaks: true,
        gfm: true,
      }),
    [markdown],
  );

  return <div className={`markdown-content ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}

function compactMarkdown(text, maxLength = 780) {
  const value = String(text || "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  if (value.length <= maxLength) {
    return value;
  }

  return `${value.slice(0, maxLength).trim()}...`;
}

function getInstallMethods(skills) {
  return Array.from(
    new Set(
      skills
        .map((skill) => skill.source?.install)
        .filter(Boolean),
    ),
  );
}

function InstallCommand({ command, labels }) {
  const [copied, setCopied] = useState(false);

  const copyCommand = async () => {
    await navigator.clipboard?.writeText(command);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div className="install-command">
      <code>{command}</code>
      <button type="button" className="icon-button install-copy-button" onClick={copyCommand} aria-label={labels.copyPath}>
        {copied ? <Check size={17} /> : <Copy size={17} />}
      </button>
    </div>
  );
}

function useDisplaySkill(skill, language, options = {}) {
  const fallbackSkill = useMemo(() => {
    if (!skill) {
      return null;
    }

    const displaySkill = localizeSkill(skill, language);

    if (options.compactUsage) {
      return {
        ...displaySkill,
        usage: compactMarkdown(displaySkill.usage),
      };
    }

    return displaySkill;
  }, [language, options.compactUsage, skill]);

  const [displaySkill, setDisplaySkill] = useState(fallbackSkill);

  useEffect(() => {
    let cancelled = false;

    setDisplaySkill(fallbackSkill);

    if (!skill || language !== "zh") {
      return () => {
        cancelled = true;
      };
    }

    translateTextAsync(skill.summary, language)
      .then((summary) => {
        if (!cancelled) {
          setDisplaySkill({
            ...skill,
            summary,
            summary_short: summary,
            usage: options.compactUsage ? compactMarkdown(skill.usage) : skill.usage,
          });
        }
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [fallbackSkill, language, options.compactUsage, skill]);

  return displaySkill;
}

function CategoryRail({ selectedCategory, setSelectedCategory, labels }) {
  const allCategory = {
    title: labels.all,
    key: "__all__",
    count: catalog.stats.skills,
    accent: "#2563eb",
  };

  const categories = [allCategory, ...catalog.categories];

  return (
    <div className="category-rail" aria-label="Skill categories">
      {categories.map((category) => {
        const categoryKey = category.key || category.title;
        const active = selectedCategory === categoryKey;

        return (
          <button
            key={categoryKey}
            className={`category-tab ${active ? "is-active" : ""}`}
            type="button"
            aria-pressed={active}
            onClick={() => {
              setSelectedCategory(categoryKey);
              document.getElementById("skills")?.scrollIntoView({ block: "start", behavior: "smooth" });
            }}
            style={{ "--accent": category.accent }}
          >
            <span className="category-dot" />
            <span className="category-name">{category.title}</span>
            <span className="category-count">{category.count}</span>
          </button>
        );
      })}
    </div>
  );
}

function SkillCard({ skill, onOpen, labels, language }) {
  const displaySkill = useDisplaySkill(skill, language, {
    compactUsage: true,
  });

  if (!displaySkill) {
    return null;
  }

  return (
    <article className="skill-card" style={{ "--accent": displaySkill.accent }}>
      <div className="skill-card-topline" />
      <div className="skill-card-header">
        <div className="skill-badge" aria-hidden="true">
          {displaySkill.category_title.slice(0, 2).toUpperCase()}
        </div>
        <div className="skill-meta">
          <span>{displaySkill.category_title}</span>
          <span>{displaySkill.source.name}</span>
        </div>
      </div>

      <h3>{displaySkill.title}</h3>

      <div className="card-section">
        <div className="section-label">{labels.summary}</div>
        <p className="summary-text">{displaySkill.summary}</p>
      </div>

      <div className="card-section usage-section">
        <div className="section-label">{labels.usage}</div>
        <MarkdownBlock className="skill-usage" markdown={displaySkill.usage} />
      </div>

      <div className="skill-footer">
        <button type="button" className="open-button" onClick={() => onOpen(skill)}>
          <span>{labels.expand}</span>
          <ArrowUpRight size={15} />
        </button>
      </div>
    </article>
  );
}

function SkillDetail({ skill, onClose, labels, language }) {
  const [copied, setCopied] = useState(false);
  const displaySkill = useDisplaySkill(skill, language);

  if (!skill || !displaySkill) {
    return null;
  }

  const copyPath = async () => {
    await navigator.clipboard?.writeText(displaySkill.skill_path);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div className="detail-backdrop" role="dialog" aria-modal="true">
      <div className="detail-panel" style={{ "--accent": displaySkill.accent }}>
        <div className="detail-topline" />
        <header className="detail-header">
          <div>
            <div className="detail-kicker">
              <span className="category-dot" />
              {displaySkill.category_title}
            </div>
            <h2>{displaySkill.title}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label={labels.close}>
            <X size={18} />
          </button>
        </header>

        <section className="detail-section">
          <h3>{labels.summary}</h3>
          <p>{displaySkill.summary}</p>
        </section>

        <section className="detail-section">
          <h3>{labels.usage}</h3>
          <MarkdownBlock className="detail-usage" markdown={displaySkill.usage} />
        </section>

        <section className="detail-section detail-grid">
          <div>
            <h3>{labels.install}</h3>
            <code>{displaySkill.source.install || "See repository"}</code>
          </div>
          <div>
            <h3>{labels.skillPath}</h3>
            <div className="path-row">
              <code>{displaySkill.skill_path}</code>
              <button type="button" className="icon-button" onClick={copyPath} aria-label={labels.copyPath}>
                {copied ? <Check size={17} /> : <Copy size={17} />}
              </button>
            </div>
          </div>
        </section>

        {displaySkill.source.repository ? (
          <a className="repo-link" href={displaySkill.source.repository} target="_blank" rel="noreferrer">
            <ExternalLink size={16} />
            <span>{labels.repository}</span>
            <small>{displaySkill.source.repository}</small>
          </a>
        ) : null}
      </div>
    </div>
  );
}

export default function SkillsDirectory() {
  const [language] = useState(() => {
    if (typeof window === "undefined") {
      return "en";
    }

    return new URLSearchParams(window.location.search).get("lang") === "zh" ? "zh" : "en";
  });
  const labels = copy[language];
  const [selectedCategory, setSelectedCategory] = useState("__all__");
  const [selectedSkill, setSelectedSkill] = useState(null);

  useEffect(() => {
    const label = document.getElementById("language-toggle-label");
    const link = document.getElementById("language-toggle");

    if (label) {
      label.textContent = labels.language;
    }

    if (link) {
      const params = new URLSearchParams(window.location.search);
      params.set("lang", language === "en" ? "zh" : "en");
      link.href = `${window.location.pathname}?${params.toString()}${window.location.hash}`;
    }
  }, [labels.language, language]);

  const filteredSkills = useMemo(() => {
    return catalog.skills.filter((skill) => {
      return selectedCategory === "__all__" || skill.category_title === selectedCategory;
    });
  }, [selectedCategory]);

  const selectedCategoryData =
    selectedCategory === "__all__"
      ? { title: labels.all, count: catalog.stats.skills, accent: "#2563eb" }
      : catalog.categories.find((category) => category.title === selectedCategory) || {
          title: labels.all,
          count: catalog.stats.skills,
          accent: "#2563eb",
        };
  const installMethods = selectedCategory === "__all__" ? [] : getInstallMethods(filteredSkills);

  return (
    <div className="directory-shell">
      <section className="hero-band">
        <div className="hero-grid">
          <div className="hero-copy">
            <div className="eyebrow">
              <Sparkles size={15} />
              {labels.eyebrow}
            </div>
            <h1>{labels.title}</h1>
            <p>{labels.subtitle}</p>
            <div className="ai-signal-row" aria-hidden="true">
              <span><Cpu size={15} /> Agent-ready</span>
              <span><Layers3 size={15} /> Exchange groups</span>
              <span><Database size={15} /> Local JSON</span>
            </div>
          </div>
        </div>
      </section>

      <section className="directory-band" id="skills">
        <CategoryRail
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          labels={labels}
        />

        <div className="results-header" style={{ "--accent": selectedCategoryData.accent }}>
          <div>
            <span className="results-kicker">
              <span className="category-dot" />
              {selectedCategory === "__all__" ? labels.all : selectedCategory}
            </span>
            <h2>{`${filteredSkills.length} ${labels.resultSuffix}`}</h2>
          </div>
          {installMethods.length ? (
            <div className="source-note install-note">
              <span>{labels.installMethods}</span>
              {installMethods.map((installMethod) => (
                <InstallCommand key={installMethod} command={installMethod} labels={labels} />
              ))}
            </div>
          ) : null}
        </div>

        {filteredSkills.length ? (
          <div className="skills-grid">
            {filteredSkills.map((skill) => (
              <SkillCard key={skill.id} skill={skill} onOpen={setSelectedSkill} labels={labels} language={language} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <Search size={24} />
            <p>{labels.noResults}</p>
          </div>
        )}
      </section>

      <SkillDetail skill={selectedSkill} onClose={() => setSelectedSkill(null)} labels={labels} language={language} />
    </div>
  );
}
