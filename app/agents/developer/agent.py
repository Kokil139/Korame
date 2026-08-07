"""
Developer Agent.

Takes a finalized user story from the RTE agent and breaks it into an ordered
todo list of small, implementable tasks. Implements each task, revises it when
the Testing Agent reports failures, and - once every task in the list passes -
opens a pull request with the generated code.

The step-by-step loop (implement -> test -> revise -> ... -> PR) is
orchestrated by WorkflowEngine.execute_development_cycle(), which calls the
methods on this agent directly; execute() itself only handles the "break a
story into a todo list" step, for simple one-off use via the generic
POST /api/v1/chat endpoint.
"""

import os
import ast
import re
import uuid
from typing import Any, Optional
from app.agents.base import BaseAgent
from app.kernel.models import Task, Response
from app.router.model_router import ModelRouter
from app.knowledge.todos import TodoStore, TodoList, TodoItem

_NUMBERED_ITEM_PATTERN = re.compile(r"^[ \t]*\d+[\.\)][ \t]*(.+)$", re.MULTILINE)
_CODE_BLOCK_PATTERN = re.compile(r"```(?:python|html)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
# Defensively strips a redundant "Title:"/"Task:"/"Step:" label some models
# prepend to a task line despite being told not to (see prompts/developer.md).
_LABEL_PREFIX_PATTERN = re.compile(r"^(?:title|task|step)\s*:\s*", re.IGNORECASE)
_HTML_SIGNATURE_PATTERN = re.compile(r"<!DOCTYPE\s+html|<html[\s>]", re.IGNORECASE)


class DeveloperAgent(BaseAgent):
    """Developer Agent - breaks stories into tasks, implements them, and opens PRs."""

    def __init__(
        self,
        model_router: ModelRouter,
        todo_store: TodoStore,
        github_service: Optional[Any] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Args:
            model_router: Router for selecting model providers
            todo_store: Shared store of todo lists (also read by status-polling endpoints)
            github_service: Optional GitHubService used to open pull requests
            config: Optional configuration
        """
        super().__init__("developer", config or {})
        self.model_router = model_router
        self.todo_store = todo_store
        self.github_service = github_service
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load the Developer agent prompt from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "developer.md")
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Fallback prompt if the file can't be loaded."""
        return (
            "You are an expert software developer. Break the given user story into a "
            "numbered list of small, independently implementable engineering tasks. "
            "When asked to implement one, respond with only a Python code block."
        )

    def start_run(self, story_title: str) -> TodoList:
        """
        Create an empty todo list "shell" immediately - no LLM call - so a
        caller gets a todo_list_id to start polling right away, before the
        story has even been broken into tasks yet. Call populate_todo_list()
        next to actually do that.

        Args:
            story_title: Human-readable title for the story

        Returns:
            The new TodoList (already registered in the shared TodoStore, with no items yet)
        """
        todo_list = TodoList(
            id=str(uuid.uuid4()),
            story_id=self._slugify(story_title),
            story_title=story_title,
        )
        self.todo_store.create(todo_list)
        return todo_list

    async def populate_todo_list(self, todo_list: TodoList, story: str) -> None:
        """
        Break a finalized user story into an ordered list of implementation
        tasks, populating `todo_list.items` in place (so anyone already
        polling this todo list sees the tasks appear).

        Args:
            todo_list: A shell created via start_run()
            story: The finalized user story text (with acceptance criteria)
        """
        todo_list.status = "planning"
        todo_list.current_agent = "developer"
        todo_list.current_activity = "Breaking the story into tasks"

        provider = self.model_router.default_provider
        prompt = (
            f"{self.prompt_template}\n\n"
            f"## User Story\n{story}\n\n"
            "First decide whether this story is simple enough to implement as ONE "
            "cohesive task, or whether it genuinely contains multiple independent, "
            "separable pieces of work (e.g. a multi-page site needs one task per "
            "page). Most stories should be ONE task - do not invent artificial "
            "steps just to produce a longer list, but also do not collapse a "
            "genuinely multi-part deliverable into a single narrow task. Respond "
            "with a numbered list (one item if simple, more only if genuinely "
            "warranted), ordered so earlier tasks don't depend on later ones. "
            "Respond with the numbered list only."
        )
        # think=True (unlike implement_item's code-generation calls, which stay
        # thinking-disabled to protect their token budget): deciding how many
        # tasks a story genuinely needs - and recognizing that e.g. "a static
        # web app" implies multiple pages, not one form - is a judgment call
        # that benefits from deliberation, not a format-constrained output
        # where reasoning tokens mostly just risk truncating the list.
        result = await provider.call(prompt, temperature=0.2, max_tokens=2000, think=True,
                                      num_ctx=32768, timeout=600)
        task_titles = [t.strip() for t in _NUMBERED_ITEM_PATTERN.findall(result) if t.strip()]
        task_titles = [_LABEL_PREFIX_PATTERN.sub("", t).strip() or t for t in task_titles]
        if not task_titles:
            # Model didn't follow the format; fall back to a single task for the whole story.
            task_titles = [todo_list.story_title]

        todo_list.items = [
            TodoItem(id=str(uuid.uuid4()), title=title, description=title)
            for title in task_titles
        ]
        todo_list.status = "running"

    async def implement_item(self, story: str, item: TodoItem, test_feedback: Optional[str] = None, test_code: Optional[str] = None) -> str:
        """
        Generate (or revise, if test_feedback is given) code for a single todo item.

        Args:
            story: The full user story, for context
            item: The todo item being implemented
            test_feedback: Failing pytest output from a previous attempt, if any
            test_code: The actual test source that produced that failure, if any

        Returns:
            The generated source code
        """
        provider = self.model_router.default_provider
        feedback_section = ""
        if test_feedback:
            test_code_section = (
                f"\n### Test Code That Was Run\n```python\n{test_code}\n```"
                if test_code else ""
            )
            feedback_section = (
                f"\n\n## Your Previous Attempt Failed Testing\n"
                f"{test_code_section}\n"
                f"### Pytest Output\n```\n{test_feedback}\n```\n\n"
                "Before writing the fix, add a brief comment block at the very top of "
                "your code (using # for Python, <!-- --> for HTML) that:\n"
                "1. States the exact assertion or error that failed.\n"
                "2. Explains in one sentence WHY the previous code didn't satisfy it.\n"
                "3. States what specific change you will make.\n"
                "Then write the COMPLETE corrected implementation below the comment.\n"
                "Do NOT rewrite from scratch unless the entire approach was wrong.\n"
                "Do NOT add fake pass-throughs or special-case the test — make the code genuinely correct."
            )

        prompt = (
            f"{self.prompt_template}\n\n"
            f"## User Story\n{story}\n\n"
            f"## Task To Implement\n{item.title}\n"
            f"{feedback_section}\n\n"
            "Write a single, COMPLETE implementation that fully implements this "
            "task - a Python module for backend/logic work, or a self-contained "
            "HTML page for a frontend/UI task (see the format rules above). "
            "Every function, class, and method must be FULLY implemented - "
            "no pass statements, no TODO comments, no stub bodies, no placeholder "
            "returns like `return None` where real logic is expected. "
            "Do not truncate output. Respond with ONLY "
            "the code in ONE fenced code block using the correct language tag - "
            "no explanation."
        )
        # Use a lower temperature on retries — the fix should be targeted and
        # deterministic, not exploratory. First attempts get 0.2 to allow some
        # creative latitude; retries get 0.1 to stay focused on the exact issue.
        temperature = 0.1 if test_feedback else 0.2
        result = await provider.call(
            prompt,
            temperature=temperature,
            # num_predict=-1: let the model finish the complete implementation
            # naturally (EOS) rather than cutting it off at a token cap.
            # num_ctx=32768: full context window — story + test code + impl
            # can approach 8-12k tokens on complex tasks; 32k gives plenty
            # of headroom. timeout=900: quality over speed — better a correct
            # 10-minute response than a truncated 3-minute one.
            max_tokens=-1,
            num_ctx=32768,
            timeout=900,
        )
        return self._extract_code(result)

    async def create_pull_request(self, todo_list: TodoList, sandbox: Optional[Any] = None) -> dict[str, Any]:
        """
        Open a pull request with the code for every completed item in the todo list.

        Args:
            todo_list: A fully-completed todo list
            sandbox: The shared per-story Sandbox holding the actual
                accumulated files on disk. When given, the PR is built
                directly from what's really in that workspace (every task's
                own file, plus its tests) instead of being reconstructed from
                in-memory item.code alone - which is what used to produce
                only the LAST task's leftover generic file for a multi-file
                project like a multi-page site.

        Returns:
            The GitHubService result (created flag + PR URL, or a reason it wasn't created)
        """
        if not self.github_service:
            return {
                "created": False,
                "reason": "GitHub integration not configured for this agent.",
            }

        if sandbox is not None:
            files: dict[str, str] = {}
            for root, dirs, filenames in os.walk(sandbox.path):
                # Prune traversal so os.walk never descends into test-tooling
                # directories — modifying dirs[:] in place is the os.walk idiom
                # for preventing descent into unwanted subtrees.
                dirs[:] = [
                    d for d in dirs
                    if d not in (".pytest_cache", "__pycache__", ".git", ".tox", "node_modules")
                    and not d.startswith(".")
                ]
                for name in filenames:
                    # Skip test scaffolding and compiled artefacts — only the
                    # developer's implementation files belong in the PR.
                    if (
                        name.startswith("test_")     # pytest test files
                        or name.endswith(".pyc")      # compiled bytecode
                        or name.startswith(".")       # hidden files (.gitignore etc.)
                        or name == "conftest.py"      # pytest config
                        or name == "pytest.ini"
                        or name == "setup.cfg"
                    ):
                        continue
                    full_path = os.path.join(root, name)
                    rel_path = os.path.relpath(full_path, sandbox.path).replace(os.sep, "/")
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except (UnicodeDecodeError, OSError):
                        continue
                    files[f"generated/{todo_list.story_id}/{rel_path}"] = content
        else:
            # Fallback for callers without a persistent sandbox (shouldn't
            # happen via the normal workflow engine path, but keeps this
            # method usable standalone / in tests).
            files = {
                f"generated/{todo_list.story_id}/{self._slugify(item.title)}"
                f"{'.html' if item.file_type == 'html' else '.py'}": item.code
                for item in todo_list.items
                if item.code
            }

        branch_name = f"korame/{todo_list.story_id}-{todo_list.id[:8]}"
        body_lines = [
            "Auto-generated by the Korame Developer Agent, verified by the Testing Agent.",
            "",
            f"**Story:** {todo_list.story_title}",
            "",
            "**Completed tasks:**",
        ] + [f"- [x] {item.title}" for item in todo_list.items]

        return await self.github_service.create_pull_request(
            branch_name=branch_name,
            title=f"Implement: {todo_list.story_title}",
            body="\n".join(body_lines),
            files=files,
        )

    @staticmethod
    def _extract_code(text: str) -> str:
        """Pull the code out of a fenced ```python/```html ...``` block, if present."""
        match = _CODE_BLOCK_PATTERN.search(text)
        return match.group(1).strip() if match else text.strip()

    @staticmethod
    def detect_file_type(code: str) -> str:
        """
        Detect whether generated code is a standalone HTML page or a Python
        module, so the Testing Agent can test it appropriately: an HTML page
        can't be `import`-ed like a Python module, so it needs a different
        testing strategy (structural assertions on the file's text/markup).

        Only checks the start of the content (not a full-text search) so a
        Python file that merely returns/contains an HTML string somewhere in
        its body (e.g. a Flask view) isn't mistaken for a standalone HTML page.

        Safety net: if there's no HTML signature AND the content doesn't even
        parse as valid Python, it's treated as "html" (i.e. tested via text
        assertions, not `import`) anyway - some tasks produce a markup/CSS
        fragment without a <!DOCTYPE>/<html> wrapper (e.g. a task that split
        off "styling" from "page structure"), and defaulting an unrecognized,
        non-Python fragment to "python" would guarantee a doomed import that
        can never pass no matter how many times it's retried.
        """
        head = code.lstrip()[:200]
        if _HTML_SIGNATURE_PATTERN.search(head):
            return "html"

        try:
            ast.parse(code)
        except SyntaxError:
            return "html"

        return "python"

    @staticmethod
    @staticmethod
    def derive_filename(title: str, file_type: str, code: str = "") -> str:
        """
        Derive a stable, per-task filename.  For HTML, inspects the generated
        code’s ``<title>`` tag and maps it to a conventional page name (index,
        contact, about …) before falling back to the task-title slug.  For
        Python, tries to extract the first public class or function name via
        the AST so the module has a meaningful import name.

        Args:
            title:     The task’s title (fallback source for the filename).
            file_type: "python" or "html", as detected from the generated code.
            code:      The generated source; used for smarter name extraction.

        Returns:
            A filesystem- and (for Python) import-safe filename.
        """
        if file_type == "html":
            return DeveloperAgent._derive_html_filename(title, code)
        return DeveloperAgent._derive_python_filename(title, code)

    # ------------------------------------------------------------------
    # Filename helpers
    # ------------------------------------------------------------------

    # Maps sets of keywords found in an HTML page’s <title> (or task title)
    # to conventional page filenames used by real websites.
    _PAGE_KEYWORD_MAP: list[tuple[tuple[str, ...], str]] = [
        (("home", "index", "main", "landing", "welcome", "start"), "index.html"),
        (("contact", "reach", "get in touch", "touch"), "contact.html"),
        (("about", "who we are", "our story", "about us", "team", "company"), "about.html"),
        (("service", "what we do", "offering", "solution"), "services.html"),
        (("portfolio", "work", "project", "case study", "gallery"), "portfolio.html"),
        (("blog", "post", "article", "news"), "blog.html"),
        (("faq", "frequently asked", "question"), "faq.html"),
        (("privacy",), "privacy.html"),
        (("terms", "conditions", "legal"), "terms.html"),
        (("login", "sign in", "signin"), "login.html"),
        (("register", "sign up", "signup"), "register.html"),
        (("dashboard", "admin", "panel"), "dashboard.html"),
        (("shop", "store", "cart", "checkout"), "shop.html"),
        (("pricing", "plan", "price"), "pricing.html"),
    ]

    @staticmethod
    def _derive_html_filename(title: str, code: str) -> str:
        """Derive a meaningful HTML filename from the page's <title> tag or task title."""
        # Prefer the <title> tag text over the task title—it reflects the
        # actual page name the developer chose, not the engineering task name.
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", code, re.IGNORECASE)
        page_name = (title_match.group(1).strip() if title_match else title).lower()

        for keywords, filename in DeveloperAgent._PAGE_KEYWORD_MAP:
            if any(kw in page_name for kw in keywords):
                return filename

        # No keyword matched — slug the page name (from <title> if found, else task title)
        slug = re.sub(r"[^a-z0-9]+", "-", page_name).strip("-")[:40]
        return f"{slug or 'page'}.html"

    @staticmethod
    def _derive_python_filename(title: str, code: str) -> str:
        """Derive a Python module filename from the first public class/function in the code."""
        if code:
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and not node.name.startswith("_"):
                        safe = re.sub(r"[^a-z0-9]+", "_", node.name.lower()).strip("_")[:40]
                        if safe and not safe[0].isdigit():
                            return f"{safe}.py"
            except SyntaxError:
                pass  # unparseable — fall through to title-based slug

        module_name = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:50] or "task"
        if module_name[0].isdigit():
            module_name = f"m_{module_name}"
        return f"{module_name}.py"

    @staticmethod
    def _slugify(text: str) -> str:
        """Turn a title into a filesystem/branch-safe slug."""
        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        return slug[:50] or "task"

    async def execute(self, task: Task) -> Response:
        """
        Single-shot entry point (e.g. via POST /api/v1/chat with agent_name="developer"):
        breaks a story into a todo list. Use WorkflowEngine.execute_development_cycle()
        for the full implement -> test -> revise -> PR loop.
        """
        try:
            story = task.input_data.get("story", "")
            story_title = task.input_data.get("story_title", "Untitled story")
            if not story:
                return Response(
                    task_id=task.id,
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="No story provided in task input",
                )

            todo_list = self.start_run(story_title)
            await self.populate_todo_list(todo_list, story)
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="success",
                data={
                    "todo_list_id": todo_list.id,
                    "tasks": [item.title for item in todo_list.items],
                },
            )
        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="error",
                data={},
                error=f"Developer Agent failed: {str(e)}",
            )
