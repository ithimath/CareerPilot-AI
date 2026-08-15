import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Compass, Mail, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { BackgroundPaths } from '@/components/ui/background-paths'

export default function ForgotPasswordPage() {
  const { resetPassword } = useAuth()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return toast.error('Enter your email address')
    setLoading(true)
    try {
      await resetPassword(email)
      setSent(true)
    } catch {
      toast.error('Could not send reset email. Check your email address.')
    } finally {
      setLoading(false)
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

        <div className="auth-card p-8">
          {sent ? (
            <div className="text-center space-y-4">
              <div className="w-12 h-12 bg-[#FF5722]/10 dark:bg-[#FF5722]/15 text-[#FF5722] dark:text-[#FF7043] border border-[#FF5722]/30 dark:border-[#FF5722]/40 rounded-full flex items-center justify-center mx-auto">
                <Mail className="w-6 h-6" />
              </div>
              <h2 className="font-heading text-2xl font-bold text-app">Check Your Email</h2>
              <p className="text-secondary text-xs font-medium">
                We sent a password reset link to <strong className="text-app font-bold">{email}</strong>
              </p>
              <Link to="/login" className="btn btn-primary w-full justify-center text-xs py-2.5">
                Back to Sign In
              </Link>
            </div>
          ) : (
            <>
              <h2 className="font-heading text-2xl font-bold text-app mb-1">Reset Password</h2>
              <p className="text-secondary text-xs mb-6 font-medium">
                Enter your email address and we will send you a reset link
              </p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1.5 block">Email Address</label>
                  <input
                    type="email"
                    className="input text-xs px-3"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" disabled={loading} className="btn btn-primary w-full justify-center text-xs py-2.5">
                  {loading && <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                  {loading ? 'Sending link...' : 'Send Reset Link'}
                </button>
              </form>
              <Link to="/login" className="flex items-center justify-center gap-2 mt-5 text-xs text-secondary font-bold hover:text-app transition-colors">
                <ArrowLeft className="w-4 h-4" /> Back to Sign In
              </Link>
            </>
          )}
        </div>
      </div>
    </BackgroundPaths>
  )
}

