"""
RTE (Requirements & Test Engineer) Agent.

Transforms high-level requirements into structured user stories with acceptance criteria.
Supports multi-turn clarification: if a requirement is ambiguous or incomplete, the agent
asks clarifying questions instead of generating a final user story. When a Knowledge
Fabric is available, the agent also looks up similar past requirements and can surface
suggestions, and stores finalized stories back into the knowledge base for future reuse.
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
# Matches a "SUGGESTIONS:" section header; everything after it (to end of content) is the body.
_SUGGESTIONS_HEADER_PATTERN = re.compile(r"^[ \t]*SUGGESTIONS:[ \t]*$", re.IGNORECASE | re.MULTILINE)
# Matches bullet list items, e.g. "- suggestion" or "* suggestion"
_BULLET_ITEM_PATTERN = re.compile(r"^[ \t]*[-*][ \t]*(.+)$", re.MULTILINE)
# Splits a Format-B reply into individual story blocks when RTE decided the
# requirement needed multiple independent stories (see rte.md instructions).
_STORY_SEPARATOR_PATTERN = re.compile(r"^[ \t]*-{3,}[ \t]*$", re.MULTILINE)


def _extract_title(content: str, fallback: str) -> str:
    """
    Find the story's title line and return the text after its first colon.

    Looks for any line mentioning "user story title" rather than requiring one
    exact markdown pattern - small local models don't always format it exactly
    as "**User Story Title**:" (the colon sometimes ends up inside the bold
    markers instead, e.g. "**User Story Title:**"). Strips markdown emphasis
    characters from the result. Falls back to the given text if no such line
    is found at all.
    """
    for line in content.splitlines():
        if "user story title" in line.lower() and ":" in line:
            title = line.split(":", 1)[1].replace("*", "").strip()
            if title:
                return title
    return fallback


class RTEAgent(BaseAgent):
    """
    RTE Agent - Requirements & Test Engineer.

    Takes business requirements and generates detailed user stories. When a
    requirement is ambiguous or incomplete, the agent returns clarifying
    questions instead so the business user can respond in a follow-up turn.
    """

    def __init__(
        self,
        model_router: ModelRouter,
        knowledge_fabric: Optional[Any] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the RTE agent.

        Args:
            model_router: Router for selecting model providers
            knowledge_fabric: Optional KnowledgeFabric instance used to look up
                similar past requirements and to store finalized stories. When
                omitted, the agent works exactly as before (no suggestions).
            config: Optional configuration
        """
        super().__init__("rte", config or {})
        self.model_router = model_router
        self.knowledge_fabric = knowledge_fabric
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
followed by only as many numbered questions as there are real gaps (zero to five - never a fixed
count out of habit). Otherwise start your reply with "STATUS: READY" followed by the story.

Generate a user story with:
- Title
- User story statement (As a... I want... So that...)
- Description
- Acceptance Criteria (at least 3)
- Technical Notes

User Input: {input}

Generate a well-structured user story based on this input."""

    def _find_similar_requirements(self, requirement: str, conversation_id: str) -> list[dict[str, Any]]:
        """
        Look up similar past finalized requirements in the knowledge fabric.

        Uses full-text (keyword) search rather than semantic/vector search: the
        default embedding provider is a dummy/random one, so semantic search
        would produce meaningless matches until a real embedding provider is
        configured. Full-text search is real and dependency-free.

        Args:
            requirement: The current business requirement text
            conversation_id: Current conversation ID (excluded from results so
                the agent doesn't "suggest" the conversation's own story)

        Returns:
            Up to 3 similar past requirements as dicts with title/description/score
        """
        if not self.knowledge_fabric:
            return []

        try:
            results = self.knowledge_fabric.search(query=requirement, search_type="full_text", limit=5)
        except Exception:
            return []

        similar: list[dict[str, Any]] = []
        for result in results:
            if result.get("score", 0) <= 0:
                continue
            if result.get("metadata", {}).get("conversation_id") == conversation_id:
                continue
            similar.append(result)
            if len(similar) == 3:
                break
        return similar

    def _build_prompt(self, requirement: str, history: str, similar: list[dict[str, Any]]) -> str:
        """
        Build the full prompt sent to the model, including prior conversation turns
        and any similar past requirements found in the knowledge fabric.

        Args:
            requirement: The latest message from the business user
            history: Formatted prior conversation turns (may be empty)
            similar: Similar past requirements (may be empty)

        Returns:
            The complete prompt string
        """
        sections = [self.prompt_template]

        if history:
            sections.append(f"## Conversation So Far\n{history}")

        if similar:
            lines = ["## Similar Past Requirements (from the knowledge base)"]
            for item in similar:
                lines.append(f"- \"{item['title']}\" — {item['description']}")
            sections.append("\n".join(lines))

        sections.append(f"USER: {requirement}" if history else f"User Input: {requirement}")
        return "\n\n".join(sections)

    def _parse_response(self, raw: str) -> tuple[bool, list[str], list[str], str]:
        """
        Parse the model's raw output into structured clarification/suggestion data.

        Args:
            raw: Raw text returned by the model

        Returns:
            Tuple of (needs_clarification, questions, suggestions, content).
            ``content`` is the response text with the STATUS line and any
            SUGGESTIONS section removed.
        """
        match = _STATUS_PATTERN.search(raw)
        if not match:
            # Model didn't follow the format; treat the whole response as the
            # final answer rather than blocking the user.
            return False, [], [], raw.strip()

        status = match.group(1).upper()
        content = (raw[: match.start()] + raw[match.end():]).strip()
        needs_clarification = status == "CLARIFICATION_NEEDED"

        # Pull out an optional SUGGESTIONS section so it doesn't pollute the
        # main story/question text shown to the user.
        suggestions: list[str] = []
        suggestions_match = _SUGGESTIONS_HEADER_PATTERN.search(content)
        if suggestions_match:
            body = content[suggestions_match.end():]
            suggestions = [s.strip() for s in _BULLET_ITEM_PATTERN.findall(body) if s.strip()]
            content = content[: suggestions_match.start()].strip()

        questions: list[str] = []
        if needs_clarification:
            questions = [q.strip() for q in _NUMBERED_ITEM_PATTERN.findall(content) if q.strip()]

        return needs_clarification, questions, suggestions, content

    def _store_finalized_story(self, requirement: str, content: str, conversation_id: str, artifact_id: str) -> None:
        """
        Persist a finalized user story into the knowledge fabric so future
        requirements can find it as a "similar past requirement". Best-effort:
        indexing failures never fail the overall request.
        """
        if not self.knowledge_fabric:
            return

        title = _extract_title(content, fallback=requirement[:80])

        try:
            self.knowledge_fabric.create_artifact(
                artifact_id=artifact_id,
                artifact_type="user_story",
                title=title,
                description=requirement,
                created_by="rte_agent",
                content=content,
                metadata={"conversation_id": conversation_id},
            )
        except Exception:
            pass

    @staticmethod
    def _split_stories(content: str) -> list[str]:
        """
        Split a Format-B reply into individual story blocks. Most replies are
        a single story (returned as a one-element list); when RTE decides a
        requirement needs multiple independent stories, they're separated by
        a line containing only "---".
        """
        parts = _STORY_SEPARATOR_PATTERN.split(content)
        return [p.strip() for p in parts if p.strip()]

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
            conversation_id = task.input_data.get("conversation_id", "")

            # Look up similar past requirements in the knowledge fabric (if configured)
            similar = self._find_similar_requirements(requirement, conversation_id)

            # Build the prompt, including prior conversation turns and similar requirements
            prompt = self._build_prompt(requirement, history, similar)

            # Get the provider from the router
            provider = self.model_router.route(task)

            # Call the model. Unlike the Developer/Testing agents' structural,
            # format-bound calls (numbered lists, code blocks - hurt more than
            # helped by a model "thinking" through a tight token budget), RTE
            # judges ambiguity, decides how many clarifying questions are
            # genuinely needed, and now also judges revision-vs-new-requirement
            # and single-vs-multiple-story splits - real deliberation that
            # benefits from thinking. It also has a generous 3000-token budget
            # (raised from 2000 to leave room for multi-story replies) and was
            # confirmed working well before the Developer-side truncation
            # issue was ever found, so there's no evidence it needs thinking
            # disabled too.
            result = await provider.call(
                prompt,
                temperature=0.7,
                max_tokens=3000,
                think=True,
            )

            needs_clarification, questions, suggestions, content = self._parse_response(result)

            # Once a story is finalized, split out and store each one (usually
            # just one) so it/they can inform future requirements.
            stories = self._split_stories(content) if not needs_clarification else []
            for i, story_content in enumerate(stories):
                artifact_id = task.id if len(stories) == 1 else f"{task.id}-{i}"
                self._store_finalized_story(requirement, story_content, conversation_id, artifact_id)

            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="success",
                data={
                    "user_story": content,
                    "needs_clarification": needs_clarification,
                    "questions": questions,
                    "suggestions": suggestions,
                    "stories": stories,
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

