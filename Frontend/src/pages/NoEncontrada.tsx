import { Link } from 'react-router-dom'
import { PageHeader } from '../ui'

export default function NoEncontrada() {
  return (
    <>
      <PageHeader titulo="Página no encontrada" />
      <div className="card pendiente">
        <p className="muted">La dirección que buscás no existe.</p>
        <p><Link to="/" className="link">Volver al inicio</Link></p>
      </div>
    </>
  )
}
