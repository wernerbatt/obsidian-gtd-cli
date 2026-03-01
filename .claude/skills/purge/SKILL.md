---
name: purge
description: Reduce bloated GTD lists by renegotiating commitments—drop, demote, merge, or simplify tasks using GTD best practice.
---

# GTD Purge Skill

Systematically reduce task list bloat by walking through every active task and forcing a keep/drop/demote decision. Based on David Allen's principle that a long list isn't the problem—carrying un-renegotiated commitments is.

## When to Use

- Context lists feel overwhelming (>15–20 active items in a single context)
- You're avoiding looking at your lists
- Weekly review keeps skipping the "cull" step
- You notice tasks that have been sitting untouched for weeks
- Total active tasks exceed what you can realistically engage with

## Quick Start

```bash
cd /path/to/obsidian-gtd-cli

# See the full picture first
python3 tools/weekly_review.py

# Find unprocessed inbox tasks
python3 tools/find_tasks.py --query inbox --verbose

# Scan a specific context
python3 tools/find_tasks.py --query tag --tag @quick --verbose

# See all open tasks
python3 tools/find_tasks.py --query all --verbose

# See someday/maybe backlog
python3 tools/find_tasks.py --query someday --verbose
```

Then ask the agent to run a purge session (see Workflow below).

## Core Principles (GTD-Aligned)

1. **Renegotiate, don't just delete.** Every task was a commitment. Consciously decide: "Am I still committed to this?" If not, deliberately let it go. Allen calls this renegotiating an agreement with yourself.

2. **Someday/Maybe is the pressure valve.** If you're not actively committed but don't want to lose it, demote to ⏬ (lowest priority). This keeps active lists lean and trustworthy.

3. **Merge duplicates and overlapping tasks.** Capture happens fast; duplicates creep in. Combine them into one clear action.

4. **Clarify vague tasks or kill them.** If a task has sat for weeks and you still can't picture the next physical action, it's not actionable yet. Either rewrite it as a concrete action or drop/demote it.

5. **Projects should only surface 1–2 next actions.** If your list is bloated because project steps are all visible, ensure blocking chains (⛔/🆔) are correct so only the true next action is unblocked.

6. **Completed work should be marked done.** Anything you've already done but forgot to check off gets marked done now.

7. **Stale recurring tasks need attention.** If a recurring task lost its recurrence or is overdue, fix or retire it.

## Workflow

### Phase 1: Triage Scan

The agent scans all open tasks **excluding ⏬ (lowest priority / Someday-Maybe)** and groups them into triage categories:

| Category | Criteria | Default Action |
|----------|----------|----------------|
| **Empty** | Blank `- [ ]` lines with no content | Drop |
| **Stale** | Open, no scheduled/due date, no context, created >4 weeks ago, no activity | Candidate for drop or demote |
| **Overdue** | Scheduled/due date in the past | Reschedule, do, or drop |
| **Duplicate** | Very similar description to another open task | Merge into one |
| **Vague** | No concrete action verb, unclear next step | Rewrite or drop |
| **Completed** | Context suggests already done (e.g., event passed) | Mark done |
| **Orphaned daily note tasks** | Open tasks in old daily notes, no scheduled date, no context, never processed | Process, move, or drop |
| **Blocked chain issues** | Project tasks with broken/missing dependency chains | Fix chain or simplify |
| **Broken system items** | Recurring tasks that lost recurrence, placeholder project tasks | Fix |

When scanning, always filter out:
- Tasks with ⏬ priority (review these in **someday purge** mode instead)
- Completed tasks
- Tasks in Templates, Checklists folders
- **Tasks with a scheduled date (⏳) don't need a context tag** — they will surface when the date arrives. Skip them in orphan/no-context triage.

```bash
# The agent will use these tools during triage:
python3 tools/find_tasks.py --query inbox --verbose
python3 tools/find_tasks.py --query someday --verbose
python3 tools/find_tasks.py --query tag --tag @quick --verbose   # per-context scan
python3 tools/find_tasks.py --query all --verbose                # everything open
```

### Phase 2: Context-by-Context Purge

Work through each context list one at a time. For each context, present all active tasks and ask the user to make a decision on each:

**Decision options per task:**

| Code | Action | What Happens |
|------|--------|--------------|
| **keep** | Keep as-is | No change |
| **drop** | Delete permanently | Task removed from file |
| **demote** | Reduce priority by one step | Demote one level (see priority ladder below) |
| **done** | Already completed | Mark done with ✅ |
| **merge** | Combine with another task | Keep one, mark other done |
| **rewrite** | Clarify the task | Edit description to concrete next action |
| **reschedule** | Push to future date | Update ⏳ date |
| **move** | Move to different context | Change context tag |
| **project** | Promote to project | Create project note, seed next actions |

**Priority ladder (Obsidian Tasks plugin — 6 levels):**

🔺 highest → ⏫ high → 🔼 medium → (normal) → 🔽 low → ⏬ lowest

When demoting, **move one step down by default** — not straight to ⏬. For example: 🔼 → normal, normal → 🔽. Only demote to ⏬ if the user explicitly asks to send something to Someday/Maybe.

Note: `edit_task.py` cannot remove a priority (only set one). To demote from 🔼/⏫/🔺 to normal, edit the file directly to strip the priority emoji.

**Context processing order** (heaviest lists first):
1. Orphaned daily note tasks (biggest source of bloat)
2. @read (reading lists grow fastest)
3. @quick
4. @deep
5. @batch
6. @pc (legacy — migrate or drop)
7. @home
8. @partner
9. @ai
10. @ponderables
11. @work
12. @out
13. Projects review (stale/stuck projects)

### Phase 3: Project Pruning

For each active project:
1. Is this project still a current commitment? → If not, demote entire project to Someday/Maybe or archive to Completed Projects.
2. Does it have a clear, unblocked next action? → If not, define one or put project on hold.
3. Are the dependency chains correct? → Fix any broken ⛔/🆔 references.
4. Are there too many steps visible? → Ensure only 1–2 are unblocked.

### Phase 4: Recurring Task Cleanup

Review `GTD/Recurring.md`:
1. Flag any recurring task that lost its recurrence pattern (like the Weekly Review task).
2. Identify recurring tasks with excessive completed-instance history — these are fine but note the file size.
3. Confirm all active recurrences still make sense.

### Phase 5: Summary Report

After purging, produce a summary:

```
=== Purge Summary ===
Tasks before:  509
Tasks dropped:  XX
Tasks demoted:  XX (→ Someday/Maybe)
Tasks done:     XX
Tasks merged:   XX
Tasks rewritten: XX
Tasks after:   XXX
---
Active projects: XX (was XX)
Stale projects fixed: XX
```

## IMPORTANT: Confirmation & Execution

**Batch presentation with user control:**

1. Present tasks in batches of 10 per context.
2. For each batch, show numbered tasks with a suggested action based on triage criteria:
   ```
   @read (42 tasks — suggesting cuts)
   
   1. Read Zhengdong Wang best facts article          → suggest: keep
   2. Read [The Shape of AI...]                       → suggest: keep (recent, high-quality)
   3. Read New Yorker: why AI didn't transform...     → suggest: demote ⏬ (5 weeks old)
   4. Read [Demystifying evals for AI agents]         → suggest: keep (@ai relevant)
   5. Read Substack article [no title, bare URL]      → suggest: drop (vague, 3 weeks)
   ...
   
   Accept all suggestions? Or type numbers to override (e.g., "3: keep, 5: keep")
   ```

3. The user can:
   - Accept all suggestions at once
   - Override specific items by number
   - Skip the entire context ("skip")
   - Stop the session ("stop")

4. After confirmation, execute all actions for that batch before moving to the next.

5. **Never delete or demote without the user seeing the suggestion first.**

6. Use `--yes` flag on tools only after the user has confirmed.

## Suggestion Heuristics

The agent should use these heuristics when suggesting actions:

| Signal | Suggestion |
|--------|------------|
| Task has ⏬ priority | **skip** (not in scope — use someday purge mode) |
| Task is an empty `- [ ]` line | **drop** |
| Task >6 weeks old, no scheduled date, no priority | **drop** or **demote** ⏬ |
| Task is a bare URL with no description | **drop** or **rewrite** |
| Task is a TikTok/Instagram link (without ⏬) | **demote** ⏬ (ephemeral content) |
| Task description matches another open task | **merge** |
| Task references a past event/date | **done** or **drop** |
| Task is in @pc (legacy) | **move** to @deep/@quick/@batch |
| Task has no context tag, sitting in daily note | **rewrite + move** or **drop** |
| Reading task from >4 weeks ago | **demote** ⏬ unless high priority |
| Project with no next action for >2 weeks | **define next action** or **archive** |
| Recurring task lost its 🔁 pattern | **fix** recurrence |
| Placeholder/generic project task (e.g. "First next action") | **rewrite** to concrete action |

## Tools Used

All tools accept `--match` (exact) or `--match-regex` for fuzzy matching, plus `--yes` for agentic use.
File paths are relative to the vault root.

```bash
# SCAN — find tasks to triage (use find_tasks.py from obsidian-cli or obsidian-gtd-cli)
python3 tools/find_tasks.py --query tag --tag @quick --verbose   # by context
python3 tools/find_tasks.py --query all --verbose                # all open tasks
python3 tools/find_tasks.py --query inbox --verbose              # unprocessed
python3 tools/find_tasks.py --query someday --verbose            # ⏬ backlog

# DROP — delete task line entirely
python3 tools/delete_task.py --file <path> --match "<desc>" --match-regex --yes

# DEMOTE — add ⏬ priority (Someday/Maybe)
python3 tools/edit_task.py --file <path> --match "<desc>" --match-regex --description "<desc>" --priority ⏬ --yes

# DONE — mark task complete
python3 tools/mark_done.py --file <path> --match "<desc>" --match-regex --date today --yes

# REWRITE — change description and/or context
python3 tools/edit_task.py --file <path> --match "<desc>" --match-regex --description "New clear description" --context @deep --yes

# RESCHEDULE — set or update ⏳ date
python3 tools/edit_task.py --file <path> --match "<desc>" --match-regex --description "<desc>" --scheduled 2026-03-01 --yes

# MOVE CONTEXT — change context tag
python3 tools/edit_task.py --file <path> --match "<desc>" --match-regex --description "<desc>" --context @batch --yes

# MOVE TO FILE — relocate task between files
python3 tools/move_task.py --source <path> --match "<desc>" --match-regex --dest "GTD/Projects/<Name>.md" --yes

# CREATE PROJECT
python3 tools/create_project.py "<Name>" --context @deep --yes
```

**Important:** Use the CLI tools for all modifications. Do not read files and edit them manually.
The `find_tasks.py --query tag` output provides file paths and line numbers needed by the other tools.

## Scope: What Gets Purged

**In scope (active commitments):**
- All open tasks that do NOT have ⏬ (lowest priority)
- These are things you've implicitly said "I'm doing this" — the purge forces you to re-confirm or let go

**Out of scope by default:**
- Tasks with ⏬ priority (Someday/Maybe) — these are already parked. Purging them defeats the purpose of the pressure valve.
- Completed tasks (`[x]`)
- Tasks in Templates, Checklists

**Someday/Maybe purge (separate mode):**
- Use `someday` mode to review the ⏬ backlog specifically
- This is a different mindset: not "am I committed?" but "do I still want this on my radar at all?"
- Heuristics differ: age matters less (they're meant to sit), but items that no longer spark any interest should be dropped
- Suggested cadence: quarterly, or when ⏬ list exceeds ~100 items

## Session Management

- **Full purge:** Walk all active (non-⏬) contexts and projects. Takes 30–60 minutes. Do this quarterly or when the system feels untrusted.
- **Quick purge:** Target one or two contexts (e.g., just @read and daily notes). Takes 10–15 minutes. Good for weekly review add-on.
- **Auto-suggest purge:** Agent scans active (non-⏬) tasks only and presents those matching stale/vague/duplicate heuristics. Fastest — just review the flagged items.
- **Someday purge:** Review ⏬ items only. Different mindset — "do I still want this on my radar?" Drop anything that no longer interests you. Do this quarterly.

Ask the user which mode they want at the start of each session.

## Coordination With Other Skills

- **Clarify**: Orphaned daily note tasks that survive the purge should be processed through Clarify to get proper context tags.
- **Organize**: Tasks that get rewritten or moved during purge should end up properly tagged and filed.
- **Project**: Projects identified during purge as stale get either revived (new next action) or archived.
- **Review**: The purge is a deeper version of the "cull" step in weekly review. Run purge when weekly review alone isn't enough.

## Anti-Patterns to Watch For

- **Purging too aggressively** — If the user drops >50% of tasks, pause and check: are these genuinely not commitments, or is this avoidance? Some tasks are hard but important.
- **Demoting everything** — Someday/Maybe shouldn't become a second junk drawer. If it grows past ~100 items, it needs its own purge.
- **Skipping the rewrite step** — A vague task that gets "kept" will just sit there again. Push to rewrite or drop.
- **Not fixing the capture habit** — If daily notes keep accumulating unprocessed tasks, the real fix is more frequent clarify sessions, not more purges.

## Example Session

```
Agent: Ready to purge. You have 509 open tasks. What mode?
  1. Full purge (all contexts + projects, ~45 min)
  2. Quick purge (pick 1-2 contexts, ~15 min)  
  3. Auto-suggest (only flagged items, ~10 min)

User: 3

Agent: Running triage scan...

Found 47 flagged items across your system:

=== Orphaned Daily Note Tasks (23 items) ===
Batch 1/3:

1. "rubber bands XL" (Jan 2, no context)           → suggest: drop
2. "cribbage @quick" (Jan 2)                        → suggest: keep
3. "[Cool astrophotographer] @quick" (Jan 3)        → suggest: demote ⏬
4. "https://thetopsecretcomedyclub.co.uk" (Jan 3)   → suggest: rewrite "Check Top Secret Comedy Club events @quick"
5. "when I pick up phone..." @deep (Jan 6)          → suggest: rewrite "Draft phone pickup rules @deep" or drop
6. "ready made proteïen @quick" (Jan 12)            → suggest: rewrite "Research ready-made protein options @quick"
7. "change alarm sounds" (Jan 21)                   → suggest: keep (scheduled Feb 7)
8. empty task "- [ ] " (Jan 24)                     → suggest: drop
9. "Check on side-project" (Jan 25)               → suggest: keep (recurring)
10. "Pi Moon Mission Patch @quick" (Jan 25)         → suggest: keep or demote

Accept all suggestions? Or type numbers to override:

User: accept, but 1: keep (need them for allotment labels)

Agent: Got it. Executing...
✓ 3: Demoted to ⏬
✓ 4: Rewritten → "Check Top Secret Comedy Club events @quick"
✓ 6: Rewritten → "Research ready-made protein options @quick"  
✓ 8: Dropped (empty task)
(7 others kept as-is)

Next batch? (y/n/stop)
```
