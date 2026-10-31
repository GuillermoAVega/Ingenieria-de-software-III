```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:ff5d7d9186912230a4e324160ea340583873486eed650e15131013a8f04e428e
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 12/12
scenarios: 87/87
test_command: cd Backend && venv/bin/python -m pytest -q
test_exit_code: 0
test_output_hash: sha256:0747e4710454a1bc2a7565c692a47fea6b452f844bbc33df68180d6a452f8a14
build_command: cd Backend && ENV=dev venv/bin/python -c "import src.main"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio**: secciones-backend
**Versión**: N/A
**Modo**: Strict TDD

### Completitud
| Métrica | Valor |
|---------|-------|
| Tareas totales | 23 |
| Tareas completas | 23 |
| Tareas incompletas | 0 |

Los 72 escenarios del Anexo A (44 SEC y 28 CAT-S) tienen al menos una prueba cuyo nombre o `id` de parametrización contiene `test_sec_NN` o `test_cat_s_NN`. SEC-12 y SEC-13 figuran como `pytest.param(id="test_sec_12_mayusculas")` y `test_sec_13_espacios`, en servicio y en HTTP. Los 15 escenarios restantes del delta de product-catalog (MODIFIED) son preexistentes y los cubren las pruebas del cambio `productos-backend`, que siguen en verde.

### Ejecución de compilación y pruebas
**Compilación (importación de la aplicación)**: aprobada, código de salida 0, sin salida.

**Pruebas**: 592 aprobadas, 0 fallidas, 0 omitidas (1 advertencia de deprecación de `httpx` en `starlette.testclient`, ajena al cambio).

```text
cd Backend && venv/bin/python -m pytest -q                  -> 592 passed, 1 warning
cd Backend && ENV=dev venv/bin/python -c "import src.main"  -> exit 0
```

`Backend/app.db` no existe tras la verificación. `git status` solo muestra `.atl/` sin seguimiento (previo a esta fase).

**Cobertura**: no disponible (`coverage: null` en `openspec/config.yaml`).

### Matriz de cumplimiento de la especificación
| Requisito | Escenarios | Pruebas representativas | Resultado |
|-----------|-----------|--------------------------|-----------|
| Entidad Seccion | SEC-01, 02 | `test_modelos.py`, `test_router.py::test_sec_02`, `test_schemas.py::test_sec_02` | COMPLIANT |
| Validación de campos | SEC-03..10, 39..43 | `test_schemas.py`, `test_router.py` (422, recorte, límites, `null`) | COMPLIANT |
| Unicidad del nombre | SEC-11..18, 21 | `test_servicios.py` (`test_sec_11_a_13`), `test_router.py` (409 y 422 sobre 409) | COMPLIANT |
| Alta | SEC-19, 20 | `test_servicios.py`, `test_router.py` (201 y cuerpo) | COMPLIANT |
| Consulta por id | SEC-22..24 | `test_router.py` (200 igual al creado, 404, 405 en `GET /secciones`) | COMPLIANT |
| Modificación | SEC-25..30, 44 | `test_router.py`, `test_servicios.py`, `test_seccion_producto_http.py::test_sec_30` | COMPLIANT (ver advertencia 2) |
| Borrado físico | SEC-31..33 | `test_router.py` (204 sin cuerpo, 404, repetido 404) | COMPLIANT |
| Desvinculación al borrar | SEC-34..38 | `test_seccion_producto.py` (BD, `DELETE` crudo y `PRAGMA`), `test_router.py` (HTTP, cinco subtipos, combo vencido, postre de baja) | COMPLIANT |
| Asignación de producto a una sección | CAT-S-01..28 | `test_seccion_producto*.py`, `platos/bebidas/postres/menus_ejecutivos/combos test_router.py`, pruebas de servicios | COMPLIANT (ver advertencia 3) |
| Rutas ABM, campos específicos y combos vencidos (MODIFIED) | 15 escenarios preexistentes | Pruebas de `productos-backend` más `test_cat_s_22..27` | COMPLIANT |

**Cumplimiento**: 87/87 escenarios (12/12 requisitos).

### Corrección (evidencia estática)
| Aspecto | Estado | Notas |
|---------|--------|-------|
| Códigos y cuerpos HTTP | Implementado | 201/200/204/404/405/409/422 verificados en pruebas HTTP. El 422 `seccion_inexistente` se compara con el cuerpo completo (`loc`, `type`, `ids`) en `test_cat_s_08`. |
| Prioridades de error | Implementado | 422 esquema, 404, 409 combo vencido, 422 referencias (componentes y luego sección), 409 componentes inactivos, 409 nombre; cubiertas por CAT-S-14..20. |
| `seccion_id` en `_sin_otros_cambios` | Implementado | `combos/services.py` (`datos.seccion_id == combo.seccion_id`); CAT-S-22..26. |
| Rollback ante errores de dominio | Implementado | `crear_producto`, `actualizar_producto`, `crear_menu`, `actualizar_menu`, `crear_combo` y `actualizar_combo` capturan `ErrorDominio`; `secciones._confirmar` y `obtener_seccion` revierten. |

### Coherencia con el diseño
| Decisión | ¿Se sigue? | Notas |
|----------|-----------|-------|
| 1. Dirección de dependencias | Sí | Sin importaciones de `src.productos` en `Backend/src/secciones`. `productos.registro` importa `secciones.models`; `productos.services` usa `Seccion`. |
| 2. `normalizar_nombre` en `src/texto.py` | Sí | La importan `productos/services.py` y `secciones/services.py`. |
| 3. Índice único y traducción a 409 | Sí | `ux_seccion_nombre_normalizado` UNIQUE; `_confirmar` traduce el `IntegrityError` que menciona `nombre_normalizado`, con rollback; los ajenos se propagan. |
| 4. `passive_deletes=True` y `ON DELETE SET NULL` | Sí | `secciones/models.py` y `productos/models.py`; pruebas de `PRAGMA foreign_keys` y de que el borrado no carga `Seccion.productos`. |
| 5. Jerarquía de excepciones separada | Sí | `ErrorSeccion` disjunta de `ErrorDominio`; Python puro. |
| 6. `SeccionInexistente(ErrorDominio)` en productos | Sí | Manejador 422 en `productos/router.MANEJADORES_EXCEPCIONES`. |
| 7. Carga de mappers vía `registro.py` | Sí | `registro.py` importa `Seccion`; `main.py` importa `registro`. |
| 8. Base existente | Sí | Sin migración; `app.db` ausente. |
| Orden de validación en menús y combos | Sí | `exigir_activos=False`, luego `verificar_seccion`, luego actividad; en el alta de combo, `FechaHastaVencida` primero. |
| Routers delgados, código en español, excepciones puras | Sí | `secciones/router.py` solo delega en `services`; las excepciones no importan FastAPI. |
| `main.py` | Sí | Registra el router y recorre ambos diccionarios de manejadores. |

### Cumplimiento TDD (Strict)
| Verificación | Resultado | Detalle |
|--------------|-----------|---------|
| Evidencia TDD informada | Parcial | El artefacto `apply-progress` (Engram #62) está desactualizado: reporta fases 1-5, 581 pruebas y la fase 6 pendiente, y no incluye la tabla "TDD Cycle Evidence". |
| Todas las tareas tienen pruebas | Sí | 23/23 tareas con archivos de prueba existentes. |
| GREEN confirmado | Sí | 592/592 pruebas aprobadas en la ejecución actual. |
| Triangulación | Adecuada | Parametrizaciones por subtipo y por variante de nombre. |

### Calidad de aserciones
Muestra leída: pruebas de secciones (`test_router.py`, `test_servicios.py`), `test_seccion_producto*.py` y las de CAT-S-16, 17, 20, 22..27 de combos y menús. No se encontraron tautologías, bucles fantasma ni aserciones sin llamada a código de producción. Las pruebas verifican estados y cuerpos y comprueban el estado posterior con un `GET`. Hallazgos menores en las advertencias 2 y 3.

### Capas de pruebas
Unidad (texto, esquemas, modelos, excepciones), integración de servicio y BD (SQLite en memoria) e integración HTTP (`TestClient`). Sin pruebas E2E (`e2e: false`).

### Problemas encontrados
**CRITICAL**: ninguno.

**WARNING**:
1. El artefacto `apply-progress` (Engram #62) está desactualizado y no contiene la tabla "TDD Cycle Evidence" que exige Strict TDD. Se clasifica como advertencia y no como crítico porque el artefacto existe, las 23 tareas están marcadas y el historial de commits muestra pruebas junto a cada funcionalidad; la conducta se comprobó en ejecución. Se recomienda actualizarlo antes de archivar.
2. `tests/productos/test_seccion_producto_http.py::test_sec_30_...`: tras `PUT /secciones/{id}` el Plato se reenvía con su `seccion_id` mediante un `PUT` y luego se compara, por lo que la aserción no distingue "la modificación no tocó el producto" de "el PUT del Plato lo reasignó". El escenario queda cubierto por `tests/secciones/test_servicios.py::test_sec_30_...`, a nivel de servicio. Conviene agregar un `GET` del Plato justo después del `PUT /secciones`.
3. Algunas pruebas de prioridad solo comprueban el código de estado: `test_cat_s_16` (solo `== 409`), `test_sec_28`, `test_sec_29` y `test_sec_21`. Son válidas porque los datos aíslan la regla, pero no fijan `detail` ni `type`.

**SUGGESTION**:
1. Numerar los 15 escenarios MODIFIED del delta, o agregarlos al Anexo A, para que la trazabilidad cubra los 87.
2. Incorporar una herramienta de cobertura (`coverage: null`) para medir los archivos cambiados.
3. La advertencia de `httpx` en `starlette.testclient` no afecta al cambio; evaluar `httpx2` más adelante.

### Veredicto
PASS WITH WARNINGS

Los 12 requisitos y 87 escenarios están implementados y probados en ejecución (592 pruebas aprobadas, importación correcta), el diseño se respeta en todos los puntos revisados y no hay problemas críticos; quedan tres advertencias de evidencia y de calidad de aserciones.


### Resolución posterior

- **WARNING 2 resuelto.** `test_sec_30` ahora consulta el Plato con `GET` inmediatamente después del `PUT /secciones`, sin reenviarlo, y verifica que conserva su `seccion_id`. La suite pasa con 592 pruebas.
- **WARNING 1** corresponde al registro de progreso en Engram, fuera del repositorio; no afecta al código ni a las pruebas.
- **WARNING 3** se acepta: los datos de esas pruebas aíslan la regla verificada.
- **Veredicto final: PASS.**
