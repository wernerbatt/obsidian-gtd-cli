#!/usr/bin/env python3
"""
Delete a task (remove the line entirely) from an Obsidian vault file.

No Obsidian CLI equivalent for line deletion — uses direct file I/O.

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
    find_task_lines_by_match,
)


def delete_task(file_rel, line_num=None, match_text=None, match_regex=False,
                occurrence=1, auto_confirm=False):
    """
    Delete a task line from a file.

    Returns True if task was deleted.
    """
    vault_path = get_vault_path()
    file_path = vault_path / file_rel

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Resolve line number by match
    if line_num is None and match_text:
        matches = find_task_lines_by_match(lines, match_text, use_regex=match_regex)
        if not matches:
            print("Error: No matching tasks found")
            return False
        if occurrence > len(matches):
            print(f"Error: Only found {len(matches)} match(es); occurrence {occurrence} out of range")
            return False
        line_num = matches[occurrence - 1]
        print(f"Matched {len(matches)} task(s); using occurrence {occurrence} at line {line_num}")

    if line_num is None or line_num < 1 or line_num > len(lines):
        print(f"Error: Invalid line number {line_num} (file has {len(lines)} lines)")
        return False

    task = parse_task_line(lines[line_num - 1], line_num)
    if not task:
        print(f"Error: Line {line_num} is not a task: {lines[line_num - 1].rstrip()}")
        return False

    print(f"\nFile: {file_rel}:{line_num}")
    print(f"Task: {task['description']}")

    if not auto_confirm:
        response = input("\nDelete this task? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("Cancelled.")
            return False

    del lines[line_num - 1]

    # Collapse consecutive blank lines
    cleaned = []
    prev_blank = False
    for line in lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned)

    print(f"\n✓ Task deleted from {file_rel}:{line_num}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Delete a task (remove line) from an Obsidian vault file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/delete_task.py --file Daily/2026/2026-01-11.md --line 29
  python tools/delete_task.py --file Daily/2026/2026-01-11.md --match "rubber bands"
  python tools/delete_task.py --file Daily/2026/2026-01-11.md --match "tiktok" --match-regex --yes
        """,
    )

    parser.add_argument("--file", "-f", required=True, metavar="PATH",
                        help="File containing task (relative to vault)")
    line_group = parser.add_mutually_exclusive_group(required=True)
    line_group.add_argument("--line", "-l", type=int, metavar="N",
                            help="Line number of task (1-indexed)")
    line_group.add_argument("--match", metavar="TEXT",
                            help="Match task description")
    parser.add_argument("--match-regex", action="store_true",
                        help="Treat --match as regex")
    parser.add_argument("--occurrence", type=int, default=1, metavar="N",
                        help="Which match occurrence (default: 1)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting")

    args = parser.parse_args()

    vault_path = get_vault_path()
    file_path = vault_path / args.file
    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return

    delete_task(
        args.file,
        line_num=args.line if args.match is None else None,
        match_text=args.match,
        match_regex=args.match_regex,
        occurrence=args.occurrence,
        auto_confirm=args.yes,
    )


if __name__ == "__main__":
    main()
