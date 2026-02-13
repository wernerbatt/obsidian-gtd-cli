#!/usr/bin/env python3
"""
Find tasks in Obsidian vault.

Canonical source: obsidian-cli/tools/find_tasks.py
Last synced: 2026-02-10

Queries:
  - inbox:   tasks needing GTD processing (no context, unblocked, not scheduled future)
  - someday: lowest-priority (⏬) or @someday tasks
  - tag:     active tasks matching a context tag (e.g. @quick, @deep)
  - all:     every open task

Usage:
    python tools/find_tasks.py --query inbox
    python tools/find_tasks.py --query tag --tag @quick
    python tools/find_tasks.py --query tag --tag @quick --verbose
    python tools/find_tasks.py --query someday --export someday.txt
    python tools/find_tasks.py --query all --limit 20
    python tools/find_tasks.py --query inbox --set-scheduled 2026-03-01
"""

import argparse
from pathlib import Path
from datetime import datetime, date
import re

from gtd_common import (
    get_vault_path,
    load_config,
    parse_task_line,
    task_matches_to_process_criteria,
)


# ---------------------------------------------------------------------------
# Query filters
# ---------------------------------------------------------------------------

def matches_tag_criteria(task, tag):
    """Active tasks with a given context tag (excludes ⏬, blocked, done)."""
    desc = task['description']

    if tag not in desc:
        return False
    if task['is_done']:
        return False
    if task['is_blocked']:
        return False
    if task.get('priority') == '⏬':
        return False

    today = date.today()
    due = task['due_date']
    scheduled = task['scheduled_date']

    # Show if: due/scheduled today-or-past, OR no date at all
    if due is not None and due > today:
        return False
    if scheduled is not None and scheduled > today:
        return False

    return True


def matches_someday_criteria(task, file_path):
    """Someday/Maybe: ⏬ priority or @someday tag."""
    if task['is_done']:
        return False
    desc = task['description']
    return task.get('priority') == '⏬' or '@someday' in desc


# ---------------------------------------------------------------------------
# Core search
# ---------------------------------------------------------------------------

def find_tasks(vault_path, query_type='inbox', tag=None, limit=None):
    """Walk vault and return tasks matching *query_type*."""
    tasks = []

    for md_file in sorted(vault_path.rglob("*.md")):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue

        for line_num, line in enumerate(lines, 1):
            task = parse_task_line(line, line_num)
            if not task:
                continue

            # Apply filter
            if query_type == 'inbox':
                if not task_matches_to_process_criteria(task, md_file):
                    continue
            elif query_type == 'someday':
                if not matches_someday_criteria(task, md_file):
                    continue
            elif query_type == 'tag':
                if not matches_tag_criteria(task, tag):
                    continue
            elif query_type == 'all':
                if task['is_done']:
                    continue

            tasks.append({
                'file': md_file,
                'file_relative': md_file.relative_to(vault_path),
                'line_num': line_num,
                'description': task['description'],
                'due_date': task['due_date'],
                'scheduled_date': task['scheduled_date'],
                'priority': task.get('priority'),
            })

            if limit and len(tasks) >= limit:
                return _sort_tasks(tasks, query_type)

    return _sort_tasks(tasks, query_type)


def _sort_tasks(tasks, query_type):
    """Sort results: tag queries by priority desc, others by path desc."""
    if query_type == 'tag':
        priority_order = {'⏫': 5, '🔺': 4, '🔼': 3, None: 2, '🔽': 1, '⏬': 0}
        tasks.sort(
            key=lambda t: (priority_order.get(t['priority'], 2), str(t['file_relative'])),
            reverse=True,
        )
    else:
        tasks.sort(key=lambda t: str(t['file_relative']), reverse=True)
    return tasks


# ---------------------------------------------------------------------------
# Batch update: --set-scheduled
# ---------------------------------------------------------------------------

def update_tasks_with_scheduled_date(tasks, scheduled_date_str, vault_path, create_backup=True):
    """Set ⏳ date on every task in *tasks*."""
    import shutil

    tasks_by_file = {}
    for task in tasks:
        tasks_by_file.setdefault(task['file'], []).append(task)

    updated = 0
    for file_path, file_tasks in tasks_by_file.items():
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if create_backup:
            shutil.copy2(file_path, file_path.with_suffix('.md.bak'))

        for task in sorted(file_tasks, key=lambda t: t['line_num'], reverse=True):
            idx = task['line_num'] - 1
            m = re.match(r'^(\s*- \[.\]\s+)(.*)$', lines[idx])
            if m:
                prefix, desc = m.groups()
                desc = re.sub(r'⏳\s*\d{4}-\d{2}-\d{2}', '', desc).strip()
                lines[idx] = f"{prefix}{desc} ⏳ {scheduled_date_str}\n"
                updated += 1

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Updated {len(file_tasks)} task(s) in {file_path.relative_to(vault_path)}")

    return updated


# ---------------------------------------------------------------------------
# Display / export
# ---------------------------------------------------------------------------

def display_tasks(tasks, label, verbose=False):
    print(f"Found {len(tasks)} {label} task(s):\n")
    if not tasks:
        print(f"No {label} tasks found.")
        return

    current_file = None
    for task in tasks:
        if task['file_relative'] != current_file:
            current_file = task['file_relative']
            print(f"\n{current_file}:")

        parts = [f"  Line {task['line_num']}: {task['description']}"]
        if verbose:
            if task.get('priority'):
                parts.append(f"[Priority: {task['priority']}]")
            if task['due_date']:
                parts.append(f"[Due: {task['due_date']}]")
            if task['scheduled_date']:
                parts.append(f"[Scheduled: {task['scheduled_date']}]")
        print(' '.join(parts))


def export_tasks(tasks, export_path, label):
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(f"# {label} Tasks ({len(tasks)} items)\n\n")
        current_file = None
        for task in tasks:
            if task['file_relative'] != current_file:
                current_file = task['file_relative']
                f.write(f"\n## {current_file}\n\n")
            f.write(f"- [ ] {task['description']}\n")
            f.write(f"  - File: {task['file_relative']}\n")
            f.write(f"  - Line: {task['line_num']}\n")
            if task['due_date']:
                f.write(f"  - Due: {task['due_date']}\n")
            if task['scheduled_date']:
                f.write(f"  - Scheduled: {task['scheduled_date']}\n")
            f.write("\n")
    print(f"\nExported {len(tasks)} tasks to: {export_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Find tasks in Obsidian vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/find_tasks.py --query inbox
  python tools/find_tasks.py --query someday
  python tools/find_tasks.py --query tag --tag @quick
  python tools/find_tasks.py --query tag --tag @quick --verbose
  python tools/find_tasks.py --query all --limit 20
  python tools/find_tasks.py --query inbox --set-scheduled 2026-03-01
  python tools/find_tasks.py --query someday --export someday.txt
        """,
    )

    # Keep short aliases for backward compat: -m works like --mode did
    parser.add_argument(
        "--query", "-q", "-m", "--mode",
        default="inbox",
        choices=["inbox", "someday", "tag", "all"],
        help="Query type (default: inbox)",
    )
    parser.add_argument("--tag", metavar="TAG",
                        help="Context tag for --query tag (e.g. @quick)")
    parser.add_argument("--verbose", "-v", "--show-details", "-d",
                        action="store_true",
                        help="Show priority, dates, and line numbers")
    parser.add_argument("--limit", "-l", type=int, metavar="N",
                        help="Maximum tasks to return")
    parser.add_argument("--export", "-e", metavar="FILE",
                        help="Export tasks to file")
    parser.add_argument("--set-scheduled", metavar="DATE",
                        help="Set ⏳ date on found tasks (YYYY-MM-DD)")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip .bak files when using --set-scheduled")

    args = parser.parse_args()

    if args.query == 'tag' and not args.tag:
        parser.error("--tag is required when using --query tag")

    vault_path = get_vault_path()
    tasks = find_tasks(vault_path, args.query, tag=args.tag, limit=args.limit)

    # Batch-update mode
    if args.set_scheduled:
        try:
            datetime.strptime(args.set_scheduled, '%Y-%m-%d')
        except ValueError:
            parser.error(f"Invalid date format '{args.set_scheduled}'. Use YYYY-MM-DD")
        print(f"Setting ⏳ {args.set_scheduled} on {len(tasks)} tasks...\n")
        n = update_tasks_with_scheduled_date(
            tasks, args.set_scheduled, vault_path,
            create_backup=not args.no_backup,
        )
        print(f"\nUpdated {n} tasks.")
        return

    # Export mode
    if args.export:
        export_tasks(tasks, args.export, args.query.title())
        return

    # Display mode
    display_tasks(tasks, args.query, verbose=args.verbose)


if __name__ == "__main__":
    main()
