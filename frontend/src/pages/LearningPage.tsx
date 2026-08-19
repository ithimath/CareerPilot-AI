import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  Target, ExternalLink, CheckCircle2, Circle, Clock,
  BookOpen, ChevronDown, ChevronUp, Info, Compass, Award
} from 'lucide-react'
import toast from 'react-hot-toast'

const STATUS_CONFIG = {
  completed:   { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10', label: 'Completed' },
  in_progress: { icon: Clock,       color: 'text-amber-500',   bg: 'bg-amber-500/10',   label: 'In Progress' },
  not_started: { icon: Circle,      color: 'text-secondary',   bg: 'bg-subtle',         label: 'Not Started' },
}

function CourseCard({ course }: { course: any }) {
  const hasUrl = Boolean(course.url && course.url !== '#')

  return (
    <div className="p-4 bg-subtle border border-app rounded-xl space-y-2.5">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <span className="text-[10px] font-extrabold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block">
            {course.platform || 'Official Resource'} • {course.duration || 'Flexible'}
          </span>
          <h5 className="font-heading text-sm font-bold text-app mt-0.5">{course.title}</h5>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="badge badge-subtle text-[10px]">
            {course.level || course.difficulty || 'Intermediate'}
          </span>
          {hasUrl ? (
            <a
              href={course.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary text-xs py-1 px-3 inline-flex items-center gap-1.5 font-extrabold shadow-xs hover:scale-105 transition-transform"
            >
              <ExternalLink className="w-3.5 h-3.5" /> Learn Now →
            </a>
          ) : (
            <span className="text-xs font-semibold text-secondary italic">Resource Unavailable</span>
          )}
        </div>
      </div>

      {course.relevance_reason && (
        <div className="flex items-start gap-1.5 p-2.5 bg-card border border-app rounded-md text-xs text-secondary font-medium">
          <Info className="w-3.5 h-3.5 text-[#FF5722] dark:text-[#FF7043] shrink-0 mt-0.5" />
          <span><strong>Role Alignment:</strong> {course.relevance_reason}</span>
        </div>
      )}
    </div>
  )
}

function ModuleCard({ item, onStatusChange }: any) {
  const [expanded, setExpanded] = useState(true)
  const cfg = STATUS_CONFIG[item.status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.not_started
  const Icon = cfg.icon

  const nextStatus = {
    not_started: 'in_progress',
    in_progress: 'completed',
    completed:   'not_started',
  }[item.status as string] || 'in_progress'

  const courses = item.courses || []
  const primaryUrl = item.resource_url && item.resource_url !== '#' ? item.resource_url : courses[0]?.url

  return (
    <div className={`p-4 border rounded-xl transition-all space-y-3 ${
      item.status === 'completed' ? 'border-emerald-500/30 bg-emerald-500/5' :
      item.status === 'in_progress' ? 'border-amber-500/30 bg-amber-500/5' :
      'border-app bg-surface'
    }`}>
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="flex items-start gap-3 flex-1 min-w-[240px]">
          <button
            onClick={() => onStatusChange(item.id, nextStatus)}
            className={`mt-0.5 shrink-0 ${cfg.color} hover:scale-110 transition-transform`}
            title={`Click to mark as ${nextStatus.replace('_', ' ')}`}
          >
            <Icon className="w-5 h-5" />
          </button>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className={`font-heading text-sm font-bold ${item.status === 'completed' ? 'line-through text-muted' : 'text-app'}`}>
                {item.title}
              </h4>
              <span className={`badge ${
                item.difficulty === 'hard' || item.difficulty === 'advanced' ? 'badge-red' :
                item.difficulty === 'medium' || item.difficulty === 'intermediate' ? 'badge-amber' : 'badge-emerald'
              }`}>
                {item.difficulty}
              </span>
            </div>
            {item.description && <p className="text-xs text-secondary font-medium mt-1">{item.description}</p>}
            <div className="flex items-center gap-3 text-[11px] text-secondary font-semibold mt-1.5">
              <span>Focus Skill: <strong className="text-app">{item.skill}</strong></span>
              <span>•</span>
              <span>Provider: <strong className="text-app">{item.platform}</strong></span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {primaryUrl && primaryUrl !== '#' && (
            <a
              href={primaryUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary text-xs py-1.5 px-3 inline-flex items-center gap-1.5 font-bold shadow-xs hover:scale-105 transition-transform"
            >
              <ExternalLink className="w-3.5 h-3.5" /> Start Learning Module →
            </a>
          )}
          <button
            onClick={() => onStatusChange(item.id, nextStatus)}
            className={`px-2.5 py-1.5 rounded-md text-[11px] font-extrabold transition-colors ${
              item.status === 'completed' ? 'bg-emerald-500 text-white' :
              item.status === 'in_progress' ? 'bg-amber-500 text-white' : 'bg-subtle text-app border border-app hover:border-[#FF5722]'
            }`}
          >
            {cfg.label}
          </button>
          {courses.length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1.5 hover:bg-subtle rounded text-secondary"
              title="Toggle Course Recommendations"
            >
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
        </div>
      </div>

      {/* Courses Accordion */}
      {expanded && courses.length > 0 && (
        <div className="pt-3 border-t border-app space-y-2">
          <span className="text-[10px] font-bold text-secondary uppercase tracking-wider block">
            Recommended Official Courses & Resources ({courses.length})
          </span>
          <div className="grid gap-2">
            {courses.map((course: any, idx: number) => (
              <CourseCard key={course.id || idx} course={course} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function LearningPage() {
  const queryClient = useQueryClient()
  const [selectedRole, setSelectedRole] = useState('')

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/api/profile').then((r) => r.data),
  })

  const currentRole = selectedRole || profile?.target_career || 'Full-Stack Engineer'

  const { data: roadmap, isLoading, isError } = useQuery({
    queryKey: ['learning', currentRole],
    queryFn: () => api.get(`/api/learning?target_career=${encodeURIComponent(currentRole)}`).then((r) => r.data),
  })

  const statusMutation = useMutation({
    mutationFn: ({ itemId, status }: { itemId: string; status: string }) =>
      api.put(`/api/learning/item/${itemId}/status`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning'] })
      // exact:false ensures Dashboard's ['jobScore', uid] key is also invalidated
      queryClient.invalidateQueries({ queryKey: ['jobScore'], exact: false })
      toast.success('Module status updated! Career Readiness Score recalculated.')
    },
    onError: () => toast.error('Failed to update module status'),
  })

  const STAGE_NAMES: Record<string, string> = {
    '1': 'Module 1 — Core Fundamentals',
    '2': 'Module 2 — Applied Stack Architecture',
    '3': 'Module 3 — Advanced Specialization',
    '4': 'Module 4 — Portfolio Projects',
    '5': 'Module 5 — Executive Interview Preparation',
  }

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-3xl animate-pulse">
        <div className="h-20 bg-subtle rounded-xl" />
        <div className="h-48 bg-subtle rounded-xl" />
        <div className="h-48 bg-subtle rounded-xl" />
      </div>
    )
  }

  const stages = roadmap?.stages || {}
  const progress = roadmap?.progress_percentage || 0
  const completed = roadmap?.completed_items || 0
  const total = roadmap?.total_items || 0
  const domain = roadmap?.domain || 'Software Systems & Architecture'

  return (
    <div className="space-y-5 max-w-3xl animate-fade-in text-app">
      {/* Header */}
      <div className="card p-6 shadow-xs flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-emerald flex items-center gap-1 text-[10px]">
              <Compass className="w-3 h-3 text-emerald-500" /> Domain: {domain}
            </span>
          </div>
          <h2 className="font-heading text-3xl font-extrabold text-app">{currentRole} Roadmap</h2>
          <p className="text-secondary text-xs mt-0.5 font-medium">Domain-matched, skill-gap driven curriculum for {currentRole} requisitions</p>
        </div>

        {/* Role Switcher */}
        <div className="shrink-0">
          <label className="text-[10px] font-bold text-secondary uppercase tracking-wider block mb-1">Switch Career Track</label>
          <select
            className="input text-xs w-48"
            value={currentRole}
            onChange={(e) => setSelectedRole(e.target.value)}
          >
            <option value="Full-Stack Engineer">Full-Stack Engineer</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Engineer">Backend Engineer</option>
            <option value="AI / Machine Learning Engineer">AI / Machine Learning Engineer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer</option>
            <option value="Mobile App Developer">Mobile App Developer</option>
            <option value="Cybersecurity Analyst">Cybersecurity Analyst</option>
          </select>
        </div>
      </div>

      {/* Progress Milestone Widget */}
      <div className="card p-5 space-y-3">
        <div className="flex justify-between items-center text-xs font-bold">
          <span className="text-app flex items-center gap-1.5">
            <Award className="w-4 h-4 text-[#FF5722]" /> Roadmap Completion Status
          </span>
          <span className="text-[#FF5722] dark:text-[#FF7043] font-extrabold">
            {completed}/{total} Modules Completed ({progress}%)
          </span>
        </div>
        <div className="w-full h-3 bg-subtle border border-app overflow-hidden rounded-full">
          <div className="h-full bg-[#FF5722] transition-all rounded-full" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Stages / Modules Accordion List */}
      {Object.keys(stages).sort().map((stageNum) => {
        const moduleItems = stages[stageNum] || []
        if (moduleItems.length === 0) return null

        return (
          <div key={stageNum} className="card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-app pb-2.5">
              <h3 className="font-heading text-lg font-bold text-app flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-[#FF5722]" />
                {STAGE_NAMES[stageNum] || `Module ${stageNum}`}
              </h3>
              <span className="text-[11px] font-semibold text-secondary">
                {moduleItems.filter((i: any) => i.status === 'completed').length}/{moduleItems.length} Completed
              </span>
            </div>

            <div className="space-y-3">
              {moduleItems.map((item: any) => (
                <ModuleCard
                  key={item.id}
                  item={item}
                  onStatusChange={(itemId: string, status: string) =>
                    statusMutation.mutate({ itemId, status })
                  }
                />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
