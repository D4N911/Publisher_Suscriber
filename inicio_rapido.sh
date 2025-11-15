#!/bin/bash
# Script de inicio rápido para el sistema Publisher-Subscriber

echo "=========================================="
echo "Sistema Publisher-Subscriber"
echo "=========================================="
echo ""
echo "Este script iniciará el servidor y múltiples clientes."
echo "Presiona Ctrl+C para detener todo."
echo ""
read -p "Presiona Enter para continuar..."

# Configuración
CRITERIO=${1:-ponderado}  # Criterio por defecto: ponderado
NUM_CLIENTES=${2:-5}       # Número de clientes por defecto: 5

echo ""
echo "Configuración:"
echo "  - Criterio: $CRITERIO"
echo "  - Número de clientes: $NUM_CLIENTES"
echo ""

# Iniciar servidor en background
echo "Iniciando servidor..."
python3 server_integrated.py --criterio $CRITERIO &
SERVER_PID=$!

# Esperar a que el servidor inicie
sleep 2

# Iniciar clientes
echo "Iniciando $NUM_CLIENTES clientes..."
for i in $(seq 1 $NUM_CLIENTES); do
    python3 client_integrated.py --id "cliente_$i" &
    sleep 0.2
done

echo ""
echo "Sistema en ejecución."
echo "Servidor PID: $SERVER_PID"
echo ""
echo "Para detener, presiona Ctrl+C o ejecuta: kill $SERVER_PID"

# Esperar a que termine el servidor o recibir señal
wait $SERVER_PID

echo ""
echo "Servidor finalizado. Deteniendo clientes..."
pkill -f "client_integrated.py"
echo "Sistema detenido."

