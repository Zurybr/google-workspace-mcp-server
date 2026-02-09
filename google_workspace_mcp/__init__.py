"""
Google Workspace MCP Server

An MCP (Model Context Protocol) server that provides tools for interacting with
Google Workspace services via Google Apps Script.

Supported services:
- Gmail: list, send, search, read emails
- Sheets: read, write, create, append rows
- Docs: create, read documents
- Drive: list, create, share files and folders
- Slides: create presentations
- Maps: geocoding, distance, directions
- Keep: create notes
"""

__version__ = "0.1.0"

from google_workspace_mcp.server import GoogleWorkspaceMCPServer

__all__ = ["GoogleWorkspaceMCPServer"]
