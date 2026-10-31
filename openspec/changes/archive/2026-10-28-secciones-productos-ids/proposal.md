# Propuesta: Ids de Productos en la Respuesta de Sección

## Intención

La respuesta de una sección no indica qué productos contiene, por lo que un cliente no puede conocer el contenido de una sección sin consultar cada producto. Se agrega `productos_ids` a `SeccionRespuesta` con los ids de los productos activos asignados a la sección.

## Alcance

### Dentro del alcance
- `SeccionRespuesta.productos_ids: list[int]` (decisión confirmada).
- Solo productos con `dado_de_baja = false` y `seccion_id` igual a la sección; los dados de baja se excluyen aunque sigan asignados (decisión confirmada).
- Valores por defecto derivados, a confirmar por el usuario:
  - Ids en orden ascendente.
  - Presente en toda respuesta de sección (POST, GET y PUT comparten `SeccionRespuesta`).
  - Una sección recién creada devuelve `[]`.
  - Cuentan los cinco subtipos; un combo vencido pero activo cuenta, porque solo `dado_de_baja` define la actividad.
- Actualización del encabezado de alcance y del escenario SEC-02 de la especificación principal, y de las pruebas afectadas.

### Fuera del alcance
- Nuevos endpoints, listados de productos por sección y cambios en los cuerpos de entrada: la asignación sigue haciéndose desde el producto.
- Objetos de producto embebidos, paginación, Frontend y migraciones.

## Capacidades

### Capacidades nuevas
- Ninguna.

### Capacidades modificadas
- `section-management`: la respuesta pasa a exponer `productos_ids` (activos, ascendentes); se reemplaza la prohibición de incluir productos en la respuesta y se ajusta SEC-02.

## Enfoque

Se respeta la convención de una carpeta por entidad: el cambio visible queda en `Backend/src/secciones/`. Restricción: `secciones` NO DEBE importar `productos`; `Seccion.productos` usa una referencia por cadena. Calcular los ids exige filtrar por `Producto.dado_de_baja` sin invertir esa dirección. Opciones: propiedad del modelo sobre la relación, consulta en la capa de router, o servicio en `productos`. La elección se fija en el diseño.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `Backend/src/secciones/schemas.py` | Modificado | Campo `productos_ids` en la respuesta |
| `Backend/src/secciones/models.py`, `router.py` o `services.py` | Modificado | Cálculo de los ids (según diseño) |
| `openspec/specs/section-management/spec.md` | Modificado | Alcance, entidad y SEC-02 vía delta |
| `Backend/tests/secciones/` | Modificado | Pruebas nuevas y SEC-02 actualizada |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Romper la dirección de importación | Media | Restricción explícita para el diseño; prueba o revisión de imports |
| Incluir productos dados de baja | Media | Escenarios con productos activos y dados de baja |
| Datos obsoletos tras el commit | Baja | Verificar con pruebas HTTP que POST/PUT reflejan el estado persistido |
| Pruebas que afirman la ausencia de productos fallan | Alta | Actualizar SEC-02 y sus pruebas en la misma tarea |

## Plan de reversión

Revertir los commits del cambio (esquema, cálculo, delta de especificación y pruebas). No hay cambios de esquema de base de datos, por lo que `app.db` no requiere recreación.

## Dependencias

- `secciones-posicion` archivado (cumplido).

## Criterios de éxito

- [ ] POST, GET y PUT devuelven `productos_ids`; una sección nueva devuelve `[]`.
- [ ] Solo figuran productos activos de esa sección, en orden ascendente, de cualquier subtipo.
- [ ] `secciones` no importa `productos`; la suite de pytest pasa.
