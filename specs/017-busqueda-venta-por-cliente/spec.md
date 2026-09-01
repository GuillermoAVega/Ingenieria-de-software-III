# Spec 017 — Búsqueda de Venta por Cliente en Anular y Modificar Venta

## Contexto y objetivo
Hoy, tanto Anular Venta ([[010-anular-venta]]) como Modificar Venta
([[011-modificacion-venta]]) localizan la venta a operar pidiendo su ID
exacto. Esto exige que el Administrador ya conozca ese ID de antemano.
El objetivo de esta spec es reemplazar esa búsqueda por ID: el
Administrador ingresa el DNI del cliente, ve la lista de sus ventas, y
elige sobre cuál actuar (anular una, o editar una que esté en Borrador).

El listado general de ventas ([[012-listar-ventas]]) muestra a propósito
solo ventas "Confirmada", pensado como historial de operaciones
concretadas. Esta spec necesita, en cambio, ver también ventas en
"Borrador" (para poder editarlas) y no reutiliza ese mecanismo: agrega
uno propio para buscar las ventas de un cliente puntual por su DNI, sin
modificar [[012-listar-ventas]].

## Usuarios
- **Administrador**: único rol que anula y modifica ventas en esta
  feature.

## Historias de usuario

### HU-VEN-06: Búsqueda de venta por cliente
Como Administrador
Quiero buscar las ventas de un cliente por su DNI y elegir sobre cuál
actuar
Para ubicar la venta correcta sin tener que conocer su ID de antemano.

## Requisitos funcionales

### RF-1: Búsqueda de ventas de un cliente por DNI
El campo de búsqueda por ID de venta se reemplaza, tanto en Anular
Venta como en Modificar Venta, por un campo de búsqueda por DNI de
cliente.

- CUANDO el Administrador ingresa un DNI y solicita la búsqueda, EL
  SISTEMA deberá localizar al cliente cuyo DNI coincide exactamente y
  traer sus ventas registradas.

### RF-2: Cliente no encontrado
- SI no existe ningún cliente registrado con el DNI ingresado,
  ENTONCES EL SISTEMA deberá advertir que el cliente no fue encontrado,
  tanto en Anular Venta como en Modificar Venta.

### RF-3: En Anular Venta, solo se listan las ventas Confirmada
- EL SISTEMA deberá mostrar, en la pantalla de Anular Venta,
  únicamente las ventas del cliente que se encuentren en estado
  "Confirmada" (las únicas que pueden anularse según
  [[010-anular-venta]]).

### RF-4: Sin ventas Confirmada para anular
- SI el cliente encontrado no tiene ninguna venta en estado
  "Confirmada", ENTONCES EL SISTEMA deberá informarlo, en vez de
  mostrar una lista vacía sin explicación.

### RF-5: Elegir una venta para anular
- CUANDO el Administrador elige una de las ventas listadas en Anular
  Venta, EL SISTEMA deberá mostrar la confirmación ya definida en
  [[010-anular-venta]] antes de anularla.

### RF-6: En Modificar Venta se listan todas las ventas del cliente
- EL SISTEMA deberá mostrar, en la pantalla de Modificar Venta, todas
  las ventas del cliente sin importar su estado (Borrador, Confirmada
  o Anulada), junto con ese estado.

### RF-7: Sin ventas registradas para el cliente (Modificar Venta)
- SI el cliente encontrado no tiene ninguna venta registrada, ENTONCES
  EL SISTEMA deberá informarlo, en vez de mostrar una lista vacía sin
  explicación.

### RF-8: Solo las ventas en Borrador son editables
- EL SISTEMA deberá habilitar la acción de editar (ícono de lápiz)
  únicamente sobre las ventas listadas que estén en estado "Borrador";
  sobre las demás, esa acción no debe estar disponible.

### RF-9: Elegir una venta en Borrador para editar
- CUANDO el Administrador presiona el ícono de editar sobre una venta
  en "Borrador", EL SISTEMA deberá cargar su detalle completo y
  mostrar la vista de edición ya definida en
  [[011-modificacion-venta]].

### RF-10: Verificación de estado al momento de editar
- SI, al presionar el ícono de editar, la venta ya no se encuentra en
  estado "Borrador" (por ejemplo, porque se cerró o anuló entre la
  búsqueda y ese clic), ENTONCES EL SISTEMA deberá advertir que la
  venta ya no admite modificaciones, mismo criterio ya definido en
  [[011-modificacion-venta]] RF-4, sin abrir la vista de edición.

### RF-11: Orden de las ventas listadas
- EL SISTEMA deberá mostrar las ventas de un cliente ordenadas por
  fecha, de la más reciente a la más antigua, tanto en Anular Venta
  como en Modificar Venta (mismo criterio que [[012-listar-ventas]]
  RF-1).

## Requisitos no funcionales
- Todos los mensajes dirigidos al Administrador deben estar en
  español.
- La búsqueda debe leer únicamente de la base de datos oficial del
  proyecto.

## Casos límite
- Un cliente con varias ventas "Confirmada": todas aparecen listadas
  en Anular Venta; el Administrador elige cuál anular (RF-3, RF-5).
- Un cliente con ventas en los tres estados: en Modificar Venta
  aparecen las tres, pero el ícono de editar solo funciona sobre la
  que está en "Borrador" (RF-6, RF-8).
- Un cliente sin ninguna venta registrada: se informa en ambas
  pantallas, sin mostrar una lista vacía sin explicación (RF-4, RF-7).
- Un cliente en estado Inactivo con ventas "Confirmada": igual puede
  buscarse y sus ventas aparecen normalmente en Anular Venta; la baja
  del cliente no afecta sus ventas ya registradas.
- Entre que se lista una venta en "Borrador" y se presiona su ícono de
  editar, otro proceso la cierra o la anula: al presionar el ícono, se
  advierte que ya no admite modificaciones, sin abrir la vista de
  edición (RF-10).
- Un DNI con formato inválido (letras, longitud incorrecta): se trata
  igual que un DNI no encontrado (RF-2).

## Fuera de alcance
- Filtro por rango de fechas u otro criterio dentro de esta búsqueda
  por cliente (ya existe, para el historial general, en
  [[012-listar-ventas]]).
- Paginación de la lista de ventas de un cliente.
- Cambios al selector de producto por nombre/descripción
  ([[016-selector-producto-venta]]).
- Cambios a las reglas de negocio de anular
  ([[010-anular-venta]]) o de editar/cerrar
  ([[011-modificacion-venta]]) ventas: siguen exactamente igual, esta
  spec solo cambia cómo se llega a elegir la venta sobre la que se
  actúa.
- Cambios a [[012-listar-ventas]] (su filtro y su alcance de Confirmada
  únicamente permanecen igual).

## Criterios de finalización
- En Anular Venta y en Modificar Venta, el Administrador busca por DNI
  del cliente en vez de por ID de venta (RF-1, RF-11).
- Un DNI sin cliente registrado informa que no fue encontrado, en
  ambas pantallas (RF-2).
- Anular Venta solo lista las ventas "Confirmada" del cliente,
  informando si no tiene ninguna (RF-3, RF-4); elegir una muestra la
  confirmación ya existente antes de anularla (RF-5).
- Modificar Venta lista todas las ventas del cliente con su estado,
  informando si no tiene ninguna (RF-6, RF-7); el ícono de editar solo
  funciona sobre las que están en Borrador (RF-8), verificando de nuevo
  el estado al presionarlo (RF-10) antes de abrir la edición ya
  existente (RF-9).
- Todos los criterios de aceptación de HU-VEN-06 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes.
