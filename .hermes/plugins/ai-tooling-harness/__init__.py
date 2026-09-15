"""Hermes harness adapter for this repo — the counterpart of the opencode plugins.

Both halves call the SAME scripts CI (`make check`) calls, so no gate logic is
duplicated per harness: the commit gate runs `make check-data` (#459) and the auto-sync
half runs `./sync-plugin-docs.sh`. Only the *trigger* is harness-shaped; it is pinned by
TestHermesHarnessAdapter in test_automation.py.

Nothing here loads unless a human opts in, per machine:

    HERMES_ENABLE_PROJECT_PLUGINS=true
    hermes plugins enable ai-tooling-harness

Project-local plugins are disabled by default on purpose — see
docs/agents/hermes-harness.md.
"""

import base64
import subprocess
from pathlib import Path

# <repo>/.hermes/plugins/ai-tooling-harness/__init__.py -> <repo>. Resolved from the
# file rather than the process cwd, which may be anywhere. Module-level so the tests
# can point it at a fixture.
REPO = Path(__file__).resolve().parents[3]

_WRITE_HINTS = ("write", "edit", "patch")
_PATH_KEYS = ("path", "file_path", "filePath", "file")
_WATCH_CACHE = {}

# The one commit predicate. Literal and metacharacter-free, so it is the same plain
# substring match as the opencode adapter's COMMIT_RE (TestHookTriggerSeam pins both).
COMMIT_PREDICATE = "git commit"

# Probed BEFORE the gate runs: `make` cannot signal "could not run" through its exit
# code — it exits non-zero for an absent target and for a real finding alike — so
# "could not run is not failed" is decided here, never inferred from the result.
_PROBE = (
    'command -v make >/dev/null 2>&1 && command -v uv >/dev/null 2>&1 '
    '&& grep -q "^check-data:" Makefile'
)

_DIAG_LIMIT = 4000


def _run(argv):
    """A subprocess that never raises: a toolchain that cannot run must not break a
    session, and must never be read as a failed gate."""
    try:
        return subprocess.run(
            argv, cwd=REPO, capture_output=True, text=True, timeout=120, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _watch_set():
    """The syncable set, DERIVED from `--list-watched` — the one definition (#194), never
    restated here. Cached only on success, so a transient failure does not disable
    auto-sync for the rest of the session."""
    if "watch" in _WATCH_CACHE:
        return _WATCH_CACHE["watch"]
    result = _run(["bash", "./sync-plugin-docs.sh", "--list-watched"])
    if result is None or result.returncode != 0:
        return (set(), ())  # fail-open: an empty watch set means "never trigger"
    files, dirs = set(), []
    for raw in (result.stdout or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.endswith("/"):
            dirs.append(line[:-1])
        else:
            files.add(line)
    _WATCH_CACHE["watch"] = (files, tuple(dirs))
    return _WATCH_CACHE["watch"]


def _edited_path(params):
    if not isinstance(params, dict):
        return ""
    for key in _PATH_KEYS:
        value = params.get(key)
        if isinstance(value, str):
            return value
    return ""


def _is_syncable(path, watched):
    files, dirs = watched
    if not path:
        return False
    norm = path.replace("\\", "/")
    if norm.startswith("plugin/docs/") or "/plugin/docs/" in norm:
        return False  # already the derived copy — syncing it would loop
    if norm.rsplit("/", 1)[-1] in files:
        return True
    return any(f"/{d}/" in norm or norm.startswith(f"{d}/") for d in dirs)


def _auto_sync(tool_name=None, args=None, result=None, **kwargs):
    """`post_tool_call` hook: re-run `./sync-plugin-docs.sh` after an edit to a root doc
    it mirrors, so `plugin/docs/` never drifts during a session. Silent and fail-open —
    the same contract as the opencode adapter.

    The second parameter is `args`, NOT `params`: Hermes calls plugin hooks by KEYWORD
    with the documented `post_tool_call` payload (`tool_name`, `args`, `result`,
    `task_id`, `session_id`, `duration_ms`, ...). A hook that names it anything else
    receives None and silently never fires.
    """
    del result, kwargs
    if not any(hint in (tool_name or "").lower() for hint in _WRITE_HINTS):
        return
    if not _is_syncable(_edited_path(args), _watch_set()):
        return
    _run(["bash", "./sync-plugin-docs.sh"])


def _commit_gate(tool_name=None, args=None, **kwargs):
    """`tool_request` middleware: rewrite a `git commit` into a diagnostic echo when
    `make check-data` fails, so the agent reads the failure instead of retrying."""
    del tool_name, kwargs
    if not isinstance(args, dict):
        return None
    command = args.get("command")
    if not isinstance(command, str) or COMMIT_PREDICATE not in command:
        return None

    probe = _run(["sh", "-c", _PROBE])
    if probe is None or probe.returncode != 0:
        return None  # cannot run -> never block

    gate = _run(["make", "--no-print-directory", "check-data"])
    if gate is None or gate.returncode == 0:
        return None  # gates clean, or unrunnable -> allow the commit unchanged

    diag = ((gate.stderr or "") + (gate.stdout or ""))[:_DIAG_LIMIT]
    payload = base64.b64encode(diag.encode("utf-8", "replace")).decode("ascii")
    blocked = (
        "echo \"BLOCKED by Hermes commit-gate: 'make check-data' failed before "
        "'git commit' — fix the tree, then re-run the commit.\" ; "
        f"printf '%s' '{payload}' | base64 -d"
    )
    return {
        "args": {**args, "command": blocked},
        "source": "ai-tooling-harness",
        "reason": "make check-data failed before git commit",
    }


def register(ctx):
    ctx.register_middleware("tool_request", _commit_gate)
    ctx.register_hook("post_tool_call", _auto_sync)
