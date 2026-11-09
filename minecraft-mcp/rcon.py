"""RCON client for Minecraft server communication."""

import socket
import struct
import threading

RCON_LOGIN = 3
RCON_COMMAND = 2
RCON_RESPONSE = 0


class RCONClient:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.sock = None
        self._lock = threading.Lock()
        self._request_id = 0

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.host, self.port))
        # Login
        resp = self._send(RCON_LOGIN, self.password)
        if resp is None:
            raise ConnectionError("RCON login failed")
        return True

    def _next_id(self):
        self._request_id += 1
        return self._request_id

    def _send(self, cmd_type, payload):
        with self._lock:
            req_id = self._next_id()
            # Build packet: length (4) + request_id (4) + type (4) + payload + 2 null bytes
            packet = struct.pack("<iii", len(payload) + 10, req_id, cmd_type) + payload.encode("utf-8") + b"\x00\x00"
            self.sock.sendall(packet)

            # Read response
            data = b""
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Check if we have a complete response
                if len(data) >= 4:
                    length = struct.unpack("<i", data[:4])[0]
                    if len(data) >= 4 + length:
                        break

            if len(data) < 12:
                return None

            resp_id = struct.unpack("<i", data[4:8])[0]
            resp_type = struct.unpack("<i", data[8:12])[0]
            # Payload is between byte 12 and the last 2 null bytes
            payload_data = data[12:-2] if len(data) > 14 else b""
            try:
                text = payload_data.decode("utf-8", errors="replace")
            except Exception:
                text = str(payload_data)
            return text

    def command(self, cmd):
        """Send a command and return the response."""
        if self.sock is None:
            self.connect()
        try:
            return self._send(RCON_COMMAND, cmd)
        except Exception as e:
            # Reconnect
            try:
                self.connect()
                return self._send(RCON_COMMAND, cmd)
            except Exception:
                raise ConnectionError(f"RCON error: {e}")

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()
