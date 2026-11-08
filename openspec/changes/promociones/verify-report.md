# Informe de verificación: promociones

**Veredicto**: PASS WITH WARNINGS (0 críticos, 1 advertencia, 2 sugerencias)

## Comandos ejecutados

| Comando | Resultado |
|---------|-----------|
| `cd Backend && venv/bin/python -m pytest --ignore=tests/productos/menus_del_dia -q` | 973 passed, 3 advertencias de deprecación |
| `cd Frontend && npx tsc -b` | Sin errores (exit 0) |
| `cd Frontend && npm run lint` | Solo los 6 errores preexistentes `react-refresh/only-export-components` en `Frontend/src/ui.tsx` |

## Cobertura de escenarios (PRO-01 a PRO-74)

Todos los escenarios tienen un test que pasa.

| Escenarios | Tests |
|------------|-------|
| PRO-01 a PRO-13, PRO-73 | `Backend/tests/promociones/test_alta.py` |
| PRO-14 a PRO-18 | `Backend/tests/promociones/test_consulta.py` |
| PRO-19 a PRO-23, PRO-69 a PRO-71 | `Backend/tests/promociones/test_modificacion.py` |
| PRO-24 a PRO-27, PRO-65, PRO-66 | `Backend/tests/promociones/test_baja.py` |
| PRO-28 | `Backend/tests/promociones/test_modelo.py` |
| PRO-29 a PRO-32, PRO-41 a PRO-43, PRO-46 a PRO-56, PRO-68 | `Backend/tests/promociones/test_lineas_factura.py` |
| PRO-33 a PRO-40, PRO-44, PRO-45 | `Backend/tests/promociones/test_calculo.py` (PRO-44 y PRO-45 como casos parametrizados de `test_calcular_precio_final`) |
| PRO-57 a PRO-64, PRO-67, PRO-72 | `Backend/tests/test_validacion_producto_comanda.py` |
| PRO-74 | `Backend/tests/productos/combos/test_router.py` |

## Conformidad con el diseño y con AGENTS.md

- `Backend/src/promociones/` sigue la convención entity-per-folder; `PromocionEnUso` responde 409.
- `features/promotions` usa `apiFetch` y no llama a `fetch` en componentes.
- `usePromotionForm` y `usePromotionsList` mantienen un único objeto de estado tipado; las páginas solo renderizan.
- `demo.ts` fue eliminado.

## Tareas

Todas las tareas están completas salvo 5.4, la verificación manual en navegador, que queda a cargo del usuario.

## Hallazgos

- **ADVERTENCIA**: algunos tests no indican su escenario PRO en el nombre ni en un comentario (por ejemplo `test_el_nombre_se_recorta`, `test_productos_ids_duplicados`, `test_put_linea_inexistente`, `test_listado_vacio`). Afecta la trazabilidad, no el comportamiento.
- **SUGERENCIA**: agregar el id PRO a esos tests, para que una búsqueda de `PRO-NN` encuentre todos los escenarios.
- **SUGERENCIA**: los tests sin seguimiento de `Backend/tests/productos/menus_del_dia/`, de otro cambio, fallan al cargarse. Conviene resolverlos antes de integrar.

## Notas operativas

- La base SQLite de desarrollo debe borrarse antes de usar la aplicación, para que `create_all` cree las FK nuevas y el `NOT NULL` de `detalle_factura.detalle_comanda_id`.
