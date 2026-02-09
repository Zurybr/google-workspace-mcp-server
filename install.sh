#!/bin/bash
# Google Workspace MCP Server - Interactive Installer
# This script guides you through setting up OAuth credentials and installing dependencies

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
    print_success "Detected OS: $OS"
}

# Check Python version
check_python() {
    print_step "Checking Python version..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        print_info "Please install Python 3.10 or higher"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_error "Python 3.10+ is required (found: $PYTHON_VERSION)"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION detected"
}

# Install UV package manager
install_uv() {
    print_step "Installing UV package manager..."

    if command -v uv &> /dev/null; then
        print_success "UV already installed"
    else
        print_info "Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"

        # Add to shell profile if needed
        if [ -f "$HOME/.bashrc" ]; then
            if ! grep -q ".local/bin" "$HOME/.bashrc"; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            fi
        fi
        if [ -f "$HOME/.zshrc" ]; then
            if ! grep -q ".local/bin" "$HOME/.zshrc"; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            fi
        fi

        print_success "UV installed"
    fi
}

# Get user email
get_email() {
    print_header "Step 1: Google Account"
    echo ""
    read -p "Enter your Google email address: " GOOGLE_EMAIL
    while [ -z "$GOOGLE_EMAIL" ]; do
        print_error "Email cannot be empty"
        read -p "Enter your Google email address: " GOOGLE_EMAIL
    done
    print_success "Email: $GOOGLE_EMAIL"
}

# Get OAuth credentials from Google Cloud Console
get_oauth_credentials() {
    print_header "Step 2: Google Cloud OAuth Setup"
    echo ""
    print_info "We need to create OAuth credentials in Google Cloud Console"
    echo ""

    # Store the current project ID if it exists in the URL
    PROJECT_ID="agents-ai-demo"

    print_step "Opening Google Cloud Console..."
    echo ""
    print_info "1. If prompted, select your Google account: $GOOGLE_EMAIL"
    print_info "2. Click 'Create credentials' > 'OAuth client ID'"
    print_info "3. Application type: Select 'Desktop app'"
    print_info "4. Name: Enter 'MCP Server' (or any name you prefer)"
    print_info "5. Click 'Create'"
    print_info "6. Copy the Client ID and Client Secret"
    echo ""

    # Open the browser with the project
    AUTH_URL="https://console.cloud.google.com/apis/credentials/oauthclient?project=$PROJECT_ID"
    print_info "Opening: $AUTH_URL"

    if command -v $OPEN_CMD &> /dev/null; then
        $OPEN_CMD "$AUTH_URL" 2>/dev/null &
    fi

    echo ""
    print_info "After creating the OAuth client, you'll see a dialog with:"
    print_info "  - Client ID (starts with numbers, like 123456789-...)"
    print_info "  - Client secret (shorter string)"
    echo ""

    # Get Client ID
    read -p "Paste your Client ID here: " CLIENT_ID
    while [ -z "$CLIENT_ID" ]; do
        print_error "Client ID cannot be empty"
        read -p "Paste your Client ID here: " CLIENT_ID
    done

    # Get Client Secret
    read -p "Paste your Client Secret here: " CLIENT_SECRET
    while [ -z "$CLIENT_SECRET" ]; do
        print_error "Client Secret cannot be empty"
        read -p "Paste your Client Secret here: " CLIENT_SECRET
    done

    print_success "OAuth credentials received"
}

# Guide user to enable APIs
enable_apis() {
    print_header "Step 3: Enable Google APIs"
    echo ""
    print_info "Now we need to enable the required Google APIs"
    echo ""

    # APIs to enable
    APIS=(
        "Gmail API:gmail"
        "Google Drive API:drive"
        "Google Sheets API:sheets"
        "Google Docs API:docs"
        "Google Slides API:slides"
    )

    print_info "I'll open each API page. Just click 'Enable' if it's not already enabled."
    echo ""
    read -p "Press Enter to continue..."

    for api in "${APIS[@]}"; do
        api_name="${api%%:*}"
        api_id="${api##*:}"
        api_url="https://console.cloud.google.com/apis/library/${api_id}.api?project=$PROJECT_ID"

        print_step "Enabling $api_name..."
        print_info "Opening: $api_url"

        if command -v $OPEN_CMD &> /dev/null; then
            $OPEN_CMD "$api_url" 2>/dev/null &
        fi

        sleep 1
    done

    echo ""
    print_success "API pages opened. Please make sure each API is enabled."
    print_info "Press Enter when you're done..."
    read
}

# Create .env file
create_env_file() {
    print_header "Step 4: Create Configuration"
    echo ""

    ENV_FILE=".env"

    cat > "$ENV_FILE" << EOF
# Google Workspace MCP Server Configuration
# Generated by install.sh on $(date)

# =============================================
# REQUIRED - OAuth Credentials
# =============================================
GOOGLE_OAUTH_CLIENT_ID="$CLIENT_ID"
GOOGLE_OAUTH_CLIENT_SECRET="$CLIENT_SECRET"

# Default user email
USER_GOOGLE_EMAIL="$GOOGLE_EMAIL"

# =============================================
# OPTIONAL - Server Configuration
# =============================================
# Port for HTTP mode (default: 8000)
# WORKSPACE_MCP_PORT=8000

# Log level (DEBUG, INFO, WARNING, ERROR)
# LOG_LEVEL=INFO

# =============================================
# DEVELOPMENT - Only for local development
# =============================================
# Allow HTTP redirect URIs (NEVER use in production)
OAUTHLIB_INSECURE_TRANSPORT=1
EOF

    print_success "Created $ENV_FILE"
    print_info "Your credentials are stored in $ENV_FILE"
    print_info "⚠️  Never commit .env to version control!"
}

# Install Python dependencies
install_dependencies() {
    print_header "Step 5: Install Dependencies"
    echo ""

    print_step "Creating virtual environment..."
    uv venv || python3 -m venv .venv

    print_step "Installing MCP server..."
    if [ "$OS" = "windows" ]; then
        .venv/Scripts/pip install -e .
    else
        source .venv/bin/activate
        uv pip install -e .
    fi

    print_success "Dependencies installed"
}

# Test the installation
test_installation() {
    print_header "Step 6: Test Installation"
    echo ""

    print_info "Let's verify the server can start..."
    echo ""

    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        exit 1
    fi

    # Test import
    print_step "Testing Python imports..."

    if [ "$OS" = "windows" ]; then
        .venv/Scripts/python -c "import google_workspace_mcp; print('✓ Imports successful')"
    else
        source .venv/bin/activate
        python -c "import google_workspace_mcp; print('✓ Imports successful')"
    fi

    print_success "Installation test passed!"
}

# Print final instructions
print_final_instructions() {
    print_header "Installation Complete!"
    echo ""
    print_success "Your Google Workspace MCP Server is ready!"
    echo ""
    echo "Next Steps:"
    echo ""
    echo "1. Activate the virtual environment:"
    if [ "$OS" = "windows" ]; then
        echo "   .venv\\Scripts\\activate"
    elif [ "$OS" = "macos" ]; then
        echo "   source .venv/bin/activate"
    else
        echo "   source .venv/bin/activate"
    fi
    echo ""
    echo "2. Run the server:"
    echo "   python -m google_workspace_mcp.server"
    echo ""
    echo "3. Or use with Claude Desktop by adding to claude_desktop_config.json:"
    echo ""
    echo "   {"
    echo "     \"mcpServers\": {"
    echo "       \"google-workspace\": {"
    echo "         \"command\": \"$(pwd)/.venv/bin/python\","
    echo "         \"args\": [\"-m\", \"google_workspace_mcp.server\"],"
    echo "         \"env\": {"
    echo "           \"GOOGLE_OAUTH_CLIENT_ID\": \"$CLIENT_ID\","
    echo "           \"GOOGLE_OAUTH_CLIENT_SECRET\": \"$CLIENT_SECRET\","
    echo "           \"USER_GOOGLE_EMAIL\": \"$GOOGLE_EMAIL\","
    echo "           \"OAUTHLIB_INSECURE_TRANSPORT\": \"1\""
    echo "         }"
    echo "       }"
    echo "     }"
    echo "   }"
    echo ""
    echo "Documentation: https://github.com/yourusername/google-workspace-mcp-server"
    echo ""
    print_info "⚠️  First time you use a tool, you'll need to authenticate in your browser."
    echo ""
}

# Main installation flow
main() {
    print_header "Google Workspace MCP Server - Installer"
    echo ""
    print_info "This installer will guide you through:"
    echo "  1. Setting up OAuth credentials in Google Cloud Console"
    echo "  2. Enabling required Google APIs"
    echo "  3. Installing dependencies"
    echo "  4. Configuring the server"
    echo ""
    read -p "Press Enter to continue..."

    echo ""
    detect_os
    check_python
    install_uv

    echo ""
    get_email
    echo ""
    get_oauth_credentials
    echo ""
    enable_apis
    echo ""
    create_env_file
    echo ""
    install_dependencies
    echo ""
    test_installation
    echo ""
    print_final_instructions
}

# Run main function
main
