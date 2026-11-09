import { Card, Field, Select } from '../../../ui/ui'
import { formatMonth } from '../format'

const MONTHS = Array.from({ length: 12 }, (_, index) => index + 1)
const CURRENT_YEAR = new Date().getFullYear()
const YEARS = Array.from({ length: CURRENT_YEAR - 2000 + 1 }, (_, index) => CURRENT_YEAR - index)

export type MonthYearFilterProps = {
  anio: number
  mes: number
  onChangeAnio: (anio: number) => void
  onChangeMes: (mes: number) => void
}

export function MonthYearFilter({ anio, mes, onChangeAnio, onChangeMes }: MonthYearFilterProps) {
  return (
    <Card title="Período" subtitle="El mes anterior se calcula automáticamente.">
      <div className="form-grid">
        <Field label="Mes">
          <Select value={mes} onChange={(event) => onChangeMes(Number(event.target.value))}>
            {MONTHS.map((month) => (
              <option key={month} value={month}>
                {formatMonth(month)}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Año">
          <Select value={anio} onChange={(event) => onChangeAnio(Number(event.target.value))}>
            {YEARS.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </Select>
        </Field>
      </div>
    </Card>
  )
}
