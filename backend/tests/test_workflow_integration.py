"""Tests for Workflow Integration Layer."""
import pytest
from app.workflows import (
    # Integrations
    ToolIntegrationContext, get_integration, list_integrations,
    execute_integration, clear_integrations,
    # Policies
    WorkflowPolicyEngine, PolicyDecision, SAFE_ACTIONS, RISKY_ACTIONS,
)
from app.workflows.actions import WorkflowAction
from app.workflows.handlers import register_handlers


# Register handlers before tests
register_handlers()


# Integration Manager Tests
def test_register_integration():
    """Test integration is registered."""
    handler = get_integration(WorkflowAction.ANALYZE_PROJECT.value)
    assert handler is not None


def test_list_integrations():
    """Test listing integrations."""
    all_integrations = list_integrations()
    assert len(all_integrations) >= 6


def test_execute_integration():
    """Test executing integration."""
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='.',
        user_request='test'
    )
    result = execute_integration(WorkflowAction.ANALYZE_PROJECT.value, context)
    assert result['success'] is True


def test_execute_unknown_integration():
    """Test executing unknown integration."""
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='.',
        user_request='test'
    )
    result = execute_integration('unknown_action', context)
    assert result['success'] is False
    assert 'error' in result


# Handler Tests
def test_analyze_handler():
    """Test analyze project handler."""
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='.',
        user_request='analyze'
    )
    result = execute_integration(WorkflowAction.ANALYZE_PROJECT.value, context)
    assert result['success'] is True
    assert 'summary' in result['data']


def test_review_handler():
    """Test review project handler."""
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='.',
        user_request='review'
    )
    result = execute_integration(WorkflowAction.RUN_REVIEW.value, context)
    assert result['success'] is True


def test_planning_handler():
    """Test planning handler."""
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='implement feature X'
    )
    result = execute_integration(WorkflowAction.CREATE_PLAN.value, context)
    assert result['success'] is True
    assert 'plan' in result['data']


def test_knowledge_handler():
    """Test knowledge storage handler."""
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='store',
        metadata={'content': 'test knowledge', 'category': 'testing'}
    )
    result = execute_integration(WorkflowAction.STORE_KNOWLEDGE.value, context)
    assert result['success'] is True
    assert 'entry_id' in result['data']


def test_validation_handler():
    """Test patch validation handler."""
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='validate',
        metadata={'file_path': 'test.py', 'original': 'old', 'proposed': 'new'}
    )
    result = execute_integration(WorkflowAction.VALIDATE_PATCH.value, context)
    assert result['success'] is True
    assert 'valid' in result['data']


# Policy Tests
def test_safe_actions_allowed():
    """Test safe actions are allowed without approval."""
    policy = WorkflowPolicyEngine()

    for action in SAFE_ACTIONS:
        decision = policy.evaluate_action(action)
        assert decision.allowed is True
        assert decision.requires_approval is False


def test_risky_actions_require_approval():
    """Test risky actions require approval."""
    policy = WorkflowPolicyEngine()

    for action in RISKY_ACTIONS:
        decision = policy.evaluate_action(action)
        assert decision.allowed is True
        assert decision.requires_approval is True


def test_unknown_actions_rejected():
    """Test unknown actions are rejected."""
    policy = WorkflowPolicyEngine()
    decision = policy.evaluate_action('unknown_action')
    assert decision.allowed is False
    assert decision.requires_approval is False


def test_policy_dict():
    """Test policy decision serialization."""
    policy = WorkflowPolicyEngine()
    decision = policy.evaluate_action(WorkflowAction.ANALYZE_PROJECT.value)
    d = decision.to_dict()
    assert d['allowed'] is True
    assert d['requires_approval'] is False


def test_policy_requires_approval():
    """Test requires_approval method."""
    policy = WorkflowPolicyEngine()
    assert policy.requires_approval(WorkflowAction.GENERATE_PATCH.value) is True
    assert policy.requires_approval(WorkflowAction.ANALYZE_PROJECT.value) is False


# Context Tests
def test_integration_context():
    """Test ToolIntegrationContext creation."""
    ctx = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='test request',
        metadata={'key': 'value'}
    )
    assert ctx.workflow_id == 'wf1'
    assert ctx.to_dict()['metadata'] == {'key': 'value'}


def test_integration_context_minimal():
    """Test minimal ToolIntegrationContext."""
    ctx = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='test'
    )
    assert ctx.metadata == {}


def test_generate_patch_handler_preview_only():
    """Test generate patch returns preview only."""
    register_handlers()
    context = ToolIntegrationContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='generate',
        metadata={
            'file_path': 'test.py',
            'original': 'def old(): pass',
            'proposed': 'def new(): pass'
        }
    )
    result = execute_integration(WorkflowAction.GENERATE_PATCH.value, context)
    assert result['success'] is True
    assert result['data']['requires_approval'] is True
