#!/usr/bin/env python3
"""
Batch add context tags, scheduled dates, or priority to tasks.

Uses Obsidian CLI tasks query for discovery, direct file I/O for
line-level edits (no CLI equivalent).

Usage:
    python tools/add_context.py --context "@quick" --search "research"
    python tools/add_context.py --context "@out" --file GTD/Dashboard.md
    python tools/add_context.py --context "@deep" --search "code" --dry-run
    python tools/add_context.py --search "maybe" --priority "⏬"
"""

import argparse
import re
from collections import defaultdict

from gtd_common import (
    get_vault_path,
    load_config,
    parse_task_line,
    add_metadata_to_task,
    parse_date_string,
)
import obsidian_cli as obs


def find_tasks_by_criteria(search_term=None, file_filter=None):
    """
    Find open tasks matching criteria via Obsidian CLI.

    Returns list of dicts with: file, line_num, description, original_line.
    """
    vault_path = get_vault_path()
    tasks = []

    if file_filter:
        # Read a specific file and scan for tasks
        content = obs.read_file(path=file_filter)
        for line_num, line in enumerate(content.splitlines(), 1):
            task = parse_task_line(line + '\n', line_num)
            if not task or task['is_done']:
                continue
            if search_term and search_term.lower() not in task['description'].lower():
                continue
            tasks.append({
                'file': file_filter,
                'line_num': line_num,
                'description': task['description'],
                'original_line': line + '\n',
            })
    else:
        # Use CLI tasks query then filter by search term
        raw = obs.tasks_todo(verbose=True, as_json=True)
        for item in raw:
            text = item.get('text', '')
            task = parse_task_line(text, int(item.get('line', 0)))
            if not task:
                continue
            if search_term and search_term.lower() not in task['description'].lower():
                continue
            tasks.append({
                'file': item.get('file', ''),
                'line_num': int(item.get('line', 0)),
                'description': task['description'],
                'original_line': text + '\n',
            })

    return tasks


def update_tasks(tasks, *, context=None, scheduled_date=None, priority=None,
                 dry_run=False):
    """
    Update tasks with context tag, scheduled date, and/or priority.

    Direct file I/O for line-level edits.
    """
    if not tasks:
        return 0

    vault_path = get_vault_path()
    tasks_by_file = defaultdict(list)
    for t in tasks:
        tasks_by_file[t['file']].append(t)

    updated = 0

    for file_rel, file_tasks in tasks_by_file.items():
        file_path = vault_path / file_rel

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if dry_run:
            print(f"\n{file_rel}:")
            for t in file_tasks:
                new_desc = add_metadata_to_task(
                    t['description'], context=context,
                    scheduled_date=scheduled_date, priority=priority,
                )
                print(f"  Line {t['line_num']}:")
                print(f"    Before: {t['description']}")
                print(f"    After:  {new_desc}")
            updated += len(file_tasks)
            continue

        for t in sorted(file_tasks, key=lambda x: x['line_num'], reverse=True):
            idx = t['line_num'] - 1
            task_match = re.match(r'^(\s*- \[.\]\s+)(.*)$', lines[idx])
            if task_match:
                prefix, description = task_match.groups()
                new_desc = add_metadata_to_task(
                    description.rstrip(), context=context,
                    scheduled_date=scheduled_date, priority=priority,
                )
                lines[idx] = f"{prefix}{new_desc}\n"
                updated += 1

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"Updated {len(file_tasks)} task(s) in {file_rel}")

    return updated


def main():
    parser = argparse.ArgumentParser(
        description="Batch add context tags and scheduled dates to tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/add_context.py --context "@quick" --search "research"
  python tools/add_context.py --context "@out" --file GTD/Dashboard.md
  python tools/add_context.py --search "maybe" --priority "⏬"
  python tools/add_context.py --context "@deep" --search "code" --dry-run

Date formats: today, tomorrow, +N (days), YYYY-MM-DD
Priority symbols: ⏫ highest, 🔼 high, 🔽 low, ⏬ lowest
        """
    )

    parser.add_argument("--context", "-c", metavar="TAG",
                        help="Context tag to add")
    parser.add_argument("--search", "-s", metavar="TERM",
                        help="Search term to match in task descriptions")
    parser.add_argument("--file", "-f", metavar="PATH",
                        help="File to search (relative to vault)")
    parser.add_argument("--scheduled", metavar="DATE",
                        help="Scheduled date to add")
    parser.add_argument("--priority", "-p", metavar="SYMBOL",
                        help="Priority symbol to add")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Preview changes without applying")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting")

    args = parser.parse_args()

    if not args.context and not args.scheduled and not args.priority:
        parser.error("At least one of --context, --scheduled, or --priority is required")
    if not args.search and not args.file:
        parser.error("At least one of --search or --file is required")

    valid_priorities = ['⏫', '🔼', '🔽', '⏬']
    if args.priority and args.priority not in valid_priorities:
        print(f"Error: Invalid priority '{args.priority}'. Valid: {', '.join(valid_priorities)}")
        return

    scheduled_date = parse_date_string(args.scheduled) if args.scheduled else None

    if args.context:
        config = load_config()
        valid_contexts = config['settings']['available_contexts']
        if args.context not in valid_contexts:
            print(f"Warning: '{args.context}' is not in configured contexts: {', '.join(valid_contexts)}")
            if not args.yes:
                response = input("Continue anyway? (yes/no): ")
                if response.lower() not in ('yes', 'y'):
                    return

    tasks = find_tasks_by_criteria(search_term=args.search, file_filter=args.file)

    if not tasks:
        print("No tasks found matching criteria")
        return

    print(f"Found {len(tasks)} task(s):")
    if args.dry_run:
        print("\n[DRY RUN - No changes will be made]")

    updated = update_tasks(
        tasks, context=args.context,
        scheduled_date=scheduled_date,
        priority=args.priority,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print(f"\n[DRY RUN] Would update {updated} task(s)")
    else:
        print(f"\nSuccessfully updated {updated} task(s)!")


if __name__ == "__main__":
    main()
