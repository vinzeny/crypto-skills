#!/usr/bin/env bun

import { readFileSync, writeFileSync } from 'fs';

const GITHUB_API = 'https://api.github.com';
const REPOS = [
  { owner: 'DevAgarwal2', repo: 'poly-gamma-skills' },
  { owner: 'DevAgarwal2', repo: 'poly-user-skills' },
];

async function fetchRepoContent(owner, repo, path = '') {
  const response = await fetch(`${GITHUB_API}/repos/${owner}/${repo}/contents/${path}`);
  if (!response.ok) return [];
  return response.json();
}

async function fetchFileContent(owner, repo, path) {
  const response = await fetch(`${GITHUB_API}/repos/${owner}/${repo}/contents/${path}`);
  if (!response.ok) return null;
  const data = await response.json();
  if (data.type === 'file' && data.content) {
    return Buffer.from(data.content, 'base64').toString('utf-8');
  }
  return null;
}

async function buildFileTree(owner, repo, path = '') {
  const contents = await fetchRepoContent(owner, repo, path);
  
  const tree = [];
  
  for (const item of contents) {
    if (item.name.startsWith('.') || item.name === 'node_modules') continue;
    
    if (item.type === 'dir') {
      const children = await buildFileTree(owner, repo, item.path);
      if (children.length > 0) {
        tree.push({
          name: item.name,
          type: 'folder',
          children
        });
      }
    } else if (item.type === 'file' && (item.name.endsWith('.md') || item.name.endsWith('.py') || item.name.endsWith('.json') || item.name.endsWith('.sh'))) {
      tree.push({
        name: item.name,
        type: 'file',
        path: item.path
      });
    }
  }
  
  return tree;
}

async function fetchAllFiles(owner, repo, tree, files = {}) {
  for (const node of tree) {
    if (node.type === 'file') {
      const content = await fetchFileContent(owner, repo, node.path);
      if (content) {
        files[node.path] = { content, path: node.path };
      }
    } else if (node.type === 'folder' && node.children) {
      await fetchAllFiles(owner, repo, node.children, files);
    }
  }
  return files;
}

function getIconForRepo(repo) {
  const icons = {
    'poly-gamma-skills': 'BarChart3',
    'poly-user-skills': 'Users',
  };
  return icons[repo] || 'Box';
}

async function fetchRepoDetails(owner, repo) {
  console.log(`Fetching ${owner}/${repo}...`);
  
  const repoRes = await fetch(`${GITHUB_API}/repos/${owner}/${repo}`);
  const repoData = await repoRes.json();
  
  const fileTree = await buildFileTree(owner, repo);
  
  console.log(`  Found ${fileTree.length} top-level items`);
  console.log(`  Fetching file contents...`);
  
  const files = await fetchAllFiles(owner, repo, fileTree);
  
  console.log(`  Fetched ${Object.keys(files).length} files`);

  return {
    id: repo,
    name: repo === 'poly-gamma-skills' ? 'Market Data API' : 'User Data API',
    owner: repoData.owner.login,
    repo: repoData.full_name,
    description: repoData.description || (repo === 'poly-gamma-skills' ? 'Discover and analyze Polymarket prediction markets. Real-time odds, volume, trending markets, and breaking news.' : 'Access user trading history, portfolio analytics, P&L analysis, and leaderboard rankings.'),
    tags: repo === 'poly-gamma-skills' ? ["Markets", "Odds", "News", "Discovery"] : ["Analytics", "Portfolio", "History", "Leaderboard"],
    icon: getIconForRepo(repo),
    repository: repoData.html_url,
    author: "Polymarket",
    stats: {
      views: 1240,
      downloads: 85
    },
    files,
    fileTree
  };
}

async function main() {
  console.log('Fetching skills from GitHub...\n');
  
  const skills = await Promise.all(
    REPOS.map(({ owner, repo }) => fetchRepoDetails(owner, repo))
  );
  
  const outputPath = './src/data/skills.json';
  writeFileSync(outputPath, JSON.stringify(skills, null, 2));
  
  console.log(`\n✓ Updated ${outputPath}`);
  console.log('\nSkills fetched:');
  skills.forEach(skill => {
    const fileCount = Object.keys(skill.files).length;
    console.log(`  - ${skill.name}: ${fileCount} files embedded`);
  });
}

main().catch(console.error);
