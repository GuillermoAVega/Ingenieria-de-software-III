# Spec 016 — Selector de Producto por Nombre o Descripción en Venta

## Contexto y objetivo
Hoy, tanto para registrar una venta ([[009-alta-venta]]) como para agregar
productos al detalle de una venta en Borrador ([[011-modificacion-venta]]),
el Administrador arma cada ítem escribiendo manualmente el SKU exacto del
producto. Esto exige conocer o tener a mano el código de cada producto.
El objetivo de esta spec es reemplazar esa carga manual del SKU por un
selector: el Administrador escribe parte del Nombre o la Descripción del
producto, elige uno de una lista de coincidencias, y el sistema completa
el SKU (y el resto de los datos del ítem) automáticamente.

Esta spec **no modifica** [[008-listar-productos]]: ese listado y su
filtro (por Nombre o Código/SKU) quedan exactamente como están. El
mecanismo de búsqueda de esta spec es propio del selector de Venta,
busca además por Descripción, y es independiente del filtro general de
productos.

## Usuarios
- **Administrador**: único rol que registra y modifica ventas en esta
  feature.

## Alcance
Aplica a los dos lugares donde hoy se arma el detalle de una venta
escribiendo un SKU manualmente:
- El armado de ítems al registrar una venta (`VentaForm.jsx`,
  [[009-alta-venta]]).
- El armado de ítems al editar el detalle de una venta en Borrador
  (`VentaEdicionForm.jsx`, [[011-modificacion-venta]]).

## Historias de usuario

### HU-VEN-05: Selección de producto por nombre o descripción
Como Administrador
Quiero elegir el producto por su nombre o descripción en vez de escribir
su SKU
Para armar el detalle de una venta más rápido, sin memorizar códigos.

## Requisitos funcionales

### RF-1: Búsqueda de producto por Nombre o Descripción
El campo de SKU manual del armado de ítems se reemplaza por un campo de
búsqueda de producto.

- CUANDO el Administrador escribe un criterio en el campo de búsqueda
  de producto, EL SISTEMA deberá buscar productos en estado **Activo**
  cuyo Nombre o Descripción contengan ese criterio, y mostrarlos como
  opciones en un desplegable debajo del campo.

### RF-2: Coincidencia parcial e insensible a mayúsculas y tildes
- EL SISTEMA deberá considerar una coincidencia cuando el criterio esté
  contenido en cualquier parte del Nombre o de la Descripción del
  producto, sin exigir que coincida con el valor completo, y sin
  distinguir mayúsculas de minúsculas ni tildes (mismo criterio ya
  usado en [[008-listar-productos]] RF-3/RF-4).

### RF-3: Exclusión de productos Inactivos
- EL SISTEMA no deberá incluir productos en estado Inactivo entre las
  opciones del desplegable, aunque su Nombre o Descripción coincidan
  con el criterio buscado.

### RF-4: Selección completa el ítem automáticamente
- CUANDO el Administrador elige una opción del desplegable, EL SISTEMA
  deberá completar automáticamente el SKU, el Nombre, el precio
  unitario y el stock disponible de ese producto, sin que el
  Administrador deba escribir el SKU en ningún momento.

### RF-5: Cada opción identifica claramente al producto
- EL SISTEMA deberá mostrar, para cada opción del desplegable, al
  menos el Nombre y el Código/SKU del producto, para que el
  Administrador pueda diferenciar productos con nombres parecidos.

### RF-6: Sin coincidencias
- SI ningún producto Activo coincide con el criterio buscado, ENTONCES
  EL SISTEMA deberá indicar que no se encontraron productos, en vez de
  mostrar un desplegable vacío sin explicación.

### RF-7: Cambiar el criterio descarta la selección previa
- CUANDO el Administrador modifica el texto de búsqueda después de
  haber elegido un producto, EL SISTEMA deberá descartar esa selección
  (SKU, nombre, precio y stock ya completados) hasta que se elija una
  nueva opción del desplegable, para no agregar por error un producto
  distinto al que quedó escrito en el campo de texto.

### RF-8: El resto del armado del ítem no cambia
- Una vez seleccionado el producto, la cantidad se ingresa de la misma
  forma que hoy, y las validaciones ya existentes (cantidad positiva,
  stock suficiente, reporte combinado de errores) siguen aplicando sin
  cambios, tanto en [[009-alta-venta]] como en
  [[011-modificacion-venta]].

## Requisitos no funcionales
- Todos los mensajes dirigidos al Administrador (ej. "no se encontraron
  productos") deben estar en español.
- La búsqueda debe leer únicamente de la base de datos oficial del
  proyecto.

## Casos límite
- Un criterio que coincide con la Descripción pero no con el Nombre de
  un producto: igual aparece entre las opciones (RF-1 busca en ambos
  campos).
- Un criterio que coincide con un producto Inactivo pero con ningún
  Activo: se informa que no se encontraron productos (RF-3, RF-6),
  igual que si no existiera ningún producto con ese criterio.
- Un producto cuyo Nombre y Descripción contienen el criterio a la vez:
  aparece una sola vez entre las opciones, no duplicado.
- Un producto sin Descripción cargada (campo opcional en
  [[005-alta-producto]]): sigue siendo candidato por coincidencia de
  Nombre; la ausencia de Descripción no rompe la búsqueda.
- El Administrador elige un producto, y después borra o cambia el
  texto del campo de búsqueda sin elegir una nueva opción: el ítem no
  puede agregarse con los datos del producto anterior (RF-7).

## Fuera de alcance
- Cualquier cambio al filtro o al comportamiento de
  [[008-listar-productos]] (sigue buscando solo por Nombre o
  Código/SKU, sin Descripción).
- Búsqueda por Marca, Precio unitario o Stock en este selector.
- Paginación tipo "Anterior/Siguiente" en el desplegable de resultados.
- Cambios a la búsqueda de cliente por DNI en Venta.
- Cambios al mecanismo de búsqueda de una venta existente (por ID) en
  Anular o Modificar Venta: se trata en una spec aparte.

## Criterios de finalización
- En Registrar Venta y en el agregado de ítems de Modificar Venta, el
  Administrador ya no escribe el SKU manualmente: busca por Nombre o
  Descripción y elige una opción (RF-1, RF-4).
- Los productos Inactivos nunca aparecen entre las opciones (RF-3).
- Un criterio sin coincidencias informa que no se encontraron productos
  (RF-6).
- Cambiar el texto de búsqueda después de elegir un producto descarta
  esa selección (RF-7).
- Las validaciones de cantidad y stock, y el resto del flujo de armado
  del detalle, siguen funcionando igual que antes (RF-8).
- Todos los criterios de aceptación de HU-VEN-05 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes.
