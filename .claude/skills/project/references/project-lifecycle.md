# Project Lifecycle Reference

Use this checklist when creating, maintaining, or closing GTD projects in the Obsidian vault (`../Obsidian/GTD`).

## When to Promote a Task to a Project
- Outcome requires more than one concrete next action or spans multiple days/weeks.
- Work depends on inputs from other people or teams (needs @waiting tracking).
- There is meaningful risk if intermediate steps are forgotten (e.g., travel, multi-stage repairs).
- Clarify has surfaced an item that cannot be finished in a single sitting or context.

Before creating a project, confirm the desired outcome statement and any hard due dates or constraints.

## Project Setup Checklist
1. Run `python tools/create_project.py "Project Name" [--context "@deep"]` to scaffold `../Obsidian/GTD/Projects/Project Name.md` and update `Projects List.md`.
2. Immediately edit the new note:
   - Describe the **Purpose / Outcome** in a single success sentence.
   - Fill in constraints, deliverables, and due dates near the top if applicable.
3. Brain-dump all known next actions in the **Next Actions** section and tag each with a context (`@quick`, `@home`, etc.). Leave only the true “next” ones unchecked.
4. Default to ordered steps unless explicitly told they can be parallel. Add Task Dependencies: assign each task a `🆔` and add `⛔ <id>` to the dependent task so the sequence is enforced. For multiple prerequisites, list IDs with commas and no spaces.
5. Move or copy any existing tasks referencing this work into the project note (or into context files while linking back with `[[Project Name]]`). Use `python tools/move_task.py ...` to preserve metadata.
6. Capture supporting material in **Notes** or **Resources / Links** (meeting notes, links, files).
7. If the project depends on someone else, record @waiting items inside the Notes section and optionally in Dashboard contexts for visibility.

## Maintenance Checklist
- During Weekly Review, scan each active project and ensure there is at least one clearly defined next action in the project note and in a context list.
- Update the `**Status:**` line to one of `Active`, `Waiting`, `On Hold`, or `Completed`.
- When a next action is finished, move it to **Completed Actions** (or mark ✅) and promote the next one.
- Record blockers, decisions, or new information in **Notes** rather than leaving it in memory.
- If no progress is possible, re-evaluate whether to place the project On Hold or move to Someday/Maybe (use lowest priority ⏬ tags on related tasks).

## Closing a Project
1. Confirm the desired outcome is achieved or intentionally dropped.
2. Set `**Status:** Completed (YYYY-MM-DD)` and summarize results in Notes.
3. Move any remaining loose tasks to other projects or contexts; archive obsolete material.
4. (Optional) Move the project note to `GTD/Projects/Archive` or prepend `Archive -` to the filename.
5. Remove or annotate the entry in `Projects List.md` so active lists remain trustworthy.
