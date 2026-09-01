# Spec 012 — Listar Ventas

## Contexto y objetivo
El sistema ya permite registrar ([[009-alta-venta]]), modificar
([[011-modificacion-venta]]) y anular ([[010-anular-venta]]) ventas, pero
siempre localizándolas de a una por su ID exacto. No existe una vista que
permita al Administrador consultar el historial completo de ventas ni
filtrarlo por fecha o por cliente. El objetivo de esta feature es que el
Administrador pueda ver ese historial y acotarlo por rango de fechas y/o
por DNI de cliente, para analizar las operaciones realizadas, siguiendo el
mismo criterio de listado y filtro ya validado en
[[004-listar-clientes]] y [[008-listar-productos]].

## Usuarios
- **Administrador**: único rol que consulta el historial de ventas en
  esta feature.

## Historias de usuario

### HU-VEN-04: Listar Ventas
Como Administrador
Quiero consultar el historial de ventas
Para analizar las operaciones realizadas según fechas y clientes.

## Requisitos funcionales

### RF-1: Listado completo por defecto
- CUANDO el Administrador ingresa a la pantalla de historial sin haber
  aplicado ningún filtro, EL SISTEMA deberá mostrar todas las ventas
  "Confirmada" registradas, ordenadas por fecha de venta de la más
  reciente a la más antigua.

### RF-2: Solo ventas "Confirmada"
- EL SISTEMA deberá incluir en el listado y en los resultados de
  cualquier filtro únicamente a las ventas en estado "Confirmada"; las
  ventas en "Borrador" ([[011-modificacion-venta]]) y "Anulada"
  ([[010-anular-venta]]) no se consideran "concretadas" y quedan
  excluidas del historial.

### RF-3: Filtro por rango de fechas
- CUANDO el Administrador aplica un filtro con una fecha "desde", una
  fecha "hasta", o ambas, EL SISTEMA deberá listar únicamente las
  ventas "Confirmada" cuya fecha de venta (sin considerar la hora) sea
  mayor o igual a la fecha "desde" (si se indicó) y menor o igual a la
  fecha "hasta" (si se indicó), incluyendo ambos extremos.

### RF-4: Filtro por DNI de cliente
- CUANDO el Administrador aplica un filtro con un DNI (completo o
  parcial), EL SISTEMA deberá listar únicamente las ventas "Confirmada"
  cuyo cliente tenga un DNI que contenga ese valor en cualquier parte,
  sin exigir que coincida con el DNI completo.

### RF-5: Combinación de filtros
- CUANDO el Administrador aplica el rango de fechas y el filtro de DNI a
  la vez, EL SISTEMA deberá listar únicamente las ventas "Confirmada"
  que cumplan ambas condiciones simultáneamente.

### RF-6: Rango de fechas inválido
- SI la fecha "desde" ingresada es posterior a la fecha "hasta",
  ENTONCES EL SISTEMA deberá advertir que el rango de fechas es inválido
  y no deberá aplicar el filtro.

### RF-7: Sin resultados
- SI ninguna venta "Confirmada" coincide con el o los filtros aplicados,
  ENTONCES EL SISTEMA deberá informar que no se encontraron resultados,
  en lugar de mostrar una lista vacía sin explicación.

### RF-8: Restablecer el listado al borrar los filtros
- CUANDO el Administrador borra todos los criterios de filtro aplicados
  (fechas y DNI), EL SISTEMA deberá volver a mostrar el listado completo
  de ventas "Confirmada", igual que en la vista inicial.

### RF-9: Paginación de resultados
El sistema deberá mostrar los resultados del listado (con o sin filtro
aplicado) de a 20 ventas por página, con la posibilidad de navegar a la
página anterior o a la siguiente.

- CUANDO el listado o el resultado del filtro tiene más de 20 ventas, EL
  SISTEMA deberá mostrar solo las primeras 20 y habilitar la navegación
  hacia las páginas siguientes.
- CUANDO el Administrador aplica o modifica cualquier criterio de
  filtro, EL SISTEMA deberá volver a mostrar la primera página de los
  nuevos resultados.

### RF-10: Datos mostrados por cada venta
- EL SISTEMA deberá mostrar, para cada venta listada, su ID, su fecha,
  el nombre completo y DNI del cliente, y su total. No se exige mostrar
  el detalle de ítems de cada venta desde esta pantalla.

## Requisitos no funcionales
- Todos los mensajes dirigidos al Administrador (ej. "no se encontraron
  resultados", "el rango de fechas es inválido") deben estar en español.
- Los datos listados deben leerse únicamente de la base de datos oficial
  del proyecto; no se admite almacenamiento local ad-hoc.

## Casos límite
- Filtrar solo con fecha "desde" (sin "hasta"): incluye todas las ventas
  "Confirmada" desde esa fecha en adelante, sin límite superior (RF-3).
- Filtrar solo con fecha "hasta" (sin "desde"): incluye todas las ventas
  "Confirmada" hasta esa fecha inclusive, sin límite inferior (RF-3).
- Una venta "Confirmada" cuya fecha coincide exactamente con "desde" o
  con "hasta" se incluye en el resultado (extremos inclusivos, RF-3).
- Una venta que estuvo "Confirmada" y luego fue anulada
  ([[010-anular-venta]]) deja de aparecer en el historial desde el
  momento de la anulación (RF-2).
- Un DNI parcial (ej. "3011") encuentra a un cliente cuyo DNI contiene
  esa secuencia (ej. "30111222"), sin exigir el DNI completo (RF-4).
- Filtrar por un DNI que no compró nunca (o solo tiene ventas en
  Borrador o Anuladas) informa que no se encontraron resultados (RF-7).
- El Administrador borra los filtros después de haber filtrado: la lista
  vuelve a mostrar todo el historial (RF-8), no queda vacía.
- El listado o el resultado del filtro tiene 20 ventas o menos: no hay
  página siguiente disponible (RF-9).
- El Administrador cambia cualquier filtro estando en una página
  distinta de la primera: la paginación vuelve a la página 1 con los
  nuevos resultados (RF-9).
- Sin ningún filtro aplicado y con más de 20 ventas "Confirmada"
  registradas: la vista inicial (RF-1) también pagina de a 20.

## Fuera de alcance
- Edición, cierre o anulación de ventas desde esta pantalla de listado
  (ya existen en [[011-modificacion-venta]] y [[010-anular-venta]]);
  esta feature es solo de consulta.
- Ver el detalle de ítems de una venta desde el listado (RF-10 solo
  exige los datos resumidos).
- Exportar el listado (CSV, PDF, etc.).
- Ordenamiento personalizado por el Administrador (elegir columna o
  dirección de orden distinta a fecha descendente).
- Filtro por otros campos (nombre de cliente, producto, monto, estado).
- Reportes o totales agregados (suma de ventas del período, promedios,
  etc.).
- Autenticación y gestión de roles de usuario (se asume que el sistema
  ya identifica quién opera como Administrador).

## Criterios de finalización
- Sin ningún filtro aplicado, se lista todo el historial de ventas
  "Confirmada", ordenado por fecha descendente (RF-1, RF-2).
- Un filtro por rango de fechas (completo o con un solo extremo)
  devuelve únicamente las ventas "Confirmada" dentro de ese rango,
  extremos incluidos (RF-3).
- Un filtro por DNI (completo o parcial) devuelve únicamente las ventas
  "Confirmada" del o de los clientes cuyo DNI coincide (RF-4).
- Combinar fecha y DNI devuelve solo las ventas que cumplen ambas
  condiciones (RF-5).
- Un rango de fechas con "desde" posterior a "hasta" se rechaza con una
  advertencia, sin aplicar el filtro (RF-6).
- Un filtro sin coincidencias informa que no se encontraron resultados
  (RF-7).
- Borrar los filtros vuelve a mostrar el historial completo (RF-8).
- Un listado o resultado filtrado con más de 20 ventas se muestra
  paginado de a 20, con navegación a la página siguiente/anterior, y
  cambiar cualquier filtro reinicia la paginación a la página 1 (RF-9).
- Cada fila muestra ID, fecha, cliente (nombre y DNI) y total (RF-10).
- Todos los criterios de aceptación de HU-VEN-04 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Se resolvió que: el listado sin filtro
muestra todo el historial (mismo criterio que
[[004-listar-clientes]]/[[008-listar-productos]]); solo se consideran
"concretadas" las ventas en estado "Confirmada", excluyendo Borrador y
Anulada; el filtro por DNI admite coincidencia parcial; y los filtros de
fecha y DNI son combinables con AND.
