"""Persistent Telegram worker for AI remote agent."""

import asyncio
import os
import logging
import signal
import sys
import time
import httpx
import json
from datetime import datetime

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS, REQUEST_TIMEOUT,
    TELEGRAM_MAX_MESSAGE_LENGTH, AI_MODEL_ID, AI_MODEL_PROVIDER,
    AI_FALLBACK_MODELS,
)
from session_store import SessionStore
from ai_client import AIClient
from task_manager import TaskManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("telegram_worker")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


class TelegramWorker:
    def __init__(self):
        self.store = SessionStore()
        self.ai = AIClient()
        self.task_manager = TaskManager(max_concurrent=3)
        self.running = False
        self.start_time = time.time()
        self._processing_chats = set()

    async def send_telegram(self, chat_id, text, parse_mode=None):
        """Send a message to Telegram, splitting if needed."""
        chunks = self._split_message(text)
        for chunk in chunks:
            payload = {"chat_id": chat_id, "text": chunk}
            if parse_mode:
                payload["parse_mode"] = parse_mode
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            except Exception as e:
                logger.error(f"Failed to send Telegram message: {e}")
            await asyncio.sleep(0.3)

    def _split_message(self, text):
        """Split long messages for Telegram's 4096 char limit."""
        if len(text) <= TELEGRAM_MAX_MESSAGE_LENGTH:
            return [text]
        chunks = []
        while text:
            if len(text) <= TELEGRAM_MAX_MESSAGE_LENGTH:
                chunks.append(text)
                break
            # Find a good split point
            split_at = text.rfind("\n", 0, TELEGRAM_MAX_MESSAGE_LENGTH)
            if split_at == -1:
                split_at = text.rfind(" ", 0, TELEGRAM_MAX_MESSAGE_LENGTH)
            if split_at == -1:
                split_at = TELEGRAM_MAX_MESSAGE_LENGTH
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip("\n")
        return chunks

    def _is_authorized(self, user_id):
        if not TELEGRAM_ALLOWED_USERS:
            return False  # Reject by default if no users configured
        return user_id in TELEGRAM_ALLOWED_USERS

    async def _handle_command(self, chat_id, user_id, text):
        """Handle bot commands."""
        cmd = text.split()[0].lower() if text else ""
        cmd = cmd.split("@")[0]  # Remove bot username

        if cmd == "/start":
            await self.send_telegram(chat_id, (
                "🤖 AI Remote Agent\n\n"
                "Tu computadora es ahora un servidor de agentes de IA.\n"
                "Envía cualquier instrucción y la IA la procesará.\n\n"
                "Comandos:\n"
                "/help - Ayuda\n"
                "/status - Estado del sistema\n"
                "/new - Nueva sesión\n"
                "/cancel - Cancelar tarea activa\n/mc - Controlar Minecraft\n\n"
                "Simplemente escribe tu instrucción y la IA trabajará en ella."
            ))
            return True

        if cmd == "/help":
            await self.send_telegram(chat_id, (
                "📋 Comandos disponibles:\n\n"
                "/start - Iniciar\n"
                "/help - Esta ayuda\n"
                "/status - Estado del sistema\n"
                "/new - Crear nueva sesión de IA\n"
                "/cancel - Cancelar generación activa\n\n"
                "Envía cualquier texto como instrucción para la IA."
            ))
            return True

        if cmd == "/status":
            await self._handle_status(chat_id)
            return True

        if cmd == "/new":
            await self._handle_new_session(chat_id)
            return True

        if cmd == "/cancel":
            await self._handle_cancel(chat_id)
            return True

        return False

    async def _handle_status(self, chat_id):
        """Show system status."""
        ai_ok, ai_info = await self.ai.health_check()
        uptime = time.time() - self.start_time
        hours, rem = divmod(int(uptime), 3600)
        mins, secs = divmod(rem, 60)

        sessions = self.store.list_sessions()
        active_tasks = self.task_manager.get_active_tasks()

        status_text = (
            f"📊 Estado del sistema\n\n"
            f"Worker: ✅ Activo\n"
            f"Uptime: {hours}h {mins}m {secs}s\n"
            f"AI Server: {'✅ Conectado' if ai_ok else '❌ Desconectado'}\n"
            f"Sesiones: {len(sessions)}\n"
            f"Tareas activas: {len(active_tasks)}\n"
            f"Usuarios autorizados: {len(TELEGRAM_ALLOWED_USERS)}\n"
        )
        await self.send_telegram(chat_id, status_text)

    async def _handle_new_session(self, chat_id):
        """Create a new AI session for this chat."""
        try:
            session = await self.ai.create_session(
                title=f"Telegram chat {chat_id}",
                directory=None,
            )
            session_id = session["id"]
            await self.ai.switch_model(session_id)
            self.store.save_session(chat_id, session_id)
            await self.send_telegram(chat_id, f"✅ Nueva sesión creada: {session_id}")
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            await self.send_telegram(chat_id, f"❌ Error creando sesión: {str(e)[:200]}")

    async def _handle_cancel(self, chat_id):
        """Cancel active generation."""
        session = self.store.get_session(chat_id)
        if session:
            sid = session.get("ai_session_id") or session.get("opencode_session_id")
            cancelled = await self.ai.interrupt(sid) if sid else False
            if cancelled:
                await self.send_telegram(chat_id, "🛑 Generación cancelada.")
            else:
                await self.send_telegram(chat_id, "No hay generación activa para cancelar.")
        else:
            await self.send_telegram(chat_id, "No hay sesión activa.")

    async def _process_message(self, chat_id, user_id, text, update_id):
        """Process a regular message through AI."""
        # Check if already processed
        if self.store.is_processed(update_id):
            logger.info(f"Update {update_id} already processed, skipping")
            return

        # Get or create session
        session = self.store.get_session(chat_id)
        if not session:
            try:
                ai_session = await self.ai.create_session(
                    title=f"Telegram chat {chat_id}",
                )
                session_id = ai_session["id"]
                await self.ai.switch_model(session_id)
                self.store.save_session(chat_id, session_id)
                session = {"ai_session_id": session_id}
            except Exception as e:
                await self.send_telegram(chat_id, f"❌ Error creando sesión: {str(e)[:200]}")
                self.store.mark_processed(update_id, chat_id, status="failed", result=str(e))
                return

        session_id = session.get("ai_session_id") or session.get("opencode_session_id")
        if not session_id:
            try:
                ai_session = await self.ai.create_session(title=f"Telegram chat {chat_id}")
                session_id = ai_session["id"]
                await self.ai.switch_model(session_id)
                self.store.save_session(chat_id, session_id)
            except Exception as e:
                await self.send_telegram(chat_id, f"❌ Error creando sesión: {str(e)[:200]}")
                self.store.mark_processed(update_id, chat_id, status="failed", result=str(e))
                return

        # Send "working" message
        await self.send_telegram(chat_id, "⏳ Trabajando en tu instrucción...")

        try:
            # Get current message count
            try:
                prev_msgs = await self.ai.get_messages(session_id)
                prev_count = len(prev_msgs)
            except Exception:
                prev_count = 0

            # Send prompt
            await self.ai.send_prompt(session_id, text)

            # Poll for progress and final response
            elapsed = 0
            poll_interval = 3
            sent_texts = set()
            final_response = None

            while True:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                try:
                    messages = await self.ai.get_messages(session_id)
                except Exception:
                    continue

                # New messages are at the top (newest first)
                new_count = len(messages) - prev_count
                if new_count <= 0:
                    # No new messages yet, keep waiting
                    if elapsed > 300:  # 5 min timeout for progress polling
                        break
                    continue

                new_messages = messages[:new_count]

                # Send any new assistant text or tool calls as progress
                for m in reversed(new_messages):  # oldest first
                    if m.get("type") == "assistant":
                        content_parts = m.get("content", [])
                        for c in content_parts:
                            if c.get("type") == "text":
                                text_content = c.get("text", "")
                                if text_content and text_content not in sent_texts:
                                    sent_texts.add(text_content)
                                    await self.send_telegram(chat_id, text_content)
                            elif c.get("type") == "tool":
                                tool_name = c.get("name", "unknown")
                                state = c.get("state", {})
                                status = state.get("status", "unknown")
                                tool_input = state.get("input", {})
                                
                                # Build detailed message
                                detail = ""
                                if tool_input:
                                    if "command" in tool_input:
                                        cmd = tool_input["command"]
                                        # Truncate long commands
                                        if len(cmd) > 150:
                                            cmd = cmd[:150] + "..."
                                        detail = f"`{cmd}`"
                                    elif "filePath" in tool_input:
                                        detail = f"`{tool_input['filePath']}`"
                                    elif "path" in tool_input:
                                        detail = f"`{tool_input['path']}`"
                                    elif "query" in tool_input:
                                        detail = f"`{tool_input['query']}`"
                                    elif "url" in tool_input:
                                        detail = f"`{tool_input['url']}`"
                                    else:
                                        # Show first key=value
                                        for k, v in list(tool_input.items())[:2]:
                                            val = str(v)
                                            if len(val) > 80:
                                                val = val[:80] + "..."
                                            detail += f"{k}={val} "
                                        detail = detail.strip()

                                if status == "running":
                                    msg = f"🔧 Ejecutando `{tool_name}`\n{detail}" if detail else f"🔧 Ejecutando `{tool_name}`..."
                                elif status == "completed":
                                    # Show output if available
                                    output = ""
                                    content_out = state.get("content", [])
                                    if content_out:
                                        for c_out in content_out:
                                            if c_out.get("type") == "text":
                                                output = c_out.get("text", "")[:200]
                                                break
                                    if output:
                                        msg = f"✅ `{tool_name}`\n```\n{output}\n```"
                                    else:
                                        msg = f"✅ `{tool_name}` {detail}"
                                elif status == "error":
                                    error = state.get("error", {})
                                    err_msg = error.get("message", "unknown error") if isinstance(error, dict) else str(error)
                                    msg = f"❌ `{tool_name}`: {err_msg[:100]}"
                                else:
                                    msg = f"🔧 `{tool_name}` ({status}) {detail}"
                                
                                if msg not in sent_texts:
                                    sent_texts.add(msg)
                                    await self.send_telegram(chat_id, msg, parse_mode="Markdown")

                # Check for completion
                for msg in new_messages:
                    if msg.get("type") == "idle":
                        outcome = msg.get("outcome", "")
                        if outcome == "succeeded":
                            # Get the last assistant message
                            for m in new_messages:
                                if m.get("type") == "assistant":
                                    content_parts = m.get("content", [])
                                    texts = [c.get("text", "") for c in content_parts if c.get("type") == "text"]
                                    if texts:
                                        final_response = "\n".join(texts)
                            if not final_response:
                                final_response = "(Sin respuesta)"
                            break
                        elif outcome == "failed":
                            error = msg.get("error", {})
                            if isinstance(error, dict):
                                err_type = str(error.get('type', ''))
                                err_msg = str(error.get('message', 'Unknown error'))
                            else:
                                err_type = ''
                                err_msg = str(error)
                            combined = (err_type + ' ' + err_msg).lower()
                            is_limit = any(k in combined for k in ['limit', 'free-limit', 'free usage', '429', 'quota'])
                            if is_limit:
                                # Try switching to fallback models
                                switched = False
                                for next_model in AI_FALLBACK_MODELS:
                                    try:
                                        await self.ai.switch_model(session_id, model_id=next_model)
                                        prev_msgs = await self.ai.get_messages(session_id)
                                        prev_count = len(prev_msgs)
                                        await self.ai.send_prompt(session_id, text)
                                        sent_texts = set()
                                        elapsed2 = 0
                                        final_response_local = None
                                        while elapsed2 < 600:
                                            await asyncio.sleep(poll_interval)
                                            elapsed2 += poll_interval
                                            try:
                                                messages2 = await self.ai.get_messages(session_id)
                                            except Exception:
                                                continue
                                            new2_count = len(messages2) - prev_count
                                            if new2_count <= 0:
                                                continue
                                            new2 = messages2[:new2_count]
                                            for m2 in new2:
                                                if m2.get("type") == "idle":
                                                    outcome2 = m2.get("outcome", "")
                                                    if outcome2 == "succeeded":
                                                        for m3 in new2:
                                                            if m3.get("type") == "assistant":
                                                                txt = [c.get("text", "") for c in m3.get("content", []) if c.get("type") == "text"]
                                                                if txt:
                                                                    final_response_local = "\n".join(txt)
                                                    elif outcome2 == "failed":
                                                        err2 = m2.get("error", {})
                                                        err2_msg = err2.get('message', '') if isinstance(err2, dict) else str(err2)
                                                        if any(k in err2_msg.lower() for k in ['limit', 'free', '429', 'quota']):
                                                            final_response_local = "SWITCH_NEXT"
                                                            break
                                            if final_response_local:
                                                break
                                        if final_response_local and final_response_local != "SWITCH_NEXT":
                                            final_response = final_response_local
                                            switched = True
                                            break
                                    except Exception:
                                        continue
                                if switched:
                                    break
                                final_response = "❌ Todos los modelos gratuitos alcanzaron su límite. Intenta más tarde."
                            else:
                                final_response = f"❌ Error: {err_msg[:300]}"
                            break
                        elif outcome == "interrupted":
                            final_response = "🛑 Generación interrumpida."
                            break

                if final_response is not None:
                    break

                # Safety: don't poll forever (30 min max)
                if elapsed > 1800:
                    final_response = "⏱ Timeout: la tarea tardó demasiado."
                    break

            self.store.touch_session(chat_id)
            if final_response and final_response not in sent_texts:
                await self.send_telegram(chat_id, final_response)
            self.store.mark_processed(update_id, chat_id, status="completed", result=(final_response or "")[:500])
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_telegram(chat_id, f"❌ Error: {str(e)[:300]}")
            self.store.mark_processed(update_id, chat_id, status="failed", result=str(e)[:500])

    async def _handle_update(self, update):
        """Handle a single Telegram update."""
        update_id = update.get("update_id")
        if update_id is None:
            return

        # Deduplication
        if self.store.is_processed(update_id):
            return

        message = update.get("message") or update.get("edited_message")
        if not message:
            # Handle callback queries, etc.
            return

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        user = message.get("from", {})
        user_id = user.get("id")
        text = message.get("text", "")

        if not chat_id or not user_id:
            return

        # Skip bot's own messages
        if user.get("is_bot"):
            return

        # Authorization check
        if not self._is_authorized(user_id):
            await self.send_telegram(chat_id, "⛔ No estás autorizado para usar este bot.")
            self.store.mark_processed(update_id, chat_id, status="rejected")
            return

        # Handle commands
        if text.startswith("/"):
            handled = await self._handle_command(chat_id, user_id, text)
            if handled:
                self.store.mark_processed(update_id, chat_id, status="completed")
                return

        # Process regular message
        if text:
            # Enqueue for ordered processing per chat
            async def process():
                await self._process_message(chat_id, user_id, text, update_id)

            await self.task_manager.enqueue(chat_id, process)
            # Process queue if not already processing
            if not self.task_manager.is_processing(chat_id):
                asyncio.create_task(self.task_manager.process_queue(chat_id))

    async def run(self):
        """Main worker loop."""
        self.running = True
        logger.info("Telegram worker starting...")

        # Verify AI connection
        ok, info = await self.ai.health_check()
        if ok:
            logger.info(f"AI server connected: {info}")
        else:
            logger.warning(f"AI server not reachable: {info}")

        last_update_id = self.store.get_last_update_id()

        while self.running:
            try:
                params = {"timeout": 30, "limit": 100}
                if last_update_id:
                    params["offset"] = last_update_id + 1

                async with httpx.AsyncClient(timeout=40) as client:
                    resp = await client.get(f"{TELEGRAM_API}/getUpdates", params=params)
                    data = resp.json()

                if not data.get("ok"):
                    logger.error(f"Telegram API error: {data}")
                    await asyncio.sleep(5)
                    continue

                updates = data.get("result", [])
                for update in updates:
                    last_update_id = update["update_id"]
                    self.store.set_last_update_id(last_update_id)
                    await self._handle_update(update)

            except httpx.TimeoutException:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self.running = False
        logger.info("Worker stopping...")


async def main():
    worker = TelegramWorker()

    # Handle signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    try:
        await worker.run()
    finally:
        await worker.ai.close()
        logger.info("Worker stopped.")


if __name__ == "__main__":
    asyncio.run(main())
