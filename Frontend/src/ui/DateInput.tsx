// DateInput — selector de fecha que SIEMPRE muestra dd/mm/aaaa (independiente del idioma del navegador).
// Contrato: value/onChange usan fechas ISO locales 'YYYY-MM-DD' (o ''). Nunca se usa toISOString().
import { useEffect, useId, useRef, useState } from 'react'
import type { CSSProperties, KeyboardEvent } from 'react'
import { createPortal } from 'react-dom'
import { DayPicker } from 'react-day-picker'
import { es } from 'react-day-picker/locale'
import { format, isValid, parse, parseISO } from 'date-fns'
import 'react-day-picker/style.css'

export type DateInputProps = {
  value: string
  onChange: (value: string) => void
  min?: string
  max?: string
  disabled?: boolean
  invalid?: boolean
  required?: boolean
  placeholder?: string
  id?: string
  name?: string
  'aria-label'?: string
}

type DateInputState = {
  open: boolean
  // Posición fija del popover, calculada al abrirlo desde el rect del campo.
  popoverStyle: CSSProperties
  // Texto en edición; null cuando el campo muestra el valor confirmado.
  draft: string | null
}

const DISPLAY_FORMAT = 'dd/MM/yyyy'
const ISO_FORMAT = 'yyyy-MM-dd'
const POPOVER_WIDTH = 320
const POPOVER_HEIGHT = 360
const POPOVER_GAP = 6
const VIEWPORT_MARGIN = 8

function computePopoverStyle(anchor: HTMLElement): CSSProperties {
  const rect = anchor.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  const flipUp = spaceBelow < POPOVER_HEIGHT && rect.top > spaceBelow
  const left = Math.max(VIEWPORT_MARGIN, Math.min(rect.left, window.innerWidth - POPOVER_WIDTH - VIEWPORT_MARGIN))
  return flipUp
    ? { position: 'fixed', left, bottom: window.innerHeight - rect.top + POPOVER_GAP }
    : { position: 'fixed', left, top: rect.bottom + POPOVER_GAP }
}

function isoToDate(iso: string | undefined): Date | undefined {
  if (!iso) return undefined
  const date = parseISO(iso)
  return isValid(date) ? date : undefined
}

function dateToIso(date: Date): string {
  return format(date, ISO_FORMAT)
}

function isoToDisplay(iso: string): string {
  const date = isoToDate(iso)
  return date ? format(date, DISPLAY_FORMAT) : ''
}

export function DateInput({
  value,
  onChange,
  min,
  max,
  disabled = false,
  invalid = false,
  required = false,
  placeholder = 'dd/mm/aaaa',
  id,
  name,
  'aria-label': ariaLabel,
}: DateInputProps) {
  const [state, setState] = useState<DateInputState>({ open: false, popoverStyle: {}, draft: null })
  const wrapperRef = useRef<HTMLDivElement>(null)
  const popoverRef = useRef<HTMLDivElement>(null)
  const popoverId = useId()

  const selected = isoToDate(value)
  const minDate = isoToDate(min)
  const maxDate = isoToDate(max)

  useEffect(() => {
    if (!state.open) return
    const handlePointerDown = (event: MouseEvent) => {
      const target = event.target as Node
      if (!wrapperRef.current?.contains(target) && !popoverRef.current?.contains(target)) {
        setState((previous) => ({ ...previous, open: false }))
      }
    }
    // El popover es fixed: al scrollear (cualquier ancestro) o redimensionar se cierra para no quedar flotando.
    const handleViewportChange = (event: Event) => {
      if (event.target instanceof Node && popoverRef.current?.contains(event.target)) return
      setState((previous) => ({ ...previous, open: false }))
    }
    document.addEventListener('mousedown', handlePointerDown)
    window.addEventListener('scroll', handleViewportChange, true)
    window.addEventListener('resize', handleViewportChange)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      window.removeEventListener('scroll', handleViewportChange, true)
      window.removeEventListener('resize', handleViewportChange)
    }
  }, [state.open])

  const isOutOfRange = (date: Date) =>
    (minDate !== undefined && date < minDate) || (maxDate !== undefined && date > maxDate)

  // Confirma el texto tipeado. Vacío limpia la fecha; texto inválido o fuera de rango se descarta
  // y el campo vuelve a mostrar el último valor válido.
  const commitDraft = () => {
    const draft = state.draft
    if (draft === null) return
    const text = draft.trim()
    if (text === '') {
      if (value !== '') onChange('')
    } else if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(text)) {
      const parsed = parse(text, 'd/M/yyyy', new Date())
      if (isValid(parsed) && !isOutOfRange(parsed)) {
        const iso = dateToIso(parsed)
        if (iso !== value) onChange(iso)
      }
    }
    setState((previous) => ({ ...previous, draft: null }))
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === 'Escape' && state.open) {
      event.stopPropagation()
      setState((previous) => ({ ...previous, open: false, draft: null }))
    }
  }

  const handleInputKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      if (state.draft !== null) {
        event.preventDefault()
        commitDraft()
      }
    } else if (event.key === 'ArrowDown') {
      event.preventDefault()
      openPopover()
    }
  }

  const openPopover = () => {
    if (!wrapperRef.current) return
    const popoverStyle = computePopoverStyle(wrapperRef.current)
    setState((previous) => ({ ...previous, open: true, popoverStyle }))
  }

  const toggleOpen = () => {
    if (state.open) setState((previous) => ({ ...previous, open: false }))
    else openPopover()
  }

  const text = state.draft ?? isoToDisplay(value)

  return (
    <div className="date-input" ref={wrapperRef} onKeyDown={handleKeyDown}>
      <input
        id={id}
        name={name}
        type="text"
        inputMode="numeric"
        autoComplete="off"
        className={`input date-input-field${invalid ? ' is-invalid' : ''}`}
        value={text}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        maxLength={10}
        aria-label={ariaLabel}
        aria-invalid={invalid || undefined}
        aria-haspopup="dialog"
        aria-expanded={state.open}
        aria-controls={state.open ? popoverId : undefined}
        onChange={(event) => {
          const draft = event.target.value.replace(/[^\d/]/g, '')
          setState((previous) => ({ ...previous, draft }))
        }}
        onClick={openPopover}
        onBlur={commitDraft}
        onKeyDown={handleInputKeyDown}
      />
      <button
        type="button"
        className="date-input-toggle"
        aria-label="Abrir calendario"
        disabled={disabled}
        onClick={toggleOpen}
      >
        <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.6">
          <rect x="3" y="4.5" width="14" height="12.5" rx="2" />
          <path d="M3 8.5h14M7 2.5v3M13 2.5v3" strokeLinecap="round" />
        </svg>
      </button>
      {state.open && !disabled
        ? createPortal(
        <div
          className="date-input-popover"
          id={popoverId}
          ref={popoverRef}
          role="dialog"
          aria-label="Calendario"
          style={state.popoverStyle}
        >
          <DayPicker
            mode="single"
            locale={es}
            weekStartsOn={1}
            captionLayout="dropdown"
            autoFocus
            selected={selected}
            defaultMonth={selected ?? (minDate && minDate > new Date() ? minDate : undefined)}
            startMonth={minDate}
            endMonth={maxDate}
            disabled={[
              ...(minDate ? [{ before: minDate }] : []),
              ...(maxDate ? [{ after: maxDate }] : []),
            ]}
            onSelect={(date) => {
              setState((previous) => ({ ...previous, open: false, draft: null }))
              onChange(date ? dateToIso(date) : '')
            }}
          />
        </div>,
        document.body,
      )
        : null}
    </div>
  )
}
