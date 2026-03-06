#!/usr/bin/env python3
"""
Create a new GTD project file with template via the official Obsidian CLI.

Usage:
    python tools/create_project.py "Website Redesign"
    python tools/create_project.py "Home Renovation" --context "@out"
    python tools/create_project.py "Research AI Tools" --context "@ai" --template custom.md
"""

import argparse
from datetime import date

from gtd_common import (
    get_vault_path,
    load_config,
    get_gtd_path,
)
import obsidian_cli as obs


def sanitize_filename(name):
    """Convert project name to valid filename."""
    sanitized = name.replace('/', '-').replace('\\', '-').replace(':', ' -')
    for ch in '<>"|?*':
        sanitized = sanitized.replace(ch, '')
    return sanitized.strip()


def create_project_template(project_name, context=None):
    """Generate project file content from template."""
    today = date.today()
    tag = f" {context}" if context else ""

    return (
        f"# {project_name}\\n\\n"
        f"**Created:** {today}\\n"
        f"**Status:** Active\\n\\n"
        f"## Purpose / Outcome\\n\\n"
        f"What is the successful outcome for this project?\\n\\n"
        f"## Next Actions\\n\\n"
        f"- [ ] First next action{tag}\\n- [ ] \\n\\n"
        f"## Notes\\n\\n"
        f"## Resources / Links\\n\\n"
        f"## Completed Actions\\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Create a new GTD project file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/create_project.py "Website Redesign"
  python tools/create_project.py "Home Renovation" --context "@out"
        """
    )

    parser.add_argument("name", help="Project name")
    parser.add_argument("--context", "-c", metavar="TAG",
                        help="Default context tag for next actions")
    parser.add_argument("--template", "-t", metavar="FILE",
                        help="Custom template file (relative to vault)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-confirm without prompting")

    args = parser.parse_args()

    config = load_config()
    vault_path = get_vault_path()

    if args.context:
        valid = config['settings']['available_contexts']
        if args.context not in valid:
            print(f"Warning: '{args.context}' is not in configured contexts")

    projects_folder = config['gtd']['projects_folder']
    filename = sanitize_filename(args.name)
    project_path = f"{projects_folder}/{filename}.md"

    # Check if exists
    if (vault_path / project_path).exists():
        print(f"Error: Project file already exists: {project_path}")
        if not args.yes:
            response = input("Overwrite? (yes/no): ")
            if response.lower() not in ('yes', 'y'):
                return

    # Generate content
    if args.template:
        template_path = vault_path / args.template
        if not template_path.exists():
            print(f"Error: Template file not found: {args.template}")
            return
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # For CLI, escape newlines
        content = content.replace('\n', '\\n')
    else:
        content = create_project_template(args.name, context=args.context)

    # Create via CLI
    obs.create_file(path=project_path, content=content, overwrite=True)
    print(f"Created project: {project_path}")

    # Add to Projects List
    projects_list_path = get_gtd_path('projects_list')
    if projects_list_path.exists():
        with open(projects_list_path, 'r', encoding='utf-8') as f:
            existing = f.read()
        if f"[[{args.name}]]" not in existing:
            obs.append_to_file(f"- [[{args.name}]]", path=config['gtd']['projects_list'])
            print(f"Added to {config['gtd']['projects_list']}")

    print(f"\nNext steps:")
    print(f"1. Edit {project_path}")
    print(f"2. Define the successful outcome")
    print(f"3. List all next actions")


if __name__ == "__main__":
    main()
