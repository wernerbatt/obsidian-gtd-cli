---
name: review
description: Conduct weekly GTD review
---

# GTD Review Skill

Facilitate the weekly review process to keep your GTD system current and maintain perspective.

## Quick Start

Generate weekly review report:
```bash
cd /mnt/c/Users/werne/obsidian-gtd-cli
python tools/weekly_review.py
```

Save review to file:
```bash
cd /mnt/c/Users/werne/obsidian-gtd-cli
python tools/weekly_review.py --output "Weekly Review 2026-01-02.md"
```

## The Weekly Review

The weekly review is the most critical GTD practice. It's your opportunity to:
1. Get Clear - Process inbox to zero
2. Get Current - Review all your commitments
3. Get Creative - Think about new possibilities

## Tool: weekly_review.py

Generate comprehensive weekly review reports with metrics and checklists.

### Basic Usage

```bash
# Display review to terminal
python tools/weekly_review.py

# Save review to file in vault
python tools/weekly_review.py --output "Weekly Review 2026-01-02.md"

# Show only projects without next actions
python tools/weekly_review.py --stale-projects

# Open review in Obsidian after generation
python tools/weekly_review.py --output review.md --open
```

### Report Sections

The weekly review report includes:

#### 1. Get Clear
- **Inbox count** - How many items need processing
- Checklist for clearing all inboxes (digital and physical)
- Reminder to review daily notes

#### 2. Get Current

**Context Review:**
- Count of active tasks by context (@pc-deep, @pc-quick, @pc-batch, @work, @home, etc.)
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

**Waiting For:**
- Review @waiting items
- Follow up on pending responses

#### 3. Get Creative
- Review Someday/Maybe list
- New projects or ideas
- Review ponderables

#### 4. Completed This Week
- Tasks completed in the last 7 days
- Shows your accomplishments

### Options

- `--output FILE` or `-o FILE` - Save report to file (relative to vault)
- `--stale-projects` - Show only projects without next actions
- `--open` - Open file in Obsidian after generation (requires --output)

## Weekly Review Checklist

Located at: `GTD/Checklists/Weekly Review Checklist.md`

The tool complements your existing weekly review checklist by providing metrics and identifying issues.

## Review Frequency

**Weekly Reviews:**
- Schedule a recurring time (e.g., Friday afternoon, Sunday evening)
- Block 30-60 minutes
- Make it non-negotiable

**Quick Daily Reviews:**
- Morning: Review today's scheduled tasks
- Evening: Process inbox, update tomorrow's list

## Common Review Findings

### High Inbox Count
If you have many items to process:
- Block time for processing
- Use `find_inbox.py` to see what needs attention
- Use `process_item.py` for interactive processing

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

## Integration with Other Tools

The weekly review works best combined with other tools:

```bash
# 1. Start with weekly review to see overview
python tools/weekly_review.py

# 2. Process inbox to zero
python tools/find_tasks.py --mode inbox
python tools/process_item.py --file GTD/Dashboard.md --line 42

# 3. Review overdue tasks
python tools/add_context.py --search "overdue" --scheduled tomorrow

# 4. Update stale projects
python tools/create_project.py "New Project" --context "@pc"

# 5. Generate final review report
python tools/weekly_review.py --output "Weekly Review 2026-01-02.md"
```

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
   $ python tools/weekly_review.py --output "Review-2026-01-02.md"

   Output:
   - Inbox: 12 items
   - Active tasks: 47
   - Overdue: 5 tasks
   - Stale projects: 2
   - Completed: 23 tasks

2. Process inbox to zero:
   $ python tools/find_inbox.py
   $ python tools/process_item.py --file GTD/Dashboard.md --line 42
   [Process all 12 items...]

3. Address overdue tasks:
   [Review each overdue task, reschedule or complete]

4. Fix stale projects:
   [Add next actions to "Website Redesign" and "Garden Planning"]

5. Review context lists:
   [@pc-deep: 8 tasks - looks good]
   [@pc-quick: 5 tasks - can knock out today]
   [@pc-batch: 3 tasks - schedule batch time]
   [@work: 8 tasks - manageable]
   [@home: 12 tasks - schedule for weekend]

6. Review Someday/Maybe (lowest priority tasks):
   [Found 2 items to activate, added to @ai list]

7. Final check:
   $ python tools/weekly_review.py

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
- Use `process_item.py` for efficiency
- Be ruthless with trash/someday decisions

**Projects always stale:**
- Review projects more frequently (bi-weekly)
- Keep project list smaller (5-10 active max)
- Move inactive projects to Someday/Maybe

**Too many active tasks:**
- Review and cull context lists
- Move nice-to-haves to Someday/Maybe
- Accept you can't do everything

## Related Tools

- `find_inbox.py` - Find items to process
- `process_item.py` - Interactive processing
- `add_context.py` - Batch update tasks
- `create_project.py` - Create new projects

## Resources

- Weekly Review Checklist: `GTD/Checklists/Weekly Review Checklist.md`
- Projects List: `GTD/Projects List.md`
- Dashboard: `GTD/Dashboard.md`

## Tips

- Save weekly reviews with dates for historical tracking
- Compare metrics week-over-week to see trends
- Celebrate completed tasks before planning ahead
- Use --stale-projects during review to catch issues early
- The weekly review is when you sharpen the saw
