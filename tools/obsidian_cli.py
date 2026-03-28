#!/usr/bin/env python3
"""
Thin wrapper around the official Obsidian CLI (obsidian 1.12+).

ALL vault reads and writes go through the CLI so the running Obsidian
app stays in sync.  Line-level edits use ``vault_eval`` with
``app.vault.process()`` — no direct file I/O anywhere.
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
# High-level helpers — native CLI commands
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


# ---------------------------------------------------------------------------
# Eval — execute JS inside Obsidian
# ---------------------------------------------------------------------------

def vault_eval(code: str, *, timeout: int = 30) -> str:
    """Execute JavaScript in the Obsidian app console."""
    return run("eval", f"code={code}", timeout=timeout)


def _js_escape(s: str) -> str:
    """Escape a Python string for embedding in a JS string literal (backtick)."""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


# ---------------------------------------------------------------------------
# Eval helpers — line-level file mutations via app.vault.process()
# ---------------------------------------------------------------------------

def edit_line(path: str, line_num: int, new_text: str) -> str:
    """Replace a single line (1-indexed) in *path* with *new_text*."""
    js = (
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js_escape(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, (content) => {"
        "    const lines = content.split('\\n');"
        f"    lines[{line_num - 1}] = `{_js_escape(new_text)}`;"
        "    return lines.join('\\n');"
        "  });"
        f"  return 'edited line {line_num}';"
        "})()"
    )
    return vault_eval(js)


def delete_lines(path: str, start: int, count: int = 1) -> str:
    """Delete *count* lines starting at *start* (1-indexed)."""
    js = (
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js_escape(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, (content) => {"
        "    const lines = content.split('\\n');"
        f"    lines.splice({start - 1}, {count});"
        "    return lines.join('\\n');"
        "  });"
        f"  return 'deleted {count} line(s) from line {start}';"
        "})()"
    )
    return vault_eval(js)


def replace_by_match(path: str, old_text: str, new_text: str) -> str:
    """Replace *old_text* with *new_text* in *path* (first occurrence)."""
    js = (
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js_escape(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, (content) => {"
        f"    const from_ = `{_js_escape(old_text)}`;"
        f"    const to_ = `{_js_escape(new_text)}`;"
        "    if (!content.includes(from_)) throw new Error('text not found');"
        "    return content.replace(from_, to_);"
        "  });"
        "  return 'replaced';"
        "})()"
    )
    return vault_eval(js)


def insert_after_heading(path: str, heading: str, text: str) -> str:
    """Insert *text* at the end of the section under *heading*."""
    js = (
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js_escape(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, (content) => {"
        "    const lines = content.split('\\n');"
        f"    const heading = `{_js_escape(heading)}`;"
        "    const re = new RegExp('^#{1,6}\\\\s+' + heading.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + '\\\\s*$');"
        "    let idx = -1;"
        "    for (let i = 0; i < lines.length; i++) {"
        "      if (re.test(lines[i])) { idx = i; break; }"
        "    }"
        "    if (idx === -1) throw new Error('heading not found: ' + heading);"
        "    let insert = idx + 1;"
        "    for (let i = idx + 1; i < lines.length; i++) {"
        "      if (/^#{1,6}\\s/.test(lines[i])) break;"
        "      insert = i + 1;"
        "    }"
        f"    lines.splice(insert, 0, `{_js_escape(text)}`);"
        "    return lines.join('\\n');"
        "  });"
        "  return 'inserted under ' + heading;"
        "})()"
    )
    return vault_eval(js)


def move_lines(src_path: str, start: int, count: int,
               dst_path: str) -> str:
    """Move *count* lines from *src_path* (at *start*, 1-indexed) to
    the end of *dst_path*.  Two sequential writes — not atomic across
    files but safe as long as src != dst.
    """
    js = (
        "(async () => {"
        f"  const srcF = app.vault.getAbstractFileByPath(`{_js_escape(src_path)}`);"
        f"  const dstF = app.vault.getAbstractFileByPath(`{_js_escape(dst_path)}`);"
        "  if (!srcF) throw new Error('source not found');"
        "  if (!dstF) throw new Error('dest not found');"
        "  let moved = '';"
        "  await app.vault.process(srcF, (content) => {"
        "    const lines = content.split('\\n');"
        f"    moved = lines.splice({start - 1}, {count}).join('\\n');"
        "    return lines.join('\\n');"
        "  });"
        "  await app.vault.process(dstF, (content) => {"
        "    return content.trimEnd() + '\\n' + moved + '\\n';"
        "  });"
        "  return 'moved ' + moved.split('\\n')[0].trim();"
        "})()"
    )
    return vault_eval(js)


def get_line(path: str, line_num: int) -> str:
    """Read a single line (1-indexed) from *path* via eval."""
    js = (
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js_escape(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  const content = await app.vault.read(f);"
        f"  return content.split('\\n')[{line_num - 1}] || '';"
        "})()"
    )
    return vault_eval(js)


def get_lines(path: str) -> list[str]:
    """Read all lines of *path* via CLI and return as a list."""
    content = read_file(path=path)
    return content.split("\n")
