"""Text-only mission export for external coding agents."""

from typing import Iterable, List

from .mission import MissionService
from .models_mission import MissionStage


class MissionExporter:
    """Render the active mission as a reusable engineering prompt."""

    def __init__(self, mission_service: MissionService) -> None:
        self._mission_service = mission_service

    def export(self) -> str:
        """Return a copy-ready implementation prompt for the active mission."""
        status = self._mission_service.mission_status()
        if status not in {"AWAITING_APPROVAL", "APPROVED"}:
            raise ValueError(
                "Mission export requires a mission awaiting approval or already approved."
            )

        state = self._mission_service.load_state()
        if not state.active_mission:
            raise ValueError("Mission export requires an active mission.")
        stage = self._mission_service.preview_stage(state.active_mission)
        if stage is None:
            raise ValueError(f"Active mission is not in the roadmap: {state.active_mission}")

        blueprint = self._mission_service.load_blueprint()
        roadmap = self._mission_service.load_roadmap()
        rules = self._mission_service.load_rules()
        completed = [item.name for item in roadmap.stages if item.status == "completed"]
        dependency_files = self._dependency_files(stage, roadmap.stages)

        sections = [
            "Repository is the source of truth.",
            self._section("Mission", [
                f"{stage.name} ({stage.id})",
                f"Current version: {state.current_version}",
                f"Target version: {roadmap.version}",
                f"Lifecycle status: {status}",
            ]),
            self._section("Purpose", [stage.description]),
            self._section("Current Architecture", blueprint.architecture_layers),
            self._section("Existing Components", completed),
            self._section("Files to Inspect", dependency_files),
            self._section("Recommended Files to Modify", stage.estimated_files),
            self._section("Requirements", [
                stage.description,
                *blueprint.approval_workflow,
                f"Approval required: {'yes' if stage.approval_required else 'no'}",
            ]),
            self._section("Constraints", [
                *blueprint.coding_standards,
                *blueprint.safety_policies,
                *rules.rules,
            ]),
            self._section("Testing Requirements", blueprint.testing_requirements),
            self._section("Expected Deliverables", [
                f"Implementation of the {stage.name} mission only.",
                "Focused tests covering the approved mission.",
                "No unrelated repository changes.",
            ]),
            self._section("Return Format", [
                "Files created.",
                "Files modified.",
                "Tests executed and results.",
                "Blockers, if any.",
                "Stop after the approved mission is complete.",
            ]),
        ]
        return "\n\n".join(sections).strip() + "\n"

    def export_codex(self) -> str:
        """Return the same prompt in directly copyable Codex format."""
        return self.export()

    @staticmethod
    def _dependency_files(stage: MissionStage, stages: List[MissionStage]) -> List[str]:
        dependencies = set(stage.dependencies)
        files = [
            path
            for item in stages
            if item.id in dependencies
            for path in item.estimated_files
        ]
        return files or ["No prerequisite files specified."]

    @staticmethod
    def _section(title: str, items: Iterable[str]) -> str:
        values = [str(item) for item in items if str(item).strip()]
        body = "\n".join(f"- {value}" for value in values)
        return f"{title}\n{body or '- None specified.'}"
