import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User as SupabaseUser } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'
import api from '@/lib/api'

export interface AppUser {
  uid: string
  email?: string
  displayName?: string
}

interface AuthContextType {
  user: AppUser | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  autoConfirm: (email: string) => Promise<void>
  loginWithGoogle: () => Promise<void>
  logout: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null)
  const [loading, setLoading] = useState(true)

  const mapSupabaseUser = (su: SupabaseUser | null): AppUser | null => {
    if (!su) return null
    return {
      uid: su.id,
      email: su.email,
      displayName: su.user_metadata?.full_name || su.user_metadata?.display_name || su.email?.split('@')[0],
    }
  }

  // Keep cp_active_uid in sync for the api.ts fallback interceptor
  useEffect(() => {
    if (user?.uid) {
      localStorage.setItem('cp_active_uid', user.uid)
    } else {
      localStorage.removeItem('cp_active_uid')
    }
  }, [user])

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(mapSupabaseUser(session.user))
      }
      setLoading(false)
    }).catch(() => {
      setLoading(false)
    })

    // Listen to Auth state changes — handles token refresh, sign-in, and sign-out
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_OUT' || !session) {
        setUser(null)
      } else if (session?.user) {
        setUser(mapSupabaseUser(session.user))
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const autoConfirm = async (email: string) => {
    try {
      await api.post('/api/auth/auto-confirm', { email })
    } catch (err: any) {
      console.warn('Auto-confirm request failed:', err?.response?.data?.detail || err.message)
      throw new Error(err?.response?.data?.detail || 'Failed to auto-confirm email.')
    }
  }

  const signup = async (name: string, email: string, password: string) => {
    let registeredViaBackend = false

    // 1. Try to register via backend Admin API (/api/auth/register).
    // This creates user with email_confirm=True, which completely bypasses
    // Supabase's free-tier email rate limit (3/hour) and prevents "Email not confirmed".
    try {
      const res = await api.post('/api/auth/register', { name, email, password })
      if (res.data?.success) {
        registeredViaBackend = true
      }
    } catch (apiErr: any) {
      const detail = apiErr?.response?.data?.detail
      // If the backend has a specific validation error or duplicate email, handle it
      if (detail && !detail.includes('Supabase configuration missing')) {
        throw new Error(detail)
      }
      console.warn('Backend /api/auth/register unavailable, falling back to direct signup:', apiErr?.message)
    }

    if (!registeredViaBackend) {
      // Fallback: direct Supabase signup
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { display_name: name, full_name: name }
        }
      })
      if (error) {
        // If hit rate limit or unconfirmed, attempt auto-confirm
        if (error.message?.toLowerCase().includes('rate limit') || error.message?.toLowerCase().includes('rate_limit')) {
          throw new Error('Supabase email limit exceeded. Please try logging in directly, or contact admin.')
        }
        throw new Error(error.message)
      }
      if (data?.user) {
        // Try to auto-confirm right away
        await autoConfirm(email).catch(() => {})
      }
    }

    // 2. Sign in to establish client-side authenticated session & JWT token
    let { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    // If signIn reports "Email not confirmed", auto-confirm via backend and retry
    if (signInError && signInError.message?.toLowerCase().includes('email not confirmed')) {
      try {
        await autoConfirm(email)
        const retry = await supabase.auth.signInWithPassword({ email, password })
        signInData = retry.data
        signInError = retry.error
      } catch {
        // Continue to error check below
      }
    }

    if (signInError) throw new Error(signInError.message)

    if (signInData?.user) {
      setUser(mapSupabaseUser(signInData.user))
      // Ensure Firestore profile + score doc exist (non-blocking)
      api.post('/api/auth/create-profile').catch(() => {})
    }
  }

  const login = async (email: string, password: string) => {
    let { data, error } = await supabase.auth.signInWithPassword({ email, password })

    // Auto-fix if Supabase reports "Email not confirmed"
    if (error && error.message?.toLowerCase().includes('email not confirmed')) {
      try {
        await autoConfirm(email)
        const retry = await supabase.auth.signInWithPassword({ email, password })
        data = retry.data
        error = retry.error
      } catch (autoErr) {
        console.warn('Auto-confirm on login failed:', autoErr)
      }
    }

    if (error) throw new Error(error.message)

    if (data?.user) {
      setUser(mapSupabaseUser(data.user))
      // Ensure Firestore profile/score doc exist (non-blocking)
      api.post('/api/auth/create-profile').catch(() => {})
    }
  }

  const loginWithGoogle = async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/dashboard`,
      },
    })
    if (error) throw new Error(error.message)
    // If data.url is returned, browser will redirect to Google auth consent screen
    if (data?.url) {
      window.location.href = data.url
    }
  }

  const logout = async () => {
    // Clear per-user cached score/profile from localStorage BEFORE clearing uid
    // so a subsequent login by a different user cannot see leftover data
    const activeUid = localStorage.getItem('cp_active_uid')
    if (activeUid) {
      localStorage.removeItem(`cp_user_score_${activeUid}`)
      localStorage.removeItem(`cp_user_history_${activeUid}`)
      localStorage.removeItem(`cp_mock_profile_${activeUid}`)
    }
    try {
      await supabase.auth.signOut()
    } catch {
      // Ignore Supabase signOut error — local state is cleared regardless
    }
    setUser(null)
  }

  const resetPassword = async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/login`,
    })
    if (error) throw new Error(error.message)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, autoConfirm, loginWithGoogle, logout, resetPassword }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
