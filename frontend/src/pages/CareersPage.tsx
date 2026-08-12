import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  Briefcase, Target, RefreshCw,
  CheckCircle, AlertCircle, ChevronDown, ChevronUp
} from 'lucide-react'
import toast from 'react-hot-toast'

function MatchBar({ pct }: { pct: number }) {
  const color = pct >= 70 ? 'bg-teal-700 dark:bg-teal-500' : pct >= 40 ? 'bg-amber-600' : 'bg-red-600'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-subtle border border-app overflow-hidden rounded-full">
        <div className={`h-full ${color} transition-all rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono font-bold text-app w-10 text-right">{pct}%</span>
    </div>
  )
}

function CareerCard({ career, isTarget, onSelect }: any) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={`card p-5 transition-all ${isTarget ? 'border-2 border-teal-700 dark:border-teal-500 shadow-xs' : ''}`}>
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 bg-teal-50 text-teal-900 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 flex items-center justify-center flex-shrink-0 rounded-md">
          <Briefcase className="w-5 h-5 text-teal-700 dark:text-teal-400" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2 justify-between flex-wrap mb-2">
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-heading text-xl font-bold text-app">{career.title}</h3>
                {isTarget && <span className="badge badge-emerald">Active Target</span>}
                {career.market_demand && (
                  <span className="badge badge-editorial">{career.market_demand} Demand</span>
                )}
              </div>
              {career.salary_range && (
                <p className="text-xs font-mono font-bold text-teal-700 dark:text-teal-400 mt-0.5">Salary Benchmark: {career.salary_range}</p>
              )}
            </div>
          </div>

          <MatchBar pct={career.match_percentage} />

          {career.reason && (
            <p className="text-xs text-secondary font-medium mt-3 leading-relaxed">{career.reason}</p>
          )}

          {/* Matching skills */}
          {career.matching_skills?.length > 0 && (
            <div className="mt-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-1.5 flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5 text-teal-700 dark:text-teal-400" /> Verified Matching Skills
              </p>
              <div className="flex flex-wrap gap-1.5">
                {career.matching_skills.slice(0, 6).map((s: string) => (
                  <span key={s} className="px-2.5 py-0.5 text-[11px] font-bold bg-teal-50 text-teal-900 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-800 rounded">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Expanded: missing skills */}
          {expanded && career.missing_skills?.length > 0 && (
            <div className="mt-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-red-700 dark:text-red-400 mb-1.5 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 text-red-600 dark:text-red-400" /> Priority Skills to Master
              </p>
              <div className="flex flex-wrap gap-1.5">
                {career.missing_skills.slice(0, 10).map((s: string) => (
                  <span key={s} className="px-2 py-0.5 text-[11px] font-bold bg-red-50 text-red-900 border border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800 rounded">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 mt-4">
            <button
              onClick={() => onSelect(career.title)}
              className={isTarget ? 'btn btn-secondary text-xs' : 'btn btn-primary text-xs'}
            >
              <Target className="w-3.5 h-3.5" />
              {isTarget ? 'Currently Selected' : 'Set as Target Track'}
            </button>
            <button
              onClick={() => setExpanded(!expanded)}
              className="btn btn-ghost text-xs gap-1"
            >
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              {expanded ? 'Less' : 'More details'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CareersPage() {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['careers'],
    queryFn: () => api.get('/api/careers/recommendations').then(r => r.data),
  })

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/api/profile').then(r => r.data),
  })

  const refreshMutation = useMutation({
    mutationFn: () => api.post('/api/careers/recommendations/refresh'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['careers'] })
      toast.success('Recommendations refreshed!')
    },
    onError: (err: any) => toast.error(err.message),
  })

  const selectMutation = useMutation({
    mutationFn: (title: string) => api.post('/api/careers/target', { career_title: title }),
    onSuccess: (_, title) => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      toast.success(`${title} set as your target career track!`)
    },
  })

  const targetCareer = profile?.target_career || ''
  const recommendations = data?.recommendations || []

  return (
    <div className="space-y-6 max-w-3xl animate-fade-in text-app">
      {/* Header */}
      <div className="card p-6 flex items-start justify-between gap-4 flex-wrap shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-1">Market Track Matching</span>
          <h2 className="font-heading text-3xl font-extrabold text-app">Market Career Tracks</h2>
          <p className="text-secondary text-xs mt-0.5 font-medium">Algorithmic track matching based on verified skill profile and employability requisitions</p>
        </div>
        <button
          onClick={() => refreshMutation.mutate()}
          disabled={refreshMutation.isPending}
          className="btn btn-secondary text-xs gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
          Re-Analyze Tracks
        </button>
      </div>

      {/* Target Status Callout */}
      {targetCareer && (
        <div className="card p-4 bg-teal-50/40 dark:bg-teal-950/20 border-teal-200 dark:border-teal-900 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-teal-700 dark:text-teal-400 flex-shrink-0" />
            <span className="font-bold text-app">Active Target Career Track: <strong className="text-teal-700 dark:text-teal-400 font-bold">{targetCareer}</strong></span>
          </div>
        </div>
      )}

      {/* Career Recommendations List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="card p-5 h-48 skeleton" />)}
        </div>
      ) : error ? (
        <div className="card p-6 text-center text-red-600 text-xs font-bold">
          Failed to load career recommendations.
        </div>
      ) : recommendations.length === 0 ? (
        <div className="card p-10 text-center">
          <Briefcase className="w-10 h-10 text-secondary mx-auto mb-3" />
          <h3 className="font-heading text-xl font-bold text-app">No Recommendations Available</h3>
          <p className="text-xs text-secondary mt-1 font-medium">Add technical skills to your profile to generate custom market career track matches.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((career: any, idx: number) => (
            <CareerCard
              key={idx}
              career={career}
              isTarget={targetCareer.toLowerCase() === career.title.toLowerCase()}
              onSelect={(title: string) => selectMutation.mutate(title)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
