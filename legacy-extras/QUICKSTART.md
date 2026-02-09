# 🚀 Inicio Rápido - Google Workspace API

## 1. Crear y Publicar el Script (5 minutos)

### Paso 1: Crear el proyecto en Google Apps Script

1. Ve a [script.google.com](https://script.google.com)
2. Clic en **"Nuevo proyecto"**
3. Borra el código existente

### Paso 2: Copiar el código

1. Abre `Code.gs` de este proyecto
2. Copia TODO el contenido
3. Pégalo en el editor de Apps Script
4. `Ctrl+S` para guardar (nómbralo "Workspace API")

### Paso 3: Habilitar servicios

1. Clic en **"Servicios"** (+) al lado de "Archivos"
2. Habilita estos servicios:
   - ✅ **Gmail API**
   - ✅ **Google Sheets API**
   - ✅ **Google Docs API**
   - ✅ **Google Drive API**
   - ✅ **Google Slides API**
   - ✅ **Maps API**

### Paso 4: Publicar como Web App

1. Clic en **"Implementar"** → **"Nueva implementación"**
2. Selecciona **"Aplicación web"**
3. Configura:
   - Descripción: `API v1`
   - Ejecutar como: **Usuario que accede**
   - Quién tiene acceso: **Cualquier persona**
4. Clic en **"Implementar"**
5. **Autoriza** el acceso cuando te lo pida
6. **COPIA LA URL** (algo como `https://script.google.com/macros/s/AKfycb.../exec`)

## 2. Configurar en tu Servidor

### Opción A: Usar variable de entorno

```bash
export WORKSPACE_API_URL="https://script.google.com/macros/s/TU_SCRIPT_ID/exec"
```

### Opción B: Usar archivo .env

```bash
cp .env.example .env
nano .env  # Edita con tu URL
source .env
```

## 3. Probar la Conexión

### Con Python

```bash
cd /home/zurybr/workspace/google-workspace-api

python3 client.py test
```

### Con Bash

```bash
./examples.sh test
```

### Con curl

```bash
curl "$WORKSPACE_API_URL"
```

## 4. Primeros Ejemplos

### Geocoding (Dirección → Coordenadas)

```bash
./examples.sh maps_geocode "Zócalo, Ciudad de México"
```

Respuesta:
```json
{
  "service": "maps",
  "action": "geocode",
  "success": true,
  "address": "Plaza de la Constitución s/n, Centro Histórico, 06000 Ciudad de México, CDMX, Mexico",
  "location": {
    "lat": 19.4326,
    "lng": -99.1332
  }
}
```

### Calcular Distancia

```bash
./examples.sh maps_distance "CDMX" "Monterrey"
```

### Crear Hoja de Cálculo

```bash
./examples.sh sheets_create "Mis Clientes"
```

### Crear Nota en Keep

```bash
./examples.sh keep_create "Compras" "Leche\nPan\nHuevos\nCafé"
```

### Enviar Email

```bash
./examples.sh gmail_send "cliente@ejemplo.com" "Bienvenido" "Gracias por registrarte"
```

## 5. Ejemplos con Python

```python
from client import WorkspaceAPI

api = WorkspaceAPI("TU_URL_AQUI")

# Geocoding
result = api.geocode "Ángel de la Independencia, CDMX"
print(f"Coordenadas: {result['lat']}, {result['lng']}")

# Crear Sheet
sheet = api.create_sheet("Contactos 2026", [
    ["Nombre", "Email", "Teléfono"],
    ["Juan", "juan@example.com", "55-1234-5678"]
])
print(f"Sheet creada: {sheet['url']}")

# Enviar email
api.send_email(
    to="cliente@ejemplo.com",
    subject="Confirmación",
    body="Su pedido ha sido confirmado"
)

# Crear nota en Keep
api.create_note(
    title="Tareas de hoy",
    content="1. Llamar a proveedores\n2. Revisar inventario\n3. Enviar reporte"
)
```

## 6. Workflows Avanzados

### Geocodificar y Guardar en Sheet

```bash
./examples.sh workflow_geocode "Palacio de Bellas Artes, CDMX"
```

### Reporte de Distancias Múltiples

```bash
./examples.sh workflow_distances "CDMX" "Monterrey" "Guadalajara" "Puebla" "Querétaro"
```

Esto crea una Sheet con:
- Origen
- Destino
- Distancia
- Duración

## 7. Integración en tus Scripts

### Ejemplo: Script de Backup

```bash
#!/bin/bash
source /home/zurybr/workspace/google-workspace-api/.env

# Crear Sheet de backup
RESULT=$(./examples.sh sheets_create "Backup $(date +%Y-%m-%d)")

# Enviar notificación
./examples.sh gmail_send \
    "admin@tuempresa.com" \
    "Backup completado" \
    "Backup realizado exitosamente"
```

### Ejemplo: Bot de Telegram

```python
import requests
from client import WorkspaceAPI

api = WorkspaceAPI(WORKSPACE_API_URL)

def handle_address(address):
    """Geocodificar dirección enviada a Telegram"""
    result = api.geocode(address)
    if result.get('success'):
        msg = f"📍 {result['address']}\n"
        msg += f"📌 Lat: {result['lat']}, Lng: {result['lng']}"
        return msg
    return "No encontré esa dirección"
```

## 8. Troubleshooting

### Error: "Script function not found"
- **Solución**: Verifica que copiaste TODO el código de Code.gs
- **Solución**: Re-publica la Web App

### Error: "You do not have permission"
- **Solución**: Re-publica con "Quién tiene acceso: Cualquier persona"

### Error de autenticación
- **Solución**: Abre el editor de Apps Script y ejecuta `testAllServices()`
- **Solución**: Acepta los permisos que te pida

### Timeout en requests largos
- **Solución**: Google Apps Script tiene limite de 6 minutos
- **Solución**: Divide operaciones grandes en varios requests

## 9. Próximos Pasos

1. **Personaliza CONFIG** en Code.gs con tus Sheet IDs
2. **Crea workflows** específicos para tus necesidades
3. **Integra con tus scripts** existentes
4. **Explora más funciones** de cada servicio

## 10. Referencia Rápida de Servicios

| Servicio | Funciones Principales |
|----------|----------------------|
| **Gmail** | list, send, search, read |
| **Sheets** | create, read, write, append |
| **Docs** | create, read |
| **Drive** | list, create, share |
| **Slides** | create |
| **Maps** | geocode, distance, route |
| **Keep** | create |

---

**¿Necesitas ayuda?** Revisa [README.md](README.md) para documentación completa
