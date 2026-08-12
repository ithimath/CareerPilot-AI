import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Compass, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { BackgroundPaths } from '@/components/ui/background-paths'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) return toast.error('Please fill in all fields')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err.message?.includes('auth/') ? 'Invalid email or password' : err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <BackgroundPaths intensity="medium" gradient={false} className="min-h-screen bg-app flex items-center justify-center p-4 text-app">
      <div className="w-full max-w-md animate-fade-in space-y-6 relative z-10">
        {/* Logo Header */}
        <div className="flex items-center justify-center gap-3">
          <div className="w-9 h-9 bg-teal-700 dark:bg-teal-600 rounded-xl flex items-center justify-center text-white shadow-xs">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-heading text-2xl font-extrabold text-app">CareerPilot AI</span>
            <p className="text-[10px] font-bold uppercase tracking-wider text-teal-700 dark:text-teal-400 block -mt-1">Candidate Intelligence Platform</p>
          </div>
        </div>

        <div className="auth-card p-8">
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
                <Link to="/forgot" className="text-xs text-teal-700 dark:text-teal-400 font-bold hover:underline">Forgot password?</Link>
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

          <p className="text-center text-xs text-secondary font-medium mt-6">
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="text-teal-700 dark:text-teal-400 font-bold hover:underline">
              Create account
            </Link>
          </p>
        </div>
      </div>
    </BackgroundPaths>
  )
}
