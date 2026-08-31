# Plan 001 — Alta de Cliente

Plan técnico para implementar `specs/001-alta-cliente/spec.md`, respetando
`docs/constitution.md`. Este documento no contiene código: describe
estructura, decisiones y estrategia de verificación.

## Estructura de módulos

### Backend (`app/backend/`)

| Módulo | Responsabilidad | RF que cubre |
|---|---|---|
| `core.py` | Núcleo puro de reglas de negocio: validación de formato de DNI, nombre, apellido, email, teléfono; normalización de espacio simple; normalización numérica del DNI; asignación del estado inicial. Sin dependencias de FastAPI ni de SQLAlchemy — testeable de forma aislada. | RF-2, RF-3, RF-4, RF-5, RF-9, RF-10 |
| `schemas.py` | Modelos Pydantic de entrada (payload del alta) y de salida (cliente creado, lista de errores por campo). Declara los cinco campos de entrada como obligatorios. | RF-1, RF-7, RF-8 |
| `models.py` | Modelo SQLAlchemy `Customer` (tabla clientes): columnas DNI (entero, único), nombre, apellido, email, teléfono, estado (enumerado), con el estado por defecto en `Activo`. | RF-6, RF-9 |
| `repository.py` | Capa de persistencia: inserta un cliente nuevo, verifica existencia previa de un DNI (comparando por valor numérico) antes de insertar. Es la única parte del backend que habla con la base de datos. | RF-1, RF-6 |
| `routes/clientes.py` | Endpoint HTTP de alta. Orquesta: recibe el payload, delega validación de formato a `core.py`, delega verificación de duplicado y persistencia a `repository.py`, agrega todos los errores encontrados (formato + duplicado + obligatoriedad) en una sola respuesta, y arma el mensaje de éxito. | RF-1, RF-8 |
| `database.py` | Configuración del engine y la sesión de SQLAlchemy contra `app/backend/database.db` (la base de datos oficial del proyecto). | RF no numerado — NFR de persistencia |

### Frontend (`app/frontend/`)

| Módulo | Responsabilidad | RF que cubre |
|---|---|---|
| `components/ClienteForm.jsx` | Formulario de alta con los cinco campos de entrada. Antes de llamar a la API, valida con `validation.js`; si hay errores de obligatoriedad o formato los muestra de inmediato y no envía la solicitud. Si esa validación pasa, llama a la API: al recibir éxito muestra "Cliente registrado exitosamente" y limpia todos los campos; al recibir errores (ej. DNI duplicado) muestra las advertencias devueltas por el backend y conserva los valores ya ingresados. Diseño con layout responsivo (flexbox/grid + media queries) para uso en plataformas móviles. | RF-1, RF-8, RF-11, NFR de idioma/UI móvil |
| `validation.js` | Réplica en JavaScript de las reglas de formato y obligatoriedad de `core.py` (nombre/apellido, email, teléfono, DNI, campos obligatorios), para dar advertencia inmediata sin esperar al servidor. No incluye la detección de DNI duplicado (RF-6), que solo puede resolverse contra la base de datos. Módulo puro, sin dependencia de React — testeable sin renderizar UI. | RF-2 a RF-5, RF-7, RF-11 |
| `api/clientesApi.js` | Única función de comunicación con el endpoint de alta; traduce la respuesta HTTP a la forma que consume `ClienteForm.jsx` (éxito o lista de errores por campo). No contiene reglas de validación propias. | RF-1, RF-8 |

### Scripts (`app/backend/scripts/`)

| Módulo | Responsabilidad | RF que cubre |
|---|---|---|
| `seed_clientes_ficticios.py` | Script independiente de datos ficticios (ver sección siguiente). No forma parte del flujo de tests automatizados. | RF-1, RF-2 a RF-7, RF-9 (indirectamente, al reutilizar `core.py`/`repository.py`) |

## Scripts de inserciones de datos ficticios

**Ubicación**: `app/backend/scripts/seed_clientes_ficticios.py`.
**Objetivo**: poblar `database.db` con clientes de prueba para desarrollo
local y demostraciones manuales del formulario, sin tocar datos reales.

**Comportamiento esperado**:
- Reutiliza las mismas funciones de `core.py` (validación) y `repository.py`
  (verificación de duplicado + inserción) que usa la API en producción, en
  lugar de insertar filas directamente por SQL. Esto garantiza que ningún
  dato ficticio viole RF-2 a RF-7, y que el script sirva como caso de uso
  real del núcleo de negocio.
- Es idempotente: antes de insertar cada registro ficticio, verifica si el
  DNI ya existe (mismo mecanismo de RF-6); si ya existe, lo omite en lugar de
  duplicarlo o fallar.
- Todos los registros ficticios se insertan con estado "Activo", ya que el
  estado se asigna automáticamente (RF-9) y no puede fijarse manualmente.
- No se ejecuta como parte de `pytest`; es una utilidad manual, separada de
  la suite de tests, para no dejar datos fijos permanentes en los tests
  automatizados.

**Dataset ficticio propuesto**:

| DNI | Nombre | Apellido | Email | Teléfono |
|---|---|---|---|---|
| 30111222 | María José | Fernández | mariaj@correo.com | 11-4444-5555 |
| 28999888 | Juan Ignacio | Gómez | jgomez@mail.com | 1145556666 |
| 41234567 | Ana | López | analopez@dominio.com | 351-222-3333 |
| 0987654 | Martín | Álvarez | martin@correo.com | 261-555-1234 |
| 39456123 | Lucía | Sánchez | lucia@mail.com | 3794441234 |

El cuarto registro (`0987654`) se incluye deliberadamente con cero a la
izquierda para poder verificar manualmente, tras correr el script, que un
alta posterior con DNI `987654` es rechazada por duplicado (RF-6).

## Decisiones técnicas

1. **Separar `core.py` (reglas puras) de `repository.py` (persistencia) y de
   `routes/clientes.py` (interfaz HTTP)**, en vez de validar dentro de los
   handlers de FastAPI o dentro de los componentes React.
   Justificación: constitución regla 3 exige que la lógica de negocio no
   viva en componentes de UI y sea testeable sin renderizar UI.
   Alternativa descartada: validar los campos directamente en el handler de
   la ruta o en `ClienteForm.jsx` — descartada porque acoplaría las reglas
   de negocio al framework HTTP o a React, impidiendo testearlas de forma
   aislada. *(RF-2 a RF-5, RF-9, RF-10)*
   **Nota (revisitada por la decisión 9)**: esto sigue aplicando dentro de
   cada capa — `core.py` en el backend y `validation.js` en el frontend son
   ambos módulos puros, sin lógica dentro de handlers HTTP ni de
   componentes React.

2. **Base de datos temporal y aislada por test** (archivo SQLite temporal o
   `:memory:`, creada y destruida en cada test de integración), nunca
   `app/backend/database.db`.
   Justificación: evita que la suite de tests contamine o dependa de datos
   reales; `database.db` queda reservada exclusivamente para el uso real de
   la aplicación, conforme a la regla 5 de la constitución (persistencia
   única en la base de datos oficial).
   Alternativa descartada: correr los tests contra `database.db` directamente
   — descartada porque ensuciaría la base real y haría los tests
   dependientes del estado dejado por ejecuciones anteriores. *(RF-1, RF-6,
   RF-7)*

3. **DNI almacenado como entero (`INTEGER`) en `models.py`**, con constraint
   de unicidad a nivel de columna.
   Justificación: RF-6 exige comparar duplicados por valor numérico
   (`0123456` y `123456` son el mismo DNI); almacenar como entero hace que
   esa normalización sea automática, sin lógica adicional de comparación.
   Alternativa descartada: almacenar como texto (`VARCHAR`) y normalizar
   manualmente (recortar ceros a la izquierda) en cada consulta de
   duplicado — descartada por el riesgo de olvidar aplicar la normalización
   en algún punto del código y producir falsos negativos. *(RF-5, RF-6)*

4. **Estado del cliente como tipo enumerado** (`Activo` / `Inactivo`) en
   `models.py`, en vez de una columna de texto libre.
   Justificación: RF-9 solo contempla dos valores posibles; un enumerado
   impide persistir un valor inesperado y hace explícito el contrato de
   datos.
   Alternativa descartada: columna `VARCHAR` sin restricción de valores —
   descartada porque delega la integridad del dato a la disciplina del
   código que escribe, en vez de a la base de datos. *(RF-9)*

5. **Un único modelo Pydantic para el payload completo del alta**, dejando
   que Pydantic acumule todos los errores de campo en un solo intento de
   validación.
   Justificación: RF-8 exige mostrar todas las advertencias de un mismo
   envío; Pydantic ya agrupa nativamente los errores de todos los campos de
   un modelo en una sola estructura, sin necesitar lógica propia de
   acumulación.
   Alternativa descartada: validar campo por campo con corte en el primer
   error (`if/raise` secuencial) — descartada porque no cumple RF-8 salvo
   que se agregue lógica adicional para acumular errores, duplicando algo
   que el framework ya resuelve. *(RF-8)*

6. **Respuesta de error de la API como lista estructurada de pares
   campo + mensaje**, en vez de un único string de error concatenado.
   Justificación: el frontend necesita saber a qué campo asociar cada
   advertencia (RF-8) sin parsear texto libre; además los mensajes deben
   quedar en español de forma explícita (regla 6 de la constitución).
   Alternativa descartada: devolver un solo mensaje de error combinado —
   descartada porque obligaría al frontend a interpretar texto para separar
   advertencias por campo, un acoplamiento frágil. *(RF-2 a RF-8)*

7. **Estado del formulario en el frontend con `useState` de React nativo**,
   sin librería externa de manejo de formularios.
   Justificación: el formulario tiene cinco campos y reglas de validación
   que ya viven en el backend (decisión 1); no hay complejidad adicional que
   justifique una dependencia nueva, y la constitución regla 1 exige
   justificar en el PR cualquier framework adicional.
   Alternativa descartada: incorporar `react-hook-form` u otra librería de
   formularios — descartada por no estar justificada para un formulario de
   esta complejidad. *(RF-8)*

8. **Script de datos ficticios reutiliza `core.py` y `repository.py`** en
   vez de sentencias `INSERT` directas.
   Justificación: garantiza que los datos ficticios cumplan las mismas
   reglas que un alta real (RF-2 a RF-7) y sirve como prueba adicional de
   que el núcleo de negocio funciona fuera del contexto HTTP.
   Alternativa descartada: insertar filas por SQL crudo en el script —
   descartada porque podría dejar en la base datos ficticios inconsistentes
   con las reglas reales del sistema. *(RF-1 a RF-7, RF-9)*

9. **Duplicar las reglas de obligatoriedad y formato en `app/frontend/validation.js`**,
   reimplementadas en JavaScript a partir de las mismas reglas de `core.py`,
   en vez de que el Frontend dependa únicamente de la respuesta del backend
   para mostrar esos errores.
   Justificación: requisito explícito de UX (RF-11) — el Administrador debe
   ver la advertencia de inmediato, sin esperar un viaje de ida y vuelta al
   servidor por errores obvios (campo vacío, formato inválido). El backend
   (`core.py`) sigue siendo la autoridad final: vuelve a validar todo en
   cada request, así que un Frontend desactualizado o baipaseado (ej. una
   llamada directa a la API) no puede crear un cliente inválido.
   Riesgo aceptado: dos fuentes de la verdad para las mismas reglas (Python
   y JavaScript) que deben mantenerse sincronizadas a mano; no hay
   generación de código compartida entre backend y frontend en este stack.
   Alternativa descartada: mantener toda la validación de formato solo en
   el backend (decisión original 1) — descartada porque ya no cumple el
   requisito de feedback inmediato pedido explícitamente para esta feature.
   *(RF-11)*

## Estrategia de tests

### Backend — tests unitarios sobre `core.py` (sin base de datos, sin HTTP)
Cubren exclusivamente reglas de formato y normalización, ejecutables sin
levantar FastAPI ni SQLite:
- Nombre/apellido válidos e inválidos, incluyendo espacios internos
  múltiples, letras fuera del alfabeto español y campos solo con espacios.
  *(RF-2)*
- Email con TLD (válido) y sin punto en el dominio o sin `@` (inválido).
  *(RF-3)*
- Teléfono con letras u otros caracteres no permitidos. *(RF-4)*
- DNI no numérico o fuera del rango de 7-8 dígitos, incluyendo DNI con
  puntos/guiones. *(RF-5)*
- Estado por defecto asignado en la creación. *(RF-9)*
- Recorte de espacio simple al inicio/fin; verificación de que tabs o saltos
  de línea NO se recortan. *(RF-10)*

### Backend — tests de integración (`TestClient` de FastAPI + SQLite temporal)
Cubren el flujo completo, incluida la base de datos:
- Alta exitosa con datos válidos: se crea el registro, queda con estado
  Activo, y la respuesta trae el mensaje de éxito. *(RF-1, RF-9)*
- DNI duplicado exacto, DNI duplicado por normalización (ceros a la
  izquierda) y DNI duplicado que pertenece a un cliente Inactivo — los tres
  casos deben bloquear el alta. *(RF-6)*
- Envío con campos obligatorios vacíos. *(RF-7)*
- Envío con múltiples campos inválidos a la vez: la respuesta debe traer
  todas las advertencias correspondientes en un solo intento. *(RF-8)*

### Frontend — tests unitarios sobre `validation.js` (sin React)
Réplica de la batería de `core.py`, ejecutada como funciones puras:
- Campos vacíos (incluido solo espacios) marcados como obligatorios.
- Formato de nombre/apellido, email (con y sin TLD), teléfono y DNI.
- Varios errores de formato reportados juntos en una sola llamada. *(RF-2 a
  RF-5, RF-7, RF-11)*

### Frontend — Vitest + React Testing Library sobre `ClienteForm.jsx`
Con la llamada a la API mockeada (sin red real):
- Formulario vacío: se muestran las 5 advertencias de obligatoriedad y
  `altaCliente` (la API) NO se llega a invocar. *(RF-11)*
- Datos con formato inválido (ej. nombre con números): se muestran las
  advertencias correspondientes y tampoco se invoca la API. *(RF-11)*
- Datos válidos para el Frontend pero rechazados por el backend (ej. DNI
  duplicado): se llama a la API, se muestra la advertencia devuelta y se
  conservan los valores ingresados. *(RF-6, RF-8)*
- Envío válido simulado como éxito: se muestra "Cliente registrado
  exitosamente" y el formulario queda vacío. *(RF-1)*

### Verificación de tipado
`npm run typecheck` (JSDoc + `tsc --checkJs`) se ejecuta como parte del
pipeline de verificación de cada tarea, según ya define `AGENTS.md`; no
reemplaza a los tests funcionales de Vitest, es una verificación adicional
de forma.

### Datos de prueba
Los tests automatizados (unitarios y de integración) usan fixtures propias,
generadas dentro del propio test, independientes del dataset ficticio del
script de seed — el script de seed es solo para uso manual/exploratorio.

## Matriz de trazabilidad

| Requisito | Módulo(s) que lo implementa | Test(s) que lo cubre |
|---|---|---|
| RF-1 | `core.py`, `repository.py`, `routes/clientes.py`, `ClienteForm.jsx` | test de integración de alta exitosa; test de frontend de confirmación y limpieza |
| RF-2 | `core.py`, `validation.js` | test unitario de nombre/apellido (backend y frontend) |
| RF-3 | `core.py`, `validation.js` | test unitario de email, con y sin TLD (backend y frontend) |
| RF-4 | `core.py`, `validation.js` | test unitario de teléfono (backend y frontend) |
| RF-5 | `core.py`, `validation.js` | test unitario de DNI (backend y frontend) |
| RF-6 | `repository.py`, `models.py` | test de integración de DNI duplicado (exacto, normalizado, cliente Inactivo) |
| RF-7 | `schemas.py`, `routes/clientes.py`, `validation.js` | test de integración de campos obligatorios (backend); test unitario y de frontend de campos vacíos |
| RF-8 | `routes/clientes.py`, `ClienteForm.jsx` | test de integración de errores múltiples; test de frontend de conservación de valores |
| RF-9 | `core.py`, `models.py` | test unitario de estado por defecto; test de integración de persistencia con estado Activo |
| RF-10 | `core.py` | test unitario de recorte de espacio simple |
| RF-11 | `validation.js`, `ClienteForm.jsx` | test unitario de `validation.js`; test de frontend que verifica que `altaCliente` no se llama ante errores de obligatoriedad/formato |
| NFR — idioma español de mensajes | `core.py` (mensajes), `routes/clientes.py` | verificado por assertions de texto exacto en los tests existentes de RF-2 a RF-8 |
| NFR — persistencia única | `database.py`, `repository.py` | cubierto por diseño (decisión técnica 2), sin test dedicado |
| NFR — usabilidad móvil | `ClienteForm.jsx` (CSS responsivo) | verificación manual en navegador; no hay herramienta de test visual en el stack |

## Cumplimiento de la constitución

- **Regla 1 (stack fijo)**: FastAPI + Pydantic + SQLAlchemy en el backend;
  React + JavaScript + JSDoc en el frontend. No se introduce ningún
  framework adicional (ver decisión técnica 7).
- **Regla 2 (spec antes que código)**: este plan se redacta a partir de
  `specs/001-alta-cliente/spec.md`, ya cerrada.
- **Regla 3 (lógica separada de la interfaz)**: `core.py` concentra las
  reglas de negocio del backend y es testeable sin HTTP; `validation.js`
  hace lo propio en el frontend y es testeable sin renderizar ningún
  componente React (decisiones técnicas 1 y 9). Ninguna regla de formato u
  obligatoriedad vive dentro de un handler HTTP o de `ClienteForm.jsx`.
- **Regla 4 (tests obligatorios)**: la estrategia de tests cubre los once
  RF y los casos límite de la spec antes de considerar la feature terminada.
- **Regla 5 (persistencia única)**: todo dato de cliente pasa por
  `database.py`/`repository.py` hacia `database.db`; los tests usan bases
  temporales separadas, no datos ad-hoc dentro de la app (decisión técnica
  2).
- **Regla 6 (idioma consistente)**: identificadores de código en inglés
  (`core.py`, `repository.py`, `ClienteForm.jsx`, etc.); mensajes al
  Administrador en español, definidos como texto explícito (decisión técnica
  6).
