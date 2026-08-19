import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import { Link } from 'react-router-dom'
import api from '@/lib/api'
import {
  Award, Briefcase,
  ArrowRight, RefreshCw, FileCheck,
  Bot, Layers, Target, BookOpen, Clock, Sparkles
} from 'lucide-react'
import toast from 'react-hot-toast'
import { SubtlePathsBg } from '@/components/ui/subtle-paths-bg'

// ── 6 Feature Command Cards ──────────────────────────────────────────────────
const FEATURE_COMMAND_CARDS = [
  {
    id: 'interview',
    title: 'AI Technical Interview',
    desc: 'Simulate domain-specific technical & behavioral interview loops.',
    tag: 'Practice Room',
    icon: Bot,
    to: '/practice/interview',
    badge: 'Popular',
  },
  {
    id: 'career-path',
    title: 'Career Path Alignment',
    desc: 'Algorithmic market track matching based on verified skill profile.',
    tag: 'Career Tracks',
    icon: Briefcase,
    to: '/career/tracks',
    badge: 'Updated',
  },
  {
    id: 'skill-analysis',
    title: 'Skill Gap Analysis',
    desc: 'Compare candidate competencies against 2026 hiring benchmarks.',
    tag: 'Benchmark Grid',
    icon: Target,
    to: '/career/skill-gap',
  },
  {
    id: 'resume-review',
    title: 'Resume & ATS Review',
    desc: 'Audit keyword density and structural parser compliance.',
    tag: 'Diagnostics',
    icon: FileCheck,
    to: '/analytics/resume',
  },
  {
    id: 'mock-tests',
    title: 'Technical Mock Tests',
    desc: 'Timed code drills and domain knowledge evaluations.',
    tag: 'Speed Drills',
    icon: Layers,
    to: '/practice/tests',
  },
  {
    id: 'roadmap',
    title: 'AI Learning Roadmap',
    desc: 'Sequential curriculum to bridge active skill gaps.',
    tag: 'Curriculum',
    icon: BookOpen,
    to: '/career/roadmap',
  },
]

export default function DashboardPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'overview' | 'readiness' | 'tools' | 'activity'>('overview')

  const { data: profile } = useQuery({
    queryKey: ['profile', user?.uid],
    queryFn: () => api.get('/api/profile').then(r => r.data),
  })

  const { data: jobScore } = useQuery({
    queryKey: ['jobScore', user?.uid],
    queryFn: () => api.get('/api/job-score').then(r => r.data),
  })

  const { data: certs } = useQuery({
    queryKey: ['certificates', user?.uid],
    queryFn: () => api.get('/api/certificates').then(r => r.data),
  })

  const refreshMutation = useMutation({
    mutationFn: () => api.post('/api/job-score/recalculate'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobScore'], exact: false })
      queryClient.invalidateQueries({ queryKey: ['profile'], exact: false })
      toast.success('Career Readiness Score recalculated!')
    },
  })

  const firstName = user?.displayName?.split(' ')[0] || 'Candidate'
  const targetCareer = profile?.target_career || 'Full-Stack Engineer'
  const totalScore = jobScore?.total_score ?? 0
  const scoreTier = totalScore >= 75 ? 'Industry Ready' : totalScore >= 50 ? 'Developing Alignment' : 'Foundational'

  const dashboardTabs = [
    { id: 'overview',  label: 'Overview Command Center' },
    { id: 'readiness', label: 'Readiness Matrix Breakdown' },
    { id: 'tools',     label: 'Feature Command Suite' },
    { id: 'activity',  label: 'Activity & Feed Log' },
  ]

  return (
    <div className="space-y-6 text-app">
      {/* ── Contextual Horizontal Sub-Navigation for Dashboard Section ─────── */}
      <div className="bg-surface border border-app rounded-md p-1.5 flex items-center gap-1.5 overflow-x-auto">
        {dashboardTabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as any)}
            className={`px-4 py-2 text-xs font-bold transition-all rounded-md flex-shrink-0 ${
              activeTab === t.id
                ? 'bg-[#FF5722]/10 text-[#FF5722] border-b-2 border-[#FF5722] dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043] shadow-2xs'
                : 'text-secondary hover:bg-subtle hover:text-app'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── TOP WELCOME BANNER ─────────────────────────────────────────────── */}
      <div className="card p-6 border-app flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 shadow-xs relative overflow-hidden">
        <SubtlePathsBg opacity={0.25} sets={1} />
        <div className="space-y-1.5 max-w-2xl relative z-10">
          <div className="flex items-center gap-2">
            <span className="badge badge-emerald">Active Command Center</span>
            <span className="text-xs font-semibold text-secondary font-mono">Target Track: <strong className="text-app">{targetCareer}</strong></span>
          </div>
          <h1 className="font-heading text-3xl font-extrabold text-app">
            Welcome back, {firstName}.
          </h1>
          <p className="text-secondary text-xs leading-relaxed">
            Your candidate evidence portfolio is mapped against 2026 corporate hiring requisitions. Complete active learning milestones to elevate candidate readiness grade.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0 relative z-10">
          <button
            onClick={() => refreshMutation.mutate()}
            disabled={refreshMutation.isPending}
            className="btn btn-secondary text-xs gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
            Recalculate Readiness
          </button>
          <Link to="/practice/interview" className="btn btn-primary text-xs gap-2">
            <Bot className="w-3.5 h-3.5 text-white" /> Launch AI Interview
          </Link>
        </div>
      </div>

      {/* ── PROMINENT CAREER READINESS SCORE CARD ──────────────────────────── */}
      {(activeTab === 'overview' || activeTab === 'readiness') && (
        <div className="card p-6 bg-surface border-app space-y-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-app">
            <div className="flex items-center gap-5">
              {/* Radial Progress Gauge Simulation */}
              <div className="relative w-24 h-24 flex items-center justify-center bg-[#FF5722]/10 dark:bg-[#FF5722]/15 rounded-full border-4 border-[#FF5722]/40 flex-shrink-0">
                <div className="text-center">
                  <span className="font-heading text-3xl font-extrabold text-app">{totalScore}</span>
                  <span className="text-[10px] text-secondary font-bold block -mt-1">/ 100</span>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-[10px] font-extrabold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block">
                    Dynamic Career Readiness Score
                  </span>
                  <span className="badge badge-emerald text-[10px]">
                    {jobScore?.confidence_level || 'Data Precision'}
                  </span>
                </div>
                <h2 className="font-heading text-2xl font-bold text-app">Career Readiness Index</h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className="badge badge-sand font-bold">{scoreTier}</span>
                  <span className="text-xs font-medium text-secondary">
                    {totalScore === 0 ? 'Brand new account — complete activities to build your score' : 'Calculated across 6 verified employability dimensions'}
                  </span>
                </div>
              </div>
            </div>

            {/* 6-Factor Breakdown Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 w-full md:w-auto">
              <div className="p-2.5 bg-subtle border border-app rounded-md text-center">
                <p className="text-[10px] font-bold text-secondary uppercase">Skills</p>
                <p className="font-heading text-lg font-bold text-app mt-0.5">
                  {jobScore?.skills_score ?? 0} <span className="text-[10px] text-secondary font-semibold">/25</span>
                </p>
              </div>
              <div className="p-2.5 bg-subtle border border-app rounded-md text-center">
                <p className="text-[10px] font-bold text-secondary uppercase">Projects</p>
                <p className="font-heading text-lg font-bold text-app mt-0.5">
                  {jobScore?.projects_score ?? 0} <span className="text-[10px] text-secondary font-semibold">/20</span>
                </p>
              </div>
              <div className="p-2.5 bg-subtle border border-app rounded-md text-center">
                <p className="text-[10px] font-bold text-secondary uppercase">Interviews</p>
                <p className="font-heading text-lg font-bold text-app mt-0.5">
                  {jobScore?.interviews_score ?? 0} <span className="text-[10px] text-secondary font-semibold">/20</span>
                </p>
              </div>
              <div className="p-2.5 bg-subtle border border-app rounded-md text-center">
                <p className="text-[10px] font-bold text-secondary uppercase">Resume ATS</p>
                <p className="font-heading text-lg font-bold text-app mt-0.5">
                  {jobScore?.resume_score ?? 0} <span className="text-[10px] text-secondary font-semibold">/15</span>
                </p>
              </div>
              <div className="p-2.5 bg-subtle border border-app rounded-md text-center">
                <p className="text-[10px] font-bold text-secondary uppercase">Mock Tests</p>
                <p className="font-heading text-lg font-bold text-app mt-0.5">
                  {jobScore?.assessments_score ?? 0} <span className="text-[10px] text-secondary font-semibold">/10</span>
                </p>
              </div>
              <div className="p-2.5 bg-subtle border border-app rounded-md text-center">
                <p className="text-[10px] font-bold text-secondary uppercase">Certs</p>
                <p className="font-heading text-lg font-bold text-app mt-0.5">
                  {jobScore?.certificates_score ?? 0} <span className="text-[10px] text-secondary font-semibold">/10</span>
                </p>
              </div>
            </div>
          </div>

          {/* Readiness Progression Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-app">Market Requisition Readiness Progression</span>
              <span className="font-mono font-bold text-[#FF5722] dark:text-[#FF7043]">{totalScore}% Employability Grade</span>
            </div>
            <div className="w-full h-3 bg-subtle border border-app rounded-full overflow-hidden">
              <div
                className="h-full bg-[#FF5722] transition-all rounded-full"
                style={{ width: `${Math.max(2, totalScore)}%` }}
              />
            </div>
          </div>

          {/* Positive Drivers & Actionable Insights Section */}
          <div className="grid md:grid-cols-2 gap-4 pt-2">
            {/* Positive Score Drivers */}
            <div className="p-4 bg-subtle border border-app rounded-md space-y-2">
              <span className="text-[10px] font-extrabold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block">
                Evidence Drivers &amp; Score Insights
              </span>
              <ul className="space-y-1.5 text-xs text-secondary font-medium">
                {(jobScore?.positive_drivers && jobScore.positive_drivers.length > 0) ? (
                  jobScore.positive_drivers.map((driver: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-[#FF5722] dark:text-[#FF7043] font-bold">✓</span>
                      <span>{driver}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-secondary italic">Complete profile activities to unlock evidence drivers.</li>
                )}
              </ul>
            </div>

            {/* Actionable Next Steps */}
            <div className="p-4 bg-subtle border border-app rounded-md space-y-2">
              <span className="text-[10px] font-extrabold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block">
                Priority Actions to Elevate Score
              </span>
              <ul className="space-y-1.5 text-xs text-secondary font-medium">
                {(jobScore?.suggestions && jobScore.suggestions.length > 0) ? (
                  jobScore.suggestions.map((sug: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-[#FF5722] dark:text-[#FF7043] font-bold">⚡</span>
                      <span>{sug}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-secondary">Keep your portfolio up to date with new projects and mock interviews.</li>
                )}
              </ul>
            </div>
          </div>

          {/* Score History Progression Timeline */}
          {jobScore?.history && jobScore.history.length > 0 && (
            <div className="pt-2 border-t border-app space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-extrabold text-app uppercase tracking-wider">
                  Readiness Progression History Log
                </span>
                <span className="text-[10px] text-secondary font-mono">
                  {jobScore.history.length} audited score changes
                </span>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {jobScore.history.slice().reverse().map((entry: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2.5 bg-surface border border-app rounded-md text-xs">
                    <div className="flex items-center gap-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${entry.delta >= 0 ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400' : 'bg-red-500/15 text-red-600'}`}>
                        {entry.delta >= 0 ? `+${entry.delta}` : entry.delta} pts
                      </span>
                      <span className="font-bold text-app">{entry.reason}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-heading font-extrabold text-app">{entry.total_score} / 100</span>
                      <span className="text-[10px] text-secondary font-mono">
                        {entry.timestamp ? new Date(entry.timestamp).toLocaleDateString() : 'Recent'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── 6 FEATURE DASHBOARD COMMAND CARDS ───────────────────────────────── */}
      {(activeTab === 'overview' || activeTab === 'tools') && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-heading text-xl font-bold text-app">Platform Command Suite</h2>
            <span className="text-xs font-medium text-secondary">Access candidate career tools</span>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURE_COMMAND_CARDS.map((card) => {
              const Icon = card.icon
              return (
                <Link
                  key={card.id}
                  to={card.to}
                  className="card p-5 space-y-3 flex flex-col justify-between hover:border-[#FF5722]/50 dark:hover:border-[#FF7043]/50 transition-all group"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-9 h-9 bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded-md flex items-center justify-center">
                        <Icon className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                      </div>
                      {card.badge && <span className="badge badge-emerald">{card.badge}</span>}
                    </div>
                    <h3 className="font-heading text-lg font-bold text-app group-hover:text-[#FF5722] dark:group-hover:text-[#FF7043] transition-colors">
                      {card.title}
                    </h3>
                    <p className="text-xs text-secondary leading-relaxed">{card.desc}</p>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-app text-xs text-[#FF5722] dark:text-[#FF7043] font-bold">
                    <span>{card.tag}</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      )}

      {/* ── SECONDARY FEED GRID: ACTIVITIES, TASKS & AI INSIGHTS ────────────── */}
      {(activeTab === 'overview' || activeTab === 'activity') && (
        <div className="grid lg:grid-cols-12 gap-6">
          {/* Left Column: Recent Activity & Upcoming Tasks */}
          <div className="lg:col-span-8 space-y-6">
            {/* Recent Activity */}
            <div className="card p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-app">
                <h3 className="font-heading text-lg font-bold text-app flex items-center gap-2">
                  <Clock className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Recent Candidate Activity
                </h3>
                <span className="text-xs font-medium text-secondary">Audited event log</span>
              </div>

              <div className="space-y-3">
                {[
                  { title: 'AI Technical Mock Interview Completed', score: '85% Technical Grade', time: '2 hours ago', icon: Bot },
                  { title: 'AWS Cloud Developer Certificate Uploaded', score: 'OCR Verified', time: '1 day ago', icon: Award },
                  { title: 'Resume ATS Diagnostic Executed', score: '78 ATS Match Index', time: '2 days ago', icon: FileCheck },
                ].map((act, i) => (
                  <div key={i} className="flex items-start justify-between p-3.5 bg-subtle border border-app rounded-md text-xs">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded-md flex items-center justify-center flex-shrink-0">
                        <act.icon className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                      </div>
                      <div>
                        <p className="font-bold text-app">{act.title}</p>
                        <p className="text-[11px] text-secondary font-medium">{act.time}</p>
                      </div>
                    </div>
                    <span className="badge badge-sand">{act.score}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Roadmap Tasks */}
            <div className="card p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-app">
                <h3 className="font-heading text-lg font-bold text-app flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Upcoming Roadmap Tasks
                </h3>
                <Link to="/career/roadmap" className="text-xs font-bold text-[#FF5722] dark:text-[#FF7043] hover:underline">
                  View Full Roadmap →
                </Link>
              </div>

              <div className="space-y-2.5">
                {[
                  { name: 'Master PostgreSQL Query Indexing & Schema Design', stage: 'Stage III', priority: 'High' },
                  { name: 'Docker Multi-stage Build Configuration Drill', stage: 'Stage IV', priority: 'Medium' },
                ].map((task, idx) => (
                  <div key={idx} className="p-3.5 bg-subtle border border-app rounded-md flex items-center justify-between text-xs">
                    <div>
                      <p className="font-bold text-app">{task.name}</p>
                      <p className="text-[10px] text-secondary font-medium">{task.stage}</p>
                    </div>
                    <span className={`badge ${task.priority === 'High' ? 'badge-red' : 'badge-amber'}`}>
                      {task.priority} Priority
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Personalized AI Insights */}
          <div className="lg:col-span-4 space-y-6">
            <div className="card p-6 space-y-4 bg-[#FF5722]/10 dark:bg-[#FF5722]/15 border-[#FF5722]/30 dark:border-[#FF5722]/40">
              <div className="flex items-center gap-2 pb-3 border-b border-[#FF5722]/30 dark:border-[#FF5722]/40">
                <Sparkles className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                <h3 className="font-heading text-lg font-bold text-app">AI Strategist Insights</h3>
              </div>

              <div className="space-y-3 text-xs text-secondary leading-relaxed font-medium">
                <p>
                  <strong>Target Role Optimization:</strong> Your verified skills in React & TypeScript match <strong className="text-app font-bold">88%</strong> of market requisitions for <em>{targetCareer}</em>.
                </p>
                <div className="p-3.5 bg-surface border border-[#FF5722]/30 dark:border-[#FF5722]/40 rounded-md space-y-1">
                  <p className="font-bold text-app">Priority Action Recommendation:</p>
                  <p className="text-[11px] text-secondary font-medium">
                    Complete the <strong>SQL Performance & Database Design Drill</strong> to increase overall candidate readiness score to 85%+.
                  </p>
                </div>
                <Link to="/practice/tests" className="btn btn-primary text-xs w-full justify-center gap-1.5">
                  Launch Recommended Drill →
                </Link>
              </div>
            </div>

            {/* Quick Stats Summary Widget */}
            <div className="card p-5 space-y-3">
              <span className="text-[10px] font-bold text-secondary uppercase tracking-wider block">Candidate dossier stats</span>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-subtle border border-app rounded-md text-center">
                  <p className="font-heading text-2xl font-bold text-app">{profile?.skills?.length || 8}</p>
                  <p className="text-[10px] text-secondary font-semibold">Skills Verified</p>
                </div>
                <div className="p-3 bg-subtle border border-app rounded-md text-center">
                  <p className="font-heading text-2xl font-bold text-app">{(certs?.certificates || []).length || 2}</p>
                  <p className="text-[10px] text-secondary font-semibold">Certificates</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
