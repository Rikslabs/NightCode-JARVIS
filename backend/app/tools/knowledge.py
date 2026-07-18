import json
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime, timezone
import uuid


class KnowledgeCategory(Enum):
    ARCHITECTURE_DECISION = 'architecture_decision'
    CODING_CONVENTION = 'coding_convention'
    ENGINEERING_RULE = 'engineering_rule'
    BUG_PATTERN = 'bug_pattern'
    BUG_RESOLUTION = 'bug_resolution'
    REFACTORING_PATTERN = 'refactoring_pattern'
    BEST_PRACTICE = 'best_practice'
    PROJECT_GUIDELINE = 'project_guideline'
    TESTING_STRATEGY = 'testing_strategy'
    PERFORMANCE_OBSERVATION = 'performance_observation'
    SECURITY_OBSERVATION = 'security_observation'
    REVIEW_RESOLUTION = 'review_resolution'
    FEATURE_DECISION = 'feature_decision'
    DEPENDENCY_NOTE = 'dependency_note'


class KnowledgeImportance(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class KnowledgeSource(Enum):
    REVIEW = 'review'
    PLAN = 'plan'
    MANUAL = 'manual'
    OBSERVATION = 'observation'
    EXTERNAL = 'external'


@dataclass
class KnowledgeEntry:
    title: str
    description: str
    category: KnowledgeCategory
    importance: KnowledgeImportance
    source: KnowledgeSource
    project: str = ''
    tags: list[str] = field(default_factory=list)
    related_entries: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    archived: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'importance': self.importance.value,
            'source': self.source.value,
            'project': self.project,
            'tags': list(self.tags),
            'related_entries': list(self.related_entries),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'archived': self.archived,
        }


class KnowledgeCollection:
    """In-memory knowledge base with indexing."""

    def __init__(self):
        self._entries: dict[str, KnowledgeEntry] = {}
        self._index_by_category: dict[str, list[str]] = {}
        self._index_by_project: dict[str, list[str]] = {}
        self._index_by_tag: dict[str, list[str]] = {}
        self._index_by_importance: dict[str, list[str]] = {}

    def add(self, entry: KnowledgeEntry) -> str:
        self._entries[entry.id] = entry
        self._index(entry)
        return entry.id

    def update(self, entry_id: str, updates: dict[str, Any]) -> bool:
        if entry_id not in self._entries:
            return False
        entry = self._entries[entry_id]
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.now(timezone.utc).isoformat()
        self._rebuild_index(entry_id)
        return True

    def archive(self, entry_id: str) -> bool:
        if entry_id not in self._entries:
            return False
        self._entries[entry_id].archived = True
        self._entries[entry_id].updated_at = datetime.now(timezone.utc).isoformat()
        return True

    def delete(self, entry_id: str) -> bool:
        if entry_id not in self._entries:
            return False
        entry = self._entries.pop(entry_id)
        self._remove_from_index(entry)
        return True

    def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        return self._entries.get(entry_id)

    def search(self, query: str = '', category: Optional[str] = None, tag: Optional[str] = None,
               project: Optional[str] = None, importance: Optional[str] = None,
               source: Optional[str] = None, include_archived: bool = False) -> list[KnowledgeEntry]:
        results = list(self._entries.values())
        if not include_archived:
            results = [e for e in results if not e.archived]
        if category:
            results = [e for e in results if e.category.value == category]
        if tag:
            results = [e for e in results if tag in e.tags]
        if project:
            results = [e for e in results if e.project == project]
        if importance:
            results = [e for e in results if e.importance.value == importance]
        if source:
            results = [e for e in results if e.source.value == source]
        if query:
            q = query.lower()
            results = [e for e in results if q in e.title.lower() or q in e.description.lower()]
        return results

    def list_by_category(self, category: str) -> list[KnowledgeEntry]:
        ids = self._index_by_category.get(category, [])
        return [self._entries[i] for i in ids if i in self._entries and not self._entries[i].archived]

    def list_by_project(self, project: str) -> list[KnowledgeEntry]:
        ids = self._index_by_project.get(project, [])
        return [self._entries[i] for i in ids if i in self._entries and not self._entries[i].archived]

    def related_entries(self, entry_id: str) -> list[KnowledgeEntry]:
        entry = self._entries.get(entry_id)
        if not entry:
            return []
        related = []
        for rel_id in entry.related_entries:
            rel = self._entries.get(rel_id)
            if rel and not rel.archived:
                related.append(rel)
        return related

    def export(self) -> dict[str, Any]:
        return {
            'entries': [e.to_dict() for e in self._entries.values() if not e.archived],
            'count': sum(1 for e in self._entries.values() if not e.archived),
        }

    def import_entries(self, data: dict[str, Any]) -> int:
        imported = 0
        for entry_data in data.get('entries', []):
            try:
                entry = KnowledgeEntry(
                    title=entry_data['title'],
                    description=entry_data['description'],
                    category=KnowledgeCategory(entry_data['category']),
                    importance=KnowledgeImportance(entry_data['importance']),
                    source=KnowledgeSource(entry_data['source']),
                    project=entry_data.get('project', ''),
                    tags=entry_data.get('tags', []),
                    related_entries=entry_data.get('related_entries', []),
                    id=entry_data.get('id', str(uuid.uuid4())),
                    created_at=entry_data.get('created_at', datetime.now(timezone.utc).isoformat()),
                    updated_at=entry_data.get('updated_at', datetime.now(timezone.utc).isoformat()),
                    archived=entry_data.get('archived', False),
                )
                self.add(entry)
                imported += 1
            except Exception:
                continue
        return imported

    def summarize(self) -> dict[str, Any]:
        active = [e for e in self._entries.values() if not e.archived]
        by_category = {}
        by_importance = {}
        by_source = {}
        for e in active:
            by_category[e.category.value] = by_category.get(e.category.value, 0) + 1
            by_importance[e.importance.value] = by_importance.get(e.importance.value, 0) + 1
            by_source[e.source.value] = by_source.get(e.source.value, 0) + 1
        return {
            'total_entries': len(active),
            'by_category': by_category,
            'by_importance': by_importance,
            'by_source': by_source,
        }

    def _index(self, entry: KnowledgeEntry) -> None:
        self._index_by_category.setdefault(entry.category.value, []).append(entry.id)
        if entry.project:
            self._index_by_project.setdefault(entry.project, []).append(entry.id)
        for tag in entry.tags:
            self._index_by_tag.setdefault(tag, []).append(entry.id)
        self._index_by_importance.setdefault(entry.importance.value, []).append(entry.id)

    def _rebuild_index(self, entry_id: str) -> None:
        if entry_id in self._entries:
            self._remove_from_index(self._entries[entry_id])
            self._index(self._entries[entry_id])

    def _remove_from_index(self, entry: KnowledgeEntry) -> None:
        self._index_by_category.get(entry.category.value, []).remove(entry.id)
        if entry.project and entry.id in self._index_by_project.get(entry.project, []):
            self._index_by_project[entry.project].remove(entry.id)
        for tag in entry.tags:
            if entry.id in self._index_by_tag.get(tag, []):
                self._index_by_tag[tag].remove(entry.id)
        if entry.id in self._index_by_importance.get(entry.importance.value, []):
            self._index_by_importance[entry.importance.value].remove(entry.id)


class KnowledgeTool:
    """Read-only engineering memory and knowledge engine."""

    def __init__(self):
        self._collection = KnowledgeCollection()

    def store(self, title: str, description: str, category: str, importance: str, source: str,
              project: str = '', tags: list[str] = None, related_entries: list[str] = None) -> dict[str, Any]:
        try:
            entry = KnowledgeEntry(
                title=title,
                description=description,
                category=KnowledgeCategory(category),
                importance=KnowledgeImportance(importance),
                source=KnowledgeSource(source),
                project=project,
                tags=tags or [],
                related_entries=related_entries or [],
            )
            entry_id = self._collection.add(entry)
            return {'success': True, 'id': entry_id}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update(self, entry_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        success = self._collection.update(entry_id, updates)
        return {'success': success, 'updated': success}

    def archive(self, entry_id: str) -> dict[str, Any]:
        success = self._collection.archive(entry_id)
        return {'success': success, 'archived': success}

    def delete(self, entry_id: str) -> dict[str, Any]:
        success = self._collection.delete(entry_id)
        return {'success': success, 'deleted': success}

    def find(self, entry_id: str) -> dict[str, Any]:
        entry = self._collection.get(entry_id)
        if not entry:
            return {'success': False, 'error': 'Entry not found'}
        return {'success': True, 'entry': entry.to_dict()}

    def search(self, query: str = '', category: Optional[str] = None, tag: Optional[str] = None,
               project: Optional[str] = None, importance: Optional[str] = None,
               source: Optional[str] = None, include_archived: bool = False) -> dict[str, Any]:
        results = self._collection.search(query, category, tag, project, importance, source, include_archived)
        return {'success': True, 'entries': [e.to_dict() for e in results], 'count': len(results)}

    def filter(self, category: Optional[str] = None, project: Optional[str] = None,
               importance: Optional[str] = None, source: Optional[str] = None) -> dict[str, Any]:
        results = self._collection.search(category=category, project=project, importance=importance, source=source)
        return {'success': True, 'entries': [e.to_dict() for e in results], 'count': len(results)}

    def list_by_category(self, category: str) -> dict[str, Any]:
        results = self._collection.list_by_category(category)
        return {'success': True, 'entries': [e.to_dict() for e in results], 'count': len(results)}

    def list_by_project(self, project: str) -> dict[str, Any]:
        results = self._collection.list_by_project(project)
        return {'success': True, 'entries': [e.to_dict() for e in results], 'count': len(results)}

    def related_entries(self, entry_id: str) -> dict[str, Any]:
        results = self._collection.related_entries(entry_id)
        return {'success': True, 'entries': [e.to_dict() for e in results], 'count': len(results)}

    def export(self) -> dict[str, Any]:
        return self._collection.export()

    def import_entries(self, data: dict[str, Any]) -> dict[str, Any]:
        count = self._collection.import_entries(data)
        return {'success': True, 'imported': count}

    def summarize(self) -> dict[str, Any]:
        return self._collection.summarize()