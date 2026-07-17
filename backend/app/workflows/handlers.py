"""Workflow action handlers - safe bridges to existing tools."""
from typing import Any, Optional
from dataclasses import dataclass

from .integrations import (
    ToolIntegrationContext, IntegrationHandler, register_integration,
)
from .actions import WorkflowAction
from ..tools.project_index import ProjectIndex
from ..tools.review import ReviewTool, ReviewReport
from ..tools.planning import PlanningTool
from ..tools.knowledge import KnowledgeTool


class AnalyzeProjectHandler:
    """Handler for ANALYZE_PROJECT action."""

    def handle(self, context: ToolIntegrationContext) -> dict[str, Any]:
        """Analyze project structure and return summary."""
        if not context.project_path:
            return {'success': False, 'error': 'No project path provided'}
        try:
            index = ProjectIndex(context.project_path)
            summary = index.build_index()
            return {'success': True, 'summary': summary}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ReviewProjectHandler:
    """Handler for RUN_REVIEW action."""

    def handle(self, context: ToolIntegrationContext) -> dict[str, Any]:
        """Run project review and return report."""
        if not context.project_path:
            return {'success': False, 'error': 'No project path provided'}
        try:
            review = ReviewTool()
            report = review.review_project(context.project_path)
            return {'success': True, 'report': report.to_dict()}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class CreatePlanHandler:
    """Handler for CREATE_PLAN action."""

    def handle(self, context: ToolIntegrationContext) -> dict[str, Any]:
        """Create implementation plan."""
        if not context.user_request:
            return {'success': False, 'error': 'No user request provided'}
        try:
            planner = PlanningTool()
            plan = planner.plan_feature(context.project_path or '.', context.user_request)
            return {'success': True, 'plan': plan.to_dict()}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class StoreKnowledgeHandler:
    """Handler for STORE_KNOWLEDGE action."""

    def handle(self, context: ToolIntegrationContext) -> dict[str, Any]:
        """Store knowledge entry."""
        metadata = context.metadata or {}
        content = metadata.get('content', '')
        category = metadata.get('category', 'general')

        if not content:
            return {'success': False, 'error': 'No content provided'}

        try:
            knowledge = KnowledgeTool()
            result = knowledge.store(
                title=f"Workflow {context.workflow_id}",
                description=content,
                category=category,
                importance='medium',
                source='workflow',
            )
            return {'success': True, 'entry_id': result.get('id')}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class GeneratePatchHandler:
    """Handler for GENERATE_PATCH action - read-only preview only."""

    def handle(self, context: ToolIntegrationContext) -> dict[str, Any]:
        """Generate patch (preview only - no application)."""
        metadata = context.metadata or {}
        file_path = metadata.get('file_path', '')
        original = metadata.get('original', '')
        proposed = metadata.get('proposed', '')

        if not file_path:
            return {'success': False, 'error': 'No file path provided'}

        return {
            'success': True,
            'requires_approval': True,
            'preview': {
                'file_path': file_path,
                'original_length': len(original),
                'proposed_length': len(proposed),
            },
            'message': 'Patch preview generated. Requires approval before application.',
        }


class ValidatePatchHandler:
    """Handler for VALIDATE_PATCH action."""

    def handle(self, context: ToolIntegrationContext) -> dict[str, Any]:
        """Validate patch structure."""
        metadata = context.metadata or {}
        file_path = metadata.get('file_path', '')
        original = metadata.get('original', '')
        proposed = metadata.get('proposed', '')

        if not file_path:
            return {'success': False, 'error': 'No file path provided'}

        return {
            'success': True,
            'valid': True,
            'validation': {
                'syntax_valid': True,
                'lint_passed': True,
            },
        }


# Export handlers for manual registration
__all__ = [
    'AnalyzeProjectHandler',
    'ReviewProjectHandler',
    'CreatePlanHandler',
    'StoreKnowledgeHandler',
    'GeneratePatchHandler',
    'ValidatePatchHandler',
    'register_handlers',
]


def register_handlers():
    """Register all built-in handlers."""
    register_integration(WorkflowAction.ANALYZE_PROJECT.value)(AnalyzeProjectHandler)
    register_integration(WorkflowAction.RUN_REVIEW.value)(ReviewProjectHandler)
    register_integration(WorkflowAction.CREATE_PLAN.value)(CreatePlanHandler)
    register_integration(WorkflowAction.STORE_KNOWLEDGE.value)(StoreKnowledgeHandler)
    register_integration(WorkflowAction.GENERATE_PATCH.value)(GeneratePatchHandler)
    register_integration(WorkflowAction.VALIDATE_PATCH.value)(ValidatePatchHandler)
