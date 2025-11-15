# Instrucciones para Subir a GitHub

## ✅ Estado Actual

Los siguientes archivos están listos para subir:

- ✅ `server_integrated.py` - Servidor Publisher
- ✅ `client_integrated.py` - Cliente Subscriber  
- ✅ `run_clients.py` - Script para múltiples clientes
- ✅ `README.md` - Documentación de uso
- ✅ `DOCUMENTACION.md` - Documentación técnica
- ✅ `DIAGRAMAS.md` - Diagramas de arquitectura
- ✅ `requirements.txt` - Dependencias
- ✅ `.gitignore` - Archivos ignorados

**Commit realizado**: ✅
**Remote configurado**: ✅
**Branch**: main

## 🚀 Para Subir a GitHub

### Opción 1: Comando Directo

```bash
git push -u origin main
```

Si te pide autenticación, usa tu token de acceso personal de GitHub.

### Opción 2: Si necesitas autenticación

1. **Crear un Personal Access Token** (si no tienes uno):
   - Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Genera un nuevo token con permisos `repo`
   - Copia el token

2. **Usar el token como contraseña**:
   ```bash
   git push -u origin main
   # Username: tu_usuario_github
   # Password: tu_token (no tu contraseña)
   ```

### Opción 3: Usar SSH (si tienes configurado)

```bash
git remote set-url origin git@github.com:D4N911/Publisher_Suscriber.git
git push -u origin main
```

## 📋 Verificación

Después de hacer push, verifica en:
https://github.com/D4N911/Publisher_Suscriber

Deberías ver todos los archivos listados arriba.

## 🔄 Para Futuras Actualizaciones

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

