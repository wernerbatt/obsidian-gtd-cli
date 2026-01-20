#!/usr/bin/env python3
"""
Mark a task as done with completion date.

This tool marks a task as complete by changing [ ] to [x] and adding
a done date (✅ YYYY-MM-DD) in Obsidian Tasks format.

Usage:
    python tools/mark_done.py --file GTD/Dashboard.md --line 42
    python tools/mark_done.py --file Daily/2025-12-29.md --line 27 --date 2026-01-03
    python tools/mark_done.py --file Daily/2025-12-28.md --line 28 --date today
"""

import argparse
from pathlib import Path
from datetime import datetime, date, timedelta
from gtd_common import (
    get_vault_path,
    parse_task_line,
    create_backup,
    find_task_lines_by_match
)
import re


def parse_date_string(date_str):
    """
    Parse date string into YYYY-MM-DD format.

    Args:
        date_str (str): Date string (today, yesterday, YYYY-MM-DD)

    Returns:
        str: Date in YYYY-MM-DD format
    """
    date_str = date_str.strip().lower()
    today = date.today()

    if date_str == 'today':
        return str(today)
    elif date_str == 'yesterday':
        return str(today - timedelta(days=1))
    else:
        # Try parsing as YYYY-MM-DD
        try:
            parsed = datetime.strptime(date_str, '%Y-%m-%d').date()
            return str(parsed)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD, today, or yesterday")


def mark_task_done(file_path, line_num, done_date=None, create_backups=True, auto_confirm=False,
                   match_text=None, match_regex=False, occurrence=1):
    """
    Mark a task as done with completion date.

    Args:
        file_path (Path): Path to file containing task
        line_num (int): Line number of task (1-indexed)
        done_date (str, optional): Done date (defaults to today)
        create_backups (bool): Whether to create backup file
        auto_confirm (bool): Skip confirmation prompt (for agentic use)

    Returns:
        bool: True if successful
    """
    vault_path = get_vault_path()

    # Default to today if no date provided
    if not done_date:
        done_date = str(date.today())

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    # Resolve line number by match if needed
    if line_num is None and match_text:
        matches = find_task_lines_by_match(lines, match_text, use_regex=match_regex)
        if not matches:
            print("Error: No matching tasks found")
            return False
        if occurrence < 1:
            print("Error: Occurrence must be >= 1")
            return False
        if occurrence > len(matches):
            print(f"Error: Only found {len(matches)} match(es); occurrence {occurrence} is out of range")
            return False
        line_num = matches[occurrence - 1]
        print(f"Matched {len(matches)} task(s); using occurrence {occurrence} at line {line_num}")

    # Validate line number
    if line_num is None or line_num < 1 or line_num > len(lines):
        print(f"Error: Invalid line number {line_num} (file has {len(lines)} lines)")
        return False

    # Get task line
    task_line = lines[line_num - 1]
    task = parse_task_line(task_line, line_num)

    if not task:
        print(f"Error: Line {line_num} is not a task")
        return False

    if task['is_done']:
        print(f"Task is already marked as done")
        return False

    # Display task
    print(f"\nFile: {file_path.relative_to(vault_path)}:{line_num}")
    print(f"Task: {task['description']}")
    print(f"Done date: {done_date}")

    # Confirm
    if not auto_confirm:
        response = input("\nMark as done? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return False

    # Create backup
    if create_backups:
        create_backup(file_path)

    # Update task - change [ ] to [x] and add done date
    task_match = re.match(r'^(\s*)- \[(.)\]\s+(.*)$', task_line)
    if task_match:
        indent, status, description = task_match.groups()

        # Remove existing done date if present
        description = re.sub(r'✅\s*\d{4}-\d{2}-\d{2}', '', description).strip()

        # Add done date at the end
        new_description = f"{description} ✅ {done_date}"

        lines[line_num - 1] = f"{indent}- [x] {new_description}\n"

        # Write back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"\n✓ Task marked as done in {file_path.relative_to(vault_path)}:{line_num}")
            if create_backups:
                print("  Backup created with .bak extension")
            return True

        except Exception as e:
            print(f"Error writing file: {e}")
            return False

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Mark a task as done with completion date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mark task as done with today's date
  python tools/mark_done.py --file GTD/Dashboard.md --line 42

  # Mark task as done with specific date
  python tools/mark_done.py --file Daily/2025-12-29.md --line 27 --date 2026-01-03

  # Mark task as done by matching description
  python tools/mark_done.py --file Daily/2025-12-29.md --match "message" --date 2026-01-03

  # Mark task as done yesterday
  python tools/mark_done.py --file Daily/2025-12-28.md --line 28 --date yesterday

The tool will:
- Change [ ] to [x]
- Add ✅ YYYY-MM-DD at the end of the task
- Create backup file before modifying

Date formats:
  - today (default)
  - yesterday
  - YYYY-MM-DD (specific date)
        """
    )

    parser.add_argument("--file", "-f", required=True, metavar="PATH",
                       help="File containing task (relative to vault)")
    line_group = parser.add_mutually_exclusive_group(required=True)
    line_group.add_argument("--line", "-l", type=int, metavar="N",
                           help="Line number of task (1-indexed)")
    line_group.add_argument("--match", metavar="TEXT",
                           help="Match exact task description (use --match-regex for patterns)")
    parser.add_argument("--match-regex", action="store_true",
                       help="Treat --match as regex")
    parser.add_argument("--occurrence", type=int, default=1, metavar="N",
                       help="Match occurrence to use when multiple tasks match (default: 1)")
    parser.add_argument("--date", "-d", metavar="DATE",
                       help="Done date (default: today)")
    parser.add_argument("--yes", "-y", action="store_true",
                       help="Auto-confirm without prompting (for agentic use)")

    args = parser.parse_args()

    # Parse date
    done_date = None
    if args.date:
        try:
            done_date = parse_date_string(args.date)
        except ValueError as e:
            print(f"Error: {e}")
            return

    # Get vault path and construct file path
    vault_path = get_vault_path()
    file_path = vault_path / args.file

    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return

    # Mark task as done
    mark_task_done(
        file_path,
        args.line if args.match is None else None,
        done_date=done_date,
        create_backups=False,  # Disabled - rely on git
        auto_confirm=args.yes,
        match_text=args.match,
        match_regex=args.match_regex,
        occurrence=args.occurrence
    )


if __name__ == "__main__":
    main()
