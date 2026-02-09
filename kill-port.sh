#!/bin/bash
# kill-port.sh - Matar proceso que está usando un puerto específico
# Uso: ./kill-port.sh [PUERTO]
# Ejemplo: ./kill-port.sh 9001

if [ -z "$1" ]; then
    echo "Uso: $0 [PUERTO]"
    echo "Ejemplo: $0 9001"
    exit 1
fi

PORT=$1

# Verificar si hay algo corriendo en el puerto
PIDS=$(lsof -ti :$PORT 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✅ No hay procesos corriendo en el puerto $PORT"
    exit 0
fi

# Mostrar información antes de matar
echo "Procesos encontrados en el puerto $PORT:"
lsof -i :$PORT 2>/dev/null | grep -v COMMAND
echo ""

# Matar procesos
echo "Matando procesos en el puerto $PORT..."
lsof -ti :$PORT | xargs kill -9 2>/dev/null

# Verificar que se mataron
sleep 1
REMAINING=$(lsof -ti :$PORT 2>/dev/null)
if [ -z "$REMAINING" ]; then
    echo "✅ Puerto $PORT liberado correctamente"
else
    echo "⚠️  Algunos procesos no pudieron ser matados"
    exit 1
fi
