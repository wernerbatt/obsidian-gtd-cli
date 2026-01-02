#!/usr/bin/env python3
"""
Interactive GTD processing for inbox items.

This tool guides you through the GTD clarify workflow:
1. What is it?
2. Is it actionable?
3. What's the next action?
4. Defer, delegate, or do?

Usage:
    python tools/process_item.py                      # Process all inbox items
    python tools/process_item.py --file GTD/PC.md --line 42  # Process specific task
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
    add_metadata_to_task,
    get_gtd_path
)


def get_user_input(prompt, options=None):
    """
    Get user input with optional validation.

    Args:
        prompt (str): Prompt to display
        options (list, optional): List of valid options

    Returns:
        str: User's input
    """
    while True:
        response = input(f"{prompt}: ").strip()

        if not response:
            continue

        if options:
            # Check if response matches any option (case-insensitive, first letter)
            for option in options:
                if response.lower() == option.lower() or response.lower() == option[0].lower():
                    return option

            print(f"Please choose from: {', '.join(options)}")
            continue

        return response


def get_context_tag():
    """
    Prompt user to select a context tag.

    Returns:
        str: Selected context tag (e.g., '@pc')
    """
    config = load_config()
    contexts = config['settings']['available_contexts']

    print("\nAvailable contexts:")
    for i, context in enumerate(contexts, 1):
        print(f"  {i}. {context}")

    while True:
        choice = input("\nSelect context (number or name): ").strip()

        # Try as number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(contexts):
                return contexts[idx]
        except ValueError:
            pass

        # Try as name (with or without @)
        if not choice.startswith('@'):
            choice = f'@{choice}'

        if choice in contexts:
            return choice

        print("Invalid choice. Please try again.")


def get_scheduled_date(prompt="When should you do this?"):
    """
    Prompt user for a scheduled date.

    Returns:
        str or None: Date in YYYY-MM-DD format, or None if not scheduled
    """
    print(f"\n{prompt}")
    print("  Options:")
    print("    - today")
    print("    - tomorrow")
    print("    - +N (days from now, e.g., +3)")
    print("    - YYYY-MM-DD (specific date)")
    print("    - <enter> to skip")

    while True:
        choice = input("\nScheduled date: ").strip().lower()

        if not choice:
            return None

        today = date.today()

        if choice == 'today':
            return str(today)
        elif choice == 'tomorrow':
            return str(today + timedelta(days=1))
        elif choice.startswith('+'):
            try:
                days = int(choice[1:])
                return str(today + timedelta(days=days))
            except ValueError:
                print("Invalid format. Use +N for days from now (e.g., +3)")
                continue
        else:
            # Try parsing as YYYY-MM-DD
            try:
                parsed = datetime.strptime(choice, '%Y-%m-%d').date()
                return str(parsed)
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD")
                continue


def process_task_interactive(file_path, line_num):
    """
    Interactive GTD processing for a single task.

    Args:
        file_path (Path): Path to file containing task
        line_num (int): Line number of task (1-indexed)

    Returns:
        bool: True if task was processed, False if skipped/cancelled
    """
    vault_path = get_vault_path()
    config = load_config()

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    # Get task line
    if line_num < 1 or line_num > len(lines):
        print(f"Invalid line number: {line_num}")
        return False

    task_line = lines[line_num - 1]
    task = parse_task_line(task_line, line_num)

    if not task:
        print(f"Line {line_num} is not a task")
        return False

    # Display task
    print(f"\n{'='*60}")
    print(f"File: {file_path.relative_to(vault_path)}")
    print(f"Line: {line_num}")
    print(f"Task: {task['description']}")
    print(f"{'='*60}\n")

    # GTD Processing Questions

    # 1. Clarify what it is
    print("1. What is it? (Clarify)")
    clarification = input("   Briefly describe what this is about (or press enter to skip): ").strip()

    # 2. Is it actionable?
    print("\n2. Is it actionable?")
    actionable = get_user_input("   Can you do something about this? (yes/no)", ['yes', 'no'])

    if actionable == 'no':
        # Not actionable - trash, reference, or someday/maybe
        print("\n   Not actionable. What should we do with it?")
        print("     1. Trash (delete it)")
        print("     2. Reference (note for later)")
        print("     3. Someday/Maybe (might do later)")
        print("     4. Cancel (keep as is)")

        choice = get_user_input("   Choice", ['1', '2', '3', '4'])

        if choice == '1':
            # Trash - delete the line
            if config['settings']['create_backups']:
                create_backup(file_path)

            del lines[line_num - 1]

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"\n✓ Task deleted from {file_path.relative_to(vault_path)}")
            return True

        elif choice == '2':
            print("\n   Consider creating a note in your References folder.")
            print(f"   Task will remain unchanged at {file_path.relative_to(vault_path)}:{line_num}")
            return False

        elif choice == '3':
            # Move to Someday Maybe
            someday_path = get_gtd_path('contexts', 'someday')

            if config['settings']['create_backups']:
                create_backup(file_path)

            # Remove from current file
            task_text = task['description']
            del lines[line_num - 1]

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            # Add to Someday Maybe
            with open(someday_path, 'a', encoding='utf-8') as f:
                f.write(f"- [ ] {task_text}\n")

            print(f"\n✓ Moved to {someday_path.relative_to(vault_path)}")
            return True

        else:
            print("\n   Cancelled. Task unchanged.")
            return False

    # Actionable - continue with processing
    print("\n3. What's the next action?")
    next_action = input("   Describe the specific, concrete next action: ").strip()

    if next_action:
        # Update description if user provided clarification
        task['description'] = next_action

    # 4. Can it be done in 2 minutes?
    print("\n4. Can you do it in 2 minutes or less?")
    two_minutes = get_user_input("   2-minute rule (yes/no)", ['yes', 'no'])

    if two_minutes == 'yes':
        print("\n   Do it now, then mark it as done!")
        mark_done = get_user_input("   Mark as done? (yes/no)", ['yes', 'no'])

        if mark_done == 'yes':
            if config['settings']['create_backups']:
                create_backup(file_path)

            # Mark task as done
            task_match = re.match(r'^(\s*)- \[.\]\s+(.*)$', task_line)
            if task_match:
                indent, desc = task_match.groups()
                # Add done date
                done_date = str(date.today())
                new_desc = add_metadata_to_task(task['description'], scheduled_date=None)
                lines[line_num - 1] = f"{indent}- [x] {new_desc} ✅ {done_date}\n"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                print(f"\n✓ Task marked as done in {file_path.relative_to(vault_path)}")
                return True

        return False

    # 5. Is it a project (multiple steps)?
    print("\n5. Is this a project (requires multiple steps)?")
    is_project = get_user_input("   Project? (yes/no)", ['yes', 'no'])

    if is_project == 'yes':
        print("\n   This looks like a project!")
        print("   Consider creating a project file in GTD/Projects/")
        print("   For now, we'll add a context tag to this next action.")

    # 6. Delegate or defer?
    print("\n6. Should you delegate or defer this?")
    print("   1. Defer (schedule for later)")
    print("   2. Delegate (assign to someone)")
    print("   3. Do ASAP (no specific date)")

    choice = get_user_input("   Choice", ['1', '2', '3'])

    context_tag = None
    scheduled_date = None

    if choice == '2':
        # Delegate
        person = input("\n   Who should do this?: ").strip()
        if person:
            task['description'] = f"{task['description']} @waiting-{person}"
        context_tag = '@waiting'

    elif choice == '1' or choice == '3':
        # Defer or Do ASAP - need context tag
        context_tag = get_context_tag()

        if choice == '1':
            # Defer - get scheduled date
            scheduled_date = get_scheduled_date()

    # Update the task
    if config['settings']['create_backups']:
        create_backup(file_path)

    # Build new description
    new_desc = task['description']
    new_desc = add_metadata_to_task(new_desc, context=context_tag, scheduled_date=scheduled_date)

    # Update line
    task_match = re.match(r'^(\s*)- \[.\]\s+(.*)$', task_line)
    if task_match:
        indent = task_match.group(1)
        lines[line_num - 1] = f"{indent}- [ ] {new_desc}\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"\n✓ Task processed and updated in {file_path.relative_to(vault_path)}:{line_num}")
        print(f"   Context: {context_tag or 'none'}")
        if scheduled_date:
            print(f"   Scheduled: {scheduled_date}")

        return True

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Interactive GTD processing for inbox items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
GTD Processing Questions:
  1. What is it? (Clarify)
  2. Is it actionable?
  3. If YES: What's the next action?
  4. Can it be done in 2 minutes?
  5. Is it a project (multiple steps)?
  6. Defer, delegate, or do?

Examples:
  python tools/process_item.py --file GTD/Dashboard.md --line 42
        """
    )

    parser.add_argument("--file", "-f", required=True,
                       help="File containing task (relative to vault)")
    parser.add_argument("--line", "-l", type=int, required=True,
                       help="Line number of task (1-indexed)")

    args = parser.parse_args()

    # Get vault path and construct file path
    vault_path = get_vault_path()
    file_path = vault_path / args.file

    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return

    # Process the task
    process_task_interactive(file_path, args.line)


if __name__ == "__main__":
    main()
