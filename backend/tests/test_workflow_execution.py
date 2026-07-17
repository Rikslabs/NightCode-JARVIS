"""Tests for Workflow Execution."""
import pytest
from app.workflows import (
    WorkflowEngine, WorkflowState, WorkflowStep, Workflow, WorkflowContext,
    WorkflowAction, ActionDefinition, WorkflowExecutor, WorkflowValidator,
    ValidationResult, register_action_direct, get_action, list_actions, remove_action,
    clear_registry
)


# Test actions registered via module
def setup_module():
    clear_registry()
    register_action_direct('analyze_project', ActionDefinition(
        name='analyze_project',
        description='Analyze project structure',
        requires_approval=False,
        risk_level='low'
    ))
    register_action_direct('apply_patch', ActionDefinition(
        name='apply_patch',
        description='Apply patch changes',
        requires_approval=True,
        risk_level='high'
    ))


def teardown_function():
    clear_registry()


# Registry Tests
def test_action_registration():
    """Test action registration."""
    setup_module()
    action = get_action('analyze_project')
    assert action is not None
    assert action.name == 'analyze_project'


def test_action_lookup():
    """Test action lookup."""
    setup_module()
    action = get_action('nonexistent')
    assert action is None


def test_list_actions():
    """Test listing all actions."""
    setup_module()
    actions = list_actions()
    assert len(actions) == 2


def test_remove_action():
    """Test removing an action."""
    setup_module()
    result = remove_action('analyze_project')
    assert result is True
    assert get_action('analyze_project') is None


def test_remove_nonexistent_action():
    """Test removing nonexistent action."""
    teardown_function()
    result = remove_action('nonexistent')
    assert result is False


# Validator Tests
def test_valid_workflow():
    """Test valid workflow validation."""
    validator = WorkflowValidator()
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = Workflow(id='wf1', name='Test', description='Test workflow', steps=steps)
    result = validator.validate_workflow(wf)
    assert result.valid is True
    assert result.errors == []


def test_invalid_workflow():
    """Test invalid workflow validation."""
    validator = WorkflowValidator()
    wf = Workflow(id='', name='Test', description='No id', steps=[])
    result = validator.validate_workflow(wf)
    assert result.valid is False
    assert 'id' in str(result.errors)


def test_missing_action():
    """Test missing action validation."""
    teardown_function()
    validator = WorkflowValidator()
    result = validator.validate_action('missing_action')
    assert result.valid is False


def test_valid_action():
    """Test valid action validation."""
    setup_module()
    validator = WorkflowValidator()
    result = validator.validate_action('analyze_project')
    assert result.valid is True


def test_invalid_context():
    """Test invalid context validation."""
    validator = WorkflowValidator()
    ctx = WorkflowContext(workflow_id='', project_path='', user_request='')
    result = validator.validate_context(ctx)
    assert result.valid is False


def test_valid_context():
    """Test valid context validation."""
    validator = WorkflowValidator()
    ctx = WorkflowContext(workflow_id='wf1', project_path='/project', user_request='Do something')
    result = validator.validate_context(ctx)
    assert result.valid is True


# Executor Tests
def test_workflow_execution():
    """Test workflow execution."""
    setup_module()
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine)
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    result = executor.execute(wf, ctx)
    assert result is not None
    assert result.success is True
    assert result.state == WorkflowState.COMPLETED


def test_multiple_step_execution():
    """Test multiple step execution."""
    setup_module()
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine)
    steps = [
        WorkflowStep(id='s1', name='Step 1', description='First', order=1),
        WorkflowStep(id='s2', name='Step 2', description='Second', order=2),
    ]
    wf = engine.create_workflow('test', 'desc', steps)
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    result = executor.execute(wf, ctx)
    assert result is not None
    assert result.success is True


def test_failure_handling():
    """Test workflow failure handling."""
    teardown_function()
    engine = WorkflowEngine()

    # Create workflow with no steps - will fail validation
    wf = Workflow(id='wf1', name='Test', description='No steps')
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    executor = WorkflowExecutor(engine)
    result = executor.execute(wf, ctx)
    assert result is not None
    assert result.success is False
    assert result.state == WorkflowState.FAILED


def test_execution_status():
    """Test execution status reporting."""
    setup_module()
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine)
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    executor.execute(wf, ctx)
    status = executor.get_execution_status(wf.id)
    assert status is not None
    assert 'steps' in status
    assert 'state' in status


def test_status_nonexistent():
    """Test status for nonexistent workflow."""
    teardown_function()
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine)
    status = executor.get_execution_status('nonexistent')
    assert status is None


# ActionDefinition Tests
def test_action_definition():
    """Test ActionDefinition model."""
    action = ActionDefinition(
        name='test',
        description='Test action',
        requires_approval=True,
        risk_level='high'
    )
    assert action.requires_approval is True
    assert action.to_dict()['name'] == 'test'


def test_workflow_action_enum():
    """Test WorkflowAction enum values."""
    assert WorkflowAction.ANALYZE_PROJECT.value == 'analyze_project'
    assert WorkflowAction.RUN_REVIEW.value == 'run_review'
    assert WorkflowAction.CREATE_PLAN.value == 'create_plan'
    assert WorkflowAction.GENERATE_PATCH.value == 'generate_patch'
    assert WorkflowAction.VALIDATE_PATCH.value == 'validate_patch'
    assert WorkflowAction.APPLY_PATCH.value == 'apply_patch'
    assert WorkflowAction.RUN_TESTS.value == 'run_tests'
    assert WorkflowAction.STORE_KNOWLEDGE.value == 'store_knowledge'