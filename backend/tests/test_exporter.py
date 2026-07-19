"""Focused tests for mission prompt export."""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from app.cli import start_cli
from app.jarvis import JarvisService, MissionService
from app.jarvis.exporter import MissionExporter


def create_export_mission(root: Path) -> MissionService:
    documents = {
        "blueprint.yaml": {
            "project_name": "Demo",
            "current_version": "1.1.0",
            "architecture_layers": ["CLI", "Mission Service", "Safe Apply"],
            "coding_standards": ["Strong typing", "Dependency injection"],
            "testing_requirements": ["Run exporter tests only"],
            "approval_workflow": ["Wait for explicit approval"],
            "safety_policies": ["Never apply automatically"],
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
                    "estimated_files": ["backend/app/foundation.py"],
                    "approval_required": True,
                },
                {
                    "id": "export",
                    "name": "Mission Export",
                    "description": "Export approved missions for external coding agents.",
                    "status": "pending",
                    "dependencies": ["foundation"],
                    "estimated_files": ["backend/app/jarvis/exporter.py"],
                    "approval_required": True,
                },
            ],
        },
        "rules.yaml": {"rules": ["Never commit automatically."]},
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
    return MissionService(root)


def test_export_requires_active_exportable_mission(tmp_path: Path):
    exporter = MissionExporter(create_export_mission(tmp_path))

    with pytest.raises(ValueError, match="awaiting approval or already approved"):
        exporter.export()


def test_export_prompt_is_complete_and_read_only(tmp_path: Path):
    mission = create_export_mission(tmp_path)
    mission.execute_mission()
    before = {
        path.name: path.read_text(encoding="utf-8")
        for path in tmp_path.iterdir()
    }

    prompt = MissionExporter(mission).export()

    for heading in (
        "Mission", "Purpose", "Current Architecture", "Existing Components",
        "Files to Inspect", "Recommended Files to Modify", "Requirements",
        "Constraints", "Testing Requirements", "Expected Deliverables", "Return Format",
    ):
        assert heading in prompt
    assert prompt.startswith("Repository is the source of truth.")
    assert "Mission Export (export)" in prompt
    assert "backend/app/jarvis/exporter.py" in prompt
    assert "Never commit automatically." in prompt
    assert before == {
        path.name: path.read_text(encoding="utf-8")
        for path in tmp_path.iterdir()
    }


def test_approved_mission_exports_for_codex(tmp_path: Path):
    mission = create_export_mission(tmp_path)
    mission.execute_mission()
    mission.approve_mission()
    exporter = MissionExporter(mission)

    assert exporter.export_codex() == exporter.export()
    assert "Lifecycle status: APPROVED" in exporter.export_codex()


def test_mission_export_cli_aliases(tmp_path: Path):
    mission = create_export_mission(tmp_path)
    mission.execute_mission()
    state_before = (tmp_path / "state.json").read_text(encoding="utf-8")
    service = Mock(spec=JarvisService)
    output = []
    commands = iter(["mission export", "mission export codex", "exit"])

    start_cli(
        service_factory=lambda: service,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
        mission_factory=lambda: mission,
    )

    prompts = [item for item in output if item.startswith("Repository is the source")]
    assert len(prompts) == 2
    assert prompts[0] == prompts[1]
    assert "Mission Export (export)" in prompts[0]
    assert (tmp_path / "state.json").read_text(encoding="utf-8") == state_before
