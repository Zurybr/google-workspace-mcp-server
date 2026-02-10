#!/usr/bin/env python3
"""
Google Workspace MCP Server - gogcli Backend

An MCP server that provides tools for interacting with Google Workspace services
using gogcli as the backend (direct execution).

Services: Gmail, Sheets, Docs, Slides, Calendar, Drive
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    # Try to load .env from the project directory
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    Tool,
    TextContent,
)

# Configuration
DEFAULT_PORT = 9001
GOGCLI_BIN = os.getenv("GOGCLI_BIN", "gogcli")
DEFAULT_ACCOUNT = os.getenv("GOGCLI_ACCOUNT", None)  # Use None instead of empty string


def run_gogcli(
    service: str,
    command: str,
    args: list[str],
    account: str | None = None,
    html_body: str | None = None,
    timeout: int = 60
) -> dict[str, Any]:
    """
    Run a gogcli command directly and return the result

    Args:
        service: The gogcli service (gmail, sheets, docs, slides, calendar, drive)
        command: The command to run
        args: Additional arguments
        account: Google account to use
        html_body: HTML content for email (optional)
        timeout: Command timeout in seconds

    Returns:
        Dict with success status and result/error
    """
    gog_cmd = [GOGCLI_BIN, service, command]
    gog_cmd.extend(args)

    # Handle HTML body for emails
    if html_body:
        # Create temp file with HTML content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_body)
            html_file = f.name

        gog_cmd.extend(["--body-html", f"@{html_file}"])

    try:
        result = subprocess.run(
            gog_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Cleanup temp file if created
        if html_body:
            try:
                os.unlink(html_file)
            except:
                pass

        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip(),
                "returncode": result.returncode
            }
        #imprimir el comando ejecutado y su resultado para debug
        print(f"[MCP DEBUG] Command: {' '.join(gog_cmd)}", flush=True)

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Create server instance
server = Server("google-workspace-gogcli-server")


# =============================================
# RESOURCES
# =============================================

@server.list_resources()
async def handle_list_resources() -> list:
    """List available resources"""
    return [
        {
            "uri": "workspace://info",
            "name": "Workspace Information",
            "description": "Information about the Google Workspace MCP server (gogcli backend)",
            "mimeType": "text/plain",
        },
        {
            "uri": "workspace://gogcli-version",
            "name": "gogcli Version",
            "description": "gogcli version information",
            "mimeType": "text/plain",
        },
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource"""
    if uri == "workspace://info":
        return """Google Workspace MCP Server v0.4.0 (gogcli Edition)

This server provides tools for interacting with Google Workspace services:
- Gmail: Send, read, search emails with HTML support
- Sheets: Create, read, write, delete spreadsheets and cells
- Docs: Create, read, edit, delete documents
- Slides: Create, read, edit presentations
- Calendar: Create, read, update, delete events
- Drive: List, search, upload, download, share files and folders

Backend: gogcli (https://github.com/steipete/gogcli)
Authentication: Direct OAuth execution (no keyring needed)

Run ./install.sh --server-only to start the server on port 9001.
"""
    elif uri == "workspace://gogcli-version":
        result = run_gogcli("--version", "", [], timeout=10)
        if result["success"]:
            return result["output"]
        else:
            return "gogcli version not available"
    else:
        raise ValueError(f"Unknown resource: {uri}")


# =============================================
# GMAIL TOOLS
# =============================================

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        # SYSTEM/STATUS TOOLS
        Tool(
            name="gogcli_status",
            description="Check gogcli authentication status and configuration",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="gogcli_version",
            description="Get gogcli version information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # GMAIL TOOLS
        Tool(
            name="gmail_send_email",
            description="Send an email via Gmail (supports HTML - use html:true)",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email(s), comma-separated"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body (plain text or HTML)"},
                    "html": {"type": "boolean", "description": "Treat body as HTML (default: false)", "default": False},
                },
                "required": ["to", "subject", "body"],
            },
        ),
        Tool(
            name="gmail_list_emails",
            description="List recent emails from Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of emails to list", "default": 10},
                },
            },
        ),
        Tool(
            name="gmail_search_emails",
            description="Search for emails in Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Number of results", "default": 10},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="gmail_read_email",
            description="Read a full email by message ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID"},
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_label_email",
            description="Add or remove labels from an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID"},
                    "labels": {"type": "string", "description": "Labels to add (comma-separated)"},
                    "remove": {"type": "string", "description": "Labels to remove (comma-separated)"},
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_archive_email",
            description="Archive an email (remove from inbox)",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID"},
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_delete_email",
            description="Delete an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID"},
                },
                "required": ["message_id"],
            },
        ),

        # SHEETS TOOLS
        Tool(
            name="sheets_create",
            description="Create a new Google Sheets spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Spreadsheet title"},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="sheets_read",
            description="Read data from a spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID or URL"},
                    "range": {"type": "string", "description": "Cell range (e.g., Sheet1!A1:D10)"},
                },
                "required": ["spreadsheet_id"],
            },
        ),
        Tool(
            name="sheets_write",
            description="Write data to a spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID or URL"},
                    "range": {"type": "string", "description": "Cell range (e.g., Sheet1!A1:D10)"},
                    "data": {"type": "string", "description": "Data to write (JSON array of arrays or CSV)"},
                },
                "required": ["spreadsheet_id", "range", "data"],
            },
        ),
        Tool(
            name="sheets_append",
            description="Append rows to a spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID or URL"},
                    "range": {"type": "string", "description": "Range to append to"},
                    "data": {"type": "string", "description": "Data to append (JSON array or CSV)"},
                },
                "required": ["spreadsheet_id", "data"],
            },
        ),
        Tool(
            name="sheets_delete",
            description="Delete a spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID or URL"},
                },
                "required": ["spreadsheet_id"],
            },
        ),

        # DOCS TOOLS
        Tool(
            name="docs_create",
            description="Create a new Google Doc",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "content": {"type": "string", "description": "Initial content"},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="docs_read",
            description="Read a Google Doc",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID or URL"},
                },
                "required": ["doc_id"],
            },
        ),
        Tool(
            name="docs_append",
            description="Append text to a Google Doc",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID or URL"},
                    "text": {"type": "string", "description": "Text to append"},
                },
                "required": ["doc_id", "text"],
            },
        ),
        Tool(
            name="docs_delete",
            description="Delete a Google Doc",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID or URL"},
                },
                "required": ["doc_id"],
            },
        ),

        # SLIDES TOOLS
        Tool(
            name="slides_create",
            description="Create a new Google Slides presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Presentation title"},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="slides_read",
            description="Read a Google Slides presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID or URL"},
                },
                "required": ["presentation_id"],
            },
        ),
        Tool(
            name="slides_delete",
            description="Delete a Google Slides presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID or URL"},
                },
                "required": ["presentation_id"],
            },
        ),

        # CALENDAR TOOLS
        Tool(
            name="calendar_create_event",
            description="Create a new calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "start": {"type": "string", "description": "Start time (RFC3339 or 'tomorrow 10am')"},
                    "end": {"type": "string", "description": "End time (RFC3339 or 'tomorrow 11am')"},
                    "description": {"type": "string", "description": "Event description"},
                    "location": {"type": "string", "description": "Event location"},
                    "attendees": {"type": "string", "description": "Attendees (comma-separated emails)"},
                },
                "required": ["title", "start", "end"],
            },
        ),
        Tool(
            name="calendar_list_events",
            description="List calendar events",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "Start date (default: today)"},
                    "end": {"type": "string", "description": "End date"},
                    "limit": {"type": "integer", "description": "Max events to return", "default": 10},
                },
            },
        ),
        Tool(
            name="calendar_delete_event",
            description="Delete a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID"},
                },
                "required": ["event_id"],
            },
        ),
        Tool(
            name="calendar_update_event",
            description="Update a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID"},
                    "title": {"type": "string", "description": "New title"},
                    "start": {"type": "string", "description": "New start time"},
                    "end": {"type": "string", "description": "New end time"},
                    "description": {"type": "string", "description": "New description"},
                    "location": {"type": "string", "description": "New location"},
                },
                "required": ["event_id"],
            },
        ),
        # DRIVE TOOLS
        Tool(
            name="drive_list_files",
            description="List files in Google Drive folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "parent": {"type": "string", "description": "Parent folder ID (default: root)"}
                }
            },
        ),
        Tool(
            name="drive_search",
            description="Search files in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="drive_get_file",
            description="Get file metadata from Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_download",
            description="Download a file from Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to download"},
                    "output": {"type": "string", "description": "Output path (optional)"},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_upload",
            description="Upload a file to Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Local file path to upload"},
                    "parent": {"type": "string", "description": "Parent folder ID (default: root)"},
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="drive_mkdir",
            description="Create a folder in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Folder name"},
                    "parent": {"type": "string", "description": "Parent folder ID (default: root)"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="drive_delete",
            description="Delete a file from Google Drive (moves to trash)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to delete"},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_move",
            description="Move a file to a different folder in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to move"},
                    "parent": {"type": "string", "description": "Destination folder ID"},
                },
                "required": ["file_id", "parent"],
            },
        ),
        Tool(
            name="drive_rename",
            description="Rename a file in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to rename"},
                    "new_name": {"type": "string", "description": "New file name"},
                },
                "required": ["file_id", "new_name"],
            },
        ),
        Tool(
            name="drive_share",
            description="Share a file in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to share"},
                    "email": {"type": "string", "description": "Email to share with"},
                    "role": {"type": "string", "description": "Permission role (reader, writer, owner)", "enum": ["reader", "writer", "owner"], "default": "reader"},
                },
                "required": ["file_id", "email"],
            },
        ),
        Tool(
            name="drive_permissions",
            description="List permissions on a Google Drive file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_url",
            description="Get web URL for a Google Drive file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID(s), comma-separated"},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_copy",
            description="Copy a file in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to copy"},
                    "name": {"type": "string", "description": "Name for the copy"},
                    "parent": {"type": "string", "description": "Parent folder ID to copy to (optional)"},
                },
                "required": ["file_id", "name"],
            },
        ),
        Tool(
            name="drive_unshare",
            description="Remove a permission from a Google Drive file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                    "permission_id": {"type": "string", "description": "Permission ID to remove"},
                },
                "required": ["file_id", "permission_id"],
            },
        ),
        Tool(
            name="drive_list_drives",
            description="List shared drives (Team Drives) in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                },
            },
        ),
        Tool(
            name="drive_list_comments",
            description="List comments on a Google Drive file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_add_comment",
            description="Add a comment to a Google Drive file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                    "content": {"type": "string", "description": "Comment content"},
                },
                "required": ["file_id", "content"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    account = arguments.get("account", None)

    try:
        # SYSTEM/STATUS TOOLS
        if name == "gogcli_status":
            # Use expect for keyring automation
            auth_result = run_gogcli("auth", "status", [], account=None, timeout=10)
            config_result = run_gogcli("config", "list", [], account=None, timeout=10)

            status_info = {
                "gogcli_bin": GOGCLI_BIN,
                "default_account": DEFAULT_ACCOUNT or "not set",
                "auth_status": "authenticated" if auth_result["success"] else "not authenticated",
                "auth_output": auth_result.get("output", auth_result.get("error", "")),
                "config": config_result.get("output", "config not available")
            }
            return [TextContent(type="text", text=json.dumps(status_info, indent=2))]

        elif name == "gogcli_version":
            result = run_gogcli("--version", "", [], account=None, timeout=10)
            if result["success"]:
                return [TextContent(type="text", text=result.get("output", result.get("error", "")))]
            else:
                return [TextContent(type="text", text=f"Error getting version: {result.get('error', '')}")]

        # GMAIL TOOLS
        elif name == "gmail_send_email":
            to = arguments["to"]
            subject = arguments["subject"]
            body = arguments["body"]
            is_html = arguments.get("html", False)

            args = ["--to", to, "--subject", subject]

            if is_html:
                # FIXED: Use the confirmed working method for HTML
                # --body-html with expect variable shell expansion
                result = run_gogcli("gmail", "send", args, account, html_body=body)
            else:
                args.extend(["--body", body])
                result = run_gogcli("gmail", "send", args, account)

            if result["success"]:
                return [TextContent(type="text", text=f"Email sent successfully!")]
            else:
                return [TextContent(type="text", text=f"Error: {result['error']}")]

        elif name == "gmail_list_emails":
            limit = arguments.get("limit", 10)
            result = run_gogcli("gmail", "list", ["--limit", str(limit)], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_search_emails":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            result = run_gogcli("gmail", "search", ["--query", query, "--limit", str(limit)], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_read_email":
            msg_id = arguments["message_id"]
            result = run_gogcli("gmail", "read", ["--id", msg_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_label_email":
            msg_id = arguments["message_id"]
            labels = arguments.get("labels", "")
            remove = arguments.get("remove", "")

            if labels:
                result = run_gogcli("gmail", "label", ["--id", msg_id, "--add", labels], account)
                return [TextContent(type="text", text=result.get("output", result["error"]))]
            elif remove:
                result = run_gogcli("gmail", "label", ["--id", msg_id, "--remove", remove], account)
                return [TextContent(type="text", text=result.get("output", result["error"]))]
            else:
                return [TextContent(type="text", text="Error: Must specify either 'labels' or 'remove'")]

        elif name == "gmail_archive_email":
            msg_id = arguments["message_id"]
            result = run_gogcli("gmail", "archive", ["--id", msg_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_delete_email":
            msg_id = arguments["message_id"]
            result = run_gogcli("gmail", "delete", ["--id", msg_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # SHEETS TOOLS
        elif name == "sheets_create":
            title = arguments["title"]
            result = run_gogcli("sheets", "create", ["--title", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_read":
            sheet_id = arguments["spreadsheet_id"]
            range_val = arguments.get("range", "A1")
            result = run_gogcli("sheets", "get", ["--id", sheet_id, "--range", range_val], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_write":
            sheet_id = arguments["spreadsheet_id"]
            range_val = arguments["range"]
            data = arguments["data"]

            # Try to parse as JSON first
            try:
                parsed_data = json.loads(data)
                if isinstance(parsed_data, list):
                    # Convert to CSV format
                    csv_data = "\n".join([",".join(row) for row in parsed_data])
                    data = csv_data
            except:
                pass  # Use as-is

            result = run_gogcli("sheets", "update", ["--id", sheet_id, "--range", range_val, "--data", data], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_append":
            sheet_id = arguments["spreadsheet_id"]
            range_val = arguments.get("range", "A1")
            data = arguments["data"]

            # Try to parse as JSON first
            try:
                parsed_data = json.loads(data)
                if isinstance(parsed_data, list):
                    csv_data = "\n".join([",".join(row) for row in parsed_data])
                    data = csv_data
            except:
                pass

            result = run_gogcli("sheets", "append", ["--id", sheet_id, "--range", range_val, "--data", data], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_delete":
            sheet_id = arguments["spreadsheet_id"]
            result = run_gogcli("sheets", "delete", ["--id", sheet_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # DOCS TOOLS
        elif name == "docs_create":
            title = arguments["title"]
            content = arguments.get("content", "")

            if content:
                result = run_gogcli("docs", "create", ["--title", title, "--content", content], account)
            else:
                result = run_gogcli("docs", "create", ["--title", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_read":
            doc_id = arguments["doc_id"]
            result = run_gogcli("docs", "get", ["--id", doc_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_append":
            doc_id = arguments["doc_id"]
            text = arguments["text"]
            result = run_gogcli("docs", "append", ["--id", doc_id, "--text", text], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_delete":
            doc_id = arguments["doc_id"]
            result = run_gogcli("docs", "delete", ["--id", doc_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # SLIDES TOOLS
        elif name == "slides_create":
            title = arguments["title"]
            result = run_gogcli("slides", "create", ["--title", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "slides_read":
            pres_id = arguments["presentation_id"]
            result = run_gogcli("slides", "get", ["--id", pres_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "slides_delete":
            pres_id = arguments["presentation_id"]
            result = run_gogcli("slides", "delete", ["--id", pres_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # CALENDAR TOOLS
        elif name == "calendar_create_event":
            title = arguments["title"]
            start = arguments["start"]
            end = arguments["end"]

            args = ["--title", title, "--start", start, "--end", end]

            if arguments.get("description"):
                args.extend(["--description", arguments["description"]])
            if arguments.get("location"):
                args.extend(["--location", arguments["location"]])
            if arguments.get("attendees"):
                args.extend(["--attendees", arguments["attendees"]])

            result = run_gogcli("calendar", "create", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "calendar_list_events":
            start = arguments.get("start", "")
            end = arguments.get("end", "")
            limit = arguments.get("limit", 10)

            args = ["--limit", str(limit)]
            if start:
                args.extend(["--start", start])
            if end:
                args.extend(["--end", end])

            result = run_gogcli("calendar", "list", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "calendar_delete_event":
            event_id = arguments["event_id"]
            result = run_gogcli("calendar", "delete", ["--id", event_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "calendar_update_event":
            event_id = arguments["event_id"]
            args = ["--id", event_id]

            if arguments.get("title"):
                args.extend(["--title", arguments["title"]])
            if arguments.get("start"):
                args.extend(["--start", arguments["start"]])
            if arguments.get("end"):
                args.extend(["--end", arguments["end"]])
            if arguments.get("description"):
                args.extend(["--description", arguments["description"]])
            if arguments.get("location"):
                args.extend(["--location", arguments["location"]])

            result = run_gogcli("calendar", "update", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # DRIVE TOOLS
        elif name == "drive_list_files":
            import sys
            parent_id = arguments.get("parent", "")
            print(f"[MCP DEBUG] drive_list_files called with parent={parent_id}", file=sys.stderr, flush=True)
            args = []
            if parent_id:
                args.extend(["--parent", parent_id])
            print(f"[MCP DEBUG] args={args}", file=sys.stderr, flush=True)
            result = run_gogcli("drive", "ls", args, account)
            print(f"[MCP DEBUG] result success={result.get('success')}", file=sys.stderr, flush=True)
            print(f"[MCP DEBUG] result output={result.get('output', 'N/A')[:100]}", file=sys.stderr, flush=True)
            print(f"[MCP DEBUG] result error={result.get('error', 'N/A')[:100]}", file=sys.stderr, flush=True)
            # formar el comando que se va a ejecutar en gogcli
            print(f"[MCP DEBUG] Running gogcli command: gogcli drive ls {' '.join(args)}", file=sys.stderr, flush=True)
            if result.get("success"):
                return [TextContent(type="text", text=result.get("output", "No output"))]
            else:
                return [TextContent(type="text", text=f"Error: {result.get('error', 'Unknown error')}")]

        elif name == "drive_search":
            query = arguments["query"]
            result = run_gogcli("drive", "search", [query], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_get_file":
            file_id = arguments["file_id"]
            result = run_gogcli("drive", "get", [file_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_download":
            file_id = arguments["file_id"]
            output = arguments.get("output", "")
            args = [file_id]
            if output:
                args.extend(["--output", output])
            result = run_gogcli("drive", "download", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_upload":
            file_path = arguments["file_path"]
            parent = arguments.get("parent", "")
            args = [file_path]
            if parent:
                args.extend([f"--folder={parent}"])
            result = run_gogcli("drive", "upload", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_mkdir":
            name = arguments["name"]
            parent = arguments.get("parent", "")
            args = [name]
            if parent:
                args.extend([f"--folder={parent}"])
            result = run_gogcli("drive", "mkdir", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_delete":
            file_id = arguments["file_id"]
            result = run_gogcli("drive", "delete", [file_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_move":
            file_id = arguments["file_id"]
            parent = arguments.get("parent", "")
            result = run_gogcli("drive", "move", [file_id, f"--folder={parent}"], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_rename":
            file_id = arguments["file_id"]
            new_name = arguments["new_name"]
            result = run_gogcli("drive", "rename", [file_id, new_name], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_share":
            file_id = arguments["file_id"]
            email = arguments["email"]
            role = arguments.get("role", "reader")
            result = run_gogcli("drive", "share", [file_id, "--email", email, "--role", role], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_permissions":
            file_id = arguments["file_id"]
            result = run_gogcli("drive", "permissions", [file_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_url":
            file_id = arguments["file_id"]
            result = run_gogcli("drive", "url", [file_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_copy":
            file_id = arguments["file_id"]
            name = arguments["name"]
            parent = arguments.get("parent", "")
            args = [file_id, name]
            if parent:
                args.extend([f"--folder={parent}"])
            result = run_gogcli("drive", "copy", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_unshare":
            file_id = arguments["file_id"]
            permission_id = arguments["permission_id"]
            result = run_gogcli("drive", "unshare", [file_id, permission_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_list_drives":
            result = run_gogcli("drive", "drives", [], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_list_comments":
            file_id = arguments["file_id"]
            result = run_gogcli("drive", "comments", ["list", file_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "drive_add_comment":
            file_id = arguments["file_id"]
            content = arguments["content"]
            result = run_gogcli("drive", "comments", ["add", file_id, "--content", content], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# =============================================
# MAIN ENTRY POINT
# =============================================

def main_server_only(port: int = DEFAULT_PORT, detach: bool = False):
    """Run the server in SSE mode on specified port"""
    from mcp.server.sse import SseServerTransport
    import uvicorn
    import asyncio

    # Create SSE transport
    sse_transport = SseServerTransport("/messages")

    # ASGI app that handles both SSE and POST endpoints
    async def app(scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]

            if path == "/health":
                # Health check endpoint
                from starlette.responses import JSONResponse

                # Check gogcli availability
                try:
                    result = subprocess.run(
                        [GOGCLI_BIN, "auth", "status"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    gogcli_ok = result.returncode == 0
                    auth_status = "authenticated" if gogcli_ok else "not_authenticated"
                except:
                    gogcli_ok = False
                    auth_status = "error"

                response = JSONResponse({
                    "status": "ok",
                    "server": "google-workspace-gogcli-server",
                    "version": "0.4.0",
                    "gogcli": "ok" if gogcli_ok else "error",
                    "auth": auth_status,
                    "account": DEFAULT_ACCOUNT or "default"
                })
                await response(scope, receive, send)

            elif path == "/sse":
                # SSE endpoint - handle MCP connection
                async with sse_transport.connect_sse(scope, receive, send) as streams:
                    await server.run(
                        streams[0],
                        streams[1],
                        InitializationOptions(
                            server_name="google-workspace-gogcli-server",
                            server_version="0.3.0",
                            capabilities=server.get_capabilities(
                                notification_options=NotificationOptions(),
                                experimental_capabilities={},
                            ),
                        ),
                    )

            elif path == "/messages" and scope["method"] == "POST":
                # POST endpoint for SSE messages - delegate to transport
                try:
                    await sse_transport.handle_post_message(scope, receive, send)
                except Exception:
                    # Silently handle client disconnects and other errors
                    pass

            else:
                # 404
                from starlette.responses import Response
                response = Response("Not Found", status_code=404)
                await response(scope, receive, send)

    # Wrap app with CORS middleware using Starlette
    from starlette.applications import Starlette
    from starlette.middleware.cors import CORSMiddleware
    from starlette.routing import Mount

    # Create a wrapper Starlette app with CORS
    starlette_app = Starlette(routes=[
        Mount("/", app=app)
    ])

    # Add CORS middleware
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Use the wrapped app
    app = starlette_app

    print(f"\n🚀 Google Workspace MCP Server (gogcli backend)")
    print(f"📡 Server running on http://localhost:{port}/sse")
    print(f"📧 Using gogcli with account: {DEFAULT_ACCOUNT or 'default'}")
    print(f"🔧 Direct execution (no keyring/expect)")

    if detach:
        # Run in background (detached mode)
        import sys
        print(f"\n✅ Server starting in background mode...")
        print(f"🛑 To stop: pkill -f 'google_workspace_mcp.server_gogcli'")
        sys.stdout.flush()
        sys.stderr.flush()

        # Daemonize: fork twice
        if os.fork() > 0:
            os._exit(0)
        os.setsid()
        if os.fork() > 0:
            os._exit(0)

        # Redirect stdin/stdout/stderr to /dev/null
        sys.stdin = open(os.devnull, 'r')
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    else:
        print(f"\nPress Ctrl+C to stop\n")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


async def main():
    """Main entry point for stdio mode"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="google-workspace-gogcli-server",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Google Workspace MCP Server (gogcli backend)")
    parser.add_argument("--server-only", action="store_true", help="Run in SSE server mode")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port for SSE server (default: {DEFAULT_PORT})")
    parser.add_argument("--detach", action="store_true", help="Run in background/detached mode")

    args = parser.parse_args()

    if args.server_only:
        main_server_only(args.port, args.detach)
    else:
        asyncio.run(main())
