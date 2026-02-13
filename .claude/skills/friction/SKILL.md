---
name: friction
description: Run the Friction Elimination protocol — diagnose resistance on stuck/avoided tasks and remove barriers to action. Use when the user feels stuck, is procrastinating, or can't start something important.
---

# Friction Elimination Skill

When the user is stuck, avoiding a task, or "can't get motivated," run this protocol instead of offering encouragement. The goal is never more force — it's less friction.

Reference: [[Friction Elimination]] in the vault.

## When to Trigger

- User says they're stuck, procrastinating, or unmotivated
- Weekly/daily review surfaces tasks that keep getting deferred
- A task has been rescheduled 3+ times
- User asks "what should I work on?" but nothing feels approachable

## The Protocol

Run the four steps below conversationally. You don't need to announce the framework — just work through it naturally.

### Step 1 — Resistance Map

**Goal:** Surface what's being avoided and why.

1. Pull the user's current task list (inbox, overdue, context lists):
   ```bash
   cd /path/to/obsidian-gtd-cli
   python tools/find_tasks.py --mode inbox --show-details
   python tools/find_tasks.py --query overdue --show-details
   ```

2. Ask the user: *"Which of these feel heavy right now? What comes to mind when you think about starting them?"*

3. Capture their responses and identify which resistance type is at play for each task:
   - **Activation Energy** — task feels too big or vague to start
   - **Psychological Reactance** — obligation is triggering rebellion ("I should" → "I don't want to")
   - **Uncertainty Paralysis** — can't picture "done," too many possible approaches

4. For each stuck task, define the **stupidest-easy first action** — not the task itself, just the entry point. Write it down as a concrete next action.

**Claude Code moves:**
- Scan for repeatedly-deferred tasks (scheduled date < today, rescheduled multiple times).
- Rewrite vague tasks into specific next actions using `edit_task.py`.
- Break multi-step items into projects with `create_project.py` if the real issue is that it's not a single action.

```bash
# Rewrite a vague task into a concrete next action
python tools/edit_task.py --file "Daily/2026-02-06.md" --match "Work on presentation" --description "Open slides.pptx and write the title slide" --yes

# Promote to project if it's actually multi-step
python tools/create_project.py "Kitchen Renovation" --next-action "Get 3 quotes from contractors @quick"
```

### Step 2 — Activation Energy Audit

**Goal:** Pre-decide everything so there are zero decisions at go-time.

For each high-friction task, lock in:

| Decision | Example |
|----------|---------|
| **When** (time trigger, not feeling) | "Tomorrow 9:00 AM" |
| **Where** (same place every time) | "Desk, laptop open" |
| **What first** (single opening move) | "Open the document and read the first paragraph" |
| **How long minimum** | "15 minutes, then you can stop" |

**Claude Code moves:**
- Schedule the task with a concrete date:
  ```bash
  python tools/edit_task.py --file "GTD/Projects/Presentation.md" --match "Open slides" --scheduled 2026-02-07 --yes
  ```
- Create the file/scaffold/outline so the blank page is already gone:
  ```bash
  # Example: pre-populate a draft so the user reacts instead of creates
  ```
- Add a time-block to the daily note or calendar (via gccli skill) so the "when" is locked.

### Step 3 — Certainty Builder

**Goal:** Define "done" before starting so the brain stops generating uncertainty.

For each stuck task, define:
- **What does finished look like?** (specific, not "better" or "good enough")
- **What's the absolute minimum that counts?** (the floor, not the ceiling)
- **What info is actually needed vs. procrastination-as-research?**

**Claude Code moves:**
- Draft a minimum-viable version of the deliverable. A rough first pass the user can react to:
  ```
  "Here's a 3-bullet skeleton of that email. Edit it or tell me what's wrong with it — 
  that's easier than writing from scratch."
  ```
- Add done-criteria as a checklist in the project file:
  ```bash
  # Append completion criteria to a project
  ```
- If the user is "researching" endlessly, call it out: *"You have enough to start. What would a terrible first draft look like?"*

### Step 4 — Environment Forcing Function

**Goal:** Make starting easier than avoiding.

- **Open the exact context** the user needs — files, notes, references — in one move.
- **Close the noise** — if they're in clarify mode but need to switch to deep work, help them transition.
- **Suggest phone-away** if they mention distraction.

**Claude Code moves:**
- Read the relevant project file, daily note, and any reference material in one prompt so everything is loaded and visible.
- Pre-stage the workspace:
  ```bash
  # Read the project so context is loaded
  cd /path/to/obsidian-gtd-cli
  VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
  cat "$VAULT_PATH/GTD/Projects/Presentation.md"
  ```
- The agent itself becomes the environment — one prompt and the user is inside the work, not deciding whether to start.

## Integration with GTD Skills

### During Clarify
When processing inbox items, watch for resistance signals:
- User keeps saying "skip" or "later"
- Items keep getting deferred to someday/maybe
- Energy drops mid-session

Switch to friction mode: *"We've skipped 3 items in a row. Want to look at what's making these feel heavy?"*

### During Review
Flag chronically deferred tasks:
```bash
# Find tasks that have been rescheduled repeatedly (manual check)
cd /path/to/obsidian-gtd-cli
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
grep -rn "⏳" "$VAULT_PATH/GTD/" --include="*.md" | grep "$(date -d '-7 days' +%Y-%m-%d)\|$(date -d '-14 days' +%Y-%m-%d)"
```

Present them as friction candidates rather than failures.

### Context Tag Hints

If friction diagnosis reveals a pattern, suggest the right context:
- Activation energy too high → break down + `@quick` for the first micro-action
- Reactance ("I should but don't want to") → reframe as `@batch` (lower perceived obligation when grouped)
- Uncertainty → `@deep` with a scheduled block and pre-built scaffold

## Example Session

```
User: I keep putting off that allotment proposal. I just can't start.

Agent: Let me pull that up.

[Reads project file, finds task has been rescheduled 4 times]

Agent: This has moved 4 times. That's not laziness — that's friction. 
Let's figure out what kind.

When you think about starting it, what's the first thought?

User: I don't even know what format it should be in. And it feels massive.

Agent: Two things going on:
1. Uncertainty — you can't picture "done" yet
2. Activation energy — it feels like one big thing

Let's fix both right now.

What's the absolute minimum this proposal needs to contain? 
Just the sections — not the content.

User: Uh... what we want to grow, the layout, and a cost estimate.

Agent: Done. Here's your skeleton:

---
# Allotment Proposal
## What We Want to Grow
- (list crops here)
## Layout
- (sketch or describe bed arrangement)
## Cost Estimate
- (seeds, tools, soil — rough numbers)
---

That's your floor. Anything beyond this is bonus.

Now — the stupidest-easy first action. Not "write the proposal." 
Just: "Open this file and list 5 crops under section 1."

Want me to schedule that for tomorrow morning and put it in your daily note?

User: Yeah, do it.

[Agent creates the file, adds the task with scheduled date, 
adds time block to daily note]

Agent: Done. Tomorrow at 9 AM you'll see:
"- [ ] Open Allotment Proposal.md and list 5 crops @quick ⏳ 2026-02-07"

The file already exists. The sections are already there. 
You just need to type 5 crop names. That's it.
```

## Key Principles

- **Never say "just do it"** — that's the opposite of this system.
- **Resistance is diagnostic data**, not a character flaw.
- **Make starting stupider-easy** than the user thinks is reasonable.
- **Draft the floor version** so they react instead of create from nothing.
- **The agent is the environment** — load context, remove decisions, collapse the gap between deciding and doing.
- **Three levels:** Level 1 = wait for motivation. Level 2 = override with discipline. **Level 3 = remove the friction that made both necessary.** Always aim for Level 3.
