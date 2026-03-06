#!/usr/bin/env python3
"""
Move a task from one file to another while preserving metadata.

Uses Obsidian CLI for append to destination; direct file I/O for
removal from source (no CLI equivalent for line deletion).

Usage:
    python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md
    python tools/move_task.py --source GTD/PC.md --line 10 --dest GTD/Projects/Website.md
"""

import argparse
from pathlib import Path

from gtd_common import (
    get_vault_path,
    parse_task_line,
    find_task_lines_by_match,
)
import obsidian_cli as obs


def move_task(source_rel, line_num, dest_rel, auto_confirm=False):
    """
    Move a task (and subtasks) from source file to destination file.
    """
    vault_path = get_vault_path()
    source_path = vault_path / source_rel

    with open(source_path, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()

    if line_num < 1 or line_num > len(source_lines):
        print(f"Error: Invalid line number {line_num} (file has {len(source_lines)} lines)")
        return False

    task_line = source_lines[line_num - 1]
    task = parse_task_line(task_line, line_num)
    if not task:
        print(f"Error: Line {line_num} is not a task")
        return False

    # Collect subtasks (indented tasks immediately following)
    subtask_lines = []
    for i in range(line_num, len(source_lines)):
        subtask = parse_task_line(source_lines[i], i + 1)
        if subtask and subtask['indent'] > task['indent']:
            subtask_lines.append(source_lines[i])
        elif i > line_num - 1:
            break

    print(f"\nMoving task:")
    print(f"  From: {source_rel}:{line_num}")
    print(f"  To:   {dest_rel}")
    print(f"  Task: {task['description']}")
    if subtask_lines:
        print(f"  Subtasks: {len(subtask_lines)}")

    if not auto_confirm:
        response = input("\nProceed? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("Cancelled.")
            return False

    # Remove from source (direct I/O — no CLI equivalent)
    lines_to_remove = [line_num - 1] + list(range(line_num, line_num + len(subtask_lines)))
    for idx in sorted(lines_to_remove, reverse=True):
        if idx < len(source_lines):
            del source_lines[idx]

    with open(source_path, 'w', encoding='utf-8') as f:
        f.writelines(source_lines)

    # Append to destination via CLI
    content = task_line.rstrip('\n')
    for sl in subtask_lines:
        content += f"\\n{sl.rstrip(chr(10))}"

    obs.append_to_file(content, path=dest_rel)

    print(f"\n✓ Task moved successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Move a task from one file to another",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md
  python tools/move_task.py --source GTD/PC.md --line 10 --dest GTD/Projects/Website.md
  python tools/move_task.py --source Daily/2025-12-29.md --match "Buy instax" --dest GTD/Projects/Gifts.md
        """
    )

    parser.add_argument("--source", "-s", required=True, metavar="FILE",
                        help="Source file (relative to vault)")
    line_group = parser.add_mutually_exclusive_group(required=True)
    line_group.add_argument("--line", "-l", type=int, metavar="N",
                            help="Line number of task to move")
    line_group.add_argument("--match", metavar="TEXT",
                            help="Match task description")
    parser.add_argument("--match-regex", action="store_true",
                        help="Treat --match as regex")
    parser.add_argument("--occurrence", type=int, default=1, metavar="N",
                        help="Which match occurrence (default: 1)")
    parser.add_argument("--dest", "-d", required=True, metavar="FILE",
                        help="Destination file (relative to vault)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting")

    args = parser.parse_args()

    vault_path = get_vault_path()
    source_path = vault_path / args.source
    if not source_path.exists():
        print(f"Error: Source file not found: {args.source}")
        return

    if (vault_path / args.source).resolve() == (vault_path / args.dest).resolve():
        print("Error: Source and destination files are the same")
        return

    line_num = args.line
    if args.match is not None:
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        matches = find_task_lines_by_match(lines, args.match, use_regex=args.match_regex)
        if not matches:
            print("Error: No matching tasks found")
            return
        if args.occurrence > len(matches):
            print(f"Error: Only found {len(matches)} match(es); occurrence {args.occurrence} out of range")
            return
        line_num = matches[args.occurrence - 1]
        print(f"Matched {len(matches)} task(s); using occurrence {args.occurrence} at line {line_num}")

    move_task(args.source, line_num, args.dest, auto_confirm=args.yes)


if __name__ == "__main__":
    main()
