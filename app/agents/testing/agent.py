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

_CODE_BLOCK_PATTERN = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


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

    async def generate_tests(self, task_title: str, code: str) -> str:
        """
        Ask the model to write pytest tests for the given implementation.

        Args:
            task_title: Description of the task the code should satisfy
            code: The implementation to test

        Returns:
            Generated pytest test source code
        """
        provider = self.model_router.default_provider
        prompt = (
            f"{self.prompt_template}\n\n"
            f"## Task\n{task_title}\n\n"
            f"## Implementation (saved as implementation.py)\n```python\n{code}\n```\n\n"
            "Write pytest test cases in a single file that `import implementation` "
            "(or `from implementation import ...`) and verify the task is correctly "
            "implemented. Respond with ONLY the test code in a fenced Python code block."
        )
        result = await provider.call(prompt, temperature=0.3, max_tokens=1500)
        return self._extract_code(result)

    async def run_tests(self, run_id: str, task_title: str, code: str) -> dict[str, Any]:
        """
        Write the implementation and generated tests into an isolated sandbox and
        actually execute pytest against them.

        Args:
            run_id: Unique ID for this test run (used as the sandbox folder name)
            task_title: Description of the task the code should satisfy
            code: The implementation to test

        Returns:
            Dict with `passed`, `output` (pytest output), and `test_code` (what was run)
        """
        sandbox = Sandbox(run_id)
        try:
            sandbox.write_file("implementation.py", code)
            test_code = await self.generate_tests(task_title, code)
            sandbox.write_file("test_implementation.py", test_code)
            result = await sandbox.run_pytest()
            return {"passed": result.passed, "output": result.output, "test_code": test_code}
        finally:
            sandbox.cleanup()

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
            if not code:
                return Response(
                    task_id=task.id,
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="No code provided to test",
                )

            result = await self.run_tests(run_id, task_title, code)
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
