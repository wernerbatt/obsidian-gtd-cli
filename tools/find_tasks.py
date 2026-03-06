#!/usr/bin/env python3
"""
Find tasks in Obsidian vault via the official Obsidian CLI.

Queries:
  inbox   – tasks needing GTD processing (no context, unblocked, not future-scheduled)
  someday – lowest-priority (⏬) or @someday tasks
  tag     – active tasks matching a context tag (e.g. @quick, @deep)
  all     – every open task

Usage:
    python tools/find_tasks.py --query inbox
    python tools/find_tasks.py --query tag --tag @quick
    python tools/find_tasks.py --query tag --tag @quick --verbose
    python tools/find_tasks.py --query someday --export someday.txt
    python tools/find_tasks.py --query all --limit 20
"""

import argparse
import re
from datetime import datetime, date

from gtd_common import (
    parse_task_from_cli,
    task_matches_inbox,
    task_matches_tag,
    task_matches_someday,
)
import obsidian_cli as obs


# ---------------------------------------------------------------------------
# Core search — pulls from Obsidian CLI, then filters in Python
# ---------------------------------------------------------------------------

def find_tasks(query_type='inbox', tag=None, limit=None):
    """Return tasks matching *query_type* via Obsidian CLI."""
    raw = obs.tasks_todo(verbose=True, as_json=True)
    tasks = [parse_task_from_cli(item) for item in raw]

    # Apply filter
    if query_type == 'inbox':
        tasks = [t for t in tasks if task_matches_inbox(t)]
    elif query_type == 'someday':
        tasks = [t for t in tasks if task_matches_someday(t)]
    elif query_type == 'tag':
        tasks = [t for t in tasks if task_matches_tag(t, tag)]
    elif query_type == 'all':
        pass  # all open tasks already

    tasks = _sort_tasks(tasks, query_type)

    if limit:
        tasks = tasks[:limit]

    return tasks


def _sort_tasks(tasks, query_type):
    """Sort results: tag queries by priority desc, others by path desc."""
    if query_type == 'tag':
        order = {'🔺': 5, '⏫': 4, '🔼': 3, None: 2, '🔽': 1, '⏬': 0}
        tasks.sort(key=lambda t: (order.get(t['priority'], 2), t['file']), reverse=True)
    else:
        tasks.sort(key=lambda t: t['file'], reverse=True)
    return tasks


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
        if task['file'] != current_file:
            current_file = task['file']
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
            if task['file'] != current_file:
                current_file = task['file']
                f.write(f"\n## {current_file}\n\n")
            f.write(f"- [ ] {task['description']}\n")
            f.write(f"  - File: {task['file']}\n")
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
        description="Find tasks in Obsidian vault (via Obsidian CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/find_tasks.py --query inbox
  python tools/find_tasks.py --query someday
  python tools/find_tasks.py --query tag --tag @quick
  python tools/find_tasks.py --query tag --tag @quick --verbose
  python tools/find_tasks.py --query all --limit 20
  python tools/find_tasks.py --query someday --export someday.txt
        """,
    )

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

    args = parser.parse_args()

    if args.query == 'tag' and not args.tag:
        parser.error("--tag is required when using --query tag")

    tasks = find_tasks(args.query, tag=args.tag, limit=args.limit)

    if args.export:
        export_tasks(tasks, args.export, args.query.title())
        return

    display_tasks(tasks, args.query, verbose=args.verbose)


if __name__ == "__main__":
    main()
