#!/usr/bin/env python3
"""
Google Workspace MCP Server - gogcli Backend

An MCP server that provides tools for interacting with Google Workspace services
using gogcli as the backend (OAuth via gogcli keyring).

Services: Gmail, Sheets, Docs, Slides, Calendar
"""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

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
DEFAULT_ACCOUNT = os.getenv("GOGCLI_ACCOUNT", "")


def run_gogcli(
    service: str,
    command: str,
    args: list[str],
    account: str | None = None,
    timeout: int = 60
) -> dict[str, Any]:
    """
    Run a gogcli command and return the result

    Args:
        service: The gogcli service (gmail, sheets, docs, slides, calendar)
        command: The command to run
        args: Additional arguments
        account: Google account to use
        timeout: Command timeout in seconds

    Returns:
        Dict with success status and result/error
    """
    acc = account or DEFAULT_ACCOUNT
    cmd = [GOGCLI_BIN, service, command]

    if acc:
        cmd.extend(["--account", acc])

    cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

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

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"gogcli not found. Install it from https://github.com/steipete/gogcli/releases"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def run_gogcli_with_expect(
    service: str,
    command: str,
    args: list[str],
    account: str | None = None,
    html_body: str | None = None,
    timeout: int = 60
) -> dict[str, Any]:
    """
    Run a gogcli command with expect for keyring passphrase automation
    Supports HTML email using the confirmed working method (variable shell expansion)

    Args:
        service: The gogcli service
        command: The command to run
        args: Additional arguments
        account: Google account to use
        html_body: HTML content for email (optional)
        timeout: Command timeout in seconds

    Returns:
        Dict with success status and result/error
    """
    acc = account or DEFAULT_ACCOUNT
    gog_cmd = [GOGCLI_BIN, service, command]

    if acc:
        gog_cmd.extend(["--account", acc])

    gog_cmd.extend(args)

    # Build expect script with the CONFIRMED working method
    # Using variable shell expansion (Prueba 6 - message_id: 19c4434e4fb9417f)
    if html_body:
        # Create temp file with HTML content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            # Escape single quotes and backslashes in HTML
            escaped_html = html_body.replace('\\', '\\\\').replace('"', '\\"')
            f.write(escaped_html)
            html_file = f.name

        # Use the confirmed working method: variable shell expansion
        expect_script = f'''set timeout {timeout}
set html_body [exec cat {html_file}]
spawn sh -c "{{" ".join(gog_cmd)}} --body-html=$html_body"
expect {{
    "Enter passphrase" {{ send "\\r"; exp_continue }}
    timeout {{ puts "Timeout waiting for response"; exit 1 }}
    eof
}}
exec rm {html_file}
'''
    else:
        # Standard expect without HTML
        expect_script = f'''set timeout {timeout}
spawn sh -c '{" ".join(gog_cmd)}'
expect {{
    "Enter passphrase" {{ send "\\r"; exp_continue }}
    timeout {{ puts "Timeout waiting for response"; exit 1 }}
    eof
}}
'''

    try:
        result = subprocess.run(
            ["expect", "-c", expect_script],
            capture_output=True,
            text=True,
            timeout=timeout + 5
        )

        # Filter out expect's own messages
        output_lines = []
        for line in result.stdout.split('\n'):
            if not line.startswith('spawn') and not line.startswith('set timeout') and not line.startswith('exec rm'):
                output_lines.append(line)

        output = '\n'.join(output_lines).strip()

        if result.returncode == 0:
            return {
                "success": True,
                "output": output,
                "stderr": result.stderr.strip()
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or output,
                "returncode": result.returncode
            }

    except FileNotFoundError:
        # expect not found, try without it
        if html_body:
            # Cleanup temp file if expect failed
            try:
                os.unlink(html_file)
            except:
                pass
        return run_gogcli(service, command, args, account, timeout)
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
        return """Google Workspace MCP Server v0.2.0 (gogcli Edition)

This server provides tools for interacting with Google Workspace services:
- Gmail: Send, read, search emails with HTML support (FIXED - uses --body-html)
- Sheets: Create, read, write, delete spreadsheets and cells
- Docs: Create, read, edit, delete documents
- Slides: Create, read, edit presentations
- Calendar: Create, read, update, delete events

Backend: gogcli (https://github.com/steipete/gogcli)
Authentication: OAuth via gogcli keyring with expect automation

HTML Email Method: Variable shell expansion (message_id: 19c4434e4fb9417f confirmed working)

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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
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
                    "account": {"type": "string", "description": "Google account to use"},
                },
                "required": ["event_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    account = arguments.get("account", None)

    try:
        # GMAIL TOOLS
        if name == "gmail_send_email":
            to = arguments["to"]
            subject = arguments["subject"]
            body = arguments["body"]
            is_html = arguments.get("html", False)

            args = ["--to", to, "--subject", subject]

            if is_html:
                # FIXED: Use the confirmed working method for HTML
                # --body-html with expect variable shell expansion
                result = run_gogcli_with_expect("gmail", "send", args, account, html_body=body)
            else:
                args.extend(["--body", body])
                result = run_gogcli_with_expect("gmail", "send", args, account)

            if result["success"]:
                return [TextContent(type="text", text=f"Email sent successfully!")]
            else:
                return [TextContent(type="text", text=f"Error: {result['error']}")]

        elif name == "gmail_list_emails":
            limit = arguments.get("limit", 10)
            result = run_gogcli_with_expect("gmail", "list", ["--limit", str(limit)], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_search_emails":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            result = run_gogcli_with_expect("gmail", "search", ["--query", query, "--limit", str(limit)], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_read_email":
            msg_id = arguments["message_id"]
            result = run_gogcli_with_expect("gmail", "read", ["--id", msg_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_label_email":
            msg_id = arguments["message_id"]
            labels = arguments.get("labels", "")
            remove = arguments.get("remove", "")

            if labels:
                result = run_gogcli_with_expect("gmail", "label", ["--id", msg_id, "--add", labels], account)
                return [TextContent(type="text", text=result.get("output", result["error"]))]
            elif remove:
                result = run_gogcli_with_expect("gmail", "label", ["--id", msg_id, "--remove", remove], account)
                return [TextContent(type="text", text=result.get("output", result["error"]))]
            else:
                return [TextContent(type="text", text="Error: Must specify either 'labels' or 'remove'")]

        elif name == "gmail_archive_email":
            msg_id = arguments["message_id"]
            result = run_gogcli_with_expect("gmail", "archive", ["--id", msg_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_delete_email":
            msg_id = arguments["message_id"]
            result = run_gogcli_with_expect("gmail", "delete", ["--id", msg_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # SHEETS TOOLS
        elif name == "sheets_create":
            title = arguments["title"]
            result = run_gogcli_with_expect("sheets", "create", ["--title", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_read":
            sheet_id = arguments["spreadsheet_id"]
            range_val = arguments.get("range", "A1")
            result = run_gogcli_with_expect("sheets", "get", ["--id", sheet_id, "--range", range_val], account)
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

            result = run_gogcli_with_expect("sheets", "update", ["--id", sheet_id, "--range", range_val, "--data", data], account)
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

            result = run_gogcli_with_expect("sheets", "append", ["--id", sheet_id, "--range", range_val, "--data", data], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_delete":
            sheet_id = arguments["spreadsheet_id"]
            result = run_gogcli_with_expect("sheets", "delete", ["--id", sheet_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # DOCS TOOLS
        elif name == "docs_create":
            title = arguments["title"]
            content = arguments.get("content", "")

            if content:
                result = run_gogcli_with_expect("docs", "create", ["--title", title, "--content", content], account)
            else:
                result = run_gogcli_with_expect("docs", "create", ["--title", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_read":
            doc_id = arguments["doc_id"]
            result = run_gogcli_with_expect("docs", "get", ["--id", doc_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_append":
            doc_id = arguments["doc_id"]
            text = arguments["text"]
            result = run_gogcli_with_expect("docs", "append", ["--id", doc_id, "--text", text], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_delete":
            doc_id = arguments["doc_id"]
            result = run_gogcli_with_expect("docs", "delete", ["--id", doc_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # SLIDES TOOLS
        elif name == "slides_create":
            title = arguments["title"]
            result = run_gogcli_with_expect("slides", "create", ["--title", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "slides_read":
            pres_id = arguments["presentation_id"]
            result = run_gogcli_with_expect("slides", "get", ["--id", pres_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "slides_delete":
            pres_id = arguments["presentation_id"]
            result = run_gogcli_with_expect("slides", "delete", ["--id", pres_id], account)
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

            result = run_gogcli_with_expect("calendar", "create", args, account)
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

            result = run_gogcli_with_expect("calendar", "list", args, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "calendar_delete_event":
            event_id = arguments["event_id"]
            result = run_gogcli_with_expect("calendar", "delete", ["--id", event_id], account)
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

            result = run_gogcli_with_expect("calendar", "update", args, account)
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

    # Create SSE app
    sse_transport = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="google-workspace-gogcli-server",
                    server_version="0.2.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    # Create ASGI app
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.middleware.cors import CORSMiddleware

    app = Starlette(routes=[
        Route("/sse", endpoint=handle_sse),
    ])

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    print(f"\n🚀 Google Workspace MCP Server (gogcli backend)")
    print(f"📡 Server running on http://localhost:{port}/sse")
    print(f"📧 Using gogcli with account: {DEFAULT_ACCOUNT or 'default'}")
    print(f"🔧 HTML email support: FIXED (using --body-html with expect)")

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
