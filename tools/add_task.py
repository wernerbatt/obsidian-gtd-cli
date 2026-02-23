#!/usr/bin/env python3
"""
Add a new task to a file in the Obsidian vault.

Appends a task line to the end of a file (or under a specific heading).
Supports the same metadata options as edit_task.py.

Usage:
    python tools/add_task.py --file Daily/2026-02-15.md --task "Buy groceries @out"
    python tools/add_task.py --file Daily/2026-02-15.md --task "Read article" --context "@read"
    python tools/add_task.py --file Daily/2026-02-15.md --task "Call dentist" --context "@quick" --due tomorrow
    python tools/add_task.py --today --task "Quick errand" --context "@out"
    python tools/add_task.py --file GTD/Dashboard.md --task "New idea" --heading "Notes"
"""

import argparse
import re
from pathlib import Path
from datetime import datetime, date, timedelta
from gtd_common import (
    get_vault_path,
    load_config,
    add_metadata_to_task,
    format_task_line,
)


def parse_date_string(date_str):
    """Parse date string into YYYY-MM-DD format."""
    date_str = date_str.strip().lower()
    today = date.today()

    if date_str == 'today':
        return str(today)
    elif date_str == 'tomorrow':
        return str(today + timedelta(days=1))
    elif date_str.startswith('+'):
        try:
            days = int(date_str[1:])
            return str(today + timedelta(days=days))
        except ValueError:
            raise ValueError(f"Invalid format: {date_str}. Use +N for days from now")
    else:
        try:
            parsed = datetime.strptime(date_str, '%Y-%m-%d').date()
            return str(parsed)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def find_heading_line(lines, heading):
    """
    Find the line index after a given heading where tasks should be inserted.

    Returns the index of the last non-empty line in the heading's section,
    so the new task is appended at the end of that section.

    Args:
        lines (list[str]): File lines
        heading (str): Heading text (without ## prefix)

    Returns:
        int or None: Line index to insert after, or None if heading not found
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

    # Find the end of this section (next heading or end of file)
    insert_idx = heading_idx + 1
    for i in range(heading_idx + 1, len(lines)):
        if next_heading_pattern.match(lines[i].strip()):
            # Insert before the next heading; back up over blank lines
            insert_idx = i
            while insert_idx > heading_idx + 1 and lines[insert_idx - 1].strip() == '':
                insert_idx -= 1
            return insert_idx
        insert_idx = i + 1

    # Reached end of file; back up over trailing blank lines
    while insert_idx > heading_idx + 1 and lines[insert_idx - 1].strip() == '':
        insert_idx -= 1
    return insert_idx


def add_task(file_path, task_text, context=None, scheduled_date=None,
             due_date=None, priority=None, heading=None, auto_confirm=False):
    """
    Add a new task to a file.

    Args:
        file_path (Path): Path to target file
        task_text (str): Task description
        context (str, optional): Context tag to add
        scheduled_date (str, optional): Scheduled date (YYYY-MM-DD)
        due_date (str, optional): Due date (YYYY-MM-DD)
        priority (str, optional): Priority symbol
        heading (str, optional): Insert under this heading
        auto_confirm (bool): Skip confirmation prompt

    Returns:
        bool: True if successful
    """
    vault_path = get_vault_path()

    # Build the full task description with metadata
    final_description = add_metadata_to_task(
        task_text,
        context=context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=priority,
    )
    task_line = format_task_line(final_description)

    # Show what we're about to do
    rel_path = file_path.relative_to(vault_path)
    print(f"\nFile:  {rel_path}")
    print(f"Task:  {task_line}")
    if heading:
        print(f"Under: ## {heading}")

    if not auto_confirm:
        response = input("\nAdd this task? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return False

    # Ensure file exists; create with minimal frontmatter if not
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text('', encoding='utf-8')
        print(f"  Created {rel_path}")

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    # Determine where to insert
    if heading:
        insert_idx = find_heading_line(lines, heading)
        if insert_idx is None:
            print(f"Error: Heading '## {heading}' not found in {rel_path}")
            return False
    else:
        # Append at end; strip trailing blank lines then add one
        insert_idx = len(lines)
        while insert_idx > 0 and lines[insert_idx - 1].strip() == '':
            insert_idx -= 1
        insert_idx = len(lines)  # actually append at very end

    # Insert the task line
    new_line = task_line + '\n'
    # Ensure there's a newline before if the previous line doesn't end with one
    if insert_idx > 0 and lines and not lines[insert_idx - 1].endswith('\n'):
        lines[insert_idx - 1] += '\n'

    lines.insert(insert_idx, new_line)

    # Write back
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\n✓ Task added to {rel_path}" + (f" under ## {heading}" if heading else ""))
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Add a new task to an Obsidian vault file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add task to a file
  python tools/add_task.py --file Daily/2026-02-15.md --task "Buy groceries" --context "@out"

  # Add to today's daily note
  python tools/add_task.py --today --task "Quick errand" --context "@quick"

  # Add under a specific heading
  python tools/add_task.py --file GTD/Dashboard.md --task "New idea" --heading "Notes"

  # Add with scheduling
  python tools/add_task.py --today --task "Call dentist" --context "@quick" --scheduled tomorrow

  # Add with priority
  python tools/add_task.py --today --task "Someday read this" --priority "⏬"

Date formats:
  - today, tomorrow, +N (days), YYYY-MM-DD

Priority symbols:
  - ⏫ highest, 🔼 high, 🔽 low, ⏬ lowest
        """
    )

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--file", "-f", metavar="PATH",
                              help="File to add task to (relative to vault)")
    target_group.add_argument("--today", "-t", action="store_true",
                              help="Add to today's daily note")

    parser.add_argument("--task", required=True, metavar="TEXT",
                        help="Task description")
    parser.add_argument("--context", "-c", metavar="TAG",
                        help="Context tag to add (e.g., @pc, @work)")
    parser.add_argument("--scheduled", "-s", metavar="DATE",
                        help="Scheduled date (today, tomorrow, +N, YYYY-MM-DD)")
    parser.add_argument("--due", metavar="DATE",
                        help="Due date (today, tomorrow, +N, YYYY-MM-DD)")
    parser.add_argument("--priority", "-p", metavar="SYMBOL",
                        help="Priority symbol (⏫, 🔼, 🔽, ⏬)")
    parser.add_argument("--heading", metavar="TEXT",
                        help="Insert under this heading (e.g., 'Notes')")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting (for agentic use)")

    args = parser.parse_args()

    # Parse dates
    scheduled_date = None
    due_date = None

    if args.scheduled:
        try:
            scheduled_date = parse_date_string(args.scheduled)
        except ValueError as e:
            print(f"Error: {e}")
            return

    if args.due:
        try:
            due_date = parse_date_string(args.due)
        except ValueError as e:
            print(f"Error: {e}")
            return

    # Validate priority
    valid_priorities = ['⏫', '🔼', '🔽', '⏬']
    if args.priority and args.priority not in valid_priorities:
        print(f"Error: Invalid priority symbol '{args.priority}'")
        print(f"Valid priorities: {', '.join(valid_priorities)}")
        return

    # Resolve target file
    vault_path = get_vault_path()

    if args.today:
        today_str = date.today().strftime('%Y-%m-%d')
        file_path = vault_path / 'Daily' / f'{today_str}.md'
    else:
        file_path = vault_path / args.file

    if not file_path.exists() and not args.today:
        print(f"Error: File not found: {args.file}")
        return

    # Add the task
    add_task(
        file_path,
        args.task,
        context=args.context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=args.priority,
        heading=args.heading,
        auto_confirm=args.yes,
    )


if __name__ == "__main__":
    main()
