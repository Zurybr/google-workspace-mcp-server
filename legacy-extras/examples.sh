#!/bin/bash
# Google Workspace API - Ejemplos de uso con curl
# Autor: Google Apps Script Integration
# Fecha: 2026

# =============================================
# CONFIGURACIÓN
# =============================================

# URL de tu Web App de Google Apps Script
# Reemplaza con tu URL real
API_URL="${WORKSPACE_API_URL:-https://script.google.com/macros/s/TU_SCRIPT_ID/exec}"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================
# FUNCIONES AUXILIARES
# =============================================

# Imprimir con color
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "\n${YELLOW}══════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}══════════════════════════════════════════${NC}\n"
}

# Llamada genérica a la API
api_call() {
    local service="$1"
    local action="$2"
    local data="$3"

    local response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"$service\",
            \"action\": \"$action\"
            $data
        }")

    echo "$response"
}

# Formatear JSON si está disponible jq
format_json() {
    if command -v jq &> /dev/null; then
        jq '.'
    else
        cat
    fi
}

# =============================================
# TEST DE CONEXIÓN
# =============================================

test_connection() {
    print_header "TEST DE CONEXIÓN"

    print_info "Probando conexión a: $API_URL"

    local response=$(curl -s "$API_URL")
    local status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    if [ "$status" = "ok" ]; then
        print_success "Conexión exitosa!"
        echo "$response" | format_json
        return 0
    else
        print_error "Error de conexión"
        echo "$response"
        return 1
    fi
}

# =============================================
# GMAIL
# =============================================

gmail_list() {
    local max="${1:-10}"
    print_header "GMAIL - Listar emails ($max)"

    api_call "gmail" "list", ", \"max\": $max" | format_json
}

gmail_send() {
    local to="$1"
    local subject="$2"
    local body="$3"

    print_header "GMAIL - Enviar email"

    if [ -z "$to" ] || [ -z "$subject" ]; then
        print_error "Uso: $0 gmail_send <to> <subject> [body]"
        return 1
    fi

    local body_escaped="${body:-Sin contenido}"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"gmail\",
            \"action\": \"send\",
            \"to\": \"$to\",
            \"subject\": \"$subject\",
            \"body\": \"$body_escaped\"
        }" | format_json
}

gmail_search() {
    local query="$1"
    print_header "GMAIL - Buscar: $query"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"gmail\",
            \"action\": \"search\",
            \"query\": \"$query\"
        }" | format_json
}

# =============================================
# SHEETS
# =============================================

sheets_create() {
    local title="$1"
    print_header "SHEETS - Crear: $title"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"sheets\",
            \"action\": \"create\",
            \"title\": \"$title\"
        }" | format_json
}

sheets_append() {
    local sheet_id="$1"
    shift
    local data=("$@")

    print_header "SHEETS - Append row"

    # Construir array JSON
    local json_data="["
    local first=true
    for item in "${data[@]}"; do
        if [ "$first" = true ]; then
            json_data="$json_data\"$item\""
            first=false
        else
            json_data="$json_data, \"$item\""
        fi
    done
    json_data="$json_data]"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"sheets\",
            \"action\": \"append\",
            \"sheetId\": \"$sheet_id\",
            \"data\": $json_data
        }" | format_json
}

# =============================================
# MAPS
# =============================================

maps_geocode() {
    local address="$1"
    print_header "MAPS - Geocoding: $address"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"maps\",
            \"action\": \"geocode\",
            \"address\": \"$address\"
        }" | format_json
}

maps_distance() {
    local origin="$1"
    local destination="$2"

    print_header "MAPS - Distancia"
    print_info "De: $origin"
    print_info "A: $destination"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"maps\",
            \"action\": \"distance\",
            \"origin\": \"$origin\",
            \"destination\": \"$destination\"
        }" | format_json
}

maps_route() {
    local origin="$1"
    local destination="$2"

    print_header "MAPS - Ruta"
    print_info "De: $origin"
    print_info "A: $destination"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"maps\",
            \"action\": \"route\",
            \"origin\": \"$origin\",
            \"destination\": \"$destination\"
        }" | format_json
}

# =============================================
# KEEP
# =============================================

keep_create() {
    local title="$1"
    local content="${2:-}"

    print_header "KEEP - Crear nota: $title"

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"keep\",
            \"action\": \"create\",
            \"title\": \"$title\",
            \"content\": \"$content\"
        }" | format_json
}

# =============================================
# WORKFLOWS DE EJEMPLO
# =============================================

# Workflow: Geocodificar y guardar en Sheet
workflow_geocode_save() {
    local address="$1"
    local sheet_id="$2"

    print_header "WORKFLOW: Geocodificar + Guardar en Sheet"

    # Geocodificar
    print_info "Geocodificando dirección..."
    local geo_result=$(maps_geocode "$address")

    # Extraer coordenadas (requiere jq)
    if command -v jq &> /dev/null; then
        local lat=$(echo "$geo_result" | jq -r '.location.lat // empty')
        local lng=$(echo "$geo_result" | jq -r '.location.lng // empty')

        if [ -n "$lat" ] && [ -n "$lng" ]; then
            print_success "Coordenadas: $lat, $lng"

            # Guardar en Sheet
            if [ -n "$sheet_id" ]; then
                print_info "Guardando en Sheet..."
                sheets_append "$sheet_id" "$address" "$lat" "$lng" "$(date +%Y-%m-%d)"
            fi
        else
            print_error "No se pudieron obtener coordenadas"
        fi
    else
        print_error "Se requiere jq para extraer coordenadas"
        echo "Instalar: sudo apt-get install jq"
    fi
}

# Workflow: Reporte de distancias
workflow_distances() {
    local origin="$1"
    shift
    local destinations=("$@")

    print_header "WORKFLOW: Reporte de Distancias"
    print_info "Origen: $origin"

    # Crear Sheet para el reporte
    print_info "Creando Sheet..."
    local sheet_result=$(sheets_create "Reporte Distancias $(date +%Y%m%d)")

    if command -v jq &> /dev/null; then
        local sheet_url=$(echo "$sheet_result" | jq -r '.url // empty')
        local sheet_id=$(echo "$sheet_result" | jq -r '.id // empty')

        if [ -n "$sheet_id" ]; then
            print_success "Sheet creada: $sheet_url"

            # Agregar cabeceras
            sheets_append "$sheet_id" "Origen" "Destino" "Distancia" "Duración"

            # Calcular distancias
            for dest in "${destinations[@]}"; do
                print_info "Calculando distancia a: $dest"
                local dist_result=$(maps_distance "$origin" "$dest")

                local dist_text=$(echo "$dist_result" | jq -r '.distance.text // "N/A"')
                local dur_text=$(echo "$dist_result" | jq -r '.duration.text // "N/A"')

                sheets_append "$sheet_id" "$origin" "$dest" "$dist_text" "$dur_text"
            done

            print_success "Reporte completado!"
        fi
    else
        print_error "Se requiere jq"
    fi
}

# =============================================
# MENU PRINCIPAL
# =============================================

show_help() {
    cat << EOF
${YELLOW}Google Workspace API - Cliente Bash${NC}

${BLUE}Uso:${NC}
  $0 [comando] [argumentos]

${BLUE}Comandos:${NC}

${GREEN}Test:${NC}
  test                    - Prueba conexión a la API

${GREEN}Gmail:${NC}
  gmail_list [max]        - Lista emails (default: 10)
  gmail_send <to> <subject> [body]  - Envía email
  gmail_search <query>    - Busca emails

${GREEN}Sheets:${NC}
  sheets_create <title>   - Crea hoja de cálculo
  sheets_append <id> <data...> - Agrega fila

${GREEN}Maps:${NC}
  maps_geocode <address>  - Convierte dirección a coordenadas
  maps_distance <origin> <dest>  - Calcula distancia
  maps_route <origin> <dest>  - Obtiene ruta detallada

${GREEN}Keep:${NC}
  keep_create <title> [content]  - Crea nota

${GREEN}Workflows:${NC}
  workflow_geocode <address> [sheet_id]  - Geocodifica y guarda
  workflow_distances <origin> <dest...>  - Reporte de distancias

${BLUE}Configuración:${NC}
  Export WORKSPACE_API_URL con tu URL del script
  Ejemplo: export WORKSPACE_API_URL="https://script.google.com/macros/s/.../exec"

${BLUE}Ejemplos:${NC}
  $0 maps_geocode "Zócalo, Ciudad de México"
  $0 maps_distance "CDMX" "Monterrey"
  $0 keep_create "Compras" "Leche\nPan\nHuevos"
  $0 workflow_distances "CDMX" "Monterrey" "Guadalajara"

EOF
}

# =============================================
# MAIN
# =============================================

main() {
    # Verificar argumentos
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    # Obtener comando
    local command="$1"
    shift

    # Ejecutar comando
    case "$command" in
        test)
            test_connection
            ;;
        gmail_list)
            gmail_list "$@"
            ;;
        gmail_send)
            gmail_send "$@"
            ;;
        gmail_search)
            gmail_search "$@"
            ;;
        sheets_create)
            sheets_create "$@"
            ;;
        sheets_append)
            sheets_append "$@"
            ;;
        maps_geocode)
            maps_geocode "$@"
            ;;
        maps_distance)
            maps_distance "$@"
            ;;
        maps_route)
            maps_route "$@"
            ;;
        keep_create)
            keep_create "$@"
            ;;
        workflow_geocode)
            workflow_geocode "$@"
            ;;
        workflow_distances)
            workflow_distances "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Comando desconocido: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
