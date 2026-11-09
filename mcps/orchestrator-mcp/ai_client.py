"""Async HTTP client for the OpenCode Server API (used by Telegram worker and Orchestrator)."""
import os
import httpx
import asyncio
import logging

from config import (
    AI_BASE_URL, AI_PASSWORD, AI_AUTH_USER, AI_DIRECTORY, REQUEST_TIMEOUT,
    AI_MODEL_ID, AI_MODEL_PROVIDER, FALLBACK_MODELS,
)

logger = logging.getLogger("orchestrator.ai_client")


class AIClient:
    """Client for communicating with the OpenCode AI Server."""

    def __init__(self, base_url=None, password=None, timeout=None):
        self.base_url = (base_url or AI_BASE_URL).rstrip("/")
        self.password = password or AI_PASSWORD
        self.timeout = REQUEST_TIMEOUT if timeout is None else timeout
        self._client = None

    def _get_client(self):
        if self._client is None or self._client.is_closed:
            auth = (AI_AUTH_USER, self.password) if self.password else None
            if self.timeout and self.timeout > 0:
                timeout_config = httpx.Timeout(self.timeout, connect=10.0)
            else:
                timeout_config = httpx.Timeout(None, connect=10.0)
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                auth=auth,
                timeout=timeout_config,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def health_check(self):
        client = self._get_client()
        try:
            resp = await client.get("/api/info")
            data = resp.json() if resp.status_code == 200 else None
            return resp.status_code == 200, data
        except Exception as e:
            return False, str(e)

    async def create_session(self, title=None, directory=None):
        client = self._get_client()
        payload = {}
        if title:
            payload["title"] = title
        payload["directory"] = directory or AI_DIRECTORY
        resp = await client.post("/api/session", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data)

    async def get_session(self, session_id):
        client = self._get_client()
        resp = await client.get(f"/api/session/{session_id}")
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data)

    async def delete_session(self, session_id):
        client = self._get_client()
        try:
            resp = await client.delete(f"/api/session/{session_id}")
            return resp.status_code in (200, 204)
        except Exception:
            return False

    async def switch_model(self, session_id, model_id=None, provider_id=None):
        client = self._get_client()
        model_id = model_id or AI_MODEL_ID
        provider_id = provider_id or AI_MODEL_PROVIDER
        resp = await client.post(
            f"/api/session/{session_id}/model",
            json={"model": {"id": model_id, "providerID": provider_id}},
        )
        return resp.status_code in (200, 204)

    async def send_prompt(self, session_id, text):
        client = self._get_client()
        resp = await client.post(
            f"/api/session/{session_id}/prompt",
            json={"text": text},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data)

    async def get_messages(self, session_id):
        client = self._get_client()
        resp = await client.get(f"/api/session/{session_id}/message",
                                params={"limit": "200", "order": "desc"})
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def wait_for_completion(self, session_id, timeout=None, poll_interval=2, prev_count=0):
        """Poll until the session finishes its current generation. Returns the assistant text."""
        if timeout is None:
            timeout = self.timeout
        if timeout == 0:
            timeout = None
        client = self._get_client()
        elapsed = 0
        while timeout is None or elapsed < timeout:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            try:
                messages = await self.get_messages(session_id)
            except Exception:
                continue

            new_count = len(messages) - prev_count
            if new_count > 0 and new_count <= len(messages):
                new_messages = messages[:new_count]
            else:
                new_messages = []

            for msg in new_messages:
                if msg.get("type") == "idle":
                    outcome = msg.get("outcome", "")
                    if outcome == "succeeded":
                        for m in new_messages:
                            if m.get("type") == "assistant":
                                content = m.get("content", [])
                                texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                                if texts:
                                    return "\n".join(texts)
                    elif outcome == "failed":
                        error = msg.get("error", {})
                        return f"Error: {error.get('message', 'Unknown error')}"
                    elif outcome == "interrupted":
                        return "Generation was interrupted."

            for m in new_messages:
                if m.get("type") == "assistant" and m.get("finish"):
                    finish = m.get("finish")
                    if finish == "error":
                        error = m.get("error", {})
                        return f"Error: {error.get('message', 'Unknown error')}"
                    content = m.get("content", [])
                    texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                    if texts:
                        return "\n".join(texts)

        return "Timeout: AI did not respond within the time limit."

    async def interrupt(self, session_id):
        client = self._get_client()
        try:
            resp = await client.post(f"/api/session/{session_id}/interrupt")
            return resp.status_code in (200, 204)
        except Exception:
            return False

    async def full_request(self, session_id, text, timeout=None):
        """Send a prompt and wait for the complete response. Falls back to the next free model on quota limits."""
        try:
            prev_msgs = await self.get_messages(session_id)
            prev_count = len(prev_msgs)
        except Exception:
            prev_count = 0

        models = [AI_MODEL_ID] + [m for m in FALLBACK_MODELS if m != AI_MODEL_ID]
        last_error = None
        for attempt, model in enumerate(models):
            try:
                await self.switch_model(session_id, model_id=model)
                await self.send_prompt(session_id, text)
                result = await self.wait_for_completion(session_id, timeout=timeout, prev_count=prev_count)

                limit_signals = ("limit", "429", "free usage", "free-limit", "quota")
                if result and any(s in result.lower() for s in limit_signals):
                    raise Exception(result)
                return result
            except Exception as e:
                error_str = str(e).lower()
                last_error = e
                if any(s in error_str for s in ("limit", "429", "free usage", "quota", "token")):
                    logger.warning("Model %s hit a quota limit, switching to next model", model)
                    continue
                return f"Error: {e}"
        return f"Error: all models exhausted ({last_error})"
