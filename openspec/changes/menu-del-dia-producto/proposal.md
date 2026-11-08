# Propuesta: Menú del Día como subtipo de Producto

## Intención

Hoy `ProductoMenu` apunta a cualquier `Producto`, por lo que no existe un producto "menú del día" reutilizable y se tiende a duplicar productos por fecha. Se crea el subtipo `MenuDelDia(Producto)` y `ProductoMenu` pasa a registrar en qué fechas un `MenuDelDia` fue o será menú del día.

## Alcance

### Dentro del alcance
- Subtipo `MenuDelDia` (herencia por tablas unidas, tabla `menu_del_dia`, `TIPO_MENU_DEL_DIA="menu_del_dia"`), sin campos propios, coexistente con `MenuEjecutivo`. Paquete `Backend/src/productos/menus_del_dia/` según la convención de una carpeta por entidad; CRUD en `/productos/menus-del-dia`.
- `ProductoMenu` (módulo `src/productos_menu/` conservado): `menu_del_dia_id` (FK NOT NULL → `menu_del_dia.id`) reemplaza a `producto_id`; `fecha` UNIQUE; relación `MenuDelDia.fechas` (0..N). Endpoints `/productos-menu` con `menu_del_dia_id`.
- Fechas pasadas, hoy y futuras permitidas.
- Asignar una fecha a un `MenuDelDia` dado de baja → 409.
- Baja lógica de un `MenuDelDia` con algún `ProductoMenu` de `fecha >= hoy` → 409 (vía `obtener_hoy`); solo con fechas pasadas se permite y se conserva el historial.
- Frontend: `features/daily-menu/` selecciona un `MenuDelDia` y usa `menu_del_dia_id`; CRUD de menús del día en `features/products/` (nueva pestaña/tipo); etiqueta `menu_del_dia` en `features/menus/format.ts`. Respetar AGENTS.md.
- Reescritura de `Backend/tests/productos_menu/`, fixtures `crear_menu_del_dia` y `crear_producto_menu`, conteo de tipos 5 → 6.

### Fuera del alcance
- `Promocion` (cambio posterior), cambios en `MenuEjecutivo`, migración de datos existentes.

## Capacidades

### Capacidades nuevas
- Ninguna.

### Capacidades modificadas
- `daily-menu-management`: la FK pasa a `menu_del_dia_id`; 409 por menú dado de baja.
- `product-catalog`: nuevo tipo `menu_del_dia` y su CRUD.
- `product-logical-delete`: bloqueo de la baja con fechas `>= hoy`.

## Enfoque

Replicar el subtipo mínimo `postres/` usando los servicios genéricos; la regla de baja se implementa como verificación específica del tipo, análoga a la de combos (`fecha_hasta >= hoy`). Prioridad del alta: inexistente 422 → dado de baja 409 → fecha ocupada 409.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `Backend/src/productos/menus_del_dia/` | Nuevo | Subtipo |
| `Backend/src/productos/{constants,registro,router,models,services}.py` | Modificado | Tipo, registro, relación, regla de baja |
| `Backend/src/productos_menu/` | Modificado | FK y validaciones |
| `Backend/tests/` | Modificado | Pruebas y fixtures |
| `Frontend/src/features/{daily-menu,products,menus}/` | Modificado | Contrato y CRUD |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Base SQLite local desfasada (`create_all` no altera tablas) | Alta | Documentar: eliminar `producto_menu` o recrear `app.db` |
| Frontend roto durante la transición | Media | Backend y frontend en la misma entrega |
| Import circular `productos` ↔ `productos_menu` en la regla de baja | Media | Relación por cadena; resolver en el diseño |

## Plan de reversión

Revertir los commits del cambio y recrear la base local (tablas `menu_del_dia` y `producto_menu`).

## Dependencias

- `productos-menu` archivado (cumplido).

## Criterios de éxito

- [ ] CRUD de `/productos/menus-del-dia` operativo; seis tipos registrados.
- [ ] `/productos-menu` exige `menu_del_dia_id`; 409 por fecha ocupada o menú dado de baja.
- [ ] Baja bloqueada con fecha `>= hoy`; permitida con solo fechas pasadas.
- [ ] Frontend compila (`tsc`, lint) y opera con el nuevo contrato; la suite de pytest pasa.
