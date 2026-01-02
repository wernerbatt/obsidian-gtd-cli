# Obsidian GTD CLI

A Python command-line toolkit for implementing Getting Things Done (GTD) workflows in Obsidian.

## Features

- **Clarify**: Process inbox items with interactive GTD workflow
- **Organize**: Add context tags, create projects, organize tasks by context
- **Review**: Generate weekly review reports and metrics
- **Claude Code Skills**: Integrated skills for AI-assisted GTD workflows

## What is GTD?

Getting Things Done (GTD) is a personal productivity methodology by David Allen. The core workflow:

1. **Capture** - Collect everything that has your attention
2. **Clarify** - Process what it means and what to do about it
3. **Organize** - Put it where it belongs (contexts, projects, calendar)
4. **Review** - Keep your system current and complete
5. **Engage** - Do the work with confidence

This toolkit focuses on the Clarify, Organize, and Review steps.

## Installation

### Prerequisites

- Python 3.7 or higher
- Obsidian vault with GTD folder structure
- Git (for pushing to GitHub)

### Setup

1. Clone this repository:
```bash
cd /mnt/c/Users/werne
git clone https://github.com/YOUR_USERNAME/obsidian-gtd-cli.git
cd obsidian-gtd-cli
```

2. Create and activate a virtual environment (recommended):
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your vault path in `config.yaml`:
```yaml
vault_path: ../Obsidian
```

## Quick Start

### Process Inbox Items

Find tasks that need processing:
```bash
python tools/find_inbox.py
```

Process items interactively with GTD questions:
```bash
python tools/process_item.py --file GTD/Dashboard.md --line 42
```

### Organize Tasks

Add context tags to multiple tasks:
```bash
python tools/add_context.py --context "@pc" --search "research"
```

Create a new project:
```bash
python tools/create_project.py "Website Redesign"
```

Move a task between files:
```bash
python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md
```

### Weekly Review

Generate review report:
```bash
python tools/weekly_review.py
```

Save review to file:
```bash
python tools/weekly_review.py --output "Weekly Review 2026-01-02.md"
```

## Tools Reference

### find_inbox.py

Find tasks matching "To Process" criteria (no context tags, unscheduled/overdue).

```bash
python tools/find_inbox.py                    # Find all inbox items
python tools/find_inbox.py --show-details     # Show file paths and line numbers
python tools/find_inbox.py --limit 10         # Limit to 10 tasks
python tools/find_inbox.py --export inbox.txt # Export to file
```

### process_item.py

Interactive GTD processing with guided questions.

```bash
python tools/process_item.py --file GTD/Dashboard.md --line 42
```

**GTD Questions:**
1. What is it? (Clarify)
2. Is it actionable?
3. What's the next action?
4. Can it be done in 2 minutes?
5. Is it a project?
6. Defer, delegate, or do?

### add_context.py

Batch add context tags and scheduled dates to tasks.

```bash
# Add context tag
python tools/add_context.py --context "@pc" --search "research"

# Add context to specific file
python tools/add_context.py --context "@work" --file GTD/Dashboard.md

# Add context and schedule
python tools/add_context.py --context "@home" --search "clean" --scheduled +7

# Preview changes (dry run)
python tools/add_context.py --context "@pc" --search "code" --dry-run
```

**Scheduled date formats:**
- `today` - Today's date
- `tomorrow` - Tomorrow's date
- `+N` - N days from now (e.g., `+3`)
- `YYYY-MM-DD` - Specific date

### create_project.py

Create project files for multi-step outcomes.

```bash
# Create simple project
python tools/create_project.py "Website Redesign"

# Create with default context
python tools/create_project.py "Home Renovation" --context "@home"

# Use custom template
python tools/create_project.py "Research" --template my_template.md
```

**Project structure:**
- Created in `GTD/Projects/` folder
- Auto-added to `Projects List.md`
- Includes: Purpose, Next Actions, Notes, Resources

### move_task.py

Move tasks between files while preserving metadata.

```bash
# Move to context file
python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md

# Move to project file
python tools/move_task.py --source GTD/PC.md --line 10 --dest "GTD/Projects/Website.md"
```

**Features:**
- Preserves all metadata (dates, tags, etc.)
- Moves subtasks along with parent
- Creates backups before changes
- Confirms before moving

### weekly_review.py

Generate comprehensive weekly review reports.

```bash
# Display to terminal
python tools/weekly_review.py

# Save to file
python tools/weekly_review.py --output "Weekly Review 2026-01-02.md"

# Show stale projects only
python tools/weekly_review.py --stale-projects

# Save and open in Obsidian
python tools/weekly_review.py --output review.md --open
```

**Report includes:**
- Inbox count
- Active tasks by context
- Overdue tasks
- Projects without next actions
- Completed tasks (last 7 days)

## Configuration

Edit `config.yaml` to customize:

```yaml
vault_path: ../Obsidian

gtd:
  base_folder: GTD
  dashboard: GTD/Dashboard.md

  contexts:
    pc: GTD/PC.md
    work: GTD/Work.md
    home: GTD/Home.md
    sharne: GTD/Sharné.md
    errands: GTD/Errands.md
    garden: GTD/Garden.md
    someday: GTD/Someday Maybe.md

  projects_folder: GTD/Projects
  projects_list: GTD/Projects List.md

  checklists_folder: GTD/Checklists
  weekly_review: GTD/Checklists/Weekly Review Checklist.md

  recurring: GTD/Recurring.md

settings:
  create_backups: true
  default_context: "@pc"
  available_contexts:
    - "@pc"
    - "@work"
    - "@home"
    - "@sharne"
    - "@out"
    - "@garden"
    - "@ai"
    - "@someday"
    - "@ponderables"
    - "@stuck"
```

## Task Format

Tasks use Obsidian Tasks plugin emoji metadata:

- `📅 YYYY-MM-DD` - Due date
- `⏳ YYYY-MM-DD` - Scheduled date
- `🛫 YYYY-MM-DD` - Start date
- `✅ YYYY-MM-DD` - Done date
- `🔁` - Recurring
- `⛔` - Blocked

Example task:
```markdown
- [ ] Research new framework @pc ⏳ 2026-01-05 📅 2026-01-10
```

## Context Tags

Tasks are organized by context (where/when/with whom):

- `@pc` - Requires computer
- `@work` - Work context
- `@home` - Home tasks
- `@sharne` - Requires Sharné
- `@out` - Errands
- `@garden` - Garden work
- `@ai` - AI-related
- `@someday` - Someday/maybe
- `@ponderables` - To think about
- `@stuck` - Blocked items

## Claude Code Skills

This toolkit includes Claude Code skills in `.claude/skills/`:

- **clarify** - Process inbox items with GTD workflow
- **organize** - Organize tasks by contexts and projects
- **review** - Conduct weekly review

Skills enable AI-assisted GTD workflows when using Claude Code.

## GTD Workflow Example

Here's a complete GTD workflow using the toolkit:

### 1. Capture (Throughout the day)

Add tasks to your Obsidian vault as you think of them. Don't worry about context tags yet.

### 2. Clarify (Daily or when inbox is full)

```bash
# Find items to process
python tools/find_inbox.py

# Process each item
python tools/process_item.py --file GTD/Dashboard.md --line 42
```

For each item, answer the GTD questions and assign context tags.

### 3. Organize (After processing)

```bash
# Batch organize similar tasks
python tools/add_context.py --context "@pc" --search "code"

# Create projects for complex outcomes
python tools/create_project.py "Website Redesign" --context "@pc"

# Move tasks to appropriate files
python tools/move_task.py --source GTD/Dashboard.md --line 15 --dest "GTD/Projects/Website Redesign.md"
```

### 4. Review (Weekly)

```bash
# Generate weekly review
python tools/weekly_review.py --output "Weekly Review 2026-01-02.md"

# Process inbox to zero
python tools/find_inbox.py
python tools/process_item.py --file GTD/Dashboard.md --line 42

# Address overdue tasks
python tools/add_context.py --search "overdue" --scheduled tomorrow

# Fix stale projects
python tools/create_project.py "New Project" --context "@pc"
```

### 5. Engage (Throughout the day)

Use your Obsidian Dashboard to see tasks by context and work from your lists with confidence.

## Best Practices

1. **Process inbox to zero regularly** - Daily or at least weekly
2. **Use specific, actionable language** - "Call dentist for appointment" not "dentist"
3. **One action per task** - If multiple steps needed, it's a project
4. **Always add context tags** - Every actionable task gets a context
5. **Schedule deferred items** - If not now, when?
6. **Weekly review is sacred** - Non-negotiable time to maintain your system
7. **Trust your system** - If it's not in GTD, it doesn't exist

## Backup Strategy

All modification tools create `.bak` backup files by default:
- Backups created before any file modification
- Original formatting preserved
- Use `--no-backup` flag to skip (not recommended)

To restore from backup:
```bash
# Linux/Mac
mv file.md.bak file.md

# Windows
move file.md.bak file.md
```

## Troubleshooting

### Virtual environment issues

If you get import errors, ensure virtual environment is activated:
```bash
# Check if activated (should show venv in prompt)
which python   # Linux/Mac
where python   # Windows

# Activate if needed
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### Config path issues

If tools can't find your vault:
- Check `vault_path` in `config.yaml`
- Use absolute path if relative path doesn't work
- Ensure path uses forward slashes or proper OS separators

### Task parsing issues

If tasks aren't recognized:
- Ensure tasks follow format: `- [ ] Description`
- Check for proper spacing after checkbox
- Verify emoji metadata format (⏳ YYYY-MM-DD)

## Development

### Project Structure

```
obsidian-gtd-cli/
├── .claude/skills/       # Claude Code skills
├── tools/                # Python CLI scripts
│   ├── gtd_common.py    # Shared utilities
│   ├── find_inbox.py    # Find inbox items
│   ├── process_item.py  # Interactive processing
│   ├── add_context.py   # Batch context tags
│   ├── create_project.py # Project creation
│   ├── move_task.py     # Move tasks
│   └── weekly_review.py # Review reports
├── config.yaml          # Configuration
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

### Adding Custom Tools

All tools share common utilities in `gtd_common.py`:
- `load_config()` - Load vault configuration
- `parse_task_line()` - Parse Obsidian task syntax
- `create_backup()` - Backup files before modification
- `task_matches_to_process_criteria()` - GTD inbox filter

See existing tools for examples.

## Contributing

Contributions welcome! Please:
1. Follow existing code patterns
2. Test with actual Obsidian vault
3. Update README for new features
4. Create backup-safe tools

## License

MIT License - see LICENSE file for details

## Credits

Based on the Getting Things Done (GTD) methodology by David Allen.

Inspired by the Obsidian Tasks plugin and existing obsidian-cli patterns.

## Resources

- [Getting Things Done Book](https://gettingthingsdone.com/)
- [Obsidian Tasks Plugin](https://github.com/obsidian-tasks-group/obsidian-tasks)
- [GTD Methodology Overview](https://gettingthingsdone.com/what-is-gtd/)

## Support

For issues or questions:
- GitHub Issues: [Report a bug or request a feature]
- Check existing documentation in `.claude/skills/`
- Review tool help: `python tools/TOOL_NAME.py --help`

---

**Generated by Claude Code** | Last updated: 2026-01-02
