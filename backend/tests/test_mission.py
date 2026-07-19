"""Focused tests for blueprint-driven mission planning."""

import json
from pathlib import Path
from unittest.mock import Mock

from app.cli import start_cli
from app.jarvis import JarvisService, MissionService, MissionState


def create_mission_files(root: Path) -> None:
    documents = {
        "blueprint.yaml": {
            "project_name": "Demo",
            "current_version": "1.1.0",
            "architecture_layers": ["CLI", "Services"],
            "coding_standards": ["Strong typing"],
            "testing_requirements": ["Targeted tests first"],
            "approval_workflow": ["Wait for approval"],
            "safety_policies": ["Never push automatically"],
        },
        "roadmap.yaml": {
            "version": "2.0",
            "stages": [
                {
                    "id": "foundation",
                    "name": "Foundation",
                    "description": "Existing foundation",
                    "status": "completed",
                    "dependencies": [],
                    "estimated_files": ["foundation.py"],
                    "approval_required": True,
                },
                {
                    "id": "planner",
                    "name": "Planning Engine",
                    "description": "Add planning information",
                    "status": "pending",
                    "dependencies": ["foundation"],
                    "estimated_files": ["planner.py"],
                    "approval_required": True,
                },
                {
                    "id": "runner",
                    "name": "Mission Runner",
                    "description": "Coordinate approved missions",
                    "status": "pending",
                    "dependencies": ["planner"],
                    "estimated_files": ["runner.py"],
                    "approval_required": True,
                },
            ],
        },
        "rules.yaml": {
            "rules": ["Never commit automatically.", "Always wait for approval."],
        },
        "state.json": {
            "current_version": "1.1.0",
            "completed_stages": ["foundation"],
            "active_mission": None,
            "last_completed_stage": "foundation",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "mission_status": "IDLE",
        },
    }
    for name, data in documents.items():
        (root / name).write_text(json.dumps(data), encoding="utf-8")


def test_loading_mission_documents(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)

    assert mission.load_blueprint().project_name == "Demo"
    assert mission.load_roadmap().stages[1].id == "planner"
    assert mission.load_rules().rules[0] == "Never commit automatically."
    assert mission.load_state().current_version == "1.1.0"


def test_next_stage_selection(tmp_path: Path):
    create_mission_files(tmp_path)

    stage = MissionService(tmp_path).determine_next_stage()

    assert stage is not None
    assert stage.id == "planner"
    assert stage.dependencies == ["foundation"]


def test_completed_stage_update_and_persistence(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)

    state = mission.mark_stage_complete("planner")
    persisted = mission.load_state()

    assert state.last_completed_stage == "planner"
    assert "planner" in persisted.completed_stages
    assert persisted.timestamp != "2026-01-01T00:00:00+00:00"
    assert mission.determine_next_stage().id == "runner"


def test_explicit_state_persistence(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)
    state = MissionState(
        current_version="1.2.0",
        completed_stages=["foundation"],
        active_mission="planner",
        last_completed_stage="foundation",
        timestamp="2026-02-01T00:00:00+00:00",
    )

    mission.update_state(state)

    assert mission.load_state() == state


def test_mission_summary(tmp_path: Path):
    create_mission_files(tmp_path)

    summary = MissionService(tmp_path).mission_summary()

    assert summary.current_version == "1.1.0"
    assert summary.target_version == "2.0"
    assert summary.completed_stages == 1
    assert summary.total_stages == 3
    assert summary.next_stage.id == "planner"


def test_read_only_mission_cli_commands(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)
    original_state = (tmp_path / "state.json").read_text(encoding="utf-8")
    service = Mock(spec=JarvisService)
    output = []
    commands = iter([
        "mission",
        "mission status",
        "mission next",
        "mission preview",
        "mission roadmap",
        "mission blueprint",
        "mission rules",
        "exit",
    ])

    start_cli(
        service_factory=lambda: service,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
        mission_factory=lambda: mission,
    )

    rendered = "\n".join(output)
    assert "Mission Status" in rendered
    assert "Current Version: 1.1.0" in rendered
    assert "Target Version: 2.0" in rendered
    assert "Next Stage: Planning Engine (planner)" in rendered
    assert "Approval Required: yes" in rendered
    assert "Roadmap to 2.0" in rendered
    assert "Blueprint: Demo" in rendered
    assert "Always wait for approval." in rendered
    assert (tmp_path / "state.json").read_text(encoding="utf-8") == original_state
    service.assert_not_called()


def test_mission_execute_and_approve(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)

    stage = mission.execute_mission()

    assert stage.id == "planner"
    assert mission.mission_status() == "AWAITING_APPROVAL"
    assert mission.load_state().active_mission == "planner"

    mission.approve_mission()

    assert mission.mission_status() == "APPROVED"


def test_mission_reject_and_reset(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)
    mission.execute_mission()

    mission.reject_mission()

    assert mission.mission_status() == "CANCELLED"
    assert mission.load_state().active_mission is None

    state = mission.reset_mission()

    assert mission.mission_status() == "IDLE"
    assert state.active_mission is None


def test_mission_complete_updates_roadmap_and_state(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)
    mission.execute_mission()
    mission.approve_mission()

    state = mission.complete_mission()

    assert mission.mission_status() == "COMPLETED"
    assert state.last_completed_stage == "planner"
    assert "planner" in state.completed_stages
    planner = mission.preview_stage("planner")
    assert planner.status == "completed"
    persisted = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert persisted["mission_status"] == "COMPLETED"


def test_mission_completion_advances_version_at_milestone(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)
    mission.execute_mission()
    mission.approve_mission()
    mission.complete_mission()
    mission.reset_mission()
    mission.execute_mission()
    mission.approve_mission()

    state = mission.complete_mission()

    assert state.current_version == "2.0"
    assert all(stage.status == "completed" for stage in mission.load_roadmap().stages)


def test_invalid_mission_transitions(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)

    for operation in (mission.approve_mission, mission.reject_mission, mission.complete_mission):
        try:
            operation()
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid transition was accepted")

    mission.execute_mission()
    try:
        mission.execute_mission()
    except ValueError as exc:
        assert "AWAITING_APPROVAL" in str(exc)
    else:
        raise AssertionError("Concurrent mission execution was accepted")


def test_mission_lifecycle_cli(tmp_path: Path):
    create_mission_files(tmp_path)
    mission = MissionService(tmp_path)
    service = Mock(spec=JarvisService)
    output = []
    commands = iter([
        "mission approve",
        "mission execute",
        "mission approve",
        "mission complete",
        "mission reset",
        "exit",
    ])

    start_cli(
        service_factory=lambda: service,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
        mission_factory=lambda: mission,
    )

    rendered = "\n".join(output)
    assert "Error: Cannot approve because no mission is awaiting approval." in rendered
    assert "Mission Name: Planning Engine" in rendered
    assert "Mission Approved." in rendered
    assert "Mission completed: planner" in rendered
    assert "Mission reset to IDLE." in rendered
