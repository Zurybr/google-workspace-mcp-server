# gogcli - Guía Completa de Uso

## 🚀 Instalación

### Opción 1: Script Automatizado
```bash
cd ~/workspace/google-workspace-api
chmod +x install-gogcli.sh
./install-gogcli.sh
```

### Opción 2: Manual
```bash
# Clonar repositorio
git clone https://github.com/steipete/gogcli.git
cd gogcli

# Compilar
make build

# Instalar
sudo cp gog /usr/local/bin/gogcli
# O en tu home
mkdir -p ~/.local/bin
cp gog ~/.local/bin/gogcli
export PATH=$PATH:~/.local/bin
```

## 🔐 Autenticación

### Primer uso
```bash
gogcli auth login
```

Esto abrirá tu navegador para autorizar el acceso a tu cuenta de Google.

### Verificar autenticación
```bash
gogcli auth status
```

## 📚 Comandos Disponibles

### GMAIL

```bash
# Listar emails recientes
gogcli gmail list

# Buscar emails
gogcli gmail search "from:juan@example.com"

# Buscar emails recientes
gogcli gmail search "newer_than:7d"

# Ver un thread específico
gogcli gmail thread <threadId>

# Enviar email
gogcli gmail send \
  --to="cliente@example.com" \
  --subject="Confirmación" \
  --body="Tu pedido ha sido confirmado"

# Ver etiquetas
gogcli gmail labels

# Operaciones con formato JSON
gogcli gmail list --format=json
```

### CALENDAR

```bash
# Listar eventos
gogcli calendar list

# Crear evento
gogcli calendar create \
  --title="Reunión de trabajo" \
  --when="2026-02-10 14:00" \
  --duration="1h"

# Listar eventos de hoy
gogcli calendar list --today

# Buscar eventos
gogcli calendar search "reunión"
```

### DRIVE

```bash
# Listar archivos
gogcli drive list

# Buscar archivos
gogcli drive search "contrato"

# Listar por tipo
gogcli drive list --type=spreadsheet
gogcli drive list --type=document
gogcli drive list --type=folder

# Descargar archivo
gogcli drive download <fileId> --output=./archivo.pdf

# Subir archivo
gogcli drive upload ./documento.pdf

# Compartir archivo
gogcli drive share <fileId> --email="cliente@example.com"
```

### SHEETS

```bash
# Listar hojas de cálculo
gogcli sheets list

# Leer datos de una hoja
gogcli sheets read <spreadsheetId> --range="A1:B10"

# Escribir datos
gogcli sheets write <spreadsheetId> --range="A1" \
  --data='[["Nombre", "Email"], ["Juan", "juan@example.com"]]'

# Crear hoja
gogcli sheets create "Nueva Hoja"
```

### CONTACTS

```bash
# Listar contactos
gogcli contacts list

# Buscar contacto
gogcli contacts search "Juan"

# Crear contacto
gogcli contacts create \
  --name="María García" \
  --email="maria@example.com" \
  --phone="+52-55-1234-5678"
```

### TASKS

```bash
# Listar tareas
gogcli tasks list

# Crear tarea
gogcli tasks create "Llamar al cliente"

# Marcar como completada
gogcli tasks complete <taskId>
```

### DOCS / SLIDES

```bash
# Listar documentos
gogcli docs list

# Crear documento
gogcli docs create "Mi Documento"

# Listar presentaciones
gogcli slides list

# Crear presentación
gogcli slides create "Mi Presentación"
```

## 📊 Formatos de Salida

### JSON (para scripting)
```bash
gogcli gmail list --format=json | jq '.[] | {subject, from}'
```

### Tabla
```bash
gogcli drive list --format=table
```

### Simple
```bash
gogcli gmail list --format=simple
```

## 🔧 Scripts de Ejemplo

### Backup de emails a JSON
```bash
#!/bin/bash
# backup-emails.sh

gogcli gmail list --format=json > emails_$(date +%Y%m%d).json
echo "Backup guardado en emails_$(date +%Y%m%d).json"
```

### Reporte de Drive
```bash
#!/bin/bash
# drive-report.sh

echo "=== Reporte de Drive ===" > report.txt
echo "" >> report.txt

echo "Archivos:" >> report.txt
gogcli drive list --format=table >> report.txt

echo "" >> report.txt
echo "Hojas de cálculo:" >> report.txt
gogcli drive list --type=spreadsheet --format=table >> report.txt
```

### Enviar reporte por email
```bash
#!/bin/bash
# send-report.sh

# Generar reporte
REPORT_FILE="/tmp/reporte_$(date +%Y%m%d).txt"
echo "Reporte generado el $(date)" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
gogcli tasks list --format=table >> "$REPORT_FILE"

# Enstrar por email
gogcli gmail send \
  --to="admin@empresa.com" \
  --subject="Reporte diario" \
  --body=@"$REPORT_FILE"
```

### Geocodificación con Google Maps + Sheets
```bash
#!/bin/bash
# geocode-save.sh

ADDRESS="$1"
SHEET_ID="TU_SHEET_ID"

# Geocodificar (usando API externa o mantener registro)
echo "$ADDRESS,$(date +%Y-%m-%d)" >> locations.txt

# Agregar a Sheet
gogcli sheets write "$SHEET_ID" \
  --range="A1" \
  --data="[\"$ADDRESS\", \"$(date +%Y-%m-%d)\"]"
```

## 🎯 Tips y Trucos

### Alias útiles
Agregar a `~/.bashrc` o `~/.zshrc`:
```bash
# gogcli aliases
alias gmail='gogcli gmail'
alias gcal='gogcli calendar'
alias gdrive='gogcli drive'
alias gsheets='gogcli sheets'
alias gtasks='gogcli tasks'
```

### Búsqueda avanzada en Gmail
```bash
# Emails no leídos
gogcli gmail search "is:unread"

# Emails con adjuntos
gogcli gmail search "has:attachment"

# Emails de esta semana
gogcli gmail search "newer_than:7d"

# Emails específicos
gogcli gmail search "from:vendedor@example.com subject:factura"
```

### Combinar con otras herramientas
```bash
# Contar emails
gogcli gmail list --format=json | jq 'length'

# Extraer direcciones de email
gogcli contacts list --format=json | jq -r '.[].email' > emails.txt

# Buscar en Drive y abrir
FILE_ID=$(gogcli drive search "mi archivo" --format=json | jq -r '.[0].id')
xdg-open "https://drive.google.com/file/d/$FILE_ID"
```

## 🐛 Troubleshooting

### Error: "Not authenticated"
```bash
gogcli auth login
```

### Error: "Invalid credentials"
```bash
# Re-autenticar
rm -rf ~/.config/gogcli/credentials.json
gogcli auth login
```

### Comando no encontrado
```bash
# Verificar PATH
which gogcli

# Si no existe, agregar a PATH
export PATH=$PATH:~/.local/bin
```

### Error de compilación
```bash
# Asegurarse de tener Go instalado
go version

# Si no está instalado
sudo apt-get install golang-go  # Debian/Ubuntu
sudo dnf install golang          # Fedora
```

## 📖 Referencia Completa

```bash
# Ayuda general
gogcli --help

# Ayuda de cada servicio
gogcli gmail --help
gogcli calendar --help
gogcli drive --help
gogcli sheets --help
gogcli contacts --help
gogcli tasks --help
gogcli docs --help
gogcli slides --help
```

## 🔗 Recursos

- **GitHub**: https://github.com/steipete/gogcli
- **Website**: https://gogcli.sh/
- **Documentación**: https://github.com/steipete/gogcli/blob/main/README.md

---

**¿Necesitas más ayuda?** Revisa la documentación oficial o prueba `gogcli <servicio> --help`
