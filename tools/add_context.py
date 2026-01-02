#!/usr/bin/env python3
"""
Batch add context tags and scheduled dates to tasks.

This tool allows you to add context tags and scheduled dates to multiple tasks
based on search criteria, helping you organize tasks by context.

Usage:
    python tools/add_context.py --context "@pc" --search "research"
    python tools/add_context.py --context "@work" --file GTD/Dashboard.md
    python tools/add_context.py --context "@home" --search "clean" --scheduled +7
    python tools/add_context.py --context "@pc" --search "code" --dry-run
"""

import argparse
import re
from pathlib import Path
from datetime import datetime, date, timedelta
from gtd_common import (
    get_vault_path,
    load_config,
    parse_task_line,
    create_backup,
    add_metadata_to_task
)


def find_tasks_by_criteria(vault_path, search_term=None, file_filter=None):
    """
    Find tasks matching search criteria.

    Args:
        vault_path (Path): Path to Obsidian vault
        search_term (str, optional): Search term to match in description
        file_filter (str, optional): File path filter (relative to vault)

    Returns:
        list: List of task dictionaries
    """
    tasks = []

    # Determine which files to search
    if file_filter:
        md_files = [vault_path / file_filter]
    else:
        md_files = vault_path.rglob("*.md")

    for md_file in md_files:
        # Skip .obsidian folder
        if ".obsidian" in md_file.parts:
            continue

        # Check file exists
        if not md_file.exists():
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if not task:
                    continue

                # Skip done tasks
                if task['is_done']:
                    continue

                # Apply search filter
                if search_term:
                    if search_term.lower() not in task['description'].lower():
                        continue

                tasks.append({
                    'file': md_file,
                    'file_relative': md_file.relative_to(vault_path),
                    'line_num': line_num,
                    'description': task['description'],
                    'original_line': line,
                    'indent': task['indent']
                })

        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    return tasks


def parse_scheduled_date(date_str):
    """
    Parse scheduled date string into YYYY-MM-DD format.

    Args:
        date_str (str): Date string (today, tomorrow, +N, YYYY-MM-DD)

    Returns:
        str: Date in YYYY-MM-DD format

    Raises:
        ValueError: If date format is invalid
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


def update_tasks(tasks, context=None, scheduled_date=None, dry_run=False, create_backups=True):
    """
    Update tasks with context tag and/or scheduled date.

    Args:
        tasks (list): List of task dictionaries
        context (str, optional): Context tag to add (e.g., '@pc')
        scheduled_date (str, optional): Scheduled date to add
        dry_run (bool): If True, show changes without applying
        create_backups (bool): Whether to create backup files

    Returns:
        int: Number of tasks updated
    """
    if not tasks:
        return 0

    # Group tasks by file
    tasks_by_file = {}
    for task in tasks:
        file_path = task['file']
        if file_path not in tasks_by_file:
            tasks_by_file[file_path] = []
        tasks_by_file[file_path].append(task)

    updated_count = 0
    vault_path = get_vault_path()

    for file_path, file_tasks in tasks_by_file.items():
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Show what would be changed
            if dry_run:
                print(f"\n{file_path.relative_to(vault_path)}:")
                for task in file_tasks:
                    new_desc = add_metadata_to_task(
                        task['description'],
                        context=context,
                        scheduled_date=scheduled_date
                    )
                    print(f"  Line {task['line_num']}:")
                    print(f"    Before: {task['description']}")
                    print(f"    After:  {new_desc}")
                updated_count += len(file_tasks)
                continue

            # Create backup if requested
            if create_backups:
                create_backup(file_path)

            # Update tasks (reverse order to preserve line numbers)
            for task in sorted(file_tasks, key=lambda t: t['line_num'], reverse=True):
                line_idx = task['line_num'] - 1
                original_line = lines[line_idx]

                # Parse the task line to get structure
                task_match = re.match(r'^(\s*- \[.\]\s+)(.*)$', original_line)
                if task_match:
                    prefix, description = task_match.groups()

                    # Update description with new metadata
                    new_description = add_metadata_to_task(
                        description.rstrip(),
                        context=context,
                        scheduled_date=scheduled_date
                    )

                    lines[line_idx] = f"{prefix}{new_description}\n"
                    updated_count += 1

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"Updated {len(file_tasks)} task(s) in {file_path.relative_to(vault_path)}")

        except Exception as e:
            print(f"Error updating {file_path}: {e}")

    return updated_count


def main():
    parser = argparse.ArgumentParser(
        description="Batch add context tags and scheduled dates to tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add @pc context to all tasks containing "research"
  python tools/add_context.py --context "@pc" --search "research"

  # Add @work context to tasks in specific file
  python tools/add_context.py --context "@work" --file GTD/Dashboard.md

  # Add context and schedule for next week
  python tools/add_context.py --context "@home" --search "clean" --scheduled +7

  # Preview changes without applying (dry run)
  python tools/add_context.py --context "@pc" --search "code" --dry-run

Scheduled date formats:
  - today       : Today's date
  - tomorrow    : Tomorrow's date
  - +N          : N days from now (e.g., +3)
  - YYYY-MM-DD  : Specific date
        """
    )

    parser.add_argument("--context", "-c", metavar="TAG",
                       help="Context tag to add (e.g., @pc, @work, @home)")
    parser.add_argument("--search", "-s", metavar="TERM",
                       help="Search term to match in task descriptions")
    parser.add_argument("--file", "-f", metavar="PATH",
                       help="File to search (relative to vault)")
    parser.add_argument("--scheduled", metavar="DATE",
                       help="Scheduled date to add (today, tomorrow, +N, YYYY-MM-DD)")
    parser.add_argument("--dry-run", "-n", action="store_true",
                       help="Preview changes without applying them")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't create backup files when updating tasks")

    args = parser.parse_args()

    # Validate arguments
    if not args.context and not args.scheduled:
        parser.error("At least one of --context or --scheduled is required")

    if not args.search and not args.file:
        parser.error("At least one of --search or --file is required")

    # Parse scheduled date if provided
    scheduled_date = None
    if args.scheduled:
        try:
            scheduled_date = parse_scheduled_date(args.scheduled)
        except ValueError as e:
            print(f"Error: {e}")
            return

    # Validate context tag
    if args.context:
        config = load_config()
        valid_contexts = config['settings']['available_contexts']
        if args.context not in valid_contexts:
            print(f"Warning: '{args.context}' is not in configured contexts: {', '.join(valid_contexts)}")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                return

    # Find tasks
    vault_path = get_vault_path()
    tasks = find_tasks_by_criteria(vault_path, search_term=args.search, file_filter=args.file)

    if not tasks:
        print("No tasks found matching criteria")
        return

    # Display found tasks
    print(f"Found {len(tasks)} task(s):")
    if args.dry_run:
        print("\n[DRY RUN - No changes will be made]")

    # Update tasks
    updated = update_tasks(
        tasks,
        context=args.context,
        scheduled_date=scheduled_date,
        dry_run=args.dry_run,
        create_backups=not args.no_backup
    )

    if args.dry_run:
        print(f"\n[DRY RUN] Would update {updated} task(s)")
        print("Run without --dry-run to apply changes")
    else:
        print(f"\nSuccessfully updated {updated} task(s)!")
        if not args.no_backup:
            print("Backup files created with .bak extension")


if __name__ == "__main__":
    main()
