"""Async HTTP client for AI Server API."""

import os

import httpx
import asyncio
from config import (
    AI_BASE_URL, AI_PASSWORD, REQUEST_TIMEOUT,
    AI_MODEL_ID, AI_MODEL_PROVIDER, AI_DIRECTORY,
)


class AIClient:
    """Client for communicating with AI Server."""

    def __init__(self, base_url=None, password=None, timeout=None):
        self.base_url = (base_url or AI_BASE_URL).rstrip("/")
        self.password = password or AI_PASSWORD
        self.timeout = timeout if timeout is not None else REQUEST_TIMEOUT
        self._client = None

    def _get_client(self):
        if self._client is None or self._client.is_closed:
            auth = (os.getenv("AI_AUTH_USER", "opencode"), self.password) if self.password else None
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
        """Check if AI server is reachable."""
        try:
            client = self._get_client()
            resp = await client.get("/api/info")
            return resp.status_code == 200, resp.json() if resp.status_code == 200 else None
        except Exception as e:
            return False, str(e)

    async def create_session(self, title=None, directory=None):
        """Create a new AI session."""
        client = self._get_client()
        payload = {}
        if title:
            payload["title"] = title
        if directory:
            payload["directory"] = directory
        elif AI_DIRECTORY:
            payload["directory"] = AI_DIRECTORY

        resp = await client.post("/api/session", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data)

    async def get_session(self, session_id):
        """Get session info."""
        client = self._get_client()
        resp = await client.get(f"/api/session/{session_id}")
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data)

    async def delete_session(self, session_id):
        """Delete a session."""
        client = self._get_client()
        resp = await client.delete(f"/api/session/{session_id}")
        return resp.status_code in (200, 204)

    async def switch_model(self, session_id, model_id=None, provider_id=None):
        """Switch the model for a session."""
        client = self._get_client()
        model_id = model_id or AI_MODEL_ID
        provider_id = provider_id or AI_MODEL_PROVIDER
        resp = await client.post(
            f"/api/session/{session_id}/model",
            json={"model": {"id": model_id, "providerID": provider_id}},
        )
        return resp.status_code in (200, 204)

    async def send_prompt(self, session_id, text):
        """Send a prompt to a session. Returns the user message info."""
        client = self._get_client()
        resp = await client.post(
            f"/api/session/{session_id}/prompt",
            json={"text": text},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data)

    async def get_messages(self, session_id):
        """Get all messages in a session."""
        client = self._get_client()
        resp = await client.get(f"/api/session/{session_id}/message")
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def wait_for_completion(self, session_id, timeout=None, poll_interval=2, prev_count=0):
        """Wait for the session to finish processing. Returns the assistant response text."""
        if timeout is None:
            timeout = self.timeout
        # 0 means no timeout
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

            # Messages come in reverse chronological order (newest first)
            # New messages are at the top (first N where N = total - prev_count)
            new_count = len(messages) - prev_count
            if new_count > 0 and new_count <= len(messages):
                new_messages = messages[:new_count]
            else:
                new_messages = []

            # Check for idle/completion message in new messages
            for msg in new_messages:
                if msg.get("type") == "idle":
                    outcome = msg.get("outcome", "")
                    if outcome == "succeeded":
                        # Find the first NEW assistant message with text (newest first)
                        found_text = None
                        for m in new_messages:
                            if m.get("type") == "assistant":
                                content = m.get("content", [])
                                texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                                if texts:
                                    found_text = "\n".join(texts)
                                    break
                        if found_text:
                            return found_text
                        # If no new assistant text yet, keep polling (don't return stale response)
                        # Fall through to continue the loop
                    elif outcome == "failed":
                        error = msg.get("error", {})
                        return f"Error: {error.get('message', 'Unknown error')}"
                    elif outcome == "interrupted":
                        return "Generation was interrupted."

            # Also check for assistant message with finish != None in new messages
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
        """Interrupt/cancel the current generation."""
        client = self._get_client()
        try:
            resp = await client.post(f"/api/session/{session_id}/interrupt")
            return resp.status_code in (200, 204)
        except Exception:
            return False

    async def full_request(self, session_id, text, timeout=None):
        """Send a prompt and wait for the complete response."""
        # Get current message count before sending
        # Messages come in reverse chronological order (newest first), so reverse them
        try:
            prev_msgs = await self.get_messages(session_id)
            prev_count = len(prev_msgs)
        except Exception:
            prev_count = 0
        from config import AI_FALLBACK_MODELS

        # Try sending with current model, fallback on token/usage limit
        max_retries = len(AI_FALLBACK_MODELS)
        for attempt in range(max_retries):
            try:
                await self.send_prompt(session_id, text)
                result = await self.wait_for_completion(session_id, timeout=timeout, prev_count=prev_count)

                # Check if result indicates a token/usage limit error
                if result and ("limit" in result.lower() or "token" in result.lower() or "429" in result or "free usage" in result.lower()):
                    raise Exception(result)

                return result

            except Exception as e:
                error_str = str(e).lower()
                if "limit" in error_str or "token" in error_str or "429" in error_str or "free usage" in error_str or "free-limit" in error_str:
                    next_model_idx = attempt + 1
                    if next_model_idx < len(AI_FALLBACK_MODELS):
                        next_model = AI_FALLBACK_MODELS[next_model_idx]
                        try:
                            await self.switch_model(session_id, model_id=next_model)
                            # Reset prev_count after model switch
                            try:
                                prev_msgs = await self.get_messages(session_id)
                                prev_count = len(prev_msgs)
                            except Exception:
                                pass
                            continue
                        except Exception:
                            pass
                    return f"Error: Todos los modelos alcanzaron su limite. Intenta mas tarde. ({str(e)[:200]})"
                else:
                    return f"Error: {str(e)[:300]}"

        return "Error: No se pudo procesar la solicitud."
