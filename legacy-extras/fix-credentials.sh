#!/bin/bash
# Script para arreglar el formato de credentials.json de Google Cloud Console
# Convierte el formato anidado {"installed": {...}} al formato plano que espera gogcli

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

CREDENTIALS_FILE="$HOME/.config/gogcli/credentials.json"
BACKUP_FILE="$HOME/.config/gogcli/credentials.json.backup"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔧 Arreglando formato de credentials.json${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Verificar que el archivo existe
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo -e "${RED}❌ No existe $CREDENTIALS_FILE${NC}"
    echo ""
    echo "Primero debes descargar el archivo credentials.json desde Google Cloud Console:"
    echo "  1. Ve a https://console.cloud.google.com/apis/credentials"
    echo "  2. Crea credenciales OAuth 2.0 > Desktop app"
    echo "  3. Descarga el archivo JSON"
    echo "  4. Cópialo a $CREDENTIALS_FILE"
    echo ""
    exit 1
fi

# Crear backup
echo -e "${YELLOW}📋 Creando backup...${NC}"
cp "$CREDENTIALS_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup creado: $BACKUP_FILE${NC}"
echo ""

# Verificar si tiene el formato anidado
if grep -q '"installed"' "$CREDENTIALS_FILE"; then
    echo -e "${YELLOW}🔄 Detectado formato anidado de Google Cloud Console${NC}"
    echo -e "${YELLOW}   Convirtiendo a formato plano para gogcli...${NC}"
    echo ""

    # Verificar que jq está instalado
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq no está instalado${NC}"
        echo ""
        echo "Instala jq:"
        echo "  sudo apt-get install jq   # Debian/Ubuntu"
        echo "  sudo yum install jq       # RHEL/CentOS"
        echo ""
        exit 1
    fi

    # Convertir formato
    cat "$CREDENTIALS_FILE" | jq '{
        client_id: .installed.client_id,
        client_secret: .installed.client_secret,
        auth_uri: .installed.auth_uri,
        token_uri: .installed.token_uri
    }' > "$CREDENTIALS_FILE.tmp"

    mv "$CREDENTIALS_FILE.tmp" "$CREDENTIALS_FILE"

    echo -e "${GREEN}✅ Formato convertido exitosamente${NC}"
    echo ""
    echo -e "${YELLOW}📄 Contenido del archivo arreglado:${NC}"
    cat "$CREDENTIALS_FILE"
    echo ""

else
    echo -e "${GREEN}✅ El archivo ya tiene el formato correcto${NC}"
    echo ""
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Listo! Ahora puedes ejecutar ./auth-headless.sh${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
