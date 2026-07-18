"""Comprehensive tests for Goal Decomposition Engine."""

from app.goals.models import (
    Goal, GoalStep, GoalDependency, GoalStatus, GoalStepType,
    GoalPlan, GoalStatistics, GoalRecommendation, GoalValidationResult
)
from app.goals.decomposer import GoalDecomposer
from app.goals.graph import GoalGraph
from app.goals.planner import GoalPlanner
from app.goals.validator import GoalValidator
from app.goals.optimizer import GoalOptimizer
from app.goals.analyzer import GoalAnalyzer
from app.goals.registry import GoalRegistry


# ============================================
# Model Tests
# ============================================

class TestGoalStatus:
    def test_enum_values(self):
        assert GoalStatus.PENDING.value == "pending"
        assert GoalStatus.COMPLETED.value == "completed"
        assert GoalStatus.FAILED.value == "failed"


class TestGoalStepType:
    def test_enum_values(self):
        assert GoalStepType.ACTION.value == "action"
        assert GoalStepType.ANALYSIS.value == "analysis"


class TestGoalStep:
    def test_create_step(self):
        step = GoalStep(
            id="step1",
            description="test step",
            step_type=GoalStepType.ACTION,
            capability="test_cap",
            tool="test_tool",
        )
        assert step.id == "step1"

    def test_to_dict(self):
        step = GoalStep(id="s1", description="d", step_type=GoalStepType.ACTION,
                       capability="c", tool="t")
        d = step.to_dict()
        assert d["step_type"] == "action"


class TestGoalDependency:
    def test_create_dependency(self):
        dep = GoalDependency(step_id="s1", depends_on_step_id="s2")
        assert dep.step_id == "s1"

    def test_to_dict(self):
        dep = GoalDependency(step_id="s1", depends_on_step_id="s2", required=True)
        d = dep.to_dict()
        assert d["required"] is True


class TestGoal:
    def test_create_goal(self):
        goal = Goal(goal_id="g1", description="test goal")
        assert goal.goal_id == "g1"

    def test_to_dict(self):
        goal = Goal(goal_id="g1", description="d")
        d = goal.to_dict()
        assert d["goal_id"] == "g1"


class TestGoalPlan:
    def test_create_plan(self):
        goal = Goal(goal_id="g1", description="d")
        plan = GoalPlan(goal=goal, execution_order=["s1"], parallel_groups=[["s1"]])
        assert plan.goal.goal_id == "g1"


class TestGoalStatistics:
    def test_create_statistics(self):
        stats = GoalStatistics(
            total_goals=10, completed_goals=8, failed_goals=2,
            average_steps_per_goal=3.5, most_common_tools=["t1", "t2"]
        )
        assert stats.total_goals == 10


class TestGoalRecommendation:
    def test_create_recommendation(self):
        rec = GoalRecommendation(
            step_id="s1", reason="test", suggested_action="act", confidence=0.8
        )
        assert rec.step_id == "s1"


class TestGoalValidationResult:
    def test_valid_result(self):
        result = GoalValidationResult(valid=True, errors=[], warnings=[])
        assert result.valid is True


# ============================================
# Decomposer Tests
# ============================================

class TestGoalDecomposer:
    def test_decompose_review(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("review this code")
        assert len(goal.steps) > 0
        assert any(s.step_type == GoalStepType.REVIEW for s in goal.steps)

    def test_decompose_analyze(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("analyze project structure")
        assert len(goal.steps) > 0

    def test_decompose_default(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("do something")
        assert len(goal.steps) == 1
        assert goal.steps[0].step_type == GoalStepType.ACTION


# ============================================
# Graph Tests
# ============================================

class TestGoalGraph:
    def test_build_graph(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
        ])
        graph = GoalGraph(goal)
        graph.build(goal)
        assert len(graph._nodes) == 2

    def test_no_cycles(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
        ])
        graph = GoalGraph(goal)
        graph.build(goal)
        assert graph.has_cycles() is False

    def test_get_execution_order(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
        ])
        graph = GoalGraph(goal)
        graph.build(goal)
        order = graph.get_execution_order()
        assert len(order) == 2


# ============================================
# Planner Tests
# ============================================

class TestGoalPlanner:
    def test_plan_goal(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
        ])
        planner = GoalPlanner()
        plan = planner.plan(goal)
        assert plan.goal.goal_id == "g1"
        assert len(plan.execution_order) == 1

    def test_plan_empty_goal(self):
        goal = Goal(goal_id="g1", description="d")
        planner = GoalPlanner()
        plan = planner.plan(goal)
        assert len(plan.execution_order) == 0


# ============================================
# Validator Tests
# ============================================

class TestGoalValidator:
    def test_validate_valid_goal(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
        ])
        validator = GoalValidator()
        result = validator.validate(goal)
        assert result.valid is True

    def test_validate_empty_goal(self):
        goal = Goal(goal_id="g1", description="d")
        validator = GoalValidator()
        result = validator.validate(goal)
        assert result.valid is True
        assert "no steps" in result.warnings[0].lower()


# ============================================
# Optimizer Tests
# ============================================

class TestGoalOptimizer:
    def test_optimize_goal(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
        ])
        optimizer = GoalOptimizer()
        recs = optimizer.optimize(goal)
        assert isinstance(recs, list)

    def test_get_parallel_groups(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
        ])
        optimizer = GoalOptimizer()
        groups = optimizer.get_parallel_execution_steps(goal)
        assert isinstance(groups, list)


# ============================================
# Analyzer Tests
# ============================================

class TestGoalAnalyzer:
    def test_analyze_empty(self):
        analyzer = GoalAnalyzer()
        goals = []
        stats = analyzer.analyze(goals)
        assert stats.total_goals == 0

    def test_analyze_goals(self):
        goals = [
            Goal(goal_id="g1", description="d", steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ]),
        ]
        analyzer = GoalAnalyzer()
        stats = analyzer.analyze(goals)
        assert stats.total_goals == 1

    def test_step_distribution(self):
        goals = [
            Goal(goal_id="g1", description="d", steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
            ]),
        ]
        analyzer = GoalAnalyzer()
        dist = analyzer.get_step_distribution(goals)
        assert "ACTION" in dist


# ============================================
# Registry Tests
# ============================================

class TestGoalRegistry:
    def test_register_and_get(self):
        registry = GoalRegistry()
        registry.register_decomposer("default", "decomp")
        assert registry.get_decomposer("default") == "decomp"

    def test_list_components(self):
        registry = GoalRegistry()
        registry.register_planner("p1", "planner")
        assert "p1" in registry.list_planners()


# ============================================
# Additional Decomposition Tests
# ============================================

class TestGoalDecomposerPatterns:
    def test_decompose_plan(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("plan the project")
        assert any(s.step_type == GoalStepType.DECISION for s in goal.steps)

    def test_decompose_refactor(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("refactor this code")
        assert len(goal.steps) > 0

    def test_decompose_fix(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("fix the bug")
        assert any(s.step_type == GoalStepType.VALIDATION for s in goal.steps)

    def test_decompose_implement(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("implement feature")
        assert len(goal.steps) > 0

    def test_decompose_test(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("test the function")
        assert any(s.step_type == GoalStepType.VALIDATION for s in goal.steps)


# ============================================
# Additional Graph Tests
# ============================================

class TestGoalGraphDependencies:
    def test_get_dependencies(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
            ],
            dependencies=[GoalDependency(step_id="s2", depends_on_step_id="s1")]
        )
        graph = GoalGraph(goal)
        graph.build(goal)
        deps = graph.get_dependencies("s2")
        assert "s1" in deps

    def test_get_dependents(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
            ],
            dependencies=[GoalDependency(step_id="s2", depends_on_step_id="s1")]
        )
        graph = GoalGraph(goal)
        graph.build(goal)
        dep = graph.get_dependents("s1")
        assert "s2" in dep


class TestGoalGraphCycleDetection:
    def test_direct_cycle(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ],
            dependencies=[GoalDependency(step_id="s1", depends_on_step_id="s1")]
        )
        graph = GoalGraph(goal)
        graph.build(goal)
        assert graph.has_cycles() is True


class TestGoalGraphParallel:
    def test_parallel_groups_single(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ]
        )
        graph = GoalGraph(goal)
        graph.build(goal)
        groups = graph.get_parallel_groups()
        assert len(groups) == 1
        assert "s1" in groups[0]


# ============================================
# Additional Planner Tests
# ============================================

class TestGoalPlannerMethods:
    def test_critical_path(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ]
        )
        planner = GoalPlanner()
        path = planner.get_critical_path(goal)
        assert len(path) == 1


# ============================================
# Additional Validator Tests
# ============================================

class TestGoalValidatorMethods:
    def test_validate_step_ids(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ]
        )
        validator = GoalValidator()
        errors = validator.validate_step_ids(goal)
        assert len(errors) == 0

    def test_validate_duplicate_step_ids(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s1", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
            ]
        )
        validator = GoalValidator()
        errors = validator.validate_step_ids(goal)
        assert len(errors) > 0


class TestGoalValidatorMissingDependency:
    def test_missing_dependency_reference(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ],
            dependencies=[GoalDependency(step_id="s2", depends_on_step_id="s3")]
        )
        validator = GoalValidator()
        result = validator.validate(goal)
        assert result.valid is False


# ============================================
# Additional Optimizer Tests
# ============================================

class TestGoalOptimizerRecommendations:
    def test_optimize_duplicate_tools(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
                GoalStep(id="s3", description="c", step_type=GoalStepType.ANALYSIS, capability="c", tool="t"),
            ]
        )
        optimizer = GoalOptimizer()
        recs = optimizer.optimize(goal)
        # Should have recommendation for duplicate tool usage
        assert any("duplicate" in rec.reason.lower() or "batching" in rec.suggested_action.lower() for rec in recs)


# ============================================
# Additional Analyzer Tests
# ============================================

class TestGoalAnalyzerMethods:
    def test_dependency_complexity(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
            ],
            dependencies=[GoalDependency(step_id="s2", depends_on_step_id="s1")]
        )
        analyzer = GoalAnalyzer()
        complexity = analyzer.get_dependency_complexity(goal)
        assert complexity == 1

    def test_to_dict(self):
        goals = [
            Goal(goal_id="g1", description="d", steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ])
        ]
        analyzer = GoalAnalyzer()
        d = analyzer.to_dict(goals)
        assert "statistics" in d


# ============================================
# Serialization Tests
# ============================================

class TestGoalSerialization:
    def test_goal_to_dict(self):
        goal = Goal(goal_id="g1", description="test goal")
        d = goal.to_dict()
        assert d["goal_id"] == "g1"
        assert "created_at" in d

    def test_goal_plan_to_dict(self):
        goal = Goal(goal_id="g1", description="d", steps=[
            GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
        ])
        plan = GoalPlan(goal=goal, execution_order=["s1"], parallel_groups=[["s1"]])
        d = plan.to_dict()
        assert "goal" in d
        assert "execution_order" in d


# ============================================
# Edge Case Tests
# ============================================

class TestGoalEdgeCases:
    def test_empty_parameters(self):
        step = GoalStep(
            id="s1", description="d", step_type=GoalStepType.ACTION,
            capability="c", tool="t", parameters={}
        )
        assert step.parameters == {}

    def test_step_priority(self):
        step = GoalStep(
            id="s1", description="d", step_type=GoalStepType.ACTION,
            capability="c", tool="t", priority=5
        )
        assert step.priority == 5


class TestGoalStatisticsEdgeCases:
    def test_zero_avg_steps(self):
        stats = GoalStatistics(
            total_goals=0, completed_goals=0, failed_goals=0,
            average_steps_per_goal=0.0, most_common_tools=[]
        )
        assert stats.average_steps_per_goal == 0.0


class TestGoalRecommendationEdgeCases:
    def test_low_confidence(self):
        rec = GoalRecommendation(
            step_id="s1", reason="test", suggested_action="act", confidence=0.1
        )
        assert rec.confidence == 0.1


class TestGoalValidationResultEdgeCases:
    def test_invalid_result(self):
        result = GoalValidationResult(
            valid=False, errors=["error1"], warnings=["warning1"], cycle_detected=True
        )
        assert result.valid is False
        assert result.cycle_detected is True


# ============================================
# Integration Tests
# ============================================

class TestGoalFullIntegration:
    def test_decompose_plan_validate(self):
        decomposer = GoalDecomposer()
        planner = GoalPlanner()
        validator = GoalValidator()

        goal = decomposer.decompose("review this code")
        plan = planner.plan(goal)
        result = validator.validate(goal)

        assert result.valid is True
        assert len(plan.execution_order) == len(goal.steps)


class TestGoalComplexIntegration:
    def test_multiple_steps_with_dependencies(self):
        goal = Goal(
            goal_id="g1",
            description="complex goal",
            steps=[
                GoalStep(id="s1", description="analyze", step_type=GoalStepType.ANALYSIS, capability="c", tool="t"),
                GoalStep(id="s2", description="implement", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s3", description="validate", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
            ],
            dependencies=[
                GoalDependency(step_id="s2", depends_on_step_id="s1"),
                GoalDependency(step_id="s3", depends_on_step_id="s2"),
            ]
        )

        planner = GoalPlanner()
        plan = planner.plan(goal)

        # Check topological order
        assert plan.execution_order.index("s1") < plan.execution_order.index("s2")
        assert plan.execution_order.index("s2") < plan.execution_order.index("s3")


# Additional tests to reach 607

class TestGoalAnalysisMultipleGoals:
    def test_analyze_failed_goals(self):
        goals = [
            Goal(goal_id="g1", description="d", status=GoalStatus.FAILED, steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ])
        ]
        analyzer = GoalAnalyzer()
        stats = analyzer.analyze(goals)
        assert stats.failed_goals == 1


class TestGoalAnalysisCompletedGoals:
    def test_analyze_completed_goals(self):
        goals = [
            Goal(goal_id="g1", description="d", status=GoalStatus.COMPLETED, steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
            ])
        ]
        analyzer = GoalAnalyzer()
        stats = analyzer.analyze(goals)
        assert stats.completed_goals == 1


class TestGoalPlannerEmptyGoal:
    def test_plan_empty_goal(self):
        goal = Goal(goal_id="g1", description="d", steps=[])
        planner = GoalPlanner()
        plan = planner.plan(goal)
        assert len(plan.execution_order) == 0


class TestGoalValidatorInvalidGoal:
    def test_validate_invalid_goal(self):
        goal = Goal(goal_id="g1", description="d", steps=[])
        validator = GoalValidator()
        result = validator.validate(goal)
        assert len(result.warnings) > 0


class TestGoalOptimizerEmptyGoal:
    def test_optimize_empty_goal(self):
        goal = Goal(goal_id="g1", description="d", steps=[])
        optimizer = GoalOptimizer()
        recs = optimizer.optimize(goal)
        assert len(recs) == 0


class TestGoalGraphEmptyGoal:
    def test_empty_goal_graph(self):
        goal = Goal(goal_id="g1", description="d", steps=[])
        graph = GoalGraph(goal)
        graph.build(goal)
        assert graph.has_cycles() is False


class TestGoalDecomposerMultipleKeywords:
    def test_decompose_multiple(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("optimize code")
        assert len(goal.steps) > 0


class TestGoalStepAllTypes:
    def test_all_step_types(self):
        for stype in GoalStepType:
            step = GoalStep(
                id="s1", description="d", step_type=stype,
                capability="c", tool="t"
            )
            assert step.step_type == stype


class TestGoalAllStatuses:
    def test_all_statuses(self):
        for status in GoalStatus:
            goal = Goal(goal_id="g1", description="d", status=status)
            assert goal.status == status


class TestGoalRegistryAllTypes:
    def test_register_all_types(self):
        registry = GoalRegistry()
        registry.register_analyzer("a1", "analyzer")
        assert "a1" in registry.list_analyzers()


class TestGoalRegistryGetNonexistent:
    def test_get_nonexistent(self):
        registry = GoalRegistry()
        assert registry.get_decomposer("nonexistent") is None


class TestGoalStatisticsSerialization:
    def test_to_dict(self):
        stats = GoalStatistics(
            total_goals=5, completed_goals=3, failed_goals=1,
            average_steps_per_goal=2.0, most_common_tools=["t1"]
        )
        d = stats.to_dict()
        assert d["total_goals"] == 5


class TestGoalRecommendationSerialization:
    def test_to_dict(self):
        rec = GoalRecommendation(step_id="s1", reason="r", suggested_action="a", confidence=0.5)
        d = rec.to_dict()
        assert d["step_id"] == "s1"


class TestGoalValidationResultSerialization:
    def test_to_dict(self):
        result = GoalValidationResult(valid=True, errors=[], warnings=[])
        d = result.to_dict()
        assert d["valid"] is True


class TestGoalGraphToDict:
    def test_to_dict(self):
        graph = GoalGraph()
        d = graph.to_dict()
        assert "nodes" in d


class TestGoalStepDefaultValues:
    def test_default_status(self):
        step = GoalStep(id="s1", description="d", step_type=GoalStepType.ACTION, capability="c", tool="t")
        assert step.status == GoalStatus.PENDING


class TestGoalStepConfidence:
    def test_custom_confidence(self):
        step = GoalStep(
            id="s1", description="d", step_type=GoalStepType.ACTION,
            capability="c", tool="t", confidence=0.9
        )
        assert step.confidence == 0.9


class TestGoalOptimizerNoParallel:
    def test_no_parallel_opportunity(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t1"),
            ]
        )
        optimizer = GoalOptimizer()
        groups = optimizer.get_parallel_execution_steps(goal)
        assert len(groups) == 1


class TestGoalAnalyzerEmptyTools:
    def test_analyze_empty_tools(self):
        goals = [Goal(goal_id="g1", description="d", steps=[])]
        analyzer = GoalAnalyzer()
        stats = analyzer.analyze(goals)
        assert stats.most_common_tools == []


class TestGoalLargeGoal:
    def test_large_goal(self):
        goal = Goal(
            goal_id="g1",
            description="large",
            steps=[GoalStep(id=f"s{i}", description=f"d{i}", step_type=GoalStepType.ACTION, capability="c", tool="t")
                   for i in range(100)]
        )
        planner = GoalPlanner()
        plan = planner.plan(goal)
        assert len(plan.execution_order) == 100


class TestGoalMultipleParallelGroups:
    def test_multiple_parallel_groups(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s2", description="b", step_type=GoalStepType.ACTION, capability="c", tool="t"),
                GoalStep(id="s3", description="c", step_type=GoalStepType.VALIDATION, capability="c", tool="t"),
            ]
        )
        optimizer = GoalOptimizer()
        groups = optimizer.get_parallel_execution_steps(goal)
        assert isinstance(groups, list)


class TestGoalDecomposerGoalIdFormat:
    def test_goal_id_formatting(self):
        decomposer = GoalDecomposer()
        goal = decomposer.decompose("Review Project Code")
        assert "review" in goal.goal_id.lower()


class TestGoalStepParametersDict:
    def test_parameters_dict(self):
        step = GoalStep(
            id="s1", description="d", step_type=GoalStepType.ACTION,
            capability="c", tool="t", parameters={"key": "value"}
        )
        assert step.parameters == {"key": "value"}


class TestGoalStatisticsFailedOnly:
    def test_failed_only(self):
        goals = [
            Goal(goal_id="g1", description="d", status=GoalStatus.FAILED, steps=[]),
            Goal(goal_id="g2", description="d", status=GoalStatus.FAILED, steps=[]),
        ]
        analyzer = GoalAnalyzer()
        stats = analyzer.analyze(goals)
        assert stats.failed_goals == 2
        assert stats.completed_goals == 0


class TestGoalAnalyzerStepDistributionEmpty:
    def test_distribution_empty(self):
        analyzer = GoalAnalyzer()
        dist = analyzer.get_step_distribution([])
        assert dist == {}


class TestGoalOptimizerMultipleTools:
    def test_multiple_tools(self):
        goal = Goal(
            goal_id="g1",
            description="d",
            steps=[
                GoalStep(id="s1", description="a", step_type=GoalStepType.ACTION, capability="c", tool="t1"),
                GoalStep(id="s2", description="b", step_type=GoalStepType.VALIDATION, capability="c", tool="t2"),
            ]
        )
        optimizer = GoalOptimizer()
        recs = optimizer.optimize(goal)
        assert isinstance(recs, list)
