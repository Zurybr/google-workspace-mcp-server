#!/usr/bin/env python3
"""
Cliente Python para Google Workspace API
Usar desde servidor Linux para interactuar con Google Workspace + Maps
"""

import requests
import json
import sys
from typing import Any, Dict, List, Optional


class WorkspaceAPI:
    """Cliente para Google Workspace API via Google Apps Script"""

    def __init__(self, script_url: str):
        """
        Inicializar cliente

        Args:
            script_url: URL de la Web App de Google Apps Script
        """
        self.url = script_url
        self.session = requests.Session()

    def _call(self, service: str, action: str, **params) -> Dict[str, Any]:
        """
        Llamada genérica a la API

        Args:
            service: Nombre del servicio (gmail, sheets, maps, etc.)
            action: Acción a ejecutar
            **params: Parámetros adicionales

        Returns:
            Dict con respuesta de la API
        """
        payload = {"service": service, "action": action}
        payload.update(params)

        try:
            response = self.session.post(
                self.url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    # =============================================
    # GMAIL
    # =============================================

    def list_emails(self, max_results: int = 10) -> Dict[str, Any]:
        """Lista emails recientes"""
        return self._call("gmail", "list", max=max_results)

    def send_email(
        self,
        to: str,
        subject: str,
        body: str = "",
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envía un email"""
        params = {"to": to, "subject": subject, "body": body}
        if html:
            params["html"] = html
        return self._call("gmail", "send", **params)

    def search_emails(self, query: str) -> Dict[str, Any]:
        """Busca emails"""
        return self._call("gmail", "search", query=query)

    def read_email(self, message_id: str) -> Dict[str, Any]:
        """Lee un email completo"""
        return self._call("gmail", "read", id=message_id)

    # =============================================
    # SHEETS
    # =============================================

    def create_sheet(
        self,
        title: str,
        data: Optional[List[List[Any]]] = None
    ) -> Dict[str, Any]:
        """Crea una nueva hoja de cálculo"""
        return self._call("sheets", "create", title=title, data=data)

    def read_sheet(
        self,
        sheet_id: str,
        range_str: str = "A1"
    ) -> Dict[str, Any]:
        """Lee datos de una hoja"""
        return self._call("sheets", "read", sheetId=sheet_id, range=range_str)

    def write_sheet(
        self,
        sheet_id: str,
        range_str: str,
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """Escribe datos en una hoja"""
        return self._call(
            "sheets",
            "write",
            sheetId=sheet_id,
            range=range_str,
            values=values
        )

    def append_row(
        self,
        sheet_id: str,
        row_data: List[Any]
    ) -> Dict[str, Any]:
        """Agrega una fila a una hoja"""
        return self._call("sheets", "append", sheetId=sheet_id, data=row_data)

    # =============================================
    # DOCS
    # =============================================

    def create_doc(
        self,
        title: str,
        content: str = ""
    ) -> Dict[str, Any]:
        """Crea un documento de Google Docs"""
        return self._call("docs", "create", title=title, content=content)

    def read_doc(self, doc_id: str) -> Dict[str, Any]:
        """Lee un documento"""
        return self._call("docs", "read", id=doc_id)

    # =============================================
    # DRIVE
    # =============================================

    def list_files(
        self,
        query: str = "",
        max_results: int = 20
    ) -> Dict[str, Any]:
        """Lista archivos en Drive"""
        return self._call("drive", "list", query=query, max=max_results)

    def create_file(
        self,
        name: str,
        file_type: str = "document",
        content: str = ""
    ) -> Dict[str, Any]:
        """Crea un archivo en Drive"""
        return self._call(
            "drive",
            "create",
            name=name,
            type=file_type,
            content=content
        )

    def create_folder(self, name: str) -> Dict[str, Any]:
        """Crea una carpeta en Drive"""
        return self._call("drive", "create", name=name, type="folder")

    def share_file(self, file_id: str, email: str) -> Dict[str, Any]:
        """Comparte un archivo"""
        return self._call("drive", "share", id=file_id, email=email)

    # =============================================
    # SLIDES
    # =============================================

    def create_presentation(
        self,
        title: str,
        content: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Crea una presentación"""
        return self._call("slides", "create", title=title, content=content)

    # =============================================
    # MAPS
    # =============================================

    def geocode(self, address: str) -> Dict[str, Any]:
        """
        Convierte una dirección en coordenadas

        Args:
            address: Dirección a geocodificar

        Returns:
            Dict con lat, lng y formatted_address
        """
        result = self._call("maps", "geocode", address=address)
        if result.get("success"):
            return {
                "success": True,
                "lat": result["location"]["lat"],
                "lng": result["location"]["lng"],
                "address": result["address"]
            }
        return result

    def distance(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Calcula distancia entre dos puntos

        Returns:
            Dict con distance (texto y valor en metros)
            y duration (texto y valor en segundos)
        """
        return self._call("maps", "distance", origin=origin, destination=destination)

    def route(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Obtiene ruta óptima entre dos puntos

        Returns:
            Dict con summary, distance, duration y pasos detallados
        """
        return self._call("maps", "route", origin=origin, destination=destination)

    def static_map(
        self,
        center: str,
        zoom: int = 13
    ) -> Dict[str, Any]:
        """Genera URL de mapa estático (requiere API Key)"""
        return self._call("maps", "static", center=center, zoom=zoom)

    # =============================================
    # KEEP
    # =============================================

    def create_note(
        self,
        title: str,
        content: str = ""
    ) -> Dict[str, Any]:
        """Crea una nota en Google Keep"""
        return self._call("keep", "create", title=title, content=content)


# =============================================
# CLI / Ejemplos de uso
# =============================================

def main():
    """Ejemplos de uso del cliente"""

    # Configurar URL de tu script
    # Reemplaza con tu URL real
    SCRIPT_URL = "https://script.google.com/macros/s/TU_SCRIPT_ID/exec"

    api = WorkspaceAPI(SCRIPT_URL)

    # Ejemplo 1: Geocoding
    print("\n=== Geocoding ===")
    result = api.geocode("Zócalo, Ciudad de México")
    if result.get("success"):
        print(f"Dirección: {result['address']}")
        print(f"Coordenadas: {result['lat']}, {result['lng']}")
    else:
        print(f"Error: {result}")

    # Ejemplo 2: Calcular distancia
    print("\n=== Distancia ===")
    result = api.distance(
        "Ciudad de México, CDMX",
        "Guadalajara, Jalisco"
    )
    if result.get("success"):
        print(f"Distancia: {result['distance']['text']}")
        print(f"Duración: {result['duration']['text']}")
    else:
        print(f"Error: {result}")

    # Ejemplo 3: Crear hoja de cálculo
    print("\n=== Crear Sheet ===")
    result = api.create_sheet(
        "Prueba API",
        data=[
            ["Nombre", "Email", "Ciudad"],
            ["Juan Pérez", "juan@example.com", "CDMX"],
            ["María López", "maria@example.com", "Monterrey"]
        ]
    )
    if result.get("success"):
        print(f"Sheet creada: {result['url']}")
    else:
        print(f"Error: {result}")

    # Ejemplo 4: Enviar email
    print("\n=== Enviar Email ===")
    result = api.send_email(
        to="ejemplo@test.com",
        subject="Prueba desde API",
        body="Este es un email de prueba enviado desde Google Apps Script"
    )
    print(result)

    # Ejemplo 5: Crear nota en Keep
    print("\n=== Crear Nota Keep ===")
    result = api.create_note(
        "Lista de tareas",
        "1. Terminar proyecto\n2. Revisar emails\n3. Actualizar documentación"
    )
    print(result)

    # Ejemplo 6: Ruta con instrucciones
    print("\n=== Ruta Detallada ===")
    result = api.route("Polanco, CDMX", "Roma Norte, CDMX")
    if result.get("success"):
        print(f"Ruta: {result['summary']}")
        print(f"Distancia: {result['distance']}")
        print(f"Duración: {result['duration']}")
        print("\nInstrucciones:")
        for i, step in enumerate(result['steps'], 1):
            print(f"{i}. {step['instruction']} ({step['distance']})")


if __name__ == "__main__":
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python client.py                    # Ejemplos")
        print("  python client.py test               # Modo pruebas")
        print("  python client.py <url>              # Usar URL específica")
        print("\nVariables de entorno:")
        print("  WORKSPACE_API_URL                   # URL del script")
        sys.exit(1)

    # Obtener URL
    if sys.argv[1] == "test":
        # Modo test - usa variable de entorno
        import os
        url = os.environ.get("WORKSPACE_API_URL")
        if not url:
            print("Error: Define WORKSPACE_API_URL")
            print("export WORKSPACE_API_URL='https://script.google.com/macros/s/.../exec'")
            sys.exit(1)
        SCRIPT_URL = url
    else:
        SCRIPT_URL = sys.argv[1]

    api = WorkspaceAPI(SCRIPT_URL)

    # Test de conexión
    print("🔍 Probando conexión...")
    result = api._call("test", "ping")

    if result.get("status") == "ok":
        print(f"✅ Conexión exitosa!")
        print(f"📅 Timestamp: {result.get('timestamp')}")

        # Listar acciones disponibles
        if "available_actions" in result:
            print(f"\n📋 Acciones disponibles: {', '.join(result['available_actions'][:5])}...")
    else:
        print(f"❌ Error de conexión: {result}")
        sys.exit(1)

    # Ejecutar ejemplos
    main()
