# 05 - API Endpoints (Puntos de Conexión de la API)
# API Endpoints (Puntos de Conexión - Los comandos disponibles)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Sí - Cada endpoint debe tener tests de integración
COBERTURA MÍNIMA: 70%
CI/CD: Compatible - Tests de API corren en pipeline
DOCUMENTACIÓN: Auto-generada en /docs (Swagger/OpenAPI)
STACK: FastAPI genera documentación automática
```

---

## Que es un Endpoint (What is an Endpoint)

**Explicación simple:**
Un endpoint es como un botón de un control remoto:
- Cada botón hace algo específico
- Presionas "volumen +" → sube el volumen
- Presionas "canal 5" → cambia al canal 5

En nuestra API:
- `/upload` → sube archivos
- `/process` → procesa los archivos
- `/download` → descarga resultados

---

## Base URL (URL Base)

```
Desarrollo:  http://localhost:8000
Producción:  https://api.paradise-json-sync.com
```

---

## Documentacion Automatica (Automatic Documentation)

FastAPI genera documentación automática. Para verla:

```
Swagger UI:     http://localhost:8000/docs
ReDoc:          http://localhost:8000/redoc
OpenAPI JSON:   http://localhost:8000/openapi.json
```

---

## Lista de Endpoints (Endpoint List)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/health` | Health Check (Verificar que está vivo) | No |
| POST | `/api/v1/upload` | Upload Files (Subir archivos) | No |
| POST | `/api/v1/process` | Process Files (Procesar archivos) | No |
| GET | `/api/v1/status/{job_id}` | Job Status (Estado del trabajo) | No |
| GET | `/api/v1/download/{job_id}` | Download Results (Descargar resultados) | No |

---

## Detalle de Endpoints (Endpoint Details)

### 1. Health Check (Verificación de Salud)

**Propósito:** Verificar que el servidor está funcionando.

```
GET /health
```

**¿Cuándo usarlo?**
- Para verificar que el servidor está activo
- Para monitoreo automático
- Antes de enviar archivos

**Request (Petición):**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response Success (Respuesta Exitosa):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-02-04T10:30:00Z"
}
```

**Códigos de Respuesta:**
| Código | Significado |
|--------|-------------|
| 200 | Todo bien, servidor funcionando |
| 503 | Servidor con problemas |

**Tests requeridos:**
- [ ] Test: Retorna 200 cuando servidor está sano
- [ ] Test: Incluye versión en respuesta
- [ ] Test: Timestamp es válido

---

### 2. Upload Files (Subir Archivos)

**Propósito:** Recibir archivos JSON y PDF del usuario.

```
POST /api/v1/upload
```

**¿Cuándo usarlo?**
- Cuando el usuario selecciona archivos para procesar
- Primer paso del flujo de trabajo

**Request (Petición):**
```http
POST /api/v1/upload HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data

files: [archivo1.json, archivo2.json, archivo3.pdf]
```

**Ejemplo con cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "files=@factura1.json" \
  -F "files=@factura2.json" \
  -F "files=@facturas.pdf"
```

**Ejemplo con JavaScript:**
```javascript
const formData = new FormData();
formData.append('files', archivo1);
formData.append('files', archivo2);

const response = await fetch('/api/v1/upload', {
  method: 'POST',
  body: formData
});
```

**Response Success (Respuesta Exitosa):**
```json
{
  "success": true,
  "job_id": "abc123-def456-ghi789",
  "files_received": 3,
  "files_detail": [
    {
      "name": "factura1.json",
      "size": 1024,
      "type": "application/json",
      "status": "received"
    },
    {
      "name": "factura2.json",
      "size": 2048,
      "type": "application/json",
      "status": "received"
    },
    {
      "name": "facturas.pdf",
      "size": 102400,
      "type": "application/pdf",
      "status": "received"
    }
  ],
  "message": "3 archivos recibidos correctamente"
}
```

**Response Error (Respuesta de Error):**
```json
{
  "success": false,
  "error": "invalid_file_type",
  "message": "Solo se aceptan archivos .json y .pdf",
  "details": {
    "rejected_files": ["documento.docx"]
  }
}
```

**Códigos de Respuesta:**
| Código | Significado |
|--------|-------------|
| 200 | Archivos recibidos correctamente |
| 400 | Archivo inválido o formato no soportado |
| 413 | Archivo demasiado grande |
| 500 | Error interno del servidor |

**Validaciones:**
- [ ] Archivos deben ser `.json` o `.pdf`
- [ ] Tamaño máximo por archivo: 10 MB
- [ ] Máximo 100 archivos por petición

**Tests requeridos:**
- [ ] Test: Upload de 1 archivo JSON exitoso
- [ ] Test: Upload de múltiples archivos exitoso
- [ ] Test: Rechaza archivos con extensión inválida
- [ ] Test: Rechaza archivos demasiado grandes
- [ ] Test: Retorna job_id único

---

### 3. Process Files (Procesar Archivos)

**Propósito:** Iniciar el procesamiento de archivos subidos.

```
POST /api/v1/process
```

**¿Cuándo usarlo?**
- Después de subir archivos
- Para iniciar la extracción de datos y generación de resultados

**Request (Petición):**
```json
{
  "job_id": "abc123-def456-ghi789",
  "options": {
    "generate_excel": true,
    "generate_pdf": true,
    "sort_by": "date"
  }
}
```

**Opciones Disponibles:**

| Opción | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `generate_excel` | boolean | true | Generar archivo Excel |
| `generate_pdf` | boolean | true | Unir PDFs en uno |
| `sort_by` | string | "date" | Ordenar por: "date", "document_number", "client" |
| `include_summary` | boolean | true | Incluir hoja de resumen en Excel |

**Response Success (Respuesta Exitosa):**
```json
{
  "success": true,
  "job_id": "abc123-def456-ghi789",
  "status": "processing",
  "message": "Procesamiento iniciado. Usa /status/{job_id} para ver progreso.",
  "estimated_time_seconds": 30
}
```

**Códigos de Respuesta:**
| Código | Significado |
|--------|-------------|
| 200 | Proceso iniciado correctamente |
| 400 | Opciones inválidas |
| 404 | job_id no encontrado |
| 500 | Error al iniciar proceso |

**Tests requeridos:**
- [ ] Test: Inicia proceso con job_id válido
- [ ] Test: Rechaza job_id inexistente
- [ ] Test: Respeta opciones de configuración
- [ ] Test: Retorna tiempo estimado

---

### 4. Job Status (Estado del Trabajo)

**Propósito:** Consultar el progreso del procesamiento.

```
GET /api/v1/status/{job_id}
```

**¿Cuándo usarlo?**
- Para mostrar barra de progreso
- Para saber cuándo el proceso terminó

**Request (Petición):**
```http
GET /api/v1/status/abc123-def456-ghi789 HTTP/1.1
Host: localhost:8000
```

**Response - En Progreso:**
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "processing",
  "progress": 45,
  "current_step": "Procesando archivo 45 de 100",
  "steps_completed": [
    "Validación de archivos",
    "Extracción de datos JSON"
  ],
  "steps_pending": [
    "Generación de Excel",
    "Unificación de PDFs"
  ]
}
```

**Response - Completado:**
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "completed",
  "progress": 100,
  "current_step": "Proceso finalizado",
  "results": {
    "files_processed": 100,
    "files_success": 98,
    "files_error": 2,
    "excel_ready": true,
    "pdf_ready": true
  },
  "errors": [
    {
      "file": "factura_corrupta.json",
      "error": "JSON inválido en línea 15"
    }
  ],
  "download_url": "/api/v1/download/abc123-def456-ghi789"
}
```

**Response - Error:**
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "failed",
  "progress": 30,
  "error": "Error crítico durante procesamiento",
  "error_detail": "No se pudo acceder al archivo temporal"
}
```

**Estados Posibles:**
| Estado | Significado |
|--------|-------------|
| `pending` | En cola, esperando |
| `processing` | Trabajando |
| `completed` | Terminado con éxito |
| `completed_with_errors` | Terminado pero algunos archivos fallaron |
| `failed` | Falló completamente |

**Códigos de Respuesta:**
| Código | Significado |
|--------|-------------|
| 200 | Estado obtenido correctamente |
| 404 | job_id no encontrado |

**Tests requeridos:**
- [ ] Test: Retorna estado pending para trabajo nuevo
- [ ] Test: Retorna progreso correcto durante proceso
- [ ] Test: Retorna completed cuando termina
- [ ] Test: Incluye errores si los hubo
- [ ] Test: 404 para job_id inexistente

---

### 5. Download Results (Descargar Resultados)

**Propósito:** Descargar los archivos generados.

```
GET /api/v1/download/{job_id}
```

**Parámetros de Query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `type` | string | "all" | "excel", "pdf", "all" (zip con ambos) |

**Request - Descargar Excel:**
```http
GET /api/v1/download/abc123-def456-ghi789?type=excel HTTP/1.1
Host: localhost:8000
```

**Request - Descargar PDF:**
```http
GET /api/v1/download/abc123-def456-ghi789?type=pdf HTTP/1.1
Host: localhost:8000
```

**Request - Descargar Todo (ZIP):**
```http
GET /api/v1/download/abc123-def456-ghi789?type=all HTTP/1.1
Host: localhost:8000
```

**Response Success:**
- Retorna el archivo binario directamente
- Headers incluyen:
  ```
  Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  Content-Disposition: attachment; filename="facturas_2025-02-04.xlsx"
  ```

**Response Error:**
```json
{
  "success": false,
  "error": "results_not_ready",
  "message": "El proceso aún no ha terminado. Progreso actual: 75%"
}
```

**Códigos de Respuesta:**
| Código | Significado |
|--------|-------------|
| 200 | Archivo descargado correctamente |
| 400 | Tipo de archivo inválido |
| 404 | job_id no encontrado o resultados expirados |
| 409 | Proceso aún no terminado |

**Tests requeridos:**
- [ ] Test: Descarga Excel correctamente
- [ ] Test: Descarga PDF correctamente
- [ ] Test: Descarga ZIP con ambos
- [ ] Test: Error si proceso no terminó
- [ ] Test: 404 si job_id no existe

---

## Manejo de Errores (Error Handling)

### Formato Estándar de Error

```json
{
  "success": false,
  "error": "error_code",
  "message": "Mensaje legible para humanos",
  "details": {
    "campo_con_error": "Detalle específico"
  },
  "timestamp": "2025-02-04T10:30:00Z",
  "request_id": "req-123456"
}
```

### Códigos de Error Comunes

| Código | HTTP | Descripción |
|--------|------|-------------|
| `invalid_file_type` | 400 | Tipo de archivo no soportado |
| `file_too_large` | 413 | Archivo excede límite de tamaño |
| `job_not_found` | 404 | Job ID no existe |
| `results_not_ready` | 409 | Proceso aún en progreso |
| `processing_failed` | 500 | Error durante procesamiento |
| `internal_error` | 500 | Error interno del servidor |

---

## Rate Limiting (Límites de Peticiones)

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| `/health` | 100 | 1 minuto |
| `/upload` | 10 | 1 minuto |
| `/process` | 10 | 1 minuto |
| `/status` | 60 | 1 minuto |
| `/download` | 30 | 1 minuto |

---

## Proximo Documento (Next Document)

Continúa con: `06_Modelos_de_Datos.md` para ver las estructuras de datos.

---

**Versión:** 1.0
**Líneas:** ~400
**Cumple reglas:** Sí
