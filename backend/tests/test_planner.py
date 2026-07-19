import json
from pathlib import Path

import pytest

from backend.app.jarvis.mission import MissionService
from backend.app.jarvis.planner import PlanningEngine


def _write_documents(root: Path, status: str = "IDLE", active: str | None = None) -> None:
    documents = {
        "blueprint.yaml": {
            "project_name": "Example",
            "current_version": "1.1.0",
            "architecture_layers": ["CLI", "Services"],
            "coding_standards": ["Strong typing", "Strong typing"],
            "testing_requirements": ["Run targeted tests first"],
            "approval_workflow": ["Wait for explicit approval"],
            "safety_policies": ["Never commit automatically"],
        },
        "roadmap.yaml": {
            "version": "2.0",
            "stages": [
                {
                    "id": "foundation",
                    "name": "Foundation",
                    "description": "Existing foundation.",
                    "status": "completed",
                    "dependencies": [],
                    "estimated_files": ["backend/app/cli"],
                    "approval_required": True,
                },
                {
                    "id": "custom-stage",
                    "name": "Custom Stage",
                    "description": "Plan an arbitrary future capability.",
                    "status": "pending",
                    "dependencies": ["foundation"],
                    "estimated_files": ["backend/app/custom.py", "backend/tests/test_custom.py"],
                    "approval_required": True,
                },
            ],
        },
        "rules.yaml": {
            "rules": ["Never commit automatically", "Stop after the approved stage"]
        },
        "state.json": {
            "current_version": "1.1.0",
            "completed_stages": ["foundation"],
            "active_mission": active,
            "last_completed_stage": "foundation",
            "timestamp": "",
            "mission_status": status,
        },
    }
    for name, document in documents.items():
        (root / name).write_text(json.dumps(document), encoding="utf-8")


def test_preview_presents_next_stage_scope_without_mutating_state(tmp_path: Path) -> None:
    _write_documents(tmp_path)
    state_before = (tmp_path / "state.json").read_text(encoding="utf-8")

    plan = PlanningEngine(MissionService(tmp_path)).preview_stage()

    assert plan.stage_id == "custom-stage"
    assert plan.current_version == "1.1.0"
    assert plan.target_version == "2.0"
    assert plan.existing_components == ("Foundation",)
    assert plan.dependencies == ("foundation",)
    assert plan.files_to_inspect == ("backend/app/cli",)
    assert plan.estimated_files == (
        "backend/app/custom.py",
        "backend/tests/test_custom.py",
    )
    assert plan.approval_required is True
    assert plan.approved is False
    assert (tmp_path / "state.json").read_text(encoding="utf-8") == state_before


def test_planning_waits_for_explicit_approval(tmp_path: Path) -> None:
    _write_documents(tmp_path, status="AWAITING_APPROVAL", active="custom-stage")
    planner = PlanningEngine(MissionService(tmp_path))

    with pytest.raises(ValueError, match="approved mission"):
        planner.plan_approved_mission()


def test_approved_plan_is_generic_and_deduplicates_constraints(tmp_path: Path) -> None:
    _write_documents(tmp_path, status="APPROVED", active="custom-stage")

    plan = PlanningEngine(MissionService(tmp_path)).plan_approved_mission()

    assert plan.mission_name == "Custom Stage"
    assert plan.lifecycle_status == "APPROVED"
    assert plan.approved is True
    assert plan.requirements == (
        "Plan an arbitrary future capability.",
        "Wait for explicit approval",
    )
    assert plan.constraints == (
        "Strong typing",
        "Never commit automatically",
        "Stop after the approved stage",
    )
    assert plan.testing_requirements == ("Run targeted tests first",)


def test_unknown_stage_is_rejected(tmp_path: Path) -> None:
    _write_documents(tmp_path)

    with pytest.raises(KeyError, match="missing"):
        PlanningEngine(MissionService(tmp_path)).preview_stage("missing")
