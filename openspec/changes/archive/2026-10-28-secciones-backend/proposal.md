# Propuesta: Secciones Backend

## Intención

El catálogo no permite agrupar productos para presentarlos (por ejemplo, "Entradas" o "Bebidas sin alcohol"). Se agrega la entidad `Seccion` con ABM y consulta por id, y la asignación opcional de cada producto a una sección.

## Alcance

### Dentro del alcance
- `Backend/src/secciones/` según la convención de una carpeta por entidad (models, schemas, exceptions, constants, services, router); pruebas en `Backend/tests/secciones/`.
- `Seccion`: `id`, `nombre` (obligatorio, recortado, 1-100, único entre TODAS las secciones vía `nombre_normalizado`: sin distinguir mayúsculas, sí tildes; duplicado → 409), `subtitulo` (opcional, <= 200).
- `POST /secciones` (201), `GET /secciones/{id}`, `PUT /secciones/{id}` (reemplazo completo), `DELETE /secciones/{id}` (borrado FÍSICO, 204). Id inexistente → 404. Sin `dado_de_baja` ni reactivación.
- FK `producto.seccion_id` anulable con `ON DELETE SET NULL`; relación bidireccional `Seccion.productos` / `Producto.seccion` con `back_populates`.
- POST y PUT de los cinco subtipos aceptan `seccion_id` opcional (inexistente → 422); las respuestas lo exponen.
- Registro del router y los manejadores en `Backend/src/main.py`.

### Fuera del alcance
- Listados de secciones o de productos por sección, ordenamiento, baja lógica de secciones, Frontend, migraciones.

## Capacidades

### Capacidades nuevas
- `section-management`: entidad Seccion, validaciones, ABM, consulta por id y borrado físico con desvinculación de productos.

### Capacidades modificadas
- `product-catalog`: `seccion_id` en altas, modificaciones y respuestas de todos los subtipos; 422 por sección inexistente; prioridad de errores.

## Valores por defecto derivados (a confirmar en la revisión)

1. El PUT de producto es reemplazo completo: omitir `seccion_id` lo deja en `null`.
2. Los combos vencidos son inmutables: un PUT que cambia `seccion_id` devuelve 409. Borrar la sección igualmente anula su `seccion_id` a nivel de base de datos.
3. Un producto puede asignarse a una sección sin importar su `dado_de_baja`.
4. Prioridad: `seccion_id` inexistente (422) se ubica igual que los componentes inválidos (tras la carga 404 y, en combos, tras el 409 de vencido).

## Enfoque

Modelo sobre `ModeloBase` con índice UNIQUE en `nombre_normalizado`, reutilizando `normalizar_nombre`. La FK delega en SQLite (`PRAGMA foreign_keys=ON`) la anulación al borrar. Una función de servicio compartida en `productos/services.py` resuelve `seccion_id` para los cinco subtipos; los routers se mantienen delgados.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `Backend/src/secciones/` | Nuevo | Módulo de la entidad |
| `Backend/src/productos/` (models, schemas, services, subtipos) | Modificado | FK, campo en esquemas y validación |
| `Backend/src/main.py` | Modificado | Router y manejadores |
| `Backend/tests/secciones/`, `Backend/tests/productos/` | Nuevo/Modificado | Pruebas |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| `create_all` no altera la tabla `producto` existente en `app.db` | Alta | Recrear la base local; documentarlo |
| La baja por PUT de un combo vencido sin repetir `seccion_id` se rechaza (defaults 1 y 2) | Media | Incluir `seccion_id` en `_sin_otros_cambios` y cubrirlo con pruebas |
| Import circular entre `secciones` y `productos` | Media | Relaciones por cadena y carga vía `registro` |

## Plan de reversión

Revertir los commits del cambio: eliminar `Backend/src/secciones/`, la columna `seccion_id` y el registro en `main.py`, y recrear la base local.

## Dependencias

- `productos-backend` archivado (cumplido).

## Criterios de éxito

- [ ] Endpoints de secciones según la especificación (201/200/204/404/409/422).
- [ ] Borrar una sección deja `seccion_id = null` en sus productos.
- [ ] Los cinco subtipos aceptan y exponen `seccion_id`; inexistente → 422.
- [ ] Mappers configurados sin errores; la suite de pytest pasa.
