"""Execution planner for the Intelligence Orchestrator."""

from typing import Any, Dict, List

from .models import (
    ExecutionPlan,
    ExecutionDecision,
    IntentAnalysis,
    IntentType,
    ReasoningContext,
)


class ExecutionPlanner:
    """
    Builds execution plans based on intent analysis.

    Creates step-by-step plans for fulfilling requests.
    """

    # Tool mapping based on intent types
    INTENT_TO_TOOL: Dict[IntentType, str] = {
        IntentType.REVIEW_PROJECT: "review",
        IntentType.PLAN_FEATURE: "planning",
        IntentType.PLAN_BUGFIX: "planning",
        IntentType.PLAN_REFACTOR: "planning",
        IntentType.ANALYZE_CODE: "coding",
        IntentType.QUERY_KNOWLEDGE: "knowledge",
        IntentType.EDIT_CODE: "editing",
        IntentType.EXECUTE_WORKFLOW: "workflow",
    }

    # Intents that require workflow execution
    WORKFLOW_INTENTS: set = {IntentType.EXECUTE_WORKFLOW}

    # Intents that require planning
    PLANNING_INTENTS: set = {
        IntentType.PLAN_FEATURE,
        IntentType.PLAN_BUGFIX,
        IntentType.PLAN_REFACTOR,
    }

    def create_plan(self, intent: IntentAnalysis, context: ReasoningContext) -> ExecutionPlan:
        """
        Create an execution plan based on the analyzed intent.

        Args:
            intent: The analyzed intent.
            context: The reasoning context.

        Returns:
            An execution plan with steps.
        """
        steps = self._build_steps(intent, context)

        return ExecutionPlan(
            goal=context.request,
            intent=intent.intent,
            steps=steps,
            estimated_steps=len(steps),
            requires_workflow=intent.intent in self.WORKFLOW_INTENTS,
            requires_planning=intent.intent in self.PLANNING_INTENTS,
        )

    def _build_steps(self, intent: IntentAnalysis, context: ReasoningContext) -> List[Dict[str, Any]]:
        """
        Build execution steps based on intent.

        Returns a list of step dictionaries.
        """
        steps = []

        if intent.intent == IntentType.REVIEW_PROJECT:
            steps = self._plan_review(context)
        elif intent.intent == IntentType.PLAN_FEATURE:
            steps = self._plan_feature(context)
        elif intent.intent == IntentType.PLAN_BUGFIX:
            steps = self._plan_bugfix(context)
        elif intent.intent == IntentType.PLAN_REFACTOR:
            steps = self._plan_refactor(context)
        elif intent.intent == IntentType.ANALYZE_CODE:
            steps = self._plan_analyze(context)
        elif intent.intent == IntentType.QUERY_KNOWLEDGE:
            steps = self._plan_query(context)
        elif intent.intent == IntentType.EDIT_CODE:
            steps = self._plan_edit(context)
        elif intent.intent == IntentType.EXECUTE_WORKFLOW:
            steps = self._plan_workflow(context)
        else:
            steps = self._plan_unknown(context)

        return steps

    def _plan_review(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan project review steps."""
        project_path = context.project_path or "."
        return [
            {
                "order": 1,
                "action": "review_project",
                "description": "Review entire project for quality issues",
                "tool": "review",
                "parameters": {"path": project_path},
            }
        ]

    def _plan_feature(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan feature implementation steps."""
        project_path = context.project_path or "."
        goal = context.request

        # Extract feature name if present
        feature_name = context.metadata.get("feature_name")

        return [
            {
                "order": 1,
                "action": "plan_feature",
                "description": f"Create implementation plan for: {goal}",
                "tool": "planning",
                "parameters": {"goal": goal, "project_path": project_path, "feature_name": feature_name},
            },
            {
                "order": 2,
                "action": "review_for_plan_validation",
                "description": "Review code to validate plan assumptions",
                "tool": "review",
                "parameters": {"path": project_path},
            },
        ]

    def _plan_bugfix(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan bugfix steps."""
        project_path = context.project_path or "."
        goal = context.request
        return [
            {
                "order": 1,
                "action": "plan_bugfix",
                "description": f"Create bugfix plan for: {goal}",
                "tool": "planning",
                "parameters": {"goal": goal, "project_path": project_path},
            }
        ]

    def _plan_refactor(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan refactoring steps."""
        project_path = context.project_path or "."
        goal = context.request
        return [
            {
                "order": 1,
                "action": "plan_refactor",
                "description": f"Create refactoring plan for: {goal}",
                "tool": "planning",
                "parameters": {"goal": goal, "project_path": project_path},
            }
        ]

    def _plan_analyze(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan code analysis steps."""
        entities = context.metadata.get("entities", [])
        file_path = entities[0] if entities else context.project_path

        return [
            {
                "order": 1,
                "action": "analyze_file",
                "description": f"Analyze code in: {file_path}",
                "tool": "coding",
                "parameters": {"operation": "analyze_module", "path": file_path},
            }
        ]

    def _plan_query(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan knowledge query steps."""
        return [
            {
                "order": 1,
                "action": "query_knowledge",
                "description": "Query knowledge base",
                "tool": "knowledge",
                "parameters": {"query": context.request},
            }
        ]

    def _plan_edit(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan code editing steps."""
        return [
            {
                "order": 1,
                "action": "edit_code",
                "description": "Prepare code modification",
                "tool": "editing",
                "parameters": {"request": context.request},
            }
        ]

    def _plan_workflow(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan workflow execution steps."""
        return [
            {
                "order": 1,
                "action": "execute_workflow",
                "description": "Run specified workflow",
                "tool": "workflow",
                "parameters": {"request": context.request},
            }
        ]

    def _plan_unknown(self, context: ReasoningContext) -> List[Dict[str, Any]]:
        """Plan for unknown/unclassified intents."""
        return [
            {
                "order": 1,
                "action": "fallback",
                "description": "Pass to AI for general response",
                "tool": "knowledge",
                "parameters": {"query": context.request},
            }
        ]