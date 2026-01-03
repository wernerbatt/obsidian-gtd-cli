#!/usr/bin/env python3
"""
Create a new GTD project file with template.

Projects in GTD are outcomes that require more than one action step.
This tool creates a properly formatted project file in the GTD/Projects folder.

Usage:
    python tools/create_project.py "Website Redesign"
    python tools/create_project.py "Home Renovation" --context "@home"
    python tools/create_project.py "Research AI Tools" --context "@ai" --template custom.md
"""

import argparse
from pathlib import Path
from datetime import date
from gtd_common import (
    get_vault_path,
    load_config,
    get_gtd_path
)


def sanitize_filename(name):
    """
    Convert project name to valid filename.

    Args:
        name (str): Project name

    Returns:
        str: Sanitized filename

    Example:
        >>> sanitize_filename("Website: Redesign (v2)")
        "Website - Redesign (v2)"
    """
    # Replace problematic characters
    sanitized = name.replace('/', '-').replace('\\', '-').replace(':', ' -')
    # Remove any other invalid filename characters
    invalid_chars = '<>"|?*'
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '')
    return sanitized.strip()


def create_project_template(project_name, context=None):
    """
    Generate project file content from template.

    Args:
        project_name (str): Name of the project
        context (str, optional): Default context tag for next actions

    Returns:
        str: Project file content
    """
    today = date.today()
    context_tag = f" {context}" if context else ""

    template = f"""# {project_name}

**Created:** {today}
**Status:** Active

## Purpose / Outcome

What is the successful outcome for this project?

## Next Actions

- [ ] First next action{context_tag}
- [ ]

## Notes

## Resources / Links

## Completed Actions

"""

    return template


def add_to_projects_list(project_name, project_file_relative):
    """
    Add project to Projects List.md.

    Args:
        project_name (str): Name of the project
        project_file_relative (str): Relative path to project file
    """
    try:
        projects_list_path = get_gtd_path('projects_list')

        # Read existing content
        if projects_list_path.exists():
            with open(projects_list_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# Projects List\n\n"

        # Add new project link (wikilink format)
        project_link = f"- [[{project_name}]]\n"

        # Check if already exists
        if project_link not in content and f"[[{project_name}]]" not in content:
            content += project_link

            # Write back
            with open(projects_list_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"Added to {projects_list_path.name}")

    except Exception as e:
        print(f"Warning: Could not update Projects List: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new GTD project file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
A project in GTD is any outcome that requires more than one action step.

Examples:
  # Create a simple project
  python tools/create_project.py "Website Redesign"

  # Create with default context for actions
  python tools/create_project.py "Home Renovation" --context "@home"

  # Use custom template
  python tools/create_project.py "Research" --template my_template.md

The project file will be created in GTD/Projects/ folder and added to
Projects List.md automatically.
        """
    )

    parser.add_argument("name", help="Project name")
    parser.add_argument("--context", "-c", metavar="TAG",
                       help="Default context tag for next actions (e.g., @pc, @work)")
    parser.add_argument("--template", "-t", metavar="FILE",
                       help="Custom template file to use (relative to vault)")
    parser.add_argument("--yes", "-y", action="store_true",
                       help="Auto-confirm without prompting (for agentic use)")

    args = parser.parse_args()

    vault_path = get_vault_path()
    config = load_config()

    # Validate context if provided
    if args.context:
        valid_contexts = config['settings']['available_contexts']
        if args.context not in valid_contexts:
            print(f"Warning: '{args.context}' is not in configured contexts")

    # Get projects folder
    projects_folder = get_gtd_path('projects_folder')
    projects_folder.mkdir(parents=True, exist_ok=True)

    # Create project filename
    filename = sanitize_filename(args.name)
    project_file = projects_folder / f"{filename}.md"

    # Check if already exists
    if project_file.exists():
        print(f"Error: Project file already exists: {project_file.relative_to(vault_path)}")
        if not args.yes:
            response = input("Overwrite? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                return

    # Generate or load template
    if args.template:
        template_path = vault_path / args.template
        if not template_path.exists():
            print(f"Error: Template file not found: {args.template}")
            return

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = create_project_template(args.name, context=args.context)

    # Create project file
    try:
        with open(project_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Created project: {project_file.relative_to(vault_path)}")

        # Add to Projects List
        add_to_projects_list(args.name, project_file.relative_to(vault_path))

        print(f"\nNext steps:")
        print(f"1. Edit {project_file.relative_to(vault_path)}")
        print(f"2. Define the successful outcome")
        print(f"3. List all next actions")
        print(f"4. Add context tags to actions")

    except Exception as e:
        print(f"Error creating project file: {e}")


if __name__ == "__main__":
    main()
