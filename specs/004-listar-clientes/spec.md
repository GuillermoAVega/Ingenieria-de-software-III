# Spec 004 — Listar Clientes

## Contexto y objetivo
El sistema ya permite dar de alta ([[001-alta-cliente]]), dar de baja
([[002-baja-cliente]]) y editar ([[003-modificacion-cliente]]) clientes de a
uno, siempre localizándolos por su DNI exacto. No existe forma de ver el
conjunto de clientes registrados ni de encontrar a uno cuando no se conoce
su DNI completo. El objetivo de esta feature es que el Administrador pueda
consultar la lista de clientes y filtrarla por Nombre, Apellido o DNI, para
localizar clientes específicos y ver su estado (Activo/Inactivo) de un
vistazo.

## Usuarios
- **Administrador**: único rol que consulta el listado de clientes en esta
  feature.

## Historias de usuario

### HU-CLI-04: Listar Clientes
Como Administrador
Quiero consultar y filtrar la lista de clientes
Para localizar clientes específicos y visualizar su estado.

## Requisitos funcionales

### RF-1: Listado completo por defecto
El sistema deberá mostrar la lista completa de clientes registrados cuando
no hay ningún filtro aplicado.

- CUANDO el Administrador ingresa a la pantalla de listado sin haber
  aplicado ningún filtro, EL SISTEMA deberá mostrar todos los clientes
  registrados, junto con su DNI, nombre, apellido y estado.

### RF-2: Filtro único sobre Nombre, Apellido y DNI
El sistema deberá permitir al Administrador filtrar la lista ingresando un
único criterio de búsqueda, comparado contra el Nombre, el Apellido y el
DNI de cada cliente.

- CUANDO el Administrador ejecuta el filtro con un criterio de búsqueda, EL
  SISTEMA deberá listar únicamente los clientes cuyo Nombre, Apellido o DNI
  contengan ese criterio.

### RF-3: Coincidencia parcial
- EL SISTEMA deberá considerar una coincidencia cuando el criterio
  ingresado esté contenido en cualquier parte del Nombre, Apellido o DNI del
  cliente, sin exigir que coincida con el valor completo.

### RF-4: Insensibilidad a mayúsculas y tildes
- EL SISTEMA deberá comparar el criterio de búsqueda contra el Nombre y el
  Apellido sin distinguir mayúsculas de minúsculas ni tildes.

### RF-5: Sin resultados
- SI ningún cliente coincide con el criterio de búsqueda aplicado, ENTONCES
  EL SISTEMA deberá informar que no se encontraron resultados, en lugar de
  mostrar una lista vacía sin explicación.

### RF-6: Inclusión de clientes Activos e Inactivos
- EL SISTEMA deberá incluir tanto a los clientes Activos como a los
  Inactivos en el listado y en los resultados del filtro, mostrando el
  estado de cada uno.

### RF-7: Restablecer el listado al borrar el filtro
- CUANDO el Administrador borra el criterio de búsqueda (deja el campo
  vacío), EL SISTEMA deberá volver a mostrar la lista completa de clientes,
  igual que en la vista inicial.

### RF-8: Paginación de resultados
El sistema deberá mostrar los resultados del listado (con o sin filtro
aplicado) de a 20 clientes por página, con la posibilidad de navegar a la
página anterior o a la siguiente.

- CUANDO el listado o el resultado del filtro tiene más de 20 clientes, EL
  SISTEMA deberá mostrar solo los primeros 20 y habilitar la navegación
  hacia las páginas siguientes.
- CUANDO el Administrador aplica o modifica el criterio de búsqueda, EL
  SISTEMA deberá volver a mostrar la primera página de los nuevos
  resultados.

## Requisitos no funcionales
- Todos los mensajes dirigidos al Administrador (ej. "no se encontraron
  resultados") deben estar en español.
- Los datos listados deben leerse únicamente de la base de datos oficial
  del proyecto; no se admite almacenamiento local ad-hoc.

## Casos límite
- Buscar un DNI parcial (ej. "301112") encuentra a un cliente cuyo DNI
  contiene esa secuencia de dígitos (ej. "30111222"), sin exigir el DNI
  completo (RF-3).
- Un cliente cuyo Nombre y Apellido contienen el criterio a la vez (ej.
  buscar "an" en un cliente "Ana López") aparece una sola vez en el
  resultado, no duplicado.
- El criterio de búsqueda con espacios al inicio o al final se recorta
  antes de comparar, igual que el resto de los campos de texto de la
  aplicación.
- Buscar un DNI usando ceros a la izquierda tal como se cargó originalmente
  (ej. "0123456"): dado que el DNI se persiste como valor numérico sin
  ceros a la izquierda desde [[001-alta-cliente]], la búsqueda debe hacerse
  contra ese valor ya normalizado; buscar con el cero a la izquierda no
  necesariamente encuentra al cliente si la cantidad de dígitos buscados no
  coincide con la del valor almacenado.
- Un filtro que coincide con clientes tanto Activos como Inactivos
  devuelve ambos en el mismo resultado, cada uno con su estado (RF-6).
- El Administrador borra el criterio después de haber filtrado: la lista
  vuelve a mostrar todos los clientes (RF-7), no queda vacía.
- El listado o el resultado del filtro tiene 20 clientes o menos: no hay
  página siguiente disponible (RF-8).
- El Administrador cambia el criterio de búsqueda estando en una página
  distinta de la primera: la paginación vuelve a la página 1 con los
  nuevos resultados (RF-8).
- Sin ningún filtro aplicado y con más de 20 clientes registrados: la vista
  inicial (RF-1) también pagina de a 20, igual que un resultado filtrado.

## Fuera de alcance
- Edición o baja de clientes desde esta pantalla de listado (ya existen en
  [[002-baja-cliente]] y [[003-modificacion-cliente]]); esta feature es solo
  de consulta.
- Exportar la lista (CSV, PDF, etc.).
- Ordenamiento personalizado por el Administrador (elegir columna o
  dirección de orden).
- Búsqueda por email o teléfono (el criterio de aceptación especifica
  únicamente Nombre, Apellido o DNI).
- Filtro por rango de fechas de alta u otros criterios no mencionados.
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Historial de búsquedas realizadas.

## Criterios de finalización
- Sin ningún filtro aplicado, se listan todos los clientes (Activos e
  Inactivos) junto con su estado (RF-1, RF-6).
- Un filtro por un fragmento de Nombre, Apellido o DNI, insensible a
  mayúsculas y tildes, devuelve únicamente los clientes que coinciden
  (RF-2, RF-3, RF-4).
- Un filtro sin coincidencias informa que no se encontraron resultados,
  sin mostrar una lista vacía sin explicación (RF-5).
- Borrar el criterio de búsqueda vuelve a mostrar la lista completa (RF-7).
- Un listado o resultado filtrado con más de 20 clientes se muestra
  paginado de a 20, con navegación a la página siguiente/anterior, y
  cambiar el filtro reinicia la paginación a la página 1 (RF-8).
- Todos los criterios de aceptación de HU-CLI-04 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. La paginación fue resuelta durante la
entrevista y volcada a RF-8: 20 clientes por página, con navegación
Anterior/Siguiente.
