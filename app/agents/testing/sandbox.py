"""
Isolated sandbox for executing Developer Agent code and Testing Agent tests.

Generated code is written under the OS temp directory (never inside the repo)
and cleaned up after each run. It must live outside the repo: when running the
server with `uvicorn --reload`, its file watcher would otherwise pick up every
generated implementation.py as a source change and restart the whole app -
wiping the in-memory TodoStore mid-workflow and turning every subsequent
GET /api/v1/todos/{id} poll into a 404. pytest executes as a subprocess with a
timeout, using the SAME Python interpreter running the server (so it shares
the same environment/dependencies).

Security note: this executes LLM-generated code. It is isolated to a
dedicated, per-run temp folder and bounded by a timeout, but this is
process-level isolation, not a full container/VM sandbox. For a production
deployment, consider running this inside a properly sandboxed/containerized
environment instead.
"""

import asyncio
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass

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

    async def run_pytest(self, timeout: int = 30) -> TestExecutionResult:
        """
        Run pytest against everything in this sandbox and capture the result.

        Args:
            timeout: Maximum seconds to allow the test run before killing it

        Returns:
            TestExecutionResult with pass/fail, combined output, and exit code
        """
        os.makedirs(self.path, exist_ok=True)
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pytest", ".", "-q",
                cwd=self.path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except NotImplementedError as e:
            # Raised (with no message at all) when the active asyncio event
            # loop doesn't support subprocess creation - the classic Windows
            # Selector-vs-Proactor event loop gotcha. app/main.py sets the
            # Proactor policy on Windows to prevent this; if it still happens,
            # something else in the process is overriding that policy.
            raise RuntimeError(
                "Could not start the pytest subprocess: the current asyncio "
                "event loop does not support subprocess creation (on Windows, "
                "this means the Selector event loop is active instead of "
                "Proactor)."
            ) from e
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return TestExecutionResult(passed=False, output="Test execution timed out", returncode=-1)

        output = stdout.decode("utf-8", errors="replace")
        return TestExecutionResult(
            passed=proc.returncode == 0,
            output=output,
            returncode=proc.returncode if proc.returncode is not None else -1,
        )

    def cleanup(self) -> None:
        """Remove the sandbox directory."""
        if os.path.exists(self.path):
            shutil.rmtree(self.path, ignore_errors=True)
