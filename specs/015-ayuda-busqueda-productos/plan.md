# Plan 015 — Texto de Ayuda en Listar Productos

Plan técnico para implementar `specs/015-ayuda-busqueda-productos/spec.md`,
respetando `docs/constitution.md`. Mismo patrón ya aplicado en
[[014-correcciones-cliente]] RF-3 sobre `ClienteListado.jsx`, ahora sobre
`ProductoListado.jsx`. No se agregan módulos ni dependencias nuevas.

## 1. Estructura de Módulos

### Frontend (`app/frontend/`)

- **`components/ProductoListado.jsx` (extendido)**: agrega un párrafo de
  ayuda debajo del formulario de búsqueda, con el texto "Podés buscar
  por Nombre o Código/SKU." [Cubre RF-1]
- **`components/ProductoListado.css` (extendido)**: agrega la clase de
  estilo del texto de ayuda, mismo criterio visual que
  `.cliente-listado__hint` de [[014-correcciones-cliente]]. [Cubre RF-1]

## 2. Modelo de la Base de Datos
No aplica. Esta spec no toca persistencia ni lectura de datos.

## 3. Contrato de la Interfaz Web

No se agregan ni modifican endpoints. La vista "Listar Productos"
(`ProductoListado.jsx`) mantiene su propósito y flujo; solo suma un
párrafo estático debajo de la barra de búsqueda, visible siempre (no
depende de ningún estado de carga o resultado). [Cubre RF-1]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** el texto de ayuda es estático, igual que la
   decisión técnica 3 de [[014-correcciones-cliente]].
   **Justificación:** RF-1 solo pide comunicar los criterios de
   búsqueda ya fijos (Nombre, Código/SKU) definidos desde
   [[008-listar-productos]] RF-2; no hay nada dinámico que calcular.
   **Alternativa descartada:** generar el texto a partir de una lista
   de campos buscables configurable — descartada por diseñar para un
   requisito que no existe. *(RF-1)*

## 5. Estrategia de Tests

### Frontend — Vitest + RTL sobre `ProductoListado.jsx`
- El texto "Podés buscar por Nombre o Código/SKU." está presente al
  renderizar el componente, sin necesidad de interactuar con el
  formulario. [Cubre RF-1]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de la tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/015-ayuda-busqueda-productos/spec.md`, ya aprobada.
- **Regla 4 (tests obligatorios):** cubierto por el test de RTL descrito.
- **Regla 6 (idioma consistente):** texto de ayuda en español.
