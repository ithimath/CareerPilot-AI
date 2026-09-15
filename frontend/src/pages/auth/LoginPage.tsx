import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Compass, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { BackgroundPaths } from '@/components/ui/background-paths'

export default function LoginPage() {
  const { login, autoConfirm } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [showAutoConfirmHelp, setShowAutoConfirmHelp] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) return toast.error('Please fill in all fields')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      const msg = err.message || ''
      if (msg.toLowerCase().includes('email not confirmed')) {
        setShowAutoConfirmHelp(true)
        toast.error('Email not confirmed. Click "Auto-Confirm Email" below.')
      } else if (msg.toLowerCase().includes('invalid login credentials')) {
        toast.error('Invalid email or password. Please check your credentials.')
      } else if (msg.toLowerCase().includes('rate limit')) {
        toast.error('Supabase rate limit exceeded. Please wait a moment and try again.')
      } else {
        toast.error(msg.includes('auth/') ? 'Invalid email or password' : msg)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleManualConfirm = async () => {
    if (!email) return toast.error('Please enter your email address')
    setConfirming(true)
    try {
      await autoConfirm(email)
      toast.success('Email confirmed! You can now sign in.')
      setShowAutoConfirmHelp(false)
    } catch (err: any) {
      toast.error(err.message || 'Auto-confirm failed.')
    } finally {
      setConfirming(false)
    }
  }

  return (
    <BackgroundPaths intensity="medium" gradient={false} className="min-h-screen bg-app flex items-center justify-center p-4 text-app">
      <div className="w-full max-w-md animate-fade-in space-y-6 relative z-10">
        {/* Logo Header */}
        <div className="flex items-center justify-center gap-3">
          <div className="w-9 h-9 bg-[#1a1f3a] dark:bg-[#141936] rounded-xl flex items-center justify-center text-white shadow-xs">
            <Compass className="w-5 h-5 text-[#FF5722]" />
          </div>
          <div>
            <span className="font-heading text-2xl font-extrabold text-app">CareerPilot AI</span>
            <p className="text-[10px] font-bold uppercase tracking-wider text-[#FF5722] dark:text-[#FF7043] block -mt-1">Candidate Intelligence Platform</p>
          </div>
        </div>

        <div className="auth-card p-5 sm:p-8">
          <div className="mb-6">
            <h2 className="font-heading text-2xl font-bold text-app">Candidate Sign In</h2>
            <p className="text-secondary text-xs mt-1 font-medium">Access candidate intelligence dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1.5 block">Email Address</label>
              <input
                id="login-email"
                type="email"
                className="input text-xs px-3"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div>
              <div className="flex justify-between mb-1.5">
                <label className="text-[10px] font-bold uppercase tracking-wider text-secondary">Password</label>
                <Link to="/forgot" className="text-xs text-[#FF5722] dark:text-[#FF7043] font-bold hover:underline">Forgot password?</Link>
              </div>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPass ? 'text' : 'password'}
                  className="input text-xs px-3 pr-10"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-app transition-colors"
                  title={showPass ? "Hide password" : "Show password"}
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {showAutoConfirmHelp && (
              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs flex items-center justify-between gap-2">
                <span className="text-amber-500 font-medium">Account not confirmed yet?</span>
                <button
                  type="button"
                  onClick={handleManualConfirm}
                  disabled={confirming}
                  className="text-xs px-2.5 py-1 bg-[#FF5722] hover:bg-[#F4511E] text-white font-bold rounded shadow-xs transition"
                >
                  {confirming ? 'Confirming...' : 'Auto-Confirm Email'}
                </button>
              </div>
            )}

            <button
              id="login-submit"
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full justify-center text-xs py-2.5 mt-2"
            >
              {loading && <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-4 pt-4 border-t border-border flex flex-col gap-2">
            {!showAutoConfirmHelp && (
              <button
                type="button"
                onClick={() => setShowAutoConfirmHelp(true)}
                className="text-[11px] text-muted-foreground hover:text-foreground text-center transition-colors"
              >
                Having email confirmation issues? Click here to auto-confirm
              </button>
            )}
          </div>

          <p className="text-center text-xs text-secondary font-medium mt-4">
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="text-[#FF5722] dark:text-[#FF7043] font-bold hover:underline">
              Create account
            </Link>
          </p>
        </div>
      </div>
    </BackgroundPaths>
  )
}
