```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:49136ca0992bb6981110a65a3fdcfefc36e6ebcf290091fd504015b802d9d049
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 16/16
scenarios: 69/69
test_command: cd Backend && venv/bin/python -m pytest -q
test_exit_code: 0
test_output_hash: sha256:5deb01bc30dc48f4e8bc185dca73a876a8543d09cb6a4bd37f7a944bcf5e1059
build_command: cd Backend && ENV=dev venv/bin/python -c "import src.main"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio**: productos-backend
**Modo**: TDD estricto (activo)
**Commit verificado**: 079f105 (rama Gonza-Guille)
**Alcance**: ABM por subtipo y `GET /productos/<subtipo>/{id}`. Fuera de alcance: CAT-04, CAT-05, CAT-06, CAT-09, LD-24, LD-25 y LD-26. Quedan 69 escenarios vigentes (46 CAT y 23 LD) y 16 requisitos.

### Completitud

| Métrica | Valor |
|---------|-------|
| Tareas totales | 33 |
| Tareas completas | 33 |
| Tareas incompletas | 0 |

Todas las tareas de `tasks.md` están marcadas `[x]`. La Fase 8 figura como eliminada y se agregó la tarea 2.7 (retirar `ProductoRespuesta`). El código coincide: `rg ProductoRespuesta` solo devuelve `ProductoRespuestaBase`, y no existen `listar` ni `incluir_bajas`.

### Ejecución de build y pruebas

**Build** (importación de la aplicación): aprobado.

```text
cd Backend && ENV=dev venv/bin/python -c "import src.main"
exit code 0, sin salida
```

**Pruebas**: 380 aprobadas, 0 fallidas, 0 omitidas.

```text
cd Backend && venv/bin/python -m pytest -q
380 passed, 1 warning in 6.00s
```

La única advertencia es `StarletteDeprecationWarning` (uso de `httpx` con `starlette.testclient`). No pertenece al cambio y es irrelevante para el comportamiento.

**Cobertura**: no disponible (el proyecto no configura herramienta de cobertura).

### Matriz de cumplimiento de especificaciones

Los nombres de las pruebas usan el identificador del escenario (`test_cat_NN_...`, `test_ld_NN_...`). Un script confirmó que cada escenario vigente tiene al menos una prueba a nivel HTTP, salvo CAT-02, CAT-03 y CAT-50, que se prueban a nivel de modelo o infraestructura, como indica la tarea 9.2. Además se leyeron las aserciones de una muestra: `combos/test_router.py` (CAT-34 a CAT-49, LD-17, LD-18, LD-20), `test_baja_logica.py` (LD-01 a LD-22), `menus_ejecutivos/test_router.py` y `platos/test_router.py`.

| Requisito | Escenarios | Pruebas (muestra) | Resultado |
|-----------|-----------|-------------------|-----------|
| Jerarquía abstracta Producto | CAT-01, CAT-02, CAT-03 | `test_manejadores.py::test_cat_01_...` (405 y nada creado), `test_modelos.py::test_cat_02_...`, `test_cat_03_...` | COMPLIANT |
| Rutas ABM por subtipo | CAT-07, 08, 10, 11, 12, 13, 14 | `<sub>/test_router.py`: 201 con id, 404 por subtipo incorrecto, `dado_de_baja` visible, PUT como reemplazo completo, 422 antes que 404 | COMPLIANT |
| Validación de campos comunes | CAT-15 a CAT-26 | `platos/test_router.py`, parametrizado por prefijo de subtipo. Aserciones: 422 para vacío, espacios, 101 caracteres, precio no positivo y descripción de 501; recorte a "Milanesa"; 409 por duplicados (exacto, mayúsculas, espacios); 201 con tildes y tras la baja; 200 con el mismo nombre | COMPLIANT |
| Campos específicos por subtipo | CAT-27, 28, 29 | `bebidas/test_router.py`, `platos/test_router.py`, `combos/test_router.py` | COMPLIANT |
| Composición de MenuEjecutivo | CAT-30 a CAT-33 | `menus_ejecutivos/test_router.py`: 201, 422 con `loc ["body","plato_id"]`, 422 para id inexistente, 409 con ids | COMPLIANT |
| Composición de ComboPromocion | CAT-34 a CAT-40 | `combos/test_router.py`: 201, 422 (vacío, duplicados, tipo incorrecto con `ids`, `loc fecha_hasta`), 409 con `ids`; la prueba de `fecha_hasta == hoy` confirma la frontera | COMPLIANT |
| Precios manuales de compuestos | CAT-41 | `test_cat_41_...` | COMPLIANT |
| Las actualizaciones de compuestos revalidan componentes | CAT-42, 43, 44 | 409 y menú sin cambios; 200 con el menú de baja y componente inactivo (con `dado_de_baja=true` y sin el campo); 422 por `postre_id=999` | COMPLIANT |
| Los combos vencidos son inmutables | CAT-45 a CAT-49 | `combos/test_router.py`: 409 y sin cambios; reactivar da 409; baja por PUT da 200; repetida da 200 con cuerpo idéntico antes y después; baja con nuevo precio da 409 con estado idéntico | COMPLIANT |
| Infraestructura de pruebas | CAT-50 | `test_infraestructura.py` (2 pruebas: motor en memoria y entorno aislado) | COMPLIANT |
| DELETE lógico | LD-01, 02, 03 | `test_baja_logica.py`: 204 con `content == b""`, GET con `dado_de_baja` true, 404 (id desconocido y de otro subtipo), DELETE repetido da 204 | COMPLIANT |
| Cambio de estado vía PUT | LD-04 a LD-09 | 422 y sigue activo; PUT `false` sobre activo da 200 con edición normal; `nombre=""` da 422; PUT sin el campo conserva la baja; baja y reactivación por PUT dan 200 | COMPLIANT |
| RESTRICT en la baja | LD-10 a LD-15 | 409 con `bloqueantes` exactos y ordenados; la baja no se aplica (comprueba por GET y por sesión); combo futuro bloquea; menú de baja y combo vencido no bloquean; combo vencido activo da 204 | COMPLIANT |
| Compuestos se dan de baja libremente | LD-16, 17, 18 | `menus_ejecutivos/test_router.py`, `combos/test_router.py` | COMPLIANT |
| Validación de la reactivación | LD-19, 20, 21, 22 | 409 con el menú aún de baja; 200; 409 por nombre en conflicto con el estado intacto; 200 | COMPLIANT |
| Invariante de componentes activos | LD-23 | `test_invariante.py` (2 pruebas: secuencias mixtas y baja bloqueada) y `test_ld_10_y_ld_23_...` | COMPLIANT |

**Resumen**: 69 de 69 escenarios COMPLIANT. 16 de 16 requisitos con implementación y prueba.

### Correctitud (evidencia estática)

| Requisito | Estado | Notas |
|-----------|--------|-------|
| Herencia de tablas unidas, discriminador `tipo` | Implementado | `Producto` abstracto (`polymorphic_abstract` y `__new__` que lanza `TypeError`); subtipos con `polymorphic_identity` |
| Relaciones bidireccionales | Implementado | Plato.menus/combos, Postre.menus/combos, Bebida.combos y MenuEjecutivo.plato/postre con `back_populates`; `inherit_condition` y `foreign_keys` explícitos |
| `POST /productos` da 405 | Implementado | Ruta explícita `POST ""`; sin GET en `/productos` |
| Rutas por id con `{producto_id:int}` | Implementado | Los cinco routers declaran POST, GET por id, PUT y DELETE |
| Unicidad de nombre | Implementado | `nombre_normalizado` (strip y casefold), índice parcial único como respaldo, `IntegrityError` traducido a 409 |
| Atomicidad | Implementado | `configurar_sqlite` con `BEGIN IMMEDIATE` y `PRAGMA foreign_keys`; rollback ante error de dominio |
| PUT como reemplazo completo; `dado_de_baja` omitido conserva el estado | Implementado | `asignar_campos_comunes`; `nuevo_estado=None` no hace nada |

### Coherencia con el diseño

| Decisión | Seguida | Notas |
|----------|---------|-------|
| Reglas de importación | Sí | `productos/services.py` no importa FastAPI ni subpaquetes; solo `registro`, `models`, `schemas` y `exceptions`. Fuera de `*/router.py`, ningún módulo de `src/productos` importa `fastapi`. `registro.py` es el único módulo que importa los cinco subpaquetes (solo sus `models`). Ningún `<sub>/models.py` importa otro subpaquete. `productos/router.py` los compone, como establece el diseño |
| Prioridad de errores 422, 404, combo vencido, componentes, nombre | Sí | `actualizar_combo`: Pydantic, `obtener` (404), vencido (409), `resolver_componentes_combo` (422 siempre, 409 solo si queda activo), y nombre y estado en `actualizar_producto`. `actualizar_menu` es análogo |
| Formas de respuesta y contrato de errores | Sí | 404 y 409 con `{"detail"}`; 422 de componentes y `fecha_hasta` con la forma de Pydantic (`loc`, `msg`, `type`, `ids`); `ComponenteInactivo` agrega `ids`; `BajaRestringida` agrega `bloqueantes` ordenados; `ComboVencidoInmutable` se resuelve por MRO desde `ErrorConflicto` |
| Función única de cambio de estado | Sí | `aplicar_cambio_estado` con el gancho `verificar_reactivacion`; la usan DELETE y todos los PUT |
| `obtener_hoy` inyectable | Sí | `Depends(services.obtener_hoy)`; las pruebas lo sobrescriben |
| Excepciones de dominio sin FastAPI | Sí | `productos/exceptions.py` y `combos/exceptions.py` son Python puro |
| Estructura de módulos (7 archivos por subpaquete) | Sí | Presentes en los cinco subpaquetes; los delgados llevan docstring |
| `main.py` | Sí | Importa `registro` antes de `create_all`, incluye el router y registra `MANEJADORES_EXCEPCIONES` |
| RESTRICT mediante `RESTRICT_POR_TIPO` | Sí | Consulta UNION construida desde el mapa; `fecha_hasta >= hoy`; los compuestos no figuran |

### Convenciones

- Código en español (identificadores, docstrings y mensajes): sí.
- Routers delgados: sí. Solo delegan en servicios y no contienen reglas de negocio.
- Excepciones de dominio en Python puro: sí. Las raíz `DetailedHTTPException` de `src/exceptions.py` no se usan en `productos`.

### Problemas encontrados

**CRITICAL**: ninguno.

**WARNING**:

1. **Listas de componentes de combo con valor por defecto.** `ComboCrear` declara `platos_ids`, `bebidas_ids` y `postres_ids` con `= []`. El requisito "Campos específicos por subtipo" dice que el combo DEBE requerir las tres listas. La tarea 2.5 pedía que la falta de una lista diera error. Hoy omitir una lista se acepta como vacía mientras haya al menos un id en otra. Las pruebas no lo detectan: `test_combo_con_listas_omitidas_se_rechaza` solo cubre omitir las tres a la vez, y la falla ya la produce la regla de "al menos un componente". Ningún escenario vigente lo exige, y el PUT como reemplazo completo hace que omitir equivalga a vacío. Se recomienda decidir si se exigen las tres listas (sin valor por defecto) o aclarar la especificación.
2. **Aceptado por el usuario, solo informativo.** Un PUT sobre un combo activo puede fijar `fecha_hasta` en el pasado. La especificación solo exige `fecha_hasta >= hoy` en la creación. No se considera un fallo.

**SUGGESTION**:

1. La respuesta 405 de `POST /productos` se genera con `HTTPException(405)` y no incluye el encabezado `Allow`. Cumple el escenario CAT-01, pero RFC 9110 recomienda ese encabezado.
2. Agregar una prueba que envíe un combo con una de las tres listas omitidas (y con ids en las otras), para fijar la decisión del WARNING 1 en cualquiera de los dos sentidos.
3. El proyecto no tiene herramienta de cobertura. Si se agrega, `src/productos` serviría como línea base.

### Veredicto

**PASS WITH WARNINGS.** Las 33 tareas están completas. Los 69 escenarios vigentes tienen prueba aprobada con aserciones de estado y cuerpo correctas. La implementación respeta el diseño: importaciones, prioridad de errores, formas de respuesta y herencia con relaciones bidireccionales. La suite pasa (380 pruebas) y la aplicación importa sin errores. Queda una advertencia menor (WARNING 1) y ningún problema crítico.

### Resolución posterior

- **WARNING 1 resuelto.** Se quitaron los valores por defecto de las tres listas en `ComboCrear`, de modo que omitir cualquiera devuelve 422, como exige la especificación. Se agregó `test_combo_con_una_lista_omitida_se_rechaza_aunque_otra_tenga_ids` (RED → GREEN), que cubre también la SUGGESTION 2. La suite pasa con 381 pruebas.
- **Veredicto final: PASS** (el WARNING 2 es una decisión aceptada por el usuario).
