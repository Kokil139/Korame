"""
Isolated sandbox for executing Developer Agent code and Testing Agent tests.

Generated code is written under the OS temp directory (never inside the repo)
and cleaned up after each run. It must live outside the repo: when running the
server with `uvicorn --reload`, its file watcher would otherwise pick up every
generated implementation.py as a source change and restart the whole app -
wiping the in-memory TodoStore mid-workflow and turning every subsequent
GET /api/v1/todos/{id} poll into a 404. pytest runs as a plain, synchronous
`subprocess.run()` call inside a worker thread (via asyncio.to_thread) rather
than asyncio.create_subprocess_exec() - the latter requires the Proactor
event loop on Windows and raises a bare NotImplementedError if a Selector
loop is active instead, which some ASGI server setups end up using
regardless of the event loop policy set at process startup. Running a
normal blocking subprocess in a thread sidesteps that entirely, using the
SAME Python interpreter running the server (so it shares the same
environment/dependencies).

Security note: this executes LLM-generated code. It is isolated to a
dedicated, per-run temp folder and bounded by a timeout, but this is
process-level isolation, not a full container/VM sandbox. For a production
deployment, consider running this inside a properly sandboxed/containerized
environment instead.
"""

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Optional

_WORKSPACE_ROOT = os.path.join(tempfile.gettempdir(), "korame-workspace")


@dataclass
class TestExecutionResult:
    """Result of running pytest against a sandboxed implementation."""
    passed: bool
    output: str
    returncode: int


class Sandbox:
    """A single isolated working directory for one implementation/test run."""

    def __init__(self, run_id: str):
        """
        Args:
            run_id: Identifier for this run; sanitized to be filesystem-safe
        """
        safe_id = "".join(c for c in run_id if c.isalnum() or c in ("-", "_")) or "run"
        self.run_id = safe_id
        self.path = os.path.join(_WORKSPACE_ROOT, safe_id)

    def write_file(self, relative_path: str, content: str) -> str:
        """Write a file inside the sandbox, creating parent directories as needed."""
        full_path = os.path.join(self.path, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return full_path

    async def run_pytest(self, target: Optional[str] = None, timeout: int = 30) -> TestExecutionResult:
        """
        Run pytest against a specific target within this sandbox, or
        everything in it if no target is given.

        Args:
            target: A specific test file (relative to the sandbox root) to
                run - e.g. "test_contact_form.py" - so only the task
                currently being graded is run, rather than re-running every
                other already-passing task's tests on every single retry.
                Omit to run the whole directory (e.g. for a final sanity pass).
            timeout: Maximum seconds to allow the test run before killing it

        Returns:
            TestExecutionResult with pass/fail, combined output, and exit code
        """
        os.makedirs(self.path, exist_ok=True)

        def _run() -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, "-m", "pytest", target or ".", "-q", "--tb=short"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

        try:
            # subprocess.run(timeout=...) kills the process for us on timeout,
            # unlike asyncio's subprocess transport which needed manual
            # proc.kill()/proc.wait() - this is simpler as well as more portable.
            result = await asyncio.to_thread(_run)
        except subprocess.TimeoutExpired:
            return TestExecutionResult(passed=False, output="Test execution timed out", returncode=-1)

        output = (result.stdout or "") + (result.stderr or "")
        return TestExecutionResult(
            passed=result.returncode == 0,
            output=output,
            returncode=result.returncode if result.returncode is not None else -1,
        )

    def cleanup(self) -> None:
        """Remove the sandbox directory."""
        if os.path.exists(self.path):
            shutil.rmtree(self.path, ignore_errors=True)
