import pytest
from app.tools.knowledge import KnowledgeTool, KnowledgeEntry, KnowledgeCategory, KnowledgeImportance, KnowledgeSource


@pytest.fixture
def knowledge_tool():
    return KnowledgeTool()


def test_store_and_find(knowledge_tool):
    result = knowledge_tool.store('Test Rule', 'Description here', KnowledgeCategory.ENGINEERING_RULE.value,
                                  KnowledgeImportance.HIGH.value, KnowledgeSource.MANUAL.value)
    assert result['success'] is True
    entry_id = result['id']
    found = knowledge_tool.find(entry_id)
    assert found['success'] is True
    assert found['entry']['title'] == 'Test Rule'


def test_update(knowledge_tool):
    result = knowledge_tool.store('Test', 'Desc', KnowledgeCategory.BEST_PRACTICE.value,
                                  KnowledgeImportance.MEDIUM.value, KnowledgeSource.MANUAL.value)
    entry_id = result['id']
    updated = knowledge_tool.update(entry_id, {'description': 'New description'})
    assert updated['success'] is True
    entry = knowledge_tool.find(entry_id)
    assert entry['entry']['description'] == 'New description'


def test_archive(knowledge_tool):
    result = knowledge_tool.store('Test', 'Desc', KnowledgeCategory.BUG_PATTERN.value,
                                  KnowledgeImportance.LOW.value, KnowledgeSource.MANUAL.value)
    entry_id = result['id']
    archived = knowledge_tool.archive(entry_id)
    assert archived['success'] is True
    found = knowledge_tool.find(entry_id)
    assert found['entry']['archived'] is True


def test_delete(knowledge_tool):
    result = knowledge_tool.store('Test', 'Desc', KnowledgeCategory.REFACTORING_PATTERN.value,
                                  KnowledgeImportance.MEDIUM.value, KnowledgeSource.MANUAL.value)
    entry_id = result['id']
    deleted = knowledge_tool.delete(entry_id)
    assert deleted['success'] is True
    found = knowledge_tool.find(entry_id)
    assert found['success'] is False


def test_search(knowledge_tool):
    knowledge_tool.store('Python Convention', 'Use snake_case', KnowledgeCategory.CODING_CONVENTION.value,
                          KnowledgeImportance.HIGH.value, KnowledgeSource.MANUAL.value)
    knowledge_tool.store('JS Convention', 'Use camelCase', KnowledgeCategory.CODING_CONVENTION.value,
                          KnowledgeImportance.MEDIUM.value, KnowledgeSource.MANUAL.value)
    results = knowledge_tool.search(query='Python')
    assert results['count'] == 1
    assert len(results['entries']) == 1


def test_filter_by_category(knowledge_tool):
    knowledge_tool.store('Rule 1', 'Desc', KnowledgeCategory.ENGINEERING_RULE.value,
                          KnowledgeImportance.HIGH.value, KnowledgeSource.MANUAL.value)
    knowledge_tool.store('Rule 2', 'Desc', KnowledgeCategory.BEST_PRACTICE.value,
                          KnowledgeImportance.MEDIUM.value, KnowledgeSource.MANUAL.value)
    results = knowledge_tool.filter(category=KnowledgeCategory.ENGINEERING_RULE.value)
    assert results['count'] == 1


def test_list_by_category(knowledge_tool):
    knowledge_tool.store('Rule A', 'Desc', KnowledgeCategory.ENGINEERING_RULE.value,
                          KnowledgeImportance.HIGH.value, KnowledgeSource.MANUAL.value)
    knowledge_tool.store('Rule B', 'Desc', KnowledgeCategory.ENGINEERING_RULE.value,
                          KnowledgeImportance.MEDIUM.value, KnowledgeSource.MANUAL.value)
    results = knowledge_tool.list_by_category(KnowledgeCategory.ENGINEERING_RULE.value)
    assert results['count'] == 2


def test_list_by_project(knowledge_tool):
    knowledge_tool.store('Proj Rule', 'Desc', KnowledgeCategory.PROJECT_GUIDELINE.value,
                          KnowledgeImportance.HIGH.value, KnowledgeSource.MANUAL.value, project='myproj')
    results = knowledge_tool.list_by_project('myproj')
    assert results['count'] == 1


def test_related_entries(knowledge_tool):
    e1 = KnowledgeEntry(title='A', description='Desc', category=KnowledgeCategory.ENGINEERING_RULE,
                        importance=KnowledgeImportance.HIGH, source=KnowledgeSource.MANUAL)
    id1 = knowledge_tool._collection.add(e1)
    e2 = KnowledgeEntry(title='B', description='Desc', category=KnowledgeCategory.ENGINEERING_RULE,
                        importance=KnowledgeImportance.MEDIUM, source=KnowledgeSource.MANUAL,
                        related_entries=[id1])
    id2 = knowledge_tool._collection.add(e2)
    results = knowledge_tool.related_entries(id2)
    assert results['count'] == 1


def test_export(knowledge_tool):
    knowledge_tool.store('Ex Rule', 'Desc', KnowledgeCategory.ENGINEERING_RULE.value,
                          KnowledgeImportance.HIGH.value, KnowledgeSource.MANUAL.value)
    exported = knowledge_tool.export()
    assert 'entries' in exported
    assert exported['count'] == 1


def test_import(knowledge_tool):
    data = {'entries': [{'title': 'Imported', 'description': 'Test', 'category': 'engineering_rule',
                        'importance': 'high', 'source': 'manual'}]}
    result = knowledge_tool.import_entries(data)
    assert result['imported'] == 1


def test_summarize(knowledge_tool):
    knowledge_tool.store('S1', 'Desc', KnowledgeCategory.ENGINEERING_RULE.value,
                          KnowledgeImportance.HIGH.value, KnowledgeSource.MANUAL.value)
    knowledge_tool.store('S2', 'Desc', KnowledgeCategory.BEST_PRACTICE.value,
                          KnowledgeImportance.MEDIUM.value, KnowledgeSource.MANUAL.value)
    summary = knowledge_tool.summarize()
    assert summary['total_entries'] == 2
    assert 'by_category' in summary