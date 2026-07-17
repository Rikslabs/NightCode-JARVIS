"""Workflow state definitions."""
from enum import Enum


class WorkflowState(Enum):
    """Enumeration of possible workflow states."""
    PENDING = 'pending'
    RUNNING = 'running'
    WAITING_APPROVAL = 'waiting_approval'
    COMPLETED = 'completed'
    FAILED = 'failed'
    ROLLED_BACK = 'rolled_back'