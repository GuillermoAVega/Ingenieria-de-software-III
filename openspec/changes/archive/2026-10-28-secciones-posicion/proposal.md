# Propuesta: Posición de las Secciones

## Intención

Las secciones no tienen un orden de presentación definido. Se agrega el atributo `posicion` a `Seccion` para determinar el orden en que se muestran, con unicidad garantizada y sin renumeraciones implícitas.

## Alcance

### Dentro del alcance
- `Seccion.posicion: int`, obligatorio en `POST /secciones` y `PUT /secciones/{id}` (reemplazo completo); ausente → 422.
- Entero >= 1; cero o negativo → 422.
- Único entre TODAS las secciones mediante el índice `ux_seccion_posicion`; colisión → 409. Nunca se desplazan otras secciones.
- Se permiten huecos: borrar una sección libera su posición y no se renumera nada.
- Doble colisión (`nombre` y `posicion`) → un único 409, con prioridad determinista: `nombre` primero, luego `posicion`.
- Nueva excepción `PosicionSeccionDuplicada` (409) en la jerarquía `ErrorSeccion`, registrada en `MANEJADORES_EXCEPCIONES`; cuerpo `{"detail": ...}` igual al 409 existente.
- `SeccionRespuesta` expone `posicion`.
- Actualización de pruebas y del fixture `crear_seccion` (posición única autoasignada si no se informa).

### Fuera del alcance
- Listado ordenado de secciones, reordenamiento masivo o intercambio atómico, migraciones, Frontend.

## Capacidades

### Capacidades nuevas
- Ninguna.

### Capacidades modificadas
- `section-management`: entidad (nuevo atributo y respuesta), validación de `posicion`, unicidad de `posicion`, prioridad de errores en alta y modificación.

## Enfoque

Se respeta la convención de una carpeta por entidad: los cambios quedan en `Backend/src/secciones/`. En el servicio, verificaciones explícitas previas en orden fijo (`nombre` → `posicion`) antes del commit; los índices únicos siguen siendo la garantía final, y `_confirmar` traduce el `IntegrityError` inspeccionando primero `nombre_normalizado` y luego `posicion`. El detalle y su justificación se fijan en el diseño.

## Consecuencias aceptadas

- Intercambiar dos posiciones requiere tres PUT, pasando una sección por una posición temporal libre.
- La base local `app.db` debe recrearse: `create_all` no agrega columnas.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `Backend/src/secciones/models.py` | Modificado | Columna e índice único |
| `Backend/src/secciones/schemas.py` | Modificado | Campo obligatorio `>= 1`; respuesta |
| `Backend/src/secciones/exceptions.py`, `router.py` | Modificado | Excepción 409 y manejador |
| `Backend/src/secciones/services.py` | Modificado | Verificaciones previas y traducción de errores |
| `Backend/tests/conftest.py`, `Backend/tests/secciones/`, `Backend/tests/productos/test_seccion_producto_http.py` | Modificado | Fixture y cuerpos con `posicion` |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| `app.db` existente sin la columna | Alta | Recrear la base local; documentarlo |
| Orden no determinista ante doble colisión | Media | Verificaciones previas ordenadas y prueba dedicada |
| Pruebas existentes fallan por `posicion` faltante | Alta | Tarea específica de actualización de fixture y cuerpos |

## Plan de reversión

Revertir los commits del cambio (columna, índice, esquema, excepción, manejador y pruebas) y recrear la base local.

## Dependencias

- `secciones-backend` archivado (cumplido).

## Criterios de éxito

- [ ] `posicion` obligatoria, entera y >= 1 en POST y PUT (422 en caso contrario).
- [ ] Posición repetida → 409; doble colisión → 409 de `nombre`.
- [ ] Borrar una sección libera su posición sin renumerar.
- [ ] La respuesta expone `posicion`; la suite de pytest pasa.
