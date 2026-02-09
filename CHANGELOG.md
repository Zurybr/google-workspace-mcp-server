# Changelog - Google Workspace MCP Server

## [0.2.1] - 2026-02-09

### Fixed - HTML Email Support (Critical)
- **Problem**: HTML emails were being sent as plain text due to using `--body-file` flag
- **Solution**: Implemented `--body-html` flag with expect variable shell expansion
- **Tested**: Message ID `19c4434e4fb9417f` confirmed working
- **Method**: Variable shell expansion (Prueba 6) - create temp file, read with expect, pass as `--body-html=$html_body`

### Added - Detach/Background Mode
- **New**: `--detach` flag to run server in background
- **Usage**: `./install.sh --server-only --detach`
- **Stop**: `pkill -f 'google_workspace_mcp.server_gogcli'`
- **Implementation**: Double-fork daemonization in Python

### Technical Details

#### HTML Email Fix
```python
# Before (broken - sends plain text)
args.extend(["--body", "Plain text", "--body-file", html_file])

# After (working - sends HTML)
run_gogcli_with_expect("gmail", "send", args, account, html_body=body)
```

#### Expect Script for HTML
```tcl
set html_body [exec cat /tmp/html_file]
spawn sh -c "gogcli gmail send ... --body-html=$html_body"
expect {
    "Enter passphrase" { send "\r"; exp_continue }
    eof
}
```

### Files Modified
- `google_workspace_mcp/gogcli_server.py`: HTML fix + detach mode
- `install.sh`: --detach flag support
- `README.md`: Updated documentation
- `send-html.sh`: Added working HTML email script (utility)

### Dependencies
- **expect**: Required for keyring passphrase automation (HTML emails)
- **gogcli**: v0.9.0+ (https://github.com/steipete/gogcli/releases)

---

## [0.2.0] - Previous Release
- Initial MCP server implementation
- Gmail, Sheets, Docs, Slides, Calendar support
- SSE server on port 9001