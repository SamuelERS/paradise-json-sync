# 10 - Guia de Despliegue (Deployment Guide)
# Deployment Guide (Guía de Despliegue - Cómo publicar la aplicación)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Todo debe pasar antes de desplegar
CI/CD: Preferir deploy automático via pipeline
BACKUP: Siempre antes de desplegar a producción
ROLLBACK: Tener plan de reversión listo
```

---

## Que es Desplegar (What is Deploying)

**Explicación simple:**
Desplegar es como mudarse a una casa nueva:
1. Empacas tus cosas (build)
2. Las llevas a la nueva casa (upload)
3. Las desempacas y acomodas (configuración)
4. Verificas que todo funcione (testing)

En software:
1. Generas los archivos finales (build)
2. Los subes al servidor (deploy)
3. Configuras variables de entorno (config)
4. Verificas que la app funcione (smoke test)

---

## Arquitectura de Despliegue (Deployment Architecture)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   ARQUITECTURA DE DESPLIEGUE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                           INTERNET                                      │
│                              │                                          │
│            ┌─────────────────┴─────────────────┐                        │
│            │                                   │                        │
│            ▼                                   ▼                        │
│   ┌─────────────────┐               ┌─────────────────┐                 │
│   │   SiteGround    │               │     Render      │                 │
│   │   (Frontend)    │               │    (Backend)    │                 │
│   │                 │               │                 │                 │
│   │  ┌───────────┐  │               │  ┌───────────┐  │                 │
│   │  │   React   │  │   API calls   │  │  FastAPI  │  │                 │
│   │  │   App     │──┼───────────────┼─►│  Server   │  │                 │
│   │  └───────────┘  │               │  └───────────┘  │                 │
│   │                 │               │                 │                 │
│   │  Archivos       │               │  Python +       │                 │
│   │  estáticos      │               │  dependencias   │                 │
│   │  (.html, .js)   │               │                 │                 │
│   └─────────────────┘               └─────────────────┘                 │
│                                                                         │
│   URL: paradise-json-sync.com       URL: api.paradise-json-sync.com     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Pre-requisitos (Prerequisites)

### Antes de Desplegar

- [ ] Todos los tests pasan (`pytest` y `npm test`)
- [ ] Build genera sin errores (`npm run build`)
- [ ] Variables de entorno configuradas
- [ ] Acceso a los servidores (credenciales)
- [ ] Backup del estado actual (si es update)

### Accesos Necesarios

| Servicio | Qué necesitas | Para qué |
|----------|---------------|----------|
| Render | Cuenta + API Key | Backend |
| SiteGround | Cuenta + FTP | Frontend |
| GitHub | Permisos de push | CI/CD |

---

## Despliegue del Backend (Backend Deployment)

### Opcion 1: Despliegue Automatico via CI/CD (Recomendado)

```
PASOS:
1. Merge tu código a la rama `main`
2. GitHub Actions detecta el merge
3. CI/CD corre tests automáticamente
4. Si todo pasa, despliega a Render

NO NECESITAS HACER NADA MÁS.
```

### Opcion 2: Despliegue Manual a Render

**Paso 1: Preparar el código**
```bash
# Asegurarte de estar en main actualizado
git checkout main
git pull origin main

# Verificar que todo funciona
cd backend
pytest
```

**Paso 2: Configurar Render (primera vez)**

1. Ir a https://render.com
2. Click "New" → "Web Service"
3. Conectar repositorio de GitHub
4. Configurar:
   - Name: `paradise-json-sync-api`
   - Region: Oregon (US West)
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

**Paso 3: Configurar variables de entorno**

En Render → Environment:
```
PYTHON_VERSION=3.11.0
ENV=production
ALLOWED_ORIGINS=https://paradise-json-sync.com
```

**Paso 4: Desplegar**

- Render detecta cambios automáticamente al hacer push a main
- O puedes hacer deploy manual desde el dashboard

**Paso 5: Verificar**

```bash
# Verificar que el servidor responde
curl https://api.paradise-json-sync.com/health

# Respuesta esperada:
# {"status": "healthy", "version": "1.0.0"}
```

---

## Despliegue del Frontend (Frontend Deployment)

### Opcion 1: Despliegue Automatico via CI/CD (Recomendado)

```
PASOS:
1. Merge tu código a la rama `main`
2. GitHub Actions corre el build
3. Sube automáticamente a SiteGround via FTP

NO NECESITAS HACER NADA MÁS.
```

### Opcion 2: Despliegue Manual a SiteGround

**Paso 1: Generar el build**

```bash
cd frontend

# Instalar dependencias
npm ci

# Generar build de producción
npm run build

# Los archivos quedan en: frontend/dist/
```

**Paso 2: Configurar variables de entorno**

Crear archivo `.env.production`:
```bash
VITE_API_URL=https://api.paradise-json-sync.com
```

Rebuild con variables de producción:
```bash
npm run build
```

**Paso 3: Subir archivos via FTP**

Usando FileZilla o cliente FTP:

1. Conectar a SiteGround:
   - Host: tudominio.com
   - Usuario: (desde cPanel)
   - Password: (desde cPanel)
   - Puerto: 21

2. Navegar a `/public_html/`

3. Subir contenido de `frontend/dist/`:
   - Todos los archivos y carpetas
   - Sobrescribir archivos existentes

**Paso 4: Configurar SiteGround**

En cPanel → Site Tools:

1. **SSL:** Asegurar que HTTPS está activo
2. **Cache:** Limpiar caché después de deploy
3. **Redirects:** Configurar SPA routing

Crear `.htaccess` para React SPA:
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-l
  RewriteRule . /index.html [L]
</IfModule>
```

**Paso 5: Verificar**

1. Abrir https://paradise-json-sync.com
2. Verificar que carga correctamente
3. Probar subir un archivo
4. Verificar conexión con backend

---

## Variables de Entorno por Ambiente (Environment Variables)

### Development (Local)

```bash
# backend/.env
ENV=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173
LOG_LEVEL=debug

# frontend/.env
VITE_API_URL=http://localhost:8000
```

### Staging

```bash
# backend (en Render)
ENV=staging
DEBUG=false
ALLOWED_ORIGINS=https://staging.paradise-json-sync.com
LOG_LEVEL=info

# frontend (en SiteGround staging)
VITE_API_URL=https://api-staging.paradise-json-sync.com
```

### Production

```bash
# backend (en Render)
ENV=production
DEBUG=false
ALLOWED_ORIGINS=https://paradise-json-sync.com
LOG_LEVEL=warning

# frontend (en SiteGround)
VITE_API_URL=https://api.paradise-json-sync.com
```

---

## Verificacion Post-Deploy (Post-Deploy Verification)

### Smoke Tests (Pruebas Básicas)

Ejecutar después de cada deploy:

```bash
# 1. Backend health check
curl -s https://api.paradise-json-sync.com/health | jq

# Esperado: {"status": "healthy"}

# 2. Frontend loads
curl -s -o /dev/null -w "%{http_code}" https://paradise-json-sync.com

# Esperado: 200

# 3. API documentation accessible
curl -s -o /dev/null -w "%{http_code}" https://api.paradise-json-sync.com/docs

# Esperado: 200
```

### Checklist de Verificación

- [ ] Frontend carga correctamente
- [ ] No hay errores en consola del navegador
- [ ] Backend responde en /health
- [ ] Documentación de API accesible en /docs
- [ ] Upload de archivos funciona
- [ ] Procesamiento funciona
- [ ] Descarga funciona
- [ ] HTTPS funciona sin errores

---

## Rollback (Revertir Cambios)

### Si Algo Sale Mal

**Backend (Render):**
1. Ir a Render Dashboard
2. Click en el servicio
3. Click en "Deploys"
4. Seleccionar un deploy anterior exitoso
5. Click "Redeploy"

**Frontend (SiteGround):**
1. Restaurar desde backup (si tienes)
2. O re-subir versión anterior via FTP

### Crear Backup Antes de Deploy

```bash
# En SiteGround, via cPanel:
# Backup → Download Full Backup

# O manualmente:
# Descargar /public_html/ antes de sobrescribir
```

---

## Troubleshooting (Resolución de Problemas)

### Error: Backend no responde

```
SÍNTOMA: curl https://api.../health no responde

POSIBLES CAUSAS:
1. El servicio no inició
2. Error en el código
3. Puerto mal configurado

SOLUCIÓN:
1. Revisar logs en Render Dashboard
2. Buscar errores de inicio
3. Verificar que Start Command es correcto
```

### Error: Frontend muestra página en blanco

```
SÍNTOMA: La página carga pero está en blanco

POSIBLES CAUSAS:
1. Build falló silenciosamente
2. Rutas mal configuradas
3. Variables de entorno incorrectas

SOLUCIÓN:
1. Abrir consola del navegador (F12)
2. Ver errores en Console
3. Verificar Network tab
4. Revisar que VITE_API_URL es correcto
```

### Error: CORS (Cross-Origin)

```
SÍNTOMA: Error "blocked by CORS policy" en consola

CAUSA: Backend no permite requests del frontend

SOLUCIÓN:
1. Verificar ALLOWED_ORIGINS en backend
2. Debe incluir el dominio del frontend
3. Ejemplo: ALLOWED_ORIGINS=https://paradise-json-sync.com
```

---

## Comandos Utiles (Useful Commands)

### Verificar Estado de Servicios

```bash
# Backend health
curl https://api.paradise-json-sync.com/health

# Frontend status
curl -I https://paradise-json-sync.com

# DNS check
nslookup paradise-json-sync.com
nslookup api.paradise-json-sync.com
```

### Logs

```bash
# En Render Dashboard:
# Services → paradise-json-sync-api → Logs

# Filtrar por errores:
# Buscar "ERROR" o "Exception"
```

---

## Checklist Final de Despliegue (Final Deployment Checklist)

### Antes del Deploy

- [ ] Tests locales pasan
- [ ] Build local funciona
- [ ] Variables de entorno listas
- [ ] Backup creado (si es update)

### Durante el Deploy

- [ ] CI/CD pipeline verde
- [ ] No hay errores en logs de deploy
- [ ] Servicios inician correctamente

### Después del Deploy

- [ ] Smoke tests pasan
- [ ] Funcionalidad principal verificada
- [ ] No hay errores en logs
- [ ] Usuarios pueden acceder
- [ ] Monitoreo activo

---

## Contacto de Emergencia (Emergency Contact)

Si algo sale muy mal en producción:

1. **Rollback inmediato** (ver sección Rollback)
2. **Revisar logs** para identificar el problema
3. **Documentar** qué pasó y cómo se resolvió
4. **Post-mortem** para evitar que vuelva a pasar

---

**Versión:** 1.0
**Líneas:** ~400
**Cumple reglas:** Sí

---

## Fin de la Guia Arquitectonica (End of Architectural Guide)

Has completado la lectura de toda la guía arquitectónica.

**Próximos pasos:**
1. Volver a `00_README.md` para ver el índice
2. Marcar los documentos como leídos
3. Comenzar el desarrollo siguiendo las guías
