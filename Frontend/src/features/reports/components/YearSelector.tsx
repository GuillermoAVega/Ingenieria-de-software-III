import { Field, Select } from '../../../ui/ui'

export function YearSelector({
  year,
  options,
  onChange,
}: {
  year: number
  options: number[]
  onChange: (year: number) => void
}) {
  return (
    <Field label="Año">
      <Select value={year} onChange={(event) => onChange(Number(event.target.value))}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </Select>
    </Field>
  )
}
