"""Tests for OpenCodeClient."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from opencode_client import OpenCodeClient


@pytest.fixture
def client():
    return OpenCodeClient(base_url="http://127.0.0.1:49374", password="test", timeout=10)


@pytest.mark.asyncio
async def test_health_check_success(client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok"}
    with patch.object(client, "_get_client") as mock_gc:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_resp)
        mock_gc.return_value = mock_http
        ok, info = await client.health_check()
        assert ok is True


@pytest.mark.asyncio
async def test_health_check_failure(client):
    with patch.object(client, "_get_client") as mock_gc:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_gc.return_value = mock_http
        ok, info = await client.health_check()
        assert ok is False


@pytest.mark.asyncio
async def test_create_session(client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"id": "ses_123", "title": "Test"}}
    mock_resp.raise_for_status = MagicMock()
    with patch.object(client, "_get_client") as mock_gc:
        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_resp)
        mock_gc.return_value = mock_http
        session = await client.create_session(title="Test")
        assert session["id"] == "ses_123"


@pytest.mark.asyncio
async def test_send_prompt(client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"id": "msg_1", "type": "user"}}
    mock_resp.raise_for_status = MagicMock()
    with patch.object(client, "_get_client") as mock_gc:
        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_resp)
        mock_gc.return_value = mock_http
        msg = await client.send_prompt("ses_123", "Hello")
        assert msg["type"] == "user"


@pytest.mark.asyncio
async def test_interrupt(client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch.object(client, "_get_client") as mock_gc:
        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_resp)
        mock_gc.return_value = mock_http
        result = await client.interrupt("ses_123")
        assert result is True
