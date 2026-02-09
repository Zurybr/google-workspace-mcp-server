# MEMORY - Zurybr Context

## MCP Server Fix (Feb 2026)

### Error 500 en `/messages` endpoint
- **Problema**: Starlette SSE integration con `request._send` (no existe)
- **Solución**: Reescribir usando ASGI puro con SSE transport
- **Archivo**: `google_workspace_mcp/gogcli_server.py`

### Tools de diagnóstico agregadas
- `gogcli_status` - Verificar estado de autenticación
- `gogcli_version` - Obtener versión de gogcli

### Comandos útiles
```bash
# Verificar health
curl http://localhost:9001/health

# Reiniciar servidor
pkill -f gogcli_server.py
python3 google_workspace_mcp/gogcli_server.py --server-only --port 9001 --detach

# Verificar proceso
ps aux | grep gogcli_server
```

### Validación
- 25 tools MCP disponibles
- gogcli autenticado
- Health endpoint funciona

---

## FastMCP vs MCP Puro (Feb 2026)

### FastMCP - RECOMENDADO para nuevos servidores
```python
from fastmcp import FastMCP

mcp = FastMCP("nombre")

@mcp.tool()
def mi_tool(param: str, limit: int = 5) -> str:
    """Descripción automática desde docstring."""
    return "resultado"

mcp.run(transport="sse", host="0.0.0.0", port=9001)
```

### Patrones de Egregore
- **Singleton**: `fcntl.flock(LOCK_EX | LOCK_NB)` para evitar múltiples instancias
- **Logging**: `FileHandler + StreamHandler` con formato estructurado
- **Signals**: `signal.signal(SIGTERM, handler)` para shutdown limpio
- **Returns**: `json.dumps(result, indent=2, default=str)` para consistencia

### Cuando usar cada uno
- **FastMCP**: Default - simple, menos bugs, type hints automáticos
- **MCP puro**: Solo cuando necesitas control total o mínimas dependencias
