# Plan 013 — Validación Amigable de Formularios

Plan técnico para implementar `specs/013-validacion-amigable-formularios/spec.md`,
respetando `docs/constitution.md`. No se agregan módulos nuevos ni
dependencias: se extienden los módulos de validación y los componentes
ya existentes de [[001-alta-cliente]], [[003-modificacion-cliente]],
[[005-alta-producto]], [[007-modificacion-producto]] y
[[009-alta-venta]]/[[011-modificacion-venta]].

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`core.py` (modificado)**: se relaja `_EMAIL_PATTERN` de
  `r"[^@\s]+@[^@\s]+\.[^@\s]+"` a `r"[^@\s]+@[^@\s]+"` (una arroba,
  parte local y dominio no vacíos, sin espacios, sin exigir un punto).
  `validate_email` no cambia de firma. [Cubre RF-3]
- **`routes/clientes.py` (modificado)**: actualiza los mensajes
  `INVALID_DNI_MESSAGE`, `INVALID_PHONE_MESSAGE` e
  `INVALID_EMAIL_MESSAGE`. Al ser constantes usadas por la única
  función `_validate_fields` (compartida por `alta_cliente` y
  `editar_cliente`), el cambio aplica a ambos endpoints con una sola
  edición. [Cubre RF-1, RF-2, RF-3]

No se toca `core_producto.py` ni `routes/productos.py`: sus mensajes
("El valor debe ser un número positivo", "El campo es obligatorio") ya
son específicos (fuera de alcance de esta spec, ver spec.md).

### Frontend (`app/frontend/`)

- **`validation.js` (modificado)**: actualiza `EMAIL_PATTERN` (mismo
  criterio que el Backend), `INVALID_DNI_MESSAGE`,
  `INVALID_PHONE_MESSAGE` e `INVALID_EMAIL_MESSAGE`. Al ser usado por
  `validateClienteForm`, que ya comparten `ClienteForm.jsx` y
  `ClienteEdicionForm.jsx`, el cambio aplica a ambos formularios de una
  vez. [Cubre RF-1, RF-2, RF-3]
- **`ventaDetalle.js` (extendido)**: agrega `validateQuantityFormat(quantity)`,
  función pura que devuelve `POSITIVE_NUMBER_MESSAGE` si la cantidad no
  es un entero positivo, o `null` si es válida — reutiliza la misma
  regla que ya usa `addItem` internamente, extraída para poder
  invocarla sola, sin necesitar el producto ni el stock. [Cubre RF-6]
- **`ClienteForm.jsx` / `ClienteEdicionForm.jsx` (extendidos)**: agregan
  un manejador `handleBlur(field)` que, si el valor del campo (recortado)
  no está vacío, corre `validateClienteForm` sobre los valores actuales
  y aplica (o limpia) únicamente el error del campo que perdió el foco,
  dejando los demás campos sin tocar. Se conecta al `onBlur` de cada
  `<input>` generado desde `CLIENTE_FIELDS`. [Cubre RF-4, RF-7, RF-9]
- **`ProductoForm.jsx` / `ProductoEdicionForm.jsx` (extendidos)**: mismo
  patrón que arriba, con `validateProductoForm`/
  `validateProductoEdicionForm` y los campos de
  `PRODUCTO_FIELDS`/`PRODUCTO_EDICION_FIELDS`. [Cubre RF-5, RF-7, RF-9]
- **`VentaForm.jsx` / `VentaEdicionForm.jsx` (extendidos)**: agregan un
  `onBlur` al input "Cantidad" que, si el valor no está vacío, corre
  `validateQuantityFormat` y muestra el mensaje en `itemError` si no es
  válido. El `onChange` de ese mismo input limpia `itemError`
  únicamente si su valor actual es el mensaje de cantidad inválida (ver
  Decisión Técnica 3), sin afectar un error de SKU/stock que ya
  estuviera mostrado. [Cubre RF-6, RF-7, RF-9]

## 2. Modelo de la Base de Datos
No se agregan ni modifican tablas ni columnas. Esta spec no toca
persistencia: es exclusivamente validación de formato en Backend y
Frontend antes de llegar a la base de datos.

## 3. Contrato de la Interfaz Web

No se agregan ni modifican endpoints. Los contratos de `POST /clientes`,
`PUT /clientes/{dni}/editar`, `POST /productos`,
`PUT /productos/{sku}/editar`, `POST /ventas` y
`PUT /ventas/{sale_id}/detalle` mantienen su forma; solo cambia, para
los de Cliente, el contenido de tres mensajes de error y el criterio de
aceptación del email (RF-1, RF-2, RF-3), sin cambiar el código HTTP ni
la forma del payload de error (`{ errors: [{ field, message }] }`).

### Vistas afectadas (sin cambios de ruta/URL ni de flujo)

- **`ClienteForm.jsx` / `ClienteEdicionForm.jsx`**: agregan aviso de
  formato al perder el foco en DNI, Nombre, Apellido, Email y
  Teléfono. [Cubre RF-4, RF-7, RF-9]
- **`ProductoForm.jsx` / `ProductoEdicionForm.jsx`**: agregan aviso de
  formato al perder el foco en Precio unitario y Stock (y, por
  reutilizar el mismo mecanismo genérico sobre todos los campos de
  `PRODUCTO_FIELDS`, también en SKU/Nombre/Marca, que hoy solo tienen
  la regla "campo obligatorio" — sin regla de formato adicional, por lo
  que el aviso de blur no tiene ningún efecto observable distinto ahí).
  [Cubre RF-5, RF-7, RF-9]
- **`VentaForm.jsx` / `VentaEdicionForm.jsx`**: agregan aviso de formato
  al perder el foco en "Cantidad", dentro del armado de ítems. [Cubre
  RF-6, RF-7, RF-9]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** el aviso al perder el foco reutiliza la función
   de validación completa ya existente (`validateClienteForm`,
   `validateProductoForm`, `validateProductoEdicionForm`), tomando del
   resultado solo la clave del campo que disparó el `blur`, en vez de
   escribir una función de validación por-campo separada.
   **Justificación:** evita duplicar cada regex/regla en dos lugares
   (una función "de campo" y otra "de formulario completo") que
   podrían desincronizarse con el tiempo; la función completa ya
   existe, está testeada, y correrla es barato (son objetos de 5-6
   campos, sin I/O).
   **Alternativa descartada:** crear `validateClienteField(field,
   value)`/`validateProductoField(field, value)` como funciones nuevas
   independientes — descartada por duplicar las reglas de formato ya
   escritas en `validateClienteForm`/`validateProductoForm`, con el
   riesgo de que diverjan al modificar una y no la otra en el futuro.
   *(RF-4, RF-5)*

2. **Decisión Tomada:** el aviso de blur se omite si el valor del campo
   (recortado) está vacío; en ese caso no se toca `fieldErrors` para
   ese campo.
   **Justificación:** es exactamente RF-7 — un campo vacío no debe
   marcarse como error hasta el envío, para no mostrar una fila de
   errores de "campo obligatorio" en cascada mientras el Administrador
   todavía está completando el formulario de arriba hacia abajo.
   **Alternativa descartada:** validar también la ausencia de valor en
   el blur — descartada porque contradice explícitamente RF-7 y
   degradaría la experiencia que esta spec busca mejorar.
   *(RF-7)*

3. **Decisión Tomada:** en `VentaForm.jsx`/`VentaEdicionForm.jsx`, el
   `onChange` del input "Cantidad" limpia `itemError` únicamente
   cuando su valor actual es exactamente el mensaje de cantidad
   inválida (`POSITIVE_NUMBER_MESSAGE`); si `itemError` tiene otro
   mensaje (SKU no encontrado, producto inactivo, stock insuficiente),
   no se toca.
   **Justificación:** a diferencia de Cliente/Producto (que tienen un
   `fieldErrors` por campo), Venta usa un único `itemError` de texto
   compartido entre varias validaciones (SKU y Cantidad). Limpiarlo sin
   condición borraría por accidente un error de SKU vigente apenas el
   Administrador toca el campo de Cantidad, aunque ese error no tenga
   nada que ver con la cantidad.
   **Alternativa descartada:** dividir `itemError` en un estado por
   campo (`skuError`/`quantityError`) para Venta, igual que
   Cliente/Producto — descartada por ser un rediseño más grande que lo
   que pide esta spec (que solo agrega el aviso de formato en
   Cantidad); queda como una mejora posible a futuro si se retoma el
   diseño del armado de ítems.
   *(RF-6, RF-9)*

4. **Decisión Tomada:** no se extrae un hook compartido (ej.
   `useFieldBlurValidation`) para los cuatro formularios de
   Cliente/Producto; cada componente implementa su propio `handleBlur`
   siguiendo el mismo patrón, igual que ya ocurre hoy con
   `handleChange` (duplicado idéntico en los cuatro).
   **Justificación:** consistencia con el estilo ya establecido en el
   proyecto (cada formulario mantiene su propio estado local sin
   hooks compartidos); introducir un hook nuevo solo para esta spec
   sería una abstracción prematura sobre cuatro usos casi idénticos
   pero no promovidos a compartidos hasta ahora.
   **Alternativa descartada:** crear un hook custom reutilizable —
   descartada por ser una refactorización más amplia que lo que pide
   la spec, y por romper la simetría con `handleChange`, que sigue sin
   estar extraído.
   *(RF-4, RF-5)*

5. **Decisión Tomada:** el regex de email se relaja tanto en
   `core.py` (Backend) como en `validation.js` (Frontend), en el mismo
   commit/tarea.
   **Justificación:** ambos ya duplican intencionalmente las mismas
   reglas (comentario explícito en `validation.js`: "el backend sigue
   siendo la autoridad final"); dejar uno de los dos con el regex viejo
   generaría una discrepancia real entre lo que el Frontend acepta y lo
   que el Backend rechaza (o viceversa).
   **Alternativa descartada:** relajarlo solo en el Backend y dejar
   que el Frontend lo detecte recién en la respuesta del servidor —
   descartada porque contradice el propósito de esta spec (dar aviso
   inmediato) y porque ambas capas ya están sincronizadas para el
   resto de las reglas.
   *(RF-3)*

## 5. Estrategia de Tests

### Backend — tests unitarios (`core.py`)
- `validate_email`: acepta `usuario@dominio` (sin punto) y
  `usuario@dominio.com` (con punto); rechaza sin arroba, con espacios,
  con más de una arroba, o con parte local/dominio vacíos. [Cubre RF-3]

### Backend — tests de integración (`routes/clientes.py`, `TestClient`)
- `POST /clientes` con DNI de formato inválido devuelve el mensaje "El
  DNI debe contener solo números (7 u 8 dígitos)". [Cubre RF-1]
- `POST /clientes` con teléfono de formato inválido devuelve "El
  teléfono debe contener solo números y guiones". [Cubre RF-2]
- `POST /clientes` con email `admin@localhost` (sin punto) devuelve
  201 (antes hubiera sido 422). [Cubre RF-3]
- `PUT /clientes/{dni}/editar` con los mismos tres casos, confirmando
  que la corrección aplica también a la edición (misma
  `_validate_fields`). [Cubre RF-1, RF-2, RF-3]

### Frontend — tests unitarios (`validation.js`, `ventaDetalle.js`)
- `validateClienteForm`: DNI/teléfono inválidos devuelven los nuevos
  mensajes; email sin punto ya no devuelve error, email con punto
  sigue sin devolver error, email sin arroba sigue devolviendo error.
  [Cubre RF-1, RF-2, RF-3]
- `validateQuantityFormat`: `"abc"`/`"0"`/`"-1"`/`"5.5"` devuelven el
  mensaje; `"3"` devuelve `null`. [Cubre RF-6]

### Frontend — Vitest + RTL sobre los seis componentes
- `ClienteForm.jsx`/`ClienteEdicionForm.jsx`: escribir un DNI inválido
  y pasar al campo Nombre (blur) muestra el mensaje de inmediato, sin
  haber tocado "Registrar"/"Guardar cambios"; dejar un campo vacío y
  pasar a otro no muestra ningún error; corregir el valor y perder el
  foco de nuevo hace desaparecer el error; el envío sigue validando
  todos los campos igual que antes. [Cubre RF-1, RF-2, RF-3, RF-4,
  RF-7, RF-8, RF-9]
- `ProductoForm.jsx`/`ProductoEdicionForm.jsx`: mismo patrón sobre
  "Precio unitario" y "Stock". [Cubre RF-5, RF-7, RF-8, RF-9]
- `VentaForm.jsx`/`VentaEdicionForm.jsx`: escribir una cantidad
  inválida en el armado de ítems y pasar al botón "Agregar" (blur)
  muestra el mensaje antes de hacer clic; un error de SKU no
  encontrado no desaparece al tocar el campo Cantidad con un valor
  válido. [Cubre RF-6, RF-7, RF-8, RF-9]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/013-validacion-amigable-formularios/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** las reglas de formato
  siguen viviendo en `core.py`/`validation.js`/`validationProducto.js`/
  `ventaDetalle.js`, testeables sin renderizar UI; los componentes solo
  deciden cuándo invocarlas (`onBlur`).
- **Regla 4 (tests obligatorios):** la estrategia cubre las 9 RF de la
  spec.
- **Regla 5 (persistencia única):** no aplica, esta spec no toca datos
  persistidos.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`validateQuantityFormat`, `handleBlur`); mensajes en español ("El
  DNI debe contener solo números (7 u 8 dígitos)").
