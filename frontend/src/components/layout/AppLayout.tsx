import { Outlet, NavLink } from 'react-router-dom'
import FloatingLeftDock from './FloatingLeftDock'
import EntranceAnimation from './EntranceAnimation'
import { Compass } from 'lucide-react'
import { SubtlePathsBg } from '@/components/ui/subtle-paths-bg'

export default function AppLayout() {
  const mobileNav = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/practice',  label: 'Practice' },
    { to: '/career',    label: 'Career' },
    { to: '/analytics', label: 'Analytics' },
  ]

  return (
    <div className="min-h-screen bg-app text-app flex flex-col font-sans relative overflow-x-hidden">
      {/* Ambient Animated Path Background across all application pages */}
      <SubtlePathsBg opacity={0.35} sets={2} />

      {/* One-Time Entrance Animation */}
      <EntranceAnimation />

      {/* Floating Left Dock (Desktop) */}
      <FloatingLeftDock />

      {/* Compact Top Navigation Bar (Mobile only) */}
      <header className="lg:hidden sticky top-0 z-30 bg-surface border-b border-app px-4 py-3 flex items-center justify-between">
        <NavLink to="/dashboard" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-[#1a1f3a] text-white flex items-center justify-center">
            <Compass className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-heading text-sm font-bold text-app">CareerPilot AI</span>
        </NavLink>

        <nav className="flex items-center gap-1 text-xs font-bold">
          {mobileNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `px-2.5 py-1 rounded-md ${
                  isActive ? 'bg-[#FF5722] text-white' : 'text-secondary'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      {/* Main Content Area with Comfortable Whitespace to Left Dock */}
      <div className="flex-1 w-full lg:pl-72 lg:pr-8 px-4 py-6 max-w-7xl mx-auto">
        <main className="animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
