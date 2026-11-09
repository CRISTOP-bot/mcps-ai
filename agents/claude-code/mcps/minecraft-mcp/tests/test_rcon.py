"""Tests for RCON client."""

import socket
import struct
import threading
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rcon import RCONClient

RCON_PASSWORD = "testpass123"


def start_mock_server():
    """Start a mock RCON server for testing."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 25599))
    server.listen(5)

    def handle(conn):
        data = conn.recv(4096)
        if len(data) < 12:
            conn.close()
            return
        length = struct.unpack("<i", data[:4])[0]
        req_id = struct.unpack("<i", data[4:8])[0]
        cmd_type = struct.unpack("<i", data[8:12])[0]
        payload = data[12:12+length-10].decode("utf-8", errors="replace").rstrip("\x00")

        if cmd_type == 3:
            if payload == RCON_PASSWORD:
                conn.sendall(struct.pack("<iii", 10, req_id, 0) + b"\x00\x00")
            else:
                conn.sendall(struct.pack("<iii", 10, -1, 0) + b"\x00\x00")
                conn.close()
                return

        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                length = struct.unpack("<i", data[:4])[0]
                req_id = struct.unpack("<i", data[4:8])[0]
                payload = data[12:12+length-10].decode("utf-8", errors="replace").rstrip("\x00")
                response = f"OK: {payload}"
                resp_data = response.encode("utf-8") + b"\x00\x00"
                resp = struct.pack("<iii", len(resp_data) + 8, req_id, 0) + resp_data
                conn.sendall(resp)
            except Exception:
                break
        conn.close()

    def accept_loop():
        while True:
            try:
                conn, _ = server.accept()
                threading.Thread(target=handle, args=(conn,), daemon=True).start()
            except Exception:
                break

    threading.Thread(target=accept_loop, daemon=True).start()
    return server


@pytest.fixture(scope="module")
def mock_server():
    server = start_mock_server()
    yield server
    server.close()


def test_connect(mock_server):
    rcon = RCONClient("127.0.0.1", 25599, RCON_PASSWORD)
    rcon.connect()
    assert rcon.sock is not None
    rcon.close()


def test_wrong_password(mock_server):
    rcon = RCONClient("127.0.0.1", 25599, "wrongpassword")
    with pytest.raises(ConnectionError):
        rcon.connect()


def test_command(mock_server):
    rcon = RCONClient("127.0.0.1", 25599, RCON_PASSWORD)
    rcon.connect()
    result = rcon.command("list")
    assert "OK: list" in result
    rcon.close()


def test_context_manager(mock_server):
    with RCONClient("127.0.0.1", 25599, RCON_PASSWORD) as rcon:
        result = rcon.command("say hello")
        assert "OK: say hello" in result
