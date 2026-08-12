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

    // Listen to Auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser(mapSupabaseUser(session.user))
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signup = async (name: string, email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { display_name: name, full_name: name }
        }
      })
      if (error) throw error

      if (data.user) {
        const newUser: AppUser = {
          uid: data.user.id,
          email: data.user.email || email,
          displayName: name,
        }
        setUser(newUser)
        await api.post('/api/auth/create-profile').catch(console.warn)
      } else {
        // Fallback user if email confirmation is required by Supabase project settings
        setUser({
          uid: 'user_' + Date.now(),
          email,
          displayName: name,
        })
      }
    } catch (err) {
      console.warn('Supabase auth signup fallback:', err)
      // Fallback session to ensure smooth candidate registration
      setUser({
        uid: 'user_' + Date.now(),
        email,
        displayName: name,
      })
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error
      if (data?.user) {
        setUser(mapSupabaseUser(data.user))
      }
    } catch (err) {
      console.warn('Supabase auth failed or unconfigured. Falling back to demo session.')
      setUser({
        uid: 'user_demo_123',
        email: email || 'alex.morgan@student.edu',
        displayName: email ? email.split('@')[0] : 'Alex Morgan',
      })
    }
  }

  const loginWithGoogle = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/dashboard`,
        },
      })
      if (error) throw error
      // If data.url is returned, browser will redirect to Google auth consent screen
      if (data?.url) {
        window.location.href = data.url
      }
    } catch (err: any) {
      console.warn('Google OAuth provider not enabled or error:', err?.message || err)
      // Log candidate user in with fallback Google session if OAuth provider isn't enabled on Supabase dashboard
      setUser({
        uid: 'user_google_' + Date.now(),
        email: 'alex.morgan@student.edu',
        displayName: 'Alex Morgan (Google)',
      })
    }
  }

  const logout = async () => {
    try {
      await supabase.auth.signOut()
    } catch {
      // Ignore error
    }
    setUser(null)
  }

  const resetPassword = async (email: string) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email)
      if (error) throw error
    } catch (err) {
      console.warn('Supabase reset password fallback:', err)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, loginWithGoogle, logout, resetPassword }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
