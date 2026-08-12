import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import api from '@/lib/api'
import {
  User, Code, Globe, Save, Edit3, Camera,
  Plus, X, Briefcase, Link as LinkIcon
} from 'lucide-react'
import toast from 'react-hot-toast'

function SkillBadge({ skill, onRemove }: { skill: string; onRemove?: () => void }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-bold bg-teal-50 text-teal-900 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-800 rounded-md">
      {skill}
      {onRemove && (
        <button onClick={onRemove} className="hover:text-red-600 transition-colors">
          <X className="w-3 h-3" />
        </button>
      )}
    </span>
  )
}

function Section({ title, icon: Icon, children }: { title: string; icon: any; children: React.ReactNode }) {
  return (
    <div className="card p-6 space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-app">
        <Icon className="w-4 h-4 text-teal-700 dark:text-teal-400" />
        <h3 className="font-heading text-lg font-bold text-app">{title}</h3>
      </div>
      {children}
    </div>
  )
}

export default function ProfilePage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [newSkill, setNewSkill] = useState('')
  const [newInterest, setNewInterest] = useState('')
  const [form, setForm] = useState<any>({})

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/api/profile').then(r => r.data),
  })

  useEffect(() => {
    if (profile) setForm(profile)
  }, [profile])

  const updateMutation = useMutation({
    mutationFn: (data: any) => api.put('/api/profile', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      queryClient.invalidateQueries({ queryKey: ['jobScore'] })
      setEditing(false)
      toast.success('Candidate Profile saved successfully')
    },
    onError: (err: any) => toast.error(`Save failed: ${err.message}`),
  })

  const pictureMutation = useMutation({
    mutationFn: (file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return api.post('/api/profile/picture', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      toast.success('Profile picture updated')
    },
    onError: () => toast.error('Picture upload failed'),
  })

  const set = (field: string, val: any) => setForm((f: any) => ({ ...f, [field]: val }))
  const p = editing ? form : (profile || {})

  const addSkill = () => {
    if (!newSkill.trim()) return
    const skills = [...(form.skills || []), newSkill.trim()]
    setForm({ ...form, skills })
    setNewSkill('')
  }

  const removeSkill = (skill: string) => {
    const skills = (form.skills || []).filter((s: string) => s !== skill)
    setForm({ ...form, skills })
  }

  const addInterest = () => {
    if (!newInterest.trim()) return
    const interests = [...(form.interests || []), newInterest.trim()]
    setForm({ ...form, interests })
    setNewInterest('')
  }

  const removeInterest = (interest: string) => {
    const interests = (form.interests || []).filter((i: string) => i !== interest)
    setForm({ ...form, interests })
  }

  const handlePicture = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) pictureMutation.mutate(file)
  }

  const handleSave = () => {
    updateMutation.mutate(form)
  }

  return (
    <div className="space-y-5 max-w-3xl animate-fade-in text-app">
      {/* Header */}
      <div className="card p-6 flex items-start justify-between gap-4 flex-wrap shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-1">Candidate Profile Dossier</span>
          <h2 className="font-heading text-3xl font-extrabold text-app">Candidate Profile</h2>
          <p className="text-secondary text-xs mt-0.5 font-medium">Maintain verified credentials and skills for recruiter ATS matching</p>
        </div>
        {editing ? (
          <div className="flex gap-2">
            <button onClick={() => { setEditing(false); setForm(profile) }} className="btn btn-secondary text-xs">Cancel</button>
            <button onClick={handleSave} disabled={updateMutation.isPending} className="btn btn-primary text-xs gap-2">
              {updateMutation.isPending && <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />}
              <Save className="w-4 h-4" />
              Save Profile
            </button>
          </div>
        ) : (
          <button onClick={() => setEditing(true)} className="btn btn-primary text-xs gap-2">
            <Edit3 className="w-4 h-4" /> Edit Dossier
          </button>
        )}
      </div>

      {/* Personal Info */}
      <Section title="Personal Identification & Education" icon={User}>
        <div className="flex items-start gap-6 flex-wrap">
          {/* Avatar */}
          <div className="relative flex-shrink-0">
            <div className="w-20 h-20 overflow-hidden bg-subtle rounded-xl border border-app">
              {profile?.profile_picture_url ? (
                <img src={profile.profile_picture_url} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-teal-700 dark:bg-teal-600 flex items-center justify-center text-white text-2xl font-bold font-heading">
                  {user?.displayName?.[0]?.toUpperCase() || 'C'}
                </div>
              )}
            </div>
            <label className="absolute -bottom-1 -right-1 w-7 h-7 bg-teal-700 hover:bg-teal-800 flex items-center justify-center cursor-pointer transition-colors rounded-md">
              <Camera className="w-3.5 h-3.5 text-white" />
              <input type="file" accept="image/*" className="hidden" onChange={handlePicture} />
            </label>
          </div>

          {/* Fields */}
          <div className="flex-1 grid sm:grid-cols-2 gap-4 min-w-0">
            {[
              { key: 'name', label: 'Full Legal Name', type: 'text' },
              { key: 'email', label: 'Registered Email', type: 'email', disabled: true },
              { key: 'college', label: 'Academic Institution', type: 'text' },
              { key: 'degree', label: 'Degree Program', type: 'text', placeholder: 'B.Tech, B.S., M.S...' },
              { key: 'department', label: 'Department / Major', type: 'text', placeholder: 'Computer Science...' },
              { key: 'current_year', label: 'Academic Year', type: 'number' },
              { key: 'cgpa', label: 'Cumulative GPA (Scale 10)', type: 'number', step: '0.01', min: '0', max: '10' },
            ].map(({ key, label, type, placeholder, disabled, step, min, max }) => (
              <div key={key}>
                <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1 block">{label}</label>
                <input
                  type={type}
                  className="input text-xs"
                  placeholder={placeholder}
                  value={p[key] || ''}
                  disabled={!editing || disabled}
                  step={step}
                  min={min}
                  max={max}
                  onChange={(e) => set(key, type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value)}
                />
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* Links */}
      <Section title="Professional Profiles & Repository Links" icon={Globe}>
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { key: 'github_url', label: 'GitHub Repository', icon: Code, placeholder: 'github.com/username' },
            { key: 'linkedin_url', label: 'LinkedIn Profile', icon: LinkIcon, placeholder: 'linkedin.com/in/...' },
            { key: 'portfolio_url', label: 'Personal Portfolio', icon: Globe, placeholder: 'yoursite.com' },
          ].map(({ key, label, icon: Icon, placeholder }) => (
            <div key={key}>
              <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1 block">{label}</label>
              <div className="relative">
                <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-secondary" />
                <input
                  type="url"
                  className="input pl-8 text-xs"
                  placeholder={placeholder}
                  value={p[key] || ''}
                  disabled={!editing}
                  onChange={(e) => set(key, e.target.value)}
                />
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Skills */}
      <Section title="Verified Technical Skills" icon={Code}>
        <div className="flex flex-wrap gap-2 mb-3">
          {(p.skills || []).length === 0 && (
            <p className="text-secondary text-xs font-medium">No technical skills documented yet.</p>
          )}
          {(p.skills || []).map((skill: string) => (
            <SkillBadge key={skill} skill={skill} onRemove={editing ? () => removeSkill(skill) : undefined} />
          ))}
        </div>
        {editing && (
          <div className="flex gap-2">
            <input
              className="input flex-1 text-xs"
              placeholder="Add skill (e.g. JavaScript, React, SQL, Docker)"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addSkill()}
            />
            <button onClick={addSkill} className="btn btn-primary px-3"><Plus className="w-4 h-4" /></button>
          </div>
        )}
      </Section>

      {/* Interests */}
      <Section title="Career Field Focus Areas" icon={Briefcase}>
        <div className="flex flex-wrap gap-2 mb-3">
          {(p.interests || []).length === 0 && (
            <p className="text-secondary text-xs font-medium">Specify career focus areas to customize recommendations.</p>
          )}
          {(p.interests || []).map((interest: string) => (
            <span key={interest} className="inline-flex items-center gap-1 px-3 py-1 text-xs font-bold bg-subtle text-app border border-app rounded-md">
              {interest}
              {editing && (
                <button onClick={() => removeInterest(interest)} className="hover:text-red-600 ml-0.5"><X className="w-3 h-3" /></button>
              )}
            </span>
          ))}
        </div>
        {editing && (
          <div className="flex gap-2">
            <input
              className="input flex-1 text-xs"
              placeholder="Add interest (e.g. Distributed Systems, Frontend Engineering)"
              value={newInterest}
              onChange={(e) => setNewInterest(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addInterest()}
            />
            <button onClick={addInterest} className="btn btn-primary px-3"><Plus className="w-4 h-4" /></button>
          </div>
        )}
      </Section>

      {/* Profile completion */}
      {profile?.profile_completion && (
        <div className="card p-5">
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-heading text-lg font-bold text-app">Profile Completeness Rate</h4>
            <span className="font-heading text-lg font-bold text-teal-700 dark:text-teal-400">{profile.profile_completion.percentage}%</span>
          </div>
          <div className="w-full h-2 bg-subtle border border-app overflow-hidden rounded-full">
            <div className="h-full bg-teal-700 dark:bg-teal-500 transition-all rounded-full" style={{ width: `${profile.profile_completion.percentage}%` }} />
          </div>
        </div>
      )}
    </div>
  )
}
