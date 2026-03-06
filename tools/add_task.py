#!/usr/bin/env python3
"""
Add a new task to a file in the Obsidian vault via the official Obsidian CLI.

Usage:
    python tools/add_task.py --file Daily/2026-02-15.md --task "Buy groceries @out"
    python tools/add_task.py --file Daily/2026-02-15.md --task "Read article" --context "@read"
    python tools/add_task.py --today --task "Quick errand" --context "@out"
    python tools/add_task.py --file GTD/Dashboard.md --task "New idea" --heading "Notes"
"""

import argparse
import re
from datetime import date

from gtd_common import (
    load_config,
    add_metadata_to_task,
    format_task_line,
    parse_date_string,
    get_vault_path,
)
import obsidian_cli as obs


def find_heading_line(lines, heading):
    """
    Find the line index after a given heading where tasks should be inserted.

    Returns the index of the last content line in the heading's section.
    """
    heading_pattern = re.compile(r'^#{1,6}\s+' + re.escape(heading) + r'\s*$', re.IGNORECASE)
    next_heading_pattern = re.compile(r'^#{1,6}\s+')

    heading_idx = None
    for i, line in enumerate(lines):
        if heading_pattern.match(line.strip()):
            heading_idx = i
            break

    if heading_idx is None:
        return None

    insert_idx = heading_idx + 1
    for i in range(heading_idx + 1, len(lines)):
        if next_heading_pattern.match(lines[i].strip()):
            insert_idx = i
            while insert_idx > heading_idx + 1 and lines[insert_idx - 1].strip() == '':
                insert_idx -= 1
            return insert_idx
        insert_idx = i + 1

    while insert_idx > heading_idx + 1 and lines[insert_idx - 1].strip() == '':
        insert_idx -= 1
    return insert_idx


def add_task(file_rel, task_text, *, context=None, scheduled_date=None,
             due_date=None, priority=None, heading=None, is_daily=False,
             auto_confirm=False):
    """
    Add a new task to a file.

    Uses Obsidian CLI for simple appends.
    Falls back to direct I/O only when inserting under a heading.
    """
    # Build the full task description with metadata
    final_description = add_metadata_to_task(
        task_text,
        context=context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=priority,
    )
    task_line = format_task_line(final_description)

    print(f"\nFile:  {file_rel}")
    print(f"Task:  {task_line}")
    if heading:
        print(f"Under: ## {heading}")

    if not auto_confirm:
        response = input("\nAdd this task? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("Cancelled.")
            return False

    # --- Heading insertion: requires line-level I/O ---
    if heading:
        vault_path = get_vault_path()
        file_path = vault_path / file_rel

        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text('', encoding='utf-8')
            print(f"  Created {file_rel}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        insert_idx = find_heading_line(lines, heading)
        if insert_idx is None:
            print(f"Error: Heading '## {heading}' not found in {file_rel}")
            return False

        if insert_idx > 0 and lines and not lines[insert_idx - 1].endswith('\n'):
            lines[insert_idx - 1] += '\n'
        lines.insert(insert_idx, task_line + '\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"\n✓ Task added to {file_rel} under ## {heading}")
        return True

    # --- Simple append via CLI ---
    if is_daily:
        obs.daily_append(task_line)
    else:
        obs.append_to_file(task_line, path=file_rel)

    print(f"\n✓ Task added to {file_rel}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Add a new task to an Obsidian vault file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/add_task.py --file Daily/2026-02-15.md --task "Buy groceries" --context "@out"
  python tools/add_task.py --today --task "Quick errand" --context "@quick"
  python tools/add_task.py --file GTD/Dashboard.md --task "New idea" --heading "Notes"
  python tools/add_task.py --today --task "Call dentist" --context "@quick" --scheduled tomorrow
  python tools/add_task.py --today --task "Someday read this" --priority "⏬"

Date formats: today, tomorrow, +N (days), YYYY-MM-DD
Priority symbols: ⏫ highest, 🔼 high, 🔽 low, ⏬ lowest
        """
    )

    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--file", "-f", metavar="PATH",
                        help="File to add task to (relative to vault)")
    target.add_argument("--today", "-t", action="store_true",
                        help="Add to today's daily note")

    parser.add_argument("--task", required=True, metavar="TEXT",
                        help="Task description")
    parser.add_argument("--context", "-c", metavar="TAG",
                        help="Context tag to add (e.g., @pc, @work)")
    parser.add_argument("--scheduled", "-s", metavar="DATE",
                        help="Scheduled date")
    parser.add_argument("--due", metavar="DATE",
                        help="Due date")
    parser.add_argument("--priority", "-p", metavar="SYMBOL",
                        help="Priority symbol (⏫, 🔼, 🔽, ⏬)")
    parser.add_argument("--heading", metavar="TEXT",
                        help="Insert under this heading")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting")

    args = parser.parse_args()

    scheduled_date = parse_date_string(args.scheduled) if args.scheduled else None
    due_date = parse_date_string(args.due) if args.due else None

    valid_priorities = ['⏫', '🔼', '🔽', '⏬']
    if args.priority and args.priority not in valid_priorities:
        print(f"Error: Invalid priority '{args.priority}'. Valid: {', '.join(valid_priorities)}")
        return

    if args.today:
        file_rel = obs.daily_path()
    else:
        file_rel = args.file

    add_task(
        file_rel,
        args.task,
        context=args.context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=args.priority,
        heading=args.heading,
        is_daily=args.today,
        auto_confirm=args.yes,
    )


if __name__ == "__main__":
    main()
