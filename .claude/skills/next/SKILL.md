---
name: next
description: >
  AI-driven task picker that selects the single best thing to work on,
  pre-fetches context, assesses delegation level, and helps execute.
  Triggers: "what's next", "what should I work on", "next", "pick a task",
  "I'm free", or any request for the next action.
---

# /next — Task Picker & Executor

One command. AI picks the task, assesses how much of you it needs, helps execute, moves on.

## Core Philosophy

- **AI picks, you veto.** No lists. One task at a time.
- **Every task has a delegation level.** The question isn't just "what" but "how much of you does it need?"
- **Reversibility is the safety line.** AI can do anything reversible without asking. Always report what was done.
- **Motion over perfection.** Picking a good task fast beats picking the perfect task slowly.
- **Stay with the task.** The goal is to COMPLETE the task, not whizz through the list. Stay with a task until it's done or the user explicitly says skip/next.

## Delegation Levels

Based on the Teresa Torres framework. Assessed per task before presenting.

| Level | What happens | You do | AI does |
|---|---|---|---|
| **Automate** | AI does it entirely, reports back | Read the summary | Everything |
| **Assist** | AI drafts/researches, you review | Approve or tweak | The heavy lifting |
| **Prompt** | AI needs one quick input from you | Answer one question | Everything else |
| **Collaborate** | Requires your judgment, creativity, or emotion | Think and decide | Support, scaffold, unblock |

### Reversibility Guide

These actions are reversible — AI can do them and report after:

- Mark a task done (can be unchecked)
- Web research and summarise findings
- Read/search vault files
- Create a draft or note (can be deleted)
- Add a task to the daily note (can be removed)
- Look up calendar events

These need your go before executing:

- Send a message or email
- Book or create calendar events
- Delete or move vault content
- Edit existing task descriptions
- Anything involving another person

**Always tell the user what you did**, even for reversible actions. One line is enough.

## Vault & Calendar Operations

**Use the `/obsidian` skill for all vault reads and writes.**
→ `.claude/skills/obsidian/SKILL.md`

**Use gccli for calendar operations.**

## Task Selection Algorithm

### Step 1: Gather candidates

Pull in parallel:

1. **Calendar** — events in the next 2 hours (via gccli). If a meeting is within 30 min, it takes priority as "prep for this meeting."
2. **Vault tasks** — all incomplete, non-someday (⏬), non-blocked (⛔) tasks via Dataview eval.

### Step 2: Score and rank

Pick the single best task using this priority:

1. **Meeting in ≤30 min** → prep for it (always wins)
2. **🔺 Highest priority** → do first
3. **⏫ + @quick** → momentum builders
4. **⏫ + @deep** → the real work
5. **🔼 overdue or aging >7 days** → surface with Avoider nudge (see PQ integration)
6. **🔼 @quick** → easy wins
7. **Normal priority, due today** → obligations
8. **@quick with no priority** → filler if energy is low

Context signals to factor in:
- **Time of day**: morning → favour @deep; afternoon → favour @quick; evening → favour @batch/@read
- **Session momentum**: if user just completed 2+ @quick tasks, suggest a @deep task ("you've got momentum — time for the real work?")
- **Recency**: prefer tasks from recent daily notes and active projects over deep archive

### Step 3: Pre-fetch context

Before presenting, gather everything the user needs:

- Read the vault note if one exists (wikilink in task)
- Read the project file if the task is in a GTD/Projects/ file
- Check for related tasks (same 🆔 chain)
- Resolve URLs — for links, fetch the page title/summary
- Check calendar for scheduling constraints

### Step 4: Assess delegation level

| Signal | Delegation level |
|---|---|
| Task is a URL to read/watch | **Automate** (summarise) or **Assist** (summarise + recommend). Check `Clippings/` folder first — if a clipping exists, read it. If not, ask the user to create one via the snipping tool, or try gmcli for email content. |
| Task is "research X" | **Automate** (search + summarise) or **Assist** (present findings) |
| Task is "check on X" / recurring check | **Automate** (check + report) |
| Task is "draft X" / "write X" | **Assist** (draft, you review) |
| Task is "discuss with [person]" | **Prompt** (AI preps talking points, you have the conversation) |
| Task is "decide X" / @ponderables | **Collaborate** (explore together) |
| Task is @stuck | **Collaborate** (trigger stuck skill) |
| Task involves sending/booking/committing | **Assist** (AI preps, you approve the action) |
| Task is vague / no clear next action | **Prompt** (clarify what it actually is, then re-assess) |

## Presentation Format

Keep it tight. No essays.

```
[task description]
📍 [file path]  [delegation level icon]

[1-2 lines of pre-fetched context]

[action prompt based on delegation level]
```

### By delegation level:

**Automate:**
```
Check on mollycantillon @quick
📍 Daily/2026/2026-01-25.md  🤖 Automate

Checked — last post was 2 weeks ago, nothing new since.

✅ Marked done.
```
(Already did it. Just informing.)

**Assist:**
```
Research Aeyla sleep solutions @deep 🔼
📍 Daily/2026/2026-01-11.md  🔧 Assist

Aeyla sells weighted blankets and cooling pillows. 4.6★ on Trustpilot,
30-night trial, £79-£149 range. Main product is the dual-comfort pillow.

Want me to write up a comparison note, or is this enough to decide?
```

**Prompt:**
```
Discuss putting password in sealed envelope with Sharné @sharne
📍 GTD/Projects/List of accounts.md  💬 Prompt

You have a password vault. The task is about emergency access if
something happens to you.

When are you next seeing Sharné today/tonight? I'll prep the talking points.
```

**Collaborate:**
```
Werner's AI Career Strategy @ponderables 🔺
📍 Daily/2026/2026-02-21.md  🤝 Collaborate

This has been 🔺 for a month. Your vault note explores three paths:
stay technical, move to AI product, or independent consulting.

Where's your head at with this right now?
```

## Flow

```
User: "what's next"

AI: [presents one task with context + delegation assessment]

User: "go"     → AI executes at the assessed delegation level
      "skip"   → AI picks the next task (no list, no guilt)
      "done"   → AI marks done, picks next
      "drop"   → AI marks dropped, picks next
      [talks]  → Collaborative mode — work through it together
```

### After completion

When a task is done/dropped/skipped, immediately present the next one. No "what would you like to do?" — just keep the conveyor belt moving.

If the user has completed 3+ tasks in a row, acknowledge the momentum:
> "That's [N] knocked off. Keep going or take a break?"

## PQ Integration

### Avoider Detection

Watch for these signals:
- User says "skip" 3+ times in a row
- User says "not the right time" or "I'll come back to this"
- 🔼 tasks that have been aging >7 days keep getting skipped

When detected, gently surface it:
> "That's 3 skips. Your Avoider might be running — want to look at what's making these feel heavy?"

If yes → hand off to the `/stuck` skill.

### When presenting 🔼 tasks aging >7 days

Note the pattern without lecturing:
> "This has been sitting since [date]. Might be worth a look — or drop it if the moment's passed."

## Stuck Handoff

If the user engages with a task but hits resistance (can't start, hesitating, avoidance language), switch to `/stuck` mode seamlessly. Don't announce "switching to stuck skill" — just start coaching.

## Calendar Integration

When a meeting is ≤30 min away:

```
Meeting: 1:1 with Craig (2:00 PM, 30 min)
📍 Google Calendar  🔧 Assist

Last met: Mar 14 — discussed API spec review.
You have 2 @waiting tasks mentioning Craig.

Want me to pull those tasks and draft an agenda?
```

## What NOT to Do

- Don't present lists. Ever. One task.
- Don't ask "what's your energy level?" — infer from time of day and session pattern.
- Don't over-explain the delegation level — just act on it.
- Don't ask permission for reversible actions — do them, report back.
- Don't stall. If context fetch takes too long, present the task with what you have.
- Don't repeat a skipped task in the same session unless the user asks.
- Always include the link when presenting a URL-based task.
- Use gmcli to fetch email content for Gmail-linked tasks — don't say "I can't access it."

## Cold Start

If invoked with no context:

1. Check calendar for imminent meetings (next 30 min)
2. Pull top-priority tasks from vault
3. Present the best one

No questions. No "what would you like to focus on?" Just go.
