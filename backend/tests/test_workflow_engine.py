"""Tests for Workflow Engine."""
import pytest
from app.workflows import WorkflowEngine, WorkflowState, WorkflowStep, Workflow, WorkflowContext, WorkflowResult


def test_workflow_state_enum():
    """Test WorkflowState enum values."""
    assert WorkflowState.PENDING.value == 'pending'
    assert WorkflowState.RUNNING.value == 'running'
    assert WorkflowState.WAITING_APPROVAL.value == 'waiting_approval'
    assert WorkflowState.COMPLETED.value == 'completed'
    assert WorkflowState.FAILED.value == 'failed'
    assert WorkflowState.ROLLED_BACK.value == 'rolled_back'


def test_workflow_step_creation():
    """Test WorkflowStep default values."""
    step = WorkflowStep(
        id='s1',
        name='Test Step',
        description='A test step',
        order=1,
    )
    assert step.status == WorkflowState.PENDING
    assert step.result is None
    assert step.error is None


def test_workflow_step_to_dict():
    """Test WorkflowStep serialization."""
    step = WorkflowStep(
        id='s1',
        name='Test Step',
        description='A test step',
        order=1,
        status=WorkflowState.RUNNING,
        result='success',
    )
    d = step.to_dict()
    assert d['id'] == 's1'
    assert d['status'] == 'running'
    assert d['result'] == 'success'


def test_workflow_creation():
    """Test Workflow default values."""
    wf = Workflow(
        id='wf1',
        name='Test Workflow',
        description='A test workflow',
    )
    assert wf.state == WorkflowState.PENDING
    assert wf.steps == []
    assert wf.current_step is None
    assert wf.created_at is not None
    assert wf.completed_at is None


def test_workflow_to_dict():
    """Test Workflow serialization."""
    step = WorkflowStep(id='s1', name='Step 1', description='First', order=1)
    wf = Workflow(
        id='wf1',
        name='Test Workflow',
        description='A test',
        steps=[step],
        state=WorkflowState.RUNNING,
        current_step=0,
    )
    d = wf.to_dict()
    assert d['id'] == 'wf1'
    assert d['state'] == 'running'
    assert len(d['steps']) == 1


def test_workflow_context_creation():
    """Test WorkflowContext default values."""
    ctx = WorkflowContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='Build feature X',
    )
    assert ctx.metadata == {}


def test_workflow_context_to_dict():
    """Test WorkflowContext serialization."""
    ctx = WorkflowContext(
        workflow_id='wf1',
        project_path='/project',
        user_request='Build feature',
        metadata={'key': 'value'},
    )
    d = ctx.to_dict()
    assert d['workflow_id'] == 'wf1'
    assert d['metadata'] == {'key': 'value'}


def test_workflow_result_creation():
    """Test WorkflowResult default values."""
    result = WorkflowResult(
        success=True,
        workflow_id='wf1',
        state=WorkflowState.COMPLETED,
        summary='All done',
    )
    assert result.errors == []


def test_workflow_result_to_dict():
    """Test WorkflowResult serialization."""
    result = WorkflowResult(
        success=False,
        workflow_id='wf1',
        state=WorkflowState.FAILED,
        summary='Failed',
        errors=['error1', 'error2'],
    )
    d = result.to_dict()
    assert d['success'] is False
    assert d['errors'] == ['error1', 'error2']


def test_engine_create_workflow():
    """Test workflow creation via engine."""
    engine = WorkflowEngine()
    steps = [
        WorkflowStep(id='s1', name='Step 1', description='First', order=1),
        WorkflowStep(id='s2', name='Step 2', description='Second', order=2),
    ]
    wf = engine.create_workflow(
        name='test',
        description='Test workflow',
        steps=steps,
    )

    assert wf.name == 'test'
    assert len(wf.steps) == 2
    assert wf.state == WorkflowState.PENDING
    assert wf.id.startswith('test_')


def test_engine_start_workflow():
    """Test workflow start transitions state."""
    engine = WorkflowEngine()
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)

    started = engine.start_workflow(wf.id)
    assert started is not None
    assert started.state == WorkflowState.RUNNING
    assert started.current_step == 0


def test_engine_start_nonexistent_workflow():
    """Test starting nonexistent workflow returns None."""
    engine = WorkflowEngine()
    result = engine.start_workflow('nonexistent')
    assert result is None


def test_step_ordering():
    """Test steps are properly ordered."""
    engine = WorkflowEngine()
    steps = [
        WorkflowStep(id='s3', name='Step 3', description='Third', order=3),
        WorkflowStep(id='s1', name='Step 1', description='First', order=1),
        WorkflowStep(id='s2', name='Step 2', description='Second', order=2),
    ]
    wf = engine.create_workflow('test', 'desc', steps)

    # Verify step order is preserved in list
    assert wf.steps[0].order == 3
    assert wf.steps[1].order == 1
    assert wf.steps[2].order == 2


def test_update_step_status():
    """Test updating step status."""
    engine = WorkflowEngine()
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    engine.start_workflow(wf.id)

    updated = engine.update_step(wf.id, 1, WorkflowState.COMPLETED, result='done')
    assert updated is not None
    assert updated.status == WorkflowState.COMPLETED
    assert updated.result == 'done'


def test_complete_workflow():
    """Test completing a workflow."""
    engine = WorkflowEngine()
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    engine.start_workflow(wf.id)

    completed = engine.complete_workflow(wf.id)
    assert completed is not None
    assert completed.state == WorkflowState.COMPLETED
    assert completed.completed_at is not None


def test_fail_workflow():
    """Test failing a workflow."""
    engine = WorkflowEngine()
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    engine.start_workflow(wf.id)

    failed = engine.fail_workflow(wf.id, error='Something went wrong')
    assert failed is not None
    assert failed.state == WorkflowState.FAILED
    assert failed.completed_at is not None


def test_rollback_workflow():
    """Test rolling back a workflow."""
    engine = WorkflowEngine()
    steps = [
        WorkflowStep(id='s1', name='Step 1', description='First', order=1),
        WorkflowStep(id='s2', name='Step 2', description='Second', order=2),
    ]
    wf = engine.create_workflow('test', 'desc', steps)
    engine.start_workflow(wf.id)

    rolled = engine.rollback_workflow(wf.id)
    assert rolled is not None
    assert rolled.state == WorkflowState.ROLLED_BACK
    for step in rolled.steps:
        assert step.status == WorkflowState.ROLLED_BACK


def test_get_status():
    """Test getting workflow status."""
    engine = WorkflowEngine()
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)

    status = engine.get_status(wf.id)
    assert status is not None
    assert status['workflow_id'] == wf.id
    assert status['state'] == 'pending'
    assert status['total_steps'] == 1


def test_get_status_nonexistent():
    """Test getting status for nonexistent workflow."""
    engine = WorkflowEngine()
    status = engine.get_status('nonexistent')
    assert status is None


def test_workflow_transitions():
    """Test full workflow state transitions."""
    engine = WorkflowEngine()
    steps = [
        WorkflowStep(id='s1', name='Step 1', description='First', order=1),
        WorkflowStep(id='s2', name='Step 2', description='Second', order=2),
    ]
    wf = engine.create_workflow('test', 'desc', steps)

    # PENDING -> RUNNING
    engine.start_workflow(wf.id)
    assert wf.state == WorkflowState.RUNNING

    # Step 1 completed, move to step 2
    engine.update_step(wf.id, 1, WorkflowState.COMPLETED)
    assert wf.state == WorkflowState.RUNNING
    assert wf.current_step == 2

    # Step 2 completed, workflow done
    engine.update_step(wf.id, 2, WorkflowState.COMPLETED)
    assert wf.state == WorkflowState.COMPLETED


def test_serialization_roundtrip():
    """Test to_dict produces clean serializable data."""
    engine = WorkflowEngine()
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)

    # Should be JSON-serializable
    import json
    d = wf.to_dict()
    json_str = json.dumps(d)
    assert json_str is not None

    # Steps should be serializable too
    for step in wf.steps:
        step_json = json.dumps(step.to_dict())
        assert step_json is not None


def test_multiple_workflows():
    """Test engine can handle multiple workflows."""
    engine = WorkflowEngine()

    wf1 = engine.create_workflow('wf1', 'desc1', [WorkflowStep(id='s1', name='Step', description='d', order=1)])
    wf2 = engine.create_workflow('wf2', 'desc2', [WorkflowStep(id='s1', name='Step', description='d', order=1)])

    assert wf1.id != wf2.id
    assert len(engine._workflows) == 2

    engine.complete_workflow(wf1.id)
    engine.fail_workflow(wf2.id)

    assert engine.get_status(wf1.id)['state'] == 'completed'
    assert engine.get_status(wf2.id)['state'] == 'failed'