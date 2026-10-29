```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:60f2ec0861faa0e9cab059c84f04f663a03e105d2b01c7ddf63cae14c7098f66
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 5/5
scenarios: 39/39
test_command: cd Backend && venv/bin/python -m pytest -q
test_exit_code: 0
test_output_hash: sha256:bd09ef7cbf9b24eb8ad67aba2f9ad19d070957830aa8fac6417a03edb7276a1d
build_command: cd Backend && ENV=test DB_URL=sqlite:// venv/bin/python -c "import src.main"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio**: secciones-productos-ids
**Versión**: N/A (delta sobre `section-management`)
**Modo**: TDD estricto
**Commit evaluado**: da9249a (rama Gonza-Guille)

### Completitud

| Métrica | Valor |
|---------|-------|
| Tareas totales | 13 |
| Tareas completas | 13 |
| Tareas incompletas | 0 |

Todas las tareas (1.1 a 4.2) están marcadas como completas y coinciden con el estado del código: la propiedad y el campo existen, y las pruebas descritas en cada tarea están presentes.

### Ejecución de compilación y pruebas

**Compilación (importación de la aplicación)**: aprobada, código de salida 0, sin salida.

```text
cd Backend && ENV=test DB_URL=sqlite:// venv/bin/python -c "import src.main"
```

Se usó `ENV=test` con SQLite en memoria; no se tocó `Backend/app.db`.

**Pruebas**: 701 aprobadas, 0 fallidas, 0 omitidas (código de salida 0).

```text
cd Backend && venv/bin/python -m pytest -q
701 passed, 1 warning
```

La advertencia es una deprecación de `httpx` en `starlette.testclient`, ajena al cambio.

**Cobertura**: no disponible (no hay herramienta configurada).

### Matriz de cumplimiento de la especificación

Totales del delta: 5 requisitos y 39 escenarios (44 encabezados, coincide con el conteo del estado nativo). Los 17 escenarios IDS y los tres SEC modificados tienen prueba nombrada y aprobada en la ejecución completa.

| Requisito | Escenario | Prueba | Resultado |
|-----------|-----------|--------|-----------|
| Entidad Seccion | SEC-01 mappers | prueba existente de modelos (suite completa) | COMPLIANT |
| Entidad Seccion | SEC-02 | `test_router.py > test_sec_02_la_respuesta_incluye_productos_ids_y_no_el_estado_de_baja`; `test_schemas.py > test_sec_02_respuesta_solo_expone_id_nombre_subtitulo_posicion_y_productos_ids` | COMPLIANT |
| Entidad Seccion | POS-01 | `test_router.py > test_pos_01_la_consulta_incluye_la_posicion` | COMPLIANT |
| Entidad Seccion | IDS-01 | `test_router.py > test_ids_01_productos_ids_es_lista_de_enteros` | COMPLIANT |
| Alta de sección | SEC-19, SEC-20, SEC-21, POS-22, POS-23, POS-24 | pruebas existentes de `test_router.py` (suite completa) | COMPLIANT |
| Alta de sección | IDS-02 | `test_router.py > test_ids_02_el_alta_devuelve_productos_ids_vacio` y `..._aunque_existan_otros_productos`; `test_modelos.py > test_ids_02_...` | COMPLIANT |
| Consulta por id | SEC-22 | `test_router.py > test_sec_22_obtener_una_seccion_existente_incluye_productos_ids` | COMPLIANT |
| Consulta por id | SEC-23, SEC-24 | pruebas existentes (suite completa) | COMPLIANT |
| Consulta por id | IDS-03 | `test_router.py > test_ids_03_la_consulta_devuelve_los_ids_de_los_productos_activos` | COMPLIANT |
| Modificación | SEC-25 | `test_router.py > test_sec_25_el_put_incluye_productos_ids_vigentes` | COMPLIANT |
| Modificación | SEC-26 a SEC-29, POS-25 a POS-28 | pruebas existentes (suite completa) | COMPLIANT |
| Modificación | SEC-30 | `test_router.py > test_sec_30_la_modificacion_no_altera_los_productos_asignados` | COMPLIANT |
| Modificación | IDS-04 | `test_router.py > test_ids_04_el_put_devuelve_el_estado_persistido` | COMPLIANT |
| Modificación | IDS-05 | `test_router.py > test_ids_05_enviar_productos_ids_en_el_put_no_cambia_la_asignacion` | COMPLIANT |
| Ids de productos activos | IDS-06 | `test_router.py > test_ids_06_get_incluye_solo_productos_activos`; `test_modelos.py > test_ids_06_...` | COMPLIANT |
| Ids de productos activos | IDS-07 | `test_router.py > test_ids_07_...`; `test_modelos.py > test_ids_07_...` | COMPLIANT |
| Ids de productos activos | IDS-08 | `test_router.py > test_ids_08_get_devuelve_ids_ascendentes`; `test_modelos.py > test_ids_08_...` | COMPLIANT |
| Ids de productos activos | IDS-09 | `test_router.py > test_ids_09_get_cuenta_los_cinco_subtipos`; `test_modelos.py > test_ids_09_...` | COMPLIANT |
| Ids de productos activos | IDS-10 | `test_router.py > test_ids_10_...`; `test_modelos.py > test_ids_10_...` | COMPLIANT |
| Ids de productos activos | IDS-11 | `test_router.py > test_ids_11_dar_de_baja_un_producto_lo_quita` | COMPLIANT |
| Ids de productos activos | IDS-12 | `test_router.py > test_ids_12_reactivar_un_producto_lo_reincorpora` | COMPLIANT |
| Ids de productos activos | IDS-13 | `test_router.py > test_ids_13_cambiar_la_seccion_de_un_producto_lo_mueve` | COMPLIANT |
| Ids de productos activos | IDS-14 | `test_router.py > test_ids_14_desasignar_un_producto_lo_quita` | COMPLIANT |
| Ids de productos activos | IDS-15 | `test_router.py > test_ids_15_...`; `test_modelos.py > test_ids_15_...` | COMPLIANT |
| Ids de productos activos | IDS-16 | `test_router.py > test_ids_16_no_quedan_ids_obsoletos_tras_borrar_y_crear_una_seccion` | COMPLIANT |
| Ids de productos activos | IDS-17 | `test_router.py > test_ids_17_no_existe_listado_de_productos_por_seccion` | COMPLIANT |

**Resumen de cumplimiento**: 39/39 escenarios cumplen. Los escenarios SEC/POS que el delta no modifica se respaldan en la suite existente, que sigue en verde; no se auditó una por una su correspondencia con el texto.

**Calidad de las aserciones (muestra leída)**: `test_sec_02` compara el cuerpo completo con `==` y verifica 201 y 200; `test_ids_04` verifica 200, el cuerpo y la igualdad con el GET siguiente; `test_ids_06`, `07`, `11`, `13`, `14` consultan por HTTP y comparan listas exactas, y `11` además verifica `seccion_id` y `dado_de_baja` del producto; `test_ids_16` verifica 204, la lista vacía de la sección nueva y que el producto subsiste con `seccion_id` nulo; `test_ids_17` verifica 404. Las pruebas aseveran códigos de estado y cuerpos, no solo nombres.

### Correctitud (evidencia estática)

| Requisito | Estado | Notas |
|-----------|--------|-------|
| Propiedad `Seccion.productos_ids` | Implementado | `sorted(p.id for p in self.productos if not p.dado_de_baja)` en `Backend/src/secciones/models.py` |
| Campo en la respuesta | Implementado | `productos_ids: list[int]` después de `posicion` en `SeccionRespuesta` (`from_attributes`) |
| Sin objetos de producto embebidos ni listados | Implementado | No hay endpoints nuevos; IDS-17 devuelve 404 |
| Sin cambios en los cuerpos de entrada | Implementado | `SeccionCrear` no cambió; IDS-05 y la prueba de apoyo del alta confirman que `productos_ids` del cuerpo se ignora |

### Coherencia (diseño)

| Decisión | ¿Se siguió? | Notas |
|----------|-------------|-------|
| 1. Propiedad que filtra solo por `dado_de_baja`, orden ascendente | Sí | No filtra por vigencia del combo (IDS-10) ni por subtipo |
| 1. Sin importar `productos` | Sí | `rg` sin resultados en `src/secciones`; `test_productos_ids_secciones_no_importa_productos` revisa con `ast` los cuatro módulos |
| 2. Carga diferida sin cambios en la relación | Sí | La relación `productos` no se modificó (`lazy` por defecto, `passive_deletes=True`) |
| 3. Un único SELECT sobre `producto`, sin tablas de subtipos | Sí | `test_productos_ids_emite_un_unico_select_sobre_producto` verifica 1 sentencia, 1 SELECT y ninguna tabla de subtipo, con los cinco subtipos |
| 4. Campo en `SeccionRespuesta` tras `posicion` | Sí | |
| 5. Frescura tras commit | Sí | Sin código adicional (`expire_on_commit` por defecto, sin overrides en `src`); fijado por IDS-02 (alta), IDS-04 y SEC-25 (PUT) |
| 6. Sin cambio de esquema de BD | Sí | La propiedad no es columna; no hay migraciones; `Backend/app.db` sin tocar |

### Convenciones

- Código en español: nombres, docstring y comentarios del cambio están en español.
- Routers delgados: `router.py` y `services.py` no cambiaron; el único cambio de código fuente son `models.py` (+5 líneas) y `schemas.py` (+1 línea).
- El diff del cambio en `Backend/src` se limita a los dos archivos previstos; `.atl/` y `Backend/app.db` figuran sin seguimiento desde antes y no se modificaron.

### Problemas encontrados

**CRITICAL**: ninguno.

**WARNING**:
1. Las comprobaciones de sensibilidad exigidas por las tareas 3.1 y 3.7 (invertir temporalmente el filtro, el orden o agregar un import prohibido) no pueden comprobarse desde el código final, porque no dejan rastro. Esta verificación, de solo lectura, no las repitió. Los controles automáticos que sí existen (comparación de listas exactas con productos dados de baja y en desorden, conteo de sentencias, recorrido `ast`) cubren esos riesgos.
2. No hay medición de cobertura disponible en el proyecto.

**SUGGESTION**:
1. Existen pares de pruebas con el mismo prefijo de escenario (`test_sec_22`, `test_sec_25` en `test_router.py`, y `test_sec_22`, `test_sec_25`, `test_sec_30` en `test_servicios.py`); son legítimos (uno por nivel), pero conviene mantener la convención de nombres para facilitar la trazabilidad.
2. Si el volumen de productos por sección crece, evaluar la alternativa (c) del diseño (relación filtrada y ordenada en SQL).
3. Si en el futuro se agrega un listado de secciones, usar `selectinload` en su propia consulta, como documenta el diseño, para evitar N+1.

### Veredicto

PASS WITH WARNINGS

La implementación cumple los 39 escenarios y las decisiones del diseño; los 701 tests y la importación de la aplicación pasan. Las advertencias son de evidencia no reproducible (sensibilidad) y de cobertura no medida, no de defectos.

### Resolución posterior

- **WARNING 1 resuelto.** Las comprobaciones de sensibilidad se ejecutaron durante la fase de aplicación: ocho mutaciones de `Seccion.productos_ids` (filtro invertido, sin filtro de baja, sin orden, orden descendente, filtro por vigencia, solo platos, carga extra por fila e importación de `productos`) hicieron fallar al menos una prueba cada una; el código de producción se restauró exactamente (`git diff -- Backend/src` vacío).
- **WARNING 2 aceptado.** El proyecto no tiene herramienta de cobertura; queda fuera del alcance de este cambio.
- **Veredicto final: PASS.**
