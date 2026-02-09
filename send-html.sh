#!/bin/bash
# send-html.sh - Enviar correos HTML usando gogcli + expect
# TESTED AND WORKING - message_id: 19c4434e4fb9417f
# METODO CONFIRMADO: Variable shell expandida

TO="${1:-brandom2ledesma@gmail.com}"
SUBJECT="${2:-Test HTML}"

# HTML SIN COMILLAS en atributos - UNA SOLA LÍNEA
# Para HTML largo, crear archivo aparte y usar $(cat archivo.html)
HTML="${3:-<h1>Hola desde Claude Code</h1><p>Este es un correo de <strong>prueba</strong> con HTML.</p><ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul><p style=color:blue>Texto azul</p><p style=color:#d93025>Texto rojo</p><a href=https://github.com>Enlace a GitHub</a><hr><p><em>Enviado desde gogcli</em></p>}"

# METODO CONFIRMADO FUNCIONANDO
# 1. Leer HTML a variable shell
HTML_CONTENT="$HTML"

# 2. Usar expect con comillas dobles para expandir variable
expect << EOF
set timeout 30
set html_body "$HTML_CONTENT"
spawn sh -c "gogcli gmail send --account=brandom2ledesma@gmail.com --to=$TO --subject='$SUBJECT' --body='Plain text version' --body-html='\$html_body'"
expect "Enter passphrase" { send "\r"; exp_continue }
expect eof
EOF

echo "✅ Correo HTML enviado a: $TO"
echo "📧 Asunto: $SUBJECT"
