# Google Workspace MCP Server

A Model Context Protocol (MCP) server that provides AI agents with access to Google Workspace services including Gmail, Sheets, Docs, Slides, and Calendar using **gogcli** as the backend.

## Features

- **Gmail**: Send, read, search, organize emails with HTML support
- **Sheets**: Create, read, write, delete spreadsheets and cells
- **Docs**: Create, read, edit, delete documents
- **Slides**: Create, read, delete presentations
- **Calendar**: Create, read, update, delete events

## Quick Start

### 1. Install gogcli

```bash
bash legacy-extras/install-gogcli.sh
```

Or download from [gogcli releases](https://github.com/steipete/gogcli/releases).

### 2. Authenticate gogcli

```bash
# Interactive authentication (opens browser)
gogcli auth login

# Manual authentication (for servers/CLI without browser)
gogcli auth login --manual
```

For `--manual` mode, follow the URL prompt and paste the authorization code when prompted.

### 3. Start the MCP Server

```bash
# Start on default port (9001) - foreground mode
./install.sh --server-only

# Start in background/detached mode
./install.sh --server-only --detach

# Start on custom port
./install.sh --server-only 8080

# Show help
./install.sh --help
```

## Usage

### Starting the Server

```bash
# Foreground mode (default)
./install.sh --server-only

# Background/detached mode
./install.sh --server-only --detach

# Custom port
./install.sh --server-only 8080

# Stop background server
pkill -f 'google_workspace_mcp.server_gogcli'
```

```bash
# Start on default port (9001)
./install.sh --server-only

# Start on custom port
./install.sh --server-only 8080

# Show help
./install.sh --help
```

### Interactive Installation

For first-time setup, run without arguments:

```bash
./install.sh
```

This will:
1. Check gogcli installation
2. Install Python dependencies
3. Create `.env` configuration file

## Available Tools

### Gmail

| Tool | Description |
|------|-------------|
| `gmail_send_email` | Send an email (supports HTML via `html:true` - FIXED using `--body-html`) |
| `gmail_list_emails` | List recent emails |
| `gmail_search_emails` | Search emails with query |
| `gmail_read_email` | Read a full email by ID |
| `gmail_label_email` | Add/remove labels from email |
| `gmail_archive_email` | Archive an email |
| `gmail_delete_email` | Delete an email |

### Sheets

| Tool | Description |
|------|-------------|
| `sheets_create` | Create a new spreadsheet |
| `sheets_read` | Read data from spreadsheet |
| `sheets_write` | Write data to cells |
| `sheets_append` | Append rows to spreadsheet |
| `sheets_delete` | Delete a spreadsheet |

### Docs

| Tool | Description |
|------|-------------|
| `docs_create` | Create a new document |
| `docs_read` | Read a document |
| `docs_append` | Append text to document |
| `docs_delete` | Delete a document |

### Slides

| Tool | Description |
|------|-------------|
| `slides_create` | Create a new presentation |
| `slides_read` | Read a presentation |
| `slides_delete` | Delete a presentation |

### Calendar

| Tool | Description |
|------|-------------|
| `calendar_create_event` | Create a new event |
| `calendar_list_events` | List calendar events |
| `calendar_update_event` | Update an event |
| `calendar_delete_event` | Delete an event |

## Configuration

Edit `.env` to set your default Google account:

```env
GOGCLI_ACCOUNT="your.email@gmail.com"
```

## Examples

### Sending an HTML Email

```json
{
  "tool": "gmail_send_email",
  "arguments": {
    "to": "recipient@example.com",
    "subject": "Hello",
    "body": "<h1>Hello World</h1><p>This is <strong>HTML</strong>!</p>",
    "html": true
  }
}
```

### Creating a Spreadsheet with Data

```json
{
  "tool": "sheets_create",
  "arguments": {
    "title": "Sales Data",
    "account": "your.email@gmail.com"
  }
}
```

Then write data:

```json
{
  "tool": "sheets_write",
  "arguments": {
    "spreadsheet_id": "YOUR_SHEET_ID",
    "range": "Sheet1!A1:C2",
    "data": "[[\"Name\", \"Email\", \"Phone\"], [\"John\", \"john@example.com\", \"555-1234\"]]"
  }
}
```

### Creating a Calendar Event

```json
{
  "tool": "calendar_create_event",
  "arguments": {
    "title": "Team Meeting",
    "start": "tomorrow 10am",
    "end": "tomorrow 11am",
    "description": "Weekly sync",
    "location": "Conference Room A"
  }
}
```

## gogcli Commands Reference

### Gmail

```bash
# Send email
gogcli gmail send --to=recipient@example.com --subject="Hello" --body="World"

# Send HTML email (from file)
echo "<h1>Hello</h1>" > /tmp/email.html
gogcli gmail send --to=recipient@example.com --subject="HTML" --body-file=/tmp/email.html

# List emails
gogcli gmail list --limit=10

# Search emails
gogcli gmail search --query="from:john@example.com"

# Read email
gogcli gmail read --id=MESSAGE_ID
```

### Sheets

```bash
# Create spreadsheet
gogcli sheets create --title="My Sheet"

# Read data
gogcli sheets get --id=SHEET_ID --range=Sheet1!A1:D10

# Write data
echo "Name,Age" | gogcli sheets update --id=SHEET_ID --range=Sheet1!A1 --data=-

# Append rows
echo "John,30" | gogcli sheets append --id=SHEET_ID --range=Sheet1!A1 --data=-

# Delete spreadsheet
gogcli sheets delete --id=SHEET_ID
```

### Docs

```bash
# Create document
gogcli docs create --title="My Doc"

# Read document
gogcli docs get --id=DOC_ID

# Append text
gogcli docs append --id=DOC_ID --text="New content"

# Delete document
gogcli docs delete --id=DOC_ID
```

### Calendar

```bash
# Create event
gogcli calendar create --title="Meeting" --start="tomorrow 10am" --end="tomorrow 11am"

# List events
gogcli calendar list --limit=10

# Update event
gogcli calendar update --id=EVENT_ID --title="New Title"

# Delete event
gogcli calendar delete --id=EVENT_ID
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude Desktop │────▶│  MCP Server     │────▶│    gogcli       │
│  (MCP Client)   │     │  (SSE/stdio)    │     │  (CLI Tool)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │  Google OAuth   │
                        │  (keyring)      │
                        └─────────────────┘
```

## Troubleshooting

### "gogcli not found"

Install gogcli from releases:
```bash
bash legacy-extras/install-gogcli.sh
```

### "Authentication required"

Run gogcli auth:
```bash
# Interactive mode (opens browser)
gogcli auth login

# Manual mode (for servers without browser)
gogcli auth login --manual
```

### Server won't start on port 9001

Check if port is in use:
```bash
lsof -i :9001
```

Use a different port:
```bash
./install.sh --server-only 8080
```

### expect not found (for HTML emails)

On Ubuntu/Debian:
```bash
sudo apt-get install expect
```

On macOS:
```bash
brew install expect
```

## Sending HTML Emails with gogcli

**WORKING COMMAND** (tested - message_id: 19c442e0f85b9fc4):

```bash
expect << 'EOF'
set timeout 30
set html_body "<h1>Hello</h1><p>HTML <strong>email</strong></p><p style=color:blue>Blue text</p><a href=https://github.com>Link</a>"
spawn gogcli gmail send --account=YOUR_EMAIL@gmail.com --to=recipient@example.com --subject=Subject --body=Plain --body-html=$html_body
expect "Enter passphrase" { send "\r"; exp_continue }
expect eof
EOF
```

### CRITICAL Rules:
- **NO quotes in attributes**: `style=color:blue` NOT `style="color: blue"`
- **NO quotes in href**: `<a href=https://example.com>` NOT `<a href="https://example.com">`
- **Single line HTML**: Newlines must be avoided
- **Use single quotes**: `<< 'EOF'` to prevent shell expansion

### Using the included script:
```bash
./send-html.sh "recipient@example.com" "Subject"
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .

# Check linting
ruff check .
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Links

- [MCP Specification](https://modelcontextprotocol.io)
- [gogcli GitHub](https://github.com/steipete/gogcli)
- [gogcli Releases](https://github.com/steipete/gogcli/releases)
- [GOGCLI Guide](legacy-extras/GOGCLI-GUIDE.md)

---

**Repository**: https://github.com/Zurybr/google-workspace-mcp-server
