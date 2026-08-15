import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import api from '@/lib/api'
import {
  User, Code, Globe, Save, Edit3, Camera,
  Plus, X, Briefcase, Link as LinkIcon, FolderGit2,
  AlertCircle, Target, Sparkles
} from 'lucide-react'
import toast from 'react-hot-toast'

const POPULAR_TECH_CHIPS = [
  'React', 'TypeScript', 'Python', 'Node.js', 'FastAPI',
  'PostgreSQL', 'Docker', 'AWS', 'Kubernetes', 'GraphQL',
  'System Design', 'TensorFlow', 'PyTorch', 'LangChain',
  'Flutter', 'Git', 'Tailwind CSS', 'SQL', 'Scikit-learn', 'Pandas'
]

function SkillBadge({ skill, onRemove }: { skill: string | { name: string; level?: string; verified?: boolean }; onRemove?: () => void }) {
  const name = typeof skill === 'string' ? skill : skill.name
  const level = typeof skill === 'string' ? 'Intermediate' : (skill.level || 'Intermediate')
  const verified = typeof skill === 'string' ? false : Boolean(skill.verified)

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-bold bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded-md shadow-2xs transition-all hover:scale-105">
      <span>{name}</span>
      <span className="text-[9px] px-1 py-0.2 bg-[#FF5722]/20 dark:bg-[#FF5722]/30 rounded text-[#FF5722] dark:text-[#FF7043] font-mono">
        {level}
      </span>
      {verified && <span className="text-[10px] text-emerald-500 font-bold" title="Verified Credential">✓</span>}
      {onRemove && (
        <button onClick={onRemove} className="hover:text-red-600 transition-colors ml-1" title="Remove skill">
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
        <Icon className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
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
  
  // Local state for skill & interest addition
  const [newSkill, setNewSkill] = useState('')
  const [newSkillLevel, setNewSkillLevel] = useState('Intermediate')
  const [newInterest, setNewInterest] = useState('')

  // Local state for adding project items
  const [newProjTitle, setNewProjTitle] = useState('')
  const [newProjDesc, setNewProjDesc] = useState('')
  const [newProjTech, setNewProjTech] = useState('')
  const [newProjGithub, setNewProjGithub] = useState('')
  const [newProjLive, setNewProjLive] = useState('')

  // Local state for adding internship items
  const [newExpCompany, setNewExpCompany] = useState('')
  const [newExpRole, setNewExpRole] = useState('')
  const [newExpDuration, setNewExpDuration] = useState('')
  const [newExpDesc, setNewExpDesc] = useState('')

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/api/profile').then((r) => r.data),
  })

  const [form, setForm] = useState<any>({})

  useEffect(() => {
    if (profile) setForm(profile)
  }, [profile])

  const updateMutation = useMutation({
    mutationFn: (data: any) => api.put('/api/profile', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      queryClient.invalidateQueries({ queryKey: ['jobScore'] })
      toast.success('Candidate Dossier updated! Career Readiness Score recalculated.')
      setEditing(false)
    },
    onError: (err: any) => toast.error(err.message || 'Dossier update failed'),
  })

  const handleSave = () => {
    const payload = {
      ...form,
      skills: form.skills || [],
      interests: form.interests || [],
      projects: form.projects || [],
      internships: form.internships || [],
      certifications: form.certifications || [],
    }
    updateMutation.mutate(payload)
  }

  const handlePicture = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      await api.post('/api/profile/picture', formData)
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      toast.success('Profile picture updated!')
    } catch {
      toast.error('Picture upload failed')
    }
  }

  const p = editing ? form : (profile || {})
  const set = (k: string, v: any) => setForm((prev: any) => ({ ...prev, [k]: v }))

  // Robust Skills Add Handler supporting single or comma-separated lists
  const addSkill = (skillInputStr?: string) => {
    const rawInput = (skillInputStr !== undefined ? skillInputStr : newSkill).trim()
    if (!rawInput) return

    const namesToAdd = rawInput
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)

    if (namesToAdd.length === 0) return

    const currentSkills = editing ? (form.skills || []) : (profile?.skills || [])
    const existingNames = new Set(
      currentSkills.map((x: any) => (typeof x === 'string' ? x : x.name).toLowerCase())
    )

    const skillObjsToAdd = namesToAdd
      .filter((name) => !existingNames.has(name.toLowerCase()))
      .map((name) => ({ name, level: newSkillLevel, verified: false }))

    if (skillObjsToAdd.length === 0) {
      toast.error('Skill(s) already exist in your dossier.')
      return
    }

    const updatedSkills = [...currentSkills, ...skillObjsToAdd]

    if (editing) {
      set('skills', updatedSkills)
      toast.success(`Added ${skillObjsToAdd.length} technical skill(s) to dossier draft.`)
    } else {
      // Direct auto-save when adding from non-editing view
      updateMutation.mutate({
        ...profile,
        skills: updatedSkills,
      })
      toast.success(`Added ${skillObjsToAdd.length} technical skill(s) and recalculated score!`)
    }

    setNewSkill('')
  }

  const removeSkill = (s: any) => {
    const targetName = typeof s === 'string' ? s : s.name
    const currentSkills = editing ? (form.skills || []) : (profile?.skills || [])
    const updatedSkills = currentSkills.filter((x: any) => {
      const xName = typeof x === 'string' ? x : x.name
      return xName.toLowerCase() !== targetName.toLowerCase()
    })

    if (editing) {
      set('skills', updatedSkills)
    } else {
      updateMutation.mutate({
        ...profile,
        skills: updatedSkills,
      })
    }
  }

  // Interests handlers
  const addInterest = () => {
    if (!newInterest.trim()) return
    const interests = [...(form.interests || []), newInterest.trim()]
    set('interests', interests)
    setNewInterest('')
  }
  const removeInterest = (i: string) => set('interests', (form.interests || []).filter((x: string) => x !== i))

  // Projects handlers
  const addProject = () => {
    if (!newProjTitle.trim()) return
    const techArray = newProjTech.split(',').map((t) => t.trim()).filter(Boolean)
    const newProj = {
      id: `proj_${Date.now()}`,
      title: newProjTitle.trim(),
      description: newProjDesc.trim(),
      technologies: techArray,
      github_url: newProjGithub.trim(),
      live_url: newProjLive.trim(),
    }
    set('projects', [...(form.projects || []), newProj])
    setNewProjTitle('')
    setNewProjDesc('')
    setNewProjTech('')
    setNewProjGithub('')
    setNewProjLive('')
  }

  const removeProject = (projId: string) => {
    set('projects', (form.projects || []).filter((p: any) => p.id !== projId && p.title !== projId))
  }

  // Experience handlers
  const addInternship = () => {
    if (!newExpCompany.trim() || !newExpRole.trim()) return
    const newExp = {
      id: `exp_${Date.now()}`,
      company: newExpCompany.trim(),
      role: newExpRole.trim(),
      duration: newExpDuration.trim(),
      description: newExpDesc.trim(),
    }
    set('internships', [...(form.internships || []), newExp])
    setNewExpCompany('')
    setNewExpRole('')
    setNewExpDuration('')
    setNewExpDesc('')
  }

  const removeInternship = (expId: string) => {
    set('internships', (form.internships || []).filter((i: any) => i.id !== expId && i.company !== expId))
  }

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-4xl animate-pulse">
        <div className="h-20 bg-subtle rounded-xl" />
        <div className="h-64 bg-subtle rounded-xl" />
      </div>
    )
  }

  const activeSkills = p.skills || []
  const activeSkillNames = new Set(
    activeSkills.map((x: any) => (typeof x === 'string' ? x : x.name).toLowerCase())
  )

  return (
    <div className="space-y-5 max-w-4xl animate-fade-in text-app">
      {/* Header */}
      <div className="card p-6 flex items-start justify-between gap-4 flex-wrap shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block mb-1">Candidate Profile & Credentials Dossier</span>
          <h2 className="font-heading text-3xl font-extrabold text-app">Candidate Dossier</h2>
          <p className="text-secondary text-xs mt-0.5 font-medium">Maintain verified academic history, portfolio projects, and technical skills for recruiter ATS matching</p>
        </div>
        {editing ? (
          <div className="flex gap-2">
            <button onClick={() => { setEditing(false); setForm(profile) }} className="btn btn-secondary text-xs">Cancel</button>
            <button onClick={handleSave} disabled={updateMutation.isPending} className="btn btn-primary text-xs gap-2">
              {updateMutation.isPending && <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />}
              <Save className="w-4 h-4" />
              Save Dossier
            </button>
          </div>
        ) : (
          <button onClick={() => setEditing(true)} className="btn btn-primary text-xs gap-2">
            <Edit3 className="w-4 h-4" /> Edit Dossier
          </button>
        )}
      </div>

      {/* Target Role Target Selection */}
      <Section title="Target Career Requisition" icon={Target}>
        <div>
          <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1 block">Primary Target Role Benchmark</label>
          <select
            className="input text-xs"
            disabled={!editing}
            value={p.target_career || 'Full-Stack Engineer'}
            onChange={(e) => set('target_career', e.target.value)}
          >
            <option value="Full-Stack Engineer">Full-Stack Engineer</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Engineer">Backend Engineer</option>
            <option value="AI / Machine Learning Engineer">AI / Machine Learning Engineer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="Data Engineer">Data Engineer</option>
            <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer</option>
            <option value="Mobile App Developer">Mobile App Developer</option>
            <option value="Cybersecurity Analyst">Cybersecurity Analyst</option>
          </select>
        </div>
      </Section>

      {/* Personal Info */}
      <Section title="Personal Identification & Academic Standing" icon={User}>
        <div className="flex items-start gap-6 flex-wrap">
          {/* Avatar */}
          <div className="relative flex-shrink-0">
            <div className="w-20 h-20 overflow-hidden bg-subtle rounded-xl border border-app">
              {profile?.profile_picture_url ? (
                <img src={profile.profile_picture_url} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-[#1a1f3a] dark:bg-[#141936] flex items-center justify-center text-white text-2xl font-bold font-heading">
                  {user?.displayName?.[0]?.toUpperCase() || 'C'}
                </div>
              )}
            </div>
            <label className="absolute -bottom-1 -right-1 w-7 h-7 bg-[#FF5722] hover:bg-[#E64A19] flex items-center justify-center cursor-pointer transition-colors rounded-md">
              <Camera className="w-3.5 h-3.5 text-white" />
              <input type="file" accept="image/*" className="hidden" onChange={handlePicture} />
            </label>
          </div>

          {/* Fields */}
          <div className="flex-1 grid sm:grid-cols-2 gap-4 min-w-0">
            {[
              { key: 'name', label: 'Full Legal Name', type: 'text' },
              { key: 'email', label: 'Registered Email', type: 'email' },
              { key: 'college', label: 'Academic Institution', type: 'text' },
              { key: 'degree', label: 'Degree Program', type: 'text', placeholder: 'B.Tech, B.S., M.S...' },
              { key: 'department', label: 'Department / Major', type: 'text', placeholder: 'Computer Science...' },
              { key: 'current_year', label: 'Academic Year', type: 'number' },
              { key: 'cgpa', label: 'Cumulative GPA (Scale 10)', type: 'number', step: '0.01', min: '0', max: '10' },
            ].map(({ key, label, type, placeholder, step, min, max }) => (
              <div key={key}>
                <label className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1 block">{label}</label>
                <input
                  type={type}
                  className="input text-xs"
                  placeholder={placeholder}
                  value={p[key] ?? ''}
                  disabled={!editing}
                  step={step}
                  min={min}
                  max={max}
                  onChange={(e) => set(key, type === 'number' ? (parseFloat(e.target.value) || 0) : e.target.value)}
                />
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* Links */}
      <Section title="Professional Links & Code Repositories" icon={Globe}>
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { key: 'github_url', label: 'GitHub Profile', icon: Code, placeholder: 'https://github.com/username' },
            { key: 'linkedin_url', label: 'LinkedIn Profile', icon: LinkIcon, placeholder: 'https://linkedin.com/in/...' },
            { key: 'portfolio_url', label: 'Personal Portfolio', icon: Globe, placeholder: 'https://yoursite.com' },
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

      {/* Verified Technical Skills — Dynamic Input Panel & Quick Add Chips */}
      <Section title="Verified Technical Skills" icon={Code}>
        <div className="space-y-4">
          {/* Current Skills List */}
          <div className="flex flex-wrap gap-2">
            {activeSkills.length === 0 && (
              <p className="text-secondary text-xs font-medium italic">No technical skills documented yet. Use the panel below to add technical skills.</p>
            )}
            {activeSkills.map((skill: any, idx: number) => {
              const skillKey = typeof skill === 'string' ? skill : `${skill.name}-${idx}`
              return (
                <SkillBadge
                  key={skillKey}
                  skill={skill}
                  onRemove={() => removeSkill(skill)}
                />
              )
            })}
          </div>

          {/* Quick-Add Popular Tech Stack Chips */}
          <div className="p-3 bg-subtle border border-app rounded-xl space-y-2">
            <span className="text-[10px] font-extrabold text-secondary uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#FF5722]" /> 1-Click Quick Add Tech Stack Chips:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {POPULAR_TECH_CHIPS.map((chip) => {
                const isAdded = activeSkillNames.has(chip.toLowerCase())
                return (
                  <button
                    key={chip}
                    onClick={() => !isAdded && addSkill(chip)}
                    disabled={isAdded}
                    className={`px-2.5 py-1 rounded text-xs font-bold transition-all flex items-center gap-1 ${
                      isAdded
                        ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 opacity-60 cursor-default'
                        : 'bg-card border border-app text-app hover:border-[#FF5722] hover:text-[#FF5722] shadow-2xs'
                    }`}
                  >
                    {isAdded ? '✓' : '+'} {chip}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Dynamic Various Technical Skills Input Control */}
          <div className="p-4 border border-app rounded-xl bg-surface space-y-2.5">
            <label className="text-xs font-bold text-app block">
              Add Custom Various Technical Skills
              <span className="text-[11px] text-secondary font-medium block mt-0.5">
                Type single or comma-separated skills (e.g. <code>React, TypeScript, Python, FastAPI, Docker, SQL</code>)
              </span>
            </label>
            <div className="flex gap-2 flex-wrap sm:flex-nowrap">
              <input
                className="input flex-1 text-xs"
                placeholder="Enter technical skill names (comma separated supported)..."
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addSkill()}
              />
              <select
                className="input text-xs w-36 shrink-0"
                value={newSkillLevel}
                onChange={(e) => setNewSkillLevel(e.target.value)}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="Expert">Expert</option>
              </select>
              <button
                onClick={() => addSkill()}
                className="btn btn-primary px-4 text-xs font-bold shrink-0 gap-1.5 py-2"
              >
                <Plus className="w-4 h-4 text-white" /> Add Skill(s)
              </button>
            </div>
          </div>
        </div>
      </Section>

      {/* Practical Projects */}
      <Section title="Practical Portfolio Projects" icon={FolderGit2}>
        <div className="space-y-3">
          {(p.projects || []).length === 0 && (
            <p className="text-secondary text-xs font-medium">No portfolio projects documented yet. Add practical projects to boost your readiness score.</p>
          )}
          {(p.projects || []).map((proj: any, idx: number) => (
            <div key={proj.id || idx} className="p-3.5 bg-subtle border border-app rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-sm text-app">{proj.title}</h4>
                {editing && (
                  <button onClick={() => removeProject(proj.id || proj.title)} className="text-red-500 hover:text-red-700 text-xs font-bold flex items-center gap-1">
                    <X className="w-3.5 h-3.5" /> Remove
                  </button>
                )}
              </div>
              {proj.description && <p className="text-xs text-secondary font-medium">{proj.description}</p>}
              {proj.technologies && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {(Array.isArray(proj.technologies) ? proj.technologies : String(proj.technologies).split(',')).map((t: string) => (
                    <span key={t} className="px-2 py-0.5 text-[10px] font-bold bg-app text-secondary border border-app rounded">
                      {t.trim()}
                    </span>
                  ))}
                </div>
              )}
              <div className="flex gap-4 text-xs pt-1">
                {proj.github_url && <a href={proj.github_url} target="_blank" rel="noreferrer" className="text-[#FF5722] hover:underline font-semibold flex items-center gap-1"><Code className="w-3 h-3" /> GitHub Repo</a>}
                {proj.live_url && <a href={proj.live_url} target="_blank" rel="noreferrer" className="text-emerald-500 hover:underline font-semibold flex items-center gap-1"><Globe className="w-3 h-3" /> Live Demo</a>}
              </div>
            </div>
          ))}

          {editing && (
            <div className="p-4 border border-dashed border-app rounded-xl space-y-3 bg-card mt-2">
              <h5 className="text-xs font-bold text-app flex items-center gap-1.5"><Plus className="w-3.5 h-3.5 text-[#FF5722]" /> Add New Portfolio Project</h5>
              <div className="grid sm:grid-cols-2 gap-3">
                <input className="input text-xs" placeholder="Project Title" value={newProjTitle} onChange={(e) => setNewProjTitle(e.target.value)} />
                <input className="input text-xs" placeholder="Tech Stack (comma separated, e.g. React, FastAPI, Docker)" value={newProjTech} onChange={(e) => setNewProjTech(e.target.value)} />
                <input className="input text-xs sm:col-span-2" placeholder="Brief Description / Impact Metrics" value={newProjDesc} onChange={(e) => setNewProjDesc(e.target.value)} />
                <input className="input text-xs" placeholder="GitHub URL" value={newProjGithub} onChange={(e) => setNewProjGithub(e.target.value)} />
                <input className="input text-xs" placeholder="Live Demo URL" value={newProjLive} onChange={(e) => setNewProjLive(e.target.value)} />
              </div>
              <button onClick={addProject} className="btn btn-primary text-xs w-full justify-center gap-1 py-2">
                <Plus className="w-4 h-4" /> Save Project to Dossier
              </button>
            </div>
          )}
        </div>
      </Section>

      {/* Work Experience & Internships */}
      <Section title="Work Experience & Internships" icon={Briefcase}>
        <div className="space-y-3">
          {(p.internships || []).length === 0 && (
            <p className="text-secondary text-xs font-medium">No internships or work experience documented yet.</p>
          )}
          {(p.internships || []).map((exp: any, idx: number) => (
            <div key={exp.id || idx} className="p-3.5 bg-subtle border border-app rounded-xl space-y-1.5">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-sm text-app">{exp.role} <span className="text-secondary font-normal">at {exp.company}</span></h4>
                {editing && (
                  <button onClick={() => removeInternship(exp.id || exp.company)} className="text-red-500 hover:text-red-700 text-xs font-bold flex items-center gap-1">
                    <X className="w-3.5 h-3.5" /> Remove
                  </button>
                )}
              </div>
              {exp.duration && <p className="text-[11px] font-semibold text-secondary">{exp.duration}</p>}
              {exp.description && <p className="text-xs text-secondary font-medium mt-1">{exp.description}</p>}
            </div>
          ))}

          {editing && (
            <div className="p-4 border border-dashed border-app rounded-xl space-y-3 bg-card mt-2">
              <h5 className="text-xs font-bold text-app flex items-center gap-1.5"><Plus className="w-3.5 h-3.5 text-[#FF5722]" /> Add Work Experience / Internship</h5>
              <div className="grid sm:grid-cols-2 gap-3">
                <input className="input text-xs" placeholder="Company / Organization" value={newExpCompany} onChange={(e) => setNewExpCompany(e.target.value)} />
                <input className="input text-xs" placeholder="Role / Position" value={newExpRole} onChange={(e) => setNewExpRole(e.target.value)} />
                <input className="input text-xs sm:col-span-2" placeholder="Duration (e.g. June 2025 - August 2025)" value={newExpDuration} onChange={(e) => setNewExpDuration(e.target.value)} />
                <input className="input text-xs sm:col-span-2" placeholder="Responsibilities & Key Achievements" value={newExpDesc} onChange={(e) => setNewExpDesc(e.target.value)} />
              </div>
              <button onClick={addInternship} className="btn btn-primary text-xs w-full justify-center gap-1 py-2">
                <Plus className="w-4 h-4" /> Save Experience to Dossier
              </button>
            </div>
          )}
        </div>
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

      {/* Profile completion & Action Checklist */}
      {profile?.profile_completion && (
        <div className="card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h4 className="font-heading text-lg font-bold text-app">Candidate Dossier Completeness</h4>
              <p className="text-xs text-secondary font-medium">Complete required credential fields to achieve 100% profile score verification</p>
            </div>
            <span className="font-heading text-2xl font-extrabold text-[#FF5722] dark:text-[#FF7043]">
              {profile.profile_completion.percentage}%
            </span>
          </div>
          <div className="w-full h-2.5 bg-subtle border border-app overflow-hidden rounded-full">
            <div className="h-full bg-[#FF5722] transition-all rounded-full" style={{ width: `${profile.profile_completion.percentage}%` }} />
          </div>

          {profile.profile_completion.missing_fields?.length > 0 && (
            <div className="pt-2 border-t border-app space-y-2">
              <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Missing Requisition Items ({profile.profile_completion.missing_fields.length}):</span>
              <div className="grid sm:grid-cols-2 gap-2 text-xs">
                {profile.profile_completion.missing_fields.map((field: string) => (
                  <div key={field} className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400 font-medium">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    <span>{field}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
