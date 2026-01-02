#!/usr/bin/env python3
"""
Find tasks in Obsidian vault matching GTD "To Process" criteria.

This tool replicates the "To Process" query from Dashboard.md to find tasks
that need to be clarified and organized according to GTD methodology.

Usage:
    python tools/find_inbox.py
    python tools/find_inbox.py --show-details
    python tools/find_inbox.py --limit 10
    python tools/find_inbox.py --export inbox.txt
"""

import argparse
from pathlib import Path
from gtd_common import (
    get_vault_path,
    parse_task_line,
    task_matches_to_process_criteria
)


def find_inbox_tasks(vault_path, limit=None):
    """
    Find all tasks matching "To Process" criteria.

    Args:
        vault_path (Path): Path to Obsidian vault
        limit (int, optional): Maximum number of tasks to return

    Returns:
        list: List of task dictionaries with file, line_num, description
    """
    tasks = []

    for md_file in vault_path.rglob("*.md"):
        # Skip .obsidian folder
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if not task:
                    continue

                # Apply "To Process" filter
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

                # Check limit
                if limit and len(tasks) >= limit:
                    break

        except Exception as e:
            print(f"Error reading {md_file}: {e}")

        # Check limit
        if limit and len(tasks) >= limit:
            break

    # Sort by path reverse (as specified in Dashboard.md)
    tasks.sort(key=lambda x: str(x['file_relative']), reverse=True)

    return tasks


def display_tasks(tasks, show_details=False):
    """
    Display tasks grouped by file.

    Args:
        tasks (list): List of task dictionaries
        show_details (bool): Whether to show file path and line numbers
    """
    print(f"Found {len(tasks)} task(s) to process:\n")

    if not tasks:
        print("Inbox is empty! All tasks have been processed.")
        return

    current_file = None
    for task in tasks:
        # Group by file
        if task['file_relative'] != current_file:
            current_file = task['file_relative']
            print(f"\n{task['file_relative']}:")

        # Show task
        if show_details:
            task_str = f"  Line {task['line_num']}: {task['description']}"
            if task['due_date']:
                task_str += f" [Due: {task['due_date']}]"
            if task['scheduled_date']:
                task_str += f" [Scheduled: {task['scheduled_date']}]"
        else:
            task_str = f"  - {task['description']}"

        print(task_str)


def export_tasks(tasks, export_path):
    """
    Export tasks to a text file.

    Args:
        tasks (list): List of task dictionaries
        export_path (str): Path to export file
    """
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(f"# Inbox - Tasks to Process ({len(tasks)} items)\n\n")

        current_file = None
        for task in tasks:
            # Group by file
            if task['file_relative'] != current_file:
                current_file = task['file_relative']
                f.write(f"\n## {task['file_relative']}\n\n")

            # Write task
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
        description="Find tasks in Obsidian vault that need GTD processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/find_inbox.py                  # Find all unprocessed tasks
  python tools/find_inbox.py --show-details   # Show file paths and line numbers
  python tools/find_inbox.py --limit 10       # Limit to first 10 tasks
  python tools/find_inbox.py --export inbox.txt  # Export to file
        """
    )

    parser.add_argument("--show-details", "-d", action="store_true",
                       help="Show file path, line number, and dates")
    parser.add_argument("--limit", "-l", type=int, metavar="N",
                       help="Limit number of tasks to display")
    parser.add_argument("--export", "-e", metavar="FILE",
                       help="Export tasks to file")

    args = parser.parse_args()

    # Get vault path and find tasks
    vault_path = get_vault_path()
    tasks = find_inbox_tasks(vault_path, limit=args.limit)

    # Export if requested
    if args.export:
        export_tasks(tasks, args.export)
    else:
        # Otherwise display to terminal
        display_tasks(tasks, show_details=args.show_details)


if __name__ == "__main__":
    main()
