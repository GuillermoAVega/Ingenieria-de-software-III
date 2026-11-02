# Informe de verificación: secciones-posicion

**Veredicto**: PASS WITH WARNINGS

## Resultados de ejecución
- `cd Backend && venv/bin/python -m pytest -q`: 668 pasaron, 0 fallaron (1 aviso de deprecación de httpx en Starlette, ajeno al cambio).
- `ENV=test DB_URL=sqlite:// venv/bin/python -c "import src.main"`: correcto (sin errores de mappers ni de importación).
- No se usó `ENV=dev`; `Backend/app.db` no fue tocado.

## Cumplimiento del diseño
- `posicion: int = Field(ge=1)` obligatoria, en modo laxo (sin `strict`): cumple. `SeccionActualizar = SeccionCrear`.
- Índice único `ux_seccion_posicion` en `models.py` y columna `nullable=False`: cumple.
- `_verificar_unicidad`: nombre antes que posición, excluye la fila propia (`excluir_id`) en PUT, `rollback()` antes de lanzar: cumple.
- `_confirmar`: traduce `nombre_normalizado` antes que `seccion.posicion`, revierte siempre y propaga errores ajenos: cumple. Está documentado como red de seguridad (carrera), no como garantía de prioridad.
- `PosicionSeccionDuplicada` hereda de `ErrorSeccion`, se registra en `MANEJADORES_EXCEPCIONES` y responde 409 con `{"detail": ...}`: cumple.
- Fixture `crear_seccion` autoasigna posiciones desde 1001: cumple.
- `secciones` no importa `productos` (solo referencia por cadena en el `relationship`): cumple.
- Convenciones: código en español, routers delgados, excepciones en Python puro: cumple.
- Fuera de alcance (listado ordenado, reordenamiento masivo, intercambio atómico, migraciones, Frontend): no implementado, correcto.

## Cobertura de escenarios
POS-01..29 tienen pruebas con nombres trazables en `tests/secciones/` (router, servicios, esquemas, modelos, manejadores, excepciones, fábrica). Se leyó una muestra del cuerpo de las pruebas de router y servicios y se confirmaron códigos y cuerpos reales, no solo nombres:
- POS-02/03/04-08/06: 422 y ausencia de filas creadas.
- POS-10: 422 y GET posterior con nombre, subtítulo y posición intactos.
- POS-11/12/16: 409 con `{"detail": "Ya existe una sección en esa posición"}`, claves exactamente `{"detail"}` y sin desplazamiento.
- POS-13/21/26: 409 y ambas secciones intactas (comparación completa del cuerpo).
- POS-23/26: 409 con el mensaje de nombre.
- POS-24/28: 422 con prioridad sobre 409.
- POS-27: 404 con prioridad sobre 409.
- POS-17..20: 201/204/200 y posiciones finales verificadas.
- POS-29: 201 con valor `int` 3 para `"3"` y `3.0`.
- Ruta de carrera de `_confirmar`: probada con `monkeypatch` y ambos órdenes del mensaje de SQLite.

## Problemas críticos
Ninguno.

## Advertencias
1. `_confirmar` detecta el índice por subcadenas del mensaje de SQLite (`"nombre_normalizado"`, `"seccion.posicion"`). Es válido para el motor actual (SQLite), pero no es portable: PostgreSQL/MySQL informan el nombre del índice (`ux_seccion_posicion`) y la traducción caería en `raise` (500). Solo afecta la ruta de carrera, ya que la verificación previa cubre el caso normal.
2. Modo laxo de Pydantic: un booleano (`true`) se acepta como `1`. No contradice la especificación (no la menciona), pero es un comportamiento no cubierto por pruebas.

## Sugerencias
1. Ampliar la detección en `_confirmar` para incluir también `ux_seccion_posicion` y `ux_seccion_nombre_normalizado`, con una prueba por cada variante.
2. Decidir y documentar si `posicion = true` debe rechazarse (por ejemplo con un validador `before` que excluya `bool`).
3. Las pruebas de carrera de la ruta de `PUT` y del alta usan `monkeypatch`; considerar una prueba de concurrencia real solo si se migra de motor.
4. Las tareas están marcadas como completas y el Anexo A de `tasks.md` mapea POS-01..29 con pruebas existentes; no se detectaron desajustes.

### Resolución posterior

- **WARNING 1 aceptado.** El proyecto usa SQLite; la traducción por mensaje es una red de seguridad que no se alcanza con `BEGIN IMMEDIATE`. Si se migra de motor, se revisará junto con el resto de la capa de datos.
- **WARNING 2 aceptado.** Se comprobó que `true` se acepta como `1` tanto en `posicion` como en `cant_personas`: es parte del modo laxo aprobado por el usuario y mantiene la consistencia del proyecto.
- **Veredicto final: PASS.**
