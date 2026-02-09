# Detach/Background Mode - Documentation

## Overview

The MCP server can now run in **background/detached mode**, allowing it to continue running after closing the terminal.

## Usage

### Start in Background
```bash
./install.sh --server-only --detach
```

### Start on Custom Port (Background)
```bash
./install.sh --server-only 8080 --detach
```

### Stop Background Server
```bash
pkill -f 'google_workspace_mcp.server_gogcli'
```

## How It Works

The detach mode uses **double-fork daemonization**:

```python
def main_server_only(port: int = DEFAULT_PORT, detach: bool = False):
    # ... setup code ...

    if detach:
        print(f"✅ Server started in background mode (PID: {os.getpid()})")
        print(f"🛑 To stop: pkill -f 'google_workspace_mcp.server_gogcli'")
        sys.stdout.flush()

        # First fork
        if os.fork() > 0:
            os._exit(0)

        # Create new session
        os.setsid()

        # Second fork
        if os.fork() > 0:
            os._exit(0)

    # Continue as daemon
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
```

## Output

### Foreground Mode
```
🚀 Google Workspace MCP Server (gogcli backend)
📡 Server running on http://localhost:9001/sse
📧 Using gogcli with account: default
🔧 HTML email support: FIXED (using --body-html with expect)

Press Ctrl+C to stop

INFO:     Started server process [12345]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9001
```

### Detached Mode
```
🚀 Google Workspace MCP Server (gogcli backend)
📡 Server running on http://localhost:9001/sse
📧 Using gogcli with account: default
🔧 HTML email support: FIXED (using --body-html with expect)

✅ Server started in background mode (PID: 12345)
📝 Logs: Check journalctl or process output
🛑 To stop: pkill -f 'google_workspace_mcp.server_gogcli'
[process exits, server continues running]
```

## Checking Status

### Check if server is running
```bash
ps aux | grep google_workspace_mcp
```

### Check port is listening
```bash
lsof -i :9001
```

### Test server endpoint
```bash
curl http://localhost:9001/sse
```

## Logs

When running in detached mode, logs are handled by uvicorn's `log_level="warning"`. For more verbose logging, you can modify the log level in `gogcli_server.py`.

## Implementation Details

### Shell Script (install.sh)
```bash
start_server() {
    local port=${1:-9001}
    local detach=${2:-false}

    # ... setup code ...

    if [ "$detach" = "true" ]; then
        python -m google_workspace_mcp.server_gogcli --server-only --port "$port" --detach
    else
        python -m google_workspace_mcp.server_gogcli --server-only --port "$port"
    fi
}
```

### Python Server (gogcli_server.py)
```python
parser.add_argument("--detach", action="store_true", help="Run in background/detached mode")

# In main_server_only function
if args.server_only:
    main_server_only(args.port, args.detach)
```

## Troubleshooting

### Server won't start in detached mode
- Check if port is already in use: `lsof -i :9001`
- Check Python dependencies are installed
- Verify gogcli is authenticated

### Can't stop detached server
```bash
# Try different methods
pkill -f 'google_workspace_mcp.server_gogcli'
pkill -f 'python.*gogcli_server'
killall python3  # Use with caution
```

### Server stops immediately
- Check logs: `journalctl -u your-service` (if using systemd)
- Run in foreground mode first to see errors