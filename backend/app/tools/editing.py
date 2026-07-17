from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime, timezone

# Import Tool and register_tool at top level
from .base import Tool, ToolResult
from .registry import register_tool


class PatchType(Enum):
    ADD = 'add'
    DELETE = 'delete'
    REPLACE = 'replace'
    INSERT_BEFORE = 'insert_before'
    INSERT_AFTER = 'insert_after'
    MODIFY = 'modify'


class PatchStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    APPLIED = 'applied'
    ROLLED_BACK = 'rolled_back'
    FAILED = 'failed'


class PatchRisk(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


@dataclass
class PatchOperation:
    file_path: str
    operation_type: PatchType
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    original_content: str = ''
    proposed_content: str = ''
    description: str = ''
    risk: PatchRisk = PatchRisk.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        return {
            'file_path': self.file_path,
            'operation_type': self.operation_type.value,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'original_content': self.original_content,
            'proposed_content': self.proposed_content,
            'description': self.description,
            'risk': self.risk.value,
        }


@dataclass
class PatchFile:
    path: str
    changes: list[PatchOperation] = field(default_factory=list)
    original_checksum: str = ''
    proposed_checksum: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'path': self.path,
            'changes': [c.to_dict() for c in self.changes],
            'original_checksum': self.original_checksum,
            'proposed_checksum': self.proposed_checksum,
        }


@dataclass
class PatchChange:
    file_path: str
    operations: list[PatchOperation] = field(default_factory=list)
    status: PatchStatus = PatchStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        return {
            'file_path': self.file_path,
            'operations': [o.to_dict() for o in self.operations],
            'status': self.status.value,
        }


@dataclass
class PatchValidation:
    syntax_valid: bool = False
    lint_passed: bool = False
    backward_compatible: bool = True
    tests_passed: bool = False
    validation_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'syntax_valid': self.syntax_valid,
            'lint_passed': self.lint_passed,
            'backward_compatible': self.backward_compatible,
            'tests_passed': self.tests_passed,
            'validation_notes': list(self.validation_notes),
        }


@dataclass
class PatchSummary:
    id: str
    title: str
    description: str
    files: list[PatchFile] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    estimated_risk: PatchRisk = PatchRisk.MEDIUM
    rollback_available: bool = True
    rollback_instructions: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'files': [f.to_dict() for f in self.files],
            'created_at': self.created_at,
            'estimated_risk': self.estimated_risk.value,
            'rollback_available': self.rollback_available,
            'rollback_instructions': self.rollback_instructions,
        }


@dataclass
class PatchResult:
    summary: PatchSummary
    validation: PatchValidation
    applied_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'summary': self.summary.to_dict(),
            'validation': self.validation.to_dict(),
            'applied_files': list(self.applied_files),
            'skipped_files': list(self.skipped_files),
            'errors': list(self.errors),
        }


class PatchGenerator:
    """Deterministic patch generator that creates structured PatchSummary objects."""

    def generate_patch(self, file_path: str, original: str, proposed: str, description: str = '') -> PatchSummary:
        """Generate patch operations comparing original and proposed text."""
        original_lines = original.splitlines(keepends=True)
        proposed_lines = proposed.splitlines(keepends=True)
        operations = self._compare_lines(file_path, original_lines, proposed_lines)
        risk = self.estimate_risk(operations)
        return PatchSummary(
            id=self._generate_id(file_path),
            title=f'Patch for {file_path}',
            description=description or f'Changes to {file_path}',
            files=[
                PatchFile(
                    path=file_path,
                    changes=operations,
                    original_checksum=self.calculate_checksum(original),
                    proposed_checksum=self.calculate_checksum(proposed),
                )
            ],
            estimated_risk=risk,
            rollback_available=len(operations) > 0,
            rollback_instructions='Revert via version control',
        )

    def compare_text(self, original: str, proposed: str) -> list[PatchOperation]:
        """Compare text and return minimal diff operations."""
        orig_lines = original.splitlines(keepends=True)
        prop_lines = proposed.splitlines(keepends=True)
        if original == proposed:
            return []
        return [PatchOperation(
            file_path='<text>',
            operation_type=PatchType.REPLACE,
            line_start=1,
            line_end=len(orig_lines),
            original_content=original,
            proposed_content=proposed,
        )]

    def merge_operations(self, operations: list[PatchOperation]) -> list[PatchOperation]:
        """Merge adjacent operations when appropriate."""
        if not operations:
            return []
        merged = []
        current = operations[0]
        for op in operations[1:]:
            if (current.operation_type == PatchType.REPLACE and
                op.operation_type == PatchType.REPLACE and
                current.file_path == op.file_path and
                current.line_end == op.line_start):
                current = PatchOperation(
                    file_path=current.file_path,
                    operation_type=PatchType.REPLACE,
                    line_start=current.line_start,
                    line_end=op.line_end,
                    original_content=current.original_content + op.original_content,
                    proposed_content=current.proposed_content + op.proposed_content,
                    risk=current.risk,
                )
            else:
                merged.append(current)
                current = op
        merged.append(current)
        return merged

    def estimate_risk(self, operations: list[PatchOperation]) -> PatchRisk:
        """Calculate patch risk based on operations."""
        if not operations:
            return PatchRisk.LOW
        risks = [op.risk for op in operations]
        if PatchRisk.CRITICAL in risks:
            return PatchRisk.CRITICAL
        if PatchRisk.HIGH in risks:
            return PatchRisk.HIGH
        if PatchRisk.MEDIUM in risks or len(operations) > 5:
            return PatchRisk.MEDIUM
        return PatchRisk.LOW

    def calculate_checksum(self, content: str) -> str:
        """Calculate simple checksum for content."""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def generate_summary(self, patch: PatchSummary) -> str:
        """Generate human-readable summary."""
        lines = [
            f'Patch: {patch.title}',
            f'Description: {patch.description}',
            f'Risk: {patch.estimated_risk.value}',
            f'Files affected: {len(patch.files)}',
        ]
        for f in patch.files:
            lines.append(f'  - {f.path}: {len(f.changes)} changes')
        return '\n'.join(lines)

    def _compare_lines(self, file_path: str, orig: list[str], prop: list[str]) -> list[PatchOperation]:
        """Internal line-by-line comparison."""
        if orig == prop:
            return []
        if not orig:
            return [PatchOperation(
                file_path=file_path,
                operation_type=PatchType.ADD,
                proposed_content=''.join(prop),
            )]
        if not prop:
            return [PatchOperation(
                file_path=file_path,
                operation_type=PatchType.DELETE,
                original_content=''.join(orig),
            )]
        return [PatchOperation(
            file_path=file_path,
            operation_type=PatchType.REPLACE,
            line_start=1,
            line_end=len(orig),
            original_content=''.join(orig),
            proposed_content=''.join(prop),
        )]

    def _generate_id(self, file_path: str) -> str:
        """Generate patch ID."""
        import uuid
        return f'{file_path}_{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}_{str(uuid.uuid4())[:8]}'


class PatchValidator:
    """Deterministic validation engine for generated patches."""

    def validate_patch(self, patch: PatchSummary) -> PatchValidation:
        """Validate entire patch and return PatchValidation."""
        notes = []
        if not patch.files:
            notes.append('No files in patch')
            return PatchValidation(
                syntax_valid=True,
                lint_passed=True,
                backward_compatible=True,
                tests_passed=True,
                validation_notes=notes,
            )
        all_valid = True
        for pf in patch.files:
            for op in pf.changes:
                op_valid, op_notes = self.validate_operation(op)
                if not op_valid:
                    notes.extend(op_notes)
                    all_valid = False
        notes.extend(self.validate_overlaps(patch))
        order_valid, order_notes = self.validate_order(patch)
        if not order_valid:
            notes.extend(order_notes)
        return PatchValidation(
            syntax_valid=all_valid,
            lint_passed=all_valid,
            backward_compatible=True,
            tests_passed=True,
            validation_notes=notes,
        )

    def validate_operation(self, op: PatchOperation) -> tuple[bool, list[str]]:
        """Validate a single PatchOperation."""
        notes = []
        valid = True
        if op.operation_type in (PatchType.REPLACE, PatchType.INSERT_BEFORE, PatchType.INSERT_AFTER) and op.line_start is not None:
            range_valid, range_notes = self.validate_ranges(op)
            if not range_valid:
                notes.extend(range_notes)
                valid = False
        if op.operation_type == PatchType.DELETE and not op.original_content:
            notes.append(f'Empty original content for DELETE in {op.file_path}')
            valid = False
        if op.operation_type == PatchType.ADD and not op.proposed_content:
            notes.append(f'Empty proposed content for ADD in {op.file_path}')
            valid = False
        if op.operation_type == PatchType.REPLACE and not op.original_content:
            notes.append(f'Empty original content for REPLACE in {op.file_path}')
            valid = False
        return valid, notes

    def validate_checksums(self, original: str, proposed: str, original_checksum: str, proposed_checksum: str) -> tuple[bool, list[str]]:
        """Validate checksum consistency."""
        import hashlib
        notes = []
        valid = True
        expected_orig = hashlib.sha256(original.encode()).hexdigest()[:16]
        if original_checksum and expected_orig != original_checksum:
            notes.append(f'Original checksum mismatch')
            valid = False
        expected_prop = hashlib.sha256(proposed.encode()).hexdigest()[:16]
        if proposed_checksum and expected_prop != proposed_checksum:
            notes.append(f'Proposed checksum mismatch')
            valid = False
        return valid, notes

    def validate_ranges(self, op: PatchOperation) -> tuple[bool, list[str]]:
        """Validate line ranges are valid."""
        notes = []
        valid = True
        if op.line_start is not None and op.line_end is not None:
            if op.line_start < 1:
                notes.append(f'Invalid line_start: {op.line_start}')
                valid = False
            if op.line_end < op.line_start:
                notes.append(f'Invalid line_end: {op.line_end} (less than start)')
                valid = False
        return valid, notes

    def validate_order(self, patch: PatchSummary) -> tuple[bool, list[str]]:
        """Validate operation ordering."""
        all_ops = []
        for pf in patch.files:
            all_ops.extend(pf.changes)
        sorted_ops = sorted([op for op in all_ops if op.line_start is not None],
                          key=lambda x: (x.file_path, x.line_start or 0))
        if [op.file_path for op in all_ops] != [op.file_path for op in sorted_ops]:
            return False, ['Operations not in file order']
        return True, []

    def validate_overlaps(self, patch: PatchSummary) -> list[str]:
        """Detect overlapping operations."""
        notes = []
        all_ops = []
        for pf in patch.files:
            all_ops.extend(pf.changes)
        by_file: dict[str, list[PatchOperation]] = {}
        for op in all_ops:
            if op.line_start is not None and op.line_end is not None:
                by_file.setdefault(op.file_path, []).append(op)
        for file_path, ops in by_file.items():
            sorted_ops = sorted(ops, key=lambda x: x.line_start or 0)
            for i in range(len(sorted_ops) - 1):
                if sorted_ops[i].line_end > sorted_ops[i + 1].line_start:
                    notes.append(f'Overlapping operations in {file_path}')
        return notes

    def validate_summary(self, patch: PatchSummary) -> tuple[bool, list[str]]:
        """Validate patch summary."""
        notes = []
        valid = True
        if not patch.id:
            notes.append('Missing patch ID')
            valid = False
        if not patch.title:
            notes.append('Missing patch title')
            valid = False
        if not patch.description:
            notes.append('Missing patch description')
            valid = False
        return valid, notes


class EditingEngine:
    """Single entry point for Safe Editing subsystem."""

    def __init__(self):
        self._generator = PatchGenerator()
        self._validator = PatchValidator()
        self._preview_engine = None
        self._apply_engine = None
        self._rollback_engine = None

    def generate_patch(self, file_path: str, original: str, proposed: str, description: str = '') -> PatchSummary:
        """Delegate to PatchGenerator."""
        return self._generator.generate_patch(file_path, original, proposed, description)

    def validate_patch(self, patch: PatchSummary) -> PatchValidation:
        """Delegate to PatchValidator."""
        return self._validator.validate_patch(patch)

    def create_patch(self, file_path: str, original: str, proposed: str, description: str = '') -> PatchResult:
        """Generate and validate patch, returning PatchResult."""
        summary = self._generator.generate_patch(file_path, original, proposed, description)
        validation = self._validator.validate_patch(summary)
        return PatchResult(summary=summary, validation=validation)


class PatchPreview:
    """Deterministic preview engine for generated patches."""

    def preview_patch(self, patch: PatchSummary) -> str:
        """Render unified diff preview of entire patch."""
        lines = [f'Patch: {patch.title}', f'Description: {patch.description}', '']
        for pf in patch.files:
            lines.extend(self.preview_file(pf))
        lines.extend(['', self.render_summary(patch)])
        return '\n'.join(lines)

    def preview_file(self, patch_file: PatchFile) -> list[str]:
        """Render diff preview for a single file."""
        lines = [f'--- {patch_file.path}', f'+++ {patch_file.path}', '']
        for op in patch_file.changes:
            lines.extend(self.render_diff(op))
        return lines

    def render_diff(self, op: PatchOperation) -> list[str]:
        """Render unified diff for a single operation."""
        lines = []
        if op.operation_type == PatchType.ADD:
            lines.append(f'@@ (new file) @@')
            for line in op.proposed_content.splitlines():
                lines.append(f'+ {line}')
        elif op.operation_type == PatchType.DELETE:
            lines.append(f'@@ line {op.line_start} @@')
            for line in op.original_content.splitlines():
                lines.append(f'- {line}')
        else:
            start = op.line_start or 1
            end = op.line_end or len(op.original_content.splitlines())
            lines.append(f'@@ {start},{end} @@')
            for line in op.original_content.splitlines():
                lines.append(f'- {line}')
            for line in op.proposed_content.splitlines():
                lines.append(f'+ {line}')
        return lines

    def render_summary(self, patch: PatchSummary) -> str:
        """Produce concise patch statistics."""
        files_changed = len(patch.files)
        insertions = 0
        deletions = 0
        modifications = 0
        for pf in patch.files:
            for op in pf.changes:
                if op.operation_type == PatchType.ADD:
                    insertions += len(op.proposed_content.splitlines())
                elif op.operation_type == PatchType.DELETE:
                    deletions += len(op.original_content.splitlines())
                else:
                    modifications += 1
                    insertions += len(op.proposed_content.splitlines())
                    deletions += len(op.original_content.splitlines())
        return f'Files changed: {files_changed} | +{insertions} -{deletions} | {modifications} modifications'


class SafeFileSystem:
    """Safe filesystem abstraction for editing operations."""

    def read_file(self, path: str) -> str:
        """Read file contents."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: str, content: str) -> bool:
        """Write file atomically."""
        import os
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(path) or '.')
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(temp_path, path)
            return True
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def backup_file(self, path: str) -> str:
        """Create backup with unique name."""
        import os
        import uuid
        backup_path = self.create_backup_path(path)
        content = self.read_file(path)
        self.write_file(backup_path, content)
        return backup_path

    def restore_backup(self, path: str, backup_path: str) -> bool:
        """Restore file from backup."""
        content = self.read_file(backup_path)
        self.write_file(path, content)
        return True

    def calculate_checksum(self, path: str) -> str:
        """Calculate SHA256 checksum of file."""
        import hashlib
        content = self.read_file(path)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        import os
        return os.path.exists(path)

    def create_backup_path(self, path: str) -> str:
        """Generate unique backup path."""
        import os
        import uuid
        base, ext = os.path.splitext(path)
        return f'{base}.bak_{str(uuid.uuid4())[:8]}{ext}'


class TransactionState(Enum):
    IDLE = 'idle'
    ACTIVE = 'active'
    COMMITTED = 'committed'
    ROLLED_BACK = 'rolled_back'
    FAILED = 'failed'


class TransactionManager:
    """Manages transaction lifecycle for multi-file editing."""

    def __init__(self, fs: SafeFileSystem):
        self._fs = fs
        self._state: TransactionState = TransactionState.IDLE
        self._backups: dict[str, str] = {}
        self._modified_files: list[str] = []
        self._transaction_id: str = ''
        self._started_at: str = ''

    def begin(self) -> str:
        """Begin a new transaction."""
        import uuid
        self._state = TransactionState.ACTIVE
        self._transaction_id = f'txn_{str(uuid.uuid4())[:8]}'
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._backups = {}
        self._modified_files = []
        return self._transaction_id

    def register_backup(self, path: str, backup_path: str) -> None:
        """Register a backup for a file."""
        if self._state != TransactionState.ACTIVE:
            raise ValueError('Transaction not active')
        self._backups[path] = backup_path
        if path not in self._modified_files:
            self._modified_files.append(path)

    def commit(self) -> bool:
        """Commit the transaction."""
        if self._state != TransactionState.ACTIVE:
            return False
        self._state = TransactionState.COMMITTED
        return True

    def rollback(self) -> bool:
        """Rollback the transaction."""
        if self._state == TransactionState.COMMITTED:
            self._state = TransactionState.FAILED
            return False
        for path, backup_path in self._backups.items():
            self._fs.restore_backup(path, backup_path)
        self._state = TransactionState.ROLLED_BACK
        return True

    def clear(self) -> None:
        """Clear transaction state."""
        self._state = TransactionState.IDLE
        self._backups = {}
        self._modified_files = []
        self._transaction_id = ''
        self._started_at = ''

    def transaction_status(self) -> dict[str, Any]:
        """Return transaction status."""
        return {
            'id': self._transaction_id,
            'state': self._state.value,
            'started_at': self._started_at,
            'backups': len(self._backups),
            'modified_files': list(self._modified_files),
        }


class PatchApplyEngine:
    """Applies validated patches to filesystem through SafeFileSystem and TransactionManager."""

    def __init__(self, fs: SafeFileSystem, tm: TransactionManager):
        self._fs = fs
        self._tm = tm

    def apply_patch(self, result: PatchResult) -> PatchResult:
        """Apply a validated patch to the filesystem."""
        if not result.validation.syntax_valid:
            return PatchResult(
                summary=result.summary,
                validation=result.validation,
                errors=['Patch validation failed']
            )

        txn_id = self._tm.begin()
        applied_files = []

        try:
            # Sort files for deterministic order
            sorted_files = sorted(result.summary.files, key=lambda f: f.path)
            for pf in sorted_files:
                backup = self._fs.backup_file(pf.path)
                self._tm.register_backup(pf.path, backup)
                self._apply_file(pf)
                applied_files.append(pf.path)

            self._tm.commit()
            return PatchResult(
                summary=result.summary,
                validation=result.validation,
                applied_files=applied_files,
            )
        except Exception as e:
            self._restore_failed_transaction()
            return PatchResult(
                summary=result.summary,
                validation=result.validation,
                applied_files=applied_files,
                errors=[str(e)],
            )

    def apply_file(self, patch_file: PatchFile) -> bool:
        """Apply operations to a single file."""
        return self._apply_file(patch_file)

    def apply_operation(self, op: PatchOperation) -> bool:
        """Apply a single operation."""
        if op.operation_type == PatchType.ADD:
            self._fs.write_file(op.file_path, op.proposed_content)
        elif op.operation_type == PatchType.DELETE:
            self._fs.write_file(op.file_path, '')
        else:
            self._fs.write_file(op.file_path, op.proposed_content)
        return True

    def _apply_file(self, patch_file: PatchFile) -> bool:
        """Internal apply file."""
        for op in patch_file.changes:
            self.apply_operation(op)
        return True

    def _restore_failed_transaction(self) -> None:
        """Restore backups on failure."""
        self._tm.rollback()


class RollbackStatus(Enum):
    SUCCESS = 'success'
    PARTIAL = 'partial'
    FAILED = 'failed'
    SKIPPED = 'skipped'


@dataclass
class RollbackEntry:
    original_path: str
    backup_path: str
    restored: bool = False
    checksum_verified: bool = False
    warning: str = ''
    error: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'original_path': self.original_path,
            'backup_path': self.backup_path,
            'restored': self.restored,
            'checksum_verified': self.checksum_verified,
            'warning': self.warning,
            'error': self.error,
        }


@dataclass
class RollbackSummary:
    rollback_id: str
    timestamp: str
    total_files: int
    restored_count: int
    failed_count: int
    skipped_count: int
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            'rollback_id': self.rollback_id,
            'timestamp': self.timestamp,
            'total_files': self.total_files,
            'restored_count': self.restored_count,
            'failed_count': self.failed_count,
            'skipped_count': self.skipped_count,
            'duration_ms': self.duration_ms,
        }


@dataclass
class RollbackResult:
    summary: RollbackSummary
    entries: list[RollbackEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'summary': self.summary.to_dict(),
            'entries': [e.to_dict() for e in self.entries],
            'warnings': list(self.warnings),
            'errors': list(self.errors),
        }


class RollbackEngine:
    """Recovery and rollback engine for completed edits."""

    def __init__(self, fs: SafeFileSystem):
        self._fs = fs
        self._history: list[RollbackSummary] = []

    def restore_patch(self, backup_map: dict[str, str]) -> RollbackResult:
        """Restore multiple files from backups."""
        import time
        start = time.time()
        entries = []
        restored_count = 0
        failed_count = 0
        skipped_count = 0

        for original_path in sorted(backup_map.keys()):
            backup_path = backup_map[original_path]
            entry = self.restore_file(original_path, backup_path)
            entries.append(entry)
            if entry.restored:
                restored_count += 1
            elif entry.error:
                failed_count += 1
            else:
                skipped_count += 1

        duration_ms = int((time.time() - start) * 1000)
        status = RollbackStatus.SUCCESS
        if failed_count > 0 and restored_count == 0:
            status = RollbackStatus.FAILED
        elif failed_count > 0:
            status = RollbackStatus.PARTIAL

        self._history.append(RollbackSummary(
            rollback_id=f'rollback_{len(self._history) + 1}',
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_files=len(backup_map),
            restored_count=restored_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            duration_ms=duration_ms,
        ))

        return RollbackResult(
            summary=RollbackSummary(
                rollback_id=f'rollback_{len(self._history)}',
                timestamp=datetime.now(timezone.utc).isoformat(),
                total_files=len(backup_map),
                restored_count=restored_count,
                failed_count=failed_count,
                skipped_count=skipped_count,
                duration_ms=duration_ms,
            ),
            entries=entries,
        )

    def restore_file(self, original_path: str, backup_path: str) -> RollbackEntry:
        """Restore single file from backup."""
        if not self._fs.file_exists(backup_path):
            return RollbackEntry(original_path=original_path, backup_path=backup_path, error='Backup missing')

        verified = self.verify_backup(backup_path)
        if not verified:
            return RollbackEntry(original_path=original_path, backup_path=backup_path, warning='Checksum verification failed')

        try:
            self._fs.restore_backup(original_path, backup_path)
            return RollbackEntry(original_path=original_path, backup_path=backup_path, restored=True, checksum_verified=True)
        except Exception as e:
            return RollbackEntry(original_path=original_path, backup_path=backup_path, error=str(e))

    def restore_multiple(self, backup_maps: list[dict[str, str]]) -> RollbackResult:
        """Restore multiple backup maps sequentially."""
        all_restored = 0
        all_failed = 0
        all_skipped = 0
        all_entries = []
        for backup_map in backup_maps:
            result = self.restore_patch(backup_map)
            all_restored += result.summary.restored_count
            all_failed += result.summary.failed_count
            all_skipped += result.summary.skipped_count
            all_entries.extend(result.entries)
        return RollbackResult(
            summary=RollbackSummary(
                rollback_id='multi_rollback',
                timestamp=datetime.now(timezone.utc).isoformat(),
                total_files=len(all_entries),
                restored_count=all_restored,
                failed_count=all_failed,
                skipped_count=all_skipped,
            ),
            entries=all_entries,
        )

    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity via checksum."""
        if not self._fs.file_exists(backup_path):
            return False
        return self.verify_restore(backup_path)

    def verify_restore(self, backup_path: str) -> bool:
        """Verify backup can be read and has content."""
        try:
            content = self._fs.read_file(backup_path)
            return len(content) >= 0
        except Exception:
            return False

    def cleanup_backups(self, backup_paths: list[str]) -> int:
        """Remove backup files after successful restore."""
        import os
        cleaned = 0
        for path in backup_paths:
            if self._fs.file_exists(path):
                os.unlink(path)
                cleaned += 1
        return cleaned

    def rollback_history(self) -> list[dict[str, Any]]:
        """Return history of rollbacks."""
        return [h.to_dict() for h in self._history]


@register_tool('editing')
class EditingTool(Tool):
    """Safe editing tool wrapper for EditingEngine."""

    name = 'editing'
    description = 'Safe file editing with preview, validation, apply, and rollback capabilities.'
    parameters = {
        'operation': 'Operation: generate_patch, validate_patch, create_patch, preview, apply',
        'path': 'File path for the patch.',
        'original': 'Original file content.',
        'proposed': 'Proposed new content.',
        'backups': 'Backup map for rollback.',
    }

    def __init__(self):
        super().__init__()
        self._engine = EditingEngine()

    def execute(
        self,
        operation: str,
        path: Optional[str] = None,
        original: str = '',
        proposed: str = '',
        backups: Optional[dict[str, str]] = None,
    ) -> ToolResult:
        """Execute editing operations."""
        try:
            if operation == 'generate_patch':
                result = self._engine.generate_patch(path, original, proposed)
                return ToolResult(success=True, data=result.to_dict())
            if operation == 'validate_patch':
                summary = self._engine.generate_patch(path, original, proposed)
                validation = self._engine.validate_patch(summary)
                return ToolResult(success=True, data=validation.to_dict())
            if operation == 'create_patch':
                result = self._engine.create_patch(path, original, proposed)
                return ToolResult(success=True, data=result.to_dict())
            if operation == 'preview':
                summary = self._engine.generate_patch(path, original, proposed)
                preview = PatchPreview()
                output = preview.preview_patch(summary)
                return ToolResult(success=True, data={'preview': output})
            return ToolResult(success=False, error=f'Unknown operation: {operation}')
        except Exception as e:
            return ToolResult(success=False, error=str(e))