#!/usr/bin/env python3
"""
Shared utilities for Obsidian GTD CLI tools.

This module provides:
- Configuration loading
- Task-line parsing (Obsidian Tasks emoji metadata)
- Metadata helpers (add/format/extract)
- GTD-specific filters (inbox criteria, etc.)

File I/O should go through obsidian_cli.py where possible.
Direct file reads/writes are only used for line-level edits that the
Obsidian CLI doesn't support.
"""

import re
from pathlib import Path
from datetime import datetime, date
import yaml


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config():
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_vault_path():
    """Get the resolved vault path from configuration."""
    config = load_config()
    vault_path = Path(__file__).parent.parent / config['vault_path']
    return vault_path.resolve()


def get_gtd_path(key, subkey=None):
    """
    Get a GTD-specific path from configuration.

    Args:
        key: Top-level key in gtd config (e.g., 'dashboard', 'projects_folder')
        subkey: Subkey for nested config (e.g., 'contexts.pc')

    Returns:
        Path: Absolute path to the GTD file or folder
    """
    config = load_config()
    vault_path = get_vault_path()
    value = config['gtd'][key][subkey] if subkey else config['gtd'][key]
    return vault_path / value


# ---------------------------------------------------------------------------
# Task parsing
# ---------------------------------------------------------------------------

def parse_task_line(line, line_num=0):
    """
    Parse a task line and extract metadata.

    Supports Obsidian Tasks plugin format with emoji metadata.

    Args:
        line: Line of text to parse
        line_num: Line number in file (1-indexed)

    Returns:
        dict or None: Task dictionary with metadata, or None if not a task
    """
    task_match = re.match(r'^(\s*)- \[(.)\]\s+(.*)$', line)
    if not task_match:
        return None

    indent, status, description = task_match.groups()
    is_done = status.lower() != ' '

    due_date = None
    scheduled_date = None
    start_date = None
    done_date = None
    priority = None

    # Due date: 📅 or 📆
    due_match = re.search(r'[📅📆]\s*(\d{4}-\d{2}-\d{2})', description)
    if due_match:
        try:
            due_date = datetime.strptime(due_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Scheduled date: ⏳
    sched_match = re.search(r'⏳\s*(\d{4}-\d{2}-\d{2})', description)
    if sched_match:
        try:
            scheduled_date = datetime.strptime(sched_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Start date: 🛫
    start_match = re.search(r'🛫\s*(\d{4}-\d{2}-\d{2})', description)
    if start_match:
        try:
            start_date = datetime.strptime(start_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Done date: ✅
    done_match = re.search(r'✅\s*(\d{4}-\d{2}-\d{2})', description)
    if done_match:
        try:
            done_date = datetime.strptime(done_match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Priority
    priority_matches = re.findall(r'[⏫🔼🔽⏬🔺]', description)
    if priority_matches:
        priority = priority_matches[-1]

    return {
        'line_num': line_num,
        'description': description.strip(),
        'is_done': is_done,
        'status': status,
        'due_date': due_date,
        'scheduled_date': scheduled_date,
        'start_date': start_date,
        'done_date': done_date,
        'priority': priority,
        'is_blocked': '⛔' in description,
        'is_recurring': '🔁' in description,
        'indent': len(indent),
    }


def parse_task_from_cli(item: dict) -> dict:
    """
    Parse a task dict returned by obsidian_cli.tasks_todo()/tasks_done().

    The CLI returns: {status, text, file, line}
    We augment it with our parsed metadata.
    """
    text = item.get('text', '')
    line_num = int(item.get('line', 0))
    parsed = parse_task_line(text, line_num) or {}
    return {
        'file': item.get('file', ''),
        'line_num': line_num,
        'description': parsed.get('description', text),
        'is_done': parsed.get('is_done', False),
        'status': item.get('status', ' '),
        'due_date': parsed.get('due_date'),
        'scheduled_date': parsed.get('scheduled_date'),
        'start_date': parsed.get('start_date'),
        'done_date': parsed.get('done_date'),
        'priority': parsed.get('priority'),
        'is_blocked': parsed.get('is_blocked', False),
        'is_recurring': parsed.get('is_recurring', False),
        'indent': parsed.get('indent', 0),
    }


# ---------------------------------------------------------------------------
# GTD filters
# ---------------------------------------------------------------------------

def task_matches_inbox(task: dict) -> bool:
    """
    Check if a task belongs in the GTD inbox (needs processing).

    Criteria:
    - No context tags
    - Not lowest priority (⏬)
    - Not a time block (HH:MM - HH:MM)
    - Not empty description
    - Path excludes: Checklist, Templates, Recurring, obsidian-tasks
    - (no due date) OR (due before today)
    - (no scheduled date) OR (scheduled before today)
    - Not blocked, not done
    """
    desc = task['description']
    file_path = task.get('file', '')

    config = load_config()
    context_tags = config['settings']['available_contexts']

    # Has any context tag?
    for tag in context_tags:
        if tag in desc:
            return False
    if '@someday' in desc:
        return False

    # Lowest priority = someday/maybe
    if task.get('priority') == '⏬':
        return False

    # Time block pattern
    if re.match(r'^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', desc):
        return False

    # Empty
    if not desc.strip():
        return False

    # Excluded paths
    for excluded in ('Checklist', 'Templates', 'Recurring', 'obsidian-tasks'):
        if excluded in file_path:
            return False

    today = date.today()

    if task['due_date'] is not None and task['due_date'] >= today:
        return False
    if task['scheduled_date'] is not None and task['scheduled_date'] >= today:
        return False

    if task.get('is_blocked'):
        return False
    if task.get('is_done'):
        return False

    return True


def task_matches_tag(task: dict, tag: str) -> bool:
    """Active tasks with a given context tag (excludes ⏬, blocked, done, future-scheduled)."""
    desc = task['description']
    if tag not in desc:
        return False
    if task.get('is_done'):
        return False
    if task.get('is_blocked'):
        return False
    if task.get('priority') == '⏬':
        return False

    today = date.today()
    if task['due_date'] is not None and task['due_date'] > today:
        return False
    if task['scheduled_date'] is not None and task['scheduled_date'] > today:
        return False

    return True


def task_matches_someday(task: dict) -> bool:
    """Someday/Maybe: ⏬ priority or @someday tag."""
    if task.get('is_done'):
        return False
    return task.get('priority') == '⏬' or '@someday' in task['description']


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def add_metadata_to_task(description, **kwargs):
    """
    Add or update metadata in a task description.

    Supported kwargs:
        scheduled_date, due_date, start_date (str YYYY-MM-DD)
        context (str e.g. '@pc')
        priority (str e.g. '⏫')
    """
    result = description

    # Remove existing priority first (will re-add at end)
    if 'priority' in kwargs:
        result = re.sub(r'[⏫🔼🔽⏬🔺]\s*$', '', result).strip()

    # Context tag
    if 'context' in kwargs and kwargs['context']:
        config = load_config()
        context_tags = config['settings']['available_contexts']
        if not any(tag in result for tag in context_tags):
            result = f"{result} {kwargs['context']}"

    # Dates — remove old then add new
    if 'scheduled_date' in kwargs:
        result = re.sub(r'⏳\s*\d{4}-\d{2}-\d{2}', '', result).strip()
    if 'due_date' in kwargs:
        result = re.sub(r'[📅📆]\s*\d{4}-\d{2}-\d{2}', '', result).strip()
    if 'start_date' in kwargs:
        result = re.sub(r'🛫\s*\d{4}-\d{2}-\d{2}', '', result).strip()

    if kwargs.get('scheduled_date'):
        result = f"{result} ⏳ {kwargs['scheduled_date']}"
    if kwargs.get('due_date'):
        result = f"{result} 📅 {kwargs['due_date']}"
    if kwargs.get('start_date'):
        result = f"{result} 🛫 {kwargs['start_date']}"

    # Priority at the END
    if kwargs.get('priority'):
        result = f"{result} {kwargs['priority']}"

    return result.strip()


def format_task_line(description, is_done=False, indent=0):
    """Format a task line with proper Markdown checkbox syntax."""
    checkbox = '[x]' if is_done else '[ ]'
    return f"{' ' * indent}- {checkbox} {description}"


def extract_context_tags(description):
    """Extract context tags from a task description."""
    config = load_config()
    return [tag for tag in config['settings']['available_contexts'] if tag in description]


# ---------------------------------------------------------------------------
# Line-matching (for tools that edit/delete by description match)
# ---------------------------------------------------------------------------

def find_task_lines_by_match(lines, match_text, use_regex=False):
    """
    Find task line numbers matching a description string or regex.

    Matching strategy (non-regex):
    1. Exact match
    2. Substring (case-sensitive)
    3. Substring (case-insensitive)
    """
    if use_regex:
        return [
            i for i, line in enumerate(lines, 1)
            if parse_task_line(line, i) and re.search(match_text, parse_task_line(line, i)['description'])
        ]

    exact, substring, substring_ci = [], [], []
    match_lower = match_text.lower()

    for i, line in enumerate(lines, 1):
        task = parse_task_line(line, i)
        if not task:
            continue
        desc = task['description']
        if desc == match_text:
            exact.append(i)
        if match_text in desc:
            substring.append(i)
        if match_lower in desc.lower():
            substring_ci.append(i)

    return exact or substring or substring_ci


# ---------------------------------------------------------------------------
# Date parsing (shared by multiple tools)
# ---------------------------------------------------------------------------

def parse_date_string(date_str):
    """Parse flexible date string → YYYY-MM-DD."""
    from datetime import timedelta
    s = date_str.strip().lower()
    today = date.today()
    if s == 'today':
        return str(today)
    if s == 'tomorrow':
        return str(today + timedelta(days=1))
    if s == 'yesterday':
        return str(today - timedelta(days=1))
    if s.startswith('+'):
        return str(today + timedelta(days=int(s[1:])))
    # YYYY-MM-DD
    return str(datetime.strptime(s, '%Y-%m-%d').date())
