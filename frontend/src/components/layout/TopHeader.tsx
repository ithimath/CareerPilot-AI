import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import {
  Compass, Search, Bell, Sun, Moon, LogOut,
  User, Settings, ChevronDown, Sparkles, Users
} from 'lucide-react'

export default function TopHeader() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const [profileOpen, setProfileOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const primaryNav = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/practice',  label: 'Practice' },
    { to: '/career',    label: 'Career' },
    { to: '/analytics', label: 'Analytics' },
  ]

  return (
    <header className="sticky top-0 z-40 bg-surface border-b border-app shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">

        {/* Left: Brand & Primary Top Nav */}
        <div className="flex items-center gap-8">
          <NavLink to="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-md bg-[#1a1f3a] dark:bg-[#141936] flex items-center justify-center text-white shadow-xs group-hover:bg-[#252c50] transition-colors">
              <Compass className="w-4 h-4 text-[#FF5722]" />
            </div>
            <div>
              <span className="font-heading text-lg font-extrabold tracking-tight text-app block leading-none">
                CareerPilot <span className="text-[#FF5722] dark:text-[#FF7043] font-sans text-xs font-black uppercase tracking-wider ml-0.5">AI</span>
              </span>
              <span className="text-[9px] uppercase tracking-widest font-bold text-secondary block mt-0.5">Career Intelligence</span>
            </div>
          </NavLink>

          {/* Primary Top Nav Links */}
          <nav className="hidden md:flex items-center gap-1">
            {primaryNav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `px-3.5 py-2 text-xs font-bold transition-all rounded-md flex items-center gap-1.5 ${
                    isActive
                      ? 'bg-[#FF5722]/10 text-[#FF5722] border-b-2 border-[#FF5722] dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043]'
                      : 'text-secondary hover:bg-subtle hover:text-app'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Center: Quick Search Input */}
        <div className="hidden lg:flex items-center flex-1 max-w-xs relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-secondary" />
          <input
            type="text"
            placeholder="Search skills, roles, prep..."
            className="input pl-9 pr-3 py-1.5 text-xs bg-subtle rounded-full border-app focus:bg-surface font-medium"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Right Actions Toolbar */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Quick AI Mentor Link */}
          <NavLink
            to="/chat"
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-[#FF5722] bg-[#FF5722]/10 border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded-md hover:bg-[#FF5722]/20 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#FF5722] dark:text-[#FF7043]" />
            <span>AI Mentor</span>
          </NavLink>

          {/* Peer Community */}
          <NavLink
            to="/community"
            className="p-2 text-secondary hover:bg-subtle rounded-md transition-colors border border-transparent hover:border-app"
            title="Peer Community"
          >
            <Users className="w-4 h-4" />
          </NavLink>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 text-secondary hover:bg-subtle rounded-md transition-colors border border-transparent hover:border-app"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-[#FF7043]" /> : <Moon className="w-4 h-4 text-zinc-700" />}
          </button>

          {/* Notifications Dropdown */}
          <div className="relative">
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              className="p-2 text-secondary hover:bg-subtle rounded-md transition-colors relative border border-transparent hover:border-app"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-[#FF5722] rounded-full" />
            </button>

            {notifOpen && (
              <div className="absolute right-0 mt-2 w-72 bg-surface border border-app rounded-md shadow-lg py-2 z-50 animate-fade-in">
                <div className="px-4 py-2 border-b border-app flex items-center justify-between">
                  <span className="text-xs font-extrabold text-app">Notifications</span>
                  <span className="badge badge-emerald text-[10px]">2 New</span>
                </div>
                <div className="divide-y divide-app text-xs max-h-60 overflow-y-auto">
                  <div className="p-3 hover:bg-subtle cursor-pointer">
                    <p className="font-bold text-app">Readiness Assessment Updated</p>
                    <p className="text-secondary text-[11px] mt-0.5">Your composite score increased to 82% after certificate verification.</p>
                  </div>
                  <div className="p-3 hover:bg-subtle cursor-pointer">
                    <p className="font-bold text-app">New Full-Stack Track Match</p>
                    <p className="text-secondary text-[11px] mt-0.5">Target company Google added 3 new interview prompts.</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Profile Dropdown */}
          <div className="relative">
            <button
              onClick={() => setProfileOpen(!profileOpen)}
              className="flex items-center gap-2 pl-2 pr-1.5 py-1 rounded-md hover:bg-subtle transition-colors border border-transparent hover:border-app"
            >
              <div className="w-7 h-7 bg-[#1a1f3a] dark:bg-[#141936] text-white rounded-md flex items-center justify-center text-xs font-extrabold shadow-2xs">
                {user?.displayName?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
              </div>
              <span className="hidden sm:inline text-xs font-bold text-app truncate max-w-[100px]">
                {user?.displayName?.split(' ')[0] || 'Candidate'}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-secondary" />
            </button>

            {profileOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-surface border border-app rounded-md shadow-lg py-1.5 z-50 animate-fade-in space-y-0.5">
                <div className="px-4 py-2 border-b border-app">
                  <p className="text-xs font-bold text-app truncate">{user?.displayName || 'Candidate User'}</p>
                  <p className="text-[10px] text-secondary truncate font-mono">{user?.email}</p>
                </div>
                <NavLink
                  to="/analytics"
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-2 px-4 py-2 text-xs font-medium text-secondary hover:bg-subtle hover:text-app"
                >
                  <User className="w-3.5 h-3.5" /> Candidate Profile & Dossier
                </NavLink>
                <NavLink
                  to="/settings"
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-2 px-4 py-2 text-xs font-medium text-secondary hover:bg-subtle hover:text-app"
                >
                  <Settings className="w-3.5 h-3.5" /> Account & Platform Settings
                </NavLink>
                <div className="border-t border-app my-1" />
                <button
                  onClick={() => { setProfileOpen(false); handleLogout() }}
                  className="w-full flex items-center gap-2 px-4 py-2 text-xs font-bold text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 text-left"
                >
                  <LogOut className="w-3.5 h-3.5" /> Sign Out Session
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Sub-Nav Row */}
      <div className="md:hidden flex items-center justify-around border-t border-app bg-subtle px-2 py-1.5 text-xs font-bold">
        {primaryNav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `px-2.5 py-1 rounded ${
                isActive ? 'bg-[#FF5722] text-white' : 'text-secondary'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </div>
    </header>
  )
}
