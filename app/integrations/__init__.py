"""External service integrations (not LLM providers - e.g. source control, issue trackers)."""

from app.integrations.github_service import GitHubService

__all__ = ["GitHubService"]
