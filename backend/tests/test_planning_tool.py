import pytest
from pathlib import Path
from app.tools.planning import PlanningTool, PlanType, RiskLevel, ImpactLevel


@pytest.fixture
def planning_tool():
    return PlanningTool()


def test_plan_feature_basic(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_feature(str(tmp_path), "Add login", priority="high")
    assert plan.goal == "Add login"
    assert plan.plan_type == PlanType.FEATURE
    assert plan.priority == "high"
    assert plan.estimated_file_count >= 1
    assert len(plan.phases) >= 1
    assert plan.testing_strategy != ""


def test_plan_bugfix_basic(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_bugfix(str(tmp_path), "Fix crash", priority="critical")
    assert plan.plan_type == PlanType.BUGFIX
    assert plan.priority == "critical"
    assert plan.impact.breaking_changes is False
    assert len(plan.phases) >= 1


def test_plan_refactor_basic(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_refactor(str(tmp_path), "Cleanup code", priority="medium")
    assert plan.plan_type == PlanType.REFACTOR
    assert plan.impact.backward_compatibility_risk == RiskLevel.MEDIUM


def test_plan_architecture_change_basic(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_architecture_change(str(tmp_path), "Split monolith", priority="high")
    assert plan.plan_type == PlanType.ARCHITECTURE_CHANGE
    assert plan.impact.breaking_changes is True
    assert plan.impact.performance == ImpactLevel.HIGH
    assert any(r.level == RiskLevel.HIGH for r in plan.risks)


def test_plan_review_resolution_basic(planning_tool, tmp_path):
    from app.tools.review import ReviewReport, ReviewFinding, ReviewSeverity, ReviewCategory
    report = ReviewReport(findings=[
        ReviewFinding(category=ReviewCategory.SECURITY, severity=ReviewSeverity.CRITICAL, message="Bad", file_path="a.py"),
        ReviewFinding(category=ReviewCategory.DOCUMENTATION, severity=ReviewSeverity.LOW, message="Minor", file_path="b.py"),
    ])
    plan = planning_tool.plan_review_resolution(str(tmp_path), report, priority="high")
    assert plan.plan_type == PlanType.REVIEW_RESOLUTION
    assert plan.estimated_file_count >= 1
    assert plan.validation_strategy != ""


def test_implementation_summary_to_dict(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_feature(str(tmp_path), "Test goal")
    data = plan.to_dict()
    assert "goal" in data
    assert "phases" in data
    assert "risks" in data
    assert "impact" in data
    assert data["plan_type"] == "feature"


def test_plan_phases_have_steps(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_feature(str(tmp_path), "Test goal")
    for phase in plan.phases:
        assert phase.name != ""
        assert len(phase.steps) >= 1
        for step in phase.steps:
            assert step.title != ""
            assert step.order >= 1
            assert step.estimated_effort in {"small", "medium", "large"}


def test_plan_risk_assessment(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_feature(str(tmp_path), "Test goal")
    assert len(plan.risks) >= 1
    for risk in plan.risks:
        assert risk.level in RiskLevel
        assert risk.description != ""
        assert risk.mitigation != ""


def test_plan_affected_modules(planning_tool, tmp_path):
    (tmp_path / "module.py").write_text("pass\n", encoding="utf-8")
    plan = planning_tool.plan_feature(str(tmp_path), "Test goal")
    for mod in plan.impact.affected_modules:
        assert mod.name != ""
        assert mod.path != ""
        assert mod.change_type in {"create", "modify", "delete"}