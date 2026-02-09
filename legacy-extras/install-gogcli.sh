#!/bin/bash
# Instalación de gogcli - Google Suite CLI
# Para servidores Linux

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo -e "${BLUE}  gogcli - Google Suite CLI Installer${NC}"
echo -e "${BLUE}══════════════════════════════════════════${NC}\n"

# Verificar dependencias
echo -e "${YELLOW}📋 Verificando dependencias...${NC}"

# Verificar curl
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ curl no está instalado${NC}"
    echo "Instalar: sudo apt-get install curl"
    exit 1
fi

# Verificar Go
if ! command -v go &> /dev/null; then
    echo -e "${YELLOW}⚠️  Go no está instalado. Instalando...${NC}"

    # Detectar distribución
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        echo "Instalando Go en Debian/Ubuntu..."
        sudo apt-get update
        sudo apt-get install -y golang-go
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS/Fedora
        echo "Instalando Go en RHEL/CentOS/Fedora..."
        sudo dnf install -y golang
    else
        echo -e "${RED}❌ No se pudo detectar la distribución${NC}"
        echo "Por favor instala Go manualmente:"
        echo "  https://go.dev/dl/"
        exit 1
    fi

    # Configurar PATH para Go
    echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
    export PATH=$PATH:$(go env GOPATH)/bin
fi

echo -e "${GREEN}✅ Dependencias OK${NC}\n"

# Crear directorio de instalación
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

echo -e "${YELLOW}📥 Descargando gogcli...${NC}"
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# Obtener última versión de la API de GitHub
LATEST_URL=$(curl -sL https://api.github.com/repos/steipete/gogcli/releases/latest | grep -o '"browser_download_url": *"[^"]*linux_amd64[^"]*"' | cut -d'"' -f4)

if [ -z "$LATEST_URL" ]; then
    echo -e "${RED}❌ No se pudo obtener la URL de descarga${NC}"
    exit 1
fi

echo "Descargando desde: $LATEST_URL"
curl -sL "$LATEST_URL" | tar xz

if [ ! -f "gog" ]; then
    echo -e "${RED}❌ Error al extraer el binario${NC}"
    exit 1
fi

# Mover binary a ubicación final
cp gog "$INSTALL_DIR/gogcli"
chmod +x "$INSTALL_DIR/gogcli"

# Limpiar
rm -rf "$TMP_DIR"

echo -e "${GREEN}✅ gogcli instalado en: $INSTALL_DIR/gogcli${NC}\n"

# Verificar instalación
echo -e "${YELLOW}🧪 Verificando instalación...${NC}"
if "$INSTALL_DIR/gogcli" --version &> /dev/null; then
    VERSION=$("$INSTALL_DIR/gogcli" --version 2>&1 || echo "unknown")
    echo -e "${GREEN}✅ gogcli $VERSION instalado correctamente${NC}\n"
else
    echo -e "${RED}❌ Error en la instalación${NC}"
    exit 1
fi

# Configurar PATH si es necesario
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}⚠️  Agregando $INSTALL_DIR a PATH${NC}"

    # Detectar shell
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    else
        SHELL_CONFIG="$HOME/.bashrc"
    fi

    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
    echo -e "${GREEN}✅ Agregado a $SHELL_CONFIG${NC}"
    echo -e "${YELLOW}⚠️  Ejecuta: source $SHELL_CONFIG${NC}\n"
fi

# Crear directorio de configuración
CONFIG_DIR="$HOME/.config/gogcli"
mkdir -p "$CONFIG_DIR"

echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Instalación completada${NC}"
echo -e "${BLUE}══════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}📝 Próximos pasos:${NC}"
echo ""
echo "1. ${GREEN}Autenticar con Google (modo headless):${NC}"
echo "   cd ~/workspace/google-workspace-api"
echo "   ./auth-headless.sh"
echo ""
echo "   El script te guiará paso a paso para:"
echo "   - Crear credenciales OAuth en Google Cloud Console"
echo "   - Ingresar client_id y client_secret"
echo "   - Autorizar la aplicación"
echo ""
echo "2. ${GREEN}Probar comandos:${NC}"
echo "   gogcli gmail list"
echo "   gogcli calendar list"
echo "   gogcli drive list"
echo ""
echo "3. ${GREEN}Ver ayuda:${NC}"
echo "   gogcli --help"
echo "   gogcli gmail --help"
echo ""

# Ejecutar comando de ayuda si está disponible
echo -e "${YELLOW}📚 Comandos disponibles:${NC}"
"$INSTALL_DIR/gogcli" --help 2>&1 | head -20 || echo "Ejecuta 'gogcli --help' para ver todos los comandos"
