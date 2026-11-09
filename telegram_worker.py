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
                "/cancel - Cancelar tarea activa\n\n"
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

        if cmd == "/mc":
            await self._handle_mc_command(chat_id, text)
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
            cancelled = await self.ai.interrupt(session["ai_session_id"])
            if cancelled:
                await self.send_telegram(chat_id, "🛑 Generación cancelada.")
            else:
                await self.send_telegram(chat_id, "No hay generación activa para cancelar.")
        else:
            await self.send_telegram(chat_id, "No hay sesión activa.")

    async def _handle_mc_command(self, chat_id, text):
        """Handle Minecraft commands via Telegram."""
        parts = text.split()
        if len(parts) < 2:
            await self.send_telegram(chat_id, (
                "🎮 Comandos de Minecraft:\n\n"
                "/mc status - Estado del servidor\n"
                "/mc players - Jugadores online\n"
                "/mc say <mensaje> - Enviar mensaje al chat\n"
                "/mc give <jugador> <item> [cantidad] - Dar item\n"
                "/mc tp <jugador> <x> <y> <z> - Teletransportar\n"
                "/mc weather <clear|rain|thunder> - Clima\n"
                "/mc time <day|night|noon|midnight> - Hora\n"
                "/mc gamemode <jugador> <modo> - Modo de juego\n"
                "/mc difficulty <peaceful|easy|normal|hard> - Dificultad\n"
                "/mc summon <entidad> [x y z] - Invocar entidad\n"
                "/mc effect <jugador> <efecto> [duración] - Efecto de poción\n"
                "/mc locate <estructura> - Localizar estructura\n"
                "/mc cmd <comando> - Comando raw\n\n"
                "O simplemente escribe lo que quieres hacer y la IA lo ejecutará."
            ))
            return True

        subcmd = parts[1].lower()
        try:
            import sys
            sys.path.insert(0, '/home/cristopher/mcp-servers/minecraft-mcp')
            from rcon import RCONClient
            rcon = RCONClient(
                os.getenv('MC_HOST', 'localhost'),
                int(os.getenv('MC_PORT', '25575')),
                os.getenv('MC_RCON_PASSWORD', ''),
            )
            rcon.connect()

            if subcmd == "status":
                result = rcon.command("list")
            elif subcmd == "players":
                result = rcon.command("list")
            elif subcmd == "say" and len(parts) >= 3:
                msg = " ".join(parts[2:])
                result = rcon.command(f"say {msg}")
            elif subcmd == "give" and len(parts) >= 4:
                player = parts[2]
                item = parts[3]
                count = int(parts[4]) if len(parts) > 4 else 1
                result = rcon.command(f"give {player} {item} {count}")
            elif subcmd == "weather" and len(parts) >= 3:
                result = rcon.command(f"weather {parts[2]}")
            elif subcmd == "time" and len(parts) >= 3:
                result = rcon.command(f"time set {parts[2]}")
            elif subcmd == "difficulty" and len(parts) >= 3:
                result = rcon.command(f"difficulty {parts[2]}")
            elif subcmd == "gamemode" and len(parts) >= 4:
                result = rcon.command(f"gamemode {parts[3]} {parts[2]}")
            elif subcmd == "tp" and len(parts) >= 6:
                result = rcon.command(f"tp {parts[2]} {parts[3]} {parts[4]} {parts[5]}")
            elif subcmd == "summon" and len(parts) >= 3:
                entity = parts[2]
                if len(parts) >= 6:
                    result = rcon.command(f"summon {entity} {parts[3]} {parts[4]} {parts[5]}")
                else:
                    result = rcon.command(f"summon {entity}")
            elif subcmd == "effect" and len(parts) >= 4:
                player = parts[2]
                effect = parts[3]
                duration = int(parts[4]) if len(parts) > 4 else 30
                result = rcon.command(f"effect give {player} {effect} {duration}")
            elif subcmd == "locate" and len(parts) >= 3:
                result = rcon.command(f"locate structure minecraft:{parts[2]}")
            elif subcmd == "cmd" and len(parts) >= 3:
                cmd = " ".join(parts[2:])
                result = rcon.command(cmd)
            else:
                await self.send_telegram(chat_id, f"Comando no reconocido: {subcmd}. Usa /mc para ver la ayuda.")
                rcon.close()
                return True

            rcon.close()
            await self.send_telegram(chat_id, f"🎮 {result or 'OK'}")
        except Exception as e:
            await self.send_telegram(chat_id, f"❌ Error: {str(e)[:200]}")
        return True

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

        session_id = session["ai_session_id"]

        # Send "working" message
        await self.send_telegram(chat_id, "⏳ Trabajando en tu instrucción...")

        try:
            response = await self.ai.full_request(session_id, text, timeout=REQUEST_TIMEOUT)
            self.store.touch_session(chat_id)
            if response:
                await self.send_telegram(chat_id, response)
            else:
                await self.send_telegram(chat_id, "(Sin respuesta)")
            self.store.mark_processed(update_id, chat_id, status="completed", result=response[:500] if response else None)
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
