"""Security tests for the Filesystem MCP path authorization.

Runs fully offline against /tmp fixtures. No network, no credentials.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main  # noqa: E402


@pytest.fixture()
def tmp():
    with tempfile.TemporaryDirectory(prefix="fs-mcp-test-") as d:
        yield d


# ---------- authorization matrix ----------

@pytest.mark.parametrize("path,expected", [
    ("/etc/passwd", False),
    ("/etc/shadow", False),
    ("/root/.bashrc", False),
    ("/var/log/syslog", False),
])
def test_system_paths_denied(path, expected):
    assert main.is_path_allowed(path)[0] is expected


def test_tmp_allowed():
    assert main.is_path_allowed("/tmp/something.txt")[0] is True


def test_home_allowed():
    assert main.is_path_allowed(os.path.expanduser("~/definitely-not-here-xyz.txt"))[0] is True


def test_traversal_escape_denied():
    assert main.is_path_allowed("/tmp/../etc/passwd")[0] is False
    assert main.is_path_allowed("/tmp/../../etc/shadow")[0] is False


def test_commonpath_prefix_bypass_denied():
    # '/tmp_evil_x' must NOT be considered inside '/tmp'
    assert main.is_path_allowed("/tmp_evil_x/file.txt")[0] is False
    assert main.is_path_allowed("/tmpx")[0] is False


def test_symlink_escape_denied(tmp):
    target = "/etc/passwd"
    link = os.path.join(tmp, "link-to-etc")
    os.symlink(target, link)
    assert main.is_path_allowed(link)[0] is False


def test_symlink_to_allowed_kept(tmp):
    real = os.path.join(tmp, "real.txt")
    Path(real).write_text("hello")
    link = os.path.join(tmp, "link-ok.txt")
    os.symlink(real, link)
    assert main.is_path_allowed(link)[0] is True


def test_relative_path_resolved(tmp):
    cwd = os.getcwd()
    os.chdir(tmp)
    try:
        assert main.is_path_allowed("./file.txt")[0] is True
        assert main.is_path_allowed("../file.txt")[0] is True
    finally:
        os.chdir(cwd)


@pytest.mark.parametrize("name", [
    "id_rsa", "id_ed25519", ".npmrc", ".netrc", ".git-credentials", "server.pem", "private.key",
])
def test_sensitive_basenames_denied(tmp, name):
    assert main.is_path_allowed(os.path.join(tmp, name))[0] is False


def test_env_denied_but_example_allowed(tmp):
    assert main.is_path_allowed(os.path.join(tmp, ".env"))[0] is False
    assert main.is_path_allowed(os.path.join(tmp, ".env.production"))[0] is False
    assert main.is_path_allowed(os.path.join(tmp, ".env.example"))[0] is True


def test_sensitive_dirs_denied(tmp):
    ssh = os.path.join(tmp, ".ssh", "config")
    Path(os.path.dirname(ssh)).mkdir(parents=True, exist_ok=True)
    Path(ssh).write_text("Host *")
    assert main.is_path_allowed(ssh)[0] is False


# ---------- functional behavior ----------

@pytest.mark.asyncio
async def test_write_read_roundtrip(tmp):
    target = os.path.join(tmp, "note.txt")
    w = await main.fs_write_file(target, "hola mundo")
    assert "error" not in w
    r = await main.fs_read_file(target)
    assert r["content"] == "hola mundo"


@pytest.mark.asyncio
async def test_read_outside_denied():
    r = await main.fs_read_file("/etc/passwd")
    assert "error" in r


@pytest.mark.asyncio
async def test_write_outside_denied():
    r = await main.fs_write_file("/etc/fs-mcp-pwned", "x")
    assert "error" in r


@pytest.mark.asyncio
async def test_delete_outside_denied():
    r = await main.fs_delete_file("/etc/passwd")
    assert "error" in r


@pytest.mark.asyncio
async def test_move_cross_boundary_denied(tmp):
    src = os.path.join(tmp, "a.txt")
    Path(src).write_text("data")
    r = await main.fs_move_file(src, "/etc/a.txt")
    assert "error" in r


@pytest.mark.asyncio
async def test_disk_usage_outside_denied():
    r = await main.fs_disk_usage("/etc")
    assert "error" in r


@pytest.mark.asyncio
async def test_chmod_validation(tmp):
    f = os.path.join(tmp, "perm.txt")
    Path(f).write_text("x")
    bad = await main.fs_chmod(f, "abc")
    assert "error" in bad
    good = await main.fs_chmod(f, "644")
    assert good.get("status") == "permissions changed"


@pytest.mark.asyncio
async def test_list_dir_cap(tmp):
    for i in range(1200):
        Path(os.path.join(tmp, f"f{i:04}.txt")).write_text("x")
    r = await main.fs_list_dir(tmp, pattern="f*.txt")
    assert r["count"] <= 1000
