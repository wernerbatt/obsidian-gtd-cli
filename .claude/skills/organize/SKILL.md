---
name: organize
description: Organize tasks by contexts and projects
---

# GTD Organize Skill

Help organize tasks into contexts and projects for effective action.

## Quick Start

Add context tags to tasks:
```bash
cd /path/to/obsidian-gtd-cli
python tools/add_context.py --context "@pc-deep" --search "research"
```

Create a new project:
```bash
cd /path/to/obsidian-gtd-cli
python tools/create_project.py "Website Redesign"
```

Move a task between files:
```bash
cd /path/to/obsidian-gtd-cli
python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md
```

## Context Organization

Tasks are organized by context - the location, tool, or person needed to complete them.

### Available Contexts

**Computer Tasks (by focus level):**
- **@pc-deep** - Deep focus work (2+ hours, requires concentration, no interruptions)
  - Examples: Programming, writing, complex analysis, learning new skills
- **@pc-quick** - Quick wins (<15 minutes, low effort, can do anytime)
  - Examples: Reply to email, update task, quick search, file something
- **@pc-batch** - Similar tasks to batch together (saves mental switching)
  - Examples: Process emails, update multiple spreadsheets, review documents
- **@pc** - Legacy context (being phased out - use specific contexts above)

**Other Contexts:**
- **@work** - Work environment/time
- **@home** - Home environment
- **@partner** - Requires partner
- **@out** - Errands/outside home
- **@garden** - Garden work
- **@ai** - AI-related tasks
- **@ponderables** - Things to think about
- **@stuck** - Blocked items

**Note:** `@someday` context is deprecated. For "someday/maybe" items, use lowest priority (⏬) instead.

Each context has a corresponding file in the GTD folder (e.g., GTD/PC - Deep Focus.md, GTD/Work.md).

## Tool: add_context.py

Batch add context tags and scheduled dates to tasks based on search criteria.

### Basic Usage

```bash
# Add @pc-deep to all tasks containing "research"
python tools/add_context.py --context "@pc-deep" --search "research"

# Add @work to all tasks in specific file
python tools/add_context.py --context "@work" --file GTD/Dashboard.md

# Add context and schedule for next week
python tools/add_context.py --context "@home" --search "clean" --scheduled +7

# Preview changes without applying
python tools/add_context.py --context "@pc" --search "code" --dry-run
```

### Scheduled Date Formats

When using `--scheduled`, you can specify:
- `today` - Today's date
- `tomorrow` - Tomorrow's date
- `+N` - N days from now (e.g., `+3` for 3 days, `+7` for one week)
- `YYYY-MM-DD` - Specific date (e.g., `2026-01-15`)

### Options

- `--context TAG` or `-c TAG` - Context tag to add (e.g., @pc-deep, @work)
- `--search TERM` or `-s TERM` - Search term to match in descriptions
- `--file PATH` or `-f PATH` - File to search (relative to vault)
- `--scheduled DATE` - Scheduled date to add
- `--dry-run` or `-n` - Preview changes without applying

## Tool: create_project.py

Create new project files for multi-step outcomes.

A project in GTD is any outcome that requires more than one action step.

### Basic Usage

```bash
# Create a simple project
python tools/create_project.py "Website Redesign"

# Create with default context for next actions
python tools/create_project.py "Home Renovation" --context "@pc-deep"

# Use custom template
python tools/create_project.py "Research AI Tools" --template my_template.md
```

### Project File Structure

Projects are created in `GTD/Projects/` folder with this structure:

```markdown
# Project Name

**Created:** 2026-01-02
**Status:** Active

## Purpose / Outcome

What is the successful outcome for this project?

## Next Actions

- [ ] First next action @context
- [ ]

## Notes

## Resources / Links

## Completed Actions
```

### Options

- `name` (positional) - Project name
- `--context TAG` or `-c TAG` - Default context tag for next actions
- `--template FILE` or `-t FILE` - Custom template file (relative to vault)

### Automatic Updates

The tool automatically:
- Creates the project file in `GTD/Projects/`
- Adds the project to `Projects List.md`
- Provides next steps for completing the project setup

## Tool: move_task.py

Move tasks between files while preserving metadata and subtasks.

### Basic Usage

```bash
# Move task from Dashboard to PC context
python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md

# Move task to project file
python tools/move_task.py --source GTD/PC.md --line 10 --dest GTD/Projects/Website.md
```

### Features

- Preserves all task metadata (emoji dates, context tags, etc.)
- Moves subtasks (indented tasks) along with parent task
- Confirms before making changes

### Options

- `--source FILE` or `-s FILE` - Source file (relative to vault)
- `--line N` or `-l N` - Line number of task (1-indexed)
- `--dest FILE` or `-d FILE` - Destination file (relative to vault)

## Workflow Examples

### Example 1: Organize Research Tasks

You have several research tasks scattered across files and want to organize them:

```bash
# Find all research tasks and add @pc-deep context
python tools/add_context.py --context "@pc-deep" --search "research"

# Schedule them for next week
python tools/add_context.py --search "research @pc-deep" --scheduled +7
```

### Example 2: Create Project for Multi-Step Outcome

You realize "Website Redesign" is a project, not a simple task:

```bash
# Create project file
python tools/create_project.py "Website Redesign" --context "@pc-deep"

# Move related tasks to project file
python tools/move_task.py --source GTD/PC.md --line 15 --dest "GTD/Projects/Website Redesign.md"
python tools/move_task.py --source GTD/PC.md --line 23 --dest "GTD/Projects/Website Redesign.md"
```

### Example 3: Reorganize Context Lists

You want to move completed @home tasks to an archive:

```bash
# Manually identify completed tasks and move them
python tools/move_task.py --source GTD/Home.md --line 42 --dest Archive/2026-01.md
```

### Example 4: Batch Schedule Weekend Tasks

Schedule all @home tasks for the weekend:

```bash
# Schedule for Saturday (5 days from now)
python tools/add_context.py --file GTD/Home.md --scheduled +5

# Preview first with --dry-run
python tools/add_context.py --file GTD/Home.md --scheduled +5 --dry-run
```

## Best Practices

1. **One context per task** - Choose the primary context needed
2. **Use projects for complex outcomes** - If >1 step, it's a project
3. **Review context files regularly** - Keep them manageable (10-20 tasks each)
4. **Move completed tasks** - Archive or delete completed tasks
5. **Use --dry-run first** - Preview batch changes before applying
6. **Commit to git regularly** - Track all changes with version control

## Integration with Dashboard

After organizing tasks:
- Tasks with @pc-deep appear in the PC - Deep Focus section of Dashboard.md
- Tasks with @pc-quick appear in the PC - Quick Wins section
- Tasks with @pc-batch appear in the PC - Batch Tasks section
- Tasks with @work appear in the Work section
- Tasks with @home appear in the Home section
- etc.

The Dashboard.md queries automatically filter tasks by context tag, so organized tasks will show up in their respective sections.

## Tips

- Use `add_context.py --dry-run` to preview changes before applying
- Project names can include spaces and special characters
- The `move_task.py` tool confirms before moving to prevent accidents
- All file modifications are tracked via git - commit regularly to preserve history

## Related Tools

- `find_inbox.py` - Find tasks needing context tags
- `process_item.py` - Interactive processing with context assignment
- `weekly_review.py` - Review all contexts and projects
