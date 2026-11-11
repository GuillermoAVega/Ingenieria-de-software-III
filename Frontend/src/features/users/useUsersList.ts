import { useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/client'
import { getUsers } from './api'
import type { UserRecord } from './types'

type UsersListState = {
  users: UserRecord[]
  loading: boolean
  error: string | null
}

export function useUsersList() {
  const [state, setState] = useState<UsersListState>({
    users: [],
    loading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const users = await getUsers()
        if (!cancelled) setState({ users, loading: false, error: null })
      } catch (error) {
        if (!cancelled) {
          setState({ users: [], loading: false, error: getErrorMessage(error) })
        }
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  return state
}
