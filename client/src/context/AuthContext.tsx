import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { login as apiLogin, setAuthToken, signup as apiSignup, getCurrentUser, getBillingStatus, SubscriptionSummary } from '../api/client'

export type User = {
  email: string
  name?: string
}

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  plan: 'free' | 'standard' | 'premium'
  refreshBilling: () => Promise<void>
  upgrade: () => void
  usage: Record<string, any> | null
  subscription: SubscriptionSummary | null
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const saved = localStorage.getItem('auth_user')
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('auth_token'))
  const [plan, setPlan] = useState<'free' | 'standard' | 'premium'>(() => {
    const saved = localStorage.getItem('billing_plan')
    return saved === 'standard' || saved === 'premium' ? (saved as 'standard' | 'premium') : 'free'
  })
  const [usage, setUsage] = useState<Record<string, any> | null>(null)
  const [subscription, setSubscription] = useState<SubscriptionSummary | null>(null)

  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')
    if (savedToken) {
      setToken(savedToken)
      setAuthToken(savedToken)
      
      // Try to refresh user profile from server
      getCurrentUser()
        .then(userProfile => {
          const u: User = { email: userProfile.email, name: userProfile.name }
          setUser(u)
          localStorage.setItem('auth_user', JSON.stringify(u))
        })
        .catch(() => {
          // If refresh fails, use saved user data
          if (savedUser) {
            try {
              setUser(JSON.parse(savedUser))
            } catch {}
          }
        })
      // Billing status
      getBillingStatus().then(b => {
        const p = (b.plan === 'standard' || b.plan === 'premium') ? b.plan : 'free'
        setPlan(p)
        setUsage(b.usage || null)
        setSubscription(b.subscription || null)
        localStorage.setItem('billing_plan', p)
      }).catch(() => {})
    } else if (savedUser) {
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
    
    // Fetch user profile with name
    try {
      const userProfile = await getCurrentUser()
      const u: User = { email: userProfile.email, name: userProfile.name }
      setUser(u)
      localStorage.setItem('auth_user', JSON.stringify(u))
      try {
        const b = await getBillingStatus()
        const p = (b.plan === 'standard' || b.plan === 'premium') ? b.plan : 'free'
        setPlan(p)
        setUsage(b.usage || null)
        setSubscription(b.subscription || null)
        localStorage.setItem('billing_plan', p)
      } catch {}
    } catch (error) {
      // Fallback to email-only if profile fetch fails
      const u: User = { email }
      setUser(u)
      localStorage.setItem('auth_user', JSON.stringify(u))
    }
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
    localStorage.removeItem('billing_plan')
    setPlan('free')
  }

  const refreshUser = async () => {
    try {
      const userProfile = await getCurrentUser()
      const u: User = { email: userProfile.email, name: userProfile.name }
      setUser(u)
      localStorage.setItem('auth_user', JSON.stringify(u))
    } catch (error) {
      // If refresh fails, keep current user data
      console.error('Failed to refresh user profile:', error)
    }
  }

  const refreshBilling = async () => {
    try {
      const b = await getBillingStatus()
      const p = (b.plan === 'standard' || b.plan === 'premium') ? b.plan : 'free'
      setPlan(p)
      setUsage(b.usage || null)
      setSubscription(b.subscription || null)
      localStorage.setItem('billing_plan', p)
    } catch {}
  }

  const upgrade = () => {
    try { window.location.assign('/pricing') } catch {}
  }

  const value = useMemo(
    () => ({ user, token, login, signup, logout, refreshUser, plan, refreshBilling, upgrade, usage, subscription }),
    [user, token, plan, usage, subscription]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
