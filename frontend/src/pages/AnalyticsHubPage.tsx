import { NavLink, Routes, Route, Navigate } from 'react-router-dom'
import ResumePage from './ResumePage'
import CertificatesPage from './CertificatesPage'
import ProfilePage from './ProfilePage'
import { FileCheck, Award, User } from 'lucide-react'

export default function AnalyticsHubPage() {
  const subNav = [
    { to: '/analytics/resume',   label: 'ATS Resume Review', icon: FileCheck },
    { to: '/analytics/certs',    label: 'Verified Credentials', icon: Award },
    { to: '/analytics/profile',  label: 'Candidate Dossier', icon: User },
  ]

  return (
    <div className="space-y-6">
      {/* Contextual Horizontal Sub-Navigation */}
      <div className="bg-surface border border-app rounded-md p-1.5 flex items-center gap-1.5 overflow-x-auto">
        {subNav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-2 px-4 py-2 text-xs font-bold transition-all rounded-md flex-shrink-0 ${
                isActive
                  ? 'bg-emerald-50 text-emerald-900 border-b-2 border-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-500 shadow-2xs'
                  : 'text-secondary hover:bg-subtle hover:text-app'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={`w-4 h-4 ${isActive ? 'text-emerald-700 dark:text-emerald-400' : 'text-muted'}`} />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>

      {/* Sub-module Routes */}
      <Routes>
        <Route index element={<Navigate to="resume" replace />} />
        <Route path="resume"  element={<ResumePage />} />
        <Route path="certs"   element={<CertificatesPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Routes>
    </div>
  )
}
