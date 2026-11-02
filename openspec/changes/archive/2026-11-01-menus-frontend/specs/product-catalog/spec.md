# Especificación delta: Catálogo de Productos

Capacidad modificada por el cambio `menus-frontend`. Se agrega el listado de menús ejecutivos activos.

## MODIFIED Requirements

### Requirement: Rutas ABM por subtipo
La API DEBE exponer `/productos/platos`, `/productos/bebidas`, `/productos/postres`, `/productos/menus-ejecutivos`, `/productos/combos`, cada una con alta (POST), obtención por id (`GET /productos/<subtype>/{id}`), modificación (PUT) y baja lógica (DELETE, véase product-logical-delete). Además, `/productos/platos`, `/productos/bebidas`, `/productos/postres` y `/productos/menus-ejecutivos` DEBEN exponer el listado `GET /productos/<subtype>`, que devuelve solo los productos activos (`dado_de_baja = false`) ordenados por id ascendente. La API NO DEBE exponer `GET /productos` (listado polimórfico), consulta polimórfica por id (`GET /productos/{id}`), el listado de combos ni el parámetro `?incluir_bajas`.

## ADDED Requirements

### Requirement: Listado de menús ejecutivos activos
`GET /productos/menus-ejecutivos` DEBE devolver 200 con la lista de menús ejecutivos activos (`dado_de_baja = false`), ordenados por `id` ascendente, con la misma forma de `MenuRespuesta` que la consulta por id. NO DEBE exponer menús dados de baja, NO DEBE mezclar otros subtipos y NO DEBE aceptar `?incluir_bajas`.

#### Scenario: CAT-S-29 Listado vacío
- DADO que no existe ningún menú ejecutivo
- CUANDO un cliente llama a `GET /productos/menus-ejecutivos`
- ENTONCES 200 y el cuerpo es una lista vacía

#### Scenario: CAT-S-30 Sólo menús activos
- DADO un menú ejecutivo activo y otro dado de baja
- CUANDO un cliente llama a `GET /productos/menus-ejecutivos`
- ENTONCES la respuesta contiene únicamente el menú activo

#### Scenario: CAT-S-31 Orden por id ascendente
- DADO dos menús ejecutivos activos
- CUANDO un cliente llama a `GET /productos/menus-ejecutivos`
- ENTONCES los ítems aparecen ordenados por `id` ascendente

#### Scenario: CAT-S-32 El listado no mezcla otros subtipos
- DADO un menú ejecutivo activo y platos o postres sueltos
- CUANDO un cliente llama a `GET /productos/menus-ejecutivos`
- ENTONCES todos los ítems tienen `tipo = "menu_ejecutivo"` y sólo aparecen menús ejecutivos
