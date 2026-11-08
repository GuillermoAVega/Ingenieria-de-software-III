# Informe de verificación: promociones-lleva-paga-y-combos

**Veredicto**: PASS WITH WARNINGS (0 críticos, 1 advertencia, 1 sugerencia)

## Comandos ejecutados

| Comando | Resultado |
|---------|-----------|
| `cd Backend && venv/bin/python -m pytest --ignore=tests/productos/menus_del_dia -q` | 1076 passed, 3 advertencias de deprecación de Starlette |
| `cd Frontend && npx tsc -b` | Sin errores |
| `cd Frontend && npm run lint` | Solo los 6 errores preexistentes en `Frontend/src/ui.tsx` |

## Cobertura de escenarios

- **Backend (PLC-01 a PLC-61 y PRO modificados)**: cada escenario tiene un test que pasa y lo referencia por id.
  - La búsqueda inicial no encontró referencia para PLC-20, PLC-44 y PLC-57.
  - **PLC-20** no estaba cubierto: se agregó `test_plc_20_cambio_de_tipo_en_uso` en `Backend/tests/promociones/test_modificacion.py`.
  - **PLC-44** y **PLC-57** ya estaban cubiertos: se etiquetaron `test_plc_28_44_varias_lineas_del_mismo_producto_suman` y `test_plc_55_y_57_cantidad_minima_y_sin_maximo`.
- **Frontend (PLC-62 a PLC-81)**: no hay runner de tests en el frontend. La evidencia es el código, más `tsc` y lint sin errores nuevos.
- **PLC-68** se alineó con el diseño: la columna "Beneficio" muestra "2x1" o "3x2" cuando `lleva - paga = 1`, y "Lleva N paga M" en los demás casos.

## Conformidad con el diseño

- `RESTRICT_POR_TIPO` (`Backend/src/productos/registro.py`) sigue usando `combo_plato`, `combo_postre` y `combo_bebida`. Ahora son alias de las tablas de las clases de asociación.
- Ya no se usan las APIs eliminadas:
  - `platos_ids` solo aparece en una aserción negativa de test.
  - `detectar_promocion` no tiene referencias.
  - `_tomar_snapshot` sigue existiendo en `Backend/src/routers/detalles_factura.py`, pero ahora solo toma el precio unitario y la promoción la resuelve el motor.
- `features/promotions` y `features/combos` cumplen `AGENTS.md`: un único objeto de estado por hook y llamadas solo a través de `apiFetch`.

## Tareas

Todas están completas salvo 5.5 (verificación manual en navegador), que queda a cargo del usuario.

## Hallazgos

- **ADVERTENCIA**: los escenarios de frontend no tienen tests automáticos; dependen de la verificación manual 5.5.
- **SUGERENCIA**: renombrar `_tomar_snapshot`, porque ya no toma un snapshot de la promoción.

## Notas operativas

- La base de desarrollo `Backend/app.db` tiene el esquema anterior. Antes de probar hay que ejecutar `cd Backend && venv/bin/python -m scripts.poblar_db`.
- El cambio `promociones` debe archivarse antes que este.
