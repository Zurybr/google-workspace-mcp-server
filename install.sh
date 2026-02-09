#!/bin/bash
# Google Workspace MCP Server - Interactive Installer
# This script guides you through setting up OAuth credentials and installing dependencies
#
# Usage:
#   ./install.sh              - Interactive installation
#   ./install.sh --server-only - Start the MCP server on port 9001

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_step() {
    echo -e "${GREEN}➤ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v xdg-open &> /dev/null; then
            OPEN_CMD="xdg-open"
        else
            OPEN_CMD="sensible-browser"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        OPEN_CMD="open"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        OS="windows"
        OPEN_CMD="start"
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Check if gogcli is installed
check_gogcli() {
    if command -v gogcli &> /dev/null; then
        print_success "gogcli found: $(gogcli --version 2>&1 | head -1)"
        return 0
    else
        print_error "gogcli not found!"
        print_info "Please install gogcli from https://github.com/steipete/gogcli/releases"
        print_info "Or run: bash legacy-extras/install-gogcli.sh"
        return 1
    fi
}

# Start server in SSE mode
start_server() {
    local port=${1:-9001}
    local detach=${2:-false}

    print_header "Starting Google Workspace MCP Server"
    echo ""

    # Check gogcli
    if ! check_gogcli; then
        exit 1
    fi

    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_info "Virtual environment not found. Creating..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -e . -q
    else
        source .venv/bin/activate
    fi

    # Check default account
    if [ -f ".env" ] && grep -q "GOGCLI_ACCOUNT" .env; then
        source .env
        print_success "Using account: ${GOGCLI_ACCOUNT:-default}"
    else
        print_info "No default account set. Using gogcli default."
        print_info "Set GOGCLI_ACCOUNT in .env to specify default account."
    fi

    echo ""
    print_step "Starting server on port $port..."
    echo ""
    print_info "Server will be available at: http://localhost:$port/sse"

    if [ "$detach" = "true" ]; then
        print_info "Server will run in background (detached) mode"
        echo ""
        # Start the server in detached mode
        python -m google_workspace_mcp.server_gogcli --server-only --port "$port" --detach
    else
        print_info "Press Ctrl+C to stop"
        echo ""
        # Start the server normally
        python -m google_workspace_mcp.server_gogcli --server-only --port "$port"
    fi
}

# Main installation flow
main() {
    # Check for --server-only flag
    if [[ "$1" == "--server-only" ]]; then
        DETACH=false
        PORT="${2:-9001}"

        # Check for --detach flag
        if [[ "$2" == "--detach" ]] || [[ "$3" == "--detach" ]]; then
            DETACH=true
            # If --detach is second arg, port is default
            if [[ "$2" == "--detach" ]]; then
                PORT="9001"
            fi
        fi

        start_server "$PORT" "$DETACH"
        exit 0
    fi

    # Show help if requested
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        echo "Google Workspace MCP Server - Installer"
        echo ""
        echo "Usage:"
        echo "  ./install.sh                           - Interactive installation"
        echo "  ./install.sh --server-only [PORT]      - Start MCP server (default port: 9001)"
        echo "  ./install.sh --server-only --detach    - Start MCP server in background"
        echo "  ./install.sh --help                    - Show this help"
        echo ""
        echo "Examples:"
        echo "  ./install.sh --server-only           - Start on port 9001 (foreground)"
        echo "  ./install.sh --server-only 8080      - Start on port 8080"
        echo "  ./install.sh --server-only --detach  - Start on port 9001 (background)"
        echo ""
        exit 0
    fi

    # Interactive installation
    print_header "Google Workspace MCP Server - Installer"
    echo ""
    print_info "This installer will guide you through:"
    echo "  1. Checking gogcli installation"
    echo "  2. Installing Python dependencies"
    echo "  3. Configuring the server"
    echo ""
    print_info "For OAuth setup with gogcli, see: legacy-extras/GOGCLI-GUIDE.md"
    echo ""
    read -p "Press Enter to continue..."

    detect_os

    # Check Python
    print_step "Checking Python version..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION detected"

    # Check UV
    print_step "Checking UV package manager..."
    if command -v uv &> /dev/null; then
        print_success "UV already installed"
    else
        print_info "Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        print_success "UV installed"
    fi

    # Check gogcli
    echo ""
    print_step "Checking gogcli installation..."
    if ! check_gogcli; then
        print_info "You can install gogcli by running:"
        print_info "  bash legacy-extras/install-gogcli.sh"
        print_info ""
        read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
    fi

    # Install dependencies
    echo ""
    print_step "Installing Python dependencies..."
    uv venv || python3 -m venv .venv

    if [ "$OS" = "windows" ]; then
        .venv/Scripts/pip install -e . -q
    else
        source .venv/bin/activate
        uv pip install -e . -q
    fi
    print_success "Dependencies installed"

    # Configure .env
    echo ""
    print_step "Creating .env file..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
        print_info "Edit .env to set your GOGCLI_ACCOUNT if needed"
    else
        print_info ".env already exists"
    fi

    # Final instructions
    echo ""
    print_header "Installation Complete!"
    echo ""
    print_success "Your Google Workspace MCP Server is ready!"
    echo ""
    echo "Quick Start:"
    echo ""
    echo "1. Start the server:"
    echo "   ./install.sh --server-only"
    echo ""
    echo "2. Or specify a custom port:"
    echo "   ./install.sh --server-only 8080"
    echo ""
    echo "3. Server will be available at: http://localhost:9001/sse"
    echo ""
    echo "Documentation: https://github.com/Zurybr/google-workspace-mcp-server"
    echo ""
    print_info "⚠️  Make sure gogcli is authenticated before using tools!"
    print_info "   Run: gogcli auth login"
    print_info "   Or for servers: gogcli auth login --manual"
    echo ""
}

# Run main function
main "$@"
