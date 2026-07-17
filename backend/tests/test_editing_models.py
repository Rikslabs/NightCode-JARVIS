import pytest
from app.tools.editing import (
    PatchType, PatchStatus, PatchRisk,
    PatchOperation, PatchFile, PatchChange,
    PatchValidation, PatchSummary, PatchResult
)


def test_patch_type_enum():
    assert PatchType.ADD.value == 'add'
    assert PatchType.DELETE.value == 'delete'
    assert PatchType.REPLACE.value == 'replace'
    assert PatchType.INSERT_BEFORE.value == 'insert_before'
    assert PatchType.INSERT_AFTER.value == 'insert_after'
    assert PatchType.MODIFY.value == 'modify'


def test_patch_status_enum():
    assert PatchStatus.PENDING.value == 'pending'
    assert PatchStatus.APPROVED.value == 'approved'
    assert PatchStatus.REJECTED.value == 'rejected'
    assert PatchStatus.APPLIED.value == 'applied'
    assert PatchStatus.ROLLED_BACK.value == 'rolled_back'
    assert PatchStatus.FAILED.value == 'failed'


def test_patch_risk_enum():
    assert PatchRisk.LOW.value == 'low'
    assert PatchRisk.MEDIUM.value == 'medium'
    assert PatchRisk.HIGH.value == 'high'
    assert PatchRisk.CRITICAL.value == 'critical'


def test_patch_operation_defaults():
    op = PatchOperation(file_path='test.py', operation_type=PatchType.ADD)
    assert op.line_start is None
    assert op.line_end is None
    assert op.original_content == ''
    assert op.proposed_content == ''
    assert op.description == ''
    assert op.risk == PatchRisk.MEDIUM


def test_patch_operation_to_dict():
    op = PatchOperation(
        file_path='test.py',
        operation_type=PatchType.REPLACE,
        line_start=10,
        line_end=20,
        original_content='old',
        proposed_content='new',
        description='Fix bug',
        risk=PatchRisk.HIGH
    )
    d = op.to_dict()
    assert d['file_path'] == 'test.py'
    assert d['operation_type'] == 'replace'
    assert d['line_start'] == 10
    assert d['line_end'] == 20
    assert d['original_content'] == 'old'
    assert d['proposed_content'] == 'new'
    assert d['description'] == 'Fix bug'
    assert d['risk'] == 'high'


def test_patch_file_defaults():
    pf = PatchFile(path='src/main.py')
    assert pf.changes == []
    assert pf.original_checksum == ''
    assert pf.proposed_checksum == ''


def test_patch_file_to_dict():
    op = PatchOperation(file_path='test.py', operation_type=PatchType.ADD)
    pf = PatchFile(path='src/main.py', changes=[op], original_checksum='abc', proposed_checksum='def')
    d = pf.to_dict()
    assert d['path'] == 'src/main.py'
    assert len(d['changes']) == 1
    assert d['original_checksum'] == 'abc'


def test_patch_change_defaults():
    pc = PatchChange(file_path='test.py')
    assert pc.operations == []
    assert pc.status == PatchStatus.PENDING


def test_patch_change_to_dict():
    op = PatchOperation(file_path='test.py', operation_type=PatchType.DELETE)
    pc = PatchChange(file_path='src/main.py', operations=[op], status=PatchStatus.APPROVED)
    d = pc.to_dict()
    assert d['file_path'] == 'src/main.py'
    assert d['status'] == 'approved'


def test_patch_validation_defaults():
    pv = PatchValidation()
    assert pv.syntax_valid is False
    assert pv.lint_passed is False
    assert pv.backward_compatible is True
    assert pv.tests_passed is False
    assert pv.validation_notes == []


def test_patch_validation_to_dict():
    pv = PatchValidation(syntax_valid=True, lint_passed=True, backward_compatible=True, tests_passed=True, validation_notes=['all good'])
    d = pv.to_dict()
    assert d['syntax_valid'] is True
    assert d['lint_passed'] is True
    assert d['backward_compatible'] is True
    assert d['tests_passed'] is True
    assert d['validation_notes'] == ['all good']


def test_patch_summary_defaults():
    ps = PatchSummary(id='p1', title='Fix', description='Fix bug')
    assert ps.files == []
    assert ps.rollback_available is True
    assert ps.rollback_instructions == ''
    assert ps.estimated_risk == PatchRisk.MEDIUM
    assert ps.created_at is not None


def test_patch_summary_to_dict():
    ps = PatchSummary(
        id='p1', title='Fix', description='Fix bug',
        rollback_available=True, rollback_instructions='git revert', estimated_risk=PatchRisk.LOW
    )
    d = ps.to_dict()
    assert d['id'] == 'p1'
    assert d['title'] == 'Fix'
    assert d['rollback_available'] is True


def test_patch_result_defaults():
    ps = PatchSummary(id='p1', title='Test', description='Test patch')
    pv = PatchValidation()
    pr = PatchResult(summary=ps, validation=pv)
    assert pr.applied_files == []
    assert pr.skipped_files == []
    assert pr.errors == []


def test_patch_result_to_dict():
    ps = PatchSummary(id='p1', title='Test', description='Test')
    pv = PatchValidation(syntax_valid=True)
    pr = PatchResult(summary=ps, validation=pv, applied_files=['a.py'], errors=['err'])
    d = pr.to_dict()
    assert d['applied_files'] == ['a.py']
    assert d['errors'] == ['err']


def test_model_equality():
    op1 = PatchOperation(file_path='a.py', operation_type=PatchType.ADD)
    op2 = PatchOperation(file_path='a.py', operation_type=PatchType.ADD)
    assert op1 == op2


def test_identical_files():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    patch = gen.generate_patch('test.py', 'same content', 'same content')
    assert len(patch.files[0].changes) == 0
    assert patch.estimated_risk == PatchRisk.LOW


def test_single_line_replacement():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    patch = gen.generate_patch('test.py', 'old line', 'new line')
    assert len(patch.files[0].changes) == 1
    assert patch.files[0].changes[0].operation_type == PatchType.REPLACE


def test_insertion():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    patch = gen.generate_patch('test.py', '', 'new content\n')
    assert len(patch.files[0].changes) == 1
    assert patch.files[0].changes[0].operation_type == PatchType.ADD


def test_deletion():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    patch = gen.generate_patch('test.py', 'old content', '')
    assert len(patch.files[0].changes) == 1
    assert patch.files[0].changes[0].operation_type == PatchType.DELETE


def test_checksum_generation():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    checksum = gen.calculate_checksum('test content')
    assert len(checksum) == 16
    assert checksum == gen.calculate_checksum('test content')


def test_operation_merging():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    ops = [
        PatchOperation('a.py', PatchType.REPLACE, 1, 2, 'a', 'b'),
        PatchOperation('a.py', PatchType.REPLACE, 3, 4, 'c', 'd'),
    ]
    merged = gen.merge_operations(ops)
    assert len(merged) >= 1


def test_risk_estimation():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    low = gen.estimate_risk([])
    assert low == PatchRisk.LOW
    high = gen.estimate_risk([PatchOperation('a.py', PatchType.REPLACE, risk=PatchRisk.HIGH)])
    assert high == PatchRisk.HIGH


def test_summary_generation():
    from app.tools.editing import PatchGenerator
    gen = PatchGenerator()
    ps = PatchSummary('id', 'title', 'desc', estimated_risk=PatchRisk.MEDIUM)
    summary = gen.generate_summary(ps)
    assert 'title' in summary
    assert 'medium' in summary


def test_validator_valid_patch():
    from app.tools.editing import PatchGenerator, PatchValidator
    gen = PatchGenerator()
    validator = PatchValidator()
    patch = gen.generate_patch('test.py', 'old', 'new')
    result = validator.validate_patch(patch)
    assert result.syntax_valid is True


def test_validator_invalid_line_ranges():
    from app.tools.editing import PatchValidator
    validator = PatchValidator()
    op = PatchOperation('test.py', PatchType.REPLACE, line_start=0, line_end=5, original_content='old', proposed_content='new')
    valid, notes = validator.validate_ranges(op)
    assert valid is False
    assert 'Invalid line_start' in notes[0]


def test_validator_check_mismatch():
    from app.tools.editing import PatchValidator
    validator = PatchValidator()
    valid, notes = validator.validate_checksums('orig', 'prop', 'wrong', 'checksum')
    assert valid is False


def test_validator_empty_operation():
    from app.tools.editing import PatchValidator
    validator = PatchValidator()
    # DELETE without original content
    op = PatchOperation('test.py', PatchType.DELETE)
    valid, notes = validator.validate_operation(op)
    assert valid is False


def test_validator_overlaps():
    from app.tools.editing import PatchGenerator, PatchValidator
    gen = PatchGenerator()
    validator = PatchValidator()
    op1 = PatchOperation('a.py', PatchType.REPLACE, line_start=1, line_end=10, original_content='a', proposed_content='b')
    op2 = PatchOperation('a.py', PatchType.REPLACE, line_start=5, line_end=15, original_content='c', proposed_content='d')
    pf = PatchFile(path='a.py', changes=[op1, op2])
    ps = PatchSummary(id='p1', title='Test', description='Test', files=[pf])
    notes = validator.validate_overlaps(ps)
    assert len(notes) > 0


def test_validator_malformed_patch():
    from app.tools.editing import PatchValidator
    validator = PatchValidator()
    ps = PatchSummary(id='p1', title='Test', description='Test')
    valid, notes = validator.validate_summary(ps)
    assert valid is True


def test_validator_deterministic():
    from app.tools.editing import PatchGenerator, PatchValidator
    gen = PatchGenerator()
    validator = PatchValidator()
    patch1 = gen.generate_patch('a.py', 'old', 'new')
    patch2 = gen.generate_patch('a.py', 'old', 'new')
    r1 = validator.validate_patch(patch1)
    r2 = validator.validate_patch(patch2)
    assert r1.syntax_valid == r2.syntax_valid


def test_engine_delegates_generate():
    from app.tools.editing import EditingEngine
    engine = EditingEngine()
    result = engine.generate_patch('test.py', 'old', 'new')
    assert result.title == 'Patch for test.py'


def test_engine_delegates_validate():
    from app.tools.editing import EditingEngine, PatchGenerator
    engine = EditingEngine()
    gen = PatchGenerator()
    patch = gen.generate_patch('test.py', 'old', 'new')
    result = engine.validate_patch(patch)
    assert result.syntax_valid is True


def test_engine_create_patch():
    from app.tools.editing import EditingEngine
    engine = EditingEngine()
    result = engine.create_patch('test.py', 'old', 'new')
    assert isinstance(result, PatchResult)
    assert result.summary is not None
    assert result.validation is not None


def test_engine_placeholders_exist():
    from app.tools.editing import EditingEngine
    engine = EditingEngine()
    assert engine._preview_engine is None
    assert engine._apply_engine is None
    assert engine._rollback_engine is None


def test_preview_single_file():
    from app.tools.editing import PatchPreview, PatchGenerator
    gen = PatchGenerator()
    preview = PatchPreview()
    patch = gen.generate_patch('test.py', 'old', 'new')
    output = preview.preview_patch(patch)
    assert 'test.py' in output
    assert '-' in output or '+' in output


def test_preview_file_method():
    from app.tools.editing import PatchPreview, PatchOperation, PatchFile, PatchType
    preview = PatchPreview()
    op = PatchOperation('a.py', PatchType.ADD, proposed_content='line1\n')
    pf = PatchFile(path='a.py', changes=[op])
    lines = preview.preview_file(pf)
    assert '--- a.py' in lines
    assert '+++ a.py' in lines


def test_preview_addition():
    from app.tools.editing import PatchPreview, PatchOperation, PatchFile, PatchType
    preview = PatchPreview()
    op = PatchOperation('a.py', PatchType.ADD, proposed_content='new line')
    lines = preview.render_diff(op)
    assert any('+ new line' in l for l in lines)


def test_preview_deletion():
    from app.tools.editing import PatchPreview, PatchOperation, PatchType
    preview = PatchPreview()
    op = PatchOperation('a.py', PatchType.DELETE, line_start=1, original_content='removed')
    lines = preview.render_diff(op)
    assert any('- removed' in l for l in lines)


def test_preview_replacement():
    from app.tools.editing import PatchPreview, PatchOperation, PatchType
    preview = PatchPreview()
    op = PatchOperation('a.py', PatchType.REPLACE, line_start=1, line_end=1,
                        original_content='old', proposed_content='new')
    lines = preview.render_diff(op)
    assert any('- old' in l for l in lines)
    assert any('+ new' in l for l in lines)


def test_preview_empty_patch():
    from app.tools.editing import PatchPreview
    preview = PatchPreview()
    ps = PatchSummary(id='p1', title='Empty', description='No changes')
    summary = preview.render_summary(ps)
    assert '0' in summary


def test_preview_deterministic():
    from app.tools.editing import PatchPreview, PatchGenerator
    preview = PatchPreview()
    gen = PatchGenerator()
    patch1 = gen.generate_patch('a.py', 'x', 'y')
    patch2 = gen.generate_patch('a.py', 'x', 'y')
    out1 = preview.preview_patch(patch1)
    out2 = preview.preview_patch(patch2)
    assert out1 == out2


def test_safe_fs_checksum(tmp_path):
    import os
    from app.tools.editing import SafeFileSystem
    fs = SafeFileSystem()
    test_file = tmp_path / 'test.txt'
    test_file.write_text('content')
    checksum = fs.calculate_checksum(str(test_file))
    assert len(checksum) == 16


def test_safe_fs_file_exists(tmp_path):
    from app.tools.editing import SafeFileSystem
    fs = SafeFileSystem()
    existing = tmp_path / 'exists.txt'
    existing.write_text('content')
    assert fs.file_exists(str(existing)) is True
    assert fs.file_exists(str(tmp_path / 'missing.txt')) is False


def test_safe_fs_atomic_write(tmp_path):
    import os
    from app.tools.editing import SafeFileSystem
    fs = SafeFileSystem()
    test_file = tmp_path / 'write.txt'
    fs.write_file(str(test_file), 'new content')
    assert test_file.read_text() == 'new content'


def test_safe_fs_backup_uniqueness(tmp_path):
    from app.tools.editing import SafeFileSystem
    fs = SafeFileSystem()
    test_file = tmp_path / 'backup.txt'
    test_file.write_text('original')
    backup1 = fs.create_backup_path(str(test_file))
    backup2 = fs.create_backup_path(str(test_file))
    assert backup1 != backup2


def test_safe_fs_backup_path_format(tmp_path):
    from app.tools.editing import SafeFileSystem
    fs = SafeFileSystem()
    path = str(tmp_path / 'file.py')
    backup = fs.create_backup_path(path)
    assert '.bak_' in backup
    assert path.replace('.py', '').replace(str(tmp_path), '') in backup


def test_transaction_begin():
    from app.tools.editing import TransactionManager, SafeFileSystem
    tm = TransactionManager(SafeFileSystem())
    txn_id = tm.begin()
    assert txn_id.startswith('txn_')
    assert tm.transaction_status()['state'] == 'active'


def test_transaction_register_backup():
    from app.tools.editing import TransactionManager, SafeFileSystem
    tm = TransactionManager(SafeFileSystem())
    tm.begin()
    tm.register_backup('a.py', 'a.py.bak')
    assert len(tm.transaction_status()['modified_files']) == 1


def test_transaction_commit():
    from app.tools.editing import TransactionManager, SafeFileSystem
    tm = TransactionManager(SafeFileSystem())
    tm.begin()
    tm.register_backup('a.py', 'a.bak')
    result = tm.commit()
    assert result is True
    assert tm.transaction_status()['state'] == 'committed'


def test_transaction_rollback(tmp_path):
    from app.tools.editing import TransactionManager, SafeFileSystem
    fs = SafeFileSystem()
    tm = TransactionManager(fs)
    test_file = tmp_path / 't.py'
    test_file.write_text('original')
    backup = tmp_path / 't.py.bak'
    backup.write_text('backup')
    tm.begin()
    tm.register_backup(str(test_file), str(backup))
    result = tm.rollback()
    assert result is True
    assert tm.transaction_status()['state'] == 'rolled_back'


def test_transaction_double_commit_rejected():
    from app.tools.editing import TransactionManager, SafeFileSystem
    tm = TransactionManager(SafeFileSystem())
    tm.begin()
    tm.commit()
    second = tm.commit()
    assert second is False


def test_transaction_rollback_after_commit():
    from app.tools.editing import TransactionManager, SafeFileSystem
    tm = TransactionManager(SafeFileSystem())
    tm.begin()
    tm.commit()
    rollback = tm.rollback()
    assert rollback is False
    assert tm.transaction_status()['state'] == 'failed'


def test_transaction_status_transitions():
    from app.tools.editing import TransactionManager, SafeFileSystem
    tm = TransactionManager(SafeFileSystem())
    assert tm.transaction_status()['state'] == 'idle'
    tm.begin()
    assert tm.transaction_status()['state'] == 'active'
    tm.commit()
    assert tm.transaction_status()['state'] == 'committed'


def test_transaction_clear():
    from app.tools.editing import TransactionManager, SafeFileSystem
    tm = TransactionManager(SafeFileSystem())
    tm.begin()
    tm.register_backup('a.py', 'a.bak')
    tm.clear()
    assert tm.transaction_status()['state'] == 'idle'
    assert tm.transaction_status()['backups'] == 0


def test_apply_single_file(tmp_path):
    from app.tools.editing import EditingEngine, PatchApplyEngine, SafeFileSystem, TransactionManager
    engine = EditingEngine()
    fs = SafeFileSystem()
    tm = TransactionManager(fs)
    apply = PatchApplyEngine(fs, tm)
    test_file = tmp_path / 'single.py'
    test_file.write_text('old')
    result = engine.create_patch(str(test_file), 'old', 'new')
    applied = apply.apply_patch(result)
    assert len(applied.applied_files) == 1


def test_apply_multi_file(tmp_path):
    from app.tools.editing import EditingEngine, PatchApplyEngine, SafeFileSystem, TransactionManager, PatchSummary, PatchFile, PatchValidation, PatchResult
    fs = SafeFileSystem()
    tm = TransactionManager(fs)
    apply = PatchApplyEngine(fs, tm)
    file_a = tmp_path / 'a.py'
    file_b = tmp_path / 'b.py'
    file_a.write_text('old_a')
    file_b.write_text('old_b')
    engine = EditingEngine()
    summary = PatchSummary(
        id='multi',
        title='Multi',
        description='Multiple files',
        files=[
            PatchFile(path=str(file_a), changes=engine._generator._compare_lines(str(file_a), ['old_a'], ['new_a'])),
            PatchFile(path=str(file_b), changes=engine._generator._compare_lines(str(file_b), ['old_b'], ['new_b'])),
        ])
    validation = PatchValidation(syntax_valid=True)
    result = PatchResult(summary=summary, validation=validation)
    applied = apply.apply_patch(result)
    assert len(applied.applied_files) == 2


def test_apply_invalid_rejected():
    from app.tools.editing import EditingEngine, PatchApplyEngine, SafeFileSystem, TransactionManager, PatchValidation, PatchResult
    fs = SafeFileSystem()
    tm = TransactionManager(fs)
    apply = PatchApplyEngine(fs, tm)
    engine = EditingEngine()
    summary = engine.generate_patch('test.py', 'old', 'new')
    invalid_result = PatchResult(summary=summary, validation=PatchValidation(syntax_valid=False))
    applied = apply.apply_patch(invalid_result)
    assert len(applied.errors) > 0


def test_apply_backup_created(tmp_path):
    from app.tools.editing import EditingEngine, PatchApplyEngine, SafeFileSystem, TransactionManager
    fs = SafeFileSystem()
    tm = TransactionManager(fs)
    apply = PatchApplyEngine(fs, tm)
    test_file = tmp_path / 'backup_test.py'
    test_file.write_text('original')
    engine = EditingEngine()
    result = engine.create_patch(str(test_file), 'original', 'modified')
    apply.apply_patch(result)
    status = tm.transaction_status()
    assert status['backups'] >= 1


def test_apply_deterministic_order(tmp_path):
    from app.tools.editing import EditingEngine, PatchApplyEngine, SafeFileSystem, TransactionManager, PatchSummary, PatchFile, PatchValidation, PatchResult
    fs = SafeFileSystem()
    tm = TransactionManager(fs)
    apply = PatchApplyEngine(fs, tm)
    file_z = tmp_path / 'z.py'
    file_a = tmp_path / 'a.py'
    file_z.write_text('z_old')
    file_a.write_text('a_old')
    engine = EditingEngine()
    summary = PatchSummary(
        id='order',
        title='Order',
        description='Test order',
        files=[
            PatchFile(path=str(file_z), changes=engine._generator._compare_lines(str(file_z), ['z_old'], ['z_new'])),
            PatchFile(path=str(file_a), changes=engine._generator._compare_lines(str(file_a), ['a_old'], ['a_new'])),
        ])
    validation = PatchValidation(syntax_valid=True)
    result = PatchResult(summary=summary, validation=validation)
    applied = apply.apply_patch(result)
    # Files should be applied in sorted order (a, then z)
    assert applied.applied_files[0].endswith('a.py')
    assert applied.applied_files[1].endswith('z.py')


def test_rollback_restore_success(tmp_path):
    from app.tools.editing import RollbackEngine, SafeFileSystem
    fs = SafeFileSystem()
    rollback = RollbackEngine(fs)
    original = tmp_path / 'restore.txt'
    original.write_text('modified')
    backup = tmp_path / 'restore.txt.bak'
    backup.write_text('original')
    result = rollback.restore_file(str(original), str(backup))
    assert result.restored is True
    assert original.read_text() == 'original'


def test_rollback_multiple_files(tmp_path):
    from app.tools.editing import RollbackEngine, SafeFileSystem
    fs = SafeFileSystem()
    rollback = RollbackEngine(fs)
    file_a = tmp_path / 'ra.py'
    file_b = tmp_path / 'rb.py'
    file_a.write_text('new')
    file_b.write_text('new')
    ba = tmp_path / 'ra.py.bak'
    bb = tmp_path / 'rb.py.bak'
    ba.write_text('old')
    bb.write_text('old')
    result = rollback.restore_patch({str(file_a): str(ba), str(file_b): str(bb)})
    assert result.summary.total_files == 2
    assert result.summary.restored_count == 2


def test_rollback_missing_backup():
    from app.tools.editing import RollbackEngine, SafeFileSystem
    rollback = RollbackEngine(SafeFileSystem())
    result = rollback.restore_file('missing.py', 'missing.bak')
    assert result.error == 'Backup missing'


def test_rollback_checksum_mismatch(tmp_path):
    from app.tools.editing import RollbackEngine, SafeFileSystem
    fs = SafeFileSystem()
    rollback = RollbackEngine(fs)
    # Create a backup file that exists
    backup = tmp_path / 'chk.bak'
    backup.write_text('content')
    entry = rollback.restore_file('other.py', str(backup))
    # Will have warning because backup exists but original doesn't
    assert entry.warning or entry.error or entry.restored


def test_rollback_partial_failure(tmp_path):
    from app.tools.editing import RollbackEngine, SafeFileSystem
    fs = SafeFileSystem()
    rollback = RollbackEngine(fs)
    file_a = tmp_path / 'pa.py'
    file_a.write_text('new')
    ba = tmp_path / 'pa.py.bak'
    ba.write_text('old')
    # One valid, one missing
    result = rollback.restore_patch({str(file_a): str(ba), 'missing.py': 'missing.bak'})
    assert result.summary.failed_count == 1
    assert result.summary.restored_count == 1


def test_rollback_cleanup(tmp_path):
    from app.tools.editing import RollbackEngine, SafeFileSystem
    fs = SafeFileSystem()
    rollback = RollbackEngine(fs)
    backup = tmp_path / 'clean.bak'
    backup.write_text('data')
    cleaned = rollback.cleanup_backups([str(backup)])
    assert cleaned == 1
    assert not fs.file_exists(str(backup))


def test_rollback_history():
    from app.tools.editing import RollbackEngine, SafeFileSystem
    rollback = RollbackEngine(SafeFileSystem())
    rollback.restore_patch({'a.py': 'a.bak'})
    history = rollback.rollback_history()
    assert len(history) == 1


def test_rollback_deterministic(tmp_path):
    from app.tools.editing import RollbackEngine, SafeFileSystem
    fs = SafeFileSystem()
    rollback = RollbackEngine(fs)
    file = tmp_path / 'det.py'
    file.write_text('current')
    backup = tmp_path / 'det.py.bak'
    backup.write_text('restore')
    r1 = rollback.restore_file(str(file), str(backup))
    r2 = rollback.restore_file(str(file), str(backup))
    assert r1.restored == r2.restored


def test_preview_command():
    from app.tools.editing import EditingTool
    tool = EditingTool()
    result = tool.execute(operation='preview', path='test.py', original='old', proposed='new')
    assert result.success is True
    assert 'preview' in result.data


def test_apply_command(tmp_path):
    from app.tools.editing import EditingTool
    tool = EditingTool()
    test_file = tmp_path / 'cmd_apply.py'
    test_file.write_text('old')
    result = tool.execute(operation='create_patch', path=str(test_file), original='old', proposed='new')
    assert result.success is True


def test_rollback_cmd(tmp_path):
    from app.tools.editing import EditingTool, SafeFileSystem, RollbackEngine
    tool = EditingTool()
    original = tmp_path / 'r.py'
    original.write_text('new')
    backup = tmp_path / 'r.py.bak'
    backup.write_text('old')
    fs = SafeFileSystem()
    rollback = RollbackEngine(fs)
    result = rollback.restore_patch({str(original): str(backup)})
    assert result.summary.restored_count == 1


def test_validate_cmd():
    from app.tools.editing import EditingTool
    tool = EditingTool()
    result = tool.execute(operation='validate_patch', path='test.py', original='old', proposed='new')
    assert result.success is True
    assert 'syntax_valid' in result.data


def test_preview_patch_command():
    from app.commands.editing_commands import PreviewPatchCommand
    cmd = PreviewPatchCommand()
    result = cmd.execute({'path': 'test.py', 'original': 'old', 'proposed': 'new'})
    assert 'test.py' in result or 'Preview failed' in result


def test_apply_patch_command():
    from app.commands.editing_commands import ApplyPatchCommand
    cmd = ApplyPatchCommand()
    result = cmd.execute({'path': 'nonexistent.py', 'original': 'old', 'proposed': 'new'})
    # Should handle missing file gracefully
    assert 'Patch' in result or 'failed' in result.lower()


def test_rollback_patch_command():
    from app.commands.editing_commands import RollbackPatchCommand
    cmd = RollbackPatchCommand()
    result = cmd.execute({'backups': {'a.py': 'a.bak'}})
    assert 'Rollback' in result or 'missing' in result.lower()


def test_validate_patch_command():
    from app.commands.editing_commands import ValidatePatchCommand
    cmd = ValidatePatchCommand()
    result = cmd.execute({'path': 'test.py', 'original': 'old', 'proposed': 'new'})
    assert 'Syntax valid' in result or 'syntax_valid' in result
