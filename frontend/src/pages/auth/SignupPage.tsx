import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Compass, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { BackgroundPaths } from '@/components/ui/background-paths'

export default function SignupPage() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !email || !password || !confirm) return toast.error('Please fill in all fields')
    if (password.length < 6) return toast.error('Password must be at least 6 characters')
    if (password !== confirm) return toast.error('Passwords do not match')

    setLoading(true)
    try {
      await signup(name, email, password)
      toast.success('Account created! Welcome to CareerPilot AI 🚀')
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err.message || 'Registration failed')
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
          <h2 className="font-heading text-2xl font-bold text-app mb-1">Create Candidate Account</h2>
          <p className="text-secondary text-xs mb-6 font-medium">Start your evidence-based career readiness journey today</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1.5 block">Full Name</label>
              <input
                id="signup-name"
                type="text"
                className="input text-xs px-3"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1.5 block">Email Address</label>
              <input
                id="signup-email"
                type="email"
                className="input text-xs px-3"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1.5 block">Password</label>
              <div className="relative">
                <input
                  id="signup-password"
                  type={showPass ? 'text' : 'password'}
                  className="input text-xs px-3 pr-10"
                  placeholder="Min. 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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

            <div>
              <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1.5 block">Confirm Password</label>
              <input
                id="signup-confirm"
                type={showPass ? 'text' : 'password'}
                className="input text-xs px-3"
                placeholder="Repeat password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
              />
            </div>

            <button id="signup-submit" type="submit" disabled={loading} className="btn btn-primary w-full justify-center text-xs py-2.5 mt-2">
              {loading && <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-xs text-secondary font-medium mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-teal-700 dark:text-teal-400 font-bold hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </BackgroundPaths>
  )
}
