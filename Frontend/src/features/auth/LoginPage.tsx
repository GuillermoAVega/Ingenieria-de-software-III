import { Alert, Button, Card, Field, Input } from '../../ui/ui'
import { useLoginForm } from './useLoginForm'

export function LoginPage() {
  const { state, updateField, submit } = useLoginForm()

  return (
    <main className="auth-page">
      <div className="auth-panel">
        <div className="auth-brand">
          <img src="/logo.png" alt="Sabor de Mar" />
          <div>
            <h1>Sabor de Mar</h1>
            <p>Gestión del restaurante</p>
          </div>
        </div>
        {state.error && (
          <Alert tone="danger" title="No se pudo iniciar sesión">
            {state.error}
          </Alert>
        )}
        <form onSubmit={submit}>
          <Card
            title="Iniciar sesión"
            subtitle="Ingresá con tu usuario para acceder al sistema."
            footer={
              <Button variant="primary" type="submit" block disabled={state.submitting}>
                {state.submitting ? 'Ingresando...' : 'Ingresar'}
              </Button>
            }
          >
            <div className="stack">
              <Field label="Usuario" required>
                <Input
                  autoFocus
                  autoComplete="username"
                  value={state.username}
                  onChange={(event) => updateField('username', event.target.value)}
                  required
                />
              </Field>
              <Field label="Contraseña" required>
                <Input
                  type="password"
                  autoComplete="current-password"
                  value={state.password}
                  onChange={(event) => updateField('password', event.target.value)}
                  required
                />
              </Field>
            </div>
          </Card>
        </form>
      </div>
    </main>
  )
}
