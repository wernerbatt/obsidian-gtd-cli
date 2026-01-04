#!/usr/bin/env python3
"""
Find tasks in Obsidian vault by mode.

Modes:
  - inbox: tasks needing GTD processing
  - someday: legacy @someday or lowest-priority (⏬) tasks

Usage:
    python tools/find_tasks.py --mode inbox
    python tools/find_tasks.py --mode someday --show-details
    python tools/find_tasks.py --mode inbox --limit 10
    python tools/find_tasks.py --mode someday --export someday.txt
"""

import argparse
from gtd_common import (
    get_vault_path,
    parse_task_line,
    task_matches_to_process_criteria
)


def find_inbox_tasks(vault_path, limit=None):
    tasks = []

    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if not task:
                    continue

                if not task_matches_to_process_criteria(task, md_file):
                    continue

                tasks.append({
                    'file': md_file,
                    'file_relative': md_file.relative_to(vault_path),
                    'line_num': line_num,
                    'description': task['description'],
                    'due_date': task['due_date'],
                    'scheduled_date': task['scheduled_date']
                })

                if limit and len(tasks) >= limit:
                    break

        except Exception as e:
            print(f"Error reading {md_file}: {e}")

        if limit and len(tasks) >= limit:
            break

    tasks.sort(key=lambda x: str(x['file_relative']), reverse=True)
    return tasks


def find_someday_tasks(vault_path, limit=None):
    tasks = []

    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if not task:
                    continue

                if task['is_done']:
                    continue

                desc = task['description']
                if "@someday" not in desc and task.get('priority') != '⏬':
                    continue

                tasks.append({
                    'file': md_file,
                    'file_relative': md_file.relative_to(vault_path),
                    'line_num': line_num,
                    'description': task['description'],
                    'due_date': task['due_date'],
                    'scheduled_date': task['scheduled_date']
                })

                if limit and len(tasks) >= limit:
                    break

        except Exception as e:
            print(f"Error reading {md_file}: {e}")

        if limit and len(tasks) >= limit:
            break

    tasks.sort(key=lambda x: str(x['file_relative']), reverse=True)
    return tasks


def display_tasks(tasks, label, show_details=False):
    print(f"Found {len(tasks)} {label} task(s):\n")

    if not tasks:
        print(f"No {label} tasks found.")
        return

    current_file = None
    for task in tasks:
        if task['file_relative'] != current_file:
            current_file = task['file_relative']
            print(f"\n{task['file_relative']}:")

        if show_details:
            task_str = f"  Line {task['line_num']}: {task['description']}"
            if task['due_date']:
                task_str += f" [Due: {task['due_date']}]"
            if task['scheduled_date']:
                task_str += f" [Scheduled: {task['scheduled_date']}]"
        else:
            task_str = f"  - {task['description']}"

        print(task_str)


def export_tasks(tasks, export_path, label):
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(f"# {label} Tasks ({len(tasks)} items)\n\n")

        current_file = None
        for task in tasks:
            if task['file_relative'] != current_file:
                current_file = task['file_relative']
                f.write(f"\n## {task['file_relative']}\n\n")

            f.write(f"- [ ] {task['description']}\n")
            f.write(f"  - File: {task['file_relative']}\n")
            f.write(f"  - Line: {task['line_num']}\n")
            if task['due_date']:
                f.write(f"  - Due: {task['due_date']}\n")
            if task['scheduled_date']:
                f.write(f"  - Scheduled: {task['scheduled_date']}\n")
            f.write("\n")

    print(f"\nExported {len(tasks)} tasks to: {export_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Find tasks in Obsidian vault by mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/find_tasks.py --mode inbox             # Find tasks to process
  python tools/find_tasks.py --mode someday           # Find someday tasks
  python tools/find_tasks.py --mode inbox --limit 10  # Limit to first 10
  python tools/find_tasks.py --mode someday --export someday.txt
        """
    )

    parser.add_argument("--mode", "-m", choices=["inbox", "someday"], required=True,
                        help="Task mode: inbox or someday")
    parser.add_argument("--show-details", "-d", action="store_true",
                        help="Show file path, line number, and dates")
    parser.add_argument("--limit", "-l", type=int, metavar="N",
                        help="Limit number of tasks to display")
    parser.add_argument("--export", "-e", metavar="FILE",
                        help="Export tasks to file")

    args = parser.parse_args()

    vault_path = get_vault_path()
    if args.mode == "inbox":
        tasks = find_inbox_tasks(vault_path, limit=args.limit)
        label = "inbox"
    else:
        tasks = find_someday_tasks(vault_path, limit=args.limit)
        label = "someday"

    if args.export:
        export_tasks(tasks, args.export, label.title())
    else:
        display_tasks(tasks, label, show_details=args.show_details)


if __name__ == "__main__":
    main()
