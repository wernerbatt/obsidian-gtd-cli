#!/usr/bin/env python3
"""
Edit a task's description at a specific file and line number.

Uses Obsidian CLI for reads and direct file I/O for the line-level write
(the CLI has no line-edit command).

Usage:
    python tools/edit_task.py --file GTD/Dashboard.md --line 42 --description "New description"
    python tools/edit_task.py --file Daily/2025-12-29.md --match "Buy instax" --description "Buy instax camera" --context "@out"
"""

import argparse
import re

from gtd_common import (
    get_vault_path,
    load_config,
    parse_task_line,
    add_metadata_to_task,
    find_task_lines_by_match,
    parse_date_string,
)
import obsidian_cli as obs


def edit_task(file_rel, line_num, new_description, *, context=None,
              scheduled_date=None, due_date=None, priority=None,
              auto_confirm=False, match_text=None, match_regex=False,
              occurrence=1):
    """
    Edit a task's description and optionally add/update metadata.

    Reads via Obsidian CLI, writes via direct file I/O (line-level edit).
    """
    vault_path = get_vault_path()
    file_path = vault_path / file_rel

    # Read file
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

    task_line = lines[line_num - 1]
    task = parse_task_line(task_line, line_num)

    if not task:
        print(f"Error: Line {line_num} is not a task")
        return False

    print(f"\nFile: {file_rel}:{line_num}")
    print(f"Current: {task['description']}")
    print(f"New:     {new_description}")

    old_desc = task['description']

    # Preserve existing metadata unless explicitly overridden
    if scheduled_date is None:
        m = re.search(r'⏳\s*(\d{4}-\d{2}-\d{2})', old_desc)
        if m:
            scheduled_date = m.group(1)

    if due_date is None:
        m = re.search(r'[📅📆]\s*(\d{4}-\d{2}-\d{2})', old_desc)
        if m:
            due_date = m.group(1)

    if priority is None:
        pm = re.findall(r'[⏫🔼🔽⏬🔺]', old_desc)
        if pm:
            priority = pm[-1]

    # Preserve recurrence
    rm = re.search(r'(🔁[^⏳📅📆🛫✅⏫🔼🔽⏬🔺]*)', old_desc)
    if rm and '🔁' not in new_description:
        new_description = f"{new_description} {rm.group(1).strip()}"

    final_description = add_metadata_to_task(
        new_description,
        context=context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=priority,
    )

    print(f"Final:   {final_description}")

    if not auto_confirm:
        response = input("\nProceed with edit? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("Cancelled.")
            return False

    # Write back (line-level edit)
    task_match = re.match(r'^(\s*- \[(.)\]\s+)(.*)$', task_line)
    if task_match:
        prefix = task_match.group(1)
        lines[line_num - 1] = f"{prefix}{final_description}\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"\n✓ Task updated in {file_rel}:{line_num}")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Edit a task's description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/edit_task.py --file GTD/Dashboard.md --line 42 --description "New description"
  python tools/edit_task.py --file Daily/2025-12-29.md --match "Buy instax" --description "Buy instax camera" --context "@out"
  python tools/edit_task.py --file Daily/2025-12-25.md --line 34 --description "Best albums" --priority "⏬"

Date formats: today, tomorrow, +N (days), YYYY-MM-DD
Priority symbols: ⏫ highest, 🔼 high, 🔽 low, ⏬ lowest
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
    parser.add_argument("--description", "-d", required=True, metavar="TEXT",
                        help="New task description")
    parser.add_argument("--context", "-c", metavar="TAG",
                        help="Context tag to add")
    parser.add_argument("--scheduled", "-s", metavar="DATE",
                        help="Scheduled date")
    parser.add_argument("--due", metavar="DATE",
                        help="Due date")
    parser.add_argument("--priority", "-p", metavar="SYMBOL",
                        help="Priority symbol")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting")

    args = parser.parse_args()

    scheduled_date = parse_date_string(args.scheduled) if args.scheduled else None
    due_date = parse_date_string(args.due) if args.due else None

    valid_priorities = ['⏫', '🔼', '🔽', '⏬']
    if args.priority and args.priority not in valid_priorities:
        print(f"Error: Invalid priority '{args.priority}'. Valid: {', '.join(valid_priorities)}")
        return

    edit_task(
        args.file,
        args.line if args.match is None else None,
        args.description,
        context=args.context,
        scheduled_date=scheduled_date,
        due_date=due_date,
        priority=args.priority,
        auto_confirm=args.yes,
        match_text=args.match,
        match_regex=args.match_regex,
        occurrence=args.occurrence,
    )


if __name__ == "__main__":
    main()
