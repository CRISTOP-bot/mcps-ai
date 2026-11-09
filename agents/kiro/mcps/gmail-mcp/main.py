"""Gmail MCP Server - Read, send, and manage Gmail emails."""

import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Gmail - opencode")

GMAIL_CREDENTIALS = os.getenv("GMAIL_CREDENTIALS", "")
GMAIL_TOKEN = os.getenv("GMAIL_TOKEN", "")
GMAIL_USER = os.getenv("GMAIL_USER", "me")


def get_gmail_service():
    """Get authenticated Gmail service."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError("Google API libraries not installed. Run: uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib")

    scopes = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.labels",
    ]

    creds = None
    if GMAIL_TOKEN and os.path.exists(GMAIL_TOKEN):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(GMAIL_TOKEN, "w") as f:
                f.write(creds.to_json())
        else:
            raise RuntimeError(
                "Gmail not authenticated. Run the auth script first: "
                "python gmail_auth.py"
            )

    service = build("gmail", "v1", credentials=creds)
    return service


@mcp.tool
async def gmail_profile():
    """Get the authenticated user's Gmail profile."""
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId=GMAIL_USER).execute()
        return {
            "email": profile.get("emailAddress"),
            "messages_total": profile.get("messagesTotal"),
            "threads_total": profile.get("threadsTotal"),
            "history_id": profile.get("historyId"),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_list_emails(max_results: int = 10, query: str = "", label: str = "INBOX"):
    """List emails. Query supports Gmail search syntax (e.g., 'from:example@gmail.com', 'is:unread', 'subject:hello')."""
    try:
        service = get_gmail_service()
        params = {"userId": GMAIL_USER, "maxResults": max_results}
        if query:
            params["q"] = query
        if label:
            params["labelIds"] = [label]

        results = service.users().messages().list(**params).execute()
        messages = results.get("messages", [])

        emails = []
        for msg in messages:
            msg_data = service.users().messages().get(
                userId=GMAIL_USER, id=msg["id"], format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]
            ).execute()
            headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
            emails.append({
                "id": msg["id"],
                "thread_id": msg_data.get("threadId"),
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": msg_data.get("snippet", ""),
                "labels": msg_data.get("labelIds", []),
            })

        return {"emails": emails, "count": len(emails), "next_page_token": results.get("nextPageToken")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_read_email(email_id: str):
    """Read a full email by its ID. Returns headers, body, and attachments info."""
    try:
        service = get_gmail_service()
        msg = service.users().messages().get(
            userId=GMAIL_USER, id=email_id, format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

        # Extract body
        body = ""
        payload = msg.get("payload", {})
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                        break
                elif part.get("mimeType") == "text/html" and not body:
                    data = part.get("body", {}).get("data", "")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif "body" in payload:
            data = payload["body"].get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

        # Extract attachments
        attachments = []
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("filename"):
                    attachments.append({
                        "filename": part["filename"],
                        "mime_type": part.get("mimeType"),
                        "size": part.get("body", {}).get("size", 0),
                        "attachment_id": part.get("body", {}).get("attachmentId"),
                    })

        return {
            "id": msg["id"],
            "thread_id": msg.get("threadId"),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "cc": headers.get("Cc", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body[:5000],
            "attachments": attachments,
            "labels": msg.get("labelIds", []),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "", html: bool = False):
    """Send an email. Supports plain text or HTML."""
    try:
        service = get_gmail_service()

        if html:
            message = MIMEMultipart("alternative")
            message.attach(MIMEText(body, "html"))
        else:
            message = MIMEText(body)

        message["to"] = to
        message["subject"] = subject
        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        sent = service.users().messages().send(
            userId=GMAIL_USER, body={"raw": raw}
        ).execute()

        return {"status": "sent", "id": sent.get("id"), "thread_id": sent.get("threadId")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_reply(email_id: str, body: str, reply_all: bool = False):
    """Reply to an email. Use reply_all=True to reply to all recipients."""
    try:
        service = get_gmail_service()

        # Get original email
        original = service.users().messages().get(
            userId=GMAIL_USER, id=email_id, format="metadata",
            metadataHeaders=["From", "To", "Subject", "Message-ID", "References"]
        ).execute()
        headers = {h["name"]: h["value"] for h in original.get("payload", {}).get("headers", [])}

        to = headers.get("From", "")
        if reply_all:
            to = headers.get("From", "") + ", " + headers.get("To", "")
            cc = headers.get("Cc", "")
        else:
            cc = ""

        subject = headers.get("Subject", "")
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        if cc:
            message["cc"] = cc

        # Add In-Reply-To and References headers
        msg_id = headers.get("Message-ID", "")
        if msg_id:
            message["In-Reply-To"] = msg_id
            refs = headers.get("References", "")
            message["References"] = f"{refs} {msg_id}".strip()

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        sent = service.users().messages().send(
            userId=GMAIL_USER, body={"raw": raw, "threadId": original.get("threadId")}
        ).execute()

        return {"status": "sent", "id": sent.get("id"), "thread_id": sent.get("threadId")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_search(query: str, max_results: int = 10):
    """Search emails using Gmail search syntax. Examples: 'from:john@example.com', 'is:unread', 'subject:meeting', 'after:2024/01/01', 'has:attachment'."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId=GMAIL_USER, q=query, maxResults=max_results
        ).execute()
        messages = results.get("messages", [])

        emails = []
        for msg in messages:
            msg_data = service.users().messages().get(
                userId=GMAIL_USER, id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()
            headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
            emails.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": msg_data.get("snippet", ""),
            })

        return {"results": emails, "count": len(emails)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_list_labels():
    """List all Gmail labels (folders)."""
    try:
        service = get_gmail_service()
        results = service.users().labels().list(userId=GMAIL_USER).execute()
        labels = results.get("labels", [])
        return {
            "labels": [{"id": l["id"], "name": l["name"], "type": l.get("type", "")} for l in labels]
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_mark_read(email_id: str):
    """Mark an email as read."""
    try:
        service = get_gmail_service()
        service.users().messages().modify(
            userId=GMAIL_USER, id=email_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        return {"status": "marked as read", "id": email_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_mark_unread(email_id: str):
    """Mark an email as unread."""
    try:
        service = get_gmail_service()
        service.users().messages().modify(
            userId=GMAIL_USER, id=email_id, body={"addLabelIds": ["UNREAD"]}
        ).execute()
        return {"status": "marked as unread", "id": email_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_delete_email(email_id: str):
    """Move an email to trash."""
    try:
        service = get_gmail_service()
        service.users().messages().trash(userId=GMAIL_USER, id=email_id).execute()
        return {"status": "moved to trash", "id": email_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_create_label(name: str):
    """Create a new Gmail label."""
    try:
        service = get_gmail_service()
        label = service.users().labels().create(
            userId=GMAIL_USER, body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
        ).execute()
        return {"status": "created", "id": label["id"], "name": label["name"]}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_add_label(email_id: str, label_id: str):
    """Add a label to an email."""
    try:
        service = get_gmail_service()
        service.users().messages().modify(
            userId=GMAIL_USER, id=email_id, body={"addLabelIds": [label_id]}
        ).execute()
        return {"status": "label added", "email_id": email_id, "label_id": label_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def gmail_unread_count():
    """Get the count of unread emails."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId=GMAIL_USER, q="is:unread", maxResults=1
        ).execute()
        return {"unread_count": results.get("resultSizeEstimate", 0)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
