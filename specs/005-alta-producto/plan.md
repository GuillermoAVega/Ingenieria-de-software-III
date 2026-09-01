# Plan 005 — Alta de Producto

Plan técnico para implementar `specs/005-alta-producto/spec.md`, respetando
`docs/constitution.md`. Este documento no contiene código: describe
estructura, decisiones y estrategia de verificación.

## 1. Estructura de Módulos

Esta es la primera feature del dominio Producto. En vez de agregar sus
funciones a los archivos ya existentes de Cliente (`core.py`,
`repository.py`), se crean sus propios módulos paralelos, replicando el
mismo patrón por dominio que ya usa `routes/` (`routes/clientes.py`).

### Backend (`app/backend/`)

- **`models.py` (extendido)**: agrega la clase `Product` (tabla
  `products`) junto a `Customer`, sobre el mismo `Base`. Se mantiene un
  único archivo de modelos para que `database.create_tables()` siga
  creando todas las tablas del proyecto desde un solo lugar. [Cubre RF-1
  a RF-5]
- **`core_producto.py` (nuevo)**: funciones puras de validación específicas
  de Producto (`validate_positive_number`, `validate_positive_integer`),
  reutilizando `trim_leading_trailing_space` y `normalize_search_text` de
  `core.py` (utilidades genéricas, no específicas de Cliente) en vez de
  duplicarlas. Sin dependencia de FastAPI ni de SQLAlchemy. [Cubre RF-3,
  RF-4, RF-7]
- **`repository_producto.py` (nuevo)**: `sku_exists` (compara sin
  distinguir mayúsculas contra los SKU ya registrados) y `create_product`
  (inserta un producto nuevo). Única capa que consulta la tabla
  `products`. [Cubre RF-1, RF-5]
- **`routes/productos.py` (nuevo)**: endpoint de alta. Orquesta: recibe el
  payload, recorta y valida los campos con `core_producto.py`, verifica
  duplicado de SKU con `repository_producto.py`, agrega todos los errores
  encontrados (formato + obligatoriedad + duplicado) en una sola
  respuesta, y arma el mensaje de éxito. [Cubre RF-1, RF-2, RF-6]
- **`main.py` (extendido)**: incluye el nuevo router de productos junto al
  de clientes. [Soporte, sin RF directo]

### Frontend (`app/frontend/`)

- **`productoFields.js` (nuevo)**: metadata de los 6 campos del formulario
  de alta de producto (label, hint), análogo a `clienteFields.js`. [Cubre
  RF-1, RF-2]
- **`validationProducto.js` (nuevo)**: réplica en JavaScript de las reglas
  de `core_producto.py` (obligatoriedad de los 5 campos requeridos,
  precio/stock positivos), para dar advertencia inmediata sin esperar al
  servidor, siguiendo la misma convención ya establecida desde
  [[001-alta-cliente]]. No incluye la detección de SKU duplicado, que solo
  puede resolverse contra la base de datos. Módulo puro, sin dependencia
  de React. [Cubre RF-2, RF-3, RF-4]
- **`api/productosApi.js` (nuevo)**: única función de comunicación con el
  endpoint de alta de producto; traduce la respuesta HTTP a éxito o lista
  de errores por campo, igual forma que `clientesApi.js`. [Cubre RF-1,
  RF-6]
- **`components/ProductoForm.jsx` (nuevo)**: formulario de alta con los 6
  campos. Valida con `validationProducto.js` antes de llamar a la API; si
  hay errores de obligatoriedad o formato los muestra de inmediato y no
  envía la solicitud. Si esa validación pasa, llama a la API: al recibir
  éxito muestra "Producto registrado exitosamente" y limpia el formulario;
  al recibir errores (ej. SKU duplicado) muestra las advertencias
  devueltas por el backend y conserva los valores ingresados. [Cubre RF-1,
  RF-6]
- **`App.jsx` (extendido)**: agrega una quinta pestaña "Alta de Producto"
  a la barra de pestañas ya existente. [Soporte, sin RF directo]

## 2. Modelo de la Base de Datos

Nueva tabla `products`, sin relación con `customers`:

| Columna | Tipo | Notas |
|---|---|---|
| `id` | Integer, PK, autoincrement | |
| `sku` | String, `unique=True`, `index=True`, `nullable=False` | Se guarda el valor recortado (trim), preservando mayúsculas/minúsculas tal como lo ingresó el Administrador. [Cubre RF-5, RF-7] |
| `name` | String, `nullable=False` | [Cubre RF-2] |
| `brand` | String, `nullable=False` | [Cubre RF-2] |
| `description` | String, `nullable=True` | Único campo opcional. [Cubre RF-2] |
| `unit_price` | Float, `nullable=False` | Debe ser > 0 (RF-3); sin restricción de decimales (resuelto en la entrevista). |
| `stock` | Integer, `nullable=False` | Debe ser > 0 (RF-4); rechaza decimales al validarse antes del insert. |

## 3. Contrato de la Interfaz Web

### Endpoint: `POST /productos`

- **Método y ruta:** `POST /productos`
- **Payload de entrada:**
  ```json
  {
    "sku": "ABC123",
    "name": "Coca-Cola 500ml",
    "brand": "Coca-Cola",
    "description": "Botella descartable",
    "unit_price": "350.50",
    "stock": "100"
  }
  ```
  `description` puede venir vacío o ausente; los demás campos son
  obligatorios. `unit_price` y `stock` llegan como texto, igual que el
  resto de los payloads de esta app (ver `ClienteAltaRequest`), y se
  validan/convierten en el backend.
- **Respuesta esperada (éxito):** `201 Created`
  ```json
  {
    "message": "Producto registrado exitosamente",
    "product": {
      "sku": "ABC123", "name": "Coca-Cola 500ml", "brand": "Coca-Cola",
      "description": "Botella descartable", "unit_price": 350.5, "stock": 100
    }
  }
  ```
  [Cubre RF-1]
- **Respuesta esperada (error):** `422 Unprocessable Entity`
  ```json
  { "errors": [ { "field": "unit_price", "message": "El valor debe ser un número positivo" } ] }
  ```
  Devuelve todas las advertencias del intento en un mismo arreglo (campos
  vacíos, formato inválido de precio/stock, SKU duplicado). [Cubre RF-2,
  RF-3, RF-4, RF-5, RF-6]

### Vista: pestaña "Alta de Producto" (`ProductoForm.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas, igual que
  las de Cliente).
- **Propósito:** registrar un nuevo producto en el catálogo. [Cubre
  HU-PROD-01]
- **Componentes/estados clave:**
  - Formulario con los 6 campos (SKU, Nombre, Marca, Descripción, Precio
    unitario, Stock inicial), con `Descripción` marcada como opcional en
    la etiqueta.
  - Banner de éxito y banner de error múltiple, igual estilo que
    `ClienteForm.jsx`.
  - Errores de campo mostrados junto a cada input; valores conservados
    tras un error del backend. [Cubre RF-6]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** crear `core_producto.py` y `repository_producto.py`
   separados de `core.py`/`repository.py` (que quedan exclusivos de
   Cliente), en vez de agregar las funciones de Producto a esos mismos
   archivos.
   **Justificación:** replica el patrón por dominio que ya existe en
   `routes/` (`routes/clientes.py`); evita mezclar las reglas de negocio
   de dos dominios distintos (Cliente y Producto) en los mismos archivos a
   medida que el proyecto crece, y mantiene cada dominio testeable de
   forma independiente.
   **Alternativa descartada:** agregar `validate_positive_number` y
   `sku_exists` dentro de `core.py`/`repository.py` — descartada porque
   esos archivos quedarían con reglas de negocio de dos dominios sin
   relación entre sí, dificultando su lectura y mantenimiento a futuro.
   *(Estructural, base de RF-1 a RF-5)*

2. **Decisión Tomada:** `models.py` sigue siendo el único archivo de
   modelos SQLAlchemy del proyecto; `Product` se agrega ahí junto a
   `Customer`, sobre el mismo `Base`.
   **Justificación:** `database.create_tables()` ya crea todas las tablas
   registradas en `Base.metadata` desde un solo lugar; separar los modelos
   en archivos por dominio obligaría a garantizar que ambos se importen
   antes de crear las tablas, sin ningún beneficio real para un proyecto
   de este tamaño.
   **Alternativa descartada:** `models_producto.py` separado — descartada
   por la complejidad extra de coordinar los imports para que
   `Base.metadata` los conozca a todos, sin necesidad real todavía.
   *(Soporte, base de RF-1 a RF-5)*

3. **Decisión Tomada:** `unit_price` se almacena como `Float`, no como
   `Numeric`/`Decimal`.
   **Justificación:** la spec resolvió explícitamente en la entrevista que
   no hay restricción de cantidad de decimales tipo moneda; el proyecto
   todavía no hace cálculos financieros agregados (totales, impuestos)
   donde el redondeo de punto flotante sea un riesgo real.
   **Alternativa descartada:** `Numeric`/`Decimal` de SQLAlchemy —
   descartada por agregar complejidad de conversión (serialización JSON,
   comparaciones) no justificada por ningún RF de esta spec.
   *(RF-3)*

4. **Decisión Tomada:** el SKU se guarda con `unique=True` a nivel de
   columna (backstop de integridad en la base) y, además, se compara sin
   distinguir mayúsculas en la capa de aplicación (`repository_producto.sku_exists`,
   vía `func.lower()` de SQLAlchemy), en vez de depender de un solo
   mecanismo.
   **Justificación:** el `unique=True` por sí solo no alcanza para RF-5
   (SQLite compara `UNIQUE` distinguiendo mayúsculas por default), así que
   la regla real vive en la aplicación; el constraint de la base queda
   como red de seguridad ante una inserción que bypasee `repository_producto.py`,
   igual que la decisión técnica 3 de [[001-alta-cliente]].
   **Alternativa descartada:** una columna `UNIQUE COLLATE NOCASE` en
   SQLite — descartada por atar el modelo a sintaxis específica de un
   dialecto para un caso que la capa de aplicación ya cubre sin
   necesidad de esa dependencia. *(RF-5)*

5. **Decisión Tomada:** `core_producto.py` importa y reutiliza
   `trim_leading_trailing_space` y `normalize_search_text` de `core.py`,
   en vez de reimplementarlos.
   **Justificación:** ambas funciones son utilidades genéricas de texto,
   sin ninguna regla específica de Cliente; duplicarlas violaría el
   principio de una sola fuente de verdad para la misma lógica.
   **Alternativa descartada:** copiar ambas funciones dentro de
   `core_producto.py` — descartada por duplicar código sin ningún
   beneficio de aislamiento real. *(RF-5, RF-7)*

6. **Decisión Tomada:** el Frontend valida de inmediato con
   `validationProducto.js` antes de llamar a la API, igual que
   `ClienteForm.jsx` hace con `validation.js`, aunque esta spec no lo pide
   de forma explícita.
   **Justificación:** es la convención ya establecida en el proyecto desde
   [[001-alta-cliente]] para todo formulario de carga; mantenerla evita una
   experiencia inconsistente entre dar de alta un cliente y dar de alta un
   producto. El backend sigue siendo la autoridad final.
   **Alternativa descartada:** depender solo de la respuesta del backend —
   descartada por romper la consistencia de UX ya establecida en el resto
   de la aplicación. *(RF-2, RF-3, RF-4)*

7. **Decisión Tomada:** la pestaña "Alta de Producto" se agrega
   directamente a la barra de pestañas plana ya existente en `App.jsx`
   (junto a las cuatro de Cliente), sin introducir todavía una navegación
   anidada tipo "Clientes" / "Productos".
   **Justificación:** esta es la primera y única funcionalidad de
   Producto; reestructurar la navegación en dos niveles ahora sería
   diseñar para una necesidad hipotética (más features de Producto) que
   todavía no existe.
   **Alternativa descartada:** agrupar las pestañas por dominio desde
   ahora — descartada por no estar justificada con una sola pestaña de
   Producto; se reconsiderará cuando exista una segunda feature de este
   dominio. *(Estructural)*

## 5. Estrategia de Tests

### Tests unitarios (`core_producto.py`, sin base de datos, sin HTTP)
- `validate_positive_number`: `"350.50"` (válido), `"0"` y `"-5"`
  (inválidos), `"abc"` (inválido, mismo resultado que los anteriores).
  [Cubre RF-3]
- `validate_positive_integer`: `"100"` (válido), `"0"` y `"-1"`
  (inválidos), `"5.5"` (inválido, decimales no permitidos), `"abc"`
  (inválido). [Cubre RF-4]

### Tests de integración (`repository_producto.py`, SQLite temporal)
- `sku_exists` detecta un SKU ya registrado sin importar mayúsculas
  (`"ABC123"` vs. `"abc123"`). [Cubre RF-5]
- `sku_exists` devuelve `False` si no hay ningún producto con ese SKU.
  [Cubre RF-5]
- `create_product` persiste el producto con los valores ingresados,
  incluida una `description` vacía/ausente. [Cubre RF-1, RF-2]

### Tests de integración (`routes/productos.py`, `TestClient`)
- Alta exitosa con los 6 campos válidos, y alta exitosa sin `description`.
  [Cubre RF-1, RF-2]
- Envío con los 5 campos obligatorios vacíos devuelve las 5 advertencias
  correspondientes. [Cubre RF-2]
- `unit_price` en `"0"`, negativo y no numérico devuelven la misma
  advertencia de "número positivo". [Cubre RF-3]
- `stock` en `"0"`, negativo, con decimales (`"5.5"`) y no numérico
  devuelven la misma advertencia. [Cubre RF-4]
- SKU duplicado (incluida una variante con mayúsculas distintas) bloquea
  el alta con la advertencia correspondiente. [Cubre RF-5]
- Envío con múltiples errores a la vez (ej. `unit_price` negativo y SKU
  duplicado) devuelve ambas advertencias en un mismo intento. [Cubre RF-6]
- Un SKU o Nombre con espacios al inicio/fin se recorta antes de
  persistirse. [Cubre RF-7]

### Tests unitarios (`validationProducto.js`, sin React)
- Réplica de la batería de `core_producto.py`: campos obligatorios vacíos,
  `unit_price`/`stock` inválidos, varios errores reportados juntos en una
  sola llamada. [Cubre RF-2, RF-3, RF-4]

### Tests E2E (Vitest + React Testing Library sobre `ProductoForm.jsx`)
Con `productosApi.js` mockeado (sin red real):
- Formulario vacío: se muestran las 5 advertencias de obligatoriedad
  (no incluye `description`) y la API no se invoca. [Cubre RF-2]
- Datos válidos para el Frontend pero rechazados por el backend (ej. SKU
  duplicado): se llama a la API, se muestra la advertencia devuelta y se
  conservan los valores ingresados. [Cubre RF-5, RF-6]
- Envío válido simulado como éxito: se muestra "Producto registrado
  exitosamente" y el formulario queda vacío. [Cubre RF-1]

### Verificación de tipado
`npm run typecheck` se ejecuta como parte del pipeline de verificación de
cada tarea, igual que en las features de Cliente.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** FastAPI + Pydantic + SQLAlchemy y React +
  JavaScript + JSDoc, sin dependencias nuevas (se descartó explícitamente
  `Numeric`/`Decimal` y `COLLATE NOCASE`; ver decisiones 3 y 4).
- **Regla 2 (spec antes que código):** este plan parte de
  `specs/005-alta-producto/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `core_producto.py`
  concentra las reglas de negocio del backend, testeable sin HTTP;
  `validationProducto.js` cumple el mismo rol en el Frontend, testeable
  sin renderizar componentes.
- **Regla 4 (tests obligatorios):** la estrategia cubre los siete RF de la
  spec antes de considerar la feature terminada.
- **Regla 5 (persistencia única):** `create_product`/`sku_exists` son la
  única vía de acceso a la tabla `products`, a través de
  `database.py`/`repository_producto.py`.
- **Regla 6 (idioma consistente):** identificadores en inglés (`Product`,
  `sku_exists`, `ProductoForm.jsx`); mensajes al Administrador en español
  ("Producto registrado exitosamente", "El código de producto está
  duplicado").
