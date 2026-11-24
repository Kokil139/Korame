"""
Knowledge Agent.

Answers questions by searching the Knowledge Fabric's indexed application
documents (READMEs, specs, build notes, architecture docs, etc.) and
grounding its answer in the exact excerpts retrieved, rather than general
knowledge. Powers the floating "Knowledge Assistant" chat widget exposed on
every page.

Unlike RTE/Developer/Testing, this agent has no multi-step workflow: each
question is a single search-then-answer call, so execute() is its only
entry point.
"""

import os
from typing import Any, Optional
from app.agents.base import BaseAgent
from app.kernel.models import Task, Response
from app.router.model_router import ModelRouter


class KnowledgeAgent(BaseAgent):
    """Knowledge Agent - answers questions by searching the Knowledge Fabric."""

    def __init__(
        self,
        model_router: ModelRouter,
        knowledge_fabric: Any,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Args:
            model_router: Router for selecting model providers
            knowledge_fabric: KnowledgeFabric instance to search for answers
            config: Optional configuration
        """
        super().__init__("knowledge", config or {})
        self.model_router = model_router
        self.knowledge_fabric = knowledge_fabric
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load the Knowledge agent prompt from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "knowledge.md")
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Fallback prompt if the file can't be loaded."""
        return (
            "You are the Knowledge Fabric Assistant. Answer the user's question using "
            "only the provided Knowledge Base Context. Quote exact wording for facts, "
            "settings, and commands. If the context doesn't contain the answer, say so "
            "clearly instead of guessing."
        )

    def _search(self, question: str, limit: int = 6) -> list[dict[str, Any]]:
        """
        Search the knowledge fabric for excerpts relevant to the question.

        Uses full-text (keyword) search rather than semantic/hybrid: the
        default embedding provider is a dummy/random one unless a real
        embedding model is configured, which would otherwise pollute results
        with meaningless matches (same reasoning as
        RTEAgent._find_similar_requirements).

        Args:
            question: The user's question
            limit: Maximum number of excerpts to retrieve

        Returns:
            Search results with score > 0, most relevant first
        """
        try:
            results = self.knowledge_fabric.search(query=question, search_type="full_text", limit=limit)
        except Exception:
            return []
        return [r for r in results if r.get("score", 0) > 0]

    @staticmethod
    def _build_context_block(results: list[dict[str, Any]]) -> str:
        """Render search results into labeled excerpts for the prompt."""
        blocks = []
        for r in results:
            metadata = r.get("metadata") or {}
            source = metadata.get("source", r.get("title", "unknown"))
            start_line = metadata.get("start_line")
            end_line = metadata.get("end_line")
            location = f"(lines {start_line}-{end_line})" if start_line and end_line else ""
            content = (metadata.get("content") or "").strip()
            if not content:
                continue
            blocks.append(f"### Source: {source}{location}\n{content}")
        return "\n\n".join(blocks)

    @staticmethod
    def _build_sources(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Build a deduplicated, frontend-friendly list of cited sources."""
        sources: list[dict[str, Any]] = []
        seen: set[str] = set()
        for r in results:
            metadata = r.get("metadata") or {}
            source = metadata.get("source", r.get("title", "unknown"))
            if source in seen:
                continue
            seen.add(source)
            sources.append({
                "source": source,
                "start_line": metadata.get("start_line"),
                "end_line": metadata.get("end_line"),
                "score": round(r.get("score", 0), 3),
            })
        return sources

    def _build_prompt(self, question: str, history: str, context_block: str) -> str:
        """
        Build the full prompt sent to the model.

        Uses plain concatenation rather than str.format(): retrieved document
        excerpts routinely contain literal '{'/' }' characters (JSON, code,
        CSS), which would break template substitution.
        """
        sections = [self.prompt_template]

        sections.append(
            f"## Knowledge Base Context\n{context_block}"
            if context_block
            else "## Knowledge Base Context\n(No matching content was found in the knowledge base for this question.)"
        )

        if history:
            sections.append(f"## Conversation So Far\n{history}")

        sections.append(f"## Question\n{question}")
        return "\n\n".join(sections)

    async def execute(self, task: Task) -> Response:
        """
        Execute a knowledge-lookup task.

        Args:
            task: The task containing the user's question

        Returns:
            Response with the grounded answer and the sources it was based on
        """
        try:
            question = task.input_data.get("question", "").strip()
            if not question:
                return Response(
                    task_id=task.id,
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="No question provided in task input",
                )

            history = task.input_data.get("history", "")

            results = self._search(question)
            context_block = self._build_context_block(results)
            sources = self._build_sources(results)

            prompt = self._build_prompt(question, history, context_block)
            provider = self.model_router.route(task)

            # A grounded lookup/synthesis task, not rigid format generation -
            # benefits from thinking the same way RTE's judgment calls do.
            # Lower temperature than RTE since factual grounding matters more
            # here than creative phrasing.
            answer = await provider.call(
                prompt,
                temperature=0.3,
                max_tokens=12000,
                think=True,
            )

            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="success",
                data={
                    "answer": answer.strip(),
                    "sources": sources,
                    "found_context": bool(context_block),
                },
            )
        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="error",
                data={},
                error=str(e),
            )