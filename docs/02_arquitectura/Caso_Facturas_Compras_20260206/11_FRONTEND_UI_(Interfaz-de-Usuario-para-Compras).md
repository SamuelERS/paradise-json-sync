# 🖥️ Frontend UI — Interfaz de Usuario para Compras

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

> **¿Qué es esto?** Este documento describe el diseño de la interfaz de usuario para el módulo de facturas de compra. El objetivo: que sea intuitivo, profesional y fácil de usar.

### Roles Requeridos para este Documento

| Rol | Misión aquí |
|-----|-------------|
| 👨‍💻 **Desarrollador de Elite (Frontend)** | Implementar componentes React, toggle, configurador de columnas |
| 👨‍💻 **Desarrollador de Elite (Backend)** | Proveer endpoints que el frontend consume |
| ✅ **Inspector de Elite** | Verificar usabilidad, accesibilidad y manejo de errores |

### Tareas de Implementación (FASE 8)

| Tarea | Agente | Archivo Destino |
|-------|--------|-----------------|
| Crear `ModeToggle` | 👨‍💻 Desarrollador Frontend | `frontend/src/components/ModeToggle.jsx` |
| Crear `PurchaseUpload` | 👨‍💻 Desarrollador Frontend | `frontend/src/components/PurchaseUpload.jsx` |
| Crear `ColumnConfigurator` | 👨‍💻 Desarrollador Frontend | `frontend/src/components/ColumnConfigurator.jsx` |
| Crear `ProcessingProgress` | 👨‍💻 Desarrollador Frontend | `frontend/src/components/ProcessingProgress.jsx` |
| Crear `PurchaseWorkflow` | 👨‍💻 Desarrollador Frontend | `frontend/src/components/PurchaseWorkflow.jsx` |
| Modificar `Home.jsx` (toggle) | 👨‍💻 Desarrollador Frontend | `frontend/src/pages/Home.jsx` |
| Tests de componentes (>=70%) | 👨‍💻 Desarrollador Frontend | `frontend/tests/components/` |
| Tests E2E (Playwright) | 👨‍💻 Desarrollador Frontend | `e2e/tests/purchases-*.spec.ts` |
| Revisión de UI/UX | ✅ Inspector de Elite | Verificar flujo, errores, responsividad |

### Manejo de Errores en UI

> Todo componente debe manejar estos estados de error:
> - **Error de upload:** Archivo rechazado (tipo/tamaño) → mensaje claro, opción de reintentar
> - **Error de procesamiento:** Job falla → mostrar archivos con error y razón
> - **Error de red:** Timeout/desconexión → mensaje con botón de reintento
> - **Error de descarga:** Archivo no disponible → mensaje con opción de reprocesar

---

## 1. Decisión: Toggle Ventas ↔ Compras

**Opción elegida: Toggle/Tab en la navegación principal.**

Razón: es la solución más profesional y fácil de usar. El usuario ve claramente en qué modo está y puede cambiar con un click.

```
┌─────────────────────────────────────────────────────────┐
│  Paradise JSON Sync                                      │
│                                                          │
│  ┌──────────────┐ ┌──────────────┐                      │
│  │   📤 Ventas   │ │  📥 Compras  │   ← Tab activo      │
│  │  (Activo)    │ │              │      cambia color     │
│  └──────────────┘ └──────────────┘                      │
│                                                          │
│  [Contenido cambia según tab seleccionado]               │
└─────────────────────────────────────────────────────────┘
```

**Ventajas:**
- Separación visual clara entre ventas y compras
- No se mezclan funcionalidades
- El usuario sabe exactamente dónde está
- Flujo existente de ventas NO se modifica en absoluto

---

## 2. Componentes Nuevos

### 2.1 ModeToggle — Selector de Modo

```jsx
// frontend/src/components/ModeToggle.jsx

function ModeToggle({ activeMode, onModeChange }) {
  return (
    <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
      <button
        className={activeMode === "ventas" ? "tab-active" : "tab-inactive"}
        onClick={() => onModeChange("ventas")}
      >
        📤 Ventas (Facturas Emitidas)
      </button>
      <button
        className={activeMode === "compras" ? "tab-active" : "tab-inactive"}
        onClick={() => onModeChange("compras")}
      >
        📥 Compras (Facturas Recibidas)
      </button>
    </div>
  );
}
```

---

### 2.2 PurchaseUpload — Upload para Compras

Reutiliza `DropzoneUpload` pero apunta a `/api/purchases/upload`.

```jsx
// frontend/src/components/PurchaseUpload.jsx

function PurchaseUpload() {
  // Misma lógica que DropzoneUpload pero con:
  // - Endpoint: /api/purchases/upload
  // - Mensaje: "Arrastra facturas de COMPRA aquí (JSON o PDF)"
  // - Tipos aceptados: .json, .pdf
  // - Después del upload: muestra configuración de columnas
}
```

**Flujo del usuario:**

```
1. Selecciona tab "Compras"
2. Arrastra archivos JSON/PDF al dropzone
3. Ve lista de archivos subidos con conteo (48 JSON + 2 PDF)
4. Configura columnas (paso opcional)
5. Selecciona formato de salida
6. Click "Procesar"
7. Ve barra de progreso con detalles
8. Descarga resultado
```

---

### 2.3 ColumnConfigurator — Configurador de Columnas

Este es el componente clave que permite activar/desactivar columnas.

```
┌──────────────────────────────────────────────────────────┐
│  Configuración de Columnas                                │
│                                                           │
│  Perfil: [Básico ▼] [Completo] [Contador] [Personalizar] │
│                                                           │
│  ── Identificación ──                                     │
│  ✅ N° Control           ✅ Tipo Documento                 │
│  ✅ Fecha Emisión         ☐ Hora Emisión                   │
│  ☐ Código Generación     ☐ Moneda                         │
│                                                           │
│  ── Proveedor ──                                          │
│  ✅ Nombre Proveedor      ✅ NIT Proveedor                 │
│  ☐ Nombre Comercial      ☐ NRC Proveedor                  │
│  ☐ Dirección             ☐ Teléfono                       │
│                                                           │
│  ── Montos ──                                             │
│  ✅ Gravado               ✅ Exento                         │
│  ☐ No Sujeto             ☐ Descuento                      │
│  ✅ Subtotal              ✅ IVA                             │
│  ✅ Total                 ☐ Total en Letras                 │
│                                                           │
│  ── Adicional ──                                          │
│  ✅ Condición Pago        ☐ Sello Fiscal                   │
│  ✅ Archivo Fuente        ☐ Formato Detectado              │
│                                                           │
│  [Seleccionar Todo] [Deseleccionar Todo]                  │
└──────────────────────────────────────────────────────────┘
```

```jsx
// frontend/src/components/ColumnConfigurator.jsx

function ColumnConfigurator({ columns, selectedColumns, onColumnsChange, profiles }) {
  const [activeProfile, setActiveProfile] = useState("completo");

  // Agrupar columnas por categoría
  const grouped = groupBy(columns, "category");

  return (
    <div>
      {/* Selector de perfil */}
      <div className="flex gap-2 mb-4">
        {Object.entries(profiles).map(([id, profile]) => (
          <button
            key={id}
            onClick={() => {
              setActiveProfile(id);
              onColumnsChange(profile.columns);
            }}
            className={activeProfile === id ? "btn-active" : "btn-outline"}
          >
            {profile.name}
          </button>
        ))}
      </div>

      {/* Checkboxes por categoría */}
      {Object.entries(grouped).map(([category, cols]) => (
        <div key={category}>
          <h4>{CATEGORY_LABELS[category]}</h4>
          <div className="grid grid-cols-2 gap-2">
            {cols.map(col => (
              <label key={col.id} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selectedColumns.includes(col.id)}
                  onChange={() => toggleColumn(col.id)}
                />
                {col.label}
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

### 2.4 ProcessingProgress — Progreso del Procesamiento

Muestra el progreso detallado mientras se procesan las facturas.

```
┌──────────────────────────────────────────────────────────┐
│  Procesando Facturas de Compra...                         │
│                                                           │
│  ████████████████░░░░░░░░░  65%  (33/50 archivos)        │
│                                                           │
│  Paso actual: Validando factura_abc_033.json              │
│                                                           │
│  Formatos detectados:                                     │
│    DTE Estándar:  28 archivos                             │
│    DTE Variante:   4 archivos                             │
│    Desconocido:    1 archivo                              │
│                                                           │
│  Estado:                                                  │
│    ✅ Válidas:    30                                       │
│    ⚠️ Warnings:   2                                       │
│    ❌ Errores:     1                                       │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Flujo Completo del Usuario

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐
│ Modo    │ →  │ Upload   │ →  │ Configurar│ →  │ Procesar │ →  │ Descargar│
│ Compras │    │ Archivos │    │ Columnas  │    │ (async)  │    │ Resultado│
└─────────┘    └──────────┘    └───────────┘    └──────────┘    └──────────┘
```

**Paso 1:** Usuario hace click en tab "Compras"
**Paso 2:** Arrastra archivos JSON/PDF → `POST /api/purchases/upload`
**Paso 3:** Ve lista de archivos y configura columnas + formato de salida
**Paso 4:** Click "Procesar" → `POST /api/purchases/process` (202 Accepted)
**Paso 5:** Frontend hace polling a `GET /api/purchases/status/{job_id}` cada 2 segundos
**Paso 6:** Cuando status = "completed" → botón de descarga aparece
**Paso 7:** Click "Descargar" → `GET /api/purchases/download/{job_id}`

---

## 4. Integración con Home.jsx Existente

```jsx
// frontend/src/pages/Home.jsx (modificación mínima)

function Home() {
  const [mode, setMode] = useState("ventas");

  return (
    <div>
      <ModeToggle activeMode={mode} onModeChange={setMode} />

      {mode === "ventas" && (
        // Componente existente — NO SE TOCA
        <DropzoneUpload />
      )}

      {mode === "compras" && (
        // Componente nuevo
        <PurchaseWorkflow />
      )}
    </div>
  );
}
```

**Cambio mínimo en Home.jsx:** Solo agregar el toggle y renderizado condicional. Todo el contenido de ventas queda intacto.

---

## 5. PurchaseWorkflow — Componente Orquestador

```jsx
// frontend/src/components/PurchaseWorkflow.jsx

function PurchaseWorkflow() {
  const [step, setStep] = useState("upload");  // upload → configure → processing → done
  const [uploadId, setUploadId] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [columns, setColumns] = useState(PROFILE_COMPLETO);
  const [format, setFormat] = useState("xlsx");

  switch (step) {
    case "upload":
      return <PurchaseUpload onUploaded={(id) => { setUploadId(id); setStep("configure"); }} />;

    case "configure":
      return (
        <div>
          <ColumnConfigurator columns={ALL_COLUMNS} selectedColumns={columns} onColumnsChange={setColumns} />
          <FormatSelector value={format} onChange={setFormat} />
          <button onClick={handleProcess}>Procesar Facturas</button>
        </div>
      );

    case "processing":
      return <ProcessingProgress jobId={jobId} onComplete={() => setStep("done")} />;

    case "done":
      return <DownloadResult jobId={jobId} onReset={() => setStep("upload")} />;
  }
}
```

---

## 6. Diseño Visual

### Paleta de Colores

| Elemento | Color | Uso |
|----------|-------|-----|
| Tab Ventas (activo) | `#4472C4` (azul actual) | Consistente con diseño existente |
| Tab Compras (activo) | `#2E7D32` (verde) | Diferenciación visual |
| Header columnas | `#4472C4` (azul) | Consistente con Excel export |
| Fondo | `#F5F5F5` (gris claro) | Consistente con diseño actual |
| Warnings | `#FFA000` (amber) | Advertencias visibles |
| Errores | `#D32F2F` (rojo) | Errores prominentes |

---

## 7. Responsividad

- Desktop: Layout completo con configurador de columnas lateral
- Tablet: Configurador de columnas debajo del dropzone
- Mobile: Columnas en acordeón expandible, perfiles como selector dropdown

---

## 8. Testing Frontend

```
frontend/tests/components/
├── ModeToggle.test.jsx               → Toggle cambia de modo
├── PurchaseUpload.test.jsx            → Upload de archivos funciona
├── ColumnConfigurator.test.jsx        → Checkboxes funcionan
│   ├── Seleccionar perfil carga columnas
│   ├── Toggle individual funciona
│   ├── Seleccionar todo / Deseleccionar todo
│   └── Custom profile se activa al cambiar manualmente
├── ProcessingProgress.test.jsx        → Progreso se muestra correctamente
├── PurchaseWorkflow.test.jsx          → Flujo completo paso a paso
└── DownloadResult.test.jsx            → Botón descarga funciona

e2e/tests/
├── purchases-upload.spec.ts           → E2E: upload de facturas de compra
├── purchases-columns.spec.ts          → E2E: configuración de columnas
├── purchases-process.spec.ts          → E2E: procesamiento completo
└── purchases-full-flow.spec.ts        → E2E: flujo completo upload → download
```

**Cobertura esperada:** >= 70% en componentes, E2E cubre flujo crítico.

---

> **Próximo documento:** [12_TESTING_Y_CICD](./12_TESTING_Y_CICD_(Pruebas-y-Despliegue-Continuo).md) — Estrategia de pruebas y CI/CD.
