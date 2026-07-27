"""
Artifact storage for Korame knowledge fabric.

Stores software engineering artifacts (user stories, designs, code, etc.)
with full versioning and relationship tracking.
"""

from typing import Optional, Any, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ArtifactType(str, Enum):
    """Types of artifacts in the software factory."""
    REQUIREMENT = "requirement"
    USER_STORY = "user_story"
    DESIGN = "design"
    CODE = "code"
    TEST = "test"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    DEPLOYMENT = "deployment"


class ArtifactStatus(str, Enum):
    """Status of an artifact."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


@dataclass
class ArtifactVersion:
    """A version of an artifact."""
    version_number: int
    content: str
    author: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    change_summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Artifact:
    """A software engineering artifact."""
    artifact_id: str
    artifact_type: ArtifactType
    title: str
    description: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: ArtifactStatus = ArtifactStatus.DRAFT
    content: str = ""
    versions: List[ArtifactVersion] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    related_artifacts: List[str] = field(default_factory=list)  # artifact IDs
    metadata: dict[str, Any] = field(default_factory=dict)


class ArtifactStore:
    """Stores and manages software engineering artifacts."""

    def __init__(self):
        """Initialize artifact store."""
        self.artifacts: Dict[str, Artifact] = {}

    def create_artifact(
        self,
        artifact_id: str,
        artifact_type: ArtifactType,
        title: str,
        description: str,
        created_by: str,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Artifact:
        """
        Create a new artifact.

        Args:
            artifact_id: Unique artifact ID
            artifact_type: Type of artifact
            title: Artifact title
            description: Artifact description
            created_by: User who created it
            content: Initial content
            metadata: Optional metadata

        Returns:
            The created artifact
        """
        artifact = Artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            title=title,
            description=description,
            created_by=created_by,
            content=content,
            metadata=metadata or {}
        )

        # Add initial version
        version = ArtifactVersion(
            version_number=1,
            content=content,
            author=created_by,
            change_summary="Initial creation"
        )
        artifact.versions.append(version)

        self.artifacts[artifact_id] = artifact
        return artifact

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get an artifact by ID."""
        return self.artifacts.get(artifact_id)

    def update_artifact(
        self,
        artifact_id: str,
        content: str,
        author: str,
        change_summary: str = ""
    ) -> bool:
        """
        Update an artifact and create a new version.

        Args:
            artifact_id: Artifact ID
            content: New content
            author: User making the change
            change_summary: Summary of changes

        Returns:
            True if updated, False if artifact not found
        """
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return False

        # Update current content
        artifact.content = content
        artifact.updated_at = datetime.utcnow()

        # Create new version
        version_number = len(artifact.versions) + 1
        version = ArtifactVersion(
            version_number=version_number,
            content=content,
            author=author,
            change_summary=change_summary
        )
        artifact.versions.append(version)

        return True

    def set_status(self, artifact_id: str, status: ArtifactStatus) -> bool:
        """
        Update artifact status.

        Args:
            artifact_id: Artifact ID
            status: New status

        Returns:
            True if updated, False if not found
        """
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return False

        artifact.status = status
        artifact.updated_at = datetime.utcnow()
        return True

    def add_tag(self, artifact_id: str, tag: str) -> bool:
        """Add a tag to an artifact."""
        artifact = self.get_artifact(artifact_id)
        if not artifact or tag in artifact.tags:
            return False

        artifact.tags.append(tag)
        return True

    def add_related_artifact(self, artifact_id: str, related_id: str) -> bool:
        """Add a relationship to another artifact."""
        artifact = self.get_artifact(artifact_id)
        if not artifact or related_id in artifact.related_artifacts:
            return False

        artifact.related_artifacts.append(related_id)
        return True

    def get_version(self, artifact_id: str, version_number: int) -> Optional[ArtifactVersion]:
        """Get a specific version of an artifact."""
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return None

        for version in artifact.versions:
            if version.version_number == version_number:
                return version

        return None

    def get_version_history(self, artifact_id: str) -> List[ArtifactVersion]:
        """Get all versions of an artifact."""
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return []

        return artifact.versions

    def list_by_type(self, artifact_type: ArtifactType) -> List[Artifact]:
        """Get all artifacts of a specific type."""
        return [
            a for a in self.artifacts.values()
            if a.artifact_type == artifact_type
        ]

    def list_by_status(self, status: ArtifactStatus) -> List[Artifact]:
        """Get all artifacts with a specific status."""
        return [
            a for a in self.artifacts.values()
            if a.status == status
        ]

    def list_by_tag(self, tag: str) -> List[Artifact]:
        """Get all artifacts with a specific tag."""
        return [
            a for a in self.artifacts.values()
            if tag in a.tags
        ]

    def list_all(self) -> List[Artifact]:
        """Get all artifacts."""
        return list(self.artifacts.values())

    def get_related_artifacts(self, artifact_id: str) -> List[Artifact]:
        """Get all artifacts related to this one."""
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return []

        related = []
        for related_id in artifact.related_artifacts:
            related_artifact = self.get_artifact(related_id)
            if related_artifact:
                related.append(related_artifact)

        return related

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored artifacts."""
        return {
            "total_artifacts": len(self.artifacts),
            "by_type": {
                atype.value: len([a for a in self.artifacts.values() if a.artifact_type == atype])
                for atype in ArtifactType
            },
            "by_status": {
                status.value: len([a for a in self.artifacts.values() if a.status == status])
                for status in ArtifactStatus
            },
            "total_versions": sum(len(a.versions) for a in self.artifacts.values())
        }

