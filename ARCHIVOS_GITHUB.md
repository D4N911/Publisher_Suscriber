# Archivos para Subir a GitHub

## ✅ Archivos Necesarios (Incluir)

### Código Principal
- `server_integrated.py` - Servidor Publisher
- `client_integrated.py` - Cliente Subscriber
- `run_clients.py` - Script para ejecutar múltiples clientes

### Documentación
- `README.md` - Guía de uso
- `DOCUMENTACION.md` - Documentación técnica y comparativa
- `DIAGRAMAS.md` - Diagramas de arquitectura

### Configuración
- `requirements.txt` - Dependencias (vacío, solo stdlib)
- `.gitignore` - Archivos a ignorar

## ❌ Archivos NO Necesarios (Excluir)

- `server.py` - Versión alternativa
- `client.py` - Versión alternativa
- `test_rapido.py` - Solo para pruebas
- `demo.py` - Solo para demostración
- `inicio_rapido.sh` - Script bash opcional
- `detener_servidor.sh` - Utilidad opcional
- `ARCHIVOS_GITHUB.md` - Este archivo (solo referencia)

## 📋 Comandos para Subir

```bash
# 1. Inicializar git (si no está inicializado)
git init

# 2. Agregar archivos necesarios
git add server_integrated.py
git add client_integrated.py
git add run_clients.py
git add README.md
git add DOCUMENTACION.md
git add DIAGRAMAS.md
git add requirements.txt
git add .gitignore

# 3. Commit
git commit -m "Implementación completa del sistema Publisher-Subscriber"

# 4. Agregar remote (si no está agregado)
git remote add origin https://github.com/D4N911/Publisher_Suscriber.git

# 5. Subir a GitHub
git branch -M main
git push -u origin main
```

## 🔄 O Usar el Script Automático

Ejecuta `subir_github.sh` para subir automáticamente.

