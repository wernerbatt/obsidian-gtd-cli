#!/usr/bin/env python3
"""
Delete a task (remove the line entirely) from an Obsidian vault file.

Usage:
    python tools/delete_task.py --file Daily/2026/2026-01-11.md --line 29
    python tools/delete_task.py --file Daily/2026/2026-01-11.md --match "rubber bands"
    python tools/delete_task.py --file Daily/2026/2026-01-11.md --match "tiktok" --match-regex --yes
"""

import argparse
from pathlib import Path
from gtd_common import (
    get_vault_path,
    parse_task_line,
    create_backup,
    find_task_lines_by_match,
)


def delete_task(file_path, line_num=None, match_text=None, match_regex=False,
                occurrence=1, create_backups=True, auto_confirm=False):
    """
    Delete a task line from a file.

    Args:
        file_path (Path): Absolute path to file
        line_num (int, optional): 1-indexed line number
        match_text (str, optional): Text or regex to match
        match_regex (bool): Treat match_text as regex
        occurrence (int): Which match to use when multiple (default: 1)
        create_backups (bool): Create .bak before modifying
        auto_confirm (bool): Skip confirmation prompt

    Returns:
        bool: True if task was deleted
    """
    vault_path = get_vault_path()

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

    # Verify it's a task
    task_line = lines[line_num - 1]
    task = parse_task_line(task_line, line_num)

    if not task:
        print(f"Error: Line {line_num} is not a task: {task_line.rstrip()}")
        return False

    # Show what will be deleted
    print(f"\nFile: {file_path.relative_to(vault_path)}:{line_num}")
    print(f"Task: {task['description']}")

    if not auto_confirm:
        response = input("\nDelete this task? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return False

    if create_backups:
        create_backup(file_path)

    # Remove the line
    del lines[line_num - 1]

    # Clean up: if removal left consecutive blank lines, collapse to one
    cleaned = []
    prev_blank = False
    for line in lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned)

        print(f"\n✓ Task deleted from {file_path.relative_to(vault_path)}:{line_num}")
        if create_backups:
            print("  Backup created with .bak extension")
        return True

    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Delete a task (remove line) from an Obsidian vault file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Delete by line number
  python tools/delete_task.py --file Daily/2026/2026-01-11.md --line 29

  # Delete by matching description
  python tools/delete_task.py --file Daily/2026/2026-01-11.md --match "rubber bands"

  # Delete by regex match (auto-confirm)
  python tools/delete_task.py --file Daily/2026/2026-01-11.md --match "tiktok" --match-regex --yes

  # Delete second occurrence of a match
  python tools/delete_task.py --file GTD/Projects/Poker.md --match "Decide on" --occurrence 2 --yes

The tool will:
- Remove the entire task line from the file
- Collapse consecutive blank lines left behind
- Create a backup before modifying (unless --no-backup)
        """,
    )

    parser.add_argument("--file", "-f", required=True, metavar="PATH",
                        help="File containing task (relative to vault)")
    line_group = parser.add_mutually_exclusive_group(required=True)
    line_group.add_argument("--line", "-l", type=int, metavar="N",
                            help="Line number of task (1-indexed)")
    line_group.add_argument("--match", metavar="TEXT",
                            help="Match task description (use --match-regex for patterns)")
    parser.add_argument("--match-regex", action="store_true",
                        help="Treat --match as regex")
    parser.add_argument("--occurrence", type=int, default=1, metavar="N",
                        help="Which match to use when multiple tasks match (default: 1)")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip creating .bak file")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting (for agentic use)")

    args = parser.parse_args()

    vault_path = get_vault_path()
    file_path = vault_path / args.file

    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return

    delete_task(
        file_path,
        line_num=args.line if args.match is None else None,
        match_text=args.match,
        match_regex=args.match_regex,
        occurrence=args.occurrence,
        create_backups=not args.no_backup,
        auto_confirm=args.yes,
    )


if __name__ == "__main__":
    main()
