---
name: task-prioritisation
description: >
  Subskill for enriching Obsidian Tasks with prioritisation metadata.
  Use when creating, updating, or triaging tasks in the GTD system.
  Triggers: "prioritise my tasks", "triage my inbox", "what should I work on",
  "set priorities", "review my task list", or any request to assess, rank, or
  enrich tasks with priority or effort metadata.
---

# Task Prioritisation

Enriches Obsidian Tasks with priority and effort metadata. Two modes: single task enrichment (during task creation) or batch review (triage sessions).

## Vault Operations

**Use the `/obsidian` skill for all vault reads and writes.**
→ `.claude/skills/obsidian/SKILL.md`

## Two modes

### 1. Single task enrichment

When creating or updating a task, assign priority and effort using available context (project, conversation, goals). Ask rather than guess when confidence is low.

### 2. Batch review

When the user asks to prioritise or triage tasks:

1. Gather tasks from the file/folder specified, or search the vault for incomplete tasks.
2. Assess and assign metadata per task.
3. Present a summary for review before writing.
4. On approval, update task lines in place.

---

## Task format

Tasks use the Obsidian Tasks plugin format. A task is a markdown checkbox line in any `.md` file in the vault.

Before enrichment:

```
- [ ] Write PRD for billing reconciliation feature
```

After enrichment:

```
- [ ] Write PRD for billing reconciliation feature 🔺 @deep
```

---

## Metadata dimensions

### 1. Priority (Obsidian Tasks emoji format)

Six levels. The Eisenhower quadrant mapping is a guide for assessment, not a rigid rule.

| Emoji | Obsidian Tasks level | Eisenhower guide | When to assign |
|---|---|---|---|
| 🔺 | Highest | Q1: Urgent + Important | Hard deadline this week, blocking others, high stakes |
| ⏫ | High | Q1/Q2 boundary | Important with time pressure, or important and overdue |
| 🔼 | Medium | Q2: Important, not urgent | Strategic work, proactive, growth |
| *(none)* | Normal | Default | Most tasks start here. Don't add an emoji. |
| 🔽 | Low | Q3: Urgent, not important | Admin, interrupts, requests from others with deadlines |
| ⬇️ | Lowest | Q4: Neither | Nice-to-haves, low-value busywork, consider dropping |

**Defaults:**
- Most tasks should have no priority emoji (Normal). Only escalate when there's a reason.
- When uncertain between two levels, ask the user.

**Important:** If a task already has a priority emoji, preserve it unless the user explicitly asks to re-prioritise.

### 2. Effort tag

Assign exactly one of `@quick` or `@deep`:

| Tag | Meaning | Examples |
|---|---|---|
| `@quick` | Under 30 minutes, low cognitive load | Send an email, update a Jira ticket, reply in a thread |
| `@deep` | Sustained focus, creative or analytical | Write a PRD, run discovery, design a data model |

**Important:** If a task already has `@quick` or `@deep`, preserve it unless re-prioritising.

**Important:** If a task already has a context tag (@read, @ai, @sharne, @stuck, @ponderables, @batch, @out, @waiting, etc.), do NOT add @quick/@deep. The effort can be inferred at runtime from the context. Only add effort tags to tasks with no existing context.

### 3. Status tag: `@waiting`

Assign `@waiting` when the task is blocked on someone else's action. Include the person's name in the description so it's clear who Werner needs to chase.

```
- [ ] Chase Craig on init spec review @waiting @quick
```

### 4. Existing tags to preserve

The following tags may appear on tasks. The skill does not assign these, but must never overwrite or remove them:

- `@stuck` — task Werner has been procrastinating on, needs momentum
- `@batch` — can be grouped and knocked out together
- `@ai` — legacy tag, now assumed for all tasks
- `@ponderables` — needs thinking, no clear next action yet

If a task already has one of these tags, keep it. If the task also needs `@quick`/`@deep` or `@waiting`, add alongside.

---

## Prioritisation guidance

### For single tasks

Use available context to make the best assignment. The parent skill or process skill will typically provide project context and the source of the task (meeting, Slack message, email).

### For batch reviews

Follow this sequence:

0. **Merge sync-conflict files** — before triaging, check for any `.sync-conflict-*` files. Append their tasks to the canonical daily note and delete the conflict file.
0. **Skip future-dated tasks** — tasks with ⏳ or 📅 dates after today are pre-scheduled. Skip them unless the user explicitly asks to triage them.
1. **Group by project/area** — tasks in the same project share context that makes prioritisation easier.
2. **Apply the action item gate** — before enriching a task, check whether Werner owns it or is blocked by it. If not (e.g. another team's domain, someone else's follow-up), propose routing it instead of enriching it. Options: add to Craig 1-1 agenda, send a Slack message to the right owner, or close with a note. Don't just deprioritise tasks that shouldn't be on Werner's list.
3. **Check for duplicate task IDs** — same 🆔 appearing in multiple files means one is canonical and the rest are stale copies (often from meeting prep or week diaries). Close the non-canonical copies pointing to the authoritative file.
4. **Scan for overdue scheduled dates** — find tasks with ⏳ before today. These need triage even if already enriched: reschedule, close as stale, or flag for immediate action.
5. **Identify highest-priority tasks first** — scan for anything with a hard deadline or blocking dependency. These get 🔺 or ⏫.
6. **Surface important non-urgent work next** — look for strategic, important tasks. Flag these prominently. The user tends toward avoidance of this category (known pattern from PQ coaching: Avoider saboteur), so explicitly call out any 🔼 tasks that have been sitting for more than a week.
7. **Assess cost of delay mentally** — for each task, consider what happens if it slips another week. Use this to inform priority, but do not write cost-of-delay to the task line.
8. **Flag quick wins** — any `@quick` task with 🔺 or ⏫ priority is a good candidate for "just do it now."
9. **Suggest a working order** — after enriching, suggest an order for the user's next session. Prioritise by: 🔺 first, then ⏫ `@quick` items (build momentum), then ⏫ `@deep` items (the real work), then 🔼.

### Companion skills

During triage, the user may ask "do I need to weigh in here?" or "does this belong with me?" Use the **advisor** skill (`.claude/skills/advisor/SKILL.md`) to give grounded advice on ownership and whether the task is worth Werner's time.

### When to ask the user

Ask rather than guess when:

- The task description is ambiguous and could be quick or deep depending on scope.
- You don't know who (if anyone) is waiting on the output.
- The task involves a deadline or commitment you're not aware of.
- Multiple tasks seem equally important and ordering them requires judgment about the user's current goals or energy.

**Bare-link tasks** (URLs with no description or context) need `/clarify` processing, not enrichment. Don't try to add priority or effort to a task that hasn't been clarified yet — flag them for a clarify session instead.

Batch your questions. Don't ask one at a time:

```
I've enriched 12 of 15 tasks. For these 3, I need your input:

1. "Follow up with Sarah on API design" — quick Slack message (@quick) or
   longer design discussion (@deep)?
2. "Prepare for Q2 planning" — is there a deadline? I'd leave it Normal otherwise.
3. "Update onboarding docs" — is anyone actively using these? Affects priority.
```

---

## Writing changes

When updating task lines:

- **Preserve everything** already on the line: description, dates, tags, links, IDs, dependency markers.
- **Append** new metadata after existing content, before any trailing dates or block references.
- **Don't rewrite** the task description.
- **Don't change** completion status.
- **Present a diff-style summary** before writing, showing what will change.
- **Mark done immediately** — when the user says "done" for a task during a triage session, update the file right then. Don't defer file writes to end of session.

Example:

```
Updates to GTD/Projects/Billing Reconciliation.md:

 - [ ] Write PRD for billing reconciliation feature
 + - [ ] Write PRD for billing reconciliation feature ⏫ @deep

 - [ ] Check if finance team has sample data
 + - [ ] Check if finance team has sample data @quick
```

Wait for user approval before writing to files.

---

## Cold start

If invoked directly without context:

1. Ask which file(s) or folder(s) to scan, or ask the user to paste tasks directly.
2. Ask about current deadlines, blockers, or priorities the user has in mind.
3. Proceed with batch review mode.
