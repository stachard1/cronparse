"""Tests for cronparse.lock and cronparse.lock_export."""
import json
import pytest

from cronparse.exceptions import CronParseError
from cronparse.lock import LockConflictError, LockEntry, LockStore
from cronparse.lock_export import from_json, to_json, to_text

EXPR = "0 9 * * 1"
EXPR2 = "*/5 * * * *"


class TestLockStore:
    def _make(self) -> LockStore:
        return LockStore()

    def test_acquire_returns_lock_entry(self):
        store = self._make()
        entry = store.acquire(EXPR, owner="alice")
        assert isinstance(entry, LockEntry)

    def test_acquire_stores_entry(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        assert store.is_locked(EXPR)

    def test_acquire_with_note(self):
        store = self._make()
        entry = store.acquire(EXPR, owner="alice", note="deploy freeze")
        assert entry.note == "deploy freeze"

    def test_acquire_invalid_expression_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.acquire("bad expr", owner="alice")

    def test_acquire_same_owner_reacquires(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        entry = store.acquire(EXPR, owner="alice")
        assert entry.owner == "alice"

    def test_acquire_different_owner_raises(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        with pytest.raises(LockConflictError):
            store.acquire(EXPR, owner="bob")

    def test_release_returns_true_when_held(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        assert store.release(EXPR, owner="alice") is True
        assert not store.is_locked(EXPR)

    def test_release_returns_false_when_not_held(self):
        store = self._make()
        assert store.release(EXPR, owner="alice") is False

    def test_release_wrong_owner_raises(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        with pytest.raises(LockConflictError):
            store.release(EXPR, owner="bob")

    def test_get_returns_entry(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        entry = store.get(EXPR)
        assert entry is not None and entry.owner == "alice"

    def test_get_missing_returns_none(self):
        store = self._make()
        assert store.get(EXPR) is None

    def test_all_returns_all_entries(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        store.acquire(EXPR2, owner="bob")
        assert len(store.all()) == 2

    def test_held_by_filters_by_owner(self):
        store = self._make()
        store.acquire(EXPR, owner="alice")
        store.acquire(EXPR2, owner="bob")
        assert len(store.held_by("alice")) == 1
        assert store.held_by("alice")[0].expression == EXPR


class TestLockExport:
    def _make(self) -> LockStore:
        store = LockStore()
        store.acquire(EXPR, owner="alice", note="freeze")
        store.acquire(EXPR2, owner="bob")
        return store

    def test_to_json_returns_string(self):
        assert isinstance(to_json(self._make()), str)

    def test_to_json_is_valid_json(self):
        data = json.loads(to_json(self._make()))
        assert isinstance(data, list)

    def test_to_json_entry_count(self):
        data = json.loads(to_json(self._make()))
        assert len(data) == 2

    def test_to_json_required_keys(self):
        data = json.loads(to_json(self._make()))
        for row in data:
            for key in ("expression", "owner", "acquired_at", "note"):
                assert key in row

    def test_from_json_round_trip(self):
        original = self._make()
        restored = from_json(to_json(original))
        expressions = {e.expression for e in restored.all()}
        assert EXPR in expressions and EXPR2 in expressions

    def test_to_text_no_locks(self):
        assert to_text(LockStore()) == "No active locks."

    def test_to_text_with_locks(self):
        text = to_text(self._make())
        assert EXPR in text
        assert "alice" in text
