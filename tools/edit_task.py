#!/usr/bin/env python3
"""
Edit a task's description at a specific file and line number.

This tool allows you to change the description of an existing task while
preserving its checkbox status and position in the file.

Usage:
    python tools/edit_task.py --file GTD/Dashboard.md --line 42 --description "New task description"
    python tools/edit_task.py --file Daily/2025-12-29.md --line 27 --description "Discuss instax 99 with Sharné" --context "@sharne" --due tomorrow
"""

import argparse
from pathlib import Path
from datetime import datetime, date, timedelta
from gtd_common import (
    get_vault_path,
    load_config,
    parse_task_line,
    create_backup,
    add_metadata_to_task
)
import re


def parse_date_string(date_str):
    """
    Parse date string into YYYY-MM-DD format.

    Args:
        date_str (str): Date string (today, tomorrow, +N, YYYY-MM-DD)

    Returns:
        str: Date in YYYY-MM-DD format
    """
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
        # Try parsing as YYYY-MM-DD
        try:
            parsed = datetime.strptime(date_str, '%Y-%m-%d').date()
            return str(parsed)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def edit_task(file_path, line_num, new_description, context=None, scheduled_date=None,
              due_date=None, priority=None, create_backups=True, auto_confirm=False):
    """
    Edit a task's description and optionally add metadata.

    Args:
        file_path (Path): Path to file containing task
        line_num (int): Line number of task (1-indexed)
        new_description (str): New task description
        context (str, optional): Context tag to add
        scheduled_date (str, optional): Scheduled date to add
        due_date (str, optional): Due date to add
        priority (str, optional): Priority symbol to add
        create_backups (bool): Whether to create backup file
        auto_confirm (bool): Skip confirmation prompt (for agentic use)

    Returns:
        bool: True if successful
    """
    vault_path = get_vault_path()

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    # Validate line number
    if line_num < 1 or line_num > len(lines):
        print(f"Error: Invalid line number {line_num} (file has {len(lines)} lines)")
        return False

    # Get task line
    task_line = lines[line_num - 1]
    task = parse_task_line(task_line, line_num)

    if not task:
        print(f"Error: Line {line_num} is not a task")
        return False

    # Display current task
    print(f"\nFile: {file_path.relative_to(vault_path)}:{line_num}")
    print(f"Current: {task['description']}")
    print(f"New:     {new_description}")

    # Add metadata if provided
    final_description = add_metadata_to_task(
        new_description,
        context=context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=priority
    )

    print(f"Final:   {final_description}")

    # Confirm
    if not auto_confirm:
        response = input("\nProceed with edit? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return False

    # Create backup
    if create_backups:
        create_backup(file_path)

    # Update task
    task_match = re.match(r'^(\s*- \[(.)\]\s+)(.*)$', task_line)
    if task_match:
        prefix, status, old_desc = task_match.groups()
        lines[line_num - 1] = f"{prefix}{final_description}\n"

        # Write back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"\n✓ Task updated in {file_path.relative_to(vault_path)}:{line_num}")
            if create_backups:
                print("  Backup created with .bak extension")
            return True

        except Exception as e:
            print(f"Error writing file: {e}")
            return False

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Edit a task's description at a specific file and line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Change task description
  python tools/edit_task.py --file GTD/Dashboard.md --line 42 --description "New description"

  # Change description and add context
  python tools/edit_task.py --file Daily/2025-12-29.md --line 27 --description "Discuss instax with Sharné" --context "@sharne"

  # Change description and add due date
  python tools/edit_task.py --file Daily/2025-12-29.md --line 29 --description "Buy instax camera" --due tomorrow --context "@out"

  # Add priority
  python tools/edit_task.py --file Daily/2025-12-25.md --line 34 --description "Best albums" --priority "⏬"

Date formats:
  - today, tomorrow, +N (days), YYYY-MM-DD

Priority symbols:
  - ⏫ highest, 🔼 high, 🔽 low, ⏬ lowest
        """
    )

    parser.add_argument("--file", "-f", required=True, metavar="PATH",
                       help="File containing task (relative to vault)")
    parser.add_argument("--line", "-l", required=True, type=int, metavar="N",
                       help="Line number of task (1-indexed)")
    parser.add_argument("--description", "-d", required=True, metavar="TEXT",
                       help="New task description")
    parser.add_argument("--context", "-c", metavar="TAG",
                       help="Context tag to add (e.g., @pc, @work)")
    parser.add_argument("--scheduled", "-s", metavar="DATE",
                       help="Scheduled date (today, tomorrow, +N, YYYY-MM-DD)")
    parser.add_argument("--due", metavar="DATE",
                       help="Due date (today, tomorrow, +N, YYYY-MM-DD)")
    parser.add_argument("--priority", "-p", metavar="SYMBOL",
                       help="Priority symbol (⏫, 🔼, 🔽, ⏬)")
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

    # Get vault path and construct file path
    vault_path = get_vault_path()
    file_path = vault_path / args.file

    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return

    # Edit the task
    edit_task(
        file_path,
        args.line,
        args.description,
        context=args.context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=args.priority,
        create_backups=False,  # Disabled - rely on git
        auto_confirm=args.yes
    )


if __name__ == "__main__":
    main()
