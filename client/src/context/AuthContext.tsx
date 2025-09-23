import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { login as apiLogin, setAuthToken, signup as apiSignup } from '../api/client'

export type User = {
  email: string
  name?: string
}

type AuthContextValue = {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')
    if (savedToken) {
      setToken(savedToken)
      setAuthToken(savedToken)
    }
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch {}
    }
  }, [])

  const login = async (email: string, password: string) => {
    const res = await apiLogin(email, password)
    setToken(res.access_token)
    setAuthToken(res.access_token)
    localStorage.setItem('auth_token', res.access_token)
    // Minimal user derived from email until backend has profile endpoint
    const u: User = { email }
    setUser(u)
    localStorage.setItem('auth_user', JSON.stringify(u))
  }

  const signup = async (name: string, email: string, password: string) => {
    await apiSignup(name, email, password)
    // Auto-login after signup
    await login(email, password)
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    setAuthToken(undefined)
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  const value = useMemo(
    () => ({ user, token, login, signup, logout }),
    [user, token]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
