"""Service context for request-scoped data."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4, uuid1


@dataclass
class ServiceContext:
    """Context for service execution."""
    request_id: str
    session_id: str = field(default_factory=lambda: str(uuid1()))
    workflow_id: Optional[str] = None
    project_path: Optional[str] = None
    user: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'request_id': self.request_id,
            'session_id': self.session_id,
            'workflow_id': self.workflow_id,
            'project_path': self.project_path,
            'user': self.user,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'started_at': self.started_at,
        }


class ServiceContextFactory:
    """Factory for creating service contexts."""

    @staticmethod
    def create_context(
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        project_path: Optional[str] = None,
        user: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ServiceContext:
        """Create a service context."""
        return ServiceContext(
            request_id=request_id or str(uuid4()),
            session_id=session_id or str(uuid1()),
            workflow_id=workflow_id,
            project_path=project_path,
            user=user,
            metadata=metadata or {},
        )