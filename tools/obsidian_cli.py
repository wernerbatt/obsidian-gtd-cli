#!/usr/bin/env python3
"""
Thin eval helpers for Obsidian vault mutations that the CLI doesn't
support natively (line-level edits, deletes, moves).

For everything else — reads, appends, creates, searches, task queries —
use the Obsidian CLI directly.  See .claude/skills/obsidian/SKILL.md.
"""

import json
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate the binary
# ---------------------------------------------------------------------------

_OBSIDIAN_BIN = None


def _find_obsidian_bin():
    global _OBSIDIAN_BIN
    if _OBSIDIAN_BIN:
        return _OBSIDIAN_BIN

    win_exe = Path("/usr/local/bin/obsidian")
    if win_exe.exists():
        _OBSIDIAN_BIN = str(win_exe)
        return _OBSIDIAN_BIN

    import shutil
    found = shutil.which("obsidian")
    if found:
        _OBSIDIAN_BIN = found
        return _OBSIDIAN_BIN

    raise FileNotFoundError("Cannot find Obsidian CLI binary.")


_VAULT_NAME = "Obsidian"


def set_vault(name: str):
    global _VAULT_NAME
    _VAULT_NAME = name


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run(*args: str, timeout: int = 30) -> str:
    cmd = [_find_obsidian_bin(), f"vault={_VAULT_NAME}"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    lines = [
        l for l in result.stdout.splitlines()
        if not (l.startswith("202") and "Loading updated app package" in l)
        and not l.startswith("Your Obsidian installer is out of date")
    ]
    stdout = "\n".join(lines).strip()
    if result.returncode not in (0, 1):
        raise subprocess.CalledProcessError(result.returncode, cmd, stdout, result.stderr)
    return stdout


def vault_eval(code: str, *, timeout: int = 30) -> str:
    return _run("eval", f"code={code}", timeout=timeout)


def _js(s: str) -> str:
    """Escape a string for embedding in a JS backtick literal."""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


# ---------------------------------------------------------------------------
# Eval helpers — line-level mutations via app.vault.process()
# ---------------------------------------------------------------------------

def edit_line(path: str, line_num: int, new_text: str) -> str:
    """Replace a single line (1-indexed) in *path*."""
    return vault_eval(
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, c => {"
        "    const L = c.split('\\n');"
        f"    L[{line_num - 1}] = `{_js(new_text)}`;"
        "    return L.join('\\n');"
        "  });"
        f"  return 'edited line {line_num}';"
        "})()"
    )


def delete_lines(path: str, start: int, count: int = 1) -> str:
    """Delete *count* lines starting at *start* (1-indexed)."""
    return vault_eval(
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, c => {"
        "    const L = c.split('\\n');"
        f"    L.splice({start - 1}, {count});"
        "    return L.join('\\n');"
        "  });"
        f"  return 'deleted {count} line(s) from {start}';"
        "})()"
    )


def replace_by_match(path: str, old_text: str, new_text: str) -> str:
    """Replace first occurrence of *old_text* with *new_text* in *path*."""
    return vault_eval(
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, c => {"
        f"    const from_ = `{_js(old_text)}`;"
        f"    const to_ = `{_js(new_text)}`;"
        "    if (!c.includes(from_)) throw new Error('text not found');"
        "    return c.replace(from_, to_);"
        "  });"
        "  return 'replaced';"
        "})()"
    )


def insert_after_heading(path: str, heading: str, text: str) -> str:
    """Insert *text* at the end of the section under *heading*."""
    return vault_eval(
        "(async () => {"
        f"  const f = app.vault.getAbstractFileByPath(`{_js(path)}`);"
        "  if (!f) throw new Error('file not found');"
        "  await app.vault.process(f, c => {"
        "    const L = c.split('\\n');"
        f"    const heading = `{_js(heading)}`;"
        "    const re = new RegExp('^#{1,6}\\\\s+' + heading.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + '\\\\s*$');"
        "    let idx = -1;"
        "    for (let i = 0; i < L.length; i++) { if (re.test(L[i])) { idx = i; break; } }"
        "    if (idx === -1) throw new Error('heading not found');"
        "    let ins = idx + 1;"
        "    for (let i = idx + 1; i < L.length; i++) { if (/^#{1,6}\\s/.test(L[i])) break; ins = i + 1; }"
        f"    L.splice(ins, 0, `{_js(text)}`);"
        "    return L.join('\\n');"
        "  });"
        "  return 'inserted';"
        "})()"
    )


def move_lines(src_path: str, start: int, count: int, dst_path: str) -> str:
    """Move *count* lines from *src_path* to end of *dst_path*."""
    return vault_eval(
        "(async () => {"
        f"  const s = app.vault.getAbstractFileByPath(`{_js(src_path)}`);"
        f"  const d = app.vault.getAbstractFileByPath(`{_js(dst_path)}`);"
        "  if (!s) throw new Error('source not found');"
        "  if (!d) throw new Error('dest not found');"
        "  let moved = '';"
        "  await app.vault.process(s, c => {"
        "    const L = c.split('\\n');"
        f"    moved = L.splice({start - 1}, {count}).join('\\n');"
        "    return L.join('\\n');"
        "  });"
        "  await app.vault.process(d, c => c.trimEnd() + '\\n' + moved + '\\n');"
        "  return 'moved';"
        "})()"
    )
