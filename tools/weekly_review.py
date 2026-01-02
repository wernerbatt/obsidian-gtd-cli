#!/usr/bin/env python3
"""
Generate GTD weekly review reports.

The weekly review is a core GTD practice to keep your system current and
maintain perspective on your projects and commitments.

Usage:
    python tools/weekly_review.py                        # Display to terminal
    python tools/weekly_review.py --output review.md     # Save to file
    python tools/weekly_review.py --stale-projects       # Show projects without next actions
"""

import argparse
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict
from gtd_common import (
    get_vault_path,
    load_config,
    get_gtd_path,
    parse_task_line,
    extract_context_tags
)


def count_inbox_items(vault_path):
    """
    Count tasks matching "To Process" criteria.

    Args:
        vault_path (Path): Path to Obsidian vault

    Returns:
        int: Number of inbox items
    """
    from gtd_common import task_matches_to_process_criteria

    count = 0

    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if task and task_matches_to_process_criteria(task, md_file):
                    count += 1

        except Exception:
            pass

    return count


def count_tasks_by_context(vault_path, config):
    """
    Count active tasks by context tag.

    Args:
        vault_path (Path): Path to Obsidian vault
        config (dict): Configuration dictionary

    Returns:
        dict: Dictionary mapping context tags to counts
    """
    context_counts = defaultdict(int)
    contexts = config['settings']['available_contexts']

    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                task = parse_task_line(line, 1)
                if not task or task['is_done']:
                    continue

                # Count by context
                task_contexts = extract_context_tags(task['description'])
                for context in task_contexts:
                    if context in contexts:
                        context_counts[context] += 1

        except Exception:
            pass

    return dict(context_counts)


def find_overdue_tasks(vault_path):
    """
    Find tasks with scheduled or due dates before today.

    Args:
        vault_path (Path): Path to Obsidian vault

    Returns:
        list: List of overdue task dictionaries
    """
    overdue = []
    today = date.today()

    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if not task or task['is_done']:
                    continue

                # Check if overdue
                is_overdue = False
                if task['scheduled_date'] and task['scheduled_date'] < today:
                    is_overdue = True
                elif task['due_date'] and task['due_date'] < today:
                    is_overdue = True

                if is_overdue:
                    overdue.append({
                        'file': md_file.relative_to(vault_path),
                        'line': line_num,
                        'description': task['description'],
                        'scheduled': task['scheduled_date'],
                        'due': task['due_date']
                    })

        except Exception:
            pass

    return overdue


def find_projects_without_actions(vault_path, config):
    """
    Find project files without any active next actions.

    Args:
        vault_path (Path): Path to Obsidian vault
        config (dict): Configuration dictionary

    Returns:
        list: List of project file names
    """
    projects_folder = get_gtd_path('projects_folder')
    stale_projects = []

    if not projects_folder.exists():
        return stale_projects

    for project_file in projects_folder.glob("*.md"):
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Count active (not done) tasks
            active_tasks = 0
            for line in lines:
                task = parse_task_line(line, 1)
                if task and not task['is_done']:
                    active_tasks += 1

            if active_tasks == 0:
                stale_projects.append(project_file.name)

        except Exception:
            pass

    return stale_projects


def find_completed_tasks(vault_path, days=7):
    """
    Find tasks completed in the last N days.

    Args:
        vault_path (Path): Path to Obsidian vault
        days (int): Number of days to look back

    Returns:
        list: List of completed task dictionaries
    """
    completed = []
    cutoff_date = date.today() - timedelta(days=days)

    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if not task or not task['is_done']:
                    continue

                # Check done date
                if task['done_date'] and task['done_date'] >= cutoff_date:
                    completed.append({
                        'file': md_file.relative_to(vault_path),
                        'description': task['description'],
                        'done_date': task['done_date']
                    })

        except Exception:
            pass

    # Sort by done date
    completed.sort(key=lambda x: x['done_date'], reverse=True)

    return completed


def generate_review_report(vault_path, config):
    """
    Generate comprehensive weekly review report.

    Args:
        vault_path (Path): Path to Obsidian vault
        config (dict): Configuration dictionary

    Returns:
        str: Markdown formatted report
    """
    today = date.today()

    # Gather data
    inbox_count = count_inbox_items(vault_path)
    context_counts = count_tasks_by_context(vault_path, config)
    overdue = find_overdue_tasks(vault_path)
    stale_projects = find_projects_without_actions(vault_path, config)
    completed = find_completed_tasks(vault_path, days=7)

    # Build report
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

    # Add context counts
    contexts = config['settings']['available_contexts']
    total_tasks = sum(context_counts.values())

    for context in contexts:
        count = context_counts.get(context, 0)
        report += f"- {context}: {count} task(s)\n"

    report += f"\n**Total active tasks:** {total_tasks}\n"

    # Overdue tasks
    report += f"\n### Overdue Tasks\n\n"
    if overdue:
        report += f"**{len(overdue)} overdue task(s):**\n\n"
        for task in overdue[:10]:  # Limit to 10
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

    # Projects review
    report += f"\n### Projects Review\n\n"
    report += f"- [ ] Review all active projects\n"
    report += f"- [ ] Ensure each project has at least one next action\n"

    if stale_projects:
        report += f"\n**⚠️ Projects without next actions ({len(stale_projects)}):**\n\n"
        for project in stale_projects:
            report += f"- {project.replace('.md', '')}\n"
    else:
        report += f"\nAll projects have next actions!\n"

    # Calendar review
    report += f"\n### Calendar Review\n\n"
    report += f"- [ ] Review past week (what happened?)\n"
    report += f"- [ ] Review upcoming week (what's coming?)\n"
    report += f"- [ ] Review next month (future commitments)\n"

    # Waiting for
    report += f"\n### Waiting For\n\n"
    report += f"- [ ] Review @waiting items\n"
    report += f"- [ ] Follow up on pending responses\n"

    # Get Creative
    report += f"\n## Get Creative\n\n"
    report += f"- [ ] Review Someday/Maybe list\n"
    report += f"- [ ] Any new projects or ideas?\n"
    report += f"- [ ] Review ponderables\n"

    # Completed this week
    report += f"\n## Completed This Week\n\n"
    if completed:
        report += f"**{len(completed)} task(s) completed:**\n\n"
        for task in completed[:20]:  # Limit to 20
            report += f"- {task['description']} ✅ {task['done_date']}\n"

        if len(completed) > 20:
            report += f"\n*...and {len(completed) - 20} more*\n"
    else:
        report += "No completed tasks tracked this week.\n"

    # Footer
    report += f"\n---\n\n"
    report += f"*Generated by Obsidian GTD CLI - {today}*\n"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate GTD weekly review report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The weekly review is essential for maintaining your GTD system.
This tool helps you review:
- Inbox items to process
- Active tasks by context
- Overdue tasks
- Projects without next actions
- Completed tasks from the past week

Examples:
  # Display review to terminal
  python tools/weekly_review.py

  # Save review to file
  python tools/weekly_review.py --output "Weekly Review 2026-01-02.md"

  # Show only projects without next actions
  python tools/weekly_review.py --stale-projects

  # Open review in Obsidian after generation
  python tools/weekly_review.py --output review.md --open
        """
    )

    parser.add_argument("--output", "-o", metavar="FILE",
                       help="Save report to file (relative to vault)")
    parser.add_argument("--stale-projects", action="store_true",
                       help="Show only projects without next actions")
    parser.add_argument("--open", action="store_true",
                       help="Open file in Obsidian after generation (requires --output)")

    args = parser.parse_args()

    vault_path = get_vault_path()
    config = load_config()

    # Stale projects only
    if args.stale_projects:
        stale = find_projects_without_actions(vault_path, config)
        print(f"Projects without next actions: {len(stale)}")
        for project in stale:
            print(f"  - {project.replace('.md', '')}")
        return

    # Generate full report
    report = generate_review_report(vault_path, config)

    # Output
    if args.output:
        output_path = vault_path / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Weekly review saved to: {args.output}")

        # Open in Obsidian
        if args.open:
            import subprocess
            import platform

            obsidian_uri = f"obsidian://open?vault=Obsidian&file={args.output}"

            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", obsidian_uri])
            elif platform.system() == "Windows":
                subprocess.run(["start", obsidian_uri], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", obsidian_uri])

    else:
        # Print to terminal
        print(report)


if __name__ == "__main__":
    main()
