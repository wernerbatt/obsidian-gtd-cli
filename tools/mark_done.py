#!/usr/bin/env python3
"""
Mark a task as done via the official Obsidian CLI.

Usage:
    python tools/mark_done.py --file GTD/Dashboard.md --line 42
    python tools/mark_done.py --file Daily/2025-12-29.md --match "message"
    python tools/mark_done.py --file Daily/2025-12-28.md --line 28 --yes
"""

import argparse

from gtd_common import (
    get_vault_path,
    parse_task_line,
    find_task_lines_by_match,
    parse_date_string,
)
import obsidian_cli as obs


def mark_task_done(file_rel, line_num=None, done_date=None, auto_confirm=False,
                   match_text=None, match_regex=False, occurrence=1):
    """
    Mark a task as done.

    Uses the Obsidian CLI `task done` command for simple cases.
    Falls back to direct file I/O when a custom done_date is specified
    (the CLI always uses today's date).
    """
    vault_path = get_vault_path()
    file_path = vault_path / file_rel

    # Resolve line number by match if needed
    if line_num is None and match_text:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        matches = find_task_lines_by_match(lines, match_text, use_regex=match_regex)
        if not matches:
            print("Error: No matching tasks found")
            return False
        if occurrence > len(matches):
            print(f"Error: Only found {len(matches)} match(es); occurrence {occurrence} out of range")
            return False
        line_num = matches[occurrence - 1]
        print(f"Matched {len(matches)} task(s); using occurrence {occurrence} at line {line_num}")

    if line_num is None:
        print("Error: No line number specified")
        return False

    # Get task info via CLI
    info = obs.task_info(file_rel, line_num)
    text = info.get('text', '')
    task = parse_task_line(text, line_num)

    if not task:
        print(f"Error: Line {line_num} is not a task")
        return False
    if task['is_done']:
        print("Task is already marked as done")
        return False

    print(f"\nFile: {file_rel}:{line_num}")
    print(f"Task: {task['description']}")
    print(f"Done date: {done_date or 'today'}")

    if not auto_confirm:
        response = input("\nMark as done? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("Cancelled.")
            return False

    # If custom date, we need direct file I/O
    if done_date and done_date != str(__import__('datetime').date.today()):
        import re
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        task_match = re.match(r'^(\s*)- \[(.)\]\s+(.*)$', lines[line_num - 1])
        if task_match:
            indent, _, description = task_match.groups()
            description = re.sub(r'✅\s*\d{4}-\d{2}-\d{2}', '', description).strip()
            lines[line_num - 1] = f"{indent}- [x] {description} ✅ {done_date}\n"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"\n✓ Task marked as done in {file_rel}:{line_num}")
            return True
        return False

    # Use CLI for today's date
    obs.task_done(file_rel, line_num)
    print(f"\n✓ Task marked as done in {file_rel}:{line_num}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Mark a task as done (via Obsidian CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/mark_done.py --file GTD/Dashboard.md --line 42
  python tools/mark_done.py --file Daily/2025-12-29.md --match "message"
  python tools/mark_done.py --file Daily/2025-12-29.md --line 27 --date yesterday

Date formats: today (default), yesterday, YYYY-MM-DD
        """
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
    parser.add_argument("--date", "-d", metavar="DATE",
                        help="Done date (default: today)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting")

    args = parser.parse_args()

    done_date = parse_date_string(args.date) if args.date else None

    mark_task_done(
        args.file,
        line_num=args.line if args.match is None else None,
        done_date=done_date,
        auto_confirm=args.yes,
        match_text=args.match,
        match_regex=args.match_regex,
        occurrence=args.occurrence,
    )


if __name__ == "__main__":
    main()
