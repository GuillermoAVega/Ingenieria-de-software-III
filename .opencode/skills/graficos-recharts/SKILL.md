---
name: graficos-recharts
description: Usar cuando se cree, modifique o revise cualquier gráfico del frontend, especialmente con Recharts. Define la estética común, los colores, la tipografía, los ejes, las leyendas y los estados de los gráficos para que sean cohesivos con ui.css.
---

# Gráficos con Recharts

## Compatibilidad

Esta skill sigue el formato abierto Agent Skills: un `SKILL.md` en Markdown con frontmatter YAML (`name` y `description`). No depende de herramientas ni metadatos exclusivos de OpenCode.

Cualquier agente puede cargarla desde `.opencode/skills/graficos-recharts/` o copiarla a su directorio de skills habitual (`.claude/skills/`, `.agents/skills/`, etc.). Si el agente no descubre skills automáticamente, `AGENTS.md` indica leer este archivo antes de modificar gráficos.

## Cuándo usar esta skill

Usarla si la tarea toca un gráfico, una visualización de datos o un componente basado en Recharts.

Antes de escribir el gráfico, revisar `Frontend/src/ui/ui.css` para confirmar las variables vigentes. No introducir colores, sombras, radios ni tipografías nuevas.

## Reglas de composición

- El gráfico vive en un componente propio de la feature (`components/`). No contiene llamadas HTTP ni reglas de negocio.
- La página o el componente superior carga los datos y pasa series ya tipadas por props.
- Usar `ResponsiveContainer` con una altura explícita y un ancho `100%`.
- No inventar un `className` nuevo si alcanza con las utilidades existentes (`card`, `muted`, `num`, `row`, `stack`).
- Si hace falta una clase visual nueva, agregarla a `ui.css` junto a los estilos de gráficos y usar variables de `:root`.
- El gráfico debe funcionar sin datos: mostrar `EmptyState` o un mensaje claro en español, nunca un canvas vacío.

## Paleta y estética

Usar exclusivamente las variables de `ui.css`:

| Uso | Variable |
|---|---|
| Serie principal o actual | `--c-accent` |
| Serie de comparación o anterior | `--c-text-3` |
| Serie secundaria/alternativa | `--c-info` |
| Serie de alerta o negativa | `--c-danger` |
| Serie positiva | `--c-success` |
| Texto principal | `--c-text` |
| Texto secundario y etiquetas | `--c-text-3` |
| Líneas de grilla | `--c-border` |
| Fondo de superficie | `--c-surface` |
| Fondo de tooltip | `--c-surface` |
| Borde de tooltip | `--c-border` |
| Tipografía | `--font-sans` |
| Radio | `--radius` |
| Sombra de tooltip | `--shadow-md` |

Reglas:

- No usar hex, `rgb()` ni nombres de color literales.
- La serie principal se dibuja con `stroke="var(--c-accent)"` y `strokeWidth={2}`.
- La serie comparada se dibuja con `stroke="var(--c-text-3)"`, `strokeWidth={2}` y línea discontinua (`strokeDasharray="4 4"`).
- No usar rellenos fuertes ni gradientes llamativos. Si hace falta área, usar `fillOpacity` mayor a 0.08 y menor a 0.18.
- Los puntos (`dot`) se ocultan en series con muchos datos; mostrar solo `activeDot` al interactuar.
- El foco y el hover no deben cambiar el layout.

## Tipografía y ejes

- `fontFamily: 'var(--font-sans)'` en `XAxis`, `YAxis`, `Legend` y `Tooltip`.
- `fontSize` entre 12 y 13 para ejes y leyenda.
- Etiquetas de eje en `var(--c-text-3)`.
- El eje Y no necesita línea ni tick line; la grilla horizontal alcanza.
- `CartesianGrid` con `stroke="var(--c-border)"`, `strokeDasharray="3 3"` y solo líneas horizontales (`vertical={false}`).
- Formatear importes en pesos argentinos con `Intl.NumberFormat('es-AR')` y sin decimales cuando el valor sea entero.
- En el eje X, mostrar solo las etiquetas necesarias para evitar superposición.
- No rotar etiquetas salvo que sea imprescindible.

## Tooltip

- Fondo `var(--c-surface)`, borde `1px solid var(--c-border)`, radio `var(--radius)` y sombra `var(--shadow-md)`.
- Título y valores en español.
- Mostrar el nombre de la serie y el valor formateado.
- No mostrar `name` técnico; usar `name` legible.
- `cursor={{ stroke: 'var(--c-border-strong)', strokeDasharray: '3 3' }}`.

## Leyenda

- Ubicarla arriba o abajo del gráfico, nunca encima de la grilla.
- Texto en `var(--c-text-2)`, tamaño 13.
- Nombres de serie legibles y en español.
- Si las series se distinguen bien por color, no agregar una segunda codificación innecesaria.

## Accesibilidad

- Envolver el gráfico en un contenedor con `role="img"` y `aria-label` descriptivo.
- Incluir un resumen textual de la comparación o un `title` dentro del SVG.
- No depender solo del color: la leyenda debe nombrar cada serie.
- Mantener contraste suficiente entre líneas y fondo.

## Estructura sugerida

```tsx
<Card title="Ventas por día" subtitle="Mes actual contra el mes anterior.">
  <div className="chart-wrap" role="img" aria-label="Ventas por día del mes actual y del mes anterior">
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--c-border)" strokeDasharray="3 3" />
        <XAxis dataKey="dia" tick={{ fill: 'var(--c-text-3)', fontSize: 12 }} />
        <YAxis tick={{ fill: 'var(--c-text-3)', fontSize: 12 }} width={72} />
        <Tooltip
          contentStyle={{
            background: 'var(--c-surface)',
            border: '1px solid var(--c-border)',
            borderRadius: 'var(--radius)',
            boxShadow: 'var(--shadow-md)',
            fontFamily: 'var(--font-sans)',
          }}
        />
        <Legend wrapperStyle={{ fontFamily: 'var(--font-sans)', fontSize: 13 }} />
        <Line type="monotone" dataKey="actual" name="Mes seleccionado" stroke="var(--c-accent)" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="anterior" name="Mes anterior" stroke="var(--c-text-3)" strokeWidth={2} strokeDasharray="4 4" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  </div>
</Card>
```

## Verificación

Después de agregar o modificar un gráfico:

- Ejecutar `npm run build` desde `Frontend/`.
- Ejecutar `npx eslint src/features/<feature>`.
- Revisar que no haya colores literales ni estilos inline ajenos a las variables de `ui.css`.
- Revisar el gráfico con datos vacíos, carga y error.
