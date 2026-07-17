"""Tests for Workflow Persistence (Storage, History, Events)."""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.workflows import (
    WorkflowEventType, WorkflowEvent,
    WorkflowHistory, WorkflowStorage, WorkflowStorageStatistics,
    WorkflowEngine, WorkflowState, WorkflowStep, Workflow, WorkflowContext,
    WorkflowExecutor, WorkflowValidator, clear_registry,
    ActionDefinition, register_action_direct, get_action
)


# ==============================================================================
# Event Tests
# ==============================================================================

def test_event_type_enum():
    """Test all event types exist."""
    assert WorkflowEventType.WORKFLOW_CREATED.value == 'workflow_created'
    assert WorkflowEventType.WORKFLOW_STARTED.value == 'workflow_started'
    assert WorkflowEventType.WORKFLOW_PAUSED.value == 'workflow_paused'
    assert WorkflowEventType.WORKFLOW_RESUMED.value == 'workflow_resumed'
    assert WorkflowEventType.STEP_STARTED.value == 'step_started'
    assert WorkflowEventType.STEP_COMPLETED.value == 'step_completed'
    assert WorkflowEventType.STEP_FAILED.value == 'step_failed'
    assert WorkflowEventType.APPROVAL_REQUIRED.value == 'approval_required'
    assert WorkflowEventType.APPROVAL_GRANTED.value == 'approval_granted'
    assert WorkflowEventType.APPROVAL_DENIED.value == 'approval_denied'
    assert WorkflowEventType.WORKFLOW_COMPLETED.value == 'workflow_completed'
    assert WorkflowEventType.WORKFLOW_FAILED.value == 'workflow_failed'
    assert WorkflowEventType.WORKFLOW_ROLLED_BACK.value == 'workflow_rolled_back'


def test_event_uuid_creation():
    """Test event has UUID id."""
    event = WorkflowEvent(
        id=uuid4(),
        workflow_id='wf1',
        event_type=WorkflowEventType.WORKFLOW_CREATED,
        timestamp=datetime.now(timezone.utc),
        message='Test event',
    )
    assert event.id is not None
    assert isinstance(event.id, type(uuid4()))


def test_event_timezone_datetime():
    """Test event has timezone-aware datetime."""
    event = WorkflowEvent(
        id=uuid4(),
        workflow_id='wf1',
        event_type=WorkflowEventType.WORKFLOW_CREATED,
        timestamp=datetime.now(timezone.utc),
    )
    assert event.timestamp.tzinfo is not None


def test_event_metadata():
    """Test event with metadata."""
    event = WorkflowEvent(
        id=uuid4(),
        workflow_id='wf1',
        event_type=WorkflowEventType.STEP_COMPLETED,
        timestamp=datetime.now(timezone.utc),
        step='step1',
        metadata={'key': 'value', 'count': 5},
    )
    assert event.metadata is not None
    assert event.metadata['key'] == 'value'
    assert event.metadata['count'] == 5


def test_event_serialization():
    """Test event to_dict serialization."""
    event = WorkflowEvent.create(
        workflow_id='wf1',
        event_type=WorkflowEventType.STEP_STARTED,
        step='step1',
        message='Starting step',
        metadata={'action': 'test'},
    )
    d = event.to_dict()
    assert d['id'] is not None
    assert d['workflow_id'] == 'wf1'
    assert d['event_type'] == 'step_started'
    assert d['step'] == 'step1'
    assert d['message'] == 'Starting step'
    assert d['metadata'] == {'action': 'test'}


def test_event_factory():
    """Test WorkflowEvent.create factory method."""
    event = WorkflowEvent.create(
        workflow_id='wf1',
        event_type=WorkflowEventType.WORKFLOW_STARTED,
        message='Started',
    )
    assert event.id is not None
    assert event.workflow_id == 'wf1'
    assert event.event_type == WorkflowEventType.WORKFLOW_STARTED
    assert event.timestamp.tzinfo is not None


# ==============================================================================
# History Tests
# ==============================================================================

def test_append_events():
    """Test appending events to history."""
    history = WorkflowHistory()
    event1 = WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_CREATED, message='Created')
    event2 = WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_STARTED, message='Started')

    history.append_event(event1)
    history.append_event(event2)

    assert len(history.list_events('wf1')) == 2


def test_event_ordering():
    """Test events are ordered by timestamp."""
    history = WorkflowHistory()
    event1 = WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_CREATED, message='Created')
    event2 = WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_STARTED, message='Started')

    # Add in reverse order
    history.append_event(event2)
    history.append_event(event1)

    events = history.list_events('wf1')
    assert events[0].event_type == WorkflowEventType.WORKFLOW_CREATED
    assert events[1].event_type == WorkflowEventType.WORKFLOW_STARTED


def test_get_events_filtered():
    """Test filtering events by type."""
    history = WorkflowHistory()
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_CREATED))
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.STEP_STARTED, step='step1'))
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.STEP_COMPLETED, step='step1'))

    started_events = history.get_events('wf1', event_type=WorkflowEventType.STEP_STARTED)
    assert len(started_events) == 1
    assert started_events[0].step == 'step1'


def test_get_events_by_step():
    """Test filtering events by step."""
    history = WorkflowHistory()
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.STEP_STARTED, step='step1'))
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.STEP_COMPLETED, step='step1'))
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.STEP_STARTED, step='step2'))

    step1_events = history.get_events('wf1', step='step1')
    assert len(step1_events) == 2
    assert all(e.step == 'step1' for e in step1_events)


def test_workflow_duration():
    """Test workflow duration calculation."""
    history = WorkflowHistory()
    history.append_event(WorkflowEvent.create(
        'wf1', WorkflowEventType.WORKFLOW_CREATED,
        timestamp=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    ))
    history.append_event(WorkflowEvent.create(
        'wf1', WorkflowEventType.WORKFLOW_STARTED,
        timestamp=datetime(2024, 1, 1, 10, 0, 1, tzinfo=timezone.utc)
    ))
    history.append_event(WorkflowEvent.create(
        'wf1', WorkflowEventType.WORKFLOW_COMPLETED,
        timestamp=datetime(2024, 1, 1, 10, 0, 5, tzinfo=timezone.utc)
    ))

    duration = history.workflow_duration('wf1')
    assert duration == 4.0  # 5 seconds - 1 second


def test_workflow_duration_no_start():
    """Test duration when no start event exists."""
    history = WorkflowHistory()
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_CREATED))

    duration = history.workflow_duration('wf1')
    assert duration is None


def test_history_summary():
    """Test history summary generation."""
    history = WorkflowHistory()
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_CREATED, message='Created'))
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_STARTED, message='Started'))
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.STEP_COMPLETED, step='step1', message='Done'))

    summary = history.summary('wf1')
    assert summary['workflow_id'] == 'wf1'
    assert summary['total_events'] == 3
    assert summary['event_counts']['workflow_created'] == 1
    assert summary['event_counts']['workflow_started'] == 1
    assert summary['event_counts']['step_completed'] == 1


def test_history_summary_empty():
    """Test summary for non-existent workflow."""
    history = WorkflowHistory()
    summary = history.summary('nonexistent')
    assert summary['total_events'] == 0


def test_history_clear():
    """Test clearing history."""
    history = WorkflowHistory()
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_CREATED))
    history.append_event(WorkflowEvent.create('wf2', WorkflowEventType.WORKFLOW_STARTED))

    history.clear()
    assert len(history.list_events('wf1')) == 0
    assert len(history.list_events('wf2')) == 0


def test_history_serialization():
    """Test history to_dict serialization."""
    history = WorkflowHistory()
    history.append_event(WorkflowEvent.create('wf1', WorkflowEventType.WORKFLOW_CREATED))

    d = history.to_dict('wf1')
    assert 'wf1' in d
    assert len(d['wf1']) == 1
    assert d['wf1'][0]['event_type'] == 'workflow_created'


# ==============================================================================
# Storage Tests
# ==============================================================================

def test_save_workflow():
    """Test saving workflow to storage."""
    storage = WorkflowStorage()
    wf = Workflow(id='wf1', name='Test', description='Test workflow')

    storage.save_workflow(wf)
    assert storage.workflow_exists('wf1')


def test_update_workflow():
    """Test updating workflow in storage."""
    storage = WorkflowStorage()
    wf = Workflow(id='wf1', name='Test', description='Original')
    storage.save_workflow(wf)

    wf.name = 'Updated'
    result = storage.update_workflow(wf)
    assert result is True
    assert storage.get_workflow('wf1').name == 'Updated'


def test_update_nonexistent_workflow():
    """Test updating non-existent workflow returns False."""
    storage = WorkflowStorage()
    wf = Workflow(id='wf1', name='Test', description='Test')

    result = storage.update_workflow(wf)
    assert result is False


def test_delete_workflow():
    """Test deleting workflow from storage."""
    storage = WorkflowStorage()
    wf = Workflow(id='wf1', name='Test', description='Test')
    storage.save_workflow(wf)

    result = storage.delete_workflow('wf1')
    assert result is True
    assert not storage.workflow_exists('wf1')


def test_delete_nonexistent_workflow():
    """Test deleting non-existent workflow returns False."""
    storage = WorkflowStorage()
    result = storage.delete_workflow('nonexistent')
    assert result is False


def test_list_ordering():
    """Test workflows are listed in deterministic order."""
    storage = WorkflowStorage()
    wf_z = Workflow(id='zebra', name='Z', description='Last')
    wf_a = Workflow(id='alpha', name='A', description='First')
    wf_m = Workflow(id='middle', name='M', description='Middle')

    storage.save_workflow(wf_z)
    storage.save_workflow(wf_a)
    storage.save_workflow(wf_m)

    workflows = storage.list_workflows()
    assert [wf.id for wf in workflows] == ['alpha', 'middle', 'zebra']


def test_storage_clear():
    """Test clearing storage."""
    storage = WorkflowStorage()
    storage.save_workflow(Workflow(id='wf1', name='Test', description='Test'))
    storage.save_workflow(Workflow(id='wf2', name='Test', description='Test'))

    storage.clear()
    assert len(storage.list_workflows()) == 0


# ==============================================================================
# Statistics Tests
# ==============================================================================

def test_statistics_counts():
    """Test workflow statistics counts."""
    statistics = WorkflowStorageStatistics()
    assert statistics.total_workflows == 0
    assert statistics.completed == 0
    assert statistics.failed == 0
    assert statistics.running == 0
    assert statistics.pending == 0
    assert statistics.rolled_back == 0


def test_statistics_status_breakdown():
    """Test statistics from workflows."""
    storage = WorkflowStorage()
    storage.save_workflow(Workflow(id='wf1', name='Test', description='Test', state=WorkflowState.COMPLETED))
    storage.save_workflow(Workflow(id='wf2', name='Test', description='Test', state=WorkflowState.FAILED))
    storage.save_workflow(Workflow(id='wf3', name='Test', description='Test', state=WorkflowState.RUNNING))
    storage.save_workflow(Workflow(id='wf4', name='Test', description='Test', state=WorkflowState.PENDING))
    storage.save_workflow(Workflow(id='wf5', name='Test', description='Test', state=WorkflowState.ROLLED_BACK))

    stats = storage.statistics()
    assert stats.total_workflows == 5
    assert stats.completed == 1
    assert stats.failed == 1
    assert stats.running == 1
    assert stats.pending == 1
    assert stats.rolled_back == 1


def test_statistics_to_dict():
    """Test statistics serialization."""
    stats = WorkflowStorageStatistics(total_workflows=5, completed=2, failed=1)
    d = stats.to_dict()
    assert d['total_workflows'] == 5
    assert d['completed'] == 2
    assert d['failed'] == 1


# ==============================================================================
# Executor Integration Tests
# ==============================================================================

def setup_module():
    clear_registry()


def teardown_function():
    clear_registry()


def test_events_emitted_on_execution():
    """Test events are emitted during workflow execution."""
    history = WorkflowHistory()
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine, history=history)
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    executor.execute(wf, ctx)

    events = history.list_events(wf.id)
    event_types = [e.event_type for e in events]

    assert WorkflowEventType.WORKFLOW_CREATED in event_types
    assert WorkflowEventType.WORKFLOW_STARTED in event_types
    assert WorkflowEventType.STEP_STARTED in event_types
    assert WorkflowEventType.STEP_COMPLETED in event_types
    assert WorkflowEventType.WORKFLOW_COMPLETED in event_types


def test_events_emitted_on_failure():
    """Test events are emitted on workflow failure."""
    history = WorkflowHistory()
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine, history=history)
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    # Register an action that requires approval
    from app.workflows import ActionDefinition, register_action_direct
    register_action_direct('apply_patch', ActionDefinition(
        name='apply_patch',
        description='Apply patch',
        requires_approval=True,
        risk_level='high'
    ))

    # Simulate step that requires approval
    wf.steps[0].metadata = {'action': get_action('apply_patch')}
    executor.execute(wf, ctx)

    events = history.list_events(wf.id)
    event_types = [e.event_type for e in events]

    # Should have created, started, step started, and approval required events
    assert WorkflowEventType.WORKFLOW_CREATED in event_types
    assert WorkflowEventType.APPROVAL_REQUIRED in event_types


def test_history_updated_with_events():
    """Test history is updated with workflow events."""
    history = WorkflowHistory()
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine, history=history)
    steps = [
        WorkflowStep(id='s1', name='Step 1', description='First', order=1),
        WorkflowStep(id='s2', name='Step 2', description='Second', order=2),
    ]
    wf = engine.create_workflow('test', 'desc', steps)
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    executor.execute(wf, ctx)

    # Verify history has correct counts
    step_events = history.get_events(wf.id, event_type=WorkflowEventType.STEP_COMPLETED)
    assert len(step_events) == 2

    # Verify summary works
    summary = history.summary(wf.id)
    assert summary['total_events'] == 7  # created, started, 2 step_started, 2 step_completed, completed


def test_executor_without_history():
    """Test executor works without history (backward compatible)."""
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine)  # No history provided
    steps = [WorkflowStep(id='s1', name='Step 1', description='First', order=1)]
    wf = engine.create_workflow('test', 'desc', steps)
    ctx = WorkflowContext(workflow_id=wf.id, project_path='/project', user_request='Test')

    # Should not raise any errors
    result = executor.execute(wf, ctx)
    assert result is not None
    assert result.success is True