#!/usr/bin/env python3
"""
Move a task from one file to another while preserving metadata.

This tool helps reorganize tasks between files, useful for moving tasks
to context files, project files, or archiving completed tasks.

Usage:
    python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md
    python tools/move_task.py --source GTD/PC.md --line 10 --dest GTD/Projects/Website.md
"""

import argparse
import re
from pathlib import Path
from gtd_common import (
    get_vault_path,
    load_config,
    parse_task_line,
    create_backup
)


def move_task(source_file, line_num, dest_file, create_backups=True, auto_confirm=False):
    """
    Move a task from source file to destination file.

    Args:
        source_file (Path): Source file path
        line_num (int): Line number of task in source file (1-indexed)
        dest_file (Path): Destination file path
        create_backups (bool): Whether to create backup files

    Returns:
        bool: True if successful, False otherwise
    """
    vault_path = get_vault_path()

    # Read source file
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
    except Exception as e:
        print(f"Error reading source file: {e}")
        return False

    # Validate line number
    if line_num < 1 or line_num > len(source_lines):
        print(f"Error: Invalid line number {line_num} (file has {len(source_lines)} lines)")
        return False

    # Get task line
    task_line = source_lines[line_num - 1]
    task = parse_task_line(task_line, line_num)

    if not task:
        print(f"Error: Line {line_num} is not a task")
        return False

    # Check for subtasks (indented tasks below)
    subtask_lines = []
    current_indent = task['indent']

    # Look for subtasks (tasks with greater indentation immediately following)
    for i in range(line_num, len(source_lines)):
        line = source_lines[i]

        # Check if it's a task
        subtask = parse_task_line(line, i + 1)
        if subtask and subtask['indent'] > current_indent:
            subtask_lines.append(line)
        else:
            # Stop when we hit a non-task or task with same/less indentation
            if i > line_num - 1:
                break

    # Display task info
    print(f"\nMoving task:")
    print(f"  From: {source_file.relative_to(vault_path)}:{line_num}")
    print(f"  To:   {dest_file.relative_to(vault_path)}")
    print(f"  Task: {task['description']}")
    if subtask_lines:
        print(f"  Subtasks: {len(subtask_lines)}")

    # Confirm
    if not auto_confirm:
        response = input("\nProceed? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return False

    # Create backups
    if create_backups:
        create_backup(source_file)
        if dest_file.exists():
            create_backup(dest_file)

    # Remove task (and subtasks) from source
    lines_to_remove = [line_num - 1]
    if subtask_lines:
        lines_to_remove.extend(range(line_num, line_num + len(subtask_lines)))

    # Remove in reverse order to preserve indices
    for idx in sorted(lines_to_remove, reverse=True):
        if idx < len(source_lines):
            del source_lines[idx]

    # Write updated source file
    try:
        with open(source_file, 'w', encoding='utf-8') as f:
            f.writelines(source_lines)
    except Exception as e:
        print(f"Error writing source file: {e}")
        return False

    # Add to destination file
    # Create destination if it doesn't exist
    if not dest_file.exists():
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_lines = []
    else:
        try:
            with open(dest_file, 'r', encoding='utf-8') as f:
                dest_lines = f.readlines()
        except Exception as e:
            print(f"Error reading destination file: {e}")
            return False

    # Append task (and subtasks) to destination
    dest_lines.append(task_line)
    for subtask_line in subtask_lines:
        dest_lines.append(subtask_line)

    # Ensure newline at end
    if dest_lines and not dest_lines[-1].endswith('\n'):
        dest_lines[-1] += '\n'

    # Write destination file
    try:
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.writelines(dest_lines)
    except Exception as e:
        print(f"Error writing destination file: {e}")
        return False

    print(f"\n✓ Task moved successfully!")
    if create_backups:
        print("  Backup files created with .bak extension")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Move a task from one file to another",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Move task from Dashboard to PC context
  python tools/move_task.py --source GTD/Dashboard.md --line 42 --dest GTD/PC.md

  # Move task to project file
  python tools/move_task.py --source GTD/PC.md --line 10 --dest GTD/Projects/Website.md

The tool will:
- Preserve all task metadata (emoji dates, context tags, etc.)
- Move subtasks (indented tasks) along with the parent
- Create backups before modifying files
- Confirm before making changes
        """
    )

    parser.add_argument("--source", "-s", required=True, metavar="FILE",
                       help="Source file (relative to vault)")
    parser.add_argument("--line", "-l", required=True, type=int, metavar="N",
                       help="Line number of task to move (1-indexed)")
    parser.add_argument("--dest", "-d", required=True, metavar="FILE",
                       help="Destination file (relative to vault)")
    parser.add_argument("--yes", "-y", action="store_true",
                       help="Auto-confirm without prompting (for agentic use)")

    args = parser.parse_args()

    # Get vault path and resolve file paths
    vault_path = get_vault_path()
    source_file = vault_path / args.source
    dest_file = vault_path / args.dest

    # Validate source file exists
    if not source_file.exists():
        print(f"Error: Source file not found: {args.source}")
        return

    # Validate source and dest are different
    if source_file.resolve() == dest_file.resolve():
        print("Error: Source and destination files are the same")
        return

    # Move task
    move_task(
        source_file,
        args.line,
        dest_file,
        create_backups=False,  # Disabled - rely on git
        auto_confirm=args.yes
    )


if __name__ == "__main__":
    main()
