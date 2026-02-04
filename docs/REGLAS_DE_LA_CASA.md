# Reglas de la Casa v2.0

**Documento de gobernanza para WhatsApp Enterprise Integration - Paradise System Labs**

> **Audiencia principal:** SamuelERS (propietario), IAs asistentes, nuevos colaboradores
> **Tipo:** Documento constitucional - Define QUÉ se hace y POR QUÉ
> **Última actualización:** 2025-12-26

---

## Qué es este documento

Este es el documento **fundacional** del proyecto. Define las reglas que **NUNCA se rompen**, la filosofía de trabajo y cómo comunicarse con SamuelERS.

**NO es un manual técnico.** Para estándares de código, ver:
- [REGLAS_DESARROLLO.md](./REGLAS_DESARROLLO.md) - Estándares técnicos
- [REGLAS_PROGRAMADOR.md](./REGLAS_PROGRAMADOR.md) - Guía práctica con ejemplos

---

## Leyes Inquebrantables

### 1. Inmutabilidad del Código Base
- **NO** modificar ni eliminar código sin justificación explícita
- **NO** eliminar funcionalidades existentes sin evaluación de impacto
- **SIEMPRE** crear backup en `/Backups-RESPALDOS/` antes de cambios estructurales

### 2. Principio de No Regresión
- Lo que funciona **NO** se toca sin necesidad
- Toda modificación requiere verificar que no rompe funcionalidad existente
- Si algo se rompe, se revierte primero, se investiga después

### 3. TypeScript Estricto
- Todo código nuevo **DEBE** ser TypeScript
- **CERO `any`** en código nuevo (usar tipos del Diccionario Oficial)
- Los 6 módulos principales ya están migrados a TypeScript

### 4. Test Coverage Obligatorio
- Toda función crítica nueva **DEBE** tener tests
- Mínimos de coverage definidos en [REGLAS_DESARROLLO.md](../REGLAS_DESARROLLO.md)
- **NUNCA** entregar código sin verificar que tests pasan

### 5. Versionado Bloqueado
- **NUNCA** ejecutar `npm update`, `npm upgrade`, o `npm audit fix --force`
- Versiones bloqueadas: Memory API (v4.0), WPPConnect
- Cualquier actualización requiere autorización explícita de SamuelERS

### 6. Backups Obligatorios
- **SIEMPRE** backup antes de cambios estructurales
- Ubicación: `/Backups-RESPALDOS/[YYYYMMDD]_[descripcion]/`

---

## Metodología de Trabajo

### Mantra Central
```
ANALIZO → PLANIFICO → EJECUTO → DOCUMENTO → VALIDO
```

### Protocolo de Sesión IA

**Al INICIAR cada sesión:**
1. Leer este documento (REGLAS_DE_LA_CASA.md)
2. Leer `/docs/CLAUDE.md` - Estado actual del proyecto
3. Verificar `pm2 status` - Todos los servicios deben estar running
4. Confirmar task list clara antes de ejecutar

**Al FINALIZAR cada sesión:**
1. Ejecutar tests del módulo modificado
2. Verificar build exitoso
3. Actualizar `/docs/CLAUDE.md` con trabajo realizado
4. Entregar limpio: cero deuda técnica nueva sin documentar

### Checklist de Calidad Pre-Entrega

Antes de considerar cualquier trabajo como "completo":

- [ ] Task list creada y aprobada antes de iniciar
- [ ] Tests escritos para funcionalidad nueva
- [ ] Build exitoso (`npm run build`) sin errores
- [ ] TypeScript limpio (`npx tsc --noEmit`) sin errores
- [ ] Documentación actualizada (`/docs/CLAUDE.md`)
- [ ] PM2 verificado (si aplica)
- [ ] Funcionalidad crítica preservada al 100%

### Regla de Oro ante Dudas
```
PAUSA · PREGUNTA · VALIDA
```
Es preferible una pausa para clarificar que una acción que rompa el sistema.

---

## Comunicación con SamuelERS

**IMPORTANTE:** SamuelERS NO es programador. Toda comunicación debe ser:

- En español claro y simple
- Sin jerga técnica innecesaria
- Enfocada en resultados y beneficios
- Pidiendo confirmación antes de cambios importantes

### Ejemplo de comunicación

**BUENO:**
> "He mejorado el sistema de memoria para que recuerde mejor las conversaciones de los clientes. Ahora cuando un cliente vuelve a escribir, el sistema sabrá su historial completo."

**MALO:**
> "Implementé un circuit breaker pattern en el Memory API con rate limiting de 100 req/min y cache TTL de 300s."

---

## Sección: Explicación Anti-Bobos by SamuelERS

**Propósito:** Traducir cambios complejos a lenguaje ultra-simple para el solicitante (SamuelERS), sin bajar el estándar técnico del proyecto.

**Reglas:**
- Máximo 15 líneas por explicación.
- Cero jerga técnica innecesaria.
- Usar analogías simples solo si aportan claridad.

**Estructura Obligatoria:**
1. **Qué es:** [Explicación en 1-2 líneas del concepto general.]
2. **Qué falta:** [El problema o la necesidad en lenguaje simple.]
3. **Qué se va a hacer:** [Los pasos a seguir de forma breve.]
4. **Beneficio:** [Por qué vale la pena hacerlo, el resultado final positivo.]

**Resumen Rápido (Siempre al final):**
- [bullet point 1]
- [bullet point 2]
- [bullet point 3]

---

## Protocolos Estándar

### Estructura de Archivos
- Scripts → `/scripts/`
- Documentación → `/docs/`
- Backups → `/Backups-RESPALDOS/`
- Código compartido → `/shared/`

### Task Lists Obligatorias
**ANTES** de ejecutar cualquier trabajo, crear task list con:
- Objetivos específicos y medibles
- Pasos granulares y secuenciales
- Criterios de aceptación claros
- Dependencias identificadas

**Sin task list aprobada = no hay ejecución permitida.**

### Disciplina de Foco
- Seguir estrictamente la task list sin desviaciones
- Si surge un tema tangencial, anotarlo en "Notas para Después"
- Continuar con el plan actual

### PM2 Process Management
- Todos los servicios **DEBEN** estar en `ecosystem.config.js`
- **NUNCA** modificar servicios en producción sin probar localmente

---

## Glosario del Proyecto

### Términos de Negocio
| Término | Significado |
|---------|-------------|
| **Acuarios Paradise** | Cliente final, negocio de venta de productos para acuarios en El Salvador |
| **Cliente WhatsApp** | Usuario final que contacta vía WhatsApp |
| **Agente** | Persona humana que responde mensajes manualmente |
| **Memoria del Cliente** | Historial de conversaciones almacenado en Memory API |
| **Cola Manual** | Sistema de mensajes que requieren respuesta humana |
| **Session** | Sesión de WhatsApp Web autenticada con código QR |

### Servicios del Sistema
| Servicio | Puerto | Función |
|----------|--------|---------|
| **WPPConnect Server** | 3000 | Cliente WhatsApp Web |
| **Memory API** | 3001 | Persistencia de conversaciones |
| **Bridge API** | 8080 | Gateway central con JWT |
| **Dashboard Lovable** | 5173 | Frontend React |
| **Dashboard Monitor** | 8081/8082 | Monitoreo y WebSocket |

### Patrones Arquitectónicos
| Patrón | Descripción |
|--------|-------------|
| **Microservicios** | Cada componente es independiente |
| **API Gateway** | Bridge API centraliza acceso |
| **JWT Authentication** | Tokens de 15 minutos + refresh |
| **WebSocket Real-time** | Puerto 8082 para actualizaciones |

---

## Visión a Futuro (Roadmap)

| Prioridad | Feature | Estado |
|-----------|---------|--------|
| Alta | Docker containerización completa | PENDIENTE |
| Media | Prometheus + Grafana para métricas | FUTURO |
| Media | Redis para cache distribuido | ROADMAP |
| Baja | E2E Testing con Playwright | PENDIENTE |
| Baja | App móvil nativa | FUTURO |

---

## Protocolo de Debugging

### Ante cualquier error:

1. **NO ASUMIR - VERIFICAR**
   - Reproducir el error con pasos exactos
   - Capturar logs: `pm2 logs [servicio] --lines 100`
   - Verificar health checks: `curl http://localhost:[puerto]/health`

2. **ANÁLISIS SISTEMÁTICO**
   - ¿Error de tipos? → Revisar interfaces TypeScript
   - ¿Error de runtime? → Revisar logs con contexto
   - ¿Error de build? → Revisar tsconfig.json
   - ¿Error de servicios? → Verificar puertos y API keys

3. **SOLUCIÓN DOCUMENTADA**
   - Aplicar fix quirúrgico (mínimamente invasivo)
   - Documentar root cause en `/docs/CLAUDE.md`
   - Agregar test que previene regresión

### Formato de Reporte de Bugs
```
NUNCA: "No funciona" o "Da error"
SIEMPRE: "Error [tipo] en [archivo:línea] cuando [condición]. Logs: [paste]"
```

---

## Referencias

| Documento | Propósito |
|-----------|-----------|
| [REGLAS_DESARROLLO.md](./REGLAS_DESARROLLO.md) | Estándares técnicos de código |
| [REGLAS_PROGRAMADOR.md](./REGLAS_PROGRAMADOR.md) | Guía práctica con ejemplos |
| [CLAUDE.md](./CLAUDE.md) | Estado actual del proyecto |
| [README.md](../README.md) | Documentación general |

---

## Docker Híbrido (Desarrollo)

### Filosofía
> Desarrolla el código fuera de Docker. Ejecuta solo servicios externos dentro de Docker.

### Servicios en Modo Híbrido
| Servicio | Modo |
|----------|------|
| Redis | Docker |
| WPPConnect, Memory API, Bridge API | PM2 Local |
| Dashboard Lovable | Vite Local |

### Comandos Esenciales
```bash
# Iniciar sistema
pm2 start ecosystem.config.js

# Ver estado
pm2 status
pm2 logs

# Reiniciar servicio
pm2 restart [nombre]

# Build completo
npm run build:all
```

---

## Historial de Versiones

### v2.0 (2025-12-26)
- Clarificado propósito como documento constitucional
- Eliminada duplicación de estándares técnicos (movidos a REGLAS_DESARROLLO)
- Añadidas referencias cruzadas a otros documentos
- Simplificado glosario
- Unificada sección de Docker

### v1.0 (Octubre 2025)
- Creación inicial para WhatsApp Enterprise Integration

---

*"Sistema enterprise con valores cristianos para el éxito de Acuarios Paradise"*

**Gloria a Dios por la excelencia en el desarrollo.**
