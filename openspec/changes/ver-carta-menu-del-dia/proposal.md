# Propuesta: Mostrar el menú del día en Ver carta

## Intención

La carta del día debe incluir el menú del día asignado a la fecha actual.

## Alcance

- Cargar las asignaciones de menú del día y los productos activos de tipo `menu_del_dia`.
- Relacionar cada asignación con su menú por `menu_del_dia_id`.
- Mostrar el menú solo cuando la fecha de la asignación coincide con la fecha vigente de la carta.
- Mantener la sección y presentación existentes de la carta.
