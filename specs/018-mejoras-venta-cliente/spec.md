# Spec 018 — Mejoras sobre Venta y Cliente

## Contexto y objetivo
Esta spec agrupa cuatro correcciones puntuales recibidas sobre features
ya implementadas de Venta y Cliente, en la misma línea que
[[013-validacion-amigable-formularios]] y [[014-correcciones-cliente]]
(feedback directo de uso, no una nueva historia de negocio):

1. **Registrar Venta** ([[009-alta-venta]], [[011-modificacion-venta]]):
   hoy se puede quitar un producto del detalle recién en "Modificar
   Venta" (edición de un Borrador ya registrado), no en la pantalla
   donde se arma la venta por primera vez. Además, esa pantalla solo
   ofrece "Registrar venta" (que la deja en "Borrador", sin descontar
   stock); para dejarla "Confirmada" hay que ir a "Modificar Venta" y
   cerrarla ahí. Se agrega, en la misma pantalla de registro, la
   posibilidad de quitar un producto del detalle antes de guardar, y una
   segunda acción ("Confirmar venta") que registra la venta ya
   "Confirmada" en un solo paso, sin pasar por "Borrador".
2. **Listar Ventas** ([[012-listar-ventas]]): el listado ya muestra los
   datos resumidos de cada venta (RF-10 de esa spec excluye
   explícitamente el detalle de ítems), pero no hay forma de ver ese
   detalle sin ir a buscar la venta en otra pantalla. Se agrega una
   acción por fila para verlo sin salir del listado.
3. **Anular Venta, Listar Ventas y Modificar Venta**: la fecha de venta
   se muestra hoy como la fecha y hora completas (formato ISO crudo).
   Se simplifica a solo año-mes-día en las tres pantallas.
4. **Modificar Cliente** ([[003-modificacion-cliente]]): el guardado
   pide una confirmación adicional en un modal aparte después de tocar
   "Guardar cambios" (RF-8 a RF-10 de esa spec). Se elimina ese paso: el
   formulario se guarda directamente si es válido.

## Usuarios
- **Administrador**: único rol que opera estas pantallas.

## Historias de usuario

### HU-VEN-07: Registrar y confirmar venta desde la misma pantalla
Como Administrador
Quiero registrar una venta
Para mejorar mi experiencia de usuario.

### HU-VEN-08: Ver el detalle de una venta desde el listado
Como Administrador
Quiero listar las ventas
Para observar el detalle de una venta específica.

### HU-VEN-09: Fecha de venta en formato año-mes-día
Como Administrador
Quiero anular una venta
Para limpiar la UI.

### HU-CLI-05: Guardado directo al modificar un cliente
Como Administrador
Quiero modificar un cliente
Para agilizar el proceso de guardado.

## Requisitos funcionales (criterios de aceptación en EARS)

### HU-VEN-07 — Registrar y confirmar venta

#### RF-1: Quitar un producto del detalle antes de guardar
- CUANDO el Administrador quita un ítem del detalle que está armando en
  la pantalla de registro de venta (antes de guardarla), EL SISTEMA
  deberá eliminarlo de la lista y recalcular el total automáticamente,
  igual que ya ocurre al editar el detalle de un Borrador en
  [[011-modificacion-venta]] RF-5.

#### RF-2: Dos acciones disponibles para guardar la venta
- CUANDO el Administrador armó el detalle de la venta con un cliente
  Activo válido y al menos un ítem válido, EL SISTEMA deberá ofrecer
  dos acciones distintas: "Registrar venta" y "Confirmar venta".

#### RF-3: "Registrar venta" sin cambios de comportamiento
- CUANDO el Administrador elige "Registrar venta", EL SISTEMA deberá
  crear la venta en estado "Borrador", sin descontar stock de ningún
  producto — mismo comportamiento ya vigente en
  [[011-modificacion-venta]] RF-1, editable después desde "Modificar
  Venta".

#### RF-4: "Confirmar venta" registra y cierra en un solo paso
- CUANDO el Administrador elige "Confirmar venta" con un detalle válido
  y stock disponible suficiente para cada ítem en ese momento, EL
  SISTEMA deberá crear la venta directamente en estado "Confirmada" —
  con su ID, fecha, cliente, detalle y total calculado— y descontar
  automáticamente del stock de cada producto la cantidad de su ítem
  correspondiente, en la misma operación.

#### RF-5: Stock insuficiente al confirmar
- SI al elegir "Confirmar venta" la cantidad solicitada de algún ítem
  supera el stock disponible de ese producto en ese momento, ENTONCES
  EL SISTEMA deberá advertir que no hay stock suficiente para completar
  la operación y no deberá crear ninguna venta ni descontar stock de
  ningún producto.

#### RF-6: Producto dado de baja entre agregarlo y confirmar
- SI al elegir "Confirmar venta" algún producto del detalle pasó a
  estado Inactivo después de haber sido agregado, ENTONCES EL SISTEMA
  deberá advertir que el producto no está disponible para la venta y no
  deberá crear ninguna venta.

#### RF-7: Confirmación previa a cada acción
- CUANDO el Administrador presiona "Registrar venta" o "Confirmar
  venta", EL SISTEMA deberá solicitar que confirme esa acción
  puntual antes de ejecutarla, indicando su efecto (una deja la venta
  en Borrador; la otra descuenta stock de inmediato).

#### RF-8: Cancelación de la confirmación
- CUANDO el Administrador cancela la confirmación de cualquiera de las
  dos acciones, EL SISTEMA no deberá registrar ninguna venta ni
  modificar el stock de ningún producto.

### HU-VEN-08 — Ver detalle desde el listado

#### RF-9: Acción de ver detalle por fila
- EL SISTEMA deberá mostrar, en cada fila del listado de ventas, una
  acción para ver el detalle completo de esa venta.

#### RF-10: Detalle en un panel superpuesto
- CUANDO el Administrador presiona la acción de ver detalle de una
  venta, EL SISTEMA deberá mostrar, en un panel superpuesto a la
  pantalla de listado (sin navegar a otra pantalla ni perder los
  filtros o la página aplicados), el detalle completo de esa venta:
  cada ítem (producto, cantidad, precio unitario, subtotal), el total,
  la fecha, el cliente y el estado.

#### RF-11: Cierre del panel de detalle
- CUANDO el Administrador cierra el panel de detalle, EL SISTEMA deberá
  volver a mostrar el listado exactamente como estaba antes de abrirlo
  (misma página, mismos filtros aplicados).

### HU-VEN-09 — Formato de fecha

#### RF-12: Fecha en año-mes-día
- EL SISTEMA deberá mostrar la fecha de una venta en formato
  año-mes-día (ej. "2026-09-01"), sin hora, en las pantallas de Anular
  Venta, Listar Ventas y Modificar Venta.

### HU-CLI-05 — Guardado directo

#### RF-13: Guardado sin confirmación adicional
- CUANDO el Administrador presiona "Guardar cambios" en la
  modificación de un cliente y el formulario no tiene errores de
  validación, EL SISTEMA deberá persistir los cambios directamente, sin
  solicitar ninguna confirmación adicional. Esto reemplaza a RF-8, RF-9
  y RF-10 de [[003-modificacion-cliente]] (confirmación previa al
  guardado), que quedan sin efecto para esta pantalla.

#### RF-14: Los errores de validación siguen bloqueando el guardado
- SI el formulario tiene errores de validación al presionar "Guardar
  cambios", ENTONCES EL SISTEMA deberá mostrarlos y no deberá guardar
  ningún cambio — mismo comportamiento ya vigente, sin relación con la
  confirmación eliminada.

## Requisitos no funcionales
- Todos los mensajes y textos de confirmación dirigidos al
  Administrador deben estar en español.
- La creación de una venta ya "Confirmada" (RF-4) debe persistirse de
  forma atómica: si no puede completarse por stock insuficiente (RF-5)
  o producto inactivo (RF-6), no debe quedar ninguna venta creada ni
  stock descontado (mismo criterio de atomicidad que
  [[009-alta-venta]] y [[011-modificacion-venta]]).
- El cambio de formato de fecha (RF-12) es solo de presentación: no
  cambia el dato almacenado ni el criterio de orden o de filtrado por
  fecha ya vigente en [[012-listar-ventas]].

## Casos límite
- Detalle con un solo ítem: quitarlo (RF-1) deja el detalle vacío,
  igual que hoy es posible al editar un Borrador; ambas acciones (RF-2)
  quedan deshabilitadas hasta agregar al menos un ítem de nuevo.
- "Confirmar venta" con dos problemas a la vez (ej. stock insuficiente
  en un ítem y otro producto dado de baja en otro): se advierten ambos
  en el mismo intento, sin crear ninguna venta (mismo criterio que
  [[009-alta-venta]] RF-12).
- El Administrador cancela la confirmación de "Confirmar venta" después
  de armar todo el detalle: no se crea ninguna venta ni se modifica
  stock (RF-8); el detalle armado permanece en pantalla para reintentar
  o corregir.
- Ver el detalle de una venta cuyo ID ya no existe al momento de
  consultarlo (por ejemplo, situación de carrera extrema): se informa
  que la venta no fue encontrada, sin romper el listado de fondo.
- Ver el detalle de una venta con el detalle vacío (Borrador sin
  ítems, ver [[011-modificacion-venta]] RF-11): el panel muestra el
  total en cero y ninguna fila de ítems, sin error.
- Cliente Activo o Inactivo al modificarlo: el guardado directo (RF-13)
  no cambia ninguna otra validación ya vigente en
  [[003-modificacion-cliente]] (DNI duplicado contra otro cliente
  Activo, formato de campos, etc.), solo elimina el paso de
  confirmación previa.

## Fuera de alcance
- Cualquier cambio al estado "Borrador" en sí mismo o a la pantalla
  "Modificar Venta" ([[011-modificacion-venta]]): sigue funcionando
  igual para las ventas registradas con la acción "Registrar venta".
- Quitar la confirmación previa en otras pantallas (Alta de Cliente,
  Alta/Baja de Producto, Anular Venta, etc.); solo se elimina en
  Modificar Cliente (RF-13).
- Editar el detalle de una venta ya "Confirmada" desde el listado o
  desde el panel de detalle (RF-10 es de solo lectura).
- Exportar o imprimir el detalle mostrado en el panel (RF-10).
- Cambiar el criterio de orden, filtrado o paginación del listado de
  ventas ([[012-listar-ventas]] sigue vigente sin cambios).
- Permitir editar o eliminar más de un ítem a la vez del detalle
  (RF-1 aplica de a un ítem por vez, igual que "Quitar" en
  [[011-modificacion-venta]]).
- Autenticación y gestión de roles de usuario (se asume que el sistema
  ya identifica quién opera como Administrador).

## Criterios de finalización
- Un Administrador puede quitar un producto ya agregado al detalle
  antes de guardar la venta, en la pantalla de registro (RF-1).
- Un Administrador puede elegir entre "Registrar venta" (queda en
  Borrador, sin descontar stock) y "Confirmar venta" (queda Confirmada,
  descontando stock en el mismo paso), cada una con su propia
  confirmación previa (RF-2 a RF-8).
- "Confirmar venta" rechaza la operación completa, sin crear nada, si
  hay stock insuficiente o un producto inactivo en el detalle (RF-5,
  RF-6).
- Cada fila del listado de ventas tiene una acción para ver el detalle
  completo de esa venta en un panel superpuesto, sin perder el listado
  de fondo (RF-9 a RF-11).
- Anular Venta, Listar Ventas y Modificar Venta muestran la fecha de
  venta en formato año-mes-día, sin hora (RF-12).
- Modificar Cliente guarda los cambios directamente al presionar
  "Guardar cambios" cuando el formulario es válido, sin ningún modal de
  confirmación adicional (RF-13); un formulario inválido sigue
  bloqueando el guardado (RF-14).
- Todos los criterios de aceptación de HU-VEN-07, HU-VEN-08, HU-VEN-09 y
  HU-CLI-05, y los casos límite listados, están cubiertos por pruebas
  automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Se resolvió que: "Registrar venta" y
"Confirmar venta" son dos acciones separadas y ambas quedan disponibles
(no se reemplaza una por la otra); el detalle de venta se ve en un
modal, no en una pantalla aparte; el formato de fecha año-mes-día se
aplica en las tres pantallas de venta que muestran fecha (Anular,
Listar y Modificar), no solo en Anular; y la eliminación de la
confirmación al modificar cliente se refiere puntualmente al modal
"¿Confirmás guardar estos cambios?" que aparece hoy tras presionar
"Guardar cambios".
