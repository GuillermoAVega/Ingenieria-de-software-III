import { useEffect, useState } from 'react'
import { normalizePath } from './navigation'

/**
 * Lee la ruta actual desde window.location.hash y se mantiene
 * sincronizado con los cambios de hash del navegador.
 */
export function useHashRoute(): string {
  const [path, setPath] = useState(() => normalizePath(window.location.hash))

  useEffect(() => {
    const handleHashChange = () => {
      setPath(normalizePath(window.location.hash))
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  return path
}
