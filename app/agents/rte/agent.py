"""
RTE (Requirements & Test Engineer) Agent.

Transforms high-level requirements into structured user stories with acceptance criteria.
"""

import os
from typing import Any, Optional
from app.agents.base import BaseAgent
from app.kernel.models import Task, Response
from app.router.model_router import ModelRouter


class RTEAgent(BaseAgent):
    """
    RTE Agent - Requirements & Test Engineer.

    Takes business requirements and generates detailed user stories.
    """

    def __init__(self, model_router: ModelRouter, config: Optional[dict[str, Any]] = None):
        """
        Initialize the RTE agent.

        Args:
            model_router: Router for selecting model providers
            config: Optional configuration
        """
        super().__init__("rte", config or {})
        self.model_router = model_router
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load the RTE prompt from file."""
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "rte.md"
        )
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            # Fallback if file not found
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Get the default prompt if file can't be loaded."""
        return """You are an expert Requirements & Test Engineer (RTE).

Your job is to take high-level business requirements and generate clear, detailed user stories.

Generate a user story with:
- Title
- User story statement (As a... I want... So that...)
- Description
- Acceptance Criteria (at least 3)
- Technical Notes

User Input: {input}

Generate a well-structured user story based on this input."""

    async def execute(self, task: Task) -> Response:
        """
        Execute an RTE task.

        Args:
            task: The task containing the business requirement

        Returns:
            Response containing the generated user story
        """
        try:
            # Get the requirement from task input
            requirement = task.input_data.get("requirement", "")
            if not requirement:
                return Response(
                    task_id=task.id,
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="No requirement provided in task input"
                )

            # Build the prompt
            prompt = f"{self.prompt_template}\n\nUser Input: {requirement}"

            # Get the provider from the router
            provider = self.model_router.route(task)

            # Call the model
            result = await provider.call(
                prompt,
                temperature=0.7,
                max_tokens=2000
            )

            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="success",
                data={"user_story": result}
            )

        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="error",
                data={},
                error=f"RTE Agent failed: {str(e)}"
            )

