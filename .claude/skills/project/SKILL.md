---
name: project
description: Manage GTD projects—promote multi-step outcomes, create/update project notes, and ensure each project has current next actions and closure steps.
---

# GTD Project Skill

Guide multi-step outcomes through the full GTD project lifecycle inside the Obsidian vault (`../Obsidian`).

## Quick Start

```bash
# Create a new project note and auto-link it in Projects List
python tools/create_project.py "Website Redesign" --context "@pc-deep" --yes

# Move an existing task into the project note while preserving metadata
python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest "GTD/Projects/Website Redesign.md"

# Surface projects that lack a next action
python tools/weekly_review.py --stale-projects
```

## Workflow

### 1. Decide if it’s a Project
- Use Clarify outputs, dashboard scans, or user context to spot items that require more than one concrete step, will span multiple sessions, or have dependencies.
- Confirm the desired outcome, deadlines, and any constraints before promoting. Reference `project/references/project-lifecycle.md` for criteria.

### 2. Create or Locate the Project Note
1. Run `tools/create_project.py "Name"` (optionally include `--context TAG` and `--yes` for non-interactive runs). The script writes to `../Obsidian/GTD/Projects/Name.md` and updates `Projects List.md`.
2. If the file already exists, open it directly (usually via Obsidian) and verify the metadata block (`**Created:**`, `**Status:**`).
3. Always tell the user what edits you plan to make before changing vault files; wait for confirmation if anything is destructive or irreversible.

### 3. Populate the Note
- Fill in **Purpose / Outcome** with a single success statement.
- Brainstorm all known steps, but only leave the true “next actions” unchecked in **Next Actions**. Tag each line with a GTD context (see Organize skill for canonical tags) and schedule if relevant.
- When promoting an inbox task into a project, generate 2–3 plausible next actions seeded from that task and add them to **Next Actions** with contexts.
- For knowledge-work steps (drafting, summarizing, research, code scaffolding), propose an LLM-agent next action (e.g., “Use LLM agent to draft outline/summary/email/code scaffold”) and tag appropriately.
- Assume steps must happen in order unless the user says they can be parallel. Add Task Dependencies so actions follow each other: assign each task a unique `🆔` and add `⛔ <id>` to each dependent task. Chain them so only the first is unblocked; multiple dependencies are comma-separated with no spaces (`,`) in the `⛔` list.
- Capture references, waiting-fors, and notes in their dedicated sections. Use wikilinks (`[[Project Name]]`) from related tasks or notes to keep traceability.
- For manual setup or extra guidance, follow the Setup Checklist in `project/references/project-lifecycle.md`.

### 4. Link Tasks and Context Lists
- Convert any standalone task representing the project into either:
  - A reference link pointing to the project note (`Do X → [[Project Name]]`), or
  - Subtasks filed under the project note or context files via `tools/move_task.py`.
- Ensure each active project has at least one actionable task living in a context list so it appears on the Dashboard. Use `tools/add_context.py` to retag/move items in bulk.
- For delegated steps, add `@waiting` (or relevant tag) plus the person’s name and record it inside the project note.

### 5. Maintain and Review
- During weekly reviews run `tools/weekly_review.py --stale-projects` and fix anything lacking a next action.
- Update the `**Status:**` field whenever the project changes state (Active, Waiting, On Hold, Completed). Log wins or blockers in **Notes** so nothing lives only in memory.
- When the outcome is achieved, follow the Closing Checklist in the reference file: mark status completed with a date, archive/move the note if desired, and clean up dangling tasks.

## References & Supporting Material
- `project/references/project-lifecycle.md` – Checklists for deciding, setting up, maintaining, and closing projects.
- `tools/create_project.py` – Primary automation for scaffolding project files and updating `Projects List.md`.
- `tools/move_task.py`, `tools/add_context.py` – Reuse from Organize skill to keep next actions filed correctly.
- `tools/weekly_review.py --stale-projects` – Fast way to surface projects without next actions.

## Coordination With Other Skills
- Use **Clarify** to decide when an inbox item crosses the “multiple steps” threshold and confirm next actions before creating the project.
- Use **Organize** to place resulting tasks into the right context files and to batch-add context tags or schedule dates.
- Use **Review** weekly to catch stale projects, unblock waiting items, and close completed work.

Following this workflow keeps the Projects list trustworthy, ensures each project exposes a visible next action, and prevents orphaned multi-step work from hiding in single tasks.
