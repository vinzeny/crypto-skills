# Installing Polymarket Skills

Installation instructions for the Polymarket Skills knowledge base for Claude Code.

## For Personal Use

Copy the polymarket folder to your Claude skills directory:

```bash
# Clone the repository
git clone https://github.com/KJHelgason/Polymarket_Agent_skills.git

# Copy to Claude skills
mkdir -p ~/.claude/skills
cp -r Polymarket_Agent_skills ~/.claude/skills/polymarket
```

Skills in `~/.claude/skills/` are available across all projects.

**Directory structure after installation:**

```
~/.claude/
  skills/
    polymarket/
      SKILL.md          # Skill entry point
      INSTALL.md        # This file
      VERSION.md        # Version history
      auth/             # Authentication module
      trading/          # Trading operations
      market-discovery/ # Market lookup
      real-time/        # WebSocket streaming
      data-analytics/   # Portfolio tracking
      edge-cases/       # Troubleshooting
      library/          # py-clob-client patterns
```

## For Project Use

Copy to your project's .claude directory:

```bash
# Copy skill to project
mkdir -p .claude/skills
cp -r Polymarket_Agent_skills .claude/skills/polymarket
```

Project-level skills are available when working in that project.

**Directory structure after installation:**

```
your-project/
  .claude/
    skills/
      polymarket/
        SKILL.md
        ...
  src/
  package.json
  ...
```

## Verification

After installation, verify the skill loads:

1. Start a new Claude Code session
2. Type `/polymarket` to invoke the skill directly
3. Or ask "How do I authenticate with Polymarket?" to test auto-triggering

**Expected:** Claude loads the skill and provides Polymarket-specific guidance.

### Quick verification commands

```bash
# Check skill directory exists
ls ~/.claude/skills/polymarket/SKILL.md

# Check all modules present
ls ~/.claude/skills/polymarket/
```

Expected output should show:
- SKILL.md
- auth/
- trading/
- market-discovery/
- real-time/
- data-analytics/
- edge-cases/
- library/

## Updating

To update to the latest version:

```bash
cd Polymarket_Agent_skills
git pull

# For personal installation
cp -r . ~/.claude/skills/polymarket

# OR for project installation
cp -r . .claude/skills/polymarket
```

Check [VERSION.md](./VERSION.md) for changelog after updates.

## Troubleshooting

### Skill doesn't load

**Symptom:** Claude doesn't recognize Polymarket commands or provide specialized guidance.

**Solutions:**

1. Verify SKILL.md exists:
   ```bash
   cat ~/.claude/skills/polymarket/SKILL.md
   ```

2. Check file permissions:
   ```bash
   chmod -R 644 ~/.claude/skills/polymarket/
   ```

3. Restart Claude Code session

### Auto-trigger doesn't work

**Symptom:** Asking about Polymarket doesn't load the skill automatically.

**Solutions:**

1. Verify the `description` field in SKILL.md frontmatter contains relevant keywords
2. Try explicit invocation: `/polymarket`
3. Check SKILL.md frontmatter format is valid YAML

### Permission errors

**Symptom:** Cannot copy files to ~/.claude/skills/

**Solutions:**

1. Create the directory if it doesn't exist:
   ```bash
   mkdir -p ~/.claude/skills/
   ```

2. Check directory ownership:
   ```bash
   ls -la ~/.claude/
   ```

3. Fix permissions if needed:
   ```bash
   chmod 755 ~/.claude/skills/
   ```

## Requirements

- **Claude Code** (claude-code CLI or VS Code extension)
- **Git** (for cloning and updates)

No additional dependencies required - skills are documentation only.

## Related Documentation

- [SKILL.md](./SKILL.md) - Skill entry point and quick navigation
- [VERSION.md](./VERSION.md) - Version history and changelog
- [auth/README.md](./auth/README.md) - Start here for first-time setup
