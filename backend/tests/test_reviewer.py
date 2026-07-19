"""Focused tests for read-only mission review coordination."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from app.cli import start_cli
from app.jarvis import (
    JarvisService,
    MissionReviewer,
    MissionService,
    TestSummary as RecordedTestSummary,
)


def create_mission(root: Path) -> MissionService:
    documents = {
        "blueprint.yaml": {"project_name": "Demo", "current_version": "1.1.0"},
        "roadmap.yaml": {
            "version": "2.0",
            "stages": [{
                "id": "reviewer",
                "name": "Mission Reviewer",
                "description": "Review completed work.",
                "status": "pending",
                "estimated_files": ["backend/app/jarvis/reviewer.py", "backend/tests/test_reviewer.py"],
            }],
        },
        "rules.yaml": {"rules": []},
        "state.json": {
            "current_version": "1.1.0",
            "completed_stages": [],
            "active_mission": "reviewer",
            "last_completed_stage": None,
            "timestamp": "",
            "mission_status": "APPROVED",
        },
    }
    for name, data in documents.items():
        (root / name).write_text(json.dumps(data), encoding="utf-8")
    return MissionService(root)


def create_completed_history(root: Path) -> MissionService:
    service = create_mission(root)
    roadmap = json.loads((root / "roadmap.yaml").read_text(encoding="utf-8"))
    roadmap["stages"] = [
        {
            "id": "reviewer",
            "name": "Mission Reviewer",
            "description": "Review completed work.",
            "status": "completed",
            "estimated_files": ["reviewer.py"],
            "allowed_companion_files": ["test_reviewer.py"],
            "completion_version": "2.0.0",
            "completion_timestamp": "2026-01-01T00:00:00+00:00",
            "completion_sequence": 1,
        },
        {
            "id": "provider",
            "name": "Provider System",
            "description": "Later work.",
            "status": "completed",
            "estimated_files": ["provider.py", "test_provider.py"],
            "completion_sequence": 2,
        },
    ]
    (root / "roadmap.yaml").write_text(json.dumps(roadmap), encoding="utf-8")
    state = json.loads((root / "state.json").read_text(encoding="utf-8"))
    state.update({
        "completed_stages": ["reviewer", "provider"],
        "active_mission": None,
        "last_completed_stage": "reviewer",
        "mission_status": "COMPLETED",
    })
    (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
    (root / "reviewer.py").touch()
    (root / "test_reviewer.py").touch()
    return service


def change(path: str, index: str = " ", worktree: str = "M") -> SimpleNamespace:
    return SimpleNamespace(path=path, index_status=index, worktree_status=worktree)


def test_review_accepts_expected_work_with_successful_recorded_tests(tmp_path: Path) -> None:
    reviewer = MissionReviewer(
        create_mission(tmp_path),
        lambda: [
            change("backend/app/jarvis/reviewer.py", "?", "?"),
            change("backend/tests/test_reviewer.py", "?", "?"),
        ],
        tmp_path,
        lambda: RecordedTestSummary(
            "pytest backend/tests/test_reviewer.py", passed=5, exit_code=0
        ),
    )

    report = reviewer.review()

    assert report.recommendation == "ACCEPT"
    assert report.verification.repository_consistent is True
    assert report.verification.required_created_files == report.verification.expected_files
    assert reviewer.latest_report() == report


def test_review_rejects_missing_unexpected_and_failed_work(tmp_path: Path) -> None:
    reviewer = MissionReviewer(
        create_mission(tmp_path),
        lambda: [change("backend/app/jarvis/reviewer.py"), change("unrelated.py")],
        tmp_path,
        lambda: RecordedTestSummary("pytest focused", failed=1, exit_code=1),
    )

    report = reviewer.review()

    assert report.recommendation == "REJECT"
    assert report.verification.missing_files == ("backend/tests/test_reviewer.py",)
    assert report.verification.unexpected_files == ("unrelated.py",)


def test_review_without_test_results_needs_review(tmp_path: Path) -> None:
    expected = [
        change("backend/app/jarvis/reviewer.py"),
        change("backend/tests/test_reviewer.py"),
    ]

    report = MissionReviewer(create_mission(tmp_path), lambda: expected, tmp_path).review()

    assert report.recommendation == "NEEDS_REVIEW"
    assert report.test_summary is None


def test_verification_treats_deleted_expected_file_as_missing(tmp_path: Path) -> None:
    reviewer = MissionReviewer(
        create_mission(tmp_path),
        lambda: [
            change("backend/app/jarvis/reviewer.py", worktree="D"),
            change("old_test.py -> backend/tests/test_reviewer.py", index="R", worktree=" "),
        ],
        tmp_path,
    )

    report = reviewer.verify()

    assert report.missing_files == ("backend/app/jarvis/reviewer.py",)
    assert report.unexpected_files == ()
    assert report.repository_consistent is False


def test_mission_review_verify_and_report_cli(tmp_path: Path, monkeypatch) -> None:
    mission = create_mission(tmp_path)
    service = Mock(spec=JarvisService)
    service.git_status.return_value = [
        change("backend/app/jarvis/reviewer.py"),
        change("backend/tests/test_reviewer.py"),
    ]
    output = []
    commands = iter(["mission verify", "mission review", "mission report", "exit"])
    monkeypatch.chdir(tmp_path)

    start_cli(
        service_factory=lambda: service,
        mission_factory=lambda: mission,
        input_func=lambda prompt: next(commands),
        output_func=output.append,
    )

    rendered = "\n".join(output)
    assert "Repository consistency: consistent" in rendered
    assert rendered.count("Recommendation: NEEDS_REVIEW") == 2
    assert "Test summary: not available" in rendered


def test_old_completed_mission_ignores_files_from_later_completed_missions(
    tmp_path: Path,
) -> None:
    reviewer = MissionReviewer(
        create_completed_history(tmp_path),
        lambda: [change("provider.py", "?", "?"), change("test_provider.py", "?", "?")],
        tmp_path,
        lambda: RecordedTestSummary("pytest reviewer", passed=5, exit_code=0),
    )

    report = reviewer.review()

    assert report.verification.missing_files == ()
    assert report.verification.unexpected_files == ()
    assert report.verification.repository_consistent is True
    assert report.recommendation == "ACCEPT"


def test_legacy_completed_stage_gets_roadmap_sequence(tmp_path: Path) -> None:
    mission = create_completed_history(tmp_path)
    roadmap = json.loads((tmp_path / "roadmap.yaml").read_text(encoding="utf-8"))
    roadmap["stages"][0].pop("completion_sequence")
    (tmp_path / "roadmap.yaml").write_text(json.dumps(roadmap), encoding="utf-8")

    assert mission.preview_stage("reviewer").completion_sequence == 1


def test_completed_mission_rejects_unrelated_manual_modification(tmp_path: Path) -> None:
    reviewer = MissionReviewer(
        create_completed_history(tmp_path),
        lambda: [change("provider.py"), change("manual.py")],
        tmp_path,
    )

    report = reviewer.review()

    assert report.verification.unexpected_files == ("manual.py",)
    assert report.recommendation == "REJECT"


def test_completed_mission_rejects_missing_expected_file(tmp_path: Path) -> None:
    mission = create_completed_history(tmp_path)
    (tmp_path / "reviewer.py").unlink()
    reviewer = MissionReviewer(mission, lambda: [], tmp_path)

    report = reviewer.review()

    assert report.verification.missing_files == ("reviewer.py",)
    assert report.recommendation == "REJECT"
