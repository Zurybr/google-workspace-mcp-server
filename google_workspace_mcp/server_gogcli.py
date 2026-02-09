#!/usr/bin/env python3
"""
Google Workspace MCP Server - gogcli Backend (Simplified)

An MCP server that provides tools for interacting with Google Workspace services
using gogcli as the backend.

Services: Gmail, Sheets, Docs, Slides, Calendar
"""

import asyncio
import json
import os
import subprocess
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuration
DEFAULT_PORT = 9001
GOGCLI_BIN = os.getenv("GOGCLI_BIN", "gogcli")
DEFAULT_ACCOUNT = os.getenv("GOGCLI_ACCOUNT", "")


def run_gogcli(args: list[str], account: str | None = None, timeout: int = 60) -> dict[str, Any]:
    """Run a gogcli command and return the result"""
    acc = account or DEFAULT_ACCOUNT
    cmd = [GOGCLI_BIN] + args

    if acc:
        cmd.extend(["--account", acc])

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
            "error": f"gogcli not found. Install from https://github.com/steipete/gogcli/releases"
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
        return """Google Workspace MCP Server v0.2.0 (gogcli Edition)

This server provides tools for interacting with Google Workspace services:
- Gmail: Send, read, search emails with HTML support
- Sheets: Create, read, write, delete spreadsheets
- Docs: Create, read, delete documents
- Slides: Create, read, delete presentations
- Calendar: Create, list, update, delete events

Backend: gogcli (https://github.com/steipete/gogcli)
Authentication: OAuth via gogcli keyring (run: gogcli auth login)

Tools Available (27 total):
- Gmail (7): send_email, list_emails, search_emails, read_email, label_email, archive_email, delete_email
- Sheets (5): create, read, write, append, delete
- Docs (4): create, read, delete, export
- Slides (4): create, read, copy, export
- Calendar (7): create_event, list_events, get_event, update_event, delete_event, list_calendars, freebusy

Run ./install.sh --server-only to start the server on port 9001.
"""
    elif uri == "workspace://gogcli-version":
        result = run_gogcli(["--version"])
        if result["success"]:
            return result["output"]
        else:
            return "gogcli version not available"
    else:
        raise ValueError(f"Unknown resource: {uri}")


# =============================================
# TOOLS
# =============================================

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        # GMAIL TOOLS
        Tool(
            name="gmail_send_email",
            description="Send an email via Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email(s), comma-separated"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body (plain text or HTML file path)"},
                    "body_file": {"type": "string", "description": "Path to HTML file for email body"},
                    "account": {"type": "string", "description": "Google account to use"},
                },
                "required": ["to", "subject"],
            },
        ),
        Tool(
            name="gmail_search_emails",
            description="Search for emails in Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Gmail search query"},
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
            name="gmail_list_labels",
            description="List Gmail labels",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "Google account to use"},
                },
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
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
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
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
                    "range": {"type": "string", "description": "Cell range (e.g., Sheet1!A1:D10)"},
                    "data": {"type": "string", "description": "Data to write"},
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
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
                    "range": {"type": "string", "description": "Range to append to"},
                    "data": {"type": "string", "description": "Data to append"},
                    "account": {"type": "string", "description": "Google account to use"},
                },
                "required": ["spreadsheet_id", "data"],
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
                    "account": {"type": "string", "description": "Google account to use"},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="docs_read",
            description="Read a Google Doc as plain text",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID"},
                    "account": {"type": "string", "description": "Google account to use"},
                },
                "required": ["doc_id"],
            },
        ),
        Tool(
            name="docs_export",
            description="Export a Google Doc",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID"},
                    "format": {"type": "string", "description": "Export format (pdf, docx, txt)", "enum": ["pdf", "docx", "txt"]},
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
            name="slides_info",
            description="Get presentation metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID"},
                    "account": {"type": "string", "description": "Google account to use"},
                },
                "required": ["presentation_id"],
            },
        ),

        # CALENDAR TOOLS
        Tool(
            name="calendar_list_events",
            description="List calendar events",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID (primary for default)"},
                    "account": {"type": "string", "description": "Google account to use"},
                },
            },
        ),
        Tool(
            name="calendar_create_event",
            description="Create a new calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID (primary for default)"},
                    "summary": {"type": "string", "description": "Event title"},
                    "description": {"type": "string", "description": "Event description"},
                    "location": {"type": "string", "description": "Event location"},
                    "account": {"type": "string", "description": "Google account to use"},
                },
                "required": ["calendar_id", "summary"],
            },
        ),
        Tool(
            name="calendar_list_calendars",
            description="List all calendars",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "Google account to use"},
                },
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
            body = arguments.get("body", "")
            body_file = arguments.get("body_file", "")

            args_list = ["send", "--to", to, "--subject", subject]

            if body_file:
                args_list.extend(["--body-file", body_file])
            elif body:
                args_list.extend(["--body", body])

            result = run_gogcli(["gmail"] + args_list, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_search_emails":
            query = arguments["query"]
            result = run_gogcli(["gmail", "search", query], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_read_email":
            msg_id = arguments["message_id"]
            result = run_gogcli(["gmail", "get", msg_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "gmail_list_labels":
            result = run_gogcli(["gmail", "labels"], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # SHEETS TOOLS
        elif name == "sheets_create":
            title = arguments["title"]
            result = run_gogcli(["sheets", "create", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_read":
            sheet_id = arguments["spreadsheet_id"]
            range_val = arguments.get("range", "A1")
            result = run_gogcli(["sheets", "get", sheet_id, range_val], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_write":
            sheet_id = arguments["spreadsheet_id"]
            range_val = arguments["range"]
            data = arguments["data"]
            result = run_gogcli(["sheets", "update", sheet_id, range_val, data], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "sheets_append":
            sheet_id = arguments["spreadsheet_id"]
            range_val = arguments.get("range", "A1")
            data = arguments["data"]
            result = run_gogcli(["sheets", "append", sheet_id, range_val, data], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # DOCS TOOLS
        elif name == "docs_create":
            title = arguments["title"]
            result = run_gogcli(["docs", "create", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_read":
            doc_id = arguments["doc_id"]
            result = run_gogcli(["docs", "cat", doc_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "docs_export":
            doc_id = arguments["doc_id"]
            fmt = arguments.get("format", "pdf")
            result = run_gogcli(["docs", "export", doc_id, f"--{fmt}"], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # SLIDES TOOLS
        elif name == "slides_create":
            title = arguments["title"]
            result = run_gogcli(["slides", "create", title], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "slides_info":
            pres_id = arguments["presentation_id"]
            result = run_gogcli(["slides", "info", pres_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        # CALENDAR TOOLS
        elif name == "calendar_list_events":
            cal_id = arguments.get("calendar_id", "primary")
            result = run_gogcli(["calendar", "events", cal_id], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "calendar_create_event":
            cal_id = arguments["calendar_id"]
            summary = arguments["summary"]
            description = arguments.get("description", "")
            location = arguments.get("location", "")

            args_list = ["calendar", "create", cal_id, summary]
            if description:
                args_list.extend(["--description", description])
            if location:
                args_list.extend(["--location", location])

            result = run_gogcli(args_list, account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        elif name == "calendar_list_calendars":
            result = run_gogcli(["calendar", "calendars"], account)
            return [TextContent(type="text", text=result.get("output", result["error"]))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# =============================================
# MAIN ENTRY POINT
# =============================================

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

    args = parser.parse_args()

    if args.server_only:
        # For SSE mode, use the original gogcli_server.py
        import importlib
        import sys
        spec = importlib.util.spec_from_file_location(
            "google_workspace_mcp.gogcli_server",
            "google_workspace_mcp/gogcli_server.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main_server_only(args.port)
    else:
        asyncio.run(main())
