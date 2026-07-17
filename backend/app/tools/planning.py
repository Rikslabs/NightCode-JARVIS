from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

from app.tools.project_index import ProjectIndex
from app.tools.review import ReviewTool, ReviewReport


class PlanType(Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    REVIEW_RESOLUTION = "review_resolution"
    ARCHITECTURE_CHANGE = "architecture_change"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AffectedModule:
    name: str
    path: str
    change_type: str  # modify, create, delete
    estimated_changes: int = 0


@dataclass
class DependencyRequirement:
    name: str
    version: Optional[str] = None
    purpose: str = ""


@dataclass
class RiskAssessment:
    level: RiskLevel
    description: str
    mitigation: str = ""


@dataclass
class EstimatedImpact:
    performance: ImpactLevel = ImpactLevel.LOW
    breaking_changes: bool = False
    backward_compatibility_risk: RiskLevel = RiskLevel.LOW
    affected_modules: list[AffectedModule] = field(default_factory=list)


@dataclass
class PlanStep:
    title: str
    description: str
    order: int
    estimated_effort: str  # small, medium, large
    validations: list[str] = field(default_factory=list)
    rollback: str = "Revert changes via version control."


@dataclass
class PlanPhase:
    name: str
    steps: list[PlanStep] = field(default_factory=list)
    estimated_duration: str = "unknown"


@dataclass
class ImplementationSummary:
    goal: str
    plan_type: PlanType
    priority: str
    estimated_complexity: str
    estimated_file_count: int
    phases: list[PlanPhase] = field(default_factory=list)
    dependencies: list[DependencyRequirement] = field(default_factory=list)
    risks: list[RiskAssessment] = field(default_factory=list)
    impact: EstimatedImpact = field(default_factory=EstimatedImpact)
    testing_strategy: str = ""
    validation_strategy: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "plan_type": self.plan_type.value,
            "priority": self.priority,
            "estimated_complexity": self.estimated_complexity,
            "estimated_file_count": self.estimated_file_count,
            "phases": [
                {
                    "name": p.name,
                    "estimated_duration": p.estimated_duration,
                    "steps": [
                        {
                            "title": s.title,
                            "description": s.description,
                            "order": s.order,
                            "estimated_effort": s.estimated_effort,
                            "validations": s.validations,
                            "rollback": s.rollback,
                        }
                        for s in p.steps
                    ],
                }
                for p in self.phases
            ],
            "dependencies": [
                {
                    "name": d.name,
                    "version": d.version,
                    "purpose": d.purpose,
                }
                for d in self.dependencies
            ],
            "risks": [
                {
                    "level": r.level.value,
                    "description": r.description,
                    "mitigation": r.mitigation,
                }
                for r in self.risks
            ],
            "impact": {
                "performance": self.impact.performance.value,
                "breaking_changes": self.impact.breaking_changes,
                "backward_compatibility_risk": self.impact.backward_compatibility_risk.value,
                "affected_modules": [
                    {
                        "name": m.name,
                        "path": m.path,
                        "change_type": m.change_type,
                        "estimated_changes": m.estimated_changes,
                    }
                    for m in self.impact.affected_modules
                ],
            },
            "testing_strategy": self.testing_strategy,
            "validation_strategy": self.validation_strategy,
        }


class PlanningTool:
    """Read-only engineering planning engine."""

    def __init__(self):
        self._coding = None  # placeholder for future AI integration
        self._index: Optional[ProjectIndex] = None
        self._review: Optional[ReviewTool] = None

    def plan_feature(self, project_path: str, goal: str, priority: str = "medium") -> ImplementationSummary:
        """Plan implementation of a new feature."""
        self._ensure_index(project_path)
        summary = self._get_project_summary(project_path)
        modules = summary.get("modules", [])

        affected = [AffectedModule(name=m, path=m + ".py", change_type="create", estimated_changes=1) for m in modules[:3]]

        phases = [
            PlanPhase(
                name="Design",
                steps=[
                    PlanStep(
                        title="Define feature scope",
                        description="Clarify requirements and acceptance criteria.",
                        order=1,
                        estimated_effort="small",
                        validations=["Stakeholder review", "Requirements doc"],
                    )
                ],
                estimated_duration="1-2 days",
            ),
            PlanPhase(
                name="Implementation",
                steps=[
                    PlanStep(
                        title="Implement core logic",
                        description=f"Add feature implementation for: {goal}",
                        order=2,
                        estimated_effort="medium",
                        validations=["Unit tests", "Integration tests"],
                    ),
                    PlanStep(
                        title="Add configuration",
                        description="Update configuration and environment setup.",
                        order=3,
                        estimated_effort="small",
                        validations=["Config validation", "Smoke test"],
                    ),
                ],
                estimated_duration="3-5 days",
            ),
            PlanPhase(
                name="Validation",
                steps=[
                    PlanStep(
                        title="Run test suite",
                        description="Execute full test suite and verify coverage.",
                        order=4,
                        estimated_effort="small",
                        validations=["All tests pass", "Coverage >= 80%"],
                    )
                ],
                estimated_duration="1 day",
            ),
        ]

        risks = [
            RiskAssessment(
                level=RiskLevel.MEDIUM,
                description="Integration complexity with existing modules.",
                mitigation="Add integration tests and review interfaces.",
            )
        ]

        return ImplementationSummary(
            goal=goal,
            plan_type=PlanType.FEATURE,
            priority=priority,
            estimated_complexity="medium",
            estimated_file_count=len(affected),
            phases=phases,
            dependencies=[],
            risks=risks,
            impact=EstimatedImpact(
                performance=ImpactLevel.MEDIUM,
                breaking_changes=False,
                backward_compatibility_risk=RiskLevel.LOW,
                affected_modules=affected,
            ),
            testing_strategy="Add unit and integration tests for new functionality.",
            validation_strategy="Run existing test suite; verify no regressions.",
        )

    def plan_bugfix(self, project_path: str, goal: str, priority: str = "high") -> ImplementationSummary:
        """Plan a bugfix."""
        self._ensure_index(project_path)
        summary = self._get_project_summary(project_path)
        modules = summary.get("modules", [])

        affected = [AffectedModule(name=m, path=m + ".py", change_type="modify", estimated_changes=1) for m in modules[:2]]

        phases = [
            PlanPhase(
                name="Investigation",
                steps=[
                    PlanStep(
                        title="Reproduce bug",
                        description=f"Confirm bug behavior: {goal}",
                        order=1,
                        estimated_effort="small",
                        validations=["Reproduction script", "Logs review"],
                    )
                ],
                estimated_duration="1 day",
            ),
            PlanPhase(
                name="Fix",
                steps=[
                    PlanStep(
                        title="Implement fix",
                        description="Apply minimal change to resolve issue.",
                        order=2,
                        estimated_effort="small",
                        validations=["Regression test", "Bug no longer reproducible"],
                    )
                ],
                estimated_duration="1-2 days",
            ),
        ]

        return ImplementationSummary(
            goal=goal,
            plan_type=PlanType.BUGFIX,
            priority=priority,
            estimated_complexity="low",
            estimated_file_count=len(affected),
            phases=phases,
            dependencies=[],
            risks=[RiskAssessment(level=RiskLevel.LOW, description="Minimal change scope.", mitigation="Code review and regression tests.")],
            impact=EstimatedImpact(
                performance=ImpactLevel.LOW,
                breaking_changes=False,
                backward_compatibility_risk=RiskLevel.LOW,
                affected_modules=affected,
            ),
            testing_strategy="Add regression test covering the bug scenario.",
            validation_strategy="Confirm bug is fixed and existing tests pass.",
        )

    def plan_refactor(self, project_path: str, goal: str, priority: str = "medium") -> ImplementationSummary:
        """Plan a refactoring effort."""
        self._ensure_index(project_path)
        summary = self._get_project_summary(project_path)
        modules = summary.get("modules", [])

        affected = [AffectedModule(name=m, path=m + ".py", change_type="modify", estimated_changes=2) for m in modules[:4]]

        phases = [
            PlanPhase(
                name="Analysis",
                steps=[
                    PlanStep(
                        title="Identify hotspots",
                        description="Locate code smells and complexity issues.",
                        order=1,
                        estimated_effort="small",
                        validations=["Review findings", "Metrics baseline"],
                    )
                ],
                estimated_duration="1 day",
            ),
            PlanPhase(
                name="Refactor",
                steps=[
                    PlanStep(
                        title="Apply refactoring",
                        description=f"Refactor to improve: {goal}",
                        order=2,
                        estimated_effort="medium",
                        validations=["Tests pass", "No behavior change"],
                    )
                ],
                estimated_duration="2-4 days",
            ),
        ]

        return ImplementationSummary(
            goal=goal,
            plan_type=PlanType.REFACTOR,
            priority=priority,
            estimated_complexity="medium",
            estimated_file_count=len(affected),
            phases=phases,
            dependencies=[],
            risks=[RiskAssessment(level=RiskLevel.MEDIUM, description="Behavioral regression risk.", mitigation="Comprehensive test coverage and incremental refactor.")],
            impact=EstimatedImpact(
                performance=ImpactLevel.LOW,
                breaking_changes=False,
                backward_compatibility_risk=RiskLevel.MEDIUM,
                affected_modules=affected,
            ),
            testing_strategy="Run full test suite after each refactoring step.",
            validation_strategy="Compare behavior before and after with integration tests.",
        )

    def plan_review_resolution(self, project_path: str, review_report: ReviewReport, priority: str = "medium") -> ImplementationSummary:
        """Plan resolution of review findings."""
        self._ensure_index(project_path)
        findings = review_report.findings
        high = [f for f in findings if f.severity.value in ("high", "critical")]
        modules = [f.file_path for f in high if f.file_path]

        affected = [AffectedModule(name=m.replace("/", ".").replace(".py", ""), path=m, change_type="modify", estimated_changes=1) for m in modules[:5]]

        phases = [
            PlanPhase(
                name="Triage",
                steps=[
                    PlanStep(
                        title="Classify findings",
                        description="Group findings by category and severity.",
                        order=1,
                        estimated_effort="small",
                        validations=["Findings catalog", "Owner assignment"],
                    )
                ],
                estimated_duration="1 day",
            ),
            PlanPhase(
                name="Remediation",
                steps=[
                    PlanStep(
                        title="Fix critical issues",
                        description="Address high/critical findings.",
                        order=2,
                        estimated_effort="medium",
                        validations=["Review pass", "Tests pass"],
                    )
                ],
                estimated_duration="2-5 days",
            ),
        ]

        return ImplementationSummary(
            goal="Resolve review findings",
            plan_type=PlanType.REVIEW_RESOLUTION,
            priority=priority,
            estimated_complexity="medium",
            estimated_file_count=len(affected),
            phases=phases,
            dependencies=[],
            risks=[RiskAssessment(level=RiskLevel.MEDIUM, description="Scope creep from findings.", mitigation="Prioritize critical/high findings only.")],
            impact=EstimatedImpact(
                performance=ImpactLevel.LOW,
                breaking_changes=False,
                backward_compatibility_risk=RiskLevel.LOW,
                affected_modules=affected,
            ),
            testing_strategy="Run tests after each batch of fixes.",
            validation_strategy="Re-run review to confirm findings resolved.",
        )

    def plan_architecture_change(self, project_path: str, goal: str, priority: str = "high") -> ImplementationSummary:
        """Plan an architecture change."""
        self._ensure_index(project_path)
        summary = self._get_project_summary(project_path)
        modules = summary.get("modules", [])

        affected = [AffectedModule(name=m, path=m + ".py", change_type="modify", estimated_changes=3) for m in modules[:5]]

        phases = [
            PlanPhase(
                name="Design",
                steps=[
                    PlanStep(
                        title="Architecture proposal",
                        description="Document target architecture and migration path.",
                        order=1,
                        estimated_effort="medium",
                        validations=["Architecture review", "Stakeholder approval"],
                    )
                ],
                estimated_duration="3-5 days",
            ),
            PlanPhase(
                name="Migration",
                steps=[
                    PlanStep(
                        title="Incremental migration",
                        description=f"Migrate modules to new architecture for: {goal}",
                        order=2,
                        estimated_effort="large",
                        validations=["Integration tests", "Performance benchmarks"],
                    )
                ],
                estimated_duration="1-2 weeks",
            ),
            PlanPhase(
                name="Validation",
                steps=[
                    PlanStep(
                        title="Final verification",
                        description="Validate all systems and rollback prepared.",
                        order=3,
                        estimated_effort="medium",
                        validations=["Full test suite", "Rollback drill"],
                    )
                ],
                estimated_duration="2-3 days",
            ),
        ]

        risks = [
            RiskAssessment(
                level=RiskLevel.HIGH,
                description="Architecture changes may introduce regressions.",
                mitigation="Incremental migration with feature flags and rollback plan.",
            )
        ]

        return ImplementationSummary(
            goal=goal,
            plan_type=PlanType.ARCHITECTURE_CHANGE,
            priority=priority,
            estimated_complexity="high",
            estimated_file_count=len(affected),
            phases=phases,
            dependencies=[],
            risks=risks,
            impact=EstimatedImpact(
                performance=ImpactLevel.HIGH,
                breaking_changes=True,
                backward_compatibility_risk=RiskLevel.HIGH,
                affected_modules=affected,
            ),
            testing_strategy="Run full suite plus targeted integration and performance tests.",
            validation_strategy="Review architecture against requirements and verify rollback.",
        )

    def _ensure_index(self, project_path: str) -> None:
        if not self._index:
            self._index = ProjectIndex(project_path)
            self._index.build_index()

    def _get_project_summary(self, project_path: str) -> dict[str, Any]:
        self._ensure_index(project_path)
        return self._index.get_project_summary()