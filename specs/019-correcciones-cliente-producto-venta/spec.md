# Spec 019 — Correcciones sobre Cliente, Producto y Venta

## Contexto y objetivo
Esta spec agrupa cuatro correcciones puntuales recibidas sobre features ya
implementadas, en la misma línea que [[013-validacion-amigable-formularios]]
y [[014-correcciones-cliente]] (feedback directo de uso, no una nueva
historia de negocio):

1. **Modificación de Cliente** ([[003-modificacion-cliente]]): hoy se
   permite editar los datos de un cliente en estado Inactivo (sin
   reactivarlo). Se pide bloquear esta operación por completo.
2. **Alta de Producto** ([[005-alta-producto]]): la leyenda de ayuda del
   campo Código/SKU ("Cualquier texto, sin espacios al inicio/fin") es
   demasiado técnica; se pide un texto más claro.
3. **Listado de Ventas** ([[012-listar-ventas]], [[018-mejoras-venta-cliente]]):
   el botón de "ver detalle" de una venta ya usa el emoji 👁 y ya intenta
   abrir un panel con los productos de la venta, pero ese panel no tiene
   estilos de modal (sin fondo superpuesto, sin cierre con ícono de
   cierre): visualmente no se comporta como un modal. Se pide corregir
   esto y reemplazar el emoji por un ícono SVG.
4. **Listado de Clientes** ([[004-listar-clientes]], [[014-correcciones-cliente]]):
   hoy hay un único campo de texto que busca a la vez sobre Nombre,
   Apellido y DNI. Se pide reemplazarlo por un menú desplegable donde el
   Administrador elija un único campo (Nombre, Apellido o DNI) y un input
   al lado para el valor de búsqueda de ese campo.

## Usuarios / actores
- **Administrador**: único rol que modifica clientes, da de alta
  productos, y consulta listados de ventas y clientes en esta spec.

## Historias de usuario
- H1: Como Administrador quiero que el sistema no me permita modificar los
  datos de un cliente Inactivo, para evitar operaciones inválidas sobre
  clientes dados de baja.
- H2: Como Administrador quiero ver una leyenda de ayuda más clara sobre
  el campo Código/SKU al dar de alta un producto, para entender qué es
  ese campo sin tecnicismos de formato.
- H3: Como Administrador quiero que la acción de ver el detalle de una
  venta se represente con un ícono y abra un modal real (con fondo
  superpuesto y cierre mediante un ícono de cierre) que muestre los
  productos de esa venta, para identificar la acción de un vistazo y
  consultar el detalle sin que se confunda con el resto del listado.
- H4: Como Administrador quiero elegir el campo por el cual buscar
  clientes (Nombre, Apellido o DNI) desde un menú desplegable junto a un
  input de valor, para filtrar de forma más precisa que con un único
  campo de texto genérico.

## Requisitos funcionales (criterios de aceptación en EARS)

### Modificación de Cliente (H1)

- RF-1: SI el Administrador busca por DNI a un cliente en estado
  Inactivo desde la pantalla de Modificar Cliente, ENTONCES EL SISTEMA
  informará que el cliente está Inactivo y no puede modificarse, sin
  mostrar el formulario precargado con sus datos ni el botón de guardar.
- RF-2: SI se solicita guardar cambios sobre un cliente en estado
  Inactivo, ENTONCES EL SISTEMA rechazará la operación a nivel de API y
  no persistirá ningún cambio, aun si la solicitud no pasa por la
  pantalla de edición.
- RF-3: EL SISTEMA seguirá permitiendo buscar y editar sin restricciones
  a los clientes en estado Activo (comportamiento sin cambios respecto
  de [[003-modificacion-cliente]]).

### Alta de Producto (H2)

- RF-4: EL SISTEMA mostrará el texto de ayuda "Identificador único del
  producto" debajo del campo Código/SKU en la pantalla de Alta de
  Producto, en reemplazo del texto "Cualquier texto, sin espacios al
  inicio/fin".
- RF-5: EL SISTEMA no modificará la validación de formato del campo
  Código/SKU ya vigente en [[005-alta-producto]]; el cambio es
  únicamente del texto de ayuda.

### Listado de Ventas (H3)

- RF-6: CUANDO el Administrador presiona el ícono de ver detalle de una
  venta en el listado, EL SISTEMA abrirá un modal con fondo superpuesto
  que oscurece el resto de la pantalla y muestra los datos de la venta
  y la lista de sus productos.
- RF-7: EL SISTEMA representará la acción de ver detalle con un ícono
  gráfico en formato SVG, no con un emoji ni con texto literal (ej.
  "Ver" u "ojo").
- RF-8: EL SISTEMA permitirá cerrar el modal mediante un botón con un
  ícono de cierre ("X"), además de cualquier otro mecanismo de cierre
  ya existente.
- RF-9: MIENTRAS el modal esté abierto, EL SISTEMA impedirá interactuar
  con los elementos del listado que queden detrás del fondo superpuesto.

### Listado de Clientes (H4)

- RF-10: EL SISTEMA mostrará en la pantalla de Listado de Clientes un
  menú desplegable para elegir el campo de búsqueda entre Nombre,
  Apellido y DNI, con Nombre seleccionado por defecto, junto a un input
  de texto para el valor a buscar.
- RF-11: CUANDO el Administrador ejecuta la búsqueda, EL SISTEMA
  filtrará los clientes comparando el valor ingresado únicamente contra
  el campo elegido en el desplegable, sin compararlo contra los otros
  dos campos.
- RF-12: EL SISTEMA mantendrá, para el campo elegido, el mismo criterio
  de coincidencia parcial e insensible a mayúsculas y tildes ya vigente
  en [[004-listar-clientes]] (RF-3/RF-4), aplicado ahora solo al campo
  seleccionado.
- RF-13: CUANDO el Administrador cambia el campo elegido en el
  desplegable, EL SISTEMA no disparará una nueva búsqueda
  automáticamente; el nuevo campo se aplica recién la próxima vez que
  se presiona Buscar.
- RF-14: SI el input de valor está vacío al presionar Buscar
  (cualquiera sea el campo elegido), ENTONCES EL SISTEMA mostrará el
  listado completo de clientes, igual que en la vista inicial
  (equivalente a RF-7 de [[004-listar-clientes]]).
- RF-15: EL SISTEMA conservará el resto del comportamiento ya definido
  en [[004-listar-clientes]]: paginación de 20 resultados, inclusión de
  clientes Activos e Inactivos, mensaje de "no se encontraron
  resultados" y reinicio a la página 1 al aplicar un nuevo filtro.

## Requisitos no funcionales
- Todos los mensajes dirigidos al Administrador (aviso de cliente
  Inactivo, leyenda del SKU) deben estar en español, mismo criterio que
  el resto de la aplicación.
- El ícono SVG de ver detalle y el ícono de cierre del modal deben tener
  un `aria-label` descriptivo, igual que hoy lo tiene el botón con el
  emoji.

## Casos límite
- Un cliente Inactivo con un DNI que también coincide parcialmente con
  otro cliente Activo: solo se bloquea la edición del Inactivo, el
  Activo se edita con normalidad.
- Se intenta guardar cambios sobre un cliente que era Activo al momento
  de cargar el formulario pero pasó a Inactivo mientras tanto (por una
  baja concurrente): la API rechaza el guardado igual (RF-2), aunque la
  pantalla no lo haya anticipado.
- Buscar en el Listado de Clientes con el campo "DNI" seleccionado y un
  valor parcial (ej. "301112"): sigue encontrando por coincidencia
  parcial contra el DNI, sin comparar ese valor contra Nombre o
  Apellido.
- Buscar con el campo "Nombre" seleccionado un valor que también
  coincide con el Apellido de otro cliente: ese otro cliente no aparece
  en el resultado, porque el filtro compara solo contra el campo
  elegido (RF-11).
- El Administrador cambia el campo del desplegable estando en una
  página distinta de la primera, pero no presiona Buscar: la paginación
  no se altera hasta que se ejecute una nueva búsqueda.
- El modal de detalle de venta se abre para una venta con un solo
  producto o con varios: la tabla de productos ya existente se sigue
  mostrando igual, solo cambian el ícono de apertura y el estilo del
  modal.

## Fuera de alcance
- Reactivar automáticamente a un cliente Inactivo desde la pantalla de
  edición (ya descartado explícitamente en [[014-correcciones-cliente]]).
- Cambios al flujo de Baja de Cliente ([[002-baja-cliente]]).
- Cambios a la validación de formato del SKU; solo se reemplaza el
  texto de ayuda (RF-5).
- Agregar una opción "Todos los campos" al desplegable de búsqueda de
  clientes que reproduzca el comportamiento combinado anterior.
- Agregar búsqueda por email o teléfono al desplegable de clientes.
- Rediseñar otros íconos de la aplicación fuera del de ver detalle de
  venta.
- Cambios al contenido o formato de los datos que muestra el modal de
  detalle de venta (ya cubiertos por [[018-mejoras-venta-cliente]]);
  esta spec solo corrige su presentación como modal y el ícono que lo
  abre.

## Criterios de finalización
- Buscar por DNI a un cliente Inactivo en Modificar Cliente informa que
  no puede modificarse y no muestra el formulario ni el botón de
  guardar (RF-1); un intento de guardado vía API sobre un cliente
  Inactivo es rechazado (RF-2); los clientes Activos se editan sin
  cambios (RF-3).
- La pantalla de Alta de Producto muestra "Identificador único del
  producto" como ayuda del campo Código/SKU, sin cambios en su
  validación (RF-4, RF-5).
- El listado de Ventas muestra un ícono SVG para ver detalle que abre
  un modal con fondo superpuesto, bloquea la interacción con el
  listado de fondo mientras está abierto, y se cierra con un ícono de
  cierre (RF-6 a RF-9).
- El listado de Clientes ofrece un desplegable (Nombre/Apellido/DNI,
  Nombre por defecto) junto a un input de valor; la búsqueda filtra
  solo contra el campo elegido, con coincidencia parcial e insensible a
  mayúsculas/tildes; cambiar el campo no dispara la búsqueda sola; un
  valor vacío al buscar muestra el listado completo; se conserva
  paginación, inclusión de Activos/Inactivos y mensaje de sin
  resultados (RF-10 a RF-15).
- Todos los criterios de aceptación de H1 a H4 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. El texto exacto del aviso de cliente
Inactivo en Modificar Cliente y el diseño puntual del ícono SVG de ver
detalle y del ícono de cierre quedan para el plan de implementación
(no son decisiones de negocio de esta spec).
