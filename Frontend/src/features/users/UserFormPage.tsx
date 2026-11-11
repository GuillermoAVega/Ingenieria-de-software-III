import { Alert, Button, Card, Check, Field, Input, PageHeader, Select } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { useUserForm } from './useUserForm'

export function UserFormPage({ id }: { id?: string }) {
  const { state, isEditing, updateField, submit } = useUserForm(id)
  return (
    <>
      <PageHeader
        title={isEditing ? 'Editar usuario' : 'Nuevo usuario'}
        subtitle="Definí las credenciales y los permisos de acceso."
      />
      {state.error && <Alert tone="danger" title="No se pudo guardar el usuario">{state.error}</Alert>}
      {state.loading ? <Card><p className="muted">Cargando usuario...</p></Card> : (
        <form onSubmit={submit}>
          <Card footer={
            <>
              <Button onClick={() => navigate('/usuarios')} disabled={state.saving}>Cancelar</Button>
              <Button variant="primary" type="submit" disabled={state.saving}>{state.saving ? 'Guardando...' : 'Guardar usuario'}</Button>
            </>
          }>
            <div className="form-grid">
              <Field label="Nombre" required error={state.fieldErrors.nombre}>
                <Input value={state.nombre} onChange={(event) => updateField('nombre', event.target.value)} required />
              </Field>
              <Field label="Usuario" required error={state.fieldErrors.nombre_usuario}>
                <Input value={state.nombreUsuario} onChange={(event) => updateField('nombreUsuario', event.target.value)} autoComplete="username" required />
              </Field>
              <Field label={isEditing ? 'Nueva contraseña' : 'Contraseña'} required={!isEditing} hint={isEditing ? 'Dejala vacía para conservar la actual.' : 'Mínimo 8 caracteres.'} error={state.fieldErrors.clave}>
                <Input type="password" minLength={8} value={state.clave} onChange={(event) => updateField('clave', event.target.value)} required={!isEditing} autoComplete="new-password" />
              </Field>
              <Field label="Rol" required>
                <Select value={state.rol} onChange={(event) => updateField('rol', event.target.value)}>
                  <option value="administrador">Administrador</option>
                  <option value="operario">Operario</option>
                </Select>
              </Field>
              {isEditing && <Field><Check checked={state.activo} onChange={(event) => updateField('activo', event.target.checked)}>Usuario activo</Check></Field>}
            </div>
          </Card>
        </form>
      )}
    </>
  )
}
