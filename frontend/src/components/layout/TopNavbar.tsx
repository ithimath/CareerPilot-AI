import { Menu, Sun, Moon } from 'lucide-react'
import { useTheme } from '@/context/ThemeContext'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, string> = {
  '/dashboard':    'Career Dashboard',
  '/profile':      'Candidate Profile',
  '/certificates': 'Verified Credentials',
  '/careers':      'Market Career Tracks',
  '/skill-gap':    'Skill Gap Analysis',
  '/learning':     'Curriculum Roadmap',
  '/resume':       'Resume & ATS Diagnostics',
  '/interview':    'AI Technical Interviewer',
  '/company-prep': 'Company Intelligence',
  '/community':    'Candidate Network',
  '/chat':         'AI Career Strategist',
  '/settings':     'Platform Settings',
}

interface TopNavbarProps {
  onMenuClick: () => void
}

export default function TopNavbar({ onMenuClick }: TopNavbarProps) {
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'CareerPilot AI'

  return (
    <header className="bg-surface border-b border-app px-5 md:px-7 h-15 flex items-center gap-4 flex-shrink-0">
      {/* Mobile hamburger */}
      <button
        onClick={onMenuClick}
        className="lg:hidden p-1.5 text-app hover:bg-subtle transition-colors rounded-md"
        aria-label="Open sidebar"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Page title */}
      <div className="flex-1 min-w-0">
        <h1 className="font-heading text-lg md:text-xl font-bold text-app tracking-tight truncate">
          {title}
        </h1>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <span className="hidden sm:inline-flex px-2.5 py-1 rounded bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 text-[11px] font-semibold tracking-tight">
          Target Track: Full-Stack Engineer
        </span>

        {/* Theme toggle */}
        <button
          id="theme-toggle-nav"
          onClick={toggleTheme}
          className="p-2 text-secondary hover:bg-subtle transition-colors rounded-md border border-app"
          aria-label="Toggle theme"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark'
            ? <Sun className="w-4 h-4 text-[#FF7043]" />
            : <Moon className="w-4 h-4 text-zinc-700" />
          }
        </button>
      </div>
    </header>
  )
}
