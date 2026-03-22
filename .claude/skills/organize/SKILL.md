---
name: organize
description: Organize tasks by contexts and projects
---

# GTD Organize Skill

Help organize tasks into contexts and projects for effective action.

## Vault Operations

**Use the `/obsidian` skill for all vault reads and writes.** Load it before running any commands:
→ `.claude/skills/obsidian/SKILL.md`

Quick reference:
- **Add context tags:** Use edit-by-match to rewrite task line with context tag
- **Create a project:** Use `create path=...` to scaffold project file
- **Move a task:** Use eval move pattern (delete from source + append to dest)
- **Search tasks by context:** Use Dataview eval tag query

## Context Organization

Tasks are organized by context - the location, tool, or person needed to complete them.

### Available Contexts

**Computer Tasks (by focus level):**
- **@deep** - Deep focus work (2+ hours, requires concentration, no interruptions)
  - Examples: Programming, writing, complex analysis, learning new skills
- **@quick** - Quick wins (<15 minutes, low effort, can do anytime)
  - Examples: Reply to email, update task, quick search, file something
- **@batch** - Similar tasks to batch together (saves mental switching)
  - Examples: Process emails, update multiple spreadsheets, review documents
- **@pc** - Legacy context (being phased out - use specific contexts above)

**Other Contexts:**
- **@work** - Work environment/time
- **@home** - Home environment
- **@partner** - Requires partner/collaborator
- **@out** - Errands/outside home
- **@garden** - Garden work
- **@ai** - AI-related tasks
- **@ponderables** - Things to think about
- **@stuck** - Blocked items

**Note:** `@someday` context is deprecated. For "someday/maybe" items, use lowest priority (⏬) instead.

Each context has a corresponding file in the GTD folder (e.g., GTD/PC - Deep Focus.md, GTD/Work.md).

## Batch Context Tagging

To add context tags to multiple tasks matching a search term, use the `/obsidian` skill's Dataview query to find matching tasks, then edit each with the edit-by-match eval pattern. Present changes to the user before executing.

## Creating Projects

Use the `/obsidian` skill's `create` command to scaffold project files in `GTD/Projects/`:

```markdown
# Project Name

**Created:** YYYY-MM-DD
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

After creating the file, append a link to `GTD/Projects List.md`.

## Moving Tasks

Use the `/obsidian` skill's move pattern (eval: delete from source + append to dest). This preserves all task metadata (emoji dates, context tags, etc.).

## Workflow Examples

### Example 1: Organize Research Tasks

Find research tasks via Dataview eval tag query, then batch-edit to add @deep and schedule:
1. Query tasks containing "research" without a context tag
2. Present list to user for confirmation
3. Edit each via edit-by-match pattern, adding `@deep ⏳ YYYY-MM-DD`

### Example 2: Create Project for Multi-Step Outcome

1. Create project file via `create path="GTD/Projects/Website Redesign.md" content="..."`
2. Append link to `GTD/Projects List.md`
3. Move related tasks via eval move pattern (sequentially if same source file)

### Example 3: Batch Schedule Weekend Tasks

1. Query tasks by context tag via Dataview eval
2. Present list and get confirmation
3. Edit each to add `⏳ YYYY-MM-DD` for the target date

## Best Practices

1. **One context per task** - Choose the primary context needed
2. **Use projects for complex outcomes** - If >1 step, it's a project
3. **Review context files regularly** - Keep them manageable (10-20 tasks each)
4. **Move completed tasks** - Archive or delete completed tasks
5. **Use --dry-run first** - Preview batch changes before applying
6. **Commit to git regularly** - Track all changes with version control

## Integration with Dashboard

After organizing tasks:
- Tasks with @deep appear in the PC - Deep Focus section of Dashboard.md
- Tasks with @quick appear in the PC - Quick Wins section
- Tasks with @batch appear in the PC - Batch Tasks section
- Tasks with @work appear in the Work section
- Tasks with @home appear in the Home section
- etc.

The Dashboard.md queries automatically filter tasks by context tag, so organized tasks will show up in their respective sections.

## Tips

- Always present changes to the user before executing batch edits
- Project names can include spaces and special characters
- All file modifications are tracked via git - commit regularly to preserve history

## Related Skills

- `/obsidian` — All vault read/write operations
- `/clarify` — Processing inbox items
- `/project` — Full project lifecycle
- `/review` — Weekly review workflow
