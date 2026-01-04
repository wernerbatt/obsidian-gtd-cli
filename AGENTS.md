---
name: obsidian-gtd-cli
description: Agent instructions and skill discovery for the Obsidian GTD CLI toolkit.
---

# AGENTS

## Purpose

This repository provides a Python CLI toolkit plus reusable skills for AI agents that can read `AGENTS.md` and `SKILL.md` files.

## Skills

- Primary skills live in `.claude/skills/*/SKILL.md`.
- If your agent expects a different skills path, mirror or symlink those folders (for example, `.codex/skills/`).
- Always follow the instructions inside each `SKILL.md` when using a skill.

## Tooling

- CLI scripts live in `tools/`.
- Configuration lives in `config.yaml` (notably `vault_path` and GTD paths).
- Prefer the existing tools over manual file edits in the Obsidian vault.

## Safety and Confirmation

- Do not modify tasks or vault files without explicit user confirmation.
- If a tool supports preview or dry-run behavior, use it when asked and summarize changes before applying them.
