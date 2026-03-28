---
name: clarify
description: Process inbox items using GTD workflow
---

# GTD Clarify Skill

Help process unprocessed items in the Obsidian vault using GTD (Getting Things Done) methodology.

## Vault Operations

**Use the `/obsidian` skill for all vault reads and writes.** Load it before running any commands:
→ `~/.claude/skills/obsidian/SKILL.md`

Quick reference (see `/obsidian` skill for full patterns):
- **Find inbox items:** Dataview eval inbox query
- **Add task to daily note:** `daily:path` + `append`
- **Add task under heading:** eval + `vault.process()` insert-under-heading
- **Edit task:** eval + `vault.process()` edit-by-match
- **Move task:** eval + `vault.process()` (delete from source + append to dest)
- **Mark done:** `task path=... line=N done`
- **Delete task:** eval + `vault.process()` splice

### Open Today's Daily Note in Obsidian

```bash
cmd.exe /c start "" "obsidian://daily"
```

### Stable Targeting (Avoid Line-Shift Errors)

When batch editing or moving tasks, prefer description matching over line numbers.

### Avoid Parallel Edits to the Same File

**CRITICAL:** Never run parallel writes to the same file. `app.vault.process()` is atomic per call, but two concurrent evals on the same file will race. Sequence writes to the same file; different files can be parallel.

## IMPORTANT: Confirmation & Execution

**CRITICAL (aligned with safety):**
- Default to batch suggestions: present numbered options/sub-options before edits.
- Treat explicit user selections as confirmation for those chosen actions.
- If an action is unclear, destructive (delete/move), or conflicts with stated preferences, pause and ask for explicit yes/no before running tools.
- Use `--dry-run` only when requested.

Agents should:
1. Find and display inbox items.
2. Present batch suggestions (numbered/sub-options) and capture the user's selections.
3. If any selection is ambiguous/destructive/conflicting, ask for explicit confirmation on those items; otherwise proceed.
4. Execute the selected actions with stable matching (description-based).
5. Summarize what changed.

### Batch Suggestion Mode (Default)

Present options as numbered items with sub-options (e.g., 1, 1.1, 1.2, 2, 2.1) for inbox processing by default. If an item clearly needs multiple steps, include a sub-option to promote it to a project (e.g., `1.3 Create project: "<Name>" and seed next actions`). When suggesting actions, always look for opportunities to complete the task using an LLM agent (e.g., Claude Code CLI, Codex CLI, Gemini CLI). When a task could be accelerated by an LLM agent (drafting, summarizing, research, email), include a sub-option to delegate to an agent (e.g., `1.4 Use LLM agent to draft/research/summarize`) and also suggest adding `@ai` context tag to those tasks. After selections, proceed unless a step is ambiguous, destructive, or conflicting-then ask to confirm those specific items.

## Workflow

### 1. Find Inbox Items

Use the `/obsidian` skill's **GTD Inbox** Dataview eval query. It finds tasks that need clarification:
- No context tags (@deep, @quick, @batch, @read, @partner, @out, etc.)
- Not scheduled or overdue
- Not in excluded folders (Checklists, Templates, Recurring)
- Not blocked or done
- Excludes `@someday` and lowest-priority (⏬) items

For someday/maybe items, use the `/obsidian` skill's **Someday/maybe** query.

### 1.0 Batch Size Guidance

If there are more than 10 inbox items, present only the first 10 and process them.
After those are handled, ask whether to show the next 10.
Repeat until the user stops or the inbox is cleared.

### 1.1 Link-Heavy Items

For raw URLs, default to actions like "Read/Watch [source]" with `@batch` unless the user prefers archiving or a different context.
Always preserve the original link in the rewritten task line.
Place links before context tags (e.g., `Task https://... @batch`).

If the task contains a TikTok or Instagram URL, auto-assign `@batch` in the background without presenting options, then continue with the rest.

#### TikTok Title Resolution

When a task contains a bare TikTok URL (e.g., `https://vm.tiktok.com/...`), resolve it to a descriptive markdown link using curl with the `facebookexternalhit` user-agent (TikTok serves OG metadata to social crawlers):

```bash
# 1. Resolve the short URL to get the canonical URL
resolved=$(curl -sL -o /dev/null -w "%{url_effective}" "https://vm.tiktok.com/ZNRfjoYEP/")

# 2. Fetch OG description from the resolved URL
desc=$(curl -sL -H "User-Agent: facebookexternalhit/1.1" "$resolved" \
  | grep -oP 'og:description.*?content="[^"]*"' \
  | sed 's/.*content="//;s/"//')
```

Then rewrite the task line from:
```
- [ ] https://vm.tiktok.com/ZNRfjoYEP/ @batch
```
to:
```
- [ ] [Short descriptive title](https://vm.tiktok.com/ZNRfjoYEP/) @batch
```

Guidelines for the title:
- Write a short, natural, lowercase title (sentence case) summarising the video content
- Derive it from the `og:description` content returned by curl
- Strip like/comment counts, hashtags, and disclaimers — just capture the gist
- Keep it concise (under ~80 chars)
- Batch multiple TikTok URLs in a single loop to save time

### 1.2 Scheduling Shorthand

If the user says a weekday (e.g., "Tuesday" or "Thursday"), schedule the task for the first upcoming occurrence of that day.

### 1.3 Reference Creation

If an item is clearly a book, game, product, or other reference, suggest creating a reference note (using the appropriate reference skill/tooling) and then mark the task done once the reference is created.

### 2. Process Items Interactively

The GTD clarify workflow asks these questions for each task:

1. **What is it?** (Clarify the item)
2. **Is it actionable?**
   - **NO**: Trash / Reference / Lowest Priority (⏬)
   - **YES**: Continue...
3. **What's the next action?** (Specific, concrete step)
4. **Can it be done in 2 minutes?**
   - **YES**: Do it now, mark as done
   - **NO**: Continue...
5. **Is it a project?** (Multiple steps required?)
6. **Defer, delegate, or do?**
   - **Defer**: Add context tag + scheduled date
   - **Delegate**: Add @waiting tag + person
   - **Do ASAP**: Add context tag

Use the `/obsidian` skill's edit-by-match, move, mark-done, and delete patterns to execute these actions.

## Context Tags

Tasks are organized by context (where/when/with whom/what focus can you do it):

**Computer Tasks (by focus level):**
- `@deep` - Deep focus work (2+ hours, requires concentration, no interruptions)
  - Examples: Programming, writing, complex analysis, learning new skills
- `@quick` - Quick wins (<15 minutes, low effort, can do anytime)
  - Examples: Reply to email, update task, quick search, file something
- `@batch` - Similar tasks to batch together (saves mental switching)
  - Examples: Process emails, update multiple spreadsheets, review documents
- `@pc` - Legacy context (being phased out - use specific contexts above)

**Other Contexts:**
- `@work` - Work context (retired — use @deep/@quick/@batch instead)
- `@partner` - Requires partner/collaborator
- `@out` - Errands/outside/garden
- `@ai` - AI-related tasks
- `@ponderables` - Things to think about
- `@stuck` - Blocked items

**Note:** `@someday` context is deprecated. For "someday/maybe" items, use lowest priority (⏬) instead.

### How to Choose PC Context:

Ask yourself:
1. **How long will this take?**
   - 2+ hours → `@deep`
   - <15 min → `@quick`

2. **What's my energy level right now?**
   - Fresh/morning → Check `@deep`
   - Tired/afternoon → Check `@quick`

3. **Can I batch this with similar tasks?**
   - Multiple emails/updates → `@batch`

4. **Does this require deep focus?**
   - Yes, no interruptions → `@deep`
   - No, can handle interruptions → `@quick`

## Priority Levels

Tasks use Obsidian Tasks plugin priority symbols:
- ⏫ Highest priority
- 🔼 High priority
- (no symbol) Normal priority
- 🔽 Low priority
- ⏬ Lowest priority (use for someday/maybe items)

## Date Formats

Tasks use Obsidian Tasks plugin emoji metadata:
- ⏳ YYYY-MM-DD - Scheduled date
- 📅 YYYY-MM-DD - Due date
- 🛫 YYYY-MM-DD - Start date
- ✅ YYYY-MM-DD - Done date

When scheduling, you can use:
- `today` - Today's date
- `tomorrow` - Tomorrow's date
- `+N` - N days from now (e.g., `+3` for 3 days)
- `YYYY-MM-DD` - Specific date

## Best Practices

1. **Process inbox regularly** - Daily or weekly, aim for inbox zero
2. **Be specific** - "Call dentist for appointment" not "dentist"
3. **One action per task** - If multiple steps, it's a project
4. **Always add context** - Every actionable task gets a context tag
5. **Schedule deferred items** - If not now, when?
6. **Trust your system** - Once processed, don't second-guess

## Tips

- Use the `/obsidian` skill's inbox query with `.slice(0, 5)` to process just a few items at a time
- Cancelled processing leaves tasks unchanged
- Deleted tasks are removed from files
- For someday/maybe items, add lowest priority (⏬) instead of using @someday context
- All file modifications are tracked via git - commit regularly to preserve history

## Integration with Dashboard

After processing, tasks with context tags will appear in their respective Dashboard.md sections:
- @pc tasks → PC section
- @home tasks → Home section
- etc.

Tasks that remain without context tags will continue to appear in "To Process" section.

## Gmail Follow-up

If the user explicitly asks to clarify Gmail (e.g., "clarify my gmail inbox"), go straight to Gmail triage — do **not** require processing the Obsidian inbox first. If the user runs a general `/clarify` without specifying, process the Obsidian inbox first, then offer to switch to Gmail.

Use the gmcli skill/tooling for Gmail actions and follow the same confirmation-first pattern.

Gmail clarify defaults:
- When creating tasks from Gmail, use the /obsidian skill (`$OBS vault=$VAULT daily:path` then `$OBS vault=$VAULT append path=... content="- [ ] ..."`) to add to today's daily note and archive the email unless the user explicitly says not to.
- When suggesting options for Gmail triage, include a recommended context tag (e.g., @batch/@quick) and note that archiving is the default after action.
- For any "read" task created from Gmail, always include a Gmail URL that opens the email directly. Use `gmcli <email> url <threadId>` to generate the link, and place it after the task description before the context tag.
- Archive **all** triaged emails by default (including ones with tasks created), not just the ones with no action.
- `gmcli labels` does not support comma-separated thread IDs. Archive emails individually in a loop.
- **Archive syntax:** Use `gmcli <email> labels <threadId> --remove INBOX` (flag form). The positional form `gmcli <email> labels remove <threadId> INBOX` silently succeeds without archiving. Always verify the first archive with `gmcli <email> search "in:inbox" | grep <id>` before bulk-archiving the rest.
- **Always use the Obsidian CLI** (`daily:path` + `append`) to add tasks to today's daily note — it uses the system clock, which is authoritative. Do not compute today's date from the system prompt (it may be stale).

## Example Session

```
Agent: Found 3 inbox items:

GTD/Dashboard.md:
  1. Buy groceries
  2. Research new framework
  3. Fix kitchen sink

Suggestions:
  1.  Buy groceries → @out, schedule tomorrow
  1.1 Rewrite: "Buy weekly groceries" @out ⏳ 2026-01-03
  2.  Research new framework → @deep
  2.1 Promote to project (multi-step)
  3.  Fix kitchen sink → @partner (need to discuss)
  3.1 Rewrite: "Discuss kitchen sink repair options" @partner

Accept all? Or override by number:

User: accept

Agent: [executes via /obsidian skill edit-by-match patterns]
✓ 1: Rewritten + scheduled
✓ 2: Tagged @deep
✓ 3: Rewritten + tagged @partner
```

## Related Skills

- `/obsidian` — All vault read/write operations
- `/organize` — Batch context tagging, project creation
- `/project` — Multi-step outcome management
- `/review` — Weekly review workflow
