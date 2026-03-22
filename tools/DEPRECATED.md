# ⚠️ DEPRECATED

The Python tools in this directory are deprecated as of 2026-03-21.

All vault operations now go through the Obsidian CLI directly, using the
`/obsidian` skill (`.claude/skills/obsidian/SKILL.md`).

## What replaced what

| Python tool | Replacement |
|---|---|
| `find_tasks.py` | Obsidian CLI `eval` + Dataview API queries |
| `add_task.py` | CLI `daily:path` + `append` / `eval` insert-under-heading |
| `edit_task.py` | CLI `eval` + `app.vault.process()` edit-by-match |
| `move_task.py` | CLI `eval` + `app.vault.process()` (delete + append) |
| `mark_done.py` | CLI `task path=... line=N done` (native) |
| `delete_task.py` | CLI `eval` + `app.vault.process()` splice |
| `add_context.py` | Dataview query + batch edit-by-match |
| `create_project.py` | CLI `create path=... content=...` |
| `weekly_review.py` | Combination of Dataview eval queries |
| `process_item.py` | Agent-driven workflow (never used programmatically) |

## Why

- The Obsidian CLI (1.12+) now supports `eval`, giving direct access to
  the Dataview plugin API and `app.vault.process()` for atomic file edits.
- All reads AND writes go through Obsidian's own APIs — no more direct
  file I/O, no race conditions, vault always stays in sync.
- Eliminates an entire Python codebase to maintain.

## These files are kept for reference

The Python tools are not deleted yet in case of rollback. They should not
be used for new work. All skills have been updated to reference the
`/obsidian` skill instead.
