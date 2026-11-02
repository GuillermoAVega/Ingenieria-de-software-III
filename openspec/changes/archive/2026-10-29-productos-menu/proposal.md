# Propuesta: Productos Menú del Día

## Intención

No hay forma de registrar qué producto fue o será "menú del día" en una fecha. Se agrega la entidad `ProductoMenu` con alta, modificación de fecha y borrado físico, con un único menú del día por fecha.

## Alcance

### Dentro del alcance
- `Backend/src/productos_menu/` según la convención de una carpeta por entidad (models, schemas, exceptions, constants, services, router); pruebas en `Backend/tests/productos_menu/`.
- Tabla `producto_menu`: `id`, `producto_id` (FK obligatoria a `producto.id`, cualquier subtipo), `fecha` (date; pasada, hoy o futura). Índice UNIQUE en `fecha`.
- Relación bidireccional con `back_populates`: `ProductoMenu.producto` / `Producto.menus_del_dia` (0..N).
- `POST /productos-menu` `{producto_id, fecha}` → 201 `{id, producto_id, fecha}`. Prioridad: esquema 422 → producto inexistente 422 → producto dado de baja 409 → fecha ocupada 409.
- `PUT /productos-menu/{id}` `{fecha}` → 200. Prioridad: esquema 422 → 404 → producto dado de baja 409 → fecha ocupada por OTRO registro 409 (conservar la propia es válido).
- `DELETE /productos-menu/{id}` físico → 204; inexistente o repetido → 404.
- Registro del router y los manejadores en `Backend/src/main.py`; carga del modelo en `registro.py`.

### Fuera del alcance
- GET y listados, cambio de `producto_id`, exponer los menús en las respuestas de producto, Frontend, migraciones.
- Cambios en la baja lógica: ser menú del día NO bloquea la baja (`RESTRICT_POR_TIPO` no cambia).

## Capacidades

### Capacidades nuevas
- `daily-menu-management`: entidad ProductoMenu, unicidad por fecha, alta, modificación de fecha, borrado físico y prioridad de errores.

### Capacidades modificadas
- Ninguna. `product-catalog` y `product-logical-delete` no cambian a nivel de requisitos.

## Valores por defecto derivados (a confirmar en la revisión)

1. Las respuestas de producto no exponen los menús del día.
2. FK sin cláusula `ON DELETE` (comportamiento por defecto, NO ACTION): los productos solo se dan de baja lógicamente.
3. `create_all` crea la tabla nueva; `producto` no gana columnas. La `app.db` local igualmente debe recrearse, solo por el cambio previo de `posicion`.
4. `productos_menu` importa `productos`; `productos` no importa `productos_menu`, salvo `registro.py` para configurar los mappers (`Producto.menus_del_dia` se declara por cadena). A precisar en el diseño.
5. El DELETE no verifica el estado del producto.
6. Un `producto_id` enviado en el PUT se ignora (Pydantic descarta campos extra, como en el resto de la API).

## Enfoque

Modelo sobre `ModeloBase`; validación del producto reutilizando la carga de `productos`. El servicio verifica la fecha antes de escribir y traduce el `IntegrityError` del índice UNIQUE a 409 como respaldo ante concurrencia. Routers delgados.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `Backend/src/productos_menu/` | Nuevo | Módulo de la entidad |
| `Backend/src/productos/models.py`, `registro.py` | Modificado | Relación inversa y carga del modelo |
| `Backend/src/main.py` | Modificado | Router y manejadores |
| `Backend/tests/productos_menu/` | Nuevo | Pruebas |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Import circular entre `productos` y `productos_menu` | Media | Relación por cadena; carga solo vía `registro` |
| No se puede corregir la fecha de un registro histórico cuyo producto se dio de baja | Media | Consecuencia aceptada; cubrirla con pruebas |
| Carrera entre dos altas con la misma fecha | Baja | Índice UNIQUE traducido a 409 |

## Plan de reversión

Revertir los commits del cambio: eliminar `Backend/src/productos_menu/`, la relación en `Producto`, la carga en `registro.py` y el registro en `main.py`; eliminar la tabla `producto_menu` o recrear la base local.

## Dependencias

- `productos-backend` archivado (cumplido).

## Criterios de éxito

- [ ] Endpoints según la especificación (201/200/204/404/409/422) con la prioridad indicada.
- [ ] Una segunda alta o modificación a una fecha ocupada devuelve 409.
- [ ] La baja de un producto que es menú del día sigue funcionando sin cambios.
- [ ] Mappers configurados sin errores; la suite de pytest pasa.
