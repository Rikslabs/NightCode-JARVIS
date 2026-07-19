"""Approval-gated, read-only implementation planning."""

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from .mission import MissionService
from .models_mission import MissionStage, ProjectRoadmap


@dataclass(frozen=True)
class ImplementationPlan:
    """A bounded view of one roadmap stage and its implementation scope."""

    stage_id: str
    mission_name: str
    description: str
    current_version: str
    target_version: str
    architecture_layers: Tuple[str, ...]
    existing_components: Tuple[str, ...]
    dependencies: Tuple[str, ...]
    files_to_inspect: Tuple[str, ...]
    estimated_files: Tuple[str, ...]
    requirements: Tuple[str, ...]
    constraints: Tuple[str, ...]
    testing_requirements: Tuple[str, ...]
    approval_required: bool
    lifecycle_status: str
    approved: bool


class PlanningEngine:
    """Build plans from mission documents without executing or persisting work."""

    def __init__(self, mission_service: MissionService) -> None:
        self._mission_service = mission_service

    def preview_stage(self, stage_id: Optional[str] = None) -> ImplementationPlan:
        """Preview a selected, active, or next eligible roadmap stage."""
        state = self._mission_service.load_state()
        selected_id = stage_id or state.active_mission
        stage = self._mission_service.preview_stage(selected_id)
        if stage is None:
            if selected_id is not None:
                raise KeyError(f"Unknown roadmap stage: {selected_id}")
            raise ValueError("No eligible mission stage is available.")

        blueprint = self._mission_service.load_blueprint()
        roadmap = self._mission_service.load_roadmap()
        rules = self._mission_service.load_rules()
        status = self._mission_service.mission_status()

        return ImplementationPlan(
            stage_id=stage.id,
            mission_name=stage.name,
            description=stage.description,
            current_version=state.current_version,
            target_version=roadmap.version,
            architecture_layers=tuple(blueprint.architecture_layers),
            existing_components=tuple(
                item.name for item in roadmap.stages if item.status == "completed"
            ),
            dependencies=tuple(stage.dependencies),
            files_to_inspect=self._dependency_files(stage, roadmap),
            estimated_files=tuple(stage.estimated_files),
            requirements=self._unique((
                stage.description,
                *blueprint.approval_workflow,
            )),
            constraints=self._unique((
                *blueprint.coding_standards,
                *blueprint.safety_policies,
                *rules.rules,
            )),
            testing_requirements=tuple(blueprint.testing_requirements),
            approval_required=stage.approval_required,
            lifecycle_status=status,
            approved=status == "APPROVED" and state.active_mission == stage.id,
        )

    def plan_approved_mission(self) -> ImplementationPlan:
        """Return the active plan only after explicit mission approval."""
        state = self._mission_service.load_state()
        if self._mission_service.mission_status() != "APPROVED":
            raise ValueError("Planning requires an approved mission.")
        if not state.active_mission:
            raise ValueError("Planning requires an active mission.")
        return self.preview_stage(state.active_mission)

    @staticmethod
    def _dependency_files(
        stage: MissionStage,
        roadmap: ProjectRoadmap,
    ) -> Tuple[str, ...]:
        dependency_ids = set(stage.dependencies)
        return PlanningEngine._unique(
            path
            for item in roadmap.stages
            if item.id in dependency_ids
            for path in item.estimated_files
        )

    @staticmethod
    def _unique(values: Iterable[str]) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(value for value in values if value.strip()))
