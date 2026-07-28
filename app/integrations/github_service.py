"""
GitHub integration for the Developer Agent.

Creates a branch, commits generated files, and opens a pull request via the
GitHub REST API. Requires a personal access token and target repository to be
configured (GITHUB_TOKEN / GITHUB_REPO); if they aren't set, methods report
that PR creation is unavailable instead of guessing or attempting anything.
"""

import base64
from typing import Any, Optional
import httpx


class GitHubService:
    """Thin wrapper around the GitHub REST API for opening pull requests."""

    def __init__(
        self,
        token: Optional[str] = None,
        repo: Optional[str] = None,
        base_branch: str = "main",
    ):
        """
        Args:
            token: GitHub personal access token (needs `repo` scope)
            repo: Target repository as "owner/name"
            base_branch: Branch to base new branches/PRs off of
        """
        self.token = token
        self.repo = repo
        self.base_branch = base_branch

    def is_configured(self) -> bool:
        """True once both a token and target repo are set."""
        return bool(self.token and self.repo)

    async def create_pull_request(
        self,
        branch_name: str,
        title: str,
        body: str,
        files: dict[str, str],
    ) -> dict[str, Any]:
        """
        Create a branch, commit the given files to it, and open a pull request.

        Args:
            branch_name: Name for the new branch
            title: Pull request title
            body: Pull request description
            files: Mapping of repo-relative file path -> file content

        Returns:
            Dict with `created: bool` and either `pr_url`/`pr_number`, or a
            `reason` explaining why nothing was created.
        """
        if not self.is_configured():
            return {
                "created": False,
                "reason": (
                    "GitHub integration not configured. Set GITHUB_TOKEN and "
                    "GITHUB_REPO (and optionally GITHUB_BASE_BRANCH) to enable "
                    "pull request creation."
                ),
            }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }
        base_url = f"https://api.github.com/repos/{self.repo}"

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                ref_resp = await client.get(
                    f"{base_url}/git/ref/heads/{self.base_branch}", headers=headers
                )
                ref_resp.raise_for_status()
                base_sha = ref_resp.json()["object"]["sha"]

                create_ref_resp = await client.post(
                    f"{base_url}/git/refs",
                    headers=headers,
                    json={"ref": f"refs/heads/{branch_name}", "sha": base_sha},
                )
                create_ref_resp.raise_for_status()

                for path, content in files.items():
                    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
                    commit_resp = await client.put(
                        f"{base_url}/contents/{path}",
                        headers=headers,
                        json={
                            "message": f"Add {path}",
                            "content": encoded,
                            "branch": branch_name,
                        },
                    )
                    commit_resp.raise_for_status()

                pr_resp = await client.post(
                    f"{base_url}/pulls",
                    headers=headers,
                    json={
                        "title": title,
                        "body": body,
                        "head": branch_name,
                        "base": self.base_branch,
                    },
                )
                pr_resp.raise_for_status()
                pr_data = pr_resp.json()

            return {
                "created": True,
                "pr_url": pr_data.get("html_url"),
                "pr_number": pr_data.get("number"),
            }
        except httpx.HTTPError as e:
            return {"created": False, "reason": f"GitHub API request failed: {e}"}
