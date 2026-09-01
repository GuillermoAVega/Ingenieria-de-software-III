# Spec 007 — Modificación de Producto

## Contexto y objetivo
El sistema ya permite dar de alta ([[005-alta-producto]]) y dar de baja
([[006-baja-producto]]) productos, pero no hay forma de corregir sus datos
cuando cambian (precio, stock, descripción) o fueron mal cargados. El
objetivo de esta feature es que el Administrador pueda editar los datos de
un producto existente (localizándolo por su SKU), para mantenerlos
actualizados sin necesidad de volver a darlo de alta.

## Usuarios
- **Administrador**: único rol que ejecuta la modificación de productos en
  esta feature.

## Historias de usuario

### HU-PROD-03: Modificación de Producto
Como Administrador
Quiero editar los datos de un producto
Para actualizar su precio, descripción o información general.

## Requisitos funcionales

### RF-1: Búsqueda de producto por SKU para editar
El sistema deberá permitir al Administrador buscar un producto ingresando
su SKU, como paso previo a la edición.

- CUANDO el Administrador ingresa un SKU y solicita la búsqueda, EL
  SISTEMA deberá localizar al producto registrado cuyo SKU, comparado sin
  distinguir mayúsculas de minúsculas, coincida con el ingresado, sin
  importar si su estado es Activo o Inactivo.

### RF-2: Producto no encontrado
- SI no existe ningún producto registrado con el SKU buscado, ENTONCES EL
  SISTEMA deberá advertir que el producto no fue encontrado y no deberá
  mostrar ningún formulario de edición.

### RF-3: Formulario de edición con los datos actuales
- CUANDO el sistema localiza un producto, EL SISTEMA deberá mostrar un
  formulario con sus datos actuales (Nombre, Marca, Descripción, Precio
  unitario y Stock) para que el Administrador los modifique. El SKU se
  muestra como referencia, pero no es un campo editable.

### RF-4: Validación de campos con las reglas del alta
El sistema deberá validar los campos editados con las mismas reglas de
formato, obligatoriedad y recorte que rigen el alta de producto (RF-2 a
RF-4 y RF-7 de [[005-alta-producto]]): Nombre, Marca, Precio unitario y
Stock son obligatorios; la Descripción es opcional; el Precio unitario
debe ser un número positivo; el Stock debe ser un entero positivo.

- CUANDO el Administrador envía el formulario de edición con algún campo
  obligatorio vacío o con Precio unitario/Stock inválidos, ENTONCES EL
  SISTEMA deberá advertir el campo afectado y no deberá guardar ningún
  cambio del intento.

### RF-5: Reporte completo de errores por intento
- CUANDO el formulario de edición se envía con más de un campo inválido
  y/o vacío a la vez, ENTONCES EL SISTEMA deberá mostrar todas las
  advertencias correspondientes en el mismo intento, sin guardar ningún
  cambio.

### RF-6: Guardado directo de cambios válidos
- CUANDO el Administrador envía el formulario de edición con todos los
  campos válidos, EL SISTEMA deberá guardar los cambios de inmediato y
  mostrar el mensaje "Producto modificado exitosamente", sin requerir un
  paso adicional de confirmación.

### RF-7: El SKU no es editable
- EL SISTEMA no permitirá modificar el SKU de un producto desde esta
  funcionalidad; el SKU con el que se localizó al producto (RF-1) sigue
  siendo su identificador después de guardar los cambios.

### RF-8: La edición no altera el estado del producto
- EL SISTEMA no modificará el estado (Activo/Inactivo) del producto como
  parte de la edición de sus datos.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español.
- Los cambios deben persistirse únicamente en la base de datos oficial
  del proyecto; no se admite almacenamiento local ad-hoc.
- Editar el Stock reemplaza directamente su valor por el ingresado (no es
  un movimiento incremental de entrada/salida de inventario), igual
  criterio que el resto de los campos numéricos editables.

## Casos límite
- Se edita un producto Inactivo: sus datos cambian, pero permanece
  Inactivo (RF-8).
- Precio unitario en cero o negativo: bloquea el intento completo, mismo
  mensaje que el alta (RF-4).
- Stock con decimales (ej. `5.5`): bloquea el intento completo, mismo
  mensaje que el alta (RF-4).
- Descripción vacía: válida, ya que es el único campo opcional (heredado
  del alta).
- Intento con múltiples errores a la vez (ej. precio negativo y stock con
  decimales): se muestran todas las advertencias en el mismo intento, sin
  guardar ningún cambio (RF-5).

## Fuera de alcance
- Cambiar el SKU del producto (RF-7 lo excluye explícitamente).
- Cambiar el estado del producto (alta o baja) desde esta funcionalidad
  — eso corresponde a [[005-alta-producto]] y [[006-baja-producto]].
- Integración con un módulo de Ventas (que el nuevo precio "se aplique" a
  una venta futura): no existe todavía ningún módulo de Ventas en el
  sistema.
- Movimientos de stock por entrada/salida de inventario (la edición
  reemplaza el valor de Stock directamente, no lleva un registro de
  movimientos).
- Historial de auditoría de cambios (qué campo cambió, cuándo, quién).
- Edición masiva de varios productos a la vez.
- Deshacer una edición ya guardada.
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Listado, búsqueda general o filtrado de productos más allá de la
  búsqueda puntual por SKU necesaria para iniciar la edición.

## Criterios de finalización
- Un Administrador puede buscar un producto (Activo o Inactivo) por SKU,
  editar sus datos (Nombre, Marca, Descripción, Precio unitario, Stock)
  con valores válidos, y ver los cambios persistidos de inmediato junto
  con el mensaje "Producto modificado exitosamente" (RF-6).
- Un intento de edición con campos inválidos y/o vacíos muestra todas las
  advertencias correspondientes en el mismo intento y no guarda ningún
  cambio (RF-4, RF-5).
- El SKU del producto nunca cambia como resultado de una edición (RF-7).
- El estado del producto no cambia como resultado de la edición (RF-8).
- Todos los criterios de aceptación de HU-PROD-03 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Todas las aclaraciones fueron resueltas y
volcadas a los requisitos correspondientes (RF-6, RF-7, RF-8, y la
exclusión del módulo de Ventas en "Fuera de alcance").
