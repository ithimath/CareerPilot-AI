import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import {
  Compass, LayoutDashboard, Bot, Briefcase, FileCheck,
  Sparkles, Users, Settings, Sun, Moon, LogOut, ChevronDown, Bell
} from 'lucide-react'

export default function FloatingLeftDock() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const [profileOpen, setProfileOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const navItems = [
    { to: '/dashboard', label: 'Dashboard',   icon: LayoutDashboard },
    { to: '/practice',  label: 'Practice',    icon: Bot },
    { to: '/career',    label: 'Career',      icon: Briefcase },
    { to: '/analytics', label: 'Analytics',   icon: FileCheck },
    { to: '/chat',      label: 'AI Mentor',   icon: Sparkles },
    { to: '/community', label: 'Community',   icon: Users },
  ]

  return (
    <aside className="hidden lg:flex fixed left-5 top-1/2 -translate-y-1/2 z-40 w-60 glass-dock rounded-2xl p-4 flex-col justify-between max-h-[92vh] overflow-y-auto transition-all">
      {/* Top: Brand Header */}
      <div className="space-y-4">
        <NavLink to="/dashboard" className="flex items-center gap-3 px-2 py-1 group">
          <div className="w-8 h-8 rounded-xl bg-[#1a1f3a] dark:bg-[#141936] border border-[#FF5722]/30 flex items-center justify-center text-white shadow-xs group-hover:bg-[#252c50] transition-colors flex-shrink-0">
            <Compass className="w-4 h-4 text-[#FF5722]" />
          </div>
          <div className="min-w-0">
            <span className="font-heading text-base font-extrabold tracking-tight text-app block leading-none truncate">
              CareerPilot <span className="text-[#FF5722] dark:text-[#FF7043] font-sans text-xs font-black uppercase tracking-wider ml-0.5">AI</span>
            </span>
            <span className="text-[9px] uppercase tracking-widest font-bold text-secondary block mt-0.5 truncate">Career Dock</span>
          </div>
        </NavLink>

        <div className="border-t border-app my-1" />

        {/* Primary Navigation Links */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 text-xs font-bold transition-all rounded-xl ${
                    isActive
                      ? 'bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 shadow-2xs'
                      : 'text-secondary hover:bg-subtle hover:text-app'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-[#FF5722] dark:text-[#FF7043]' : 'text-secondary'}`} />
                    <span className="truncate">{item.label}</span>
                  </>
                )}
              </NavLink>
            )
          })}
        </nav>
      </div>

      {/* Bottom: Utilities & Candidate Profile */}
      <div className="space-y-2 pt-3 border-t border-app mt-4">
        {/* Quick Utility Toolbar (Theme, Notifications, Settings) */}
        <div className="flex items-center justify-between px-1">
          <button
            onClick={toggleTheme}
            className="p-2 text-secondary hover:bg-subtle rounded-xl transition-colors border border-transparent hover:border-app"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-[#FF7043]" /> : <Moon className="w-4 h-4 text-zinc-700" />}
          </button>

          <div className="relative">
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              className="p-2 text-secondary hover:bg-subtle rounded-xl transition-colors relative border border-transparent hover:border-app"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#FF5722] rounded-full" />
            </button>

            {notifOpen && (
              <div className="absolute left-0 bottom-10 w-64 bg-surface border border-app rounded-xl shadow-lg py-2 z-50 animate-fade-in">
                <div className="px-4 py-2 border-b border-app flex items-center justify-between">
                  <span className="text-xs font-bold text-app">Notifications</span>
                  <span className="badge badge-emerald text-[10px]">2 New</span>
                </div>
                <div className="divide-y divide-app text-xs max-h-48 overflow-y-auto">
                  <div className="p-3 hover:bg-subtle cursor-pointer">
                    <p className="font-bold text-app">Readiness Score Updated</p>
                    <p className="text-secondary text-[11px] mt-0.5">Composite score increased to 82%.</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <NavLink
            to="/settings"
            className="p-2 text-secondary hover:bg-subtle rounded-xl transition-colors border border-transparent hover:border-app"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </NavLink>
        </div>

        {/* Profile Pill Popover */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="w-full flex items-center justify-between p-2 rounded-xl hover:bg-subtle transition-colors border border-app"
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-7 h-7 bg-[#1a1f3a] dark:bg-[#141936] text-white rounded-lg flex items-center justify-center text-xs font-extrabold shadow-2xs flex-shrink-0">
                {user?.displayName?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="min-w-0 text-left">
                <p className="text-xs font-bold text-app truncate max-w-[100px]">
                  {user?.displayName?.split(' ')[0] || 'Candidate'}
                </p>
                <p className="text-[9px] text-secondary font-mono truncate max-w-[100px]">{user?.email}</p>
              </div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-secondary flex-shrink-0" />
          </button>

          {profileOpen && (
            <div className="absolute left-0 bottom-12 w-full bg-surface border border-app rounded-xl shadow-lg py-1.5 z-50 animate-fade-in space-y-0.5">
              <NavLink
                to="/analytics"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-secondary hover:bg-subtle hover:text-app"
              >
                Profile & Dossier
              </NavLink>
              <NavLink
                to="/settings"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-secondary hover:bg-subtle hover:text-app"
              >
                Platform Settings
              </NavLink>
              <div className="border-t border-app my-1" />
              <button
                onClick={() => { setProfileOpen(false); handleLogout() }}
                className="w-full flex items-center gap-2 px-3 py-2 text-xs font-bold text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 text-left"
              >
                <LogOut className="w-3.5 h-3.5" /> Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
