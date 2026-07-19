"""Read-only coordination for reviewing completed mission work."""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Optional, Protocol, Sequence, Tuple, Union

from .mission import MissionService
from .models_mission import MissionStage


class RepositoryChange(Protocol):
    """Structural view of a repository status entry."""

    path: str
    index_status: str
    worktree_status: str


@dataclass(frozen=True)
class TestSummary:
    """Previously captured test execution results supplied to the reviewer."""

    command: str
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    exit_code: Optional[int] = None

    @property
    def successful(self) -> bool:
        return self.exit_code == 0 and self.failed == 0


@dataclass(frozen=True)
class VerificationReport:
    """Repository-only verification against an approved mission scope."""

    mission_id: str
    mission_name: str
    lifecycle: str
    expected_files: Tuple[str, ...]
    detected_modified_files: Tuple[str, ...]
    missing_files: Tuple[str, ...]
    required_created_files: Tuple[str, ...]
    unexpected_files: Tuple[str, ...]
    repository_consistent: bool


@dataclass(frozen=True)
class ReviewReport:
    """Structured mission review including supplied test results."""

    verification: VerificationReport
    test_summary: Optional[TestSummary]
    recommendation: str


class MissionReviewer:
    """Compare repository status and recorded tests with the current mission."""

    def __init__(
        self,
        mission_service: MissionService,
        status_provider: Callable[[], Sequence[RepositoryChange]],
        repository_root: Union[str, Path],
        test_summary_provider: Optional[Callable[[], Optional[TestSummary]]] = None,
    ) -> None:
        self._mission_service = mission_service
        self._status_provider = status_provider
        self._repository_root = Path(repository_root)
        self._test_summary_provider = test_summary_provider or (lambda: None)
        self._latest_report: Optional[ReviewReport] = None

    def verify(self) -> VerificationReport:
        """Verify repository changes without executing code or tests."""
        stage = self._review_stage()
        expected = self._normalized((*stage.estimated_files, *stage.allowed_companion_files))
        changes = tuple(self._status_provider())
        detected = self._normalized(change.path for change in changes)
        detected_set = set(detected)
        expected_set = set(expected)
        completed = self._completed_stage_ids()
        owned_by_other_completed_missions = set(self._normalized(
            path
            for item in self._mission_service.load_roadmap().stages
            if item.id != stage.id and item.id in completed
            for path in (*item.estimated_files, *item.allowed_companion_files)
        ))
        missing = tuple(
            path
            for path in expected
            if self._has_status(path, changes, "D")
            or (
                stage.id in completed
                and not (self._repository_root / Path(*PurePosixPath(path).parts)).is_file()
            )
            or (stage.id not in completed and path not in detected_set)
        )
        required_created = tuple(
            path
            for path in expected
            if path in detected_set and self._has_status(path, changes, "A?")
        )
        unexpected = tuple(
            path
            for path in detected
            if path not in expected_set and path not in owned_by_other_completed_missions
        )
        paths_valid = all(self._is_repository_path(path) for path in detected)
        return VerificationReport(
            mission_id=stage.id,
            mission_name=stage.name,
            lifecycle=self._mission_service.mission_status(),
            expected_files=expected,
            detected_modified_files=detected,
            missing_files=missing,
            required_created_files=required_created,
            unexpected_files=unexpected,
            repository_consistent=not missing and not unexpected and paths_valid,
        )

    def review(self) -> ReviewReport:
        """Create and retain a review report from read-only inputs."""
        verification = self.verify()
        tests = self._test_summary_provider()
        if not verification.repository_consistent or (tests and not tests.successful):
            recommendation = "REJECT"
        elif tests is None:
            recommendation = "NEEDS_REVIEW"
        else:
            recommendation = "ACCEPT"
        report = ReviewReport(verification, tests, recommendation)
        self._latest_report = report
        return report

    def latest_report(self) -> ReviewReport:
        """Return the latest report created by this reviewer instance."""
        if self._latest_report is None:
            raise ValueError("No mission review report is available.")
        return self._latest_report

    def _review_stage(self) -> MissionStage:
        state = self._mission_service.load_state()
        stage_id = state.active_mission or state.last_completed_stage
        if not stage_id:
            raise ValueError("No active or completed mission is available for review.")
        stage = self._mission_service.preview_stage(stage_id)
        if stage is None:
            raise ValueError(f"Mission is not in the roadmap: {stage_id}")
        return stage

    def _completed_stage_ids(self) -> set[str]:
        state = self._mission_service.load_state()
        completed = set(state.completed_stages)
        completed.update(
            stage.id
            for stage in self._mission_service.load_roadmap().stages
            if stage.status == "completed"
        )
        return completed

    def _is_repository_path(self, path: str) -> bool:
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            return False
        try:
            (self._repository_root / Path(*candidate.parts)).resolve().relative_to(
                self._repository_root.resolve()
            )
        except ValueError:
            return False
        return True

    @staticmethod
    def _has_status(
        path: str,
        changes: Sequence[RepositoryChange],
        statuses: str,
    ) -> bool:
        return any(
            MissionReviewer._normalize(change.path) == path
            and (
                change.index_status in statuses
                or change.worktree_status in statuses
            )
            for change in changes
        )

    @staticmethod
    def _normalized(paths: Iterable[str]) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(MissionReviewer._normalize(path) for path in paths))

    @staticmethod
    def _normalize(path: str) -> str:
        normalized = path.replace("\\", "/").rpartition(" -> ")[2]
        return str(PurePosixPath(normalized))
