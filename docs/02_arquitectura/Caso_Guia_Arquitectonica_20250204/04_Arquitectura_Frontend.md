# 04 - Arquitectura Frontend (Frontend Architecture)
# Frontend Architecture (Arquitectura Frontend - La cara del sistema)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Sí - Componentes deben tener tests unitarios
COBERTURA MÍNIMA: 70% general
CI/CD: Compatible - Build debe pasar antes de deploy
STACK: React 18+ / Vite 5+ / Tailwind CSS 3+
```

---

## Que es el Frontend (What is the Frontend)

**Explicación simple:**
El frontend es como la fachada de un restaurante:
- Es lo que ve el cliente
- Los botones, colores, textos
- Lo que hace que la experiencia sea agradable

En nuestro caso:
- La pantalla donde subes archivos
- Los botones para procesar
- Los mensajes de progreso
- El lugar donde descargas resultados

---

## Estructura de Carpetas (Folder Structure)

```
frontend/
├── 📄 index.html                 # Entry Point (Punto de Entrada - La puerta principal)
├── 📄 package.json               # Dependencies (Dependencias - Lista de librerías)
├── 📄 vite.config.js             # Vite Config (Configuración de Vite)
├── 📄 tailwind.config.js         # Tailwind Config (Configuración de estilos)
├── 📄 .env.example               # Environment Template (Plantilla de Variables)
│
├── 📂 public/                    # Static Assets (Archivos Estáticos)
│   ├── 📄 favicon.ico            # Icon (Ícono del navegador)
│   └── 📄 logo.svg               # Logo (Logotipo)
│
├── 📂 src/                       # Source Code (Código Fuente)
│   │
│   ├── 📄 main.jsx               # Main Entry (Entrada Principal - Donde arranca React)
│   ├── 📄 App.jsx                # App Component (Componente Principal)
│   ├── 📄 index.css              # Global Styles (Estilos Globales)
│   │
│   ├── 📂 components/            # UI Components (Componentes de Interfaz)
│   │   ├── 📂 common/            # Common Components (Componentes Comunes)
│   │   │   ├── 📄 Button.jsx     # Button (Botón - Para acciones)
│   │   │   ├── 📄 Card.jsx       # Card (Tarjeta - Para agrupar info)
│   │   │   ├── 📄 Modal.jsx      # Modal (Ventana Emergente)
│   │   │   └── 📄 Loading.jsx    # Loading (Indicador de Carga)
│   │   │
│   │   ├── 📂 upload/            # Upload Components (Componentes de Carga)
│   │   │   ├── 📄 Dropzone.jsx   # Dropzone (Zona de Arrastre)
│   │   │   ├── 📄 FileList.jsx   # File List (Lista de Archivos)
│   │   │   └── 📄 FileItem.jsx   # File Item (Item de Archivo)
│   │   │
│   │   ├── 📂 process/           # Process Components (Componentes de Proceso)
│   │   │   ├── 📄 ProgressBar.jsx    # Progress Bar (Barra de Progreso)
│   │   │   ├── 📄 ProcessStatus.jsx  # Process Status (Estado del Proceso)
│   │   │   └── 📄 ResultSummary.jsx  # Result Summary (Resumen de Resultados)
│   │   │
│   │   └── 📂 download/          # Download Components (Componentes de Descarga)
│   │       ├── 📄 DownloadCard.jsx   # Download Card (Tarjeta de Descarga)
│   │       └── 📄 DownloadButton.jsx # Download Button (Botón de Descarga)
│   │
│   ├── 📂 pages/                 # Page Components (Páginas)
│   │   ├── 📄 HomePage.jsx       # Home Page (Página Principal)
│   │   ├── 📄 ProcessPage.jsx    # Process Page (Página de Procesamiento)
│   │   └── 📄 ResultsPage.jsx    # Results Page (Página de Resultados)
│   │
│   ├── 📂 hooks/                 # Custom Hooks (Hooks Personalizados)
│   │   ├── 📄 useUpload.js       # Upload Hook (Hook de Carga)
│   │   ├── 📄 useProcess.js      # Process Hook (Hook de Proceso)
│   │   └── 📄 useDownload.js     # Download Hook (Hook de Descarga)
│   │
│   ├── 📂 services/              # API Services (Servicios de API)
│   │   ├── 📄 api.js             # API Client (Cliente de API)
│   │   ├── 📄 uploadService.js   # Upload Service (Servicio de Carga)
│   │   └── 📄 processService.js  # Process Service (Servicio de Proceso)
│   │
│   ├── 📂 utils/                 # Utilities (Utilidades)
│   │   ├── 📄 fileHelpers.js     # File Helpers (Ayudantes de Archivos)
│   │   └── 📄 formatters.js      # Formatters (Formateadores)
│   │
│   └── 📂 config/                # Configuration (Configuración)
│       └── 📄 constants.js       # Constants (Constantes)
│
└── 📂 tests/                     # Tests (Pruebas)
    ├── 📂 components/            # Component Tests
    │   ├── 📄 Button.test.jsx
    │   ├── 📄 Dropzone.test.jsx
    │   └── 📄 ProgressBar.test.jsx
    └── 📂 hooks/                 # Hook Tests
        └── 📄 useUpload.test.js
```

---

## Descripcion de Componentes (Component Description)

### 1. Common Components (Componentes Comunes - Piezas reutilizables)

#### `Button.jsx` (Botón - Para acciones)

**¿Qué es?**
Un botón es como un timbre: lo presionas y algo pasa.

```jsx
/**
 * Button Component (Componente Botón)
 * Un botón reutilizable con diferentes estilos.
 *
 * Piensa en esto como: Un timbre que puede ser azul, rojo o gris
 * dependiendo de para qué sirve.
 */
function Button({ children, variant = 'primary', onClick, disabled }) {
  // Variant (Variante - El estilo del botón)
  // - primary: Azul, para acciones principales
  // - secondary: Gris, para acciones secundarias
  // - danger: Rojo, para acciones peligrosas

  const baseClasses = "px-4 py-2 rounded font-medium";

  const variantClasses = {
    primary: "bg-blue-500 text-white hover:bg-blue-600",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300",
    danger: "bg-red-500 text-white hover:bg-red-600"
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
```

**Tests requeridos:**
- [ ] Test: Renderiza con texto correcto
- [ ] Test: Aplica clase según variante
- [ ] Test: Ejecuta onClick al hacer clic
- [ ] Test: Se deshabilita cuando `disabled=true`

---

#### `Dropzone.jsx` (Zona de Arrastre - Donde sueltas archivos)

**¿Qué es?**
Es como una bandeja donde puedes soltar archivos con el mouse.
Imagina una caja donde metes papeles.

```jsx
/**
 * Dropzone Component (Componente Zona de Arrastre)
 * Área donde el usuario puede arrastrar y soltar archivos.
 *
 * Piensa en esto como: Una bandeja de entrada donde
 * puedes tirar documentos y la bandeja los recoge.
 */
function Dropzone({ onFilesAccepted, acceptedTypes }) {
  // acceptedTypes (Tipos Aceptados - Qué archivos permitimos)
  // Ejemplo: ['.json', '.pdf']

  const handleDrop = (event) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    onFilesAccepted(files);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className="border-2 border-dashed border-gray-300 p-8 text-center"
    >
      <p>Arrastra archivos aquí o haz clic para seleccionar</p>
      <p className="text-sm text-gray-500">
        Archivos aceptados: {acceptedTypes.join(', ')}
      </p>
    </div>
  );
}
```

**Tests requeridos:**
- [ ] Test: Renderiza zona de drop
- [ ] Test: Acepta archivos al soltar
- [ ] Test: Muestra tipos aceptados
- [ ] Test: Cambia estilo al arrastrar sobre él

---

#### `ProgressBar.jsx` (Barra de Progreso - Muestra avance)

**¿Qué es?**
Es como el indicador de carga de un video:
Te muestra cuánto falta para terminar.

```jsx
/**
 * ProgressBar Component (Componente Barra de Progreso)
 * Muestra el porcentaje de avance de una operación.
 *
 * Piensa en esto como: La barra de carga cuando
 * descargas algo de internet.
 */
function ProgressBar({ progress, label }) {
  // progress (Progreso - Número de 0 a 100)
  // label (Etiqueta - Texto descriptivo)

  return (
    <div className="w-full">
      {label && <p className="text-sm mb-1">{label}</p>}

      {/* Barra exterior (el contenedor gris) */}
      <div className="w-full bg-gray-200 rounded-full h-4">

        {/* Barra interior (la parte azul que crece) */}
        <div
          className="bg-blue-500 h-4 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Porcentaje en texto */}
      <p className="text-sm text-right mt-1">{progress}%</p>
    </div>
  );
}
```

**Tests requeridos:**
- [ ] Test: Muestra 0% al inicio
- [ ] Test: Muestra 100% al completar
- [ ] Test: Ancho corresponde al porcentaje
- [ ] Test: Muestra etiqueta si se proporciona

---

### 2. Pages (Páginas - Las pantallas completas)

#### `HomePage.jsx` (Página Principal)

**Responsabilidad:** Primera pantalla que ve el usuario.

**Estructura:**
```jsx
/**
 * HomePage (Página Principal)
 * La primera pantalla de la aplicación.
 *
 * Piensa en esto como: La puerta de entrada a una tienda.
 * Te da la bienvenida y te dice qué puedes hacer.
 */
function HomePage() {
  return (
    <div className="container mx-auto p-8">
      {/* Título de bienvenida */}
      <h1 className="text-3xl font-bold mb-4">
        Paradise JSON Sync
      </h1>

      {/* Descripción */}
      <p className="mb-8">
        Sube tus archivos JSON y PDF para procesarlos.
      </p>

      {/* Zona de carga de archivos */}
      <Dropzone
        onFilesAccepted={handleFiles}
        acceptedTypes={['.json', '.pdf']}
      />

      {/* Lista de archivos seleccionados */}
      <FileList files={selectedFiles} />

      {/* Botón para procesar */}
      <Button
        onClick={handleProcess}
        disabled={selectedFiles.length === 0}
      >
        Procesar Archivos
      </Button>
    </div>
  );
}
```

**Tests requeridos:**
- [ ] Test: Renderiza título
- [ ] Test: Muestra Dropzone
- [ ] Test: Botón deshabilitado sin archivos
- [ ] Test: Botón habilitado con archivos

---

### 3. Hooks (Hooks Personalizados - Lógica reutilizable)

#### `useUpload.js` (Hook de Carga)

**¿Qué es un Hook?**
Un Hook es como una receta que puedes usar en cualquier componente.
Encapsula lógica que se repite.

```javascript
/**
 * useUpload Hook (Hook de Carga)
 * Maneja toda la lógica de subir archivos.
 *
 * Piensa en esto como: Una receta para subir archivos
 * que cualquier componente puede seguir.
 */
function useUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const addFiles = (newFiles) => {
    setFiles([...files, ...newFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    setUploading(true);
    setProgress(0);

    try {
      const result = await uploadService.upload(files, (p) => {
        setProgress(p);
      });
      return result;
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return {
    files,          // Lista de archivos seleccionados
    uploading,      // ¿Está subiendo ahora?
    progress,       // Progreso de 0 a 100
    error,          // Mensaje de error (si hay)
    addFiles,       // Función para agregar archivos
    removeFile,     // Función para quitar un archivo
    uploadFiles     // Función para iniciar la subida
  };
}
```

**Tests requeridos:**
- [ ] Test: `addFiles` agrega archivos a la lista
- [ ] Test: `removeFile` quita archivo por índice
- [ ] Test: `uploading` es true durante subida
- [ ] Test: `progress` se actualiza correctamente
- [ ] Test: `error` se setea cuando hay fallo

---

## Servicios de API (API Services)

### `api.js` (Cliente de API)

```javascript
/**
 * API Client (Cliente de API)
 * Configuración base para todas las llamadas al backend.
 *
 * Piensa en esto como: El teléfono que usamos para
 * llamar al restaurante (backend).
 */

// Base URL (URL Base - La dirección del backend)
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Fetch Wrapper (Envoltura de Fetch)
 * Hace llamadas HTTP con configuración estándar.
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: (endpoint) => apiRequest(endpoint),
  post: (endpoint, data) => apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
```

---

## Flujo de Usuario (User Flow)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DEL FRONTEND                           │
│               (El viaje del usuario)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. LLEGA                                                       │
│     Usuario abre la aplicación → Ve HomePage                    │
│                        │                                        │
│                        ▼                                        │
│  2. SELECCIONA ARCHIVOS                                         │
│     Arrastra archivos → Dropzone los recibe → FileList muestra  │
│                        │                                        │
│                        ▼                                        │
│  3. PROCESA                                                     │
│     Click en "Procesar" → Progreso se muestra → Espera          │
│                        │                                        │
│                        ▼                                        │
│  4. VE RESULTADOS                                               │
│     Proceso termina → ResultsPage muestra → Opciones de descarga│
│                        │                                        │
│                        ▼                                        │
│  5. DESCARGA                                                    │
│     Click en "Descargar Excel" o "Descargar PDF" → Listo        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Ejecutar el Frontend (Running the Frontend)

### Desarrollo (Development)

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Abre en: http://localhost:5173
```

### Producción (Production)

```bash
# Generar build
npm run build

# Los archivos quedan en: /dist
```

### Tests

```bash
# Correr todos los tests
npm test

# Correr con cobertura
npm test -- --coverage
```

---

## Proximo Documento (Next Document)

Continúa con: `05_API_Endpoints.md` para ver los comandos disponibles del backend.

---

**Versión:** 1.0
**Líneas:** ~380
**Cumple reglas:** Sí
