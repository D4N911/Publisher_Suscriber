#!/bin/bash
# Script para subir solo los archivos necesarios a GitHub

echo "=========================================="
echo "Preparando archivos para GitHub"
echo "=========================================="
echo ""

# Verificar si git está inicializado
if [ ! -d ".git" ]; then
    echo "Inicializando repositorio git..."
    git init
fi

# Verificar si el remote existe
if ! git remote | grep -q "origin"; then
    echo "Agregando remote origin..."
    git remote add origin https://github.com/D4N911/Publisher_Suscriber.git
fi

echo ""
echo "Agregando archivos necesarios..."

# Agregar solo los archivos necesarios
git add server_integrated.py
git add client_integrated.py
git add run_clients.py
git add README.md
git add DOCUMENTACION.md
git add DIAGRAMAS.md
git add requirements.txt
git add .gitignore

echo ""
echo "Archivos agregados:"
git status --short

echo ""
read -p "¿Deseas hacer commit y push? (s/n): " respuesta

if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
    echo ""
    echo "Haciendo commit..."
    git commit -m "Implementación completa del sistema Publisher-Subscriber
    
    - Servidor Publisher con tres criterios de selección (aleatorio, ponderado, condicional)
    - Cliente Subscriber con suscripción a 1 o 2 colas
    - Sistema de comunicación por sockets TCP
    - Registro de resultados y suscripciones
    - Criterio de paro (1 millón de resultados)
    - Reporte final completo
    - Documentación técnica completa
    - Diagramas de arquitectura"
    
    echo ""
    echo "Subiendo a GitHub..."
    git branch -M main
    git push -u origin main
    
    echo ""
    echo "✅ ¡Archivos subidos exitosamente!"
else
    echo ""
    echo "Commit cancelado. Los archivos están en staging."
    echo "Puedes revisarlos con: git status"
    echo "Para hacer commit manualmente: git commit -m 'mensaje'"
    echo "Para hacer push: git push -u origin main"
fi

