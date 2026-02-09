# Google Workspace MCP Server

A Model Context Protocol (MCP) server that provides AI agents with access to Google Workspace services including Gmail, Sheets, Docs, Drive, and Slides using direct Google APIs with OAuth 2.0 authentication.

## Features

- **Gmail**: List, send, search, and read emails
- **Sheets**: Create, read, write, and append rows to spreadsheets
- **Docs**: Create and read Google Docs documents
- **Drive**: List files, create files, and share resources
- **Slides**: Create presentations

## Quick Start (Automatic Installation)

The easiest way to set up the server is using the interactive installer:

```bash
chmod +x install.sh
./install.sh
```

The installer will guide you through:
1. Creating OAuth credentials in Google Cloud Console
2. Enabling required Google APIs
3. Installing dependencies
4. Configuring the server

## Manual Installation

If you prefer to set up manually:

### 1. Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials/oauthclient?project=agents-ai-demo)
2. Sign in with your Google account
3. Click **Create credentials** → **OAuth client ID**
4. Application type: **Desktop application**
5. Name: Enter `MCP Server`
6. Click **Create**
7. Copy the **Client ID** and **Client Secret**

### 2. Enable Google APIs

Enable the following APIs in [Google Cloud Console](https://console.cloud.google.com/apis/library):

- [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com?project=agents-ai-demo)
- [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com?project=agents-ai-demo)
- [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=agents-ai-demo)
- [Google Docs API](https://console.cloud.google.com/apis-library/docs.googleapis.com?project=agents-ai-demo)
- [Google Slides API](https://console.cloud.google.com/apis/library/slides.googleapis.com?project=agents-ai-demo)

### 3. Install the Server

```bash
# Clone the repository
git clone https://github.com/yourusername/google-workspace-mcp-server.git
cd google-workspace-mcp-server

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 4. Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
GOOGLE_OAUTH_CLIENT_ID="your-client-id"
GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
USER_GOOGLE_EMAIL="your.email@gmail.com"
OAUTHLIB_INSECURE_TRANSPORT=1
```

## Usage

### First-Time Authentication

The first time you use a tool, you'll be prompted to authenticate in your browser:

1. The server will open a browser window
2. Sign in with your Google account
3. Grant permissions to the requested services
4. The server will save your authentication token

### Running the Server

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the server
python -m google_workspace_mcp.server
```

### Configuring Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "/path/to/google-workspace-mcp-server/.venv/bin/python",
      "args": ["-m", "google_workspace_mcp.server"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-secret",
        "USER_GOOGLE_EMAIL": "your.email@gmail.com",
        "OAUTHLIB_INSECURE_TRANSPORT": "1"
      }
    }
  }
}
```

## Available Tools

### Gmail

| Tool | Description |
|------|-------------|
| `gmail_list_emails` | List recent emails |
| `gmail_send_email` | Send an email |
| `gmail_search_emails` | Search emails |
| `gmail_read_email` | Read a full email |

### Sheets

| Tool | Description |
|------|-------------|
| `sheets_create` | Create a new spreadsheet |
| `sheets_read` | Read data from a spreadsheet |
| `sheets_write` | Write data to a spreadsheet |
| `sheets_append` | Append rows to a spreadsheet |

### Docs

| Tool | Description |
|------|-------------|
| `docs_create` | Create a new document |
| `docs_read` | Read a document |

### Drive

| Tool | Description |
|------|-------------|
| `drive_list_files` | List files in Drive |
| `drive_create_file` | Create a file or folder |
| `drive_share_file` | Share a file with another user |

### Slides

| Tool | Description |
|------|-------------|
| `slides_create` | Create a new presentation |

## Example Usage

After setting up Claude Desktop, you can ask:

- "List my recent emails"
- "Create a spreadsheet named 'Q1 Sales' with data [['Product', 'Amount'], ['Widget', '$100']]"
- "Send an email to john@example.com with subject 'Hello' and body 'Testing MCP'"
- "Create a document titled 'Meeting Notes' with content 'Discussed project timeline'"

## Troubleshooting

### "OAuth credentials not set" Error

Make sure `.env` exists and contains valid credentials:
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`

### "API not enabled" Error

Make sure you've enabled all required APIs in Google Cloud Console (see step 2 in Manual Installation).

### Authentication Fails

1. Delete `token.json` if it exists
2. Try again - you'll be re-prompted to authenticate

### Browser Doesn't Open

If the browser doesn't open automatically, look for a URL in the terminal output and paste it into your browser manually.

## Security

- **Never commit** `.env`, `token.json`, or any credentials to version control
- The `.gitignore` is configured to exclude these files
- Use `OAUTHLIB_INSECURE_TRANSPORT=1` only for local development
- For production, use HTTPS and proper OAuth callbacks

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
- [Google APIs Documentation](https://developers.google.com/apis-explorer)
- [OAuth 2.0 for Mobile & Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)

---

**Note**: This project is not affiliated with or endorsed by Google. It uses Google APIs and OAuth 2.0 for authentication.
