"""
Google Workspace MCP Server - OAuth Version

An MCP server that provides tools for interacting with Google Workspace services
using direct Google APIs with OAuth 2.0 authentication.
"""

import asyncio
import os
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

from google_workspace_mcp.auth import GoogleAuth, get_auth


# Create server instance
server = Server("google-workspace-mcp-server")

# Global auth instance
_auth: GoogleAuth | None = None


def get_auth_instance() -> GoogleAuth:
    """Get or create the auth instance"""
    global _auth
    if _auth is None:
        _auth = GoogleAuth()
    return _auth


# =============================================
# SERVICES
# =============================================

async def get_gmail_service():
    """Get authenticated Gmail service"""
    import googleapiclient.discovery as discovery

    credentials = get_auth_instance().get_credentials()
    return discovery.build("gmail", "v1", credentials=credentials)


async def get_sheets_service():
    """Get authenticated Sheets service"""
    import googleapiclient.discovery as discovery

    credentials = get_auth_instance().get_credentials()
    return discovery.build("sheets", "v4", credentials=credentials)


async def get_docs_service():
    """Get authenticated Docs service"""
    import googleapiclient.discovery as discovery

    credentials = get_auth_instance().get_credentials()
    return discovery.build("docs", "v1", credentials=credentials)


async def get_drive_service():
    """Get authenticated Drive service"""
    import googleapiclient.discovery as discovery

    credentials = get_auth_instance().get_credentials()
    return discovery.build("drive", "v3", credentials=credentials)


async def get_slides_service():
    """Get authenticated Slides service"""
    import googleapiclient.discovery as discovery

    credentials = get_auth_instance().get_credentials()
    return discovery.build("slides", "v1", credentials=credentials)


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
            "description": "General information about the Google Workspace MCP server",
            "mimeType": "text/plain",
        },
        {
            "uri": "workspace://stats",
            "name": "Usage Statistics",
            "description": "Server usage statistics and status",
            "mimeType": "application/json",
        },
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource"""
    if uri == "workspace://info":
        return """Google Workspace MCP Server v0.1.0 (OAuth Edition)

This server provides tools for interacting with Google Workspace services:
- Gmail: Send, read, search emails
- Sheets: Create, read, write spreadsheets
- Docs: Create, read documents
- Drive: List, create, share files and folders
- Slides: Create presentations

Requirements:
- GOOGLE_OAUTH_CLIENT_ID environment variable
- GOOGLE_OAUTH_CLIENT_SECRET environment variable

Authentication uses OAuth 2.0 - you'll be prompted to authenticate in your browser
on first use.
"""
    elif uri == "workspace://stats":
        import json
        from datetime import datetime

        stats = {
            "server_version": "0.1.0",
            "auth_type": "OAuth 2.0",
            "timestamp": datetime.utcnow().isoformat(),
            "services": ["gmail", "sheets", "docs", "drive", "slides"],
            "transport": "stdio",
        }
        return json.dumps(stats, indent=2)
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
            name="gmail_list_emails",
            description="List recent emails from Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of emails to return (default: 10)",
                        "default": 10,
                    }
                },
            },
        ),
        Tool(
            name="gmail_send_email",
            description="Send an email via Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body (plain text)",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        ),
        Tool(
            name="gmail_search_emails",
            description="Search for emails in Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (Gmail search syntax)",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="gmail_read_email",
            description="Read a full email by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Gmail message ID",
                    },
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
                    "title": {
                        "type": "string",
                        "description": "Spreadsheet title",
                    },
                    "data": {
                        "type": "array",
                        "description": "Initial data as 2D array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="sheets_read",
            description="Read data from a Google Sheets spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "Spreadsheet ID",
                    },
                    "range": {
                        "type": "string",
                        "description": "Cell range (e.g., 'Sheet1!A1:D10')",
                        "default": "Sheet1!A1",
                    },
                },
                "required": ["spreadsheet_id"],
            },
        ),
        Tool(
            name="sheets_write",
            description="Write data to a Google Sheets spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "Spreadsheet ID",
                    },
                    "range": {
                        "type": "string",
                        "description": "Cell range (e.g., 'Sheet1!A1:D10')",
                    },
                    "values": {
                        "type": "array",
                        "description": "Data to write as 2D array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                "required": ["spreadsheet_id", "range", "values"],
            },
        ),
        Tool(
            name="sheets_append",
            description="Append rows to a Google Sheets spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "Spreadsheet ID",
                    },
                    "range": {
                        "type": "string",
                        "description": "Range to append to (e.g., 'Sheet1!A1')",
                    },
                    "values": {
                        "type": "array",
                        "description": "Rows to append as 2D array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                "required": ["spreadsheet_id", "values"],
            },
        ),
        # DOCS TOOLS
        Tool(
            name="docs_create",
            description="Create a new Google Docs document",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Document title",
                    },
                    "content": {
                        "type": "string",
                        "description": "Document content",
                    },
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="docs_read",
            description="Read a Google Docs document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document ID",
                    },
                },
                "required": ["document_id"],
            },
        ),
        # DRIVE TOOLS
        Tool(
            name="drive_list_files",
            description="List files in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results (default: 20)",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="drive_create_file",
            description="Create a file in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "File name",
                    },
                    "mime_type": {
                        "type": "string",
                        "description": "MIME type (e.g., 'application/vnd.google-apps.document')",
                    },
                    "content": {
                        "type": "string",
                        "description": "File content (for docs)",
                    },
                },
                "required": ["name", "mime_type"],
            },
        ),
        Tool(
            name="drive_share_file",
            description="Share a file with another user",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "File ID to share",
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address to share with",
                    },
                    "role": {
                        "type": "string",
                        "description": "Permission role (reader, writer, owner)",
                        "enum": ["reader", "writer", "owner"],
                        "default": "reader",
                    },
                },
                "required": ["file_id", "email"],
            },
        ),
        # SLIDES TOOLS
        Tool(
            name="slides_create",
            description="Create a new Google Slides presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Presentation title",
                    },
                },
                "required": ["title"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    try:
        # GMAIL
        if name == "gmail_list_emails":
            service = await get_gmail_service()
            results = service.users().messages().list(
                userId="me",
                maxResults=arguments.get("max_results", 10)
            ).execute()
            messages = results.get("messages", [])
            return [TextContent(
                type="text",
                text=f"Found {len(messages)} recent emails. Message IDs: {[m['id'] for m in messages]}"
            )]

        elif name == "gmail_send_email":
            import base64
            from email.message import EmailMessage

            service = await get_gmail_service()
            message = EmailMessage()
            message.set_content(arguments["body"])
            message["To"] = arguments["to"]
            message["Subject"] = arguments["subject"]

            encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(
                userId="me",
                body={"raw": encoded}
            ).execute()
            return [TextContent(type="text", text="Email sent successfully")]

        elif name == "gmail_search_emails":
            service = await get_gmail_service()
            results = service.users().messages().list(
                userId="me",
                q=arguments["query"]
            ).execute()
            messages = results.get("messages", [])
            return [TextContent(
                type="text",
                text=f"Found {len(messages)} emails matching query: {arguments['query']}"
            )]

        elif name == "gmail_read_email":
            service = await get_gmail_service()
            msg = service.users().messages().get(
                userId="me",
                id=arguments["message_id"],
                format="full"
            ).execute()
            return [TextContent(
                type="text",
                text=f"Email data: {msg.get('snippet', 'No snippet available')}"
            )]

        # SHEETS
        elif name == "sheets_create":
            service = await get_sheets_service()
            data = arguments.get("data")

            if data:
                # Create with data
                body = {
                    "properties": {"title": arguments["title"]},
                    "sheets": [{
                        "data": [{
                            "rowData": [{"values": [{"userEnteredValue": {"stringValue": v}} for v in row]} for row in data]
                        }]
                    }]
                }
            else:
                body = {"properties": {"title": arguments["title"]}}

            spreadsheet = service.spreadsheets().create(body=body).execute()
            return [TextContent(
                type="text",
                text=f"Created spreadsheet: {spreadsheet['spreadsheetUrl']}\nID: {spreadsheet['spreadsheetId']}"
            )]

        elif name == "sheets_read":
            service = await get_sheets_service()
            result = service.spreadsheets().values().get(
                spreadsheetId=arguments["spreadsheet_id"],
                range=arguments.get("range", "Sheet1!A1")
            ).execute()
            values = result.get("values", [])
            return [TextContent(
                type="text",
                text=f"Data: {values}"
            )]

        elif name == "sheets_write":
            service = await get_sheets_service()
            body = {"values": arguments["values"]}
            service.spreadsheets().values().update(
                spreadsheetId=arguments["spreadsheet_id"],
                range=arguments["range"],
                valueInputOption="RAW",
                body=body
            ).execute()
            return [TextContent(type="text", text="Data written successfully")]

        elif name == "sheets_append":
            service = await get_sheets_service()
            body = {"values": arguments["values"]}
            service.spreadsheets().values().append(
                spreadsheetId=arguments["spreadsheet_id"],
                range=arguments.get("range", "Sheet1!A1"),
                valueInputOption="RAW",
                body=body
            ).execute()
            return [TextContent(type="text", text="Rows appended successfully")]

        # DOCS
        elif name == "docs_create":
            service = await get_docs_service()
            body = {
                "title": arguments["title"]
            }
            if arguments.get("content"):
                body["body"] = {
                    "content": [{
                        "paragraph": {
                            "elements": [{
                                "textRun": {"content": arguments["content"]}
                            }]
                        }
                    }]
                }
            doc = service.documents().create(body=body).execute()
            return [TextContent(
                type="text",
                text=f"Created document: https://docs.google.com/document/d/{doc['documentId']}/edit"
            )]

        elif name == "docs_read":
            service = await get_docs_service()
            doc = service.documents().get(
                documentId=arguments["document_id"]
            ).execute()
            content = doc.get("body", {}).get("content", [])
            text = "".join([
                elem.get("paragraph", {}).get("elements", [{}])[0].get("textRun", {}).get("content", "")
                for elem in content if "paragraph" in str(elem)
            ])
            return [TextContent(type="text", text=text or "Empty document")]

        # DRIVE
        elif name == "drive_list_files":
            service = await get_drive_service()
            results = service.files().list(
                q=arguments.get("query", ""),
                pageSize=arguments.get("max_results", 20),
                fields="files(id,name,mimeType)"
            ).execute()
            files = results.get("files", [])
            output = "\n".join([f"{f['name']} ({f['mimeType']}) - ID: {f['id']}" for f in files])
            return [TextContent(type="text", text=output or "No files found")]

        elif name == "drive_create_file":
            service = await get_drive_service()
            body = {
                "name": arguments["name"],
                "mimeType": arguments["mime_type"]
            }
            file = service.files().create(body=body, fields="id,name,webViewLink").execute()
            return [TextContent(
                type="text",
                text=f"Created file: {file['webViewLink']}\nID: {file['id']}"
            )]

        elif name == "drive_share_file":
            service = await get_drive_service()
            body = {
                "role": arguments.get("role", "reader"),
                "type": "user",
                "emailAddress": arguments["email"]
            }
            service.permissions().create(
                fileId=arguments["file_id"],
                body=body,
                sendNotificationEmail=False
            ).execute()
            return [TextContent(
                type="text",
                text=f"File shared with {arguments['email']} as {arguments.get('role', 'reader')}"
            )]

        # SLIDES
        elif name == "slides_create":
            service = await get_slides_service()
            body = {
                "title": arguments["title"]
            }
            presentation = service.presentations().create(body=body).execute()
            return [TextContent(
                type="text",
                text=f"Created presentation: https://docs.google.com/presentation/d/{presentation['presentationId']}/edit"
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


# =============================================
# MAIN ENTRY POINT
# =============================================

async def main():
    """Main entry point for the MCP server"""
    # Verify environment variables are set
    if not os.getenv("GOOGLE_OAUTH_CLIENT_ID") or not os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"):
        print("\n" + "="*60)
        print("GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET")
        print("environment variables are not set!")
        print("\nPlease run ./install.sh to set up OAuth credentials.")
        print("="*60 + "\n")
        raise ValueError(
            "GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET environment variables are not set. "
            "Please run ./install.sh to set up OAuth credentials."
        )

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="google-workspace-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
