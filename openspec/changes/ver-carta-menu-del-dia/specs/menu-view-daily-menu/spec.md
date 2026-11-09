# Menú del día en Ver carta

## Requisito: Mostrar el menú asignado a la fecha de la carta

La pantalla “Ver carta” DEBE incluir el producto de tipo menú del día activo que esté asignado a la fecha vigente de la carta. DEBE resolver la asignación mediante `menu_del_dia_id` y conservar el nombre, la descripción, el precio y la sección del producto. No DEBE mostrar menús asignados a otras fechas ni menús dados de baja.

### Escenario: Hay un menú asignado para hoy

- DADO un menú del día activo asignado a la fecha vigente
- CUANDO se abre “Ver carta”
- ENTONCES se muestra el menú en su sección correspondiente con su nombre, descripción y precio.

### Escenario: No hay menú asignado para hoy

- DADO que no existe un menú del día activo asignado a la fecha vigente
- CUANDO se abre “Ver carta”
- ENTONCES la carta no muestra menús asignados a otras fechas.
