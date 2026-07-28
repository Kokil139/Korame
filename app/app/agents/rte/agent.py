"""
RTE (Requirements & Test Engineer) Agent.

Transforms high-level requirements into structured user stories with acceptance criteria.
Supports multi-turn clarification: if a requirement is ambiguous or incomplete, the agent
asks clarifying questions instead of generating a final user story.
"""

import os
import re
from typing import Any, Optional
from app.agents.base import BaseAgent
from app.kernel.models import Task, Response
from app.router.model_router import ModelRouter

# Matches a "STATUS: CLARIFICATION_NEEDED" or "STATUS: READY" line anywhere in the response.
_STATUS_PATTERN = re.compile(
    r"^[ \t]*STATUS:[ \t]*(CLARIFICATION_NEEDED|READY)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
# Matches numbered list items, e.g. "1. Question?" or "2) Question?"
_NUMBERED_ITEM_PATTERN = re.compile(r"^[ \t]*\d+[\.\)][ \t]*(.+)$", re.MULTILINE)


class RTEAgent(BaseAgent):
    """
    RTE Agent - Requirements & Test Engineer.

    Takes business requirements and generates detailed user stories. When a
    requirement is ambiguous or incomplete, the agent returns clarifying
    questions instead so the business user can respond in a follow-up turn.
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
If the requirement is ambiguous or incomplete, start your reply with "STATUS: CLARIFICATION_NEEDED"
followed by a numbered list of questions. Otherwise start your reply with "STATUS: READY" followed
by the story.

Generate a user story with:
- Title
- User story statement (As a... I want... So that...)
- Description
- Acceptance Criteria (at least 3)
- Technical Notes

User Input: {input}

Generate a well-structured user story based on this input."""

    def _build_prompt(self, requirement: str, history: str) -> str:
        """
        Build the full prompt sent to the model, including prior conversation turns.

        Args:
            requirement: The latest message from the business user
            history: Formatted prior conversation turns (may be empty)

        Returns:
            The complete prompt string
        """
        if history:
            return (
                f"{self.prompt_template}\n\n"
                f"## Conversation So Far\n{history}\n\n"
                f"USER: {requirement}"
            )
        return f"{self.prompt_template}\n\nUser Input: {requirement}"

    def _parse_response(self, raw: str) -> tuple[bool, list[str], str]:
        """
        Parse the model's raw output into structured clarification data.

        Args:
            raw: Raw text returned by the model

        Returns:
            Tuple of (needs_clarification, questions, content). ``content`` is
            the response text with the STATUS line removed.
        """
        match = _STATUS_PATTERN.search(raw)
        if not match:
            # Model didn't follow the format; treat the whole response as the
            # final answer rather than blocking the user.
            return False, [], raw.strip()

        status = match.group(1).upper()
        content = (raw[: match.start()] + raw[match.end():]).strip()
        needs_clarification = status == "CLARIFICATION_NEEDED"

        questions: list[str] = []
        if needs_clarification:
            questions = [q.strip() for q in _NUMBERED_ITEM_PATTERN.findall(content) if q.strip()]

        return needs_clarification, questions, content

    async def execute(self, task: Task) -> Response:
        """
        Execute an RTE task.

        Args:
            task: The task containing the business requirement

        Returns:
            Response containing either clarifying questions or the generated user story
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

            # Prior conversation turns (if any), formatted for the model
            history = task.input_data.get("history", "")

            # Build the prompt, including prior conversation turns if available
            prompt = self._build_prompt(requirement, history)

            # Get the provider from the router
            provider = self.model_router.route(task)

            # Call the model
            result = await provider.call(
                prompt,
                temperature=0.7,
                max_tokens=2000
            )

            needs_clarification, questions, content = self._parse_response(result)

            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="success",
                data={
                    "user_story": content,
                    "needs_clarification": needs_clarification,
                    "questions": questions,
                }
            )

        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="error",
                data={},
                error=f"RTE Agent failed: {str(e)}"
            )

