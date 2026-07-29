"""
Testing Agent.

Writes real pytest test cases for a Developer Agent implementation and
executes them in an isolated sandbox - returning genuine pass/fail results
rather than an LLM's opinion about whether the code looks right.
"""

import os
import re
from typing import Any, Optional
from app.agents.base import BaseAgent
from app.kernel.models import Task, Response
from app.router.model_router import ModelRouter
from app.agents.testing.sandbox import Sandbox

_CODE_BLOCK_PATTERN = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


class TestingAgent(BaseAgent):
    """Testing Agent - generates and executes real tests against Developer Agent code."""

    def __init__(self, model_router: ModelRouter, config: Optional[dict[str, Any]] = None):
        """
        Args:
            model_router: Router for selecting model providers
            config: Optional configuration
        """
        super().__init__("testing", config or {})
        self.model_router = model_router
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load the Testing agent prompt from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "testing.md")
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Fallback prompt if the file can't be loaded."""
        return (
            "You are an expert software tester. Write pytest test cases that import "
            "from `implementation` and verify it against the given task. Respond with "
            "only a Python code block."
        )

    async def generate_tests(
        self,
        task_title: str,
        code: str,
        file_type: str = "python",
        prior_error: Optional[str] = None,
    ) -> str:
        """
        Ask the model to write pytest tests for the given implementation.

        Args:
            task_title: Description of the task the code should satisfy
            code: The implementation to test
            file_type: "python" (default) or "html" - an HTML page can't be
                `import`-ed like a module, so it needs a different testing
                strategy (structural assertions on the file's raw text).
            prior_error: If the last generated test failed to even run (e.g.
                it imported an unavailable package), the pytest collection
                error, so this attempt can be told specifically what to avoid.

        Returns:
            Generated pytest test source code
        """
        provider = self.model_router.default_provider
        if file_type == "html":
            implementation_section = (
                f"## Implementation (saved as implementation.html)\n```html\n{code}\n```\n\n"
            )
            strategy = (
                "This implementation is a standalone HTML page, not a Python module - "
                "it cannot be imported. Write pytest test cases in a single file that "
                "open() and read implementation.html as plain text (optionally using "
                "the standard library's html.parser), then assert on the specific "
                "structure/content the task requires. Do not try to import the HTML "
                "file, and do not use a browser, Selenium, or any package outside the "
                "Python standard library."
            )
        else:
            implementation_section = (
                f"## Implementation (saved as implementation.py)\n```python\n{code}\n```\n\n"
            )
            strategy = (
                "Write pytest test cases in a single file that `import implementation` "
                "(or `from implementation import ...`) and verify the task is correctly "
                "implemented."
            )

        error_section = ""
        if prior_error:
            error_section = (
                "\n\n## Your Previous Test Failed To Even Run\n"
                f"Collection error:\n{prior_error}\n\n"
                "This means the TEST CODE ITSELF has a problem (most likely it "
                "imported a package that isn't installed) - the implementation was "
                "never actually exercised. Fix the test so it runs: import ONLY from "
                "Python's standard library (e.g. re, html.parser, json, os, "
                "unittest.mock) plus `pytest` and `implementation` itself. Do NOT "
                "import bs4/BeautifulSoup, requests, selenium, playwright, lxml, "
                "flask, or any other third-party package."
            )

        prompt = (
            f"{self.prompt_template}\n\n"
            f"## Task\n{task_title}\n\n"
            f"{implementation_section}"
            f"{strategy}{error_section} Respond with ONLY the test code in a fenced Python code block."
        )
        result = await provider.call(prompt, temperature=0.3, max_tokens=1500)
        return self._extract_code(result)

    async def run_tests(self, run_id: str, task_title: str, code: str, file_type: str = "python") -> dict[str, Any]:
        """
        Write the implementation and generated tests into an isolated sandbox and
        actually execute pytest against them.

        If the generated test itself fails to even run (e.g. it imported a
        package that isn't installed, despite being told to use only the
        standard library), that's this agent's own mistake, not a real finding
        about the implementation - retrying the Developer's code would be
        pointless since the test never actually ran against it. In that case,
        test generation gets one do-over with the specific error, keeping the
        same implementation, before falling back to reporting whatever happened.

        Args:
            run_id: Unique ID for this test run (used as the sandbox folder name)
            task_title: Description of the task the code should satisfy
            code: The implementation to test
            file_type: "python" (default) or "html" - determines the saved
                implementation file's extension and the testing strategy used

        Returns:
            Dict with `passed`, `output` (pytest output), and `test_code` (what was run)
        """
        sandbox = Sandbox(run_id)
        try:
            impl_filename = "implementation.html" if file_type == "html" else "implementation.py"
            sandbox.write_file(impl_filename, code)
            test_code = await self.generate_tests(task_title, code, file_type)
            sandbox.write_file("test_implementation.py", test_code)
            result = await sandbox.run_pytest()

            if not result.passed and self._looks_like_test_infra_failure(result.output):
                test_code = await self.generate_tests(task_title, code, file_type, prior_error=result.output)
                sandbox.write_file("test_implementation.py", test_code)
                result = await sandbox.run_pytest()

            return {"passed": result.passed, "output": result.output, "test_code": test_code}
        finally:
            sandbox.cleanup()

    @staticmethod
    def _looks_like_test_infra_failure(output: str) -> bool:
        """
        Distinguish "the test code itself couldn't even run" (this agent's own
        mistake, e.g. importing an unavailable package, or attempting to
        `import` a file that isn't actually valid Python) from a genuine test
        failure (an assertion against the implementation that actually ran).
        Only the former is worth retrying test generation for - a real
        assertion failure needs to go back to the Developer instead.
        """
        markers = (
            "ModuleNotFoundError",
            "ImportError",
            "SyntaxError",
            "ERROR collecting",
            "during collection",
        )
        return any(marker in output for marker in markers)

    @staticmethod
    def _extract_code(text: str) -> str:
        """Pull the code out of a fenced ```python ...``` block, if present."""
        match = _CODE_BLOCK_PATTERN.search(text)
        return match.group(1).strip() if match else text.strip()

    async def execute(self, task: Task) -> Response:
        """
        Single-shot entry point (e.g. via POST /api/v1/chat with agent_name="testing"):
        generates and runs tests for whatever code is passed in task input.
        """
        try:
            task_title = task.input_data.get("task_title", "")
            code = task.input_data.get("code", "")
            run_id = task.input_data.get("run_id", task.id)
            file_type = task.input_data.get("file_type", "python")
            if not code:
                return Response(
                    task_id=task.id,
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="No code provided to test",
                )

            result = await self.run_tests(run_id, task_title, code, file_type)
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="success",
                data=result,
            )
        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="error",
                data={},
                error=f"Testing Agent failed: {str(e)}",
            )
