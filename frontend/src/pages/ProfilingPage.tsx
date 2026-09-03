import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import api from '@/lib/api'
import {
  RefreshCw, Brain, Zap, ChevronRight, Info,
  Database, GitBranch, Target, Users, Award
} from 'lucide-react'
import toast from 'react-hot-toast'

// ── Types ─────────────────────────────────────────────────────────────────────
interface ClusterResult {
  cluster_available: boolean
  cluster_id?: number
  archetype_id?: string
  archetype_name?: string
  archetype_icon?: string
  archetype_color?: string
  description?: string
  career_fit?: string[]
  prediction_method?: string
  prediction_label?: string
  note?: string
  message?: string
}

interface MLStatus {
  ml_engine_version: string
  models: {
    readiness_rf:      { status: string; trained_at?: string; metrics?: Record<string, number> }
    career_rf:         { status: string; trained_at?: string; metrics?: Record<string, number> }
    kmeans_clustering: { status: string; trained_at?: string; metrics?: Record<string, number> }
  }
}

// ── How It Works steps ────────────────────────────────────────────────────────
const HOW_IT_WORKS_STEPS = [
  {
    step: '1',
    icon: Database,
    title: 'Feature Extraction',
    desc: 'Your skills, course, academic year, and project data are converted into a structured numerical feature vector.',
  },
  {
    step: '2',
    icon: GitBranch,
    title: 'K-Means Clustering',
    desc: 'K-Means groups students with similar feature vectors into clusters. Your cluster is determined by nearest centroid distance.',
  },
  {
    step: '3',
    icon: Brain,
    title: 'Archetype Assignment',
    desc: 'Each cluster centroid is analyzed for its dominant skill signals and mapped to a human-readable career archetype.',
  },
  {
    step: '4',
    icon: Target,
    title: 'Career Alignment',
    desc: 'Your archetype\'s career alignment reflects the most common career goals within your cluster of similar students.',
  },
]

// ── ML Engine Badge ───────────────────────────────────────────────────────────
function EngineMethodBadge({ method, label }: { method?: string; label?: string }) {
  const methodColors: Record<string, string> = {
    kmeans_clustering:           'bg-violet-500/10 text-violet-700 border-violet-500/30 dark:text-violet-300',
    random_forest_regression:    'bg-emerald-500/10 text-emerald-700 border-emerald-500/30 dark:text-emerald-300',
    random_forest_classification:'bg-blue-500/10 text-blue-700 border-blue-500/30 dark:text-blue-300',
    rule_based_career_mapping:   'bg-amber-500/10 text-amber-700 border-amber-500/30 dark:text-amber-300',
    tfidf_semantic:              'bg-cyan-500/10 text-cyan-700 border-cyan-500/30 dark:text-cyan-300',
  }

  const colorClass = method ? (methodColors[method] || 'bg-slate-500/10 text-slate-700 border-slate-500/30') : 'bg-slate-500/10 text-slate-700 border-slate-500/30'

  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full border ${colorClass}`}>
      <Zap className="w-2.5 h-2.5" />
      {label || method || 'Unknown'}
    </span>
  )
}

// ── Archetype Card ────────────────────────────────────────────────────────────
function ArchetypeCard({ cluster }: { cluster: ClusterResult }) {
  if (!cluster.cluster_available || !cluster.archetype_name) {
    return (
      <div className="card p-8 text-center">
        <Brain className="w-12 h-12 text-muted mx-auto mb-4" />
        <h3 className="font-heading text-lg font-bold text-app mb-2">Profile Not Yet Available</h3>
        <p className="text-sm text-secondary leading-relaxed">
          {cluster.message || 'The student profiling model needs to be trained first.'}
        </p>
        <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-700/50 rounded-md">
          <p className="text-xs text-amber-800 dark:text-amber-300 font-medium">
            An administrator can train the ML models by calling <code className="font-mono bg-amber-100 dark:bg-amber-900/50 px-1.5 py-0.5 rounded">POST /api/ml/train</code>
          </p>
        </div>
      </div>
    )
  }

  const icon = cluster.archetype_icon || '🎯'
  const color = cluster.archetype_color || '#8B5CF6'

  return (
    <div className="card overflow-hidden">
      {/* Header gradient bar */}
      <div className="h-1.5 w-full" style={{ background: `linear-gradient(90deg, ${color}90, ${color}20)` }} />

      <div className="p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row items-start gap-4 sm:gap-5">
          {/* Icon */}
          <div
            className="w-14 h-14 sm:w-16 sm:h-16 flex-shrink-0 flex items-center justify-center text-2xl sm:text-3xl rounded-xl border-2"
            style={{
              background: `${color}15`,
              borderColor: `${color}40`,
              boxShadow: `0 0 24px ${color}20`,
            }}
          >
            {icon}
          </div>

          <div className="flex-1 min-w-0 w-full">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <span className="text-[10px] font-bold uppercase tracking-widest text-secondary">
                Student Archetype · Cluster #{(cluster.cluster_id ?? 0) + 1}
              </span>
            </div>

            <h2 className="font-heading text-xl sm:text-2xl font-bold text-app mb-1 break-words">
              {cluster.archetype_name}
            </h2>

            <EngineMethodBadge method={cluster.prediction_method} label={cluster.prediction_label} />

            <p className="mt-3 text-xs sm:text-sm text-secondary leading-relaxed">
              {cluster.description}
            </p>
          </div>
        </div>

        {/* Career Alignment */}
        {cluster.career_fit && cluster.career_fit.length > 0 && (
          <div className="mt-5 pt-5 border-t border-app">
            <p className="text-[10px] font-bold uppercase tracking-wider text-secondary mb-2.5 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5" style={{ color }} />
              Career Alignment in Your Cluster
            </p>
            <div className="flex flex-wrap gap-2">
              {cluster.career_fit.map((career) => (
                <span
                  key={career}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border"
                  style={{
                    background: `${color}10`,
                    borderColor: `${color}35`,
                    color,
                  }}
                >
                  <ChevronRight className="w-3 h-3" />
                  {career}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Technical note */}
        {cluster.note && (
          <div className="mt-4 flex items-start gap-2 p-3 rounded-md bg-subtle border border-app">
            <Info className="w-4 h-4 text-muted flex-shrink-0 mt-0.5" />
            <p className="text-xs text-secondary leading-relaxed">{cluster.note}</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Model Status Card ─────────────────────────────────────────────────────────
function ModelStatusCard({ status }: { status: MLStatus | undefined }) {
  if (!status) return null

  const models = [
    { key: 'readiness_rf',       label: 'Random Forest Regression',    subtitle: 'Job Readiness Score' },
    { key: 'career_rf',          label: 'Random Forest Classification', subtitle: 'Career Recommendations' },
    { key: 'kmeans_clustering',  label: 'K-Means Clustering',          subtitle: 'Student Profiling' },
  ]

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-4">
        <Award className="w-4 h-4 text-[#FF5722]" />
        <h3 className="font-heading font-bold text-app text-sm uppercase tracking-wider">ML Engine Status</h3>
        <span className="ml-auto text-[10px] font-mono text-secondary">v{status.ml_engine_version}</span>
      </div>

      <div className="space-y-3">
        {models.map(({ key, label, subtitle }) => {
          const modelStatus = (status.models as any)[key]
          const isTrained = modelStatus?.status === 'trained'
          const metrics = modelStatus?.metrics || {}

          return (
            <div key={key} className={`flex items-center gap-3 p-3 rounded-md border ${
              isTrained
                ? 'bg-emerald-50/50 border-emerald-200/60 dark:bg-emerald-950/20 dark:border-emerald-700/40'
                : 'bg-subtle border-app'
            }`}>
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${isTrained ? 'bg-emerald-500' : 'bg-amber-400'}`} />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-app truncate">{label}</p>
                <p className="text-[10px] text-secondary">{subtitle}</p>
              </div>
              <div className="text-right">
                {isTrained ? (
                  <div>
                    <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400">Trained</span>
                    {Object.entries(metrics).slice(0, 1).map(([k, v]) => (
                      <p key={k} className="text-[9px] font-mono text-secondary">
                        {k.toUpperCase()}: {typeof v === 'number' ? (v as number).toFixed(3) : String(v)}
                      </p>
                    ))}
                  </div>
                ) : (
                  <span className="text-[10px] font-bold text-amber-600 dark:text-amber-400">Not Trained</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function ProfilingPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [showTrainConfirm, setShowTrainConfirm] = useState(false)

  const { data: cluster, isLoading: clusterLoading } = useQuery<ClusterResult>({
    queryKey: ['mlCluster', user?.uid],
    queryFn: () => api.get('/api/ml/profile-cluster').then(r => r.data),
    staleTime: 5 * 60 * 1000, // 5 min
  })

  const { data: mlStatus } = useQuery<MLStatus>({
    queryKey: ['mlStatus'],
    queryFn: () => api.get('/api/ml/status').then(r => r.data),
    staleTime: 60 * 1000,
  })

  const trainMutation = useMutation({
    mutationFn: () => api.post('/api/ml/train?n_clusters=5'),
    onSuccess: () => {
      toast.success('ML models trained successfully! Refreshing your profile...')
      setShowTrainConfirm(false)
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['mlCluster'] })
        queryClient.invalidateQueries({ queryKey: ['mlStatus'] })
        queryClient.invalidateQueries({ queryKey: ['jobScore'] })
      }, 1500)
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'Training failed'
      toast.error(msg)
    },
  })

  const reclusterMutation = useMutation({
    mutationFn: () => api.get('/api/ml/profile-cluster'),
    onSuccess: (res) => {
      queryClient.setQueryData(['mlCluster', user?.uid], res.data)
      toast.success('Profile cluster updated!')
    },
    onError: () => toast.error('Re-cluster failed'),
  })

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Users className="w-5 h-5 text-[#FF5722]" />
            <h1 className="font-heading text-xl sm:text-2xl font-bold text-app">Student Profiling</h1>
          </div>
          <p className="text-xs sm:text-sm text-secondary leading-relaxed max-w-xl">
            K-Means Clustering groups you with similar students to identify your career archetype and skill orientation.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap w-full sm:w-auto">
          <button
            id="btn-recluster"
            onClick={() => reclusterMutation.mutate()}
            disabled={reclusterMutation.isPending || clusterLoading}
            className="btn btn-secondary text-xs flex items-center justify-center gap-2 w-full sm:w-auto min-h-[38px]"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reclusterMutation.isPending ? 'animate-spin' : ''}`} />
            Re-cluster Profile
          </button>
          <button
            id="btn-train-ml"
            onClick={() => setShowTrainConfirm(true)}
            className="btn btn-primary text-xs flex items-center justify-center gap-2 w-full sm:w-auto min-h-[38px]"
          >
            <Brain className="w-3.5 h-3.5 text-white" />
            Train ML Models
          </button>
        </div>
      </div>

      {/* Train Confirmation Banner */}
      {showTrainConfirm && (
        <div className="card p-4 border-2 border-[#FF5722]/40 bg-[#FF5722]/5">
          <p className="text-sm font-medium text-app mb-3">
            This will train all ML models using the <code className="font-mono text-xs bg-subtle px-1 rounded">students_database.json</code> dataset (~250 students).
            Training takes 10–30 seconds. Proceed?
          </p>
          <div className="flex gap-2">
            <button
              id="btn-confirm-train"
              onClick={() => trainMutation.mutate()}
              disabled={trainMutation.isPending}
              className="btn-editorial text-xs flex items-center gap-1.5"
            >
              {trainMutation.isPending ? (
                <><RefreshCw className="w-3 h-3 animate-spin" /> Training...</>
              ) : (
                <><Brain className="w-3 h-3" /> Yes, Train Now</>
              )}
            </button>
            <button
              onClick={() => setShowTrainConfirm(false)}
              className="btn-secondary text-xs"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Archetype Card (main) */}
        <div className="lg:col-span-2">
          {clusterLoading ? (
            <div className="card p-8 text-center">
              <RefreshCw className="w-8 h-8 text-muted mx-auto mb-3 animate-spin" />
              <p className="text-sm text-secondary">Analyzing your profile...</p>
            </div>
          ) : cluster ? (
            <ArchetypeCard cluster={cluster} />
          ) : (
            <div className="card p-8 text-center">
              <Brain className="w-10 h-10 text-muted mx-auto mb-3" />
              <p className="text-sm text-secondary">Failed to load cluster data.</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <ModelStatusCard status={mlStatus} />
        </div>
      </div>

      {/* How It Works */}
      <div className="card p-6">
        <h3 className="font-heading font-bold text-app mb-4 flex items-center gap-2">
          <Info className="w-4 h-4 text-[#FF5722]" />
          How Student Profiling Works
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {HOW_IT_WORKS_STEPS.map((step) => (
            <div key={step.step} className="flex flex-col gap-2 p-3 rounded-md bg-subtle border border-app">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-[#FF5722]/10 text-[#FF5722] flex items-center justify-center text-[10px] font-bold border border-[#FF5722]/30 flex-shrink-0">
                  {step.step}
                </div>
                <step.icon className="w-4 h-4 text-secondary" />
              </div>
              <p className="text-xs font-bold text-app">{step.title}</p>
              <p className="text-[11px] text-secondary leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>

        {/* Method Transparency */}
        <div className="mt-4 p-3 rounded-md bg-subtle border border-app">
          <p className="text-[11px] text-secondary leading-relaxed">
            <span className="font-bold text-app">Transparency:</span>{' '}
            All ML predictions are clearly labeled with their method. This page uses{' '}
            <strong>K-Means Clustering</strong> (scikit-learn). The job readiness score uses{' '}
            <strong>Random Forest Regression</strong> when trained, or{' '}
            <strong>TF-IDF Semantic Alignment</strong> as fallback. Career recommendations use{' '}
            <strong>Random Forest Classification</strong> when trained, or{' '}
            <strong>Rule-Based Skill Matching</strong> as fallback. The AI chatbot uses{' '}
            <strong>Gemini LLM</strong>. No predictions are fabricated or hardcoded.
          </p>
        </div>
      </div>
    </div>
  )
}
