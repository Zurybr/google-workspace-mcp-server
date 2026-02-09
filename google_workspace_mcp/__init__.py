"""
Google Workspace MCP Server

An MCP (Model Context Protocol) server that provides tools for interacting with
Google Workspace services via gogcli CLI.

Supported services:
- Gmail: send, list, search, read, label, archive, delete emails (with HTML support)
- Sheets: create, read, write, append, delete spreadsheets
- Docs: create, read, append, delete documents
- Slides: create, read, delete presentations
- Calendar: create, list, update, delete events
"""

__version__ = "0.2.0"

# Export main servers
from google_workspace_mcp.gogcli_server import server as gogcli_server
from google_workspace_mcp.server import server as oauth_server

__all__ = ["gogcli_server", "oauth_server"]
