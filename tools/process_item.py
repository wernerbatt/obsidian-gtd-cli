#!/usr/bin/env python3
"""
Interactive GTD processing for inbox items.

Guides you through the GTD clarify workflow:
1. What is it?
2. Is it actionable?
3. What's the next action?
4. Defer, delegate, or do?

Usage:
    python tools/process_item.py --file GTD/Dashboard.md --line 42
"""

import argparse
import re
from datetime import date, timedelta

from gtd_common import (
    get_vault_path,
    load_config,
    parse_task_line,
    add_metadata_to_task,
    parse_date_string,
)
import obsidian_cli as obs


def get_user_input(prompt, options=None):
    """Get user input with optional validation."""
    while True:
        response = input(f"{prompt}: ").strip()
        if not response:
            continue
        if options:
            for option in options:
                if response.lower() == option.lower() or response.lower() == option[0].lower():
                    return option
            print(f"Please choose from: {', '.join(options)}")
            continue
        return response


def get_context_tag():
    """Prompt user to select a context tag."""
    config = load_config()
    contexts = config['settings']['available_contexts']

    print("\nAvailable contexts:")
    for i, ctx in enumerate(contexts, 1):
        print(f"  {i}. {ctx}")

    while True:
        choice = input("\nSelect context (number or name): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(contexts):
                return contexts[idx]
        except ValueError:
            pass
        if not choice.startswith('@'):
            choice = f'@{choice}'
        if choice in contexts:
            return choice
        print("Invalid choice. Please try again.")


def get_scheduled_date(prompt="When should you do this?"):
    """Prompt user for a scheduled date."""
    print(f"\n{prompt}")
    print("  Options: today | tomorrow | +N | YYYY-MM-DD | <enter> to skip")

    while True:
        choice = input("\nScheduled date: ").strip()
        if not choice:
            return None
        try:
            return parse_date_string(choice)
        except (ValueError, KeyError):
            print("Invalid date format. Try again.")


def process_task_interactive(file_rel, line_num):
    """Interactive GTD processing for a single task."""
    vault_path = get_vault_path()
    file_path = vault_path / file_rel

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if line_num < 1 or line_num > len(lines):
        print(f"Invalid line number: {line_num}")
        return False

    task_line = lines[line_num - 1]
    task = parse_task_line(task_line, line_num)

    if not task:
        print(f"Line {line_num} is not a task")
        return False

    print(f"\n{'='*60}")
    print(f"File: {file_rel}")
    print(f"Line: {line_num}")
    print(f"Task: {task['description']}")
    print(f"{'='*60}\n")

    # 1. Clarify
    print("1. What is it? (Clarify)")
    input("   Briefly describe what this is about (or press enter to skip): ")

    # 2. Actionable?
    print("\n2. Is it actionable?")
    actionable = get_user_input("   Can you do something about this? (yes/no)", ['yes', 'no'])

    if actionable == 'no':
        print("\n   Not actionable. What should we do with it?")
        print("     1. Trash (delete it)")
        print("     2. Reference (note for later)")
        print("     3. Someday/Maybe (⏬ lowest priority)")
        print("     4. Cancel (keep as is)")

        choice = get_user_input("   Choice", ['1', '2', '3', '4'])

        if choice == '1':
            del lines[line_num - 1]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"\n✓ Task deleted from {file_rel}")
            return True

        elif choice == '2':
            print("\n   Consider creating a note in your References folder.")
            return False

        elif choice == '3':
            # Set ⏬ priority
            task_match = re.match(r'^(\s*- \[.\]\s+)(.*)$', task_line)
            if task_match:
                prefix, desc = task_match.groups()
                new_desc = add_metadata_to_task(desc.rstrip(), priority='⏬')
                lines[line_num - 1] = f"{prefix}{new_desc}\n"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"\n✓ Task set to ⏬ (someday/maybe) in {file_rel}")
                return True

        print("\n   Cancelled. Task unchanged.")
        return False

    # 3. Next action
    print("\n3. What's the next action?")
    next_action = input("   Describe the specific, concrete next action: ").strip()
    if next_action:
        task['description'] = next_action

    # 4. Two-minute rule
    print("\n4. Can you do it in 2 minutes or less?")
    two_minutes = get_user_input("   2-minute rule (yes/no)", ['yes', 'no'])

    if two_minutes == 'yes':
        print("\n   Do it now, then mark it as done!")
        mark_done = get_user_input("   Mark as done? (yes/no)", ['yes', 'no'])
        if mark_done == 'yes':
            obs.task_done(file_rel, line_num)
            print(f"\n✓ Task marked as done in {file_rel}")
            return True
        return False

    # 5. Project?
    print("\n5. Is this a project (requires multiple steps)?")
    is_project = get_user_input("   Project? (yes/no)", ['yes', 'no'])
    if is_project == 'yes':
        print("\n   Consider creating a project file in GTD/Projects/")

    # 6. Defer, delegate, or do
    print("\n6. Should you delegate or defer this?")
    print("   1. Defer (schedule for later)")
    print("   2. Delegate (assign to someone)")
    print("   3. Do ASAP (no specific date)")

    choice = get_user_input("   Choice", ['1', '2', '3'])

    context_tag = None
    scheduled_date = None

    if choice == '2':
        person = input("\n   Who should do this?: ").strip()
        if person:
            task['description'] = f"{task['description']} @waiting-{person}"
        context_tag = '@waiting'
    else:
        context_tag = get_context_tag()
        if choice == '1':
            scheduled_date = get_scheduled_date()

    # Update the task
    new_desc = add_metadata_to_task(
        task['description'], context=context_tag, scheduled_date=scheduled_date,
    )
    task_match = re.match(r'^(\s*)- \[.\]\s+(.*)$', task_line)
    if task_match:
        indent = task_match.group(1)
        lines[line_num - 1] = f"{indent}- [ ] {new_desc}\n"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\n✓ Task processed in {file_rel}:{line_num}")
        print(f"   Context: {context_tag or 'none'}")
        if scheduled_date:
            print(f"   Scheduled: {scheduled_date}")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Interactive GTD processing for inbox items",
    )

    parser.add_argument("--file", "-f", required=True,
                        help="File containing task (relative to vault)")
    parser.add_argument("--line", "-l", type=int, required=True,
                        help="Line number of task (1-indexed)")

    args = parser.parse_args()

    vault_path = get_vault_path()
    file_path = vault_path / args.file
    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return

    process_task_interactive(args.file, args.line)


if __name__ == "__main__":
    main()
