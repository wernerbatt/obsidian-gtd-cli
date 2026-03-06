#!/usr/bin/env python3
"""
Generate GTD weekly review reports via the official Obsidian CLI.

Usage:
    python tools/weekly_review.py
    python tools/weekly_review.py --output review.md
    python tools/weekly_review.py --stale-projects
"""

import argparse
from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path

from gtd_common import (
    get_vault_path,
    load_config,
    get_gtd_path,
    parse_task_from_cli,
    task_matches_inbox,
    extract_context_tags,
)
import obsidian_cli as obs


def count_inbox_items():
    """Count tasks matching inbox criteria via CLI."""
    raw = obs.tasks_todo(verbose=True, as_json=True)
    tasks = [parse_task_from_cli(item) for item in raw]
    return sum(1 for t in tasks if task_matches_inbox(t))


def count_tasks_by_context():
    """Count active tasks by context tag via CLI."""
    config = load_config()
    contexts = config['settings']['available_contexts']
    counts = defaultdict(int)

    raw = obs.tasks_todo(verbose=True, as_json=True)
    for item in raw:
        task = parse_task_from_cli(item)
        if task['is_done']:
            continue
        for ctx in extract_context_tags(task['description']):
            if ctx in contexts:
                counts[ctx] += 1

    return dict(counts)


def find_overdue_tasks():
    """Find tasks with scheduled/due dates before today."""
    today = date.today()
    overdue = []

    raw = obs.tasks_todo(verbose=True, as_json=True)
    for item in raw:
        task = parse_task_from_cli(item)
        if task['is_done'] or task.get('priority') == '⏬':
            continue

        is_overdue = False
        if task['scheduled_date'] and task['scheduled_date'] < today:
            is_overdue = True
        elif task['due_date'] and task['due_date'] < today:
            is_overdue = True

        if is_overdue:
            overdue.append({
                'file': task['file'],
                'line': task['line_num'],
                'description': task['description'],
                'scheduled': task['scheduled_date'],
                'due': task['due_date'],
            })

    return overdue


def find_projects_without_actions():
    """Find project files without active next actions."""
    config = load_config()
    vault_path = get_vault_path()
    projects_folder = get_gtd_path('projects_folder')
    stale = []

    if not projects_folder.exists():
        return stale

    # Get all todo tasks and index by file
    raw = obs.tasks_todo(verbose=True, as_json=True)
    tasks_by_file = defaultdict(int)
    for item in raw:
        tasks_by_file[item.get('file', '')] += 1

    # Check each project file
    projects_rel = config['gtd']['projects_folder']
    for project_file in projects_folder.glob("*.md"):
        rel = f"{projects_rel}/{project_file.name}"
        if tasks_by_file.get(rel, 0) == 0:
            stale.append(project_file.name)

    return stale


def find_completed_tasks(days=7):
    """Find tasks completed in the last N days."""
    cutoff = date.today() - timedelta(days=days)
    completed = []

    raw = obs.tasks_done(verbose=True, as_json=True)
    for item in raw:
        task = parse_task_from_cli(item)
        if task['done_date'] and task['done_date'] >= cutoff:
            completed.append({
                'file': task['file'],
                'description': task['description'],
                'done_date': task['done_date'],
            })

    completed.sort(key=lambda x: x['done_date'], reverse=True)
    return completed


def generate_review_report():
    """Generate comprehensive weekly review report."""
    config = load_config()
    today = date.today()

    inbox_count = count_inbox_items()
    context_counts = count_tasks_by_context()
    overdue = find_overdue_tasks()
    stale_projects = find_projects_without_actions()
    completed = find_completed_tasks(days=7)

    contexts = config['settings']['available_contexts']
    total_tasks = sum(context_counts.values())

    report = f"""# Weekly Review - {today}

## Get Clear

**Inbox Status:**
- [ ] Items to process: **{inbox_count}**
- [ ] Review recent daily notes for loose tasks
- [ ] Clear downloads folder
- [ ] Clear physical inboxes (desk, bag, etc.)

## Get Current

### Context Review

**Active Tasks by Context:**
"""

    for ctx in contexts:
        count = context_counts.get(ctx, 0)
        report += f"- {ctx}: {count} task(s)\n"

    report += f"\n**Total active tasks:** {total_tasks}\n"

    report += "\n### Overdue Tasks\n\n"
    if overdue:
        report += f"**{len(overdue)} overdue task(s):**\n\n"
        for task in overdue[:10]:
            date_info = ""
            if task['scheduled']:
                date_info = f"(Scheduled: {task['scheduled']})"
            elif task['due']:
                date_info = f"(Due: {task['due']})"
            report += f"- {task['description']} {date_info}\n"
            report += f"  - {task['file']}:{task['line']}\n"
        if len(overdue) > 10:
            report += f"\n*...and {len(overdue) - 10} more*\n"
    else:
        report += "No overdue tasks. Good job!\n"

    report += "\n### Projects Review\n\n"
    report += "- [ ] Review all active projects\n"
    report += "- [ ] Ensure each project has at least one next action\n"

    if stale_projects:
        report += f"\n**⚠️ Projects without next actions ({len(stale_projects)}):**\n\n"
        for p in stale_projects:
            report += f"- {p.replace('.md', '')}\n"
    else:
        report += "\nAll projects have next actions!\n"

    report += """
### Calendar Review

- [ ] Review past week (what happened?)
- [ ] Review upcoming week (what's coming?)
- [ ] Review next month (future commitments)

### Waiting For

- [ ] Review @waiting items
- [ ] Follow up on pending responses

## Get Creative

- [ ] Review Someday/Maybe list
- [ ] Any new projects or ideas?
- [ ] Review ponderables

## Completed This Week

"""

    if completed:
        report += f"**{len(completed)} task(s) completed:**\n\n"
        for task in completed[:20]:
            report += f"- {task['description']} ✅ {task['done_date']}\n"
        if len(completed) > 20:
            report += f"\n*...and {len(completed) - 20} more*\n"
    else:
        report += "No completed tasks tracked this week.\n"

    report += f"\n---\n\n*Generated by Obsidian GTD CLI - {today}*\n"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate GTD weekly review report (via Obsidian CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/weekly_review.py
  python tools/weekly_review.py --output "Weekly Review.md"
  python tools/weekly_review.py --stale-projects
        """
    )

    parser.add_argument("--output", "-o", metavar="FILE",
                        help="Save report to file (relative to vault)")
    parser.add_argument("--stale-projects", action="store_true",
                        help="Show only projects without next actions")

    args = parser.parse_args()

    if args.stale_projects:
        stale = find_projects_without_actions()
        print(f"Projects without next actions: {len(stale)}")
        for p in stale:
            print(f"  - {p.replace('.md', '')}")
        return

    report = generate_review_report()

    if args.output:
        vault_path = get_vault_path()
        output_path = vault_path / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Weekly review saved to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
