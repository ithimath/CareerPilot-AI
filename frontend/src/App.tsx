import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import { ThemeProvider } from '@/context/ThemeContext'
import AppLayout from '@/components/layout/AppLayout'
import ProtectedRoute from '@/components/auth/ProtectedRoute'

// Auth & Landing pages
import LoginPage     from '@/pages/auth/LoginPage'
import SignupPage    from '@/pages/auth/SignupPage'
import ForgotPage   from '@/pages/auth/ForgotPasswordPage'
import LandingPage  from '@/pages/LandingPage'
import HeroDemo     from '@/pages/HeroDemo'

// Command Center & Hub pages
import DashboardPage    from '@/pages/DashboardPage'
import PracticeHubPage  from '@/pages/PracticeHubPage'
import CareerHubPage    from '@/pages/CareerHubPage'
import AnalyticsHubPage from '@/pages/AnalyticsHubPage'

// Standalone pages
import CommunityPage    from '@/pages/CommunityPage'
import ChatPage         from '@/pages/ChatPage'
import SettingsPage     from '@/pages/SettingsPage'

function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-app flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full border-2 border-emerald-600 border-t-transparent animate-spin" />
          <p className="text-secondary text-sm font-medium">Loading CareerPilot AI Command Center...</p>
        </div>
      </div>
    )
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/hero-demo" element={<HeroDemo />} />
      <Route path="/login"   element={<LoginPage />} />
      <Route path="/signup"  element={<SignupPage />} />
      <Route path="/forgot"  element={<ForgotPage />} />

      {/* Protected Top-Nav Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard"    element={<DashboardPage />} />
          <Route path="/practice/*"   element={<PracticeHubPage />} />
          <Route path="/career/*"     element={<CareerHubPage />} />
          <Route path="/analytics/*"  element={<AnalyticsHubPage />} />
          <Route path="/community"    element={<CommunityPage />} />
          <Route path="/chat"         element={<ChatPage />} />
          <Route path="/settings"     element={<SettingsPage />} />

          {/* Backward-compatible redirects */}
          <Route path="/interview"    element={<Navigate to="/practice/interview" replace />} />
          <Route path="/company-prep" element={<Navigate to="/practice/company" replace />} />
          <Route path="/careers"      element={<Navigate to="/career/tracks" replace />} />
          <Route path="/skill-gap"    element={<Navigate to="/career/skill-gap" replace />} />
          <Route path="/learning"     element={<Navigate to="/career/roadmap" replace />} />
          <Route path="/resume"       element={<Navigate to="/analytics/resume" replace />} />
          <Route path="/certificates" element={<Navigate to="/analytics/certs" replace />} />
          <Route path="/profile"      element={<Navigate to="/analytics/profile" replace />} />
        </Route>
      </Route>

      {/* Default routes */}
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <LandingPage />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  )
}
