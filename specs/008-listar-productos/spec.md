# Spec 008 — Listar Productos

## Contexto y objetivo
El sistema ya permite dar de alta ([[005-alta-producto]]), dar de baja
([[006-baja-producto]]) y editar ([[007-modificacion-producto]]) productos
de a uno, siempre localizándolos por su SKU exacto. No existe forma de ver
el catálogo completo ni de encontrar un producto cuando no se conoce su
SKU completo. El objetivo de esta feature es que el Administrador pueda
consultar el catálogo de productos y filtrarlo por Nombre o Código/SKU,
para controlar el stock y localizar productos específicos.

## Usuarios
- **Administrador**: único rol que consulta el listado de productos en
  esta feature.

## Historias de usuario

### HU-PROD-04: Listar Productos
Como Administrador
Quiero visualizar el catálogo de productos
Para controlar el stock y buscar ítems por nombre o código.

## Requisitos funcionales

### RF-1: Listado completo por defecto
El sistema deberá mostrar la lista completa de productos registrados
cuando no hay ningún filtro aplicado.

- CUANDO el Administrador ingresa a la pantalla de listado sin haber
  aplicado ningún filtro, EL SISTEMA deberá mostrar todos los productos
  registrados, junto con su SKU, Nombre, Marca, Precio unitario, Stock y
  estado.

### RF-2: Filtro único sobre Nombre y Código/SKU
El sistema deberá permitir al Administrador filtrar la lista ingresando
un único criterio de búsqueda, comparado contra el Nombre y el
Código/SKU de cada producto.

- CUANDO el Administrador ejecuta el filtro con un criterio de búsqueda,
  EL SISTEMA deberá listar únicamente los productos cuyo Nombre o
  Código/SKU contengan ese criterio.

### RF-3: Coincidencia parcial
- EL SISTEMA deberá considerar una coincidencia cuando el criterio
  ingresado esté contenido en cualquier parte del Nombre o del
  Código/SKU del producto, sin exigir que coincida con el valor completo.

### RF-4: Insensibilidad a mayúsculas y tildes
- EL SISTEMA deberá comparar el criterio de búsqueda contra el Nombre y
  el Código/SKU sin distinguir mayúsculas de minúsculas ni tildes.

### RF-5: Sin resultados
- SI ningún producto coincide con el criterio de búsqueda aplicado,
  ENTONCES EL SISTEMA deberá informar que no se encontraron resultados,
  en lugar de mostrar una lista vacía sin explicación.

### RF-6: Inclusión de productos Activos e Inactivos
- EL SISTEMA deberá incluir tanto a los productos Activos como a los
  Inactivos en el listado y en los resultados del filtro, mostrando el
  estado de cada uno.

### RF-7: Restablecer el listado al borrar el filtro
- CUANDO el Administrador borra el criterio de búsqueda (deja el campo
  vacío), EL SISTEMA deberá volver a mostrar la lista completa de
  productos, igual que en la vista inicial.

### RF-8: Paginación de resultados
El sistema deberá mostrar los resultados del listado (con o sin filtro
aplicado) de a 20 productos por página, con la posibilidad de navegar a
la página anterior o a la siguiente.

- CUANDO el listado o el resultado del filtro tiene más de 20 productos,
  EL SISTEMA deberá mostrar solo los primeros 20 y habilitar la
  navegación hacia las páginas siguientes.
- CUANDO el Administrador aplica o modifica el criterio de búsqueda, EL
  SISTEMA deberá volver a mostrar la primera página de los nuevos
  resultados.

## Requisitos no funcionales
- Todos los mensajes dirigidos al Administrador (ej. "no se encontraron
  resultados") deben estar en español.
- Los datos listados deben leerse únicamente de la base de datos oficial
  del proyecto; no se admite almacenamiento local ad-hoc.

## Casos límite
- Buscar un SKU parcial (ej. "ABC") encuentra a un producto cuyo SKU
  contiene esa secuencia (ej. "ABC123"), sin exigir el SKU completo
  (RF-3).
- Un producto cuyo Nombre y SKU contienen el criterio a la vez aparece
  una sola vez en el resultado, no duplicado.
- El criterio de búsqueda con espacios al inicio o al final se recorta
  antes de comparar.
- Un filtro que coincide con productos tanto Activos como Inactivos
  devuelve ambos en el mismo resultado, cada uno con su estado (RF-6).
- El Administrador borra el criterio después de haber filtrado: la lista
  vuelve a mostrar todo el catálogo (RF-7), no queda vacía.
- El listado o el resultado del filtro tiene 20 productos o menos: no hay
  página siguiente disponible (RF-8).
- El Administrador cambia el criterio de búsqueda estando en una página
  distinta de la primera: la paginación vuelve a la página 1 con los
  nuevos resultados (RF-8).
- Sin ningún filtro aplicado y con más de 20 productos registrados: la
  vista inicial (RF-1) también pagina de a 20.

## Fuera de alcance
- Edición o baja de productos desde esta pantalla de listado (ya existen
  en [[006-baja-producto]] y [[007-modificacion-producto]]); esta
  feature es solo de consulta.
- Exportar la lista (CSV, PDF, etc.).
- Ordenamiento personalizado por el Administrador (elegir columna o
  dirección de orden).
- Búsqueda por Marca, Descripción, Precio unitario o Stock (el criterio
  de aceptación especifica únicamente Nombre o Código de producto).
- Filtro por rango de precio o de stock.
- Integración con un módulo de Ventas.
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Historial de búsquedas realizadas.

## Criterios de finalización
- Sin ningún filtro aplicado, se lista todo el catálogo (Activos e
  Inactivos) junto con su estado (RF-1, RF-6).
- Un filtro por un fragmento de Nombre o Código/SKU, insensible a
  mayúsculas y tildes, devuelve únicamente los productos que coinciden
  (RF-2, RF-3, RF-4).
- Un filtro sin coincidencias informa que no se encontraron resultados,
  sin mostrar una lista vacía sin explicación (RF-5).
- Borrar el criterio de búsqueda vuelve a mostrar el catálogo completo
  (RF-7).
- Un listado o resultado filtrado con más de 20 productos se muestra
  paginado de a 20, con navegación a la página siguiente/anterior, y
  cambiar el filtro reinicia la paginación a la página 1 (RF-8).
- Todos los criterios de aceptación de HU-PROD-04 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Todas las aclaraciones fueron resueltas y
volcadas a los requisitos correspondientes (RF-1, RF-6, RF-8), siguiendo
el mismo criterio ya validado en [[004-listar-clientes]].
