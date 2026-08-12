import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { Target, ExternalLink, CheckCircle, Circle, Clock } from 'lucide-react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'

const STATUS_CONFIG = {
  completed:   { icon: CheckCircle, color: 'text-teal-700 dark:text-teal-400', bg: 'bg-teal-50/50',  label: 'Completed' },
  in_progress: { icon: Clock,       color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50/50', label: 'In Progress' },
  not_started: { icon: Circle,      color: 'text-secondary',  bg: 'bg-subtle', label: 'Not Started' },
}

function LearningItem({ item, onStatusChange }: any) {
  const cfg = STATUS_CONFIG[item.status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.not_started
  const Icon = cfg.icon

  const nextStatus = {
    not_started: 'in_progress',
    in_progress: 'completed',
    completed:   'not_started',
  }[item.status as string] || 'in_progress'

  return (
    <div className={`p-4 border rounded-xl transition-all ${
      item.status === 'completed' ? 'border-app bg-subtle opacity-90' :
      item.status === 'in_progress' ? 'border-teal-700/40 bg-surface shadow-xs' :
      'border-app bg-surface'
    }`}>
      <div className="flex items-start gap-3">
        <button
          onClick={() => onStatusChange(item.id, nextStatus)}
          className={`mt-0.5 flex-shrink-0 ${cfg.color} hover:scale-110 transition-transform`}
          title={`Mark as ${nextStatus.replace('_', ' ')}`}
        >
          <Icon className="w-4 h-4" />
        </button>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className={`text-xs font-bold ${item.status === 'completed' ? 'line-through text-muted' : 'text-app'}`}>
              {item.title}
            </p>
            <span className={`badge flex-shrink-0 ${
              item.difficulty === 'hard' ? 'badge-red' :
              item.difficulty === 'medium' ? 'badge-amber' : 'badge-sand'
            }`}>{item.difficulty}</span>
          </div>

          {item.skill && <p className="text-[11px] font-medium text-secondary mt-0.5">Focus Skill: {item.skill}</p>}
          {item.platform && <p className="text-[11px] font-semibold text-secondary">Curriculum Provider: {item.platform}</p>}

          {item.resource_url && (
            <a
              href={item.resource_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-[11px] text-teal-700 dark:text-teal-400 font-extrabold hover:underline mt-2"
            >
              <ExternalLink className="w-3 h-3" /> Access Resource
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

export default function LearningPage() {
  const queryClient = useQueryClient()

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/api/profile').then(r => r.data),
  })

  const { data: roadmap, isLoading } = useQuery({
    queryKey: ['learning'],
    queryFn: () => api.get('/api/learning').then(r => r.data),
    enabled: !!profile?.target_career,
  })

  const statusMutation = useMutation({
    mutationFn: ({ itemId, status }: { itemId: string; status: string }) =>
      api.put(`/api/learning/item/${itemId}/status`, { status }),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['learning'] })
      if (res.data.progress_percentage !== undefined) {
        queryClient.invalidateQueries({ queryKey: ['jobScore'] })
      }
    },
    onError: () => toast.error('Failed to update status'),
  })

  const STAGE_NAMES: Record<string, string> = {
    '1': 'Stage I: Core Fundamentals',
    '2': 'Stage II: Applied Competencies',
    '3': 'Stage III: Advanced Specialization',
    '4': 'Stage IV: Portfolio Architecture',
    '5': 'Stage V: Executive Interview Preparation',
  }

  if (!profile?.target_career) {
    return (
      <div className="max-w-xl space-y-4 animate-fade-in text-app">
        <div className="card p-6 shadow-xs">
          <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-1">Curriculum Engine</span>
          <h2 className="font-heading text-3xl font-extrabold text-app">Curriculum Learning Roadmap</h2>
        </div>
        <div className="card p-10 text-center">
          <Target className="w-10 h-10 text-secondary mx-auto mb-3" />
          <h3 className="font-heading text-xl font-bold text-app">No Target Track Selected</h3>
          <p className="text-xs text-secondary mt-1 mb-4 font-medium">Select a target career track to generate your personalized learning curriculum</p>
          <Link to="/career/tracks" className="btn btn-primary text-xs">Choose Career Track</Link>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-2xl">
        {[...Array(3)].map((_, i) => <div key={i} className="card p-5 h-48 skeleton" />)}
      </div>
    )
  }

  const stages = roadmap?.stages || {}
  const progress = roadmap?.progress_percentage || 0
  const completed = roadmap?.completed_items || 0
  const total = roadmap?.total_items || 0

  return (
    <div className="space-y-5 max-w-2xl animate-fade-in text-app">
      <div className="card p-6 shadow-xs">
        <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-1">Curriculum Milestone Tracker</span>
        <h2 className="font-heading text-3xl font-extrabold text-app">Curriculum Learning Roadmap</h2>
        <p className="text-secondary text-xs mt-0.5 font-medium">Sequential learning progression targeted for your selected career track</p>
      </div>

      {/* Progress */}
      <div className="card p-5 space-y-2">
        <div className="flex justify-between text-xs font-bold">
          <span className="text-app">Roadmap Completion</span>
          <span className="text-teal-700 dark:text-teal-400">{completed}/{total} Modules ({progress}%)</span>
        </div>
        <div className="w-full h-2.5 bg-subtle border border-app overflow-hidden rounded-full">
          <div className="h-full bg-teal-700 dark:bg-teal-500 transition-all rounded-full" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Stages */}
      {Object.keys(stages).sort().map((stageNum) => (
        <div key={stageNum} className="card p-5 space-y-3">
          <h3 className="font-heading text-lg font-bold text-app border-b border-app pb-2">
            {STAGE_NAMES[stageNum] || `Stage ${stageNum}`}
          </h3>
          <div className="space-y-2">
            {(stages[stageNum] || []).map((item: any) => (
              <LearningItem
                key={item.id}
                item={item}
                onStatusChange={(itemId: string, status: string) =>
                  statusMutation.mutate({ itemId, status })
                }
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
