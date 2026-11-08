# Especificación de la interfaz de promociones y combos (promotions-ui)

Capacidad nueva. Describe el comportamiento observable del frontend (`Frontend/src/features/promotions/`) para el tipo de promoción y la gestión de combos con cantidades. Los mensajes de interfaz están en español y los identificadores de código en inglés. Se respetan las reglas de `AGENTS.md`: un único objeto de estado tipado por componente o hook, la lógica en hooks de la feature (`usePromotionForm`, `usePromotionsList` y un hook propio de combos), sin `fetch` directo en componentes (se usa `apiFetch` y las funciones de `api.ts`). Los escenarios usan el prefijo `PLC-` (desde PLC-62). La verificación del frontend es `npm run lint` y `tsc -b` (no hay runner de pruebas).

## ADDED Requirements

### Requirement: Selector de tipo en el formulario de promociones
El formulario de alta y edición de promociones DEBE incluir un selector de tipo con las opciones "Porcentaje" (`porcentaje`) y "Por cantidad (2x1, 3x2…)" (`lleva_paga`). Con `porcentaje` DEBE mostrar el campo de descuento y ocultar `lleva` y `paga`; con `lleva_paga` DEBE mostrar `lleva` y `paga` y ocultar el descuento. Al cambiar de tipo, los campos del otro tipo NO DEBEN enviarse. El envío DEBE incluir `tipo` y solo los campos de ese tipo. Los errores 422 y 409 del servidor DEBEN mostrarse en el formulario.

#### Scenario: PLC-62 Selector de tipo porcentaje
- DADO el formulario de promociones abierto
- CUANDO el usuario elige "Porcentaje"
- ENTONCES se muestra el descuento y no se muestran `lleva` ni `paga`

#### Scenario: PLC-63 Selector de tipo lleva_paga
- DADO el formulario de promociones abierto
- CUANDO el usuario elige "Lleva X paga Y"
- ENTONCES se muestran `lleva` y `paga` y no se muestra el descuento

#### Scenario: PLC-64 Envío de lleva_paga
- DADO el tipo "Lleva X paga Y" con `lleva = 3` y `paga = 2`
- CUANDO el usuario guarda
- ENTONCES la petición contiene `tipo = "lleva_paga"`, `lleva = 3` y `paga = 2` y no contiene `descuento`

#### Scenario: PLC-65 Cambio de tipo descarta los campos del otro tipo
- DADO el tipo "Porcentaje" con un descuento cargado
- CUANDO el usuario cambia a "Lleva X paga Y" y guarda
- ENTONCES la petición no contiene `descuento`

#### Scenario: PLC-66 Validación de lleva y paga en el formulario
- DADO el tipo "Lleva X paga Y"
- CUANDO el usuario ingresa `lleva` menor o igual a `paga`, o `paga` menor que 1
- ENTONCES se muestra un error en español y no se envía la petición

#### Scenario: PLC-67 Error del servidor visible
- DADO un envío rechazado con 422 o 409
- CUANDO responde el servidor
- ENTONCES el formulario muestra el error y conserva los datos ingresados

### Requirement: Tipo en el listado y la edición de promociones
El listado de promociones DEBE mostrar, en una columna "Beneficio", la regla de cada promoción de forma que el tipo quede implícito: `porcentaje` como "15%"; `lleva_paga` como "NxM" cuando `lleva - paga = 1` (por ejemplo "2x1", "3x2") y como "Lleva N paga M" en los demás casos. La edición de una promoción con `en_uso = true` NO DEBE ofrecerse, y al editar una sin uso el formulario DEBE precargar su `tipo` y sus campos. Una promoción dada de baja por vencimiento DEBE aparecer como dada de baja.

#### Scenario: PLC-68 Regla visible en el listado
- DADO una promoción `lleva_paga` con `lleva = 2` y `paga = 1`
- CUANDO el usuario abre el listado
- ENTONCES la columna "Beneficio" muestra "2x1"; una con `lleva = 5` y `paga = 3` muestra "Lleva 5 paga 3"

#### Scenario: PLC-69 Edición precargada
- DADO una promoción `lleva_paga` sin uso
- CUANDO el usuario abre su edición
- ENTONCES el selector está en "Lleva X paga Y" con `lleva` y `paga` precargados

#### Scenario: PLC-70 Promoción en uso no editable
- DADO una promoción con `en_uso = true`
- CUANDO el usuario ve el listado
- ENTONCES no se ofrece la edición

#### Scenario: PLC-71 Vencida aparece dada de baja
- DADO una promoción con `fecha_hasta` anterior a hoy
- CUANDO el usuario abre el listado con bajas visibles
- ENTONCES aparece como dada de baja

### Requirement: Gestión de combos dentro de la sección de productos
La sección de productos DEBE ofrecer alta, edición y baja de combos en una pestaña "Combos", junto a Platos, Bebidas y Postres (rutas `/productos/combos/nuevo` y `/productos/combos/:id/editar`). La sección de promociones NO DEBE ofrecer un acceso propio a combos. El formulario de combo DEBE incluir nombre, precio, fechas de vigencia y, para platos, bebidas y postres, la selección de componentes activos con una cantidad entera `>= 1` por componente (por defecto 1). DEBE impedir duplicar un componente dentro de una lista, exigir al menos un componente en total y enviar `platos`, `bebidas` y `postres` como listas `{id, cantidad}`. El listado de combos DEBE mostrar los componentes con sus cantidades y ocultar los dados de baja. La baja DEBE invocar la baja lógica del combo. Los errores 422 y 409 del servidor DEBEN mostrarse en español.

#### Scenario: PLC-72 Alta de combo con cantidades
- DADO el formulario de combo con un plato (cantidad 2) y una bebida (cantidad 1)
- CUANDO el usuario guarda
- ENTONCES la petición contiene `platos = [{id, cantidad: 2}]` y `bebidas = [{id, cantidad: 1}]`

#### Scenario: PLC-73 Cantidad por defecto
- DADO un componente recién seleccionado
- CUANDO el usuario no modifica la cantidad
- ENTONCES se envía `cantidad = 1`

#### Scenario: PLC-74 Cantidad inválida
- DADO un componente
- CUANDO el usuario ingresa una cantidad menor que 1 o no entera
- ENTONCES se muestra un error en español y no se envía la petición

#### Scenario: PLC-75 Sin componentes
- DADO un formulario de combo sin ningún componente
- CUANDO el usuario intenta guardar
- ENTONCES se muestra un error en español y no se envía la petición

#### Scenario: PLC-76 Componente no duplicable
- DADO un plato ya agregado
- CUANDO el usuario intenta agregarlo de nuevo en la misma lista
- ENTONCES no se duplica el elemento

#### Scenario: PLC-77 Edición de combo
- DADO un combo existente con cantidades
- CUANDO el usuario abre su edición
- ENTONCES el formulario precarga los componentes con sus cantidades y permite modificarlas

#### Scenario: PLC-78 Listado de combos con cantidades
- DADO un combo activo con `platos = [{id: 1, cantidad: 2}]`
- CUANDO el usuario abre el listado de combos
- ENTONCES se muestra el plato con su cantidad y no se muestran combos dados de baja

#### Scenario: PLC-79 Baja de combo
- DADO un combo activo
- CUANDO el usuario confirma la baja
- ENTONCES el combo deja de mostrarse en el listado por defecto

#### Scenario: PLC-80 Error del servidor en combos
- DADO un envío de combo rechazado con 422 o 409
- CUANDO responde el servidor
- ENTONCES el formulario muestra el error y conserva los datos ingresados

### Requirement: Combos seleccionables en una promoción
El formulario de promociones DEBE seguir ofreciendo los combos activos como productos seleccionables, sin cambios de comportamiento respecto de `promotion-management`.

#### Scenario: PLC-81 Combo ofrecido en el formulario de promoción
- DADO un combo activo
- CUANDO el usuario abre el formulario de promociones
- ENTONCES el combo aparece entre los productos seleccionables

## MODIFIED Requirements

Ninguno.

## REMOVED Requirements

Ninguno.
