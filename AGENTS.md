---
name: obsidian-gtd-cli
description: Agent instructions and skill discovery for the Obsidian GTD CLI toolkit.
---

# AGENTS

## Purpose

This repository provides a Python CLI toolkit plus reusable skills for AI agents that can read `AGENTS.md` and `SKILL.md` files.

## Skills

- Primary skills live in `.claude/skills/*/SKILL.md`.
- Available skills: clarify, organize, project, purge, review, stuck, **systems-review**, **obsidian**, **reflect**, **task-prioritisation**, **next**.
- If your agent expects a different skills path, mirror or symlink those folders (for example, `.codex/skills/`).
- Always follow the instructions inside each `SKILL.md` when using a skill.

## Tooling

- All vault operations go through the Obsidian CLI — see the `/obsidian` skill.
- `tools/obsidian_cli.py` is a thin Python wrapper around the CLI binary (used when Python is more convenient than shell).
- Configuration lives in `config.yaml` (notably `obsidian_bin`, `vault_name`, and GTD paths).
- Never use direct file I/O for vault files — always go through the Obsidian CLI.

## Safety and Confirmation

- Do not modify tasks or vault files without explicit user confirmation.
- If a tool supports preview or dry-run behavior, use it when asked and summarize changes before applying them.
