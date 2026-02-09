# 🔐 Autenticación Headless de gogcli

Para servidores Linux SIN navegador.

## ⚠️ IMPORTANTE: Formato de credentials.json

El archivo que descargas de Google Cloud Console tiene un formato **anidado** que **no es compatible** con gogcli. Necesitas convertirlo.

### Formato incorrecto (Google Cloud Console):
```json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    ...
  }
}
```

### Formato correcto (gogcli):
```json
{
  "client_id": "...",
  "client_secret": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### Solución automática:

```bash
cd ~/workspace/google-workspace-api
./fix-credentials.sh
```

Este script automáticamente:
1. Detecta el formato incorrecto
2. Crea un backup
3. Convierte al formato correcto usando jq

## Opción 1: Modo Manual (OAuth) ⭐ Recomendado para uso personal

### Paso 1: Iniciar autenticación manual

```bash
cd ~/workspace/google-workspace-api
./install-gogcli.sh

# Después de instalar, autenticar en modo manual
gogcli auth add tu-email@gmail.com --manual
```

### Paso 2: Copiar la URL

El comando te mostrará algo como:

```
Please visit this URL to authorize the application:
https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&client_id=...

Enter the authorization code:
```

### Paso 3: Abrir la URL en OTRO dispositivo

- Abre la URL en tu **celular**, **computadora personal**, o **tablet**
- Inicia sesión con tu cuenta de Google
- Autoriza los permisos solicitados
- **Copia el código de autorización** que te muestra

### Paso 4: Pegar el código en el servidor

Vuelve a tu terminal y pega el código:

```
Enter the authorization code: 4/0AX4XfWh7...
```

¡Listo! Ya estás autenticado.

### Verificar autenticación

```bash
# Listar cuentas configuradas
gogcli auth list

# Verificar estado
gogcli auth status
```

---

## Opción 2: Service Account ⭐ Para entornos empresariales/automatización

### Requisitos

- Cuenta de Google Workspace (empresarial)
- Acceso a Google Cloud Console
- Permisos de administrador

### Paso 1: Crear Service Account en Google Cloud

```bash
# Instalar gcloud CLI (opcional, para gestión más fácil)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

O vía navegador:

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un **nuevo proyecto** o selecciona uno existente
3. **IAM & Admin** → **Service Accounts**
4. Clic en **Crear Service Account**
5. Nombre: `gogcli-service`
6. Clic en **Crear y continuar**

### Paso 2: Habilitar APIs

1. **APIs & Services** → **Library**
2. Habilita estas APIs:
   - Gmail API
   - Google Drive API
   - Google Sheets API
   - Google Calendar API
   - Google Docs API
   - Google Slides API

### Paso 3: Configurar Domain-Wide Delegation

1. En el Service Account creado
2. Clic en **Editar**
3. Sección **Domain-wide delegation**
4. Clic en **Show IAM admin** y copia el **Client ID**

### Paso 4: Autorizar en Google Workspace Admin

1. Ve a [Google Admin Console](https://admin.google.com)
2. **Security** → **Access and data control** → **API controls**
3. **Domain-wide delegation**
4. Clic en **Add**
5. Pega el **Client ID** del service account
6. Añade estos **scopes** (uno por línea):

```
https://mail.google.com/
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/presentations
```

7. Clic en **Authorize**

### Paso 5: Crear clave JSON

1. Vuelve al Service Account en Google Cloud
2. Clic en **Keys** → **Add Key** → **Create new key**
3. Tipo: **JSON**
4. Clic en **Create** - se descargará un archivo `.json`

### Paso 6: Configurar gogcli con Service Account

```bash
# Mover archivo JSON al servidor
scp gogcli-service-xxxxx.json tu-servidor:~/.config/gogcli/

# En el servidor, configurar gogcli
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gogcli/gogcli-service-xxxxx.json

# Usar gogcli con service account
gogcli --service-account gmail list
```

O crear un script wrapper:

```bash
#!/bin/bash
# gogcli-sa.sh

export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gogcli/gogcli-service-xxxxx.json
gogcli "$@"
```

---

## Comparación

| Característica | Modo Manual | Service Account |
|----------------|-------------|-----------------|
| **Dificultad** | ⭐ Fácil | ⭐⭐⭐ Compleja |
| **Requiere Admin Workspace** | ❌ No | ✅ Sí |
| **Permisos de usuario** | ✅ Tus permisos | ⚠️ Delegación necesaria |
| **Automatización** | ⚠️ Token expira | ✅ No expira |
| **Ideal para** | Uso personal | Producción/servidores |
| **Requiere Google Workspace** | ❌ No (cualquier Google) | ✅ Sí |

---

## Script de Autenticación Headless

```bash
#!/bin/bash
# auth-headless.sh

echo "🔐 Autenticación de gogcli en modo headless"
echo ""
echo "Este script te guiará en la autenticación sin navegador."
echo ""
echo "📱 Necesitarás:"
echo "   - Un celular u otro dispositivo con navegador"
echo "   - Acceso a tu cuenta de Google"
echo ""

# Verificar si gogcli está instalado
if ! command -v gogcli &> /dev/null; then
    echo "❌ gogcli no está instalado"
    echo "Ejecuta primero: ./install-gogcli.sh"
    exit 1
fi

# Pedir email
read -p "📧 Ingresa tu email de Google: " EMAIL

echo ""
echo "🔗 Iniciando autenticación manual..."
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Ejecutar comando de autenticación
gogcli auth add "$EMAIL" --manual

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ Si completaste los pasos correctamente, ya estás autenticado"
echo ""
echo "🧪 Verificar:"
echo "   gogcli auth list"
echo "   gogcli gmail list"
```

---

## Troubleshooting

### Error: "stored credentials.json is missing client_id/client_secret"

Este error significa que tu archivo `credentials.json` tiene el formato incorrecto.

**Solución:**
```bash
cd ~/workspace/google-workspace-api
./fix-credentials.sh
```

El error ocurre porque Google Cloud Console descarga credenciales en formato:
```json
{"installed": {"client_id": "...", "client_secret": "..."}}
```

Pero gogcli espera el formato plano:
```json
{"client_id": "...", "client_secret": "..."}
```

El script `fix-credentials.sh` convierte automáticamente el formato.

### Error: "No matching credentials found"

```bash
# Verificar cuentas configuradas
gogcli auth list

# Si está vacío, repite la autenticación
gogcli auth add tu-email@gmail.com --manual
```

### Error: "Invalid grant"

El código de autorización expira en 10 minutos. Vuelve a generar uno nuevo.

### Error: "Access blocked"

Tu cuenta de Google puede tener bloqueado el acceso de apps menos seguras:

1. Ve a [Google Account Security](https://myaccount.google.com/security)
2. **Security** → **Less secure app access** (si está disponible)
3. O usa App Passwords

### Service Account: "Requested entity not found"

El service account no está autorizado correctamente en Google Admin Console.

1. Verifica el Client ID
2. Verifica que los scopes estén correctos
3. Verifica la cuenta de usuario para impersonación

---

## Recursos

- [gogcli Official Site](https://gogcli.sh/)
- [gogcli GitHub](https://github.com/steipete/gogcli)
- [Google Cloud Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Workspace Domain-wide Delegation](https://developers.google.com/admin-sdk/directory/v1/guides/delegation)

---

**¿Necesitas ayuda?** Revisa la documentación oficial de gogcli o Google Cloud IAM
