# 02 - Stack Tecnologico (Stack Tecnológico)
# Tech Stack (Stack Tecnológico - Las herramientas que usamos)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Sí - Cada librería debe tener tests de integración
CI/CD: Compatible - Versiones bloqueadas en requirements.txt y package.json
REGLA: No cambiar versiones sin autorización y sin actualizar este documento
```

---

## Que es un Stack Tecnologico (What is a Tech Stack)

**Explicación simple:**
Un "stack" es como la caja de herramientas de un carpintero. Cada herramienta tiene un propósito:
- El martillo para clavar
- El serrucho para cortar
- La cinta para medir

Nuestro "stack" son los programas y librerías que usamos para construir la aplicación.

---

## Resumen del Stack (Stack Summary)

| Capa | Tecnología | Versión | Propósito |
|------|------------|---------|-----------|
| Backend | Python | 3.11+ | El idioma principal |
| Backend | FastAPI | 0.109+ | El mesero que recibe pedidos |
| Backend | Pandas | 2.1+ | El organizador de datos |
| Backend | openpyxl | 3.1+ | El escritor de Excel |
| Backend | PyMuPDF | 1.23+ | El unificador de PDFs |
| Frontend | React | 18+ | El constructor de pantallas |
| Frontend | Vite | 5+ | El que hace todo rápido |
| Frontend | Tailwind | 3+ | El diseñador de estilos |
| Testing | pytest | 8+ | El verificador de código |
| Testing | Jest | 29+ | El verificador del frontend |

---

## Backend Stack (Stack del Backend - El cerebro)

### Python 3.11+ (Lenguaje Principal)

**¿Qué es?**
Python es el idioma en que le "hablamos" a la computadora. Es como español para máquinas.

**¿Por qué lo elegimos?**
- Fácil de leer (parece inglés)
- Muchas librerías para datos
- Comunidad enorme de ayuda

**Ejemplo simple:**
```python
# Esto suma dos números
resultado = 5 + 3
print(resultado)  # Muestra: 8
```

**Configuración requerida:**
- [ ] Instalar Python 3.11 o superior
- [ ] Crear virtual environment (entorno virtual)
- [ ] Instalar dependencias con `pip install -r requirements.txt`

**Tests de verificación:**
- [ ] Test: `python --version` muestra 3.11+
- [ ] Test: Importar todas las librerías sin error

---

### FastAPI 0.109+ (Framework Web - El mesero)

**¿Qué es?**
FastAPI es como un mesero en un restaurante:
- Recibe pedidos (requests HTTP)
- Los lleva a la cocina (tu código)
- Regresa con la respuesta

**¿Por qué lo elegimos?**
- Súper rápido (de los más rápidos que hay)
- Documentación automática
- Validación de datos incluida

**Ejemplo simple:**
```python
from fastapi import FastAPI

app = FastAPI()

# Cuando alguien visita /hello, responde "Hola Mundo"
@app.get("/hello")
def say_hello():
    return {"message": "Hola Mundo"}
```

**Configuración requerida:**
- [ ] `pip install fastapi[all]`
- [ ] Puerto por defecto: 8000
- [ ] Docs automáticos en: `/docs`

**Tests de verificación:**
- [ ] Test: Servidor inicia sin errores
- [ ] Test: Endpoint `/health` responde 200
- [ ] Test: Documentación accesible en `/docs`

---

### Pandas 2.1+ (Procesador de Datos - El organizador)

**¿Qué es?**
Pandas es como una super hoja de Excel dentro de Python. Puede:
- Leer archivos de datos
- Filtrar información
- Hacer cálculos
- Exportar resultados

**¿Por qué lo elegimos?**
- Estándar de la industria para datos
- Maneja millones de filas
- Fácil de usar

**Ejemplo simple:**
```python
import pandas as pd

# Crear una "tabla" con datos
datos = {
    "cliente": ["Juan", "María", "Pedro"],
    "total": [100, 200, 150]
}
tabla = pd.DataFrame(datos)

# Calcular el total de todos
suma_total = tabla["total"].sum()  # Resultado: 450
```

**Configuración requerida:**
- [ ] `pip install pandas`
- [ ] Memoria suficiente para datos grandes

**Tests de verificación:**
- [ ] Test: Crear DataFrame vacío
- [ ] Test: Leer CSV de ejemplo
- [ ] Test: Calcular suma correctamente

---

### openpyxl 3.1+ (Escritor de Excel - El que hace planillas)

**¿Qué es?**
openpyxl es el que sabe escribir archivos de Excel (.xlsx).
Python no sabe Excel de nacimiento, esta librería le enseña.

**¿Por qué lo elegimos?**
- Soporta formato moderno de Excel
- Puede dar formato a celdas
- Funciona con Pandas

**Ejemplo simple:**
```python
from openpyxl import Workbook

# Crear un archivo Excel nuevo
libro = Workbook()
hoja = libro.active

# Escribir en celda A1
hoja['A1'] = "Hola Excel!"

# Guardar archivo
libro.save("mi_archivo.xlsx")
```

**Configuración requerida:**
- [ ] `pip install openpyxl`
- [ ] Viene incluido cuando instalas pandas

**Tests de verificación:**
- [ ] Test: Crear archivo Excel vacío
- [ ] Test: Escribir datos en celdas
- [ ] Test: Aplicar formato a columnas
- [ ] Test: Archivo abre en Excel real

---

### PyMuPDF 1.23+ (Procesador de PDF - El unificador)

**¿Qué es?**
PyMuPDF (también llamado "fitz") es el experto en PDFs:
- Puede leer PDFs
- Puede unir PDFs
- Puede extraer texto e imágenes

**¿Por qué lo elegimos?**
- Muy rápido
- Mantiene calidad
- Funciona con PDFs complicados

**Ejemplo simple:**
```python
import fitz  # PyMuPDF se importa como "fitz"

# Abrir un PDF
documento = fitz.open("factura.pdf")

# Ver cuántas páginas tiene
paginas = len(documento)
print(f"El PDF tiene {paginas} páginas")

# Cerrar
documento.close()
```

**Configuración requerida:**
- [ ] `pip install pymupdf`
- [ ] Nota: Se importa como `fitz`, no como `pymupdf`

**Tests de verificación:**
- [ ] Test: Abrir PDF de ejemplo
- [ ] Test: Contar páginas correctamente
- [ ] Test: Unir dos PDFs
- [ ] Test: Manejar PDF corrupto sin crashear

---

## Frontend Stack (Stack del Frontend - La cara)

### React 18+ (Constructor de Interfaces - El arquitecto visual)

**¿Qué es?**
React es como un juego de LEGO para pantallas:
- Creas piezas pequeñas (componentes)
- Las combinas para hacer pantallas completas
- Si cambias una pieza, React actualiza solo lo necesario

**¿Por qué lo elegimos?**
- Usado por Facebook, Netflix, Airbnb
- Comunidad gigante
- Muchos componentes ya hechos

**Ejemplo simple:**
```jsx
// Un botón que cuenta clics
function Contador() {
  const [cuenta, setCuenta] = useState(0);

  return (
    <button onClick={() => setCuenta(cuenta + 1)}>
      Clics: {cuenta}
    </button>
  );
}
```

**Configuración requerida:**
- [ ] Node.js 18+ instalado
- [ ] `npm install` para dependencias

**Tests de verificación:**
- [ ] Test: Componente renderiza sin error
- [ ] Test: Eventos de clic funcionan
- [ ] Test: Estado se actualiza correctamente

---

### Vite 5+ (Bundler - El empaquetador rápido)

**¿Qué es?**
Vite es como un cocinero muy rápido:
- Toma todos los ingredientes (archivos JS, CSS)
- Los mezcla y cocina
- Sirve un plato listo (la aplicación)

**¿Por qué lo elegimos?**
- Increíblemente rápido
- Hot reload (ve cambios al instante)
- Configuración simple

**Configuración requerida:**
- [ ] Incluido al crear proyecto con React
- [ ] Puerto por defecto: 5173

**Tests de verificación:**
- [ ] Test: `npm run dev` inicia sin errores
- [ ] Test: `npm run build` genera carpeta dist
- [ ] Test: Build se puede servir estáticamente

---

### Tailwind CSS 3+ (Estilos - El diseñador)

**¿Qué es?**
Tailwind es como tener un diseñador que ya hizo todas las piezas:
- Colores predefinidos
- Tamaños estándar
- Responsivo incluido

**¿Por qué lo elegimos?**
- No escribes CSS manual
- Consistente en todo el proyecto
- Muy rápido para prototipar

**Ejemplo simple:**
```html
<!-- Un botón azul con texto blanco, redondeado -->
<button class="bg-blue-500 text-white rounded px-4 py-2">
  Click aquí
</button>
```

**Configuración requerida:**
- [ ] `npm install tailwindcss`
- [ ] Archivo `tailwind.config.js` configurado

**Tests de verificación:**
- [ ] Test: Clases de Tailwind se aplican
- [ ] Test: Build incluye solo CSS usado
- [ ] Test: Diseño responsive funciona

---

## Testing Stack (Stack de Pruebas)

### pytest 8+ (Testing Backend - El verificador de Python)

**¿Qué es?**
pytest es como un inspector de calidad:
- Ejecuta pruebas automáticas
- Te dice qué pasó y qué falló
- Genera reportes de cobertura

**Configuración requerida:**
- [ ] `pip install pytest pytest-cov`
- [ ] Archivos de test en carpeta `tests/`
- [ ] Nombres: `test_*.py`

**Cobertura mínima:** 70%

---

### Jest 29+ (Testing Frontend - El verificador de React)

**¿Qué es?**
Jest hace lo mismo que pytest pero para JavaScript/React.

**Configuración requerida:**
- [ ] `npm install --save-dev jest @testing-library/react`
- [ ] Archivos de test: `*.test.js` o `*.spec.js`

**Cobertura mínima:** 70%

---

## Checklist de Instalacion (Installation Checklist)

### Backend
- [ ] Python 3.11+ instalado
- [ ] Virtual environment creado (`python -m venv venv`)
- [ ] Virtual environment activado (`source venv/bin/activate`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Servidor inicia (`uvicorn main:app --reload`)

### Frontend
- [ ] Node.js 18+ instalado
- [ ] Dependencias instaladas (`npm install`)
- [ ] Servidor de desarrollo inicia (`npm run dev`)
- [ ] Build genera sin errores (`npm run build`)

---

## Versiones Bloqueadas (Locked Versions)

**IMPORTANTE:** No actualizar versiones sin autorización.

```txt
# requirements.txt (Backend)
fastapi==0.109.0
pandas==2.1.4
openpyxl==3.1.2
pymupdf==1.23.8
pytest==8.0.0
pytest-cov==4.1.0
uvicorn==0.27.0

# package.json (Frontend)
"react": "^18.2.0",
"vite": "^5.0.0",
"tailwindcss": "^3.4.0",
"jest": "^29.7.0"
```

---

## Proximo Documento (Next Document)

Continúa con: `03_Arquitectura_Backend.md` para ver la estructura del backend.

---

**Versión:** 1.0
**Líneas:** ~350
**Cumple reglas:** Sí
