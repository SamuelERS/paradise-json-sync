# Reglas del Programador v3.0

**Guía práctica con ejemplos para desarrolladores - Paradise System Labs**

> **Audiencia:** Programadores, desarrolladores nuevos, agentes IA
> **Tipo:** Tutorial práctico - Muestra CÓMO se aplican las reglas con ejemplos
> **Última actualización:** 2025-12-26

---

## Qué es este documento

Este documento es una **guía práctica con ejemplos extensos** de cómo aplicar los estándares del proyecto. Complementa a:

- [REGLAS_DE_LA_CASA.md](./REGLAS_DE_LA_CASA.md) - El POR QUÉ (gobernanza, filosofía)
- [REGLAS_DESARROLLO.md](REGLAS_DESARROLLO.md) - El QUÉ (estándares técnicos)

**Este documento muestra el CÓMO** con código real, tutoriales y ejemplos detallados.

---

## Contenido

1. [Misión del Programador](#1-misión-del-programador)
2. [Evitar Monolitos](#2-evitar-monolitos)
3. [Comentar Código Profesionalmente](#3-comentar-código-profesionalmente)
4. [Scripts Ordenados y Reutilizables](#4-scripts-ordenados-y-reutilizables)
5. [Código Sólido y Autónomo](#5-código-sólido-y-autónomo)
6. [Docker y Entorno](#6-docker-y-entorno)
7. [Gestión de Puertos](#7-gestión-de-puertos)
8. [Variables de Entorno](#8-variables-de-entorno)
9. [Checklist Oficial](#9-checklist-oficial)
10. [Reporte Ejecutivo](#10-reporte-ejecutivo)

---

## 1. Misión del Programador

### Principio Fundamental

> **"Cada línea de código debe incrementar la inteligencia del sistema, no su complejidad."**

### Objetivos

Entregar código que:
- Es limpio, comentado y organizado
- No es monolítico
- Reduce la complejidad
- Se mantiene solo sin intervención manual

### Características del Buen Código

| Característica | Significado |
|----------------|-------------|
| **Predecible** | Se comporta como se espera |
| **Mantenible** | Fácil de modificar sin romper |
| **Inteligible** | Cualquiera puede entenderlo |
| **Autónomo** | Se mantiene solo |

---

## 2. Evitar Monolitos

### Regla de Oro

> **"Si para agregar una función debo tocar muchas partes a la vez, ya hay un diseño incorrecto."**

### Ejemplo Práctico

```typescript
// ❌ MAL - Función monolítica (500+ líneas)
function processWhatsAppMessage(message: any) {
    // Validación
    if (!message) return;
    if (!message.from) return;
    if (!message.body) return;

    // Autorización
    const user = db.query('SELECT * FROM users WHERE phone = ?', [message.from]);
    if (!user) return;
    if (!user.active) return;

    // Parsing
    const parsed = {
        text: message.body.trim(),
        timestamp: new Date(),
        // ... 50 líneas más de parsing
    };

    // Guardado
    db.insert('messages', parsed);

    // Notificación
    webhook.send(parsed);

    // Métricas
    metrics.increment('messages_processed');

    // Logging
    console.log('Message processed:', parsed.id);

    // ... 300 líneas más
}

// ✅ BIEN - Funciones modulares
function processWhatsAppMessage(message: WhatsAppMessage): ProcessResult {
    const validation = validateMessage(message);
    if (!validation.isValid) return validation;

    const auth = checkAuthorization(message.from);
    if (!auth.authorized) return auth;

    const parsed = parseMessageContent(message);
    const saved = saveMessageToDatabase(parsed);

    notifyRelevantParties(saved);
    updateSystemMetrics(saved);
    logMessageActivity(saved);

    return { success: true, messageId: saved.id };
}

// Cada función hace UNA cosa
function validateMessage(message: WhatsAppMessage): ValidationResult {
    if (!message) return { isValid: false, error: 'Message is null' };
    if (!message.from) return { isValid: false, error: 'No sender' };
    if (!message.body) return { isValid: false, error: 'No body' };
    return { isValid: true };
}

function checkAuthorization(phone: string): AuthResult {
    const user = userService.findByPhone(phone);
    if (!user) return { authorized: false, reason: 'User not found' };
    if (!user.active) return { authorized: false, reason: 'User inactive' };
    return { authorized: true, user };
}
```

### Qué Hacer si Heredas un Monolito

1. **Solo modificar lo necesario** para la tarea actual
2. **NUNCA** hacerlo más grande
3. **Proponer refactorización** futura si el módulo lo requiere
4. **Documentar el problema** en el código

```typescript
// Ejemplo de documentación de monolito heredado
/**
 * NOTA TÉCNICA: Este archivo es un monolito heredado de ~800 líneas.
 * Se mantiene intacto por compatibilidad.
 *
 * PLAN DE REFACTORIZACIÓN:
 * - Extraer validación a MessageValidator.ts
 * - Extraer parsing a MessageParser.ts
 * - Extraer notificaciones a NotificationService.ts
 *
 * Ver: docs/refactoring/legacy-handler-plan.md
 */
```

---

## 3. Comentar Código Profesionalmente

### Qué Comentar

```typescript
/**
 * Procesa mensaje de WhatsApp y lo enruta según su tipo
 *
 * IMPORTANTE: Solo procesa mensajes de texto plano.
 * Para multimedia usar processMultimediaMessage()
 *
 * @param message - Mensaje raw de WPPConnect
 * @returns ID del mensaje procesado o null si falla
 *
 * Limitaciones:
 * - No soporta mensajes de grupo
 * - Asume que el cliente ya está autenticado
 */
async function processWhatsAppMessage(message: WhatsAppMessage): Promise<string | null> {
    // Validar que el mensaje tenga contenido de texto
    // (mensajes vacíos se descartan por diseño)
    if (!message.body || message.body.trim().length === 0) {
        return null;
    }

    // ... resto del código
}
```

### Qué NO Comentar

```typescript
// ❌ MAL - Obvio y redundante
// Suma 1 al contador
counter = counter + 1;

// Retorna verdadero
return true;

// ✅ BIEN - Explica decisión no obvia
// Incrementamos ANTES de validar para evitar race conditions
counter = counter + 1;
if (validateState()) {
    // ...
}
```

### Características de Buenos Comentarios

| Característica | Descripción |
|----------------|-------------|
| **Breves** | No novelas |
| **Precisos** | Explican el "por qué", no el "qué" obvio |
| **Útiles** | Aportan contexto no evidente |
| **Actualizados** | Coinciden con el código actual |

---

## 4. Scripts Ordenados y Reutilizables

### Estructura de Carpetas

```
/scripts/
├── operations/      # Scripts de operación (.bat/.ps1)
├── diagnostics/     # Scripts de diagnóstico
├── docker/          # Scripts de Docker
└── maintenance/     # Limpieza, backups, etc.
```

### Antes de Crear un Script

1. **Buscar** si ya existe uno similar
2. **Si existe:** Mejorarlo o extenderlo
3. **Si no existe:** Crear en la carpeta correcta con documentación

### Plantilla de Script Estándar

```javascript
/**
 * Script: Limpiar logs antiguos del sistema
 *
 * Propósito:
 *   Elimina archivos de log con más de 30 días de antigüedad
 *   para evitar saturación de disco.
 *
 * Uso:
 *   node scripts/maintenance/clean-old-logs.js [days]
 *
 * Parámetros:
 *   days (opcional) - Días de antigüedad. Default: 30
 *
 * Ejemplo:
 *   node scripts/maintenance/clean-old-logs.js 60
 *
 * Dependencias:
 *   - fs-extra
 *   - path
 *
 * Autor: [Tu nombre]
 * Fecha: 2025-12-26
 */

const fs = require('fs-extra');
const path = require('path');

// Configuración
const DEFAULT_DAYS = 30;
const LOGS_DIR = path.join(__dirname, '../../logs');

// Función principal
async function cleanOldLogs(daysOld = DEFAULT_DAYS) {
    console.log(`🧹 Limpiando logs más antiguos de ${daysOld} días...`);

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysOld);

    const files = await fs.readdir(LOGS_DIR);
    let deleted = 0;

    for (const file of files) {
        const filePath = path.join(LOGS_DIR, file);
        const stats = await fs.stat(filePath);

        if (stats.mtime < cutoffDate) {
            await fs.remove(filePath);
            deleted++;
            console.log(`  ✓ Eliminado: ${file}`);
        }
    }

    console.log(`\n✅ Limpieza completada. ${deleted} archivos eliminados.`);
    return deleted;
}

// Ejecutar si se llama directamente
if (require.main === module) {
    const days = parseInt(process.argv[2]) || DEFAULT_DAYS;
    cleanOldLogs(days)
        .then(() => process.exit(0))
        .catch(err => {
            console.error('❌ Error:', err.message);
            process.exit(1);
        });
}

module.exports = { cleanOldLogs };
```

### Reglas para Scripts

| Regla | Descripción |
|-------|-------------|
| Siempre en carpeta correcta | No dejarlos "sueltos" |
| Nombre descriptivo | `clean-old-logs.js`, no `script1.js` |
| Documentación completa | Qué hace, cómo se usa, qué necesita |
| Exportable | Poder usarlo como módulo |
| Sin hardcodear rutas | Usar paths relativos o ENV |

---

## 5. Código Sólido y Autónomo

### Auto-Recovery

```typescript
// ✅ BIEN - Sistema que se recupera solo
async function connectToDatabase(): Promise<Connection> {
    const maxRetries = 3;
    let attempt = 0;

    while (attempt < maxRetries) {
        try {
            const connection = await db.connect();
            logger.info('Database connected', { attempt });
            return connection;
        } catch (error) {
            attempt++;
            logger.warn('Connection failed, retrying...', { attempt, error });
            await sleep(1000 * attempt); // Backoff exponencial
        }
    }

    throw new Error('Failed to connect after retries');
}
```

### Evitar Redundancias

```typescript
// ❌ MAL - Código duplicado
function formatUserName(user) {
    return user.firstName + ' ' + user.lastName;
}

function formatAgentName(agent) {
    return agent.firstName + ' ' + agent.lastName;
}

// ✅ BIEN - Función compartida
function formatFullName(person: { firstName: string, lastName: string }): string {
    return `${person.firstName} ${person.lastName}`.trim();
}

const userName = formatFullName(user);
const agentName = formatFullName(agent);
```

### Validación Exhaustiva

```typescript
// ✅ BIEN - Validación completa
function processPayment(amount: number, currency: string): PaymentResult {
    // Validar inputs
    if (amount <= 0) {
        throw new ValidationError('Amount must be positive');
    }

    if (!['USD', 'EUR', 'MXN'].includes(currency)) {
        throw new ValidationError(`Unsupported currency: ${currency}`);
    }

    // Validar estado del sistema
    if (!paymentGateway.isConnected()) {
        throw new ConnectionError('Payment gateway not available');
    }

    // Procesar
    return paymentGateway.process(amount, currency);
}
```

### Manejo de Errores Específico

```typescript
// ✅ BIEN - Errores específicos y recuperables
async function fetchUserData(userId: string): Promise<User> {
    try {
        const response = await api.get(`/users/${userId}`);
        return response.data;
    } catch (error) {
        if (error.response?.status === 404) {
            throw new UserNotFoundError(userId);
        }

        if (error.response?.status === 403) {
            throw new UnauthorizedError('No access to user data');
        }

        // Error genérico
        logger.error('Failed to fetch user', { userId, error });
        throw new Error('Failed to fetch user data');
    }
}
```

---

## 6. Docker y Entorno

### Cuándo Usar Docker

| Usar Docker | No Usar Docker |
|-------------|----------------|
| Base de datos (PostgreSQL, MongoDB) | Debug complejo con breakpoints |
| Redis, RabbitMQ | Hot-reload lento |
| Workers en background | Performance degradada en desarrollo |
| Deploy a producción | Conexiones a servicios externos locales |

### Regla General

> **"Todo lo que pueda vivir en Docker sin perjudicar el desarrollo, va en Docker."**

### docker-compose.yml Ejemplo

```yaml
version: '3.8'

services:
  # ✅ Base de datos - SIEMPRE en Docker
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: whatsapp_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # ✅ Redis - SIEMPRE en Docker
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # ⚠️ App Node.js - Opcional según necesidad de debug
  api:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://admin:${DB_PASSWORD}@postgres:5432/whatsapp_db
      REDIS_URL: redis://redis:6379
    volumes:
      - ./backend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
```

### Si Trabajas Fuera de Docker

1. **El servicio final DEBE funcionar en Docker**
2. **Documentar la razón** en README
3. **Verificar que deploy a producción use Docker**

```markdown
# Desarrollo Local (Sin Docker)

**Razón:** Hot-reload de Vite es 10x más lento en Docker en Windows.

**Para desarrollo:**
npm install && npm run dev

**Para producción:**
docker-compose up --build
```

---

## 7. Gestión de Puertos

### Tabla de Puertos del Proyecto

| Servicio | Puerto | Protocolo | Descripción |
|----------|--------|-----------|-------------|
| WPPConnect Server | 3000 | HTTP | Cliente WhatsApp |
| Memory API | 3001 | HTTP | Persistencia |
| Dashboard Lovable | 5173 | HTTP | Frontend React |
| Bridge API | 8080 | HTTP | Gateway central |
| Dashboard Monitor | 8081 | HTTP | API de monitoreo |
| WebSocket | 8082 | WS | Real-time events |

### Antes de Iniciar una Tarea

1. **Revisar puertos usados** en docker-compose.yml y .env
2. **Elegir puerto libre**
3. **Documentar en 3 lugares:** .env, docker-compose, docs

### Verificar Puertos en Sistema

```bash
# Windows
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :3000
ss -tulpn | grep :3000
```

### Resolver Conflictos

```bash
# Error común
Error: listen EADDRINUSE: address already in use :::3000

# Solución 1: Matar proceso
kill -9 <PID>

# Solución 2: Cambiar puerto en .env
API_PORT=3001
```

---

## 8. Variables de Entorno

### Estructura Estándar

```bash
# .env.example - Template público (sí va en Git)
# .env - Valores locales (NO va en Git)
# .env.production - Producción (encriptado)
```

### Ejemplo Completo

```bash
# .env.example
# ======================
# CONFIGURACIÓN DEL PROYECTO
# ======================

# Node
NODE_ENV=development

# Servidor API
API_PORT=3000
API_HOST=localhost

# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=whatsapp_db
DB_USER=admin
DB_PASSWORD=change_this_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Servicios Externos
WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_KEY=your_api_key_here

# Seguridad
JWT_SECRET=your_jwt_secret_here

# Logging
LOG_LEVEL=debug
```

### Validación al Inicio

```typescript
// config/validate-env.ts
import { z } from 'zod';

const envSchema = z.object({
    NODE_ENV: z.enum(['development', 'production', 'test']),
    API_PORT: z.string().transform(Number),
    DB_HOST: z.string(),
    DB_PORT: z.string().transform(Number),
    DB_NAME: z.string(),
    DB_USER: z.string(),
    DB_PASSWORD: z.string().min(8),
    JWT_SECRET: z.string().min(32),
});

// Validar al inicio - falla rápido si falta algo
export const env = envSchema.parse(process.env);
```

### Reglas de Variables de Entorno

| SIEMPRE | NUNCA |
|---------|-------|
| Agregar nueva variable a .env.example | Hardcodear valores en código |
| Usar valores de ejemplo | Commitear .env a Git |
| Documentar con comentarios | Usar valores de producción en desarrollo |
| Validar que existan al inicio | Dejar variables sin documentar |

---

## 9. Checklist Oficial

Antes de marcar una tarea como "terminada", responde SÍ a todas:

### Calidad de Código
- [ ] Evité crear monolitos
- [ ] Dividí en funciones pequeñas
- [ ] Nombres claros y descriptivos
- [ ] Código legible sin comentarios excesivos
- [ ] Sin código duplicado
- [ ] Sin código muerto

### Documentación
- [ ] Comenté partes complejas (el "por qué")
- [ ] Actualicé README si agregué funcionalidad
- [ ] JSDoc/TSDoc en funciones públicas

### Organización
- [ ] Archivos en carpeta correcta
- [ ] Scripts organizados (no "sueltos")
- [ ] Convenciones de naming respetadas

### Seguridad y Configuración
- [ ] Sin credenciales hardcodeadas
- [ ] Variables de entorno para configuración
- [ ] Input de usuario validado
- [ ] Sin info sensible en logs
- [ ] Nuevas variables en .env.example

### Docker y Entorno
- [ ] Docker usado cuando apropiado
- [ ] Sin conflictos de puertos
- [ ] Puerto documentado en 3 lugares
- [ ] Dependencias justificadas

### Testing
- [ ] Tests para funcionalidad crítica
- [ ] Casos edge cubiertos
- [ ] Todos los tests pasan
- [ ] Funcionalidad probada manualmente

### Autonomía del Sistema
- [ ] Manejo de errores sin crashear
- [ ] Retry logic donde necesario
- [ ] Logs suficientes para debugging

---

## 10. Reporte Ejecutivo

Al terminar cada sesión, entregar este reporte:

### Formato

```markdown
# Reporte Ejecutivo - [Fecha]

## 1. Resumen de lo Realizado

### Funcionalidades Desarrolladas
- [x] Feature 1: Descripción breve
- [x] Feature 2: Descripción breve
- [ ] Feature 3: En progreso (80%)

### Archivos Modificados
- `src/services/WhatsAppService.ts` (+150, -30)
- `src/models/Message.ts` (+50, -10)
- `tests/services/whatsapp.test.ts` (+200, -0)

---

## 2. Estado del Sistema

### Indicadores
- ✅ Todos los tests pasando (45/45)
- ✅ Build exitoso sin warnings
- ⚠️ 2 warnings de deprecation (no críticos)

### Flujos Probados
- ✅ Envío de mensajes de texto
- ✅ Recepción de mensajes
- ⏳ Integración con IA (pendiente)

### Riesgos Detectados
- ⚠️ Performance issue potencial en `processLargeQueue()` con >1000 mensajes
- 💡 Sugerencia: Implementar paginación

---

## 3. Próximos Pasos

### Qué Falta
- [ ] Integrar con servicio de IA
- [ ] Agregar tests de carga
- [ ] Documentar API endpoints nuevos

### Qué se Sugiere Mejorar
- Refactorizar `MessageParser` (monolito de 800 líneas)
- Implementar caching para queries frecuentes

---

## 4. Para Revisión

### Archivos Principales
1. `src/services/WhatsAppService.ts` - Lógica core
2. `tests/services/whatsapp.test.ts` - Tests nuevos

### Decisiones Técnicas
- Usé SQLite en vez de MongoDB para la cola por simplicidad
- Implementé patrón Observer para notificaciones
```

---

## Referencias

| Documento | Propósito | Cuándo Consultar |
|-----------|-----------|------------------|
| [REGLAS_DE_LA_CASA.md](./REGLAS_DE_LA_CASA.md) | Gobernanza y filosofía | Para entender el POR QUÉ |
| [REGLAS_DESARROLLO.md](REGLAS_DESARROLLO.md) | Estándares técnicos | Para consultar el QUÉ |
| Este documento | Ejemplos prácticos | Para ver el CÓMO |

---

## Historial de Versiones

### v3.0 (2025-12-26)
- Clarificado propósito como guía práctica con ejemplos
- Eliminada duplicación de estándares (ahora en REGLAS_DESARROLLO)
- Añadidas referencias cruzadas a otros documentos
- Simplificado contenido redundante
- Mantenidos ejemplos extensos de código
- Reducido de ~1780 líneas a ~600 líneas

### v2.0 (2025-12-21) - Operación "Cimientos de Cristal"
- Nueva sección Diccionario Oficial de Tipos
- Actualizada estructura de proyecto

### v1.0 (2025-12-10)
- Versión inicial

---

**Mantenedor:** Equipo de Desarrollo - Paradise System Labs
