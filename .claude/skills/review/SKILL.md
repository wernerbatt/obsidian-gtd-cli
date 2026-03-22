---
name: review
description: Conduct weekly GTD review
---

# GTD Review Skill

Facilitate the weekly review process to keep your GTD system current and maintain perspective.

## Vault Operations

**Use the `/obsidian` skill for all vault reads and writes.** Load it before running any commands:
→ `.claude/skills/obsidian/SKILL.md`

**IMPORTANT:** Always use the system clock (`date`, `new Date()`) for today's date — never rely on the system prompt date, which may be stale.

Key queries for the review:
- **Inbox count:** Dataview eval inbox query → `.length`
- **Context distribution:** Dataview eval context-counts query
- **Overdue tasks:** Dataview eval overdue query
- **Stale projects:** Dataview eval stale-projects query
- **Completed this week:** Dataview eval completed-tasks query (last 7 days)
- **Someday/maybe:** Dataview eval someday query

## The Weekly Review

The weekly review is the most critical GTD practice. It's your opportunity to:
1. Get Clear - Process inbox to zero
2. Get Current - Review all your commitments
3. Get Creative - Think about new possibilities

### Step 0: Read Last Week's Summary

Before starting, check for the most recent weekly review summary:
```bash
# Read vault_path from config.yaml
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
ls -t "$VAULT_PATH/GTD/Weekly Review "*Summary.md | head -1
```
Read it and surface any "Still On The Radar" items from last time. These become the first things to check in the current review — were they addressed, or do they carry forward?

## Review Report

Generate the review report by running the `/obsidian` skill queries and assembling the results. The report includes:

#### 1. Get Clear
- **Inbox count** - How many items need processing
- Checklist for clearing all inboxes (digital and physical)
- Reminder to review daily notes

#### 2. Get Current

**Context Review:**
- Count of active tasks by context (@deep, @quick, @batch, @work, @home, etc.)
- Total active task count

**Overdue Tasks:**
- Tasks with scheduled or due dates before today
- File location and line numbers for quick access

**Projects Review:**
- Projects without next actions (stale projects)
- Checklist for reviewing all active projects

**Calendar Review:**
- Past week review
- Upcoming week preview
- Future commitments

**Live Calendar Data (gccli):**
When running the review interactively, read the `calendars` section from `config.yaml` to get the account email and calendar IDs, then pull real calendar events:
```bash
# Primary calendar — past week
gccli <account> events primary --from YYYY-MM-DDTHH:MM:SSZ --to YYYY-MM-DDTHH:MM:SSZ

# Additional calendars (loop through calendars.additional in config)
gccli <account> events <calendar-id> --from ... --to ...
```
Note: Date format must be `YYYY-MM-DDTHH:MM:SSZ` (UTC with Z suffix). Plain `YYYY-MM-DD` returns Bad Request.

**Waiting For:**
- Review @waiting items
- Follow up on pending responses

#### 3. Get Creative
- Review Someday/Maybe list
- New projects or ideas
- Review ponderables

#### 4. Completed This Week
- Tasks completed in the last 7 days
- Separate **genuine wins** (non-recurring tasks completed) from **recurring maintenance** (tasks with 🔁) — highlight the wins, summarise the recurring as a group

To save the review report, use the `/obsidian` skill's `create` command to write to `GTD/Weekly Review YYYY-MM-DD Summary.md`.

## Weekly Review Checklist

Located at: `GTD/Checklists/Weekly Review Checklist.md`

## Review Frequency

**Weekly Reviews:**
- Schedule a recurring time (e.g., Friday afternoon, Sunday evening)
- Block 30-60 minutes
- Make it non-negotiable

**Quick Daily Reviews:**
- Morning: Review today's scheduled tasks
- Evening: Process inbox, update tomorrow's list

## Infrastructure Check

During the review, verify that the daily overdue script ran recently:
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
cd "$VAULT_PATH" && git log --oneline -3
```
Look for "Automated task update" commits. If the last one is >2 days old, the scheduled task for daily scripts may need attention.

## Context & Priority Distribution

As part of Get Current, use the `/obsidian` skill's **context distribution** Dataview eval query to generate counts for all active (non-⏬) tasks by context tag. Track these week-over-week to spot trends (growing lists, priority inflation, etc.).

## Weekly Review Summary File

At the end of the review, save a summary to `GTD/Weekly Review YYYY-MM-DD Summary.md`. Follow the format of prior summaries in that folder. Include:
- Metrics (inbox, overdue, stale projects, active tasks, completed)
- Context and priority distribution
- Calendar highlights (past and upcoming week)
- Actions taken (purge results, fixes, infrastructure changes)
- Items still on the radar for next time

## Common Review Findings

### High Inbox Count
If you have many items to process:
- Block time for processing
- Use the `/clarify` skill to process inbox items

### Many Overdue Tasks
If tasks are consistently overdue:
- Re-evaluate scheduled dates
- Consider if tasks are still relevant
- Move to Someday/Maybe if not urgent
- Break down large tasks

### Stale Projects
If projects have no next actions:
- Decide if project is still active
- If YES: Define the very next action
- If NO: Move to Someday/Maybe or archive

### Too Many Active Tasks
If context lists are overwhelming:
- Be ruthless with Someday/Maybe moves
- Consider if you're over-committed
- Focus on highest-impact items

## Integration with Other Skills

The weekly review works best combined with:
1. `/obsidian` — All vault queries and edits
2. `/clarify` — Process inbox to zero
3. `/organize` — Retag and reschedule tasks
4. `/project` — Fix stale projects, create new ones
5. `/purge` — Cull bloated context lists

## Best Practices

1. **Same time each week** - Make it a ritual
2. **Distraction-free environment** - No interruptions
3. **Review everything** - Don't skip sections
4. **Update context lists** - Keep them current
5. **Reflect on wins** - Review completed tasks
6. **Look ahead** - Check calendar and upcoming commitments
7. **Trust your system** - If it's not in GTD, it doesn't exist

## Metrics to Track

The weekly review provides these metrics:
- **Inbox count** - Trending toward zero?
- **Total active tasks** - Manageable or overwhelming?
- **Overdue tasks** - Improving or getting worse?
- **Stale projects** - Are projects moving forward?
- **Completed tasks** - What did you accomplish?

Track these over time to identify patterns and improve your system.

## Example Weekly Review Session

```
[Friday 5:00 PM - Weekly Review]

1. Run review report:
   [Run /obsidian skill queries for inbox, overdue, stale, completed]

   Output:
   - Inbox: 12 items
   - Active tasks: 47
   - Overdue: 5 tasks
   - Stale projects: 2
   - Completed: 23 tasks

2. Process inbox to zero:
   [Use /clarify skill]
   [Process all 12 items...]

3. Address overdue tasks:
   [Review each overdue task, reschedule or complete]

4. Fix stale projects:
   [Add next actions to "Website Redesign" and "Garden Planning"]

5. Review context lists:
   [@deep: 8 tasks - looks good]
   [@quick: 5 tasks - can knock out today]
   [@batch: 3 tasks - schedule batch time]
   [@work: 8 tasks - manageable]
   [@home: 12 tasks - schedule for weekend]

6. Review Someday/Maybe (lowest priority tasks):
   [Found 2 items to activate, added to @ai list]

7. Final check:
   [Re-run /obsidian queries]

   Output:
   - Inbox: 0 items ✓
   - Active tasks: 51
   - Overdue: 0 tasks ✓
   - Stale projects: 0 ✓
   - Completed: 23 tasks

8. Week ahead:
   [Check calendar, schedule time blocks for priority tasks]

Total time: 45 minutes
Result: Clean, current, trusted system!
```

## Troubleshooting

**Review feels overwhelming:**
- Start with just Get Clear (inbox to zero)
- Gradually add other sections
- Use timer (Pomodoro) to stay focused

**Can't reach inbox zero:**
- Block dedicated processing time
- Use the `/clarify` skill for efficient processing
- Be ruthless with trash/someday decisions

**Projects always stale:**
- Review projects more frequently (bi-weekly)
- Keep project list smaller (5-10 active max)
- Move inactive projects to Someday/Maybe

**Too many active tasks:**
- Review and cull context lists
- Move nice-to-haves to Someday/Maybe
- Accept you can't do everything

## Related Skills

- `/obsidian` — All vault read/write operations
- `/clarify` — Inbox processing
- `/organize` — Context tagging and project creation
- `/project` — Project lifecycle management
- `/purge` — List reduction

## Resources

- Weekly Review Checklist: `GTD/Checklists/Weekly Review Checklist.md`
- Projects List: `GTD/Projects List.md`
- Dashboard: `GTD/Dashboard.md`

## Closing the Review

**Always end the review by saving a weekly summary.** This is the last step — do not consider the review complete without it.

Save to `GTD/Weekly Review YYYY-MM-DD Summary.md` following the format of prior summaries. The agent should generate this automatically at the end of the review session, even if the user doesn't ask.

## Tips

- Save weekly reviews with dates for historical tracking
- Compare metrics week-over-week to see trends
- Celebrate completed tasks before planning ahead
- Use --stale-projects during review to catch issues early
- The weekly review is when you sharpen the saw
