#!/usr/bin/env python3
"""
Thin wrapper around the official Obsidian CLI (obsidian 1.12+).

Every tool should call obsidian() instead of doing direct file I/O for reads.
Writes that touch a single line still use direct file I/O (the CLI has no
line-level edit/delete), but all reads, appends, task queries, and creates
go through the CLI so Obsidian stays in sync.
"""

import json
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate the binary
# ---------------------------------------------------------------------------

_OBSIDIAN_BIN = None


def _find_obsidian_bin():
    """Find the obsidian CLI binary."""
    global _OBSIDIAN_BIN
    if _OBSIDIAN_BIN:
        return _OBSIDIAN_BIN

    # WSL: use the Windows exe directly
    win_exe = Path("/usr/local/bin/obsidian")
    if win_exe.exists():
        _OBSIDIAN_BIN = str(win_exe)
        return _OBSIDIAN_BIN

    # Wrapper in ~/bin
    import shutil
    found = shutil.which("obsidian")
    if found:
        _OBSIDIAN_BIN = found
        return _OBSIDIAN_BIN

    raise FileNotFoundError(
        "Cannot find Obsidian CLI binary. "
        "Install Obsidian 1.12+ and ensure it's on PATH or at the standard Windows location."
    )


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

_VAULT_NAME = "Obsidian"  # default vault name


def set_vault(name: str):
    """Override the default vault name."""
    global _VAULT_NAME
    _VAULT_NAME = name


def run(*args: str, vault: str | None = None, timeout: int = 30) -> str:
    """
    Run an Obsidian CLI command and return stdout (stripped).

    Raises subprocess.CalledProcessError on non-zero exit.
    Filters out the noisy version/warning lines automatically.
    """
    v = vault or _VAULT_NAME
    cmd = [_find_obsidian_bin(), f"vault={v}"] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    # Filter noise lines from stdout (the exe mixes them into stdout)
    lines = []
    for line in result.stdout.splitlines():
        if line.startswith("202") and "Loading updated app package" in line:
            continue
        if line.startswith("Your Obsidian installer is out of date"):
            continue
        lines.append(line)
    stdout = "\n".join(lines).strip()

    if result.returncode not in (0, 1):
        # code 1 sometimes means "no results" which is fine
        raise subprocess.CalledProcessError(result.returncode, cmd, stdout, result.stderr)
    return stdout


def run_json(*args: str, **kwargs) -> list | dict:
    """Run a CLI command that returns JSON and parse it."""
    raw = run(*args, **kwargs)
    if not raw:
        return []
    return json.loads(raw)


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------

def tasks_todo(*, verbose: bool = True, as_json: bool = True) -> list[dict]:
    """
    Return all incomplete tasks.

    Each dict has: status, text, file, line (str).
    """
    args = ["tasks", "todo"]
    if verbose:
        args.append("verbose")
    if as_json:
        args.append("format=json")
        return run_json(*args)
    return run(*args)


def tasks_done(*, verbose: bool = True, as_json: bool = True) -> list[dict]:
    """Return all completed tasks."""
    args = ["tasks", "done"]
    if verbose:
        args.append("verbose")
    if as_json:
        args.append("format=json")
        return run_json(*args)
    return run(*args)


def _task_file_arg(path: str) -> str:
    """Convert vault-relative path to the file= arg the CLI expects.

    The CLI file= resolver uses wikilink-style name matching, so we
    strip the extension and any folder prefix. For exact targeting we
    use path=.
    """
    return f"path={path}"


def task_info(path: str, line: int) -> dict:
    """Get info about a specific task."""
    raw = run("task", _task_file_arg(path), f"line={line}")
    info = {}
    for row in raw.splitlines():
        if "\t" in row:
            k, v = row.split("\t", 1)
            info[k] = v
    return info


def task_done(path: str, line: int) -> str:
    """Mark a task as done."""
    return run("task", _task_file_arg(path), f"line={line}", "done")


def task_toggle(path: str, line: int) -> str:
    """Toggle a task's completion status."""
    return run("task", _task_file_arg(path), f"line={line}", "toggle")


def read_file(*, file: str | None = None, path: str | None = None) -> str:
    """Read file contents via CLI."""
    args = ["read"]
    if path:
        args.append(f"path={path}")
    elif file:
        args.append(f"file={file}")
    return run(*args)


def append_to_file(content: str, *, path: str | None = None, file: str | None = None) -> str:
    """Append content to a file."""
    args = ["append", f"content={content}"]
    if path:
        args.append(f"path={path}")
    elif file:
        args.append(f"file={file}")
    return run(*args)


def daily_append(content: str) -> str:
    """Append content to today's daily note.

    Uses daily:path + append (daily:append is broken in 1.12.4).
    """
    path = daily_path()
    return append_to_file(content, path=path)


def daily_path() -> str:
    """Get the path to today's daily note."""
    return run("daily:path")


def create_file(*, name: str | None = None, path: str | None = None,
                content: str | None = None, template: str | None = None,
                overwrite: bool = False) -> str:
    """Create a new file."""
    args = ["create"]
    if name:
        args.append(f"name={name}")
    if path:
        args.append(f"path={path}")
    if content:
        args.append(f"content={content}")
    if template:
        args.append(f"template={template}")
    if overwrite:
        args.append("overwrite")
    return run(*args)


def search(query: str, *, path: str | None = None, limit: int | None = None,
           context: bool = False) -> str:
    """Search the vault. Use context=True for line-level matches."""
    cmd = "search:context" if context else "search"
    args = [cmd, f"query={query}"]
    if path:
        args.append(f"path={path}")
    if limit:
        args.append(f"limit={limit}")
    return run(*args)


def list_files(*, folder: str | None = None, total: bool = False) -> str:
    """List files in the vault."""
    args = ["files"]
    if folder:
        args.append(f"folder={folder}")
    if total:
        args.append("total")
    return run(*args)


def vault_eval(code: str) -> str:
    """Execute JavaScript in the Obsidian app console."""
    return run("eval", f"code={code}")
