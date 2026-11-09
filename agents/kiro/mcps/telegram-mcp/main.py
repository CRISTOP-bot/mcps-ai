import os
import httpx
from fastmcp import FastMCP
from typing import Optional
import dotenv

dotenv.load_dotenv()

mcp = FastMCP("Telegram Bot - kiro")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set in environment")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


@mcp.tool
async def get_bot_info():
    """Fetch the bot's own user info."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/getMe")
        response.raise_for_status()
        return response.json()


@mcp.tool
async def send_message(chat_id: str, text: str):
    """Send a message to a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def get_updates(offset: int | None = None, limit: int = 100):
    """Fetch updates (messages, commands, etc.) for the bot."""
    params = {"limit": limit}
    if offset is not None:
        params["offset"] = offset
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/getUpdates",
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def set_webhook(url: str):
    """Set a webhook URL for the bot to receive updates."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/setWebhook",
            json={"url": url},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def delete_webhook():
    """Delete the bot's webhook."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/deleteWebhook",
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def get_webhook_info():
    """Get information about the bot's webhook."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/getWebhookInfo",
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def answer_callback_query(callback_query_id: str, text: str | None = None, show_alert: bool = False):
    """Answer a callback query (from inline buttons)."""
    payload = {"callback_query_id": callback_query_id,
               "show_alert": show_alert}
    if text is not None:
        payload["text"] = text
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/answerCallbackQuery",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def edit_message_text(chat_id: str, message_id: int, text: str):
    """Edit the text of a message."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/editMessageText",
            json={"chat_id": chat_id, "message_id": message_id, "text": text},
        )
        response.raise_for_status()
        return response.json()


# ---------- Messaging essentials ----------

@mcp.tool
async def send_photo(chat_id: int, photo: str, caption: Optional[str] = None):
    """Send a photo to a chat. `photo` can be a URL or a file_id already known to Telegram."""
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "photo": photo}
        if caption:
            payload["caption"] = caption
        response = await client.post(
            f"{BASE_URL}/sendPhoto", 
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def send_document(chat_id: int, document: str, caption: Optional[str] = None):
    """Send a document/file to a chat. `document` can be a URL or a file_id."""
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "document": document}
        if caption:
            payload["caption"] = caption
        response = await client.post(
            f"{BASE_URL}/sendDocument", 
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def delete_message(chat_id: int, message_id: int):
    """Delete a message from a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/deleteMessage",
            json={"chat_id": chat_id, "message_id": message_id},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def pin_chat_message(chat_id: int, message_id: int, disable_notification: bool = False):
    """Pin a message in a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/pinChatMessage",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "disable_notification": disable_notification,
            },
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def unpin_chat_message(chat_id: int, message_id: Optional[int] = None):
    """Unpin a message (or the most recent pinned message if message_id is omitted)."""
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id}
        if message_id is not None:
            payload["message_id"] = message_id
        response = await client.post(
            f"{BASE_URL}/unpinChatMessage", 
            json=payload
        )
        response.raise_for_status()
        return response.json()


# ---------- Polls ----------

@mcp.tool
async def send_poll(chat_id: int, question: str, options: list[str], is_anonymous: bool = True):
    """Send a poll to a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/sendPoll",
            json={
                "chat_id": chat_id,
                "question": question,
                "options": options,
                "is_anonymous": is_anonymous,
            },
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def stop_poll(chat_id: int, message_id: int):
    """Close a poll and return the final results."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/stopPoll",
            json={"chat_id": chat_id, "message_id": message_id},
        )
        response.raise_for_status()
        return response.json()


# ---------- Chat / group info & management ----------

@mcp.tool
async def get_chat(chat_id: int):
    """Fetch info about a chat/channel by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/getChat", params={"chat_id": chat_id})
        response.raise_for_status()
        return response.json()


@mcp.tool
async def get_chat_member(chat_id: int, user_id: int):
    """Get a specific user's membership status in a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/getChatMember",
            params={"chat_id": chat_id, "user_id": user_id},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def get_chat_administrators(chat_id: int):
    """List the administrators of a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/getChatAdministrators", params={"chat_id": chat_id}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def ban_chat_member(chat_id: int, user_id: int):
    """Ban a user from a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/banChatMember",
            json={"chat_id": chat_id, "user_id": user_id},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def unban_chat_member(chat_id: int, user_id: int):
    """Unban a user from a chat."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/unbanChatMember",
            json={"chat_id": chat_id, "user_id": user_id},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def set_chat_title(chat_id: int, title: str):
    """Rename a chat/channel."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/setChatTitle",
            json={"chat_id": chat_id, "title": title},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def set_chat_description(chat_id: int, description: str):
    """Update a chat/channel's description."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/setChatDescription",
            json={"chat_id": chat_id, "description": description},
        )
        response.raise_for_status()
        return response.json()


# ---------- Media ----------

@mcp.tool
async def send_video(chat_id: int, video: str, caption: Optional[str] = None):
    """Send a video to a chat. `video` can be a URL or a file_id."""
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "video": video}
        if caption:
            payload["caption"] = caption
        response = await client.post(
            f"{BASE_URL}/sendVideo", 
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def send_audio(chat_id: int, audio: str, caption: Optional[str] = None):
    """Send an audio file to a chat. `audio` can be a URL or a file_id."""
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "audio": audio}
        if caption:
            payload["caption"] = caption
        response = await client.post(
            f"{BASE_URL}/sendAudio", 
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def send_voice(chat_id: int, voice: str):
    """Send a voice note to a chat. `voice` can be a URL or a file_id."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/sendVoice", json={"chat_id": chat_id, "voice": voice}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def set_message_reaction(chat_id: int, message_id: int, emoji: str = "\U0001F44D"):
    """React to a message with an emoji (default: thumbs up)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/setMessageReaction",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "reaction": [{"type": "emoji", "emoji": emoji}],
            },
        )
        response.raise_for_status()
        return response.json()


# ---------- Commands / discoverability ----------

@mcp.tool
async def set_my_commands(commands: list[dict]):
    """
    Register bot commands so Telegram shows them in the UI.
    `commands` is a list of {"command": "start", "description": "..."} dicts.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/setMyCommands", json={"commands": commands}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool
async def get_my_commands():
    """Fetch the bot's currently registered commands."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/getMyCommands")
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    mcp.run(transport="stdio")
