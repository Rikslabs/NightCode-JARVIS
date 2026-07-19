"""Independent, blueprint-driven mission planning service."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Union

from .models_mission import (
    MissionRules,
    MissionStage,
    MissionState,
    MissionSummary,
    ProjectBlueprint,
    ProjectRoadmap,
)


class MissionService:
    """Load project plans and persist only explicit mission-state updates."""

    def __init__(self, mission_root: Union[str, Path]) -> None:
        self._mission_root = Path(mission_root)

    def load_blueprint(self) -> ProjectBlueprint:
        data = self._load_document("blueprint.yaml")
        return ProjectBlueprint(
            project_name=str(data["project_name"]),
            current_version=str(data["current_version"]),
            architecture_layers=list(data.get("architecture_layers", [])),
            coding_standards=list(data.get("coding_standards", [])),
            testing_requirements=list(data.get("testing_requirements", [])),
            approval_workflow=list(data.get("approval_workflow", [])),
            safety_policies=list(data.get("safety_policies", [])),
        )

    def load_roadmap(self) -> ProjectRoadmap:
        data = self._load_document("roadmap.yaml")
        stages = [MissionStage(
            id=str(stage["id"]),
            name=str(stage["name"]),
            description=str(stage["description"]),
            status=str(stage["status"]),
            dependencies=list(stage.get("dependencies", [])),
            estimated_files=list(stage.get("estimated_files", [])),
            approval_required=bool(stage.get("approval_required", True)),
        ) for stage in data.get("stages", [])]
        return ProjectRoadmap(version=str(data["version"]), stages=stages)

    def load_rules(self) -> MissionRules:
        data = self._load_document("rules.yaml")
        return MissionRules(rules=list(data.get("rules", [])))

    def load_state(self) -> MissionState:
        data = self._load_document("state.json")
        return MissionState(
            current_version=str(data["current_version"]),
            completed_stages=list(data.get("completed_stages", [])),
            active_mission=data.get("active_mission"),
            last_completed_stage=data.get("last_completed_stage"),
            timestamp=str(data.get("timestamp", "")),
        )

    def determine_next_stage(self) -> Optional[MissionStage]:
        roadmap = self.load_roadmap()
        state = self.load_state()
        completed = set(state.completed_stages)
        completed.update(stage.id for stage in roadmap.stages if stage.status == "completed")
        for stage in roadmap.stages:
            if stage.id in completed or stage.status == "completed":
                continue
            if set(stage.dependencies).issubset(completed):
                return stage
        return None

    def mission_summary(self) -> MissionSummary:
        roadmap = self.load_roadmap()
        state = self.load_state()
        completed = set(state.completed_stages)
        completed.update(stage.id for stage in roadmap.stages if stage.status == "completed")
        return MissionSummary(
            current_version=state.current_version,
            target_version=roadmap.version,
            completed_stages=len(completed),
            total_stages=len(roadmap.stages),
            active_mission=state.active_mission,
            next_stage=self.determine_next_stage(),
        )

    def preview_stage(self, stage_id: Optional[str] = None) -> Optional[MissionStage]:
        if stage_id is None:
            return self.determine_next_stage()
        return next(
            (stage for stage in self.load_roadmap().stages if stage.id == stage_id),
            None,
        )

    def mark_stage_complete(self, stage_id: str) -> MissionState:
        stage = self.preview_stage(stage_id)
        if stage is None:
            raise KeyError(f"Unknown roadmap stage: {stage_id}")
        state = self.load_state()
        if stage_id not in state.completed_stages:
            state.completed_stages.append(stage_id)
        state.last_completed_stage = stage_id
        if state.active_mission == stage_id:
            state.active_mission = None
        state.timestamp = datetime.now(timezone.utc).isoformat()
        self.update_state(state)
        return state

    def mission_status(self) -> str:
        """Return the persisted lifecycle status, defaulting to IDLE."""
        return str(self._load_document("state.json").get("mission_status", "IDLE"))

    def execute_mission(self) -> MissionStage:
        """Select the next stage and wait for approval without executing work."""
        status = self.mission_status()
        if status != "IDLE":
            raise ValueError(f"Cannot execute a mission while status is {status}.")
        stage = self.determine_next_stage()
        if stage is None:
            raise ValueError("No eligible mission stage is available.")
        state = self.load_state()
        state.active_mission = stage.id
        state.timestamp = self._timestamp()
        self._write_state(state, "AWAITING_APPROVAL")
        return stage

    def approve_mission(self) -> MissionState:
        """Approve the active mission without starting implementation."""
        if self.mission_status() != "AWAITING_APPROVAL":
            raise ValueError("Cannot approve because no mission is awaiting approval.")
        state = self.load_state()
        if not state.active_mission:
            raise ValueError("Cannot approve because no active mission exists.")
        state.timestamp = self._timestamp()
        self._write_state(state, "APPROVED")
        return state

    def reject_mission(self) -> MissionState:
        """Cancel a mission that is awaiting approval."""
        if self.mission_status() != "AWAITING_APPROVAL":
            raise ValueError("Cannot reject because no mission is awaiting approval.")
        state = self.load_state()
        state.active_mission = None
        state.timestamp = self._timestamp()
        self._write_state(state, "CANCELLED")
        return state

    def complete_mission(self) -> MissionState:
        """Complete an approved stage and update roadmap and state metadata."""
        if self.mission_status() != "APPROVED":
            raise ValueError("Cannot complete a mission before approval.")
        state = self.load_state()
        if not state.active_mission:
            raise ValueError("Cannot complete because no active mission exists.")
        roadmap_data = self._load_document("roadmap.yaml")
        stages = roadmap_data.get("stages", [])
        matched = False
        for stage in stages:
            if stage.get("id") == state.active_mission:
                stage["status"] = "completed"
                matched = True
                break
        if not matched:
            raise ValueError(f"Active mission is not in the roadmap: {state.active_mission}")

        if state.active_mission not in state.completed_stages:
            state.completed_stages.append(state.active_mission)
        state.last_completed_stage = state.active_mission
        state.active_mission = None
        if stages and all(stage.get("status") == "completed" for stage in stages):
            state.current_version = str(roadmap_data["version"])
        state.timestamp = self._timestamp()
        self._write_document("roadmap.yaml", roadmap_data)
        self._write_state(state, "COMPLETED")
        return state

    def reset_mission(self) -> MissionState:
        """Return the lifecycle to IDLE and clear the active mission."""
        state = self.load_state()
        state.active_mission = None
        state.timestamp = self._timestamp()
        self._write_state(state, "IDLE")
        return state

    def update_state(self, state: MissionState) -> None:
        status = self.mission_status() if (self._mission_root / "state.json").exists() else "IDLE"
        self._write_state(state, status)

    def _write_state(self, state: MissionState, status: str) -> None:
        data = asdict(state)
        data["mission_status"] = status
        self._write_document("state.json", data)

    def _write_document(self, name: str, data: Dict[str, object]) -> None:
        (self._mission_root / name).write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_document(self, name: str) -> Dict[str, object]:
        path = self._mission_root / name
        with path.open("r", encoding="utf-8") as document:
            data = json.load(document)
        if not isinstance(data, dict):
            raise ValueError(f"Mission document must contain an object: {name}")
        return data
