"""Tests for cronparse.annotate."""
import pytest
from datetime import timezone

from cronparse.annotate import Annotation, AnnotationStore
from cronparse.exceptions import CronParseError

EXPR = "0 9 * * 1-5"
EXPR2 = "*/5 * * * *"


class TestAnnotationStore:
    def _make(self) -> AnnotationStore:
        return AnnotationStore()

    def test_add_returns_annotation_instance(self):
        store = self._make()
        result = store.add(EXPR, "Runs every weekday morning")
        assert isinstance(result, Annotation)

    def test_add_stores_note(self):
        store = self._make()
        store.add(EXPR, "Morning job")
        annotations = store.get(EXPR)
        assert len(annotations) == 1
        assert annotations[0].note == "Morning job"

    def test_add_strips_whitespace_from_note(self):
        store = self._make()
        store.add(EXPR, "  padded note  ")
        assert store.get(EXPR)[0].note == "padded note"

    def test_add_empty_note_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.add(EXPR, "")

    def test_add_whitespace_only_note_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.add(EXPR, "   ")

    def test_add_multiple_notes_same_expression(self):
        store = self._make()
        store.add(EXPR, "First note")
        store.add(EXPR, "Second note")
        assert len(store.get(EXPR)) == 2

    def test_get_unknown_expression_returns_empty_list(self):
        store = self._make()
        assert store.get("1 2 3 4 5") == []

    def test_remove_by_index(self):
        store = self._make()
        store.add(EXPR, "Keep me")
        store.add(EXPR, "Remove me")
        removed = store.remove(EXPR, 1)
        assert removed.note == "Remove me"
        assert len(store.get(EXPR)) == 1

    def test_remove_last_annotation_cleans_up_key(self):
        store = self._make()
        store.add(EXPR, "Only note")
        store.remove(EXPR, 0)
        assert EXPR not in store.all_expressions()

    def test_remove_invalid_index_raises(self):
        store = self._make()
        with pytest.raises(IndexError):
            store.remove(EXPR, 0)

    def test_all_expressions_lists_annotated(self):
        store = self._make()
        store.add(EXPR, "note a")
        store.add(EXPR2, "note b")
        assert set(store.all_expressions()) == {EXPR, EXPR2}

    def test_clear_removes_all_for_expression(self):
        store = self._make()
        store.add(EXPR, "n1")
        store.add(EXPR, "n2")
        count = store.clear(EXPR)
        assert count == 2
        assert store.get(EXPR) == []

    def test_total_counts_all_annotations(self):
        store = self._make()
        store.add(EXPR, "a")
        store.add(EXPR, "b")
        store.add(EXPR2, "c")
        assert store.total() == 3

    def test_annotation_str_contains_expression_and_note(self):
        store = self._make()
        ann = store.add(EXPR, "My note")
        s = str(ann)
        assert EXPR in s
        assert "My note" in s
        assert "UTC" in s

    def test_annotation_created_at_is_utc(self):
        store = self._make()
        ann = store.add(EXPR, "timezone check")
        assert ann.created_at.tzinfo == timezone.utc
