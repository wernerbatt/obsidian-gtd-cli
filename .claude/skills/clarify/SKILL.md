---
name: clarify
description: Process inbox items using GTD workflow
---

# GTD Clarify Skill

Help process unprocessed items in the Obsidian vault using GTD (Getting Things Done) methodology.

## Quick Start

Find items to process:
```bash
cd /path/to/obsidian-gtd-cli
python tools/find_inbox.py
```

Process a specific task interactively:
```bash
cd /path/to/obsidian-gtd-cli
python tools/process_item.py --file GTD/Dashboard.md --line 42
```

## IMPORTANT: User Confirmation Required

**CRITICAL:** When using this skill with Claude Code or AI assistance:
- **NEVER** make changes to tasks without explicit user confirmation
- **ALWAYS** present options and recommendations first
- **WAIT** for user approval before executing any add_context.py, process_item.py, or other modification commands
- Use `--dry-run` flag to preview changes before asking for confirmation

AI assistants should:
1. Find and display inbox items
2. Analyze and recommend actions based on GTD principles
3. **Ask user:** "Would you like me to apply these changes?"
4. **Wait for confirmation** (yes/no)
5. Only then execute the actual commands

## Workflow

### 1. Find Inbox Items

The "To Process" query finds tasks that need clarification:
- No context tags (@pc, @work, @home, etc.)
- Not scheduled or overdue
- Not time blocks
- Not in excluded folders (Checklists, Templates, Recurring)
- Not blocked or done

```bash
# Find all inbox items
python tools/find_inbox.py

# Show details (file paths, line numbers)
python tools/find_inbox.py --show-details

# Limit results
python tools/find_inbox.py --limit 10

# Export to file for batch processing
python tools/find_inbox.py --export inbox.txt
```

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

```bash
# Process specific task
python tools/process_item.py --file GTD/Dashboard.md --line 42
```

## Context Tags

Tasks are organized by context (where/when/with whom can you do it):

- `@pc` - Requires computer
- `@work` - Work context
- `@home` - Home tasks
- `@partner` - Requires partner
- `@out` - Errands/outside
- `@garden` - Garden work
- `@ai` - AI-related tasks
- `@ponderables` - Things to think about
- `@stuck` - Blocked items

**Note:** `@someday` context is deprecated. For "someday/maybe" items, use lowest priority (⏬) instead.

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

- Use `find_inbox.py --limit 5` to process just a few items at a time
- The tool creates backups (.bak files) before modifying tasks
- Cancelled processing leaves tasks unchanged
- Deleted tasks are removed from files (backups preserved)
- For someday/maybe items, add lowest priority (⏬) instead of using @someday context

## Integration with Dashboard

After processing, tasks with context tags will appear in their respective Dashboard.md sections:
- @pc tasks → PC section
- @work tasks → Work section
- @home tasks → Home section
- etc.

Tasks that remain without context tags will continue to appear in "To Process" section.

## Example Session

```
$ python tools/find_inbox.py --limit 3
Found 3 task(s) to process:

GTD/Dashboard.md:
  - Buy groceries
  - Research new framework
  - Fix kitchen sink

$ python tools/process_item.py --file GTD/Dashboard.md --line 15

============================================================
File: GTD/Dashboard.md
Line: 15
Task: Buy groceries
============================================================

1. What is it? (Clarify)
   Briefly describe what this is about (or press enter to skip): Weekly grocery shopping

2. Is it actionable?
   Can you do something about this? (yes/no): yes

3. What's the next action?
   Describe the specific, concrete next action: Buy groceries for the week

4. Can you do it in 2 minutes or less?
   2-minute rule (yes/no): no

5. Is this a project (requires multiple steps)?
   Project? (yes/no): no

6. Should you delegate or defer this?
   1. Defer (schedule for later)
   2. Delegate (assign to someone)
   3. Do ASAP (no specific date)
   Choice: 1

Available contexts:
  1. @pc
  2. @work
  3. @home
  4. @partner
  5. @out
  6. @garden
  7. @ai
  8. @ponderables
  9. @stuck

Select context (number or name): 5

When should you do this?
  Options:
    - today
    - tomorrow
    - +N (days from now, e.g., +3)
    - YYYY-MM-DD (specific date)
    - <enter> to skip

Scheduled date: tomorrow

✓ Task processed and updated in GTD/Dashboard.md:15
   Context: @out
   Scheduled: 2026-01-03
```

## Related Tools

- `add_context.py` - Batch add context tags to multiple tasks
- `create_project.py` - Create project files for multi-step outcomes
- `weekly_review.py` - Review all contexts and projects
