"""Typed request models for the service layer."""
from dataclasses import dataclass, field
from typing import Any, Optional

from .models import BaseRequest


@dataclass
class AnalyzeProjectRequest(BaseRequest):
    """Request to analyze a project."""
    project_path: str
    depth: str = 'standard'


@dataclass
class ReviewProjectRequest(BaseRequest):
    """Request to review a project."""
    project_path: str
    max_issues: int = 50


@dataclass
class PlanningRequest(BaseRequest):
    """Request to create a plan."""
    goal: str
    project_path: Optional[str] = None
    change_type: str = 'feature'


@dataclass
class KnowledgeRequest(BaseRequest):
    """Request to store or retrieve knowledge."""
    action: str = 'store'
    key: Optional[str] = None
    content: Optional[str] = None
    project_path: Optional[str] = None


@dataclass
class EditingRequest(BaseRequest):
    """Request for editing operations."""
    action: str = 'preview'
    workflow_id: Optional[str] = None
    file_path: Optional[str] = None
    project_path: Optional[str] = None


@dataclass
class WorkflowRequest(BaseRequest):
    """Request to execute a workflow."""
    workflow_type: str = 'analyze'
    project_path: Optional[str] = None
    goal: Optional[str] = None
    user_request: Optional[str] = None


@dataclass
class StatusRequest(BaseRequest):
    """Request for system status."""
    component: Optional[str] = None