#!/bin/bash
# Script para detener procesos del servidor que están usando los puertos

echo "Buscando procesos usando los puertos 8888 y 8889..."

# Buscar procesos en el puerto 8888
PIDS_8888=$(lsof -ti :8888)
if [ ! -z "$PIDS_8888" ]; then
    echo "Procesos usando puerto 8888: $PIDS_8888"
    kill -9 $PIDS_8888 2>/dev/null
    echo "✓ Procesos en puerto 8888 detenidos"
else
    echo "No hay procesos usando el puerto 8888"
fi

# Buscar procesos en el puerto 8889
PIDS_8889=$(lsof -ti :8889)
if [ ! -z "$PIDS_8889" ]; then
    echo "Procesos usando puerto 8889: $PIDS_8889"
    kill -9 $PIDS_8889 2>/dev/null
    echo "✓ Procesos en puerto 8889 detenidos"
else
    echo "No hay procesos usando el puerto 8889"
fi

# Buscar procesos de Python relacionados
PYTHON_PIDS=$(ps aux | grep -E "server_integrated.py|client_integrated.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PYTHON_PIDS" ]; then
    echo "Procesos Python relacionados encontrados: $PYTHON_PIDS"
    kill -9 $PYTHON_PIDS 2>/dev/null
    echo "✓ Procesos Python detenidos"
else
    echo "No hay procesos Python relacionados ejecutándose"
fi

echo ""
echo "Listo. Los puertos deberían estar disponibles ahora."

