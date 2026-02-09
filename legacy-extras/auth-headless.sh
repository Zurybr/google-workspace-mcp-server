#!/bin/bash
# Script de autenticación headless para gogcli
# Para servidores Linux sin navegador
# Guía paso a paso la creación de credenciales OAuth

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

CONFIG_DIR="$HOME/.config/gogcli"
CREDENTIALS_FILE="$CONFIG_DIR/credentials.json"

echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🔐 gogcli - Autenticación Headless                   ║
║                                                          ║
║     Para servidores sin navegador                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar si gogcli está instalado
echo -e "${YELLOW}📋 Verificando instalación de gogcli...${NC}"

if ! command -v gogcli &> /dev/null; then
    if [ -f "$HOME/.local/bin/gogcli" ]; then
        export PATH="$PATH:$HOME/.local/bin"
        GOG_CMD="$HOME/.local/bin/gogcli"
    else
        echo -e "${RED}❌ gogcli no está instalado${NC}"
        echo ""
        echo "Instala primero:"
        echo "  cd ~/workspace/google-workspace-api"
        echo "  ./install-gogcli.sh"
        exit 1
    fi
else
    GOG_CMD="gogcli"
fi

echo -e "${GREEN}✅ gogcli encontrado${NC}\n"

# Crear directorio de configuración
mkdir -p "$CONFIG_DIR"

# Verificar si ya existen credenciales
if [ -f "$CREDENTIALS_FILE" ]; then
    echo -e "${YELLOW}⚠️  Ya existe un archivo credentials.json${NC}"
    echo -e "${YELLOW}   Ubicación: $CREDENTIALS_FILE${NC}"
    echo ""
    read -p "¿Quieres sobrescribirlo? (s/N): " OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Ss]$ ]]; then
        echo -e "${GREEN}Usando credenciales existentes${NC}\n"
        USE_EXISTING=1
    else
        echo -e "${YELLOW}Creando nuevas credenciales...${NC}\n"
        USE_EXISTING=0
    fi
else
    USE_EXISTING=0
fi

if [ "$USE_EXISTING" -eq 0 ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  📝 Paso 1: Crear credenciales OAuth en Google Cloud${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo -e "${MAGENTA}🔗 Abre esta URL en tu navegador:${NC}"
    echo ""
    echo -e "${BOLD}https://console.cloud.google.com/apis/credentials${NC}"
    echo ""

    echo -e "${YELLOW}O usa este enlace directo para crear un cliente OAuth:${NC}"
    echo -e "${CYAN}https://console.cloud.google.com/auth/clients/create${NC}"
    echo ""

    echo -e "${YELLOW}Instrucciones:${NC}"
    echo "  1. Selecciona tu proyecto (o crea uno nuevo)"
    echo "  2. Clic en ${BOLD}+ CREAR CREDENCIALES${NC} → ${BOLD}ID de cliente OAuth${NC}"
    echo "  3. Tipo de aplicación: ${BOLD}Aplicación de escritorio${NC}"
    echo "  4. Nombre: ${BOLD}gogcli${NC} (o el que quieras)"
    echo "  5. Clic en ${BOLD}CREAR${NC}"
    echo "  6. Se mostrará una ventana con:"
    echo "     - ID de cliente (client_id)"
    echo "     - Secreto de cliente (client_secret)"
    echo ""

    read -p "Presiona Enter cuando hayas creado las credenciales..."
    echo ""

    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  📋 Paso 2: Ingresar los datos de las credenciales${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    # Pedir client_id
    echo -e "${YELLOW}📌 Copia y pega el ${BOLD}ID de cliente${NC} (client_id):"
    echo -e "${CYAN}   Ejemplo: 123456789-abcdefg.apps.googleusercontent.com${NC}"
    read -p "   → " CLIENT_ID

    if [ -z "$CLIENT_ID" ]; then
        echo -e "${RED}❌ El ID de cliente es requerido${NC}"
        exit 1
    fi

    # Validar formato básico del client_id
    if [[ ! "$CLIENT_ID" =~ \.apps\.googleusercontent\.com$ ]]; then
        echo -e "${RED}⚠️  El ID de cliente parece inválido${NC}"
        echo "   Debe terminar en '.apps.googleusercontent.com'"
        read -p "   ¿Continuar de todos modos? (s/N): " CONTINUE
        if [[ ! "$CONTINUE" =~ ^[Ss]$ ]]; then
            exit 1
        fi
    fi

    echo ""

    # Pedir client_secret
    echo -e "${YELLOW}🔑 Copia y pega el ${BOLD}Secreto de cliente${NC} (client_secret):"
    echo -e "${CYAN}   Ejemplo: GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx${NC}"
    read -p "   → " CLIENT_SECRET

    if [ -z "$CLIENT_SECRET" ]; then
        echo -e "${RED}❌ El secreto de cliente es requerido${NC}"
        exit 1
    fi

    echo ""

    # Crear el archivo credentials.json con el formato correcto
    echo -e "${YELLOW}📝 Creando archivo credentials.json...${NC}"

    cat > "$CREDENTIALS_FILE" << EOF
{
  "client_id": "$CLIENT_ID",
  "client_secret": "$CLIENT_SECRET",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
EOF

    echo -e "${GREEN}✅ Archivo creado: $CREDENTIALS_FILE${NC}"
    echo ""

    # Mostrar el contenido
    echo -e "${YELLOW}📄 Contenido del archivo:${NC}"
    cat "$CREDENTIALS_FILE"
    echo ""
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📱 Paso 3: Autorizar la aplicación${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}1. Este proceso generará una URL de autorización${NC}"
echo -e "${YELLOW}2. Abre la URL en tu celular u otro dispositivo${NC}"
echo -e "${YELLOW}3. Inicia sesión y autoriza los permisos${NC}"
echo -e "${YELLOW}4. Copia el código de autorización que te muestran${NC}"
echo -e "${YELLOW}5. Pega el código aquí${NC}"
echo ""

read -p "Presiona Enter cuando estés listo..."

# Pedir email
echo ""
read -p "📧 Ingresa tu email de Google: " EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${RED}❌ Email es requerido${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔗 Iniciando autenticación manual${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Ejecutar comando de autenticación
if $GOG_CMD auth add "$EMAIL" --manual; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ Autenticación completada${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    # Mostrar cuentas configuradas
    echo -e "${YELLOW}📋 Cuentas configuradas:${NC}"
    $GOG_CMD auth list

    echo ""
    echo -e "${GREEN}🎉 ¡Listo! Ya puedes usar gogcli${NC}"
    echo ""
    echo -e "${YELLOW}Prueba estos comandos:${NC}"
    echo ""
    echo -e "${CYAN}# Configurar cuenta por defecto (opcional):${NC}"
    echo -e "${BOLD}export GOG_ACCOUNT=$EMAIL${NC}"
    echo ""
    echo -e "${CYAN}# Gmail:${NC}"
    echo -e "${BOLD}$GOG_CMD gmail search 'is:inbox' --account $EMAIL${NC}"
    echo ""
    echo -e "${CYAN}# Drive:${NC}"
    echo -e "${BOLD}$GOG_CMD drive ls --account $EMAIL${NC}"
    echo ""
    echo -e "${CYAN}# Calendar:${NC}"
    echo -e "${BOLD}$GOG_CMD calendar events --account $EMAIL${NC}"
    echo ""
    echo -e "${CYAN}# Sheets:${NC}"
    echo -e "${BOLD}$GOG_CMD sheets list --account $EMAIL${NC}"
    echo ""
    echo -e "${YELLOW}💡 Tip: Agrega 'export GOG_ACCOUNT=$EMAIL' a tu ~/.bashrc para no usar --account siempre${NC}"
    echo ""

else
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ❌ Error en la autenticación${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Si el problema persiste:"
    echo "  1. Verifica que hayas copiado el código correctamente"
    echo "  2. Los códigos expiran en 10 minutos - genera uno nuevo"
    echo "  3. Revisa que tu cuenta de Google permita el acceso de apps"
    echo ""
    exit 1
fi
