"""Tests for the Orchestrator SQLite store and role parsing. No network required."""
import os
import sys
import tempfile

fd, tmp_db = tempfile.mkstemp(suffix=".db", prefix="orchestra-test-")
os.close(fd)
os.environ["DATABASE_PATH"] = tmp_db
os.environ["AI_PASSWORD"] = "test-password"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import store  # noqa: E402
import main  # noqa: E402


def test_add_and_list_agents():
    aid = store.add_agent("testbot", "analyst", "session-123")
    agents = store.list_agents()
    assert any(a["id"] == aid for a in agents)
    agent = store.get_agent(aid)
    assert agent["name"] == "testbot" and agent["role"] == "analyst"


def test_delete_agent():
    aid = store.add_agent("temp", "coder", "session-xyz")
    store.delete_agent(aid)
    assert store.get_agent(aid) is None


def test_touch_agent_updates():
    aid = store.add_agent("touch", "writer", "session-touch")
    before = {a["id"]: a for a in store.list_agents()}[aid]["last_active"]
    store.touch_agent(aid)
    after = {a["id"]: a for a in store.list_agents()}[aid]["last_active"]
    assert after >= before


def test_blackboard_write_read_list_delete():
    store.blackboard_write("k1", "v1")
    store.blackboard_write("k2", "v2")
    assert store.blackboard_read("k1")["value"] == "v1"
    keys = [e["key"] for e in store.blackboard_list()]
    assert keys == ["k2", "k1"]  # most recent first
    store.blackboard_delete("k1")
    assert store.blackboard_read("k1") is None


def test_blackboard_upsert_overwrites():
    store.blackboard_write("dup", "first")
    store.blackboard_write("dup", "second")
    assert store.blackboard_read("dup")["value"] == "second"


def test_messages_log_and_filter():
    store.log_message("run-a", "worker-analyst", "analyst", "hello")
    store.log_message("run-b", "worker-coder", "coder", "world")
    all_msgs = store.get_messages(limit=10)
    assert any(m["content"] == "hello" for m in all_msgs)
    only_a = store.get_messages(limit=10, run_id="run-a")
    assert all(m["run_id"] == "run-a" for m in only_a)


def test_runs_lifecycle():
    run_id = store.create_run("test goal")
    store.finish_run(run_id, {"analyst": {"reply": "ok"}}, "done", "final answer")
    runs = store.list_runs(limit=5)
    match = [r for r in runs if r["id"] == run_id]
    assert match and match[0]["status"] == "done"


def test_parse_roles():
    assert main._parse_roles("researcher, coder ,reviewer") == ["researcher", "coder", "reviewer"]
    assert main._parse_roles("") == []
    assert main._parse_roles("a,,b") == ["a", "b"]


def test_worker_prompt_persona():
    p = main._worker_prompt("reviewer", "ship the feature")
    assert "reviewer" in p.lower() and "ship the feature" in p


def test_worker_prompt_unknown_role():
    p = main._worker_prompt("wizard", "do magic")
    assert "wizard" in p and "do magic" in p


def test_stats_shape():
    s = store.stats()
    assert set(s) == {"agents", "runs", "blackboard_entries", "messages"}
