# Contributing to Google Workspace MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/google-workspace-mcp-server.git
   cd google-workspace-mcp-server
   ```

3. Set up your development environment:
   ```bash
   # Install UV (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

Before committing, run:
```bash
# Format code
ruff format .

# Check for issues
ruff check .
```

## Running Tests

```bash
pytest
```

## Submitting Changes

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with a clear message

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub

## Adding New Tools

To add a new tool to the MCP server:

1. Add the client method in `google_workspace_mcp/client.py`
2. Register the tool in `google_workspace_mcp/server.py`:
   - Add to `handle_list_tools()` with proper schema
   - Add handler in `handle_call_tool()`
3. Update the README with the new tool documentation

## Reporting Issues

When reporting issues, please include:
- Python version
- MCP client being used
- Error messages or unexpected behavior
- Steps to reproduce the issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
