# Reglas de Desarrollo v3.0

**Estándares técnicos para WhatsApp Enterprise Integration - Paradise System Labs**

> **Audiencia:** Todos los desarrolladores (humanos e IAs)
> **Tipo:** Referencia técnica - Define CÓMO se escribe código
> **Última actualización:** 2025-12-26

---

## Qué es este documento

Este documento define los **estándares técnicos de código** que todos los desarrolladores deben seguir. Es la referencia autoritativa para:

- Convenciones de código
- Reglas de TypeScript
- Métricas de calidad
- Flujo de trabajo Git

**Documentos relacionados:**
- [REGLAS_DE_LA_CASA.md](./REGLAS_DE_LA_CASA.md) - Gobernanza y filosofía (para entender el POR QUÉ)
- [REGLAS_PROGRAMADOR.md](REGLAS_PROGRAMADOR.md) - Ejemplos prácticos y tutoriales (para ver el CÓMO en detalle)

---

## Stack Tecnológico Oficial

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Node.js** | >= 20.x | Runtime |
| **TypeScript** | 5.x | Lenguaje |
| **Express** | 4.x | Framework web |
| **SQLite** | 3.x | Base de datos (better-sqlite3) |
| **WPPConnect** | 1.37.x | Cliente WhatsApp |
| **React** | 18.x | Frontend |
| **Vite** | 5.x | Build tool frontend |
| **Jest** | 29.x | Testing |
| **PM2** | Latest | Process manager |

---

## Regla de Oro: CERO `any`

```typescript
// ❌ PROHIBIDO
const data: any = response;
function process(input: any): any { }
catch (error: any) { }

// ✅ OBLIGATORIO - Usar tipos del Diccionario Oficial
import { ApiResponse, FrontendChat } from '@paradise/shared/types';

async function fetchChats(): Promise<ApiResponse<FrontendChat[]>> {
  // Implementación tipada
}

// ✅ Para errores usar 'unknown'
catch (error: unknown) {
  const message = error instanceof Error ? error.message : 'Unknown error';
}
```

---

## Diccionario Oficial de Tipos

Todos los tipos compartidos **DEBEN** importarse de `shared/types/`:

| Archivo | Tipos Disponibles | Uso |
|---------|-------------------|-----|
| `api.types.ts` | `ApiResponse<T>`, `FrontendChat`, `MemoryMessage`, `ServiceStatus` | Respuestas HTTP |
| `auth.types.ts` | `JWTPayload`, `UserRole`, `Permission`, `TokenPair` | Autenticación |
| `whatsapp.types.ts` | `WhatsAppChat`, `WhatsAppMessage`, `FormattedMessage` | WhatsApp |
| `queue.types.ts` | `QueueMessage`, `DLQEntry`, `QueueStats` | Sistema de colas |

```typescript
// ✅ Importar del diccionario
import {
  ApiResponse,
  FrontendChat,
  isSuccessResponse  // Type Guard incluido
} from '@paradise/shared/types';

// ✅ Extender tipos existentes
interface EnrichedChat extends FrontendChat {
  aiSuggestions: string[];
}

// ❌ NO redefinir tipos que ya existen
interface MyApiResponse {  // PROHIBIDO
  success: boolean;
  data: any;
}
```

---

## Estructura del Proyecto

```
whatsapp-server-integration/
├── shared/                        ← MÓDULO COMPARTIDO
│   ├── types/                     ← Diccionario Oficial de Tipos
│   ├── interceptors/              ← Interceptores HTTP
│   ├── auth/                      ← Utilidades de autenticación
│   └── middleware/                ← Middlewares compartidos
│
├── bridge-api/                    ← API Gateway (Puerto 8080)
│   └── src/
│       ├── controllers/           ← Controladores HTTP
│       ├── services/              ← Lógica de negocio
│       ├── routes/                ← Endpoints API
│       └── middleware/            ← Middlewares Express
│
├── memory-api/                    ← Memory Service (Puerto 3001)
├── wppconnect-server/             ← WhatsApp Server (Puerto 3000)
├── dashboard_lovable/             ← Frontend React (Puerto 5173)
├── dashboard_monitor/             ← Monitoring (Puertos 8081/8082)
│
├── config/                        ← Configuraciones
│   ├── docker/                    ← Docker Compose files
│   └── pm2/                       ← PM2 ecosystem configs
│
├── scripts/                       ← Scripts organizados
│   ├── operations/                ← Scripts de operación
│   ├── diagnostics/               ← Scripts de diagnóstico
│   └── docker/                    ← Scripts de Docker
│
├── docs/                          ← Documentación
├── data/                          ← Bases de datos SQLite
└── logs/                          ← Logs del sistema
```

### Reglas de Estructura

1. **NUNCA** crear archivos sueltos en la raíz del proyecto
2. **SIEMPRE** usar `shared/` para código compartido
3. **MÁXIMO** 500 líneas por archivo (300 recomendado)
4. Scripts de operación van en `scripts/operations/`

#### Excepciones Documentadas (Raíz del Proyecto)

Los siguientes archivos son **excepciones permitidas** en la raíz por ser estándar de la industria:

| Archivo | Justificación |
|---------|---------------|
| `.env.*` | Variables de entorno (Node.js/dotenv estándar) |
| `.env.master` | Archivo principal de configuración |
| `.env.production.example` | Template para producción |
| `.env.master.example` | Template de desarrollo |
| `ecosystem.config.js` | Configuración PM2 (estándar) |
| `package.json` | Manifiesto npm (obligatorio) |
| `tsconfig.json` | Configuración TypeScript |
| `.gitignore` | Exclusiones Git |

---

## Convenciones de Código

### Nomenclatura

```typescript
// Variables: camelCase descriptivo
const userSessionToken = generateToken();
const activeConversations = await getActiveChats();

// Funciones: verbo + sustantivo, camelCase
async function fetchUserProfile(userId: string): Promise<UserProfile> { }
function validateEmailFormat(email: string): boolean { }

// Constantes: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_TIMEOUT_MS = 5000;

// Clases: PascalCase
class MessageQueueService { }

// Archivos: kebab-case
// whatsapp-service.ts, message-handler.ts
```

### Funciones

```typescript
// ✅ BIEN: Función corta, una responsabilidad
async function processIncomingMessage(message: WhatsAppMessage): Promise<void> {
  const validatedMessage = await validateMessage(message);
  const enrichedMessage = await enrichWithUserData(validatedMessage);
  await saveToDatabase(enrichedMessage);
  await notifyWebhooks(enrichedMessage);
}

// ❌ MAL: Función gigante que hace todo
async function processMessage(msg: any) {
  // 200 líneas mezclando validación, transformación, guardado...
}
```

**Límites:**
- MÁXIMO 50 líneas por función
- Si excede, dividir en funciones más pequeñas

### Async/Await

```typescript
// ✅ BIEN: Paralelo cuando es posible
async function loadDashboardData(userId: string): Promise<DashboardData> {
  const [user, chats, metrics] = await Promise.all([
    fetchUser(userId),
    fetchChats(userId),
    fetchMetrics(userId)
  ]);
  return { user, chats, metrics };
}

// ❌ MAL: Secuencial innecesario
async function loadData(userId: string) {
  const user = await fetchUser(userId);      // Espera
  const chats = await fetchChats(userId);    // Espera
  const metrics = await fetchMetrics(userId); // Espera
}

// ❌ MAL: Promesas no esperadas
async function sendMessages(messages: Message[]) {
  for (const msg of messages) {
    sendMessage(msg); // Falta await
  }
}
```

### Manejo de Errores

```typescript
// ✅ BIEN: Try-catch específico
async function fetchUserData(userId: string): Promise<User | null> {
  try {
    const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
    return user || null;
  } catch (error) {
    logger.error('Failed to fetch user', { userId, error });
    throw new DatabaseError('User fetch failed', { cause: error });
  }
}

// ❌ MAL: Silenciar errores
try {
  await criticalOperation();
} catch (e) {
  // Nada - ERROR: el error se pierde
}

// ❌ MAL: Exponer detalles internos
res.status(500).json({
  error: err.stack,        // Expone stack trace
  dbPassword: config.pass  // Expone credenciales
});
```

### Logs

```typescript
// ✅ BIEN: Logs estructurados con contexto
logger.info('WhatsApp session created', { clientId, sessionId });
logger.warn('Message retry attempt', { messageId, attempt: 2, maxAttempts: 3 });
logger.error('Database connection failed', { host: db.host, error: err.message });

// ❌ MAL: Logs inútiles
console.log('here');
console.log(data);
logger.info('Password:', password);  // NUNCA loguear credenciales
```

---

## Testing

### Métricas de Coverage

| Tipo de Código | Coverage Mínimo | Target Ideal |
|----------------|-----------------|--------------|
| **Lógica de negocio crítica** | 80% | 95% |
| **APIs/Endpoints** | 70% | 85% |
| **Servicios** | 60% | 80% |
| **Utilidades** | 50% | 70% |
| **Configuración** | 30% | 50% |

### Reglas de Testing

1. **Un test por caso de uso**
2. **Tests independientes** (no dependen de orden)
3. **Nombres descriptivos**
4. **Patrón Arrange-Act-Assert**
5. **Mock de dependencias externas**

```typescript
describe('MessageQueueService', () => {
  let service: MessageQueueService;
  let mockDb: jest.Mocked<Database>;

  beforeEach(() => {
    mockDb = createMockDatabase();
    service = new MessageQueueService(mockDb);
  });

  describe('enqueueMessage', () => {
    it('should add message to queue successfully', async () => {
      // Arrange
      const message = { id: '123', text: 'Hello', chatId: 'chat-1' };

      // Act
      const result = await service.enqueueMessage(message);

      // Assert
      expect(result.success).toBe(true);
      expect(mockDb.insert).toHaveBeenCalledWith('queue', message);
    });

    it('should throw error if message is invalid', async () => {
      const invalidMessage = { text: '' };

      await expect(service.enqueueMessage(invalidMessage))
        .rejects
        .toThrow('Invalid message');
    });
  });
});
```

---

## Seguridad

### Checklist Obligatorio

#### Variables de Entorno
```typescript
// ✅ BIEN: Usar .env
const API_KEY = process.env.OPENAI_API_KEY;

// ❌ MAL: Hardcodear
const API_KEY = 'sk-1234567890abcdef';
```

#### Validación de Entrada
```typescript
// ✅ BIEN: Validar TODO input de usuario
function createUser(req: Request, res: Response) {
  const { email, phone } = req.body;

  if (!email || !isValidEmail(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  // Procesar...
}

// ❌ MAL: Confiar en el input
function createUser(req: Request, res: Response) {
  const user = req.body;
  db.insert('users', user); // Peligroso
}
```

#### SQL Injection
```typescript
// ✅ BIEN: Queries parametrizadas
const user = await db.query('SELECT * FROM users WHERE email = ?', [email]);

// ❌ MAL: String concatenation
const user = await db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

---

## Flujo de Trabajo Git

### Branches
```
main              ← Producción (protegida)
├── develop       ← Desarrollo (protegida)
    ├── feature/add-user-auth
    ├── fix/message-queue-bug
    └── refactor/database-layer
```

### Commits

**Formato:**
```
<tipo>: <descripción corta>

<descripción detallada (opcional)>
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `refactor`: Refactorización
- `test`: Tests
- `docs`: Documentación
- `chore`: Mantenimiento

**Ejemplos:**
```bash
# ✅ BIEN
git commit -m "feat: add WhatsApp QR code generation endpoint"
git commit -m "fix: resolve race condition in message queue"

# ❌ MAL
git commit -m "fix"
git commit -m "update"
```

### Pull Request Template

```markdown
## Descripción
[Qué hace este PR]

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Refactorización

## Checklist
- [ ] Tests agregados/actualizados
- [ ] Todos los tests pasan
- [ ] Documentación actualizada
- [ ] Sin vulnerabilidades de seguridad
```

---

## Anti-Patrones

### God Objects
```typescript
// ❌ MAL: Clase que hace de todo
class Application {
  connectDatabase() { }
  sendEmail() { }
  processPayment() { }
  generateReport() { }
  // ... 50 métodos más
}

// ✅ BIEN: Separación de responsabilidades
class DatabaseService { }
class EmailService { }
class PaymentService { }
```

### Magic Numbers
```typescript
// ❌ MAL
if (status === 3) { }
setTimeout(() => { }, 86400000);

// ✅ BIEN
const STATUS_COMPLETED = 3;
const ONE_DAY_MS = 24 * 60 * 60 * 1000;

if (status === STATUS_COMPLETED) { }
setTimeout(() => { }, ONE_DAY_MS);
```

### Callback Hell
```typescript
// ❌ MAL
getData(function(a) {
  getMoreData(a, function(b) {
    getEvenMoreData(b, function(c) { });
  });
});

// ✅ BIEN
const a = await getData();
const b = await getMoreData(a);
const c = await getEvenMoreData(b);
```

---

## Checklist del Desarrollador

Antes de crear PR, verificar:

### Código
- [ ] Nombres descriptivos
- [ ] Funciones < 50 líneas
- [ ] Sin código duplicado
- [ ] Sin magic numbers
- [ ] Formateado con Prettier
- [ ] Pasa ESLint

### TypeScript
- [ ] Sin uso de `any`
- [ ] Tipos explícitos en funciones públicas
- [ ] Compila sin errores

### Seguridad
- [ ] Sin credenciales hardcodeadas
- [ ] Input validado
- [ ] Errores manejados correctamente
- [ ] npm audit sin críticos

### Testing
- [ ] Tests unitarios agregados
- [ ] Coverage cumple mínimos
- [ ] Todos los tests pasan

### Git
- [ ] Commits atómicos
- [ ] Mensajes descriptivos
- [ ] Branch actualizado con develop

---

## Dependencias

### Reglas

1. **NO agregar dependencias** sin justificación
2. **SIEMPRE** verificar licencia
3. **PREFERIR** dependencias activamente mantenidas
4. **DOCUMENTAR** por qué se agregó

```bash
# Verificar vulnerabilidades
npm audit

# Ver dependencias
npm ls
```

---

## Métricas de Calidad

| Métrica | Objetivo | Herramienta |
|---------|----------|-------------|
| Test Coverage | > 70% | Jest --coverage |
| Complejidad Ciclomática | < 10 | ESLint complexity |
| Líneas por función | < 50 | Review manual |
| Vulnerabilidades | 0 críticas | npm audit |
| Type coverage | 100% | TypeScript strict |

### Deuda Técnica Permitida

- ESLint warnings: Máximo 20 totales
- TypeScript `@ts-ignore`: Máximo 5 en todo el proyecto
- TODO comments: Máximo 30 en todo el proyecto

---

## Referencias

| Documento | Propósito |
|-----------|-----------|
| [REGLAS_DE_LA_CASA.md](./REGLAS_DE_LA_CASA.md) | Gobernanza y filosofía |
| [REGLAS_PROGRAMADOR.md](REGLAS_PROGRAMADOR.md) | Ejemplos prácticos detallados |
| [TypeScript Handbook](https://www.typescriptlang.org/docs/) | Documentación oficial |
| [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices) | Guía de referencia |

---

## Historial de Versiones

### v3.0 (2025-12-26)
- Unificado coverage de tests (80% lógica crítica como estándar único)
- Estandarizado Node.js >= 20.x
- Clarificado propósito como referencia técnica
- Añadidas referencias cruzadas a otros documentos
- Eliminada duplicación con REGLAS_PROGRAMADOR
- Simplificada estructura del documento

### v2.0 (2025-12-21) - Operación "Cimientos de Cristal"
- Arquitectura Pythonic v2.0
- Regla CERO `any`
- Diccionario Oficial de Tipos

### v1.0 (2025-12-10)
- Versión inicial

---

**Mantenedor:** Equipo de Desarrollo - Paradise System Labs
