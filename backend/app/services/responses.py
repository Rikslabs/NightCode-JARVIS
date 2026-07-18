"""Typed response models for the service layer."""
from dataclasses import dataclass, field
from typing import Any, Optional

from .models import BaseResponse


@dataclass
class SuccessResponse(BaseResponse):
    """Successful response."""
    success: bool = True


@dataclass
class FailureResponse(BaseResponse):
    """Failed response."""
    success: bool = False
    error_code: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        result = super().to_dict()
        result['error_code'] = self.error_code
        return result


@dataclass
class WorkflowResponse(BaseResponse):
    """Response for workflow operations."""
    success: bool = True
    workflow_id: Optional[str] = None
    status: Optional[str] = None


@dataclass
class PlanningResponse(BaseResponse):
    """Response for planning operations."""
    success: bool = True
    plan: Optional[dict[str, Any]] = None
    phases: Optional[list[dict[str, Any]]] = None


@dataclass
class KnowledgeResponse(BaseResponse):
    """Response for knowledge operations."""
    success: bool = True
    entries: Optional[list[dict[str, Any]]] = None
    entry: Optional[dict[str, Any]] = None


@dataclass
class ReviewResponse(BaseResponse):
    """Response for review operations."""
    success: bool = True
    issues: Optional[list[dict[str, Any]]] = None
    score: Optional[float] = None


@dataclass
class EditingResponse(BaseResponse):
    """Response for editing operations."""
    success: bool = True
    patch: Optional[dict[str, Any]] = None
    valid: Optional[bool] = None


@dataclass
class StatusResponse(BaseResponse):
    """Response for status operations."""
    success: bool = True
    component: Optional[str] = None
    status: Optional[str] = None
    details: Optional[dict[str, Any]] = None