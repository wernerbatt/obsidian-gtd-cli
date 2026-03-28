# Obsidian GTD CLI

AI-assisted [Getting Things Done](https://gettingthingsdone.com/) workflows for [Obsidian](https://obsidian.md), powered by the Obsidian CLI and agent skills.

This is my personal GTD system. It uses the Obsidian CLI (1.12+) as the backbone and a set of skill files that teach AI agents (Claude, Codex, Gemini, etc.) how to run GTD workflows against my vault. No plugins beyond [Obsidian Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) and [Dataview](https://github.com/blacksmithgu/obsidian-dataview) are required.

Feel free to fork and adapt to your own system.

## How it works

```
You ↔ AI agent ↔ Skills (.claude/skills/) ↔ Obsidian CLI ↔ Your vault
```

1. **You** talk to an AI agent (Claude Code, Codex CLI, etc.)
2. **Skills** teach the agent the GTD workflow — what to ask, how to process, when to confirm
3. **The Obsidian CLI** does all the vault reads and writes — the agent calls it directly
4. **Your vault** stays in sync because everything goes through Obsidian's own APIs

There are no custom plugins, no server, no database. Just markdown files, the Obsidian CLI, and skill documents that any agent can follow.

## Skills

Skills live in `.claude/skills/` and can be mirrored to other agent skill directories (`.codex/skills/`, etc.).

| Skill | What it does |
|-------|-------------|
| **[obsidian](/.claude/skills/obsidian/SKILL.md)** | Base layer — all vault operations (query, edit, create, move, delete) via the Obsidian CLI |
| **[clarify](/.claude/skills/clarify/SKILL.md)** | Process inbox items using the GTD clarify workflow |
| **[organize](/.claude/skills/organize/SKILL.md)** | Batch-tag tasks by context, create projects, move tasks between files |
| **[project](/.claude/skills/project/SKILL.md)** | Full project lifecycle — promote, scaffold, maintain, close |
| **[review](/.claude/skills/review/SKILL.md)** | Weekly review — metrics, overdue tasks, stale projects, calendar check |
| **[purge](/.claude/skills/purge/SKILL.md)** | Reduce list bloat — drop, demote, merge, or rewrite tasks |
| **[stuck](/.claude/skills/stuck/SKILL.md)** | Break through procrastination — diagnose friction, generate micro-actions |
| **[systems-review](/.claude/skills/systems-review/SKILL.md)** | Weekly review of all active personal systems |

### The `/obsidian` skill

This is the foundation. All other skills reference it for vault operations. It documents:

- **Native CLI commands** — `tasks todo`, `task done`, `read`, `append`, `create`, `search`
- **Dataview eval queries** — inbox, by-context, overdue, stale projects, completed tasks, context distribution
- **File mutations via `eval`** — edit by line/match, delete, insert under heading, move between files
- **Task metadata format** — emoji dates, priorities, context tags, dependency chains

The key insight: the Obsidian CLI's `eval` command gives you direct access to the Dataview plugin API and `app.vault.process()` for atomic file edits. This eliminates the need for any external tooling — no Python scripts, no direct file I/O, no sync issues.

## Prerequisites

- [Obsidian](https://obsidian.md) 1.12+ (includes the CLI)
- [Obsidian Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) plugin
- [Dataview](https://github.com/blacksmithgu/obsidian-dataview) plugin
- An AI agent that reads `AGENTS.md` / `SKILL.md` files (Claude Code, Codex CLI, Gemini CLI, etc.)

## Setup

1. Fork or clone this repo
2. Copy `config.yaml.example` to `config.yaml` and fill in your paths:
   ```bash
   cp config.yaml.example config.yaml
   ```
3. Point your agent's skill directory at `.claude/skills/` (or symlink/mirror as needed)

The `config.yaml` holds your personal settings — Obsidian binary path, vault name, vault path, calendar accounts. It's gitignored so your config stays local.

## GTD structure

The system expects this folder structure in your Obsidian vault (customizable in `config.yaml`):

```
Vault/
├── Daily/              # Daily notes (capture happens here)
├── GTD/
│   ├── Dashboard.md    # Main view with Dataview/Tasks queries
│   ├── Projects/       # One note per project
│   ├── Projects List.md
│   ├── Checklists/     # Reference checklists
│   └── Recurring.md    # Recurring task definitions
└── Templates/          # Note templates
```

### Task format

Tasks use [Obsidian Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) emoji notation:

```markdown
- [ ] Call dentist for appointment @quick ⏳ 2026-03-25 📅 2026-03-30 🔼
```

- **Context tags:** `@deep`, `@quick`, `@batch`, `@read`, `@out`, `@partner`, `@ai`, `@ponderables`, `@stuck`, `@waiting`
- **Dates:** `⏳` scheduled, `📅` due, `🛫` start, `✅` done
- **Priority:** `⏫` highest → `🔼` high → (normal) → `🔽` low → `⏬` lowest (someday/maybe)
- **Dependencies:** `🆔 abc` defines an ID, `⛔ abc` blocks on it

## Example session

```
You: clarify my inbox

Agent: [loads /clarify skill, runs /obsidian inbox query]

Found 8 inbox items. First batch:

1.  "rubber bands XL" (Daily/2026-03-18.md:14)
    → suggest: @out, schedule Saturday
2.  "https://example.com/interesting-article"
    → suggest: rewrite "Read: Interesting Article" @read
3.  "kitchen renovation quotes"
    → suggest: promote to project, seed 3 next actions

Accept all? Or override by number:

You: accept, but 3: just @quick for now

Agent: [executes via Obsidian CLI eval patterns]
✓ 1: Tagged @out ⏳ 2026-03-22
✓ 2: Rewritten + tagged @read
✓ 3: Tagged @quick
```

## Architecture

```
.claude/skills/
├── obsidian/SKILL.md      # Base layer: CLI patterns, eval templates
├── clarify/SKILL.md       # GTD clarify workflow
├── organize/SKILL.md      # Context tagging, project creation
├── project/SKILL.md       # Project lifecycle
├── review/SKILL.md        # Weekly review
├── purge/SKILL.md         # List reduction
├── stuck/SKILL.md         # Procrastination coaching
└── systems-review/SKILL.md

AGENTS.md                  # Entry point for agents — skill discovery
config.yaml.example        # Template for personal config
tools/obsidian_cli.py       # Thin Python wrapper around the CLI (optional)
```

### Why skills instead of code?

Skills are plain markdown files that teach an agent a workflow. Compared to traditional CLI tools:

- **No runtime dependencies** — no Python, no npm, no virtual environments
- **Model-agnostic** — works with any agent that reads markdown instructions
- **Self-documenting** — the skill file IS the documentation
- **Easy to fork and customize** — edit a markdown file, not code
- **Composable** — skills reference each other (`/clarify` uses `/obsidian`)

The Obsidian CLI's `eval` command is the key enabler — it gives agents direct access to vault APIs, Dataview queries, and atomic file edits through a single binary.

## License

[MIT](LICENSE)
