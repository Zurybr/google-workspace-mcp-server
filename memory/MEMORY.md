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
