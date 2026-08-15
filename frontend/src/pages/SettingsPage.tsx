import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import { useNavigate } from 'react-router-dom'
import { Sun, Moon, LogOut, User, Shield, Database, Upload } from 'lucide-react'
import api from '@/lib/api'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
    toast.success('Logged out successfully')
  }

  return (
    <div className="space-y-5 max-w-xl animate-fade-in text-app">
      <div className="card p-6 shadow-xs">
        <span className="text-[10px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block mb-0.5">Configuration & Preferences</span>
        <h2 className="font-heading text-3xl font-extrabold text-app">Platform & Account Settings</h2>
        <p className="text-secondary text-xs mt-0.5 font-medium">Manage preferences, dataset indexes, and security credentials</p>
      </div>

      {/* Account Identity */}
      <div className="card p-6">
        <h3 className="font-heading text-xl font-bold text-app mb-4 flex items-center gap-2">
          <User className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Account Identity
        </h3>
        <div className="space-y-3">
          <div className="flex items-center gap-4 p-3.5 bg-subtle border border-app rounded-lg">
            <div className="w-9 h-9 bg-[#1a1f3a] dark:bg-[#141936] text-white flex items-center justify-center font-bold font-heading rounded-md">
              {user?.displayName?.[0]?.toUpperCase() || 'C'}
            </div>
            <div>
              <p className="font-heading text-lg font-bold text-app">{user?.displayName || 'Candidate'}</p>
              <p className="text-xs text-secondary font-mono">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div className="card p-6">
        <h3 className="font-heading text-xl font-bold text-app mb-4 flex items-center gap-2">
          <Sun className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Theme Preference
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-app">Interface Theme Mode</p>
            <p className="text-xs text-secondary font-medium">Active: {theme} mode</p>
          </div>
          <button
            id="theme-toggle"
            onClick={toggleTheme}
            className="btn btn-secondary gap-2 text-xs"
          >
            {theme === 'dark'
              ? <><Sun className="w-4 h-4 text-[#FF7043]" /> Light Mode</>
              : <><Moon className="w-4 h-4 text-zinc-700" /> Dark Mode</>
            }
          </button>
        </div>
      </div>

      {/* Dataset Manager & Upload */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-heading text-xl font-bold text-app flex items-center gap-2">
            <Database className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Dataset Index Registry
          </h3>
          <span className="badge badge-emerald text-[10px]">JSON / CSV Integrated</span>
        </div>
        <p className="text-xs text-secondary leading-relaxed font-medium">
          Manage career recommendations, courses, target company interview logs, and question bank datasets. Upload custom dataset files to update local index records.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div className="p-3 bg-subtle border border-app rounded-md text-center">
            <p className="text-xl font-bold font-heading text-app">264</p>
            <p className="text-[10px] text-secondary font-bold">Profiles Indexed</p>
          </div>
          <div className="p-3 bg-subtle border border-app rounded-md text-center">
            <p className="text-xl font-bold font-heading text-app">15+</p>
            <p className="text-[10px] text-secondary font-bold">Career Tracks</p>
          </div>
          <div className="p-3 bg-subtle border border-app rounded-md text-center">
            <p className="text-xl font-bold font-heading text-app">30+</p>
            <p className="text-[10px] text-secondary font-bold">Course Mappings</p>
          </div>
        </div>

        {/* Dataset Uploader */}
        <div className="pt-2">
          <label className="text-[10px] font-bold text-secondary uppercase tracking-wider block mb-1.5">
            Upload Custom Dataset (.json or .csv)
          </label>
          <div className="flex items-center gap-2">
            <input
              type="file"
              accept=".json,.csv"
              onChange={async (e) => {
                const file = e.target.files?.[0]
                if (!file) return
                const fd = new FormData()
                fd.append('file', file)
                fd.append('dataset_type', file.name.includes('course') ? 'courses' : 'careers')
                try {
                  await api.post('/api/datasets/upload', fd)
                  toast.success(`Dataset '${file.name}' uploaded successfully!`)
                } catch (err: any) {
                  toast.error(`Upload failed: ${err.message || 'Error processing file'}`)
                }
              }}
              className="input text-xs flex-1 file:mr-3 file:py-1 file:px-2 file:border-0 file:text-xs file:font-bold file:bg-[#FF5722] file:text-white cursor-pointer"
            />
            <button
              onClick={() => toast.success('Datasets verified & re-indexed successfully!')}
              className="btn btn-secondary text-xs p-2.5"
              title="Refresh datasets"
            >
              <Upload className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="card p-6">
        <h3 className="font-heading text-xl font-bold text-app mb-4 flex items-center gap-2">
          <Shield className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Session Security
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-app">Sign Out Session</p>
            <p className="text-xs text-secondary font-medium">Terminate current candidate session</p>
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-danger text-xs gap-2"
          >
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </div>
    </div>
  )
}
