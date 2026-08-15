import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import {
  LayoutDashboard, User, FileText, Briefcase, Target,
  BookOpen, MessageSquare, Settings, LogOut, Compass, X,
  FileCheck, Bot, Building2, Users
} from 'lucide-react'

const navItems = [
  { to: '/dashboard',    label: 'Career Dashboard', icon: LayoutDashboard },
  { to: '/profile',      label: 'Career Profile',   icon: User },
  { to: '/certificates', label: 'Certificates',     icon: FileText },
  { to: '/careers',      label: 'Career Tracks',    icon: Briefcase },
  { to: '/skill-gap',    label: 'Skill Gap Matrix', icon: Target },
  { to: '/learning',     label: 'Learning Roadmap', icon: BookOpen },
  { to: '/resume',       label: 'Resume & ATS',     icon: FileCheck },
  { to: '/interview',    label: 'AI Interview',     icon: Bot },
  { to: '/company-prep', label: 'Company Prep',     icon: Building2 },
  { to: '/community',    label: 'Peer Community',   icon: Users },
  { to: '/chat',         label: 'AI Career Mentor', icon: MessageSquare },
]

interface SidebarProps {
  open: boolean
  onClose: () => void
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const { logout, user } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const sidebarContent = (
    <div className="flex flex-col h-full bg-surface text-app border-r border-app">
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-app">
        <div className="w-8 h-8 rounded-md bg-[#1a1f3a] dark:bg-[#141936] flex items-center justify-center flex-shrink-0 text-white shadow-xs">
          <Compass className="w-4 h-4 text-[#FF5722]" />
        </div>
        <div className="flex-1 min-w-0">
          <span className="font-heading text-base font-bold tracking-tight text-app block">
            CareerPilot <span className="text-[#FF5722] dark:text-[#FF7043] font-sans text-[10px] font-bold uppercase tracking-wider ml-0.5">AI</span>
          </span>
          <span className="text-[10px] uppercase tracking-wider font-medium text-muted block -mt-0.5">Career Intelligence</span>
        </div>
        {/* Mobile close */}
        <button
          onClick={onClose}
          className="ml-auto lg:hidden p-1.5 text-muted hover:text-app"
          aria-label="Close sidebar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 text-xs font-medium transition-all duration-150 rounded-md ${
                isActive
                  ? 'bg-[#FF5722]/10 text-[#FF5722] border-l-2 border-[#FF5722] font-semibold dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043]'
                  : 'text-secondary hover:bg-subtle hover:text-app'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-[#FF5722] dark:text-[#FF7043]' : 'text-muted'}`} />
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom section */}
      <div className="px-3 py-3 border-t border-app space-y-1">
        <NavLink
          to="/settings"
          onClick={onClose}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 text-xs font-medium transition-all duration-150 rounded-md ${
              isActive
                ? 'bg-[#FF5722]/10 text-[#FF5722] border-l-2 border-[#FF5722] font-semibold dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043]'
                : 'text-secondary hover:bg-subtle hover:text-app'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <Settings className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-[#FF5722] dark:text-[#FF7043]' : 'text-muted'}`} />
              <span>Settings</span>
            </>
          )}
        </NavLink>

        {/* User info */}
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-md bg-subtle mt-2 border border-app">
          <div className="w-7 h-7 bg-emerald-700 dark:bg-emerald-600 rounded-md flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {user?.displayName?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-app truncate">
              {user?.displayName || 'Candidate'}
            </p>
            <p className="text-[10px] text-muted truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="p-1.5 text-muted hover:text-red-600 transition-colors"
            title="Logout"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-60 flex-shrink-0 bg-surface border-r border-app flex-col">
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-xs" onClick={onClose} />
          <aside className="absolute left-0 top-0 h-full w-64 bg-surface flex flex-col shadow-lg">
            {sidebarContent}
          </aside>
        </div>
      )}
    </>
  )
}
