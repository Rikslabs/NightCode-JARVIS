from ..memory.base import Command
from ..memory.registry import register_command
from ..tools.registry import get_tool
from ..tools.editing import SafeFileSystem, RollbackEngine, EditingEngine


def _get_editing_engine():
    return EditingEngine()


@register_command('preview_patch')
class PreviewPatchCommand(Command):
    """Preview a patch before applying."""

    description = 'Preview changes for a file patch.'
    parameters = {
        'path': 'Path to the file to patch.',
        'original': 'Original file content.',
        'proposed': 'Proposed new content.',
    }

    def execute(self, params: dict) -> str:
        path = params.get('path', '').strip()
        original = params.get('original', '')
        proposed = params.get('proposed', '')

        if not path:
            return 'Please provide a file path.'

        engine = _get_editing_engine()
        patch = engine.generate_patch(path, original, proposed)
        validation = engine.validate_patch(patch)
        if not validation.syntax_valid:
            return f'Patch validation failed: {validation.validation_notes}'

        from ..tools.editing import PatchPreview
        preview = PatchPreview()
        return preview.preview_patch(patch)


@register_command('apply_patch')
class ApplyPatchCommand(Command):
    """Apply a validated patch to files."""

    description = 'Apply a patch to a file.'
    parameters = {
        'path': 'Path to the file to patch.',
        'original': 'Original file content.',
        'proposed': 'Proposed new content.',
    }

    def execute(self, params: dict) -> str:
        path = params.get('path', '').strip()
        original = params.get('original', '')
        proposed = params.get('proposed', '')

        if not path:
            return 'Please provide a file path.'

        engine = _get_editing_engine()
        result = engine.create_patch(path, original, proposed)

        if result.errors:
            return f'Patch application failed: {result.errors}'

        return f'Patch applied successfully to {path}.'


@register_command('rollback_patch')
class RollbackPatchCommand(Command):
    """Rollback changes using backup map."""

    description = 'Rollback a file to a previous backup.'
    parameters = {
        'backups': 'Dict mapping file paths to backup paths.',
    }

    def execute(self, params: dict) -> str:
        backups = params.get('backups', {})

        if not backups:
            return 'Please provide a backup map to restore.'

        fs = SafeFileSystem()
        rollback = RollbackEngine(fs)
        result = rollback.restore_patch(backups)

        if result.summary.failed_count > 0:
            return f'Rollback completed with {result.summary.failed_count} failures.'

        return f'Rollback completed. {result.summary.restored_count} files restored.'


@register_command('validate_patch')
class ValidatePatchCommand(Command):
    """Validate a patch without applying."""

    description = 'Validate a patch for a file.'
    parameters = {
        'path': 'Path to the file.',
        'original': 'Original file content.',
        'proposed': 'Proposed new content.',
    }

    def execute(self, params: dict) -> str:
        path = params.get('path', '').strip()
        original = params.get('original', '')
        proposed = params.get('proposed', '')

        if not path:
            return 'Please provide a file path.'

        engine = _get_editing_engine()
        patch = engine.generate_patch(path, original, proposed)
        result = engine.validate_patch(patch)

        lines = [
            f'File: {path}',
            f'Syntax valid: {result.syntax_valid}',
            f'Lint passed: {result.lint_passed}',
        ]

        if result.validation_notes:
            lines.append('Notes:')
            for note in result.validation_notes:
                lines.append(f'  - {note}')

        return '\n'.join(lines)