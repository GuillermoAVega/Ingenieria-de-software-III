# Spec 015 — Texto de Ayuda en Listar Productos

## Contexto y objetivo
Mismo tipo de corrección que [[014-correcciones-cliente]] RF-3, aplicada
ahora a [[008-listar-productos]]: el filtro de esa pantalla ya busca por
Nombre o Código/SKU (RF-2 de 008), pero la pantalla no se lo comunica al
Administrador. La spec 014 dejó esta extensión explícitamente anotada
como "Fuera de alcance... para más adelante"; esta spec la retoma para
Producto.

## Usuarios
- **Administrador**: único rol que consulta el listado de productos en
  esta feature.

## Requisitos funcionales

### RF-1: Texto de ayuda sobre los criterios de búsqueda (listado de productos)
- EL SISTEMA deberá mostrar, debajo de la barra de búsqueda de la
  pantalla de listado de productos, un texto indicando que la búsqueda
  puede hacerse por Nombre o Código/SKU.

## Requisitos no funcionales
- El texto debe estar en español, mismo criterio que el resto de la
  aplicación.

## Casos límite
- El texto es puramente informativo: no cambia ni restringe el
  comportamiento de filtrado ya implementado en [[008-listar-productos]]
  RF-2 a RF-4.

## Fuera de alcance
- Cambios al mecanismo de filtrado de [[008-listar-productos]] (RF-1 a
  RF-8): el filtro ya busca por Nombre o Código/SKU; esta spec solo
  agrega el texto que lo comunica.
- Extender el mismo texto de ayuda al listado de Ventas (no tiene
  filtro de texto libre por nombre/código, sino por fecha y DNI, ver
  [[012-listar-ventas]]).

## Criterios de finalización
- La pantalla de Listar Productos muestra, debajo de la barra de
  búsqueda, un texto indicando que se puede buscar por Nombre o
  Código/SKU (RF-1).
- El criterio de aceptación está cubierto por una prueba automatizada
  en verde.

## Dudas abiertas
Sin dudas abiertas pendientes.
