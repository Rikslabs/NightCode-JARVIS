"""Typed models for blueprint-driven mission planning."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ProjectBlueprint:
    project_name: str
    current_version: str
    architecture_layers: List[str] = field(default_factory=list)
    coding_standards: List[str] = field(default_factory=list)
    testing_requirements: List[str] = field(default_factory=list)
    approval_workflow: List[str] = field(default_factory=list)
    safety_policies: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MissionStage:
    id: str
    name: str
    description: str
    status: str
    dependencies: List[str] = field(default_factory=list)
    estimated_files: List[str] = field(default_factory=list)
    approval_required: bool = True


@dataclass(frozen=True)
class ProjectRoadmap:
    version: str
    stages: List[MissionStage] = field(default_factory=list)


@dataclass(frozen=True)
class MissionRules:
    rules: List[str] = field(default_factory=list)


@dataclass
class MissionState:
    current_version: str
    completed_stages: List[str] = field(default_factory=list)
    active_mission: Optional[str] = None
    last_completed_stage: Optional[str] = None
    timestamp: str = ""


@dataclass(frozen=True)
class MissionSummary:
    current_version: str
    target_version: str
    completed_stages: int
    total_stages: int
    active_mission: Optional[str]
    next_stage: Optional[MissionStage]
