# Spec 006 — Baja de Producto

## Contexto y objetivo
El sistema ya permite dar de alta productos ([[005-alta-producto]]), pero
el modelo de producto todavía no tiene ningún concepto de estado (no
existía la necesidad hasta ahora). El objetivo de esta feature es que el
Administrador pueda dar de baja (inactivar) un producto existente
localizándolo por su SKU, sin eliminar su registro, para retirarlo del
catálogo y discontinuar su venta. Esta spec introduce el estado
Activo/Inactivo del producto (análogo al de Cliente en
[[001-alta-cliente]]).

## Usuarios
- **Administrador**: único rol que ejecuta la baja de productos en esta
  feature.

## Historias de usuario

### HU-PROD-02: Baja de Producto
Como Administrador
Quiero dar de baja un producto
Para retirarlo del catálogo y discontinuar su venta.

## Requisitos funcionales

### RF-1: Búsqueda de producto por SKU
El sistema deberá permitir al Administrador buscar un producto ingresando
su SKU, como paso previo a la baja.

- CUANDO el Administrador ingresa un SKU y solicita la búsqueda, EL
  SISTEMA deberá localizar un producto registrado cuyo SKU, comparado sin
  distinguir mayúsculas de minúsculas, coincida con el ingresado.

### RF-2: Producto no encontrado
- SI no existe ningún producto registrado cuyo SKU coincida con el valor
  buscado, ENTONCES EL SISTEMA deberá advertir que el producto no fue
  encontrado y no deberá habilitar ninguna acción de baja.

### RF-3: Confirmación previa a la baja
- CUANDO la búsqueda localiza un producto en estado Activo, EL SISTEMA
  deberá solicitar al Administrador que confirme la baja antes de
  modificar su estado.

### RF-4: Ejecución de la baja
- CUANDO el Administrador confirma la baja de un producto en estado
  Activo, EL SISTEMA deberá cambiar su estado a Inactivo, mostrar el
  mensaje "Producto dado de baja exitosamente" y conservar el resto de
  sus datos, incluido el stock, sin modificarlos.

### RF-5: Cancelación de la confirmación
- CUANDO el Administrador cancela la confirmación de baja, EL SISTEMA no
  deberá modificar el estado del producto ni ningún otro dato del
  registro.

### RF-6: Baja de producto ya inactivo
- SI el producto localizado ya se encuentra en estado Inactivo, ENTONCES
  EL SISTEMA deberá advertir que el producto ya se encuentra dado de
  baja, y no deberá solicitar confirmación ni modificar su estado.

### RF-7: Persistencia sin eliminación
- EL SISTEMA nunca eliminará el registro de un producto como parte del
  proceso de baja; el proceso de baja únicamente podrá modificar el campo
  de estado del producto.

### RF-8: Ausencia de re-verificación de estado al confirmar
El sistema no deberá volver a comprobar el estado del producto en el
momento de confirmar la baja; deberá aplicar el cambio directamente sobre
el estado obtenido durante la búsqueda (RF-1), asumiendo un único
Administrador operando el sistema (mismo criterio ya resuelto en
[[002-baja-cliente]]).

- CUANDO el Administrador confirma la baja de un producto que fue
  localizado como Activo en la búsqueda, EL SISTEMA deberá cambiar su
  estado a Inactivo sin volver a consultar su estado actual antes de
  aplicar el cambio.

### RF-9: Baja permitida sin importar el stock
- EL SISTEMA permitirá dar de baja a un producto Activo sin importar la
  cantidad de stock que tenga cargada; no exigirá que el stock sea cero
  como condición para la baja.

### RF-10: SKU liberado tras la baja
- EL SISTEMA permitirá registrar un nuevo producto con el mismo SKU de
  otro producto que se encuentra Inactivo, sin considerarlo un conflicto
  de duplicado. Esto implica que la detección de SKU duplicado del alta
  ([[005-alta-producto]] RF-5) deja de bloquear contra productos
  Inactivos a partir de esta spec; sigue bloqueando contra otro producto
  Activo.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español.
- El cambio de estado debe persistirse únicamente en la base de datos
  oficial del proyecto; no se admite almacenamiento local ad-hoc.

## Casos límite
- Intento de dar de baja a un producto ya Inactivo: bloqueado por RF-6,
  sin llegar a pedir confirmación.
- El Administrador cancela la confirmación de baja: el producto permanece
  sin cambios (RF-5).
- Producto con stock alto (ej. 500 unidades) dado de baja: se permite
  igual, y el stock queda intacto en 500 tras la baja (RF-4, RF-9).
- Alta de un nuevo producto reutilizando el SKU de un producto Inactivo:
  se permite (RF-10), a diferencia de reutilizar el SKU de un producto
  Activo, que sigue bloqueado como duplicado.
- Producto encontrado y confirmado para baja, pero cuyo estado cambió a
  Inactivo por otra vía entre la búsqueda y la confirmación (condición de
  carrera): el sistema no re-verifica el estado al confirmar; aplica la
  baja directamente sobre el estado obtenido en la búsqueda (RF-8).

## Fuera de alcance
- Reactivación de un producto Inactivo (volver a estado Activo).
- Integración con un módulo de Ventas (deshabilitar la selección del
  producto en nuevas ventas): no existe todavía ningún módulo de Ventas en
  el sistema; queda para cuando ese módulo se construya.
- Edición de los datos del producto durante o fuera del proceso de baja.
- Listado, búsqueda general o filtrado de productos más allá de la
  búsqueda puntual por SKU necesaria para iniciar la baja.
- Eliminación física del registro del producto.
- Registro de motivo o comentario asociado a la baja.
- Historial de auditoría de bajas.
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Modificación del stock como parte de la baja (RF-4 ya establece que el
  stock no se toca).

## Criterios de finalización
- Un Administrador puede buscar un producto Activo por SKU y darlo de
  baja tras confirmar, quedando su estado en Inactivo sin perder el resto
  de sus datos ni el stock.
- Buscar un SKU sin producto asociado advierte "no encontrado" y no
  habilita ninguna acción de baja (RF-2).
- Intentar dar de baja a un producto ya Inactivo advierte que ya se
  encuentra dado de baja, sin modificar su estado (RF-6).
- Cancelar la confirmación de baja no produce ningún cambio en el
  producto (RF-5).
- Un producto Activo con cualquier nivel de stock puede darse de baja sin
  restricciones (RF-9).
- Un alta nueva puede reutilizar el SKU de un producto Inactivo, pero no
  el de uno Activo (RF-10).
- Todos los criterios de aceptación de HU-PROD-02 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Todas las aclaraciones fueron resueltas y
volcadas a los requisitos correspondientes (RF-9, RF-10, y la exclusión
del módulo de Ventas en "Fuera de alcance").
