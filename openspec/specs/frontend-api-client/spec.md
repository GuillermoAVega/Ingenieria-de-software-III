# Especificación del Cliente API del Frontend

Especificación principal para la integración del frontend React con la API del backend. Cubre la configuración de la URL base, el cliente HTTP compartido, el manejo de errores y las funciones de acceso a los recursos `secciones`, `platos`, `bebidas` y `postres`.

**Alcance**: esta capacidad cubre únicamente los endpoints que el backend expone actualmente:

- `GET /secciones`, `POST /secciones`, `GET /secciones/{id}`, `PUT /secciones/{id}`, `DELETE /secciones/{id}`
- `POST /productos/platos`, `GET /productos/platos/{id}`, `PUT /productos/platos/{id}`, `DELETE /productos/platos/{id}`
- `POST /productos/bebidas`, `GET /productos/bebidas/{id}`, `PUT /productos/bebidas/{id}`, `DELETE /productos/bebidas/{id}`
- `POST /productos/postres`, `GET /productos/postres/{id}`, `PUT /productos/postres/{id}`, `DELETE /productos/postres/{id}`


## ADDED Requirements

### Requirement: Configuración de la URL del backend

La URL base del backend DEBE configurarse mediante la variable de entorno `VITE_API_BASE_URL` en `Frontend/.env`. El proyecto DEBE incluir `Frontend/.env.example` con un valor de ejemplo y NO DEBE versionar el archivo `.env`. La variable DEBE estar tipada en `Frontend/src/vite-env.d.ts`. El cliente DEBE aceptar la URL sin barra final y DEBE tolerar una barra final configurada por error.

#### Scenario: API-01 El cliente usa la URL configurada
- DADO un `.env` con `VITE_API_BASE_URL=http://localhost:8000`
- CUANDO el frontend ejecuta una petición a `/secciones/1`
- ENTONCES la petición se realiza a `http://localhost:8000/secciones/1`

#### Scenario: API-02 La barra final no duplica la ruta
- DADO un `.env` con `VITE_API_BASE_URL=http://localhost:8000/`
- CUANDO el frontend ejecuta una petición a `/secciones/1`
- ENTONCES la petición se realiza a `http://localhost:8000/secciones/1`

#### Scenario: API-03 El ejemplo de entorno está versionado
- DADO el repositorio recién clonado
- CUANDO se revisa `Frontend/`
- ENTONCES existe `.env.example` con `VITE_API_BASE_URL` y el archivo `.env` está ignorado por Git

### Requirement: Cliente HTTP `apiFetch`

El frontend DEBE exponer una función genérica `apiFetch<T>(path, options)` en `Frontend/src/api/client.ts`. La función DEBE:

- Componer la URL con la variable de entorno.
- Serializar el cuerpo como JSON cuando no sea `FormData`.
- Establecer `Content-Type: application/json` automáticamente para cuerpos JSON.
- Aceptar `method`, `headers`, `signal` y otros parámetros de `RequestInit`.
- Devolver el JSON parseado con el tipo genérico solicitado.
- Devolver `undefined` para respuestas `204 No Content`.
- Lanzar un error de red controlado cuando el backend no esté disponible.

#### Scenario: API-04 Petición JSON exitosa
- DADO un backend que responde 200 con un objeto JSON
- CUANDO se llama a `apiFetch('/secciones/1')`
- ENTONCES se devuelve el objeto parseado y la petición incluye `Content-Type: application/json` si tuvo cuerpo

#### Scenario: API-05 Respuesta sin contenido
- DADO un `DELETE` que responde 204
- CUANDO se llama a `apiFetch('/secciones/1', { method: 'DELETE' })`
- ENTONCES la función resuelve con `undefined` y no intenta parsear JSON

#### Scenario: API-06 Error de red
- DADO que el backend no está en ejecución
- CUANDO se llama a `apiFetch('/secciones/1')`
- ENTONCES se lanza un error con un mensaje que indica que no se pudo conectar con el servidor

### Requirement: Manejo de errores HTTP

El cliente DEBE lanzar una instancia de `ApiError` para respuestas HTTP no exitosas. `ApiError` DEBE conservar `status`, `detail`, `body` y un `message` legible. El cliente DEBE interpretar los errores de FastAPI:

- `detail` como texto para errores de dominio (`404`, `409`, etc.).
- `detail` como lista de entradas de Pydantic para errores `422`, usando `msg` como mensaje.
- Entradas con `ids` o `bloqueantes` DEBEN conservarse dentro del cuerpo original.

El frontend DEBE exponer `getErrorMessage(error)` para obtener un mensaje apto para la interfaz y `getFieldErrors(error)` para asociar errores `422` a campos de formulario.

#### Scenario: API-07 Error de dominio con detail textual
- DADO un backend que responde `409` con `{"detail": "El nombre ya existe"}`
- CUANDO una pantalla captura el error
- ENTONCES `getErrorMessage` devuelve "El nombre ya existe"

#### Scenario: API-08 Error de validación de campo
- DADO un backend que responde `422` con `detail` que incluye `loc: ["body", "precio"]` y `msg: "Input should be greater than 0"`
- CUANDO una pantalla llama a `getFieldErrors(error)`
- ENTONCES el mapa devuelve la clave `precio` con el mensaje correspondiente

#### Scenario: API-09 Error sin cuerpo JSON
- DADO un backend que responde 500 con texto plano
- CUANDO se llama a `apiFetch`
- ENTONCES se lanza `ApiError` con `status = 500` y un mensaje genérico legible

### Requirement: Funciones de API de secciones

El frontend DEBE exponer en `Frontend/src/features/sections/api.ts` las funciones:

- `getSections()`
- `getSection(id)`
- `createSection(data)`
- `updateSection(id, data)`
- `deleteSection(id)`

`getSections()` DEBE consultar `GET /secciones` y devolver el listado ordenado por `posicion` tal como lo entrega el backend.

El tipo de envío DEBE incluir `nombre`, `subtitulo` y `posicion`. El tipo de respuesta DEBE incluir `id`, `nombre`, `subtitulo`, `posicion` y `productos_ids`. Los ids DEBEN tratarse como números. `posicion` DEBE enviarse como número entero.

#### Scenario: API-10 Listar secciones
- DADO un backend con secciones existentes
- CUANDO se llama a `getSections()`
- ENTONCES la petición es `GET /secciones` y se devuelve el listado tipado

#### Scenario: API-10b Consultar una sección
- DADO una sección existente con id 3
- CUANDO se llama a `getSection(3)`
- ENTONCES la petición es `GET /secciones/3` y se devuelve la sección tipada

#### Scenario: API-11 Crear una sección
- DADO un formulario con nombre, subtítulo y posición válidos
- CUANDO se llama a `createSection`
- ENTONCES la petición es `POST /secciones` con el cuerpo JSON correspondiente

#### Scenario: API-12 Modificar una sección
- DADO una sección existente con id 3
- CUANDO se llama a `updateSection(3, data)`
- ENTONCES la petición es `PUT /secciones/3` con el cuerpo JSON correspondiente

#### Scenario: API-13 Eliminar una sección
- DADO una sección existente con id 3
- CUANDO se llama a `deleteSection(3)`
- ENTONCES la petición es `DELETE /secciones/3` y la función resuelve sin cuerpo

### Requirement: Funciones de API de platos, bebidas y postres

El frontend DEBE exponer en `Frontend/src/features/products/api.ts` funciones de consulta, alta, modificación y borrado para cada subtipo:

- `getPlato`, `createPlato`, `updatePlato`, `deletePlato`
- `getBebida`, `createBebida`, `updateBebida`, `deleteBebida`
- `getPostre`, `createPostre`, `updatePostre`, `deletePostre`

Los cuerpos DEBEN respetar los campos del backend:

- Comunes: `nombre`, `precio`, `descripcion`, `imagen`, `seccion_id`.
- Plato: `cant_personas` obligatorio.
- Bebida: `es_alcoholica` obligatorio.
- Postre: solo campos comunes.
- En las actualizaciones, `dado_de_baja` es opcional y, si se omite, el backend conserva el estado actual.

La respuesta de producto DEBE tipar `precio` como `string` porque el backend serializa `Decimal` de Pydantic de esa forma. La conversión a número para la interfaz DEBE hacerse en la capa de presentación.

#### Scenario: API-14 Crear un plato
- DADO un formulario de plato con nombre, precio, cantidad de personas y sección opcional
- CUANDO se llama a `createPlato`
- ENTONCES la petición es `POST /productos/platos` con `cant_personas` incluido

#### Scenario: API-15 Crear una bebida
- DADO un formulario de bebida con `es_alcoholica` definido
- CUANDO se llama a `createBebida`
- ENTONCES la petición es `POST /productos/bebidas` y el cuerpo incluye el booleano

#### Scenario: API-16 Crear un postre
- DADO un formulario de postre con los campos comunes
- CUANDO se llama a `createPostre`
- ENTONCES la petición es `POST /productos/postres` sin campos específicos de otros subtipos

#### Scenario: API-17 El precio de respuesta se tipa como texto
- DADO un backend que devuelve `"precio": "1500.50"`
- CUANDO se consume `getPlato(1)`
- ENTONCES el tipo de `precio` es `string`

#### Scenario: API-18 Borrado lógico de un producto
- DADO un plato existente con id 1
- CUANDO se llama a `deletePlato(1)`
- ENTONCES la petición es `DELETE /productos/platos/1` y la función resuelve sin cuerpo

### Requirement: Integración de los formularios de sección y plato

La pantalla `SectionFormPage` DEBE usar `getSection` al editar una sección con id numérico y `createSection` o `updateSection` al guardar. La pantalla `ProductFormPage` DEBE usar `getPlato` al editar un plato con id numérico y `createPlato` o `updatePlato` al guardar. Ambas pantallas DEBEN:

- Mostrar un estado de carga mientras consultan el recurso.
- Deshabilitar el guardado mientras se envía la petición.
- Mostrar errores generales con un `Alert`.
- Asociar errores `422` a los campos correspondientes.
- Navegar al listado después de guardar correctamente.
- Tratar ids no numéricos de los datos demo como altas nuevas y avisar al usuario.

#### Scenario: API-19 Editar una sección existente
- DADO la ruta `#/secciones/3/editar` y una sección con id 3
- CUANDO se abre la pantalla
- ENTONCES el formulario se completa con los datos de `GET /secciones/3`

#### Scenario: API-20 Guardar cambios de una sección
- DADO el formulario de edición de una sección existente
- CUANDO se envía con datos válidos
- ENTONCES se llama a `PUT /secciones/{id}` y se navega a `#/secciones`

#### Scenario: API-21 Crear una sección nueva
- DADO la ruta `#/secciones/nueva`
- CUANDO se envía el formulario con datos válidos
- ENTONCES se llama a `POST /secciones` y se navega a `#/secciones`

#### Scenario: API-22 Editar un plato existente
- DADO la ruta `#/productos/1/editar` y un plato con id 1
- CUANDO se abre la pantalla
- ENTONCES el formulario se completa con los datos de `GET /productos/platos/1`, incluida la cantidad de personas

#### Scenario: API-23 Guardar un plato nuevo
- DADO la ruta `#/productos/nuevo`
- CUANDO se envía el formulario con datos válidos
- ENTONCES se llama a `POST /productos/platos` y se navega a `#/productos`

#### Scenario: API-24 Error de validación visible
- DADO un backend que rechaza el precio con un `422`
- CUANDO se envía el formulario de plato
- ENTONCES la pantalla muestra el mensaje del backend y no navega al listado

### Requirement: Selector de sección en el formulario de plato

`ProductFormPage` NO DEBE pedir el id de la sección como texto. DEBE cargar las secciones con `getSections()` y ofrecer un `<Select>` con una opción vacía ("Sin sección") y una opción por sección, mostrando el `nombre` y enviando el `id` como `seccion_id`. Mientras las secciones se cargan, el selector DEBE estar deshabilitado y mostrar un texto de carga. Si la carga falla, DEBE mostrarse el error asociado al campo de sección sin impedir el resto del formulario.

#### Scenario: API-25 Seleccionar una sección existente
- DADO un backend con las secciones "Entradas" (id 1) y "Postres" (id 2)
- CUANDO se abre el formulario de plato
- ENTONCES el selector muestra "Sin sección", "Entradas" y "Postres"
- Y al elegir "Postres" y guardar se envía `seccion_id = 2`

#### Scenario: API-26 Dejar el plato sin sección
- DADO el formulario de plato con el selector en "Sin sección"
- CUANDO se guarda con datos válidos
- ENTONCES se envía `seccion_id = null`

#### Scenario: API-27 Error al cargar las secciones
- DADO que `GET /secciones` falla
- CUANDO se abre el formulario de plato
- ENTONCES el selector queda vacío y se muestra el mensaje de error de la carga

### Requirement: Alcance de los listados

`SectionsListPage` y `ProductsListPage` NO DEBEN inventar rutas de listado que el backend no exponga. El listado de secciones (`GET /secciones`) SÍ está disponible y DEBE consumirse mediante `getSections()` cuando la pantalla lo requiera. Los listados de productos por subtipo (`GET /productos/platos`, `GET /productos/bebidas`, `GET /productos/postres`) NO existen: esas pantallas PUEDEN seguir usando datos de demostración y NO DEBEN enviar esas peticiones. Las funciones de borrado NO DEBEN usarse con ids de demostración no numéricos.

#### Scenario: API-28 Se usa el listado de secciones disponible
- DADO que el backend implementa `GET /secciones`
- CUANDO una pantalla necesita las secciones
- ENTONCES llama a `getSections()` en lugar de duplicar la petición

#### Scenario: API-29 No se inventan rutas de listado de productos
- DADO el módulo `features/products/api.ts`
- CUANDO se revisan sus funciones
- ENTONCES no existe una función de listado contra `GET /productos/platos`, `GET /productos/bebidas` ni `GET /productos/postres`
