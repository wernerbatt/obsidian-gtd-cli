#!/usr/bin/env python3
"""
Shared utilities for Obsidian GTD CLI tools.

This module provides common functions for:
- Loading configuration
- Parsing task lines with Obsidian Tasks metadata
- Creating backups
- GTD-specific task filters
"""

import re
import shutil
from pathlib import Path
from datetime import datetime, date
import yaml


def load_config():
    """
    Load configuration from config.yaml.

    Returns:
        dict: Configuration dictionary with vault_path, gtd, and settings
    """
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def get_vault_path():
    """
    Get the resolved vault path from configuration.

    Returns:
        Path: Absolute path to Obsidian vault
    """
    config = load_config()
    vault_path = Path(__file__).parent.parent / config['vault_path']
    return vault_path.resolve()


def get_gtd_path(key, subkey=None):
    """
    Get a GTD-specific path from configuration.

    Args:
        key (str): Top-level key in gtd config (e.g., 'dashboard', 'projects_folder')
        subkey (str, optional): Subkey for nested config (e.g., 'contexts.pc')

    Returns:
        Path: Absolute path to the GTD file or folder

    Examples:
        get_gtd_path('dashboard') -> /path/to/vault/GTD/Dashboard.md
        get_gtd_path('contexts', 'pc') -> /path/to/vault/GTD/PC.md
    """
    config = load_config()
    vault_path = get_vault_path()

    if subkey:
        value = config['gtd'][key][subkey]
    else:
        value = config['gtd'][key]

    return vault_path / value


def parse_task_line(line, line_num):
    """
    Parse a task line and extract metadata.

    Supports Obsidian Tasks plugin format with emoji metadata:
    - 📅 or 📆 : Due date
    - ⏳ : Scheduled date
    - 🛫 : Start date
    - ✅ : Done date
    - 🔁 : Recurring
    - ⛔ : Blocked

    Args:
        line (str): Line of text to parse
        line_num (int): Line number in file (1-indexed)

    Returns:
        dict or None: Task dictionary with metadata, or None if not a task

    Example:
        >>> parse_task_line("- [ ] Do something @pc ⏳ 2025-01-15", 1)
        {
            'line_num': 1,
            'description': 'Do something @pc ⏳ 2025-01-15',
            'is_done': False,
            'due_date': None,
            'scheduled_date': date(2025, 1, 15),
            'is_blocked': False,
            'indent': 0
        }
    """
    # Basic task pattern: - [ ] or - [x]
    task_match = re.match(r'^(\s*)- \[(.)\]\s+(.*)$', line)
    if not task_match:
        return None

    indent, status, description = task_match.groups()
    is_done = status.lower() != ' '

    # Extract Obsidian Tasks metadata
    due_date = None
    scheduled_date = None
    start_date = None
    done_date = None

    # Due date: 📅 YYYY-MM-DD or 📆 YYYY-MM-DD
    due_match = re.search(r'[📅📆]\s*(\d{4}-\d{2}-\d{2})', description)
    if due_match:
        try:
            due_date = datetime.strptime(due_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Scheduled date: ⏳ YYYY-MM-DD
    sched_match = re.search(r'⏳\s*(\d{4}-\d{2}-\d{2})', description)
    if sched_match:
        try:
            scheduled_date = datetime.strptime(sched_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Start date: 🛫 YYYY-MM-DD
    start_match = re.search(r'🛫\s*(\d{4}-\d{2}-\d{2})', description)
    if start_match:
        try:
            start_date = datetime.strptime(start_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Done date: ✅ YYYY-MM-DD
    done_match = re.search(r'✅\s*(\d{4}-\d{2}-\d{2})', description)
    if done_match:
        try:
            done_date = datetime.strptime(done_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Check for blocking/recurring
    is_blocked = '⛔' in description
    is_recurring = '🔁' in description

    return {
        'line_num': line_num,
        'description': description.strip(),
        'is_done': is_done,
        'due_date': due_date,
        'scheduled_date': scheduled_date,
        'start_date': start_date,
        'done_date': done_date,
        'is_blocked': is_blocked,
        'is_recurring': is_recurring,
        'indent': len(indent)
    }


def task_matches_to_process_criteria(task, file_path):
    """
    Check if task matches GTD "To Process" criteria.

    Criteria (from Dashboard.md):
    - No context tags (@pc, @work, @home, @sharne, @out, @garden, @someday, @ai, @ponderables, @stuck)
    - Not a time block (HH:MM - HH:MM)
    - Not empty description
    - Path excludes: Checklist, Templates, Recurring, obsidian-tasks
    - (no due date) OR (due before today)
    - (no scheduled date) OR (scheduled before today)
    - Not blocked
    - Not done

    Args:
        task (dict): Task dictionary from parse_task_line()
        file_path (Path): Path to file containing the task

    Returns:
        bool: True if task matches "To Process" criteria
    """
    desc = task['description']
    path_str = str(file_path)

    # Exclusion: description includes context tags
    config = load_config()
    context_tags = config['settings']['available_contexts']
    for tag in context_tags:
        if tag in desc:
            return False

    # Exclusion: time range pattern (HH:MM - HH:MM)
    if re.match(r'^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', desc):
        return False

    # Exclusion: empty description
    if re.match(r'^$', desc):
        return False

    # Exclusion: path includes certain folders
    excluded_paths = ['Checklist', 'Templates', 'Recurring', 'obsidian-tasks']
    for excluded in excluded_paths:
        if excluded in path_str:
            return False

    # Date filters: (no due date) OR (due before today)
    today = date.today()
    if task['due_date'] is not None and task['due_date'] >= today:
        return False

    # Date filters: (no scheduled date) OR (scheduled before today)
    if task['scheduled_date'] is not None and task['scheduled_date'] >= today:
        return False

    # Status filters
    if task['is_blocked']:
        return False

    if task['is_done']:
        return False

    return True


def create_backup(file_path):
    """
    Create a backup of a file before modification.

    Args:
        file_path (Path): Path to file to backup

    Returns:
        Path: Path to backup file (.bak extension)
    """
    backup_path = file_path.with_suffix('.md.bak')
    shutil.copy2(file_path, backup_path)
    return backup_path


def add_metadata_to_task(description, **kwargs):
    """
    Add or update metadata in a task description.

    Supported kwargs:
    - scheduled_date (str): YYYY-MM-DD format
    - due_date (str): YYYY-MM-DD format
    - start_date (str): YYYY-MM-DD format
    - context (str): Context tag (e.g., '@pc')

    Args:
        description (str): Task description
        **kwargs: Metadata to add

    Returns:
        str: Updated task description

    Example:
        >>> add_metadata_to_task("Do something", scheduled_date="2025-01-15", context="@pc")
        "Do something @pc ⏳ 2025-01-15"
    """
    result = description

    # Add context tag if provided
    if 'context' in kwargs and kwargs['context']:
        # Check if any context tag already exists
        config = load_config()
        context_tags = config['settings']['available_contexts']
        has_context = any(tag in result for tag in context_tags)

        if not has_context:
            result = f"{result} {kwargs['context']}"

    # Remove existing dates before adding new ones
    if 'scheduled_date' in kwargs:
        result = re.sub(r'⏳\s*\d{4}-\d{2}-\d{2}', '', result).strip()
    if 'due_date' in kwargs:
        result = re.sub(r'[📅📆]\s*\d{4}-\d{2}-\d{2}', '', result).strip()
    if 'start_date' in kwargs:
        result = re.sub(r'🛫\s*\d{4}-\d{2}-\d{2}', '', result).strip()

    # Add new dates
    if 'scheduled_date' in kwargs and kwargs['scheduled_date']:
        result = f"{result} ⏳ {kwargs['scheduled_date']}"
    if 'due_date' in kwargs and kwargs['due_date']:
        result = f"{result} 📅 {kwargs['due_date']}"
    if 'start_date' in kwargs and kwargs['start_date']:
        result = f"{result} 🛫 {kwargs['start_date']}"

    return result.strip()


def format_task_line(description, is_done=False, indent=0):
    """
    Format a task line with proper Markdown checkbox syntax.

    Args:
        description (str): Task description
        is_done (bool): Whether task is completed
        indent (int): Indentation level (number of spaces)

    Returns:
        str: Formatted task line

    Example:
        >>> format_task_line("Do something @pc", is_done=False, indent=2)
        "  - [ ] Do something @pc"
    """
    checkbox = '[x]' if is_done else '[ ]'
    spaces = ' ' * indent
    return f"{spaces}- {checkbox} {description}"


def get_context_files():
    """
    Get all context file paths from configuration.

    Returns:
        dict: Dictionary mapping context names to file paths

    Example:
        >>> get_context_files()
        {
            'pc': Path('/vault/GTD/PC.md'),
            'work': Path('/vault/GTD/Work.md'),
            ...
        }
    """
    config = load_config()
    vault_path = get_vault_path()

    context_files = {}
    for name, rel_path in config['gtd']['contexts'].items():
        context_files[name] = vault_path / rel_path

    return context_files


def extract_context_tags(description):
    """
    Extract context tags from a task description.

    Args:
        description (str): Task description

    Returns:
        list: List of context tags found (e.g., ['@pc', '@work'])
    """
    config = load_config()
    context_tags = config['settings']['available_contexts']

    found_tags = []
    for tag in context_tags:
        if tag in description:
            found_tags.append(tag)

    return found_tags
