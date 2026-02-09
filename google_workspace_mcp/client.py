"""
Google Apps Script Web App Client

Handles communication with the Google Apps Script Web App backend.
"""

import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx


class GoogleAppsScriptClient:
    """Client for interacting with Google Apps Script Web App"""

    def __init__(self, script_url: Optional[str] = None):
        """
        Initialize the client

        Args:
            script_url: URL of the Google Apps Script Web App.
                       If not provided, reads from GOOGLE_APPS_SCRIPT_URL env var.
        """
        self.script_url = script_url or os.getenv("GOOGLE_APPS_SCRIPT_URL")
        if not self.script_url:
            raise ValueError(
                "Google Apps Script URL not provided. "
                "Set GOOGLE_APPS_SCRIPT_URL environment variable or pass script_url parameter."
            )

        self.timeout = 30.0

    async def _call(
        self,
        service: str,
        action: str,
        **params: Any
    ) -> Dict[str, Any]:
        """
        Make a call to the Google Apps Script Web App

        Args:
            service: The service to call (gmail, sheets, docs, etc.)
            action: The action to perform
            **params: Additional parameters for the action

        Returns:
            Dict with the response from the API
        """
        payload = {
            "service": service,
            "action": action,
            **params
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.script_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {
                    "success": False,
                    "error": f"HTTP error: {e.response.status_code}",
                    "details": str(e)
                }
            except httpx.RequestError as e:
                return {
                    "success": False,
                    "error": f"Request error: {str(e)}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }

    # =============================================
    # GMAIL
    # =============================================

    async def list_emails(self, max_results: int = 10) -> Dict[str, Any]:
        """List recent emails"""
        return await self._call("gmail", "list", max=max_results)

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an email"""
        params = {"to": to, "subject": subject, "body": body}
        if html:
            params["html"] = html
        return await self._call("gmail", "send", **params)

    async def search_emails(self, query: str) -> Dict[str, Any]:
        """Search emails"""
        return await self._call("gmail", "search", query=query)

    async def read_email(self, message_id: str) -> Dict[str, Any]:
        """Read a full email"""
        return await self._call("gmail", "read", id=message_id)

    # =============================================
    # SHEETS
    # =============================================

    async def create_sheet(
        self,
        title: str,
        data: Optional[List[List[Any]]] = None
    ) -> Dict[str, Any]:
        """Create a new spreadsheet"""
        return await self._call("sheets", "create", title=title, data=data)

    async def read_sheet(
        self,
        sheet_id: str,
        range_str: str = "A1"
    ) -> Dict[str, Any]:
        """Read data from a spreadsheet"""
        return await self._call("sheets", "read", sheetId=sheet_id, range=range_str)

    async def write_sheet(
        self,
        sheet_id: str,
        range_str: str,
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """Write data to a spreadsheet"""
        return await self._call(
            "sheets",
            "write",
            sheetId=sheet_id,
            range=range_str,
            values=values
        )

    async def append_row(
        self,
        sheet_id: str,
        row_data: List[Any]
    ) -> Dict[str, Any]:
        """Append a row to a spreadsheet"""
        return await self._call("sheets", "append", sheetId=sheet_id, data=row_data)

    # =============================================
    # DOCS
    # =============================================

    async def create_doc(
        self,
        title: str,
        content: str = ""
    ) -> Dict[str, Any]:
        """Create a Google Doc"""
        return await self._call("docs", "create", title=title, content=content)

    async def read_doc(self, doc_id: str) -> Dict[str, Any]:
        """Read a Google Doc"""
        return await self._call("docs", "read", id=doc_id)

    # =============================================
    # DRIVE
    # =============================================

    async def list_files(
        self,
        query: str = "",
        max_results: int = 20
    ) -> Dict[str, Any]:
        """List files in Drive"""
        return await self._call("drive", "list", query=query, max=max_results)

    async def create_file(
        self,
        name: str,
        file_type: str = "document",
        content: str = ""
    ) -> Dict[str, Any]:
        """Create a file in Drive"""
        return await self._call(
            "drive",
            "create",
            name=name,
            type=file_type,
            content=content
        )

    async def create_folder(self, name: str) -> Dict[str, Any]:
        """Create a folder in Drive"""
        return await self._call("drive", "create", name=name, type="folder")

    async def share_file(self, file_id: str, email: str) -> Dict[str, Any]:
        """Share a file"""
        return await self._call("drive", "share", id=file_id, email=email)

    # =============================================
    # SLIDES
    # =============================================

    async def create_presentation(
        self,
        title: str,
        content: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a presentation"""
        return await self._call("slides", "create", title=title, content=content)

    # =============================================
    # MAPS
    # =============================================

    async def geocode(self, address: str) -> Dict[str, Any]:
        """
        Convert an address to coordinates

        Returns:
            Dict with lat, lng, and formatted_address
        """
        result = await self._call("maps", "geocode", address=address)
        if result.get("success") and "location" in result:
            return {
                "success": True,
                "lat": result["location"]["lat"],
                "lng": result["location"]["lng"],
                "address": result.get("address", "")
            }
        return result

    async def distance(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Calculate distance between two points

        Returns:
            Dict with distance (text and value in meters)
            and duration (text and value in seconds)
        """
        return await self._call("maps", "distance", origin=origin, destination=destination)

    async def route(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Get optimal route between two points

        Returns:
            Dict with summary, distance, duration, and detailed steps
        """
        return await self._call("maps", "route", origin=origin, destination=destination)

    async def static_map(
        self,
        center: str,
        zoom: int = 13
    ) -> Dict[str, Any]:
        """Generate static map URL (requires API Key)"""
        return await self._call("maps", "static", center=center, zoom=zoom)

    # =============================================
    # KEEP
    # =============================================

    async def create_note(
        self,
        title: str,
        content: str = ""
    ) -> Dict[str, Any]:
        """Create a note in Google Keep"""
        return await self._call("keep", "create", title=title, content=content)
