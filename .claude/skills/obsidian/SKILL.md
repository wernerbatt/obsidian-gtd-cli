---
name: obsidian
description: Low-level Obsidian vault operations via the official CLI. All other skills should use these patterns instead of Python tools or direct file I/O.
---

# Obsidian Vault Operations

All vault reads and writes go through the Obsidian CLI binary so the app stays in sync. No direct file I/O, no Python wrappers.

## CLI Binary

Read `obsidian_bin` and `vault_name` from `config.yaml` at the repo root:

```bash
# Read config (do this once per session)
OBS=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['obsidian_bin'])")
VAULT=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_name'])")
```

Every command follows the pattern:

```bash
$OBS vault=$VAULT <command> [args...]
```

## Native Commands

### List tasks

```bash
# All incomplete tasks (JSON with file, line, text, status)
$OBS vault=$VAULT tasks todo verbose format=json

# All completed tasks
$OBS vault=$VAULT tasks done verbose format=json
```

### Mark task done

```bash
$OBS vault=$VAULT task path="Daily/2026-03-21.md" line=52 done
```

### Read a file

```bash
$OBS vault=$VAULT read path="GTD/Dashboard.md"
```

### Append to a file (EOF)

```bash
$OBS vault=$VAULT append path="GTD/Projects/My Project.md" content="- [ ] New task @quick"
```

### Append to today's daily note

```bash
# Get today's daily note path
$OBS vault=$VAULT daily:path

# Append to it
$OBS vault=$VAULT append path="$($OBS vault=$VAULT daily:path)" content="- [ ] New task @quick"
```

### Create a file

```bash
$OBS vault=$VAULT create path="GTD/Projects/New Project.md" content="# New Project"

# With overwrite
$OBS vault=$VAULT create path="GTD/Projects/New Project.md" content="..." overwrite
```

### Search

```bash
# Full-text search
$OBS vault=$VAULT search query="kitchen renovation"

# With line-level context
$OBS vault=$VAULT search:context query="@waiting"

# Scoped to folder
$OBS vault=$VAULT search query="next action" path="GTD/Projects"
```

### List files

```bash
$OBS vault=$VAULT files folder="GTD/Projects"
```

## Eval Patterns — Dataview Queries

Use `eval` to access the Dataview plugin API for structured queries. Wrap in an async IIFE and return JSON for parseable output.

### GTD Inbox (tasks needing processing)

Matches the Dashboard "To Process" query: no context tag, not blocked, not future-scheduled, not lowest priority.

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const dv = app.plugins.plugins["dataview"]?.api;
  const contextRe = /@(deep|quick|batch|read|partner|sharne|out|ai|ponderables|stuck|waiting|pc|work|home|garden|someday)/;
  const excludeFolders = ["Checklists", "Templates", "Recurring"];
  const today = new Date().toISOString().slice(0,10);
  const inbox = dv.pages().file.tasks
    .where(t => !t.completed)
    .where(t => !contextRe.test(t.text))
    .where(t => !t.text.includes("⏬"))
    .where(t => !t.text.includes("⛔"))
    .where(t => !excludeFolders.some(f => (t.path||"").includes(f)))
    .where(t => {
      const sm = t.text.match(/⏳\s*(\d{4}-\d{2}-\d{2})/);
      const dm = t.text.match(/📅\s*(\d{4}-\d{2}-\d{2})/);
      return (!sm || sm[1] < today) && (!dm || dm[1] < today);
    });
  return JSON.stringify({count: inbox.length, tasks: inbox.slice(0,20).array().map(t => ({
    path: t.path, line: t.line, text: t.text
  }))});
})()'
```

### Tasks by context tag

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const dv = app.plugins.plugins["dataview"]?.api;
  const tag = "@quick";
  const tasks = dv.pages().file.tasks
    .where(t => !t.completed && t.text.includes(tag) && !t.text.includes("⏬"));
  return JSON.stringify(tasks.array().map(t => ({
    path: t.path, line: t.line, text: t.text
  })));
})()'
```

### Overdue tasks

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const dv = app.plugins.plugins["dataview"]?.api;
  const today = new Date().toISOString().slice(0,10);
  const tasks = dv.pages().file.tasks
    .where(t => !t.completed && !t.text.includes("⏬"))
    .where(t => {
      const sm = t.text.match(/⏳\s*(\d{4}-\d{2}-\d{2})/);
      const dm = t.text.match(/📅\s*(\d{4}-\d{2}-\d{2})/);
      return (sm && sm[1] < today) || (dm && dm[1] < today);
    });
  return JSON.stringify(tasks.array().map(t => ({
    path: t.path, line: t.line, text: t.text
  })));
})()'
```

### Context distribution (counts)

Excludes Checklists, Templates, and Recurring to match Dashboard scope.

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const dv = app.plugins.plugins["dataview"]?.api;
  const exclude = ["Checklists", "Templates", "Recurring"];
  const tasks = dv.pages().file.tasks
    .where(t => !t.completed && !t.text.includes("⏬"))
    .where(t => !exclude.some(f => (t.path||"").includes(f)));
  const counts = {};
  let noContext = 0;
  const re = /@(\w+)/g;
  for (const t of tasks) {
    let m, found = false;
    while ((m = re.exec(t.text)) !== null) {
      counts["@"+m[1]] = (counts["@"+m[1]]||0) + 1;
      found = true;
    }
    re.lastIndex = 0;
    if (!found) noContext++;
  }
  return JSON.stringify({total: tasks.length, contexts: counts, noContext});
})()'
```

### Completed tasks (last N days)

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const dv = app.plugins.plugins["dataview"]?.api;
  const since = new Date(Date.now() - 7*86400000).toISOString().slice(0,10);
  const tasks = dv.pages().file.tasks
    .where(t => t.completed)
    .where(t => {
      const m = t.text.match(/✅\s*(\d{4}-\d{2}-\d{2})/);
      return m && m[1] >= since;
    });
  return JSON.stringify({count: tasks.length, tasks: tasks.slice(0,20).array().map(t => ({
    path: t.path, line: t.line, text: t.text
  }))});
})()'
```

### Stale projects (no next action)

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const dv = app.plugins.plugins["dataview"]?.api;
  const projects = dv.pages("\"GTD/Projects\"").where(p => {
    const status = String(p.status || "active").toLowerCase();
    if (status !== "active") return false;
    const tasks = p.file.tasks.where(t => !t.completed);
    return tasks.length === 0;
  });
  return JSON.stringify(projects.map(p => p.file.path).array());
})()'
```

### Someday/maybe (lowest priority)

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const dv = app.plugins.plugins["dataview"]?.api;
  const tasks = dv.pages().file.tasks
    .where(t => !t.completed && (t.text.includes("⏬") || t.text.includes("@someday")));
  return JSON.stringify(tasks.slice(0,20).array().map(t => ({
    path: t.path, line: t.line, text: t.text
  })));
})()'
```

## Eval Patterns — File Mutations

For line-level edits the CLI has no native command. Use `eval` with `app.vault.process()` which atomically reads, transforms, and writes the file.

### Edit a task line

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const path = "Daily/2026-03-21.md";
  const lineNum = 52;
  const newText = "- [ ] Updated task description @deep ⏳ 2026-03-25";
  const f = app.vault.getAbstractFileByPath(path);
  await app.vault.process(f, (content) => {
    const lines = content.split("\n");
    lines[lineNum - 1] = newText;
    return lines.join("\n");
  });
  return "edited line " + lineNum;
})()'
```

### Edit a task by match

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const path = "Daily/2026-03-21.md";
  const match = "Buy groceries";
  const newText = "- [ ] Buy groceries @out ⏳ 2026-03-22";
  const f = app.vault.getAbstractFileByPath(path);
  let found = -1;
  await app.vault.process(f, (content) => {
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(match) && lines[i].match(/^\s*- \[.\]/)) {
        lines[i] = newText;
        found = i + 1;
        break;
      }
    }
    return lines.join("\n");
  });
  return found > 0 ? "edited line " + found : "no match found";
})()'
```

### Delete a task line

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const path = "Daily/2026-03-21.md";
  const lineNum = 52;
  const f = app.vault.getAbstractFileByPath(path);
  await app.vault.process(f, (content) => {
    const lines = content.split("\n");
    lines.splice(lineNum - 1, 1);
    return lines.join("\n");
  });
  return "deleted line " + lineNum;
})()'
```

### Delete a task (with subtasks)

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const path = "GTD/Projects/My Project.md";
  const lineNum = 10;
  const f = app.vault.getAbstractFileByPath(path);
  await app.vault.process(f, (content) => {
    const lines = content.split("\n");
    const baseIndent = (lines[lineNum-1].match(/^(\s*)/)||["",""])[1].length;
    let end = lineNum;
    while (end < lines.length) {
      const indent = (lines[end].match(/^(\s*)/)||["",""])[1].length;
      if (indent <= baseIndent && lines[end].trim()) break;
      end++;
    }
    lines.splice(lineNum - 1, end - lineNum + 1);
    return lines.join("\n");
  });
  return "deleted task + subtasks";
})()'
```

### Insert task under a heading

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const path = "Daily/2026-03-21.md";
  const heading = "Day planner";
  const task = "- [ ] New task @quick";
  const f = app.vault.getAbstractFileByPath(path);
  await app.vault.process(f, (content) => {
    const lines = content.split("\n");
    let headingIdx = -1;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].match(new RegExp("^#+\\\\s+" + heading))) {
        headingIdx = i;
        break;
      }
    }
    if (headingIdx === -1) return content;
    // Find last content line before next heading
    let insertIdx = headingIdx + 1;
    for (let i = headingIdx + 1; i < lines.length; i++) {
      if (lines[i].match(/^#+\s/)) break;
      insertIdx = i + 1;
    }
    lines.splice(insertIdx, 0, task);
    return lines.join("\n");
  });
  return "inserted under " + heading;
})()'
```

### Move a task between files

Combine delete from source + append to destination:

```bash
# 1. Read the task line from source
TASK=$($OBS vault=$VAULT eval 'code=
(async () => {
  const f = app.vault.getAbstractFileByPath("Daily/2026-03-21.md");
  const content = await app.vault.read(f);
  return content.split("\n")[51]; // line 52, 0-indexed
})()')

# 2. Delete from source
$OBS vault=$VAULT eval 'code=
(async () => {
  const f = app.vault.getAbstractFileByPath("Daily/2026-03-21.md");
  await app.vault.process(f, (content) => {
    const lines = content.split("\n");
    lines.splice(51, 1);
    return lines.join("\n");
  });
  return "deleted";
})()'

# 3. Append to destination
$OBS vault=$VAULT append path="GTD/Projects/My Project.md" content="$TASK"
```

Or as a single eval (atomic read-from-source, but two file writes):

```bash
$OBS vault=$VAULT eval 'code=
(async () => {
  const srcPath = "Daily/2026-03-21.md";
  const dstPath = "GTD/Projects/My Project.md";
  const lineNum = 52;
  const src = app.vault.getAbstractFileByPath(srcPath);
  const dst = app.vault.getAbstractFileByPath(dstPath);
  let taskLine = "";
  await app.vault.process(src, (content) => {
    const lines = content.split("\n");
    taskLine = lines[lineNum - 1];
    lines.splice(lineNum - 1, 1);
    return lines.join("\n");
  });
  await app.vault.process(dst, (content) => {
    return content.trimEnd() + "\n" + taskLine + "\n";
  });
  return "moved: " + taskLine.trim();
})()'
```

## Task Metadata Format

Tasks follow Obsidian Tasks plugin emoji format:

```
- [ ] Description @context ⏳ 2026-03-25 📅 2026-03-30 🔼
```

| Symbol | Meaning | Format |
|--------|---------|--------|
| `⏳` | Scheduled date | `⏳ YYYY-MM-DD` |
| `📅` | Due date | `📅 YYYY-MM-DD` |
| `🛫` | Start date | `🛫 YYYY-MM-DD` |
| `✅` | Done date | `✅ YYYY-MM-DD` |
| `⏫` | Highest priority | |
| `🔼` | High priority | |
| (none) | Normal priority | |
| `🔽` | Low priority | |
| `⏬` | Lowest / someday | |
| `🆔 abc` | Task ID | |
| `⛔ abc` | Depends on ID | |

## Context Tags

| Tag | Meaning |
|-----|---------|
| `@deep` | Deep focus, 2+ hours |
| `@quick` | Quick win, <15 min |
| `@batch` | Group similar tasks |
| `@read` | Reading tasks |
| `@partner` | Requires partner/collaborator |
| `@out` | Errands / outside |
| `@ai` | AI-related |
| `@ponderables` | Think about |
| `@stuck` | Blocked |
| `@waiting` | Delegated / waiting |

Deprecated: `@pc`, `@work`, `@home`, `@garden`, `@someday`

## Vault Structure

| Path | Purpose |
|------|---------|
| `GTD/Dashboard.md` | Main dashboard with queries |
| `GTD/Projects/` | Project notes |
| `GTD/Projects List.md` | Project index |
| `GTD/Checklists/` | Checklists (excluded from inbox) |
| `GTD/Recurring.md` | Recurring tasks (excluded from inbox) |
| `Daily/` | Daily notes |
| `Templates/` | Templates (excluded from inbox) |

## Safety Rules

- **Never run parallel writes to the same file.** `app.vault.process()` is atomic per call, but two concurrent evals on the same file will race. Sequence writes to the same file; different files can be parallel.
- **Always confirm before destructive ops** (delete, move, bulk edit) unless the user has explicitly selected the action.
- **Use match-based targeting** over line numbers when possible — line numbers shift after edits.

## Troubleshooting

- **Empty output from eval:** The query may have timed out (default 30s) or returned too much data. Add `.slice(0, N)` to limit results.
- **Exit code 255:** Usually a JS error. Check quoting — single quotes around the whole `code=...`, escape internal single quotes.
- **"Loading updated app package" noise:** Ignore these lines; they're Electron startup messages.
