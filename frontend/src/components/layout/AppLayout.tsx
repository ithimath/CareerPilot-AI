import { useState, useEffect } from 'react'
import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom'
import FloatingLeftDock from './FloatingLeftDock'
import EntranceAnimation from './EntranceAnimation'
import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import {
  Compass, LayoutDashboard, Bot, Briefcase, FileCheck,
  Sparkles, Users, Settings, Sun, Moon, LogOut, Menu, X, ChevronRight, Target
} from 'lucide-react'
import { SubtlePathsBg } from '@/components/ui/subtle-paths-bg'

export default function AppLayout() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()
  const navigate = useNavigate()
  const [drawerOpen, setDrawerOpen] = useState(false)

  // Automatically close mobile navigation drawer on route change
  useEffect(() => {
    setDrawerOpen(false)
  }, [location.pathname])

  // Prevent background scrolling when mobile drawer is open
  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [drawerOpen])

  const handleLogout = async () => {
    setDrawerOpen(false)
    await logout()
    navigate('/login')
  }

  // Primary mobile bottom navigation tabs (accessible via thumb)
  const bottomNavItems = [
    { to: '/dashboard',           label: 'Dashboard', icon: LayoutDashboard },
    { to: '/practice/interview',  label: 'Practice',  icon: Bot },
    { to: '/career/tracks',       label: 'Careers',   icon: Briefcase },
    { to: '/analytics/resume',    label: 'Analytics', icon: FileCheck },
    { to: '/chat',                label: 'AI Mentor', icon: Sparkles },
  ]

  // Full platform drawer navigation items
  const drawerSections = [
    {
      title: 'Platform Core',
      items: [
        { to: '/dashboard', label: 'Dashboard Command Center', icon: LayoutDashboard },
        { to: '/chat', label: 'AI Career Mentor & Strategist', icon: Sparkles },
        { to: '/community', label: 'Candidate Peer Network', icon: Users },
      ]
    },
    {
      title: 'Practice & Simulation',
      items: [
        { to: '/practice/interview', label: 'AI Technical Interview', icon: Bot },
        { to: '/practice/tests', label: 'Technical Mock Tests', icon: FileCheck },
        { to: '/practice/company', label: 'Company Intelligence Briefs', icon: Compass },
      ]
    },
    {
      title: 'Career Trajectory',
      items: [
        { to: '/career/tracks', label: 'Market Career Tracks', icon: Briefcase },
        { to: '/career/skill-gap', label: 'Skill Gap Analysis Matrix', icon: Target },
        { to: '/career/roadmap', label: 'AI Learning Roadmap', icon: Compass },
      ]
    },
    {
      title: 'Analytics & Credentials',
      items: [
        { to: '/analytics/resume', label: 'ATS Resume Review', icon: FileCheck },
        { to: '/analytics/certs', label: 'Verified Credentials & OCR', icon: FileCheck },
        { to: '/analytics/profile', label: 'Candidate Dossier', icon: Users },
      ]
    },
  ]

  return (
    <div className="min-h-screen bg-app text-app flex flex-col font-sans relative overflow-x-hidden w-full max-w-full">
      {/* Ambient Animated Path Background */}
      <SubtlePathsBg opacity={0.35} sets={2} />

      {/* One-Time Entrance Animation */}
      <EntranceAnimation />

      {/* Floating Left Dock (Desktop only: lg:flex) */}
      <FloatingLeftDock />

      {/* ── Compact Responsive Top Navigation Bar (Mobile / Tablet only: lg:hidden) ── */}
      <header className="lg:hidden sticky top-0 z-40 bg-surface/95 backdrop-blur-md border-b border-app px-3.5 sm:px-4 py-2.5 flex items-center justify-between shadow-2xs w-full">
        {/* Brand */}
        <NavLink to="/dashboard" className="flex items-center gap-2 flex-shrink-0">
          <div className="w-8 h-8 rounded-xl bg-[#1a1f3a] dark:bg-[#141936] text-white flex items-center justify-center shadow-xs border border-[#FF5722]/30">
            <Compass className="w-4 h-4 text-[#FF5722]" />
          </div>
          <span className="font-heading text-sm font-extrabold text-app tracking-tight">
            CareerPilot <span className="text-[#FF5722] dark:text-[#FF7043] font-sans text-[11px] font-black uppercase">AI</span>
          </span>
        </NavLink>

        {/* Action cluster on right */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          {/* Quick theme toggle */}
          <button
            onClick={toggleTheme}
            className="w-9 h-9 flex items-center justify-center text-secondary hover:bg-subtle rounded-lg transition-colors border border-transparent hover:border-app"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            aria-label="Toggle theme mode"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-[#FF7043]" /> : <Moon className="w-4 h-4 text-zinc-700" />}
          </button>

          {/* Chat shortcut */}
          <NavLink
            to="/chat"
            className="w-9 h-9 flex items-center justify-center text-secondary hover:bg-subtle rounded-lg transition-colors border border-transparent hover:border-app"
            title="AI Mentor Chat"
            aria-label="Open AI Mentor Chat"
          >
            <Sparkles className="w-4 h-4 text-[#FF5722]" />
          </NavLink>

          {/* Hamburger Drawer Toggle */}
          <button
            onClick={() => setDrawerOpen(true)}
            className="w-9 h-9 flex items-center justify-center text-app bg-subtle hover:bg-surface-hover rounded-lg transition-colors border border-app"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5 text-app" />
          </button>
        </div>
      </header>

      {/* ── Slide-Over Mobile Navigation Drawer (lg:hidden) ── */}
      {drawerOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          {/* Backdrop overlay */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity animate-fade-in"
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />

          {/* Drawer sheet */}
          <div className="relative ml-auto w-full max-w-xs sm:max-w-sm bg-surface border-l border-app shadow-2xl h-full flex flex-col justify-between z-50 animate-fade-in overflow-hidden">
            {/* Drawer Header */}
            <div className="p-4 border-b border-app flex items-center justify-between bg-surface">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#1a1f3a] dark:bg-[#141936] text-white flex items-center justify-center border border-[#FF5722]/30">
                  <Compass className="w-4 h-4 text-[#FF5722]" />
                </div>
                <div>
                  <p className="font-heading text-sm font-bold text-app">CareerPilot AI</p>
                  <p className="text-[10px] text-secondary font-medium">Candidate Command Center</p>
                </div>
              </div>

              <button
                onClick={() => setDrawerOpen(false)}
                className="w-9 h-9 flex items-center justify-center rounded-lg text-secondary hover:text-app hover:bg-subtle transition-colors border border-app"
                aria-label="Close navigation menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scrollable Navigation List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-5 custom-scrollbar">
              {drawerSections.map((sec) => (
                <div key={sec.title} className="space-y-1.5">
                  <p className="text-[10px] font-extrabold uppercase tracking-wider text-secondary px-2 mb-1">
                    {sec.title}
                  </p>
                  {sec.items.map((item) => {
                    const Icon = item.icon
                    return (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                          `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all min-h-[42px] ${
                            isActive
                              ? 'bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 shadow-xs'
                              : 'text-secondary hover:bg-subtle hover:text-app'
                          }`
                        }
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-4 h-4 flex-shrink-0 text-[#FF5722]" />
                          <span>{item.label}</span>
                        </div>
                        <ChevronRight className="w-3.5 h-3.5 opacity-50" />
                      </NavLink>
                    )
                  })}
                </div>
              ))}

              {/* Account / Settings Section */}
              <div className="space-y-1.5 pt-2 border-t border-app">
                <p className="text-[10px] font-extrabold uppercase tracking-wider text-secondary px-2 mb-1">
                  Account & System
                </p>
                <NavLink
                  to="/settings"
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all min-h-[42px] ${
                      isActive
                        ? 'bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043]'
                        : 'text-secondary hover:bg-subtle hover:text-app'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <Settings className="w-4 h-4 flex-shrink-0 text-[#FF5722]" />
                    <span>Settings & Preferences</span>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 opacity-50" />
                </NavLink>

                <button
                  onClick={toggleTheme}
                  className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold text-secondary hover:bg-subtle hover:text-app transition-all min-h-[42px]"
                >
                  <div className="flex items-center gap-3">
                    {theme === 'dark' ? <Sun className="w-4 h-4 text-[#FF7043]" /> : <Moon className="w-4 h-4 text-zinc-700" />}
                    <span>Switch to {theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
                  </div>
                  <span className="text-[10px] uppercase font-mono text-muted">{theme}</span>
                </button>
              </div>
            </div>

            {/* Drawer Footer: User Profile & Sign Out */}
            <div className="p-4 border-t border-app bg-subtle space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-[#1a1f3a] dark:bg-[#141936] text-white flex items-center justify-center font-bold text-sm">
                  {user?.displayName?.[0]?.toUpperCase() || 'C'}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-bold text-app truncate">{user?.displayName || 'Candidate'}</p>
                  <p className="text-[10px] text-secondary truncate font-mono">{user?.email || 'Authenticated'}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="btn btn-secondary text-xs w-full justify-center gap-2 py-2 text-red-600 dark:text-red-400 hover:border-red-500"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Main Content Area ── */}
      {/* Desktop: Comfortable spacing to Left Dock (lg:pl-72 lg:pr-8). Mobile: comfortable padding with bottom nav offset (pb-20 lg:pb-6) */}
      <div className="flex-1 w-full lg:pl-72 lg:pr-8 px-3 sm:px-4 py-4 sm:py-6 pb-20 lg:pb-6 max-w-7xl mx-auto box-border overflow-x-hidden">
        <main className="animate-fade-in w-full max-w-full">
          <Outlet />
        </main>
      </div>

      {/* ── Ergonomic Mobile Bottom Navigation Bar (Mobile / Tablet only: lg:hidden) ── */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-30 bg-surface/95 backdrop-blur-md border-t border-app px-2 py-1 flex items-center justify-around shadow-lg safe-area-inset-bottom">
        {bottomNavItems.map((tab) => {
          const Icon = tab.icon
          return (
            <NavLink
              key={tab.to}
              to={tab.to}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center py-1.5 px-2 rounded-lg transition-all min-w-[56px] text-[10px] font-bold ${
                  isActive
                    ? 'text-[#FF5722] dark:text-[#FF7043]'
                    : 'text-secondary hover:text-app'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className={`p-1 rounded-md transition-colors ${isActive ? 'bg-[#FF5722]/15 dark:bg-[#FF7043]/20' : ''}`}>
                    <Icon className={`w-4 h-4 ${isActive ? 'text-[#FF5722] dark:text-[#FF7043]' : 'text-secondary'}`} />
                  </div>
                  <span className="mt-0.5 tracking-tight truncate max-w-[64px]">{tab.label}</span>
                </>
              )}
            </NavLink>
          )
        })}
      </nav>
    </div>
  )
}
