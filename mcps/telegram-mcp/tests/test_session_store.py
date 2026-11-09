"""Tests for SessionStore."""

import os
import tempfile
import pytest
from session_store import SessionStore


@pytest.fixture
def store():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    s = SessionStore(db_path=path)
    yield s
    try:
        os.remove(path)
    except OSError:
        pass


def test_create_and_get_session(store):
    store.save_session(123, "ses_abc", "/home/test")
    session = store.get_session(123)
    assert session is not None
    assert session["chat_id"] == 123
    assert session["opencode_session_id"] == "ses_abc"
    assert session["directory"] == "/home/test"


def test_get_nonexistent_session(store):
    assert store.get_session(999) is None


def test_update_session(store):
    store.save_session(123, "ses_abc")
    store.save_session(123, "ses_xyz")
    session = store.get_session(123)
    assert session["opencode_session_id"] == "ses_xyz"


def test_delete_session(store):
    store.save_session(123, "ses_abc")
    store.delete_session(123)
    assert store.get_session(123) is None


def test_list_sessions(store):
    store.save_session(1, "ses_a")
    store.save_session(2, "ses_b")
    sessions = store.list_sessions()
    assert len(sessions) == 2


def test_task_processed(store):
    assert not store.is_processed(100)
    store.mark_processed(100, 123, status="completed")
    assert store.is_processed(100)


def test_pending_tasks(store):
    store.mark_processed(1, 123, status="pending")
    store.mark_processed(2, 123, status="completed")
    pending = store.get_pending_tasks(123)
    assert len(pending) == 1
    assert pending[0]["update_id"] == 1


def test_worker_state(store):
    assert store.get_state("last_update_id") is None
    store.set_state("last_update_id", "42")
    assert store.get_state("last_update_id") == "42"
    assert store.get_last_update_id() == 42


def test_last_update_id(store):
    store.set_last_update_id(100)
    assert store.get_last_update_id() == 100
    store.set_last_update_id(200)
    assert store.get_last_update_id() == 200
