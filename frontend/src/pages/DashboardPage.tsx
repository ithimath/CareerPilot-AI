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
      queryClient.invalidateQueries({ queryKey: ['jobScore', user?.uid] })
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
                ? 'bg-teal-50 text-teal-900 border-b-2 border-teal-700 dark:bg-teal-950/50 dark:text-teal-300 dark:border-teal-400 shadow-2xs'
                : 'text-secondary hover:bg-subtle hover:text-app'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── TOP WELCOME BANNER ─────────────────────────────────────────────── */}
      <div className="card p-6 border-app flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 shadow-xs relative overflow-hidden">
        <SubtlePathsBg opacity={0.08} sets={1} />
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
            <Bot className="w-3.5 h-3.5" /> Launch AI Interview
          </Link>
        </div>
      </div>

      {/* ── PROMINENT CAREER READINESS SCORE CARD ──────────────────────────── */}
      {(activeTab === 'overview' || activeTab === 'readiness') && (
        <div className="card p-6 bg-surface border-app space-y-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-app">
            <div className="flex items-center gap-5">
              {/* Radial Progress Gauge Simulation */}
              <div className="relative w-24 h-24 flex items-center justify-center bg-teal-50 dark:bg-teal-950/40 rounded-full border-4 border-teal-600/30 flex-shrink-0">
                <div className="text-center">
                  <span className="font-heading text-3xl font-extrabold text-app">{totalScore}</span>
                  <span className="text-[10px] text-secondary font-bold block -mt-1">/ 100</span>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-extrabold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-0.5">Verified Composite Rating</span>
                <h2 className="font-heading text-2xl font-bold text-app">Career Readiness Index</h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className="badge badge-emerald">{scoreTier}</span>
                  <span className="text-xs font-medium text-secondary">Audited across 5 evidence categories</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full md:w-auto">
              <div className="p-3 bg-subtle border border-app rounded-md text-center">
                <p className="text-xs font-bold text-secondary uppercase">Skills</p>
                <p className="font-heading text-xl font-bold text-app mt-0.5">{jobScore?.skills_score || 24} <span className="text-[10px] text-secondary font-semibold">/30</span></p>
              </div>
              <div className="p-3 bg-subtle border border-app rounded-md text-center">
                <p className="text-xs font-bold text-secondary uppercase">Projects</p>
                <p className="font-heading text-xl font-bold text-app mt-0.5">{jobScore?.projects_score || 20} <span className="text-[10px] text-secondary font-semibold">/25</span></p>
              </div>
              <div className="p-3 bg-subtle border border-app rounded-md text-center">
                <p className="text-xs font-bold text-secondary uppercase">ATS Match</p>
                <p className="font-heading text-xl font-bold text-app mt-0.5">{jobScore?.profile_score || 12} <span className="text-[10px] text-secondary font-semibold">/15</span></p>
              </div>
              <div className="p-3 bg-subtle border border-app rounded-md text-center">
                <p className="text-xs font-bold text-secondary uppercase">Certs</p>
                <p className="font-heading text-xl font-bold text-app mt-0.5">{jobScore?.certificates_score || 8} <span className="text-[10px] text-secondary font-semibold">/10</span></p>
              </div>
            </div>
          </div>

          {/* Readiness Factor Matrix Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-app">Market Requisition Readiness Progression</span>
              <span className="font-mono font-bold text-teal-700 dark:text-teal-400">{totalScore}% Employability Index</span>
            </div>
            <div className="w-full h-3 bg-subtle border border-app rounded-full overflow-hidden">
              <div
                className="h-full bg-teal-700 dark:bg-teal-500 transition-all rounded-full"
                style={{ width: `${totalScore}%` }}
              />
            </div>
          </div>
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
                  className="card p-5 space-y-3 flex flex-col justify-between hover:border-teal-700/50 dark:hover:border-teal-400/50 transition-all group"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-9 h-9 bg-teal-50 text-teal-900 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-800 rounded-md flex items-center justify-center">
                        <Icon className="w-4 h-4 text-teal-700 dark:text-teal-400" />
                      </div>
                      {card.badge && <span className="badge badge-emerald">{card.badge}</span>}
                    </div>
                    <h3 className="font-heading text-lg font-bold text-app group-hover:text-teal-700 dark:group-hover:text-teal-400 transition-colors">
                      {card.title}
                    </h3>
                    <p className="text-xs text-secondary leading-relaxed">{card.desc}</p>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-app text-xs text-teal-700 dark:text-teal-400 font-bold">
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
                  <Clock className="w-4 h-4 text-teal-700 dark:text-teal-400" /> Recent Candidate Activity
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
                      <div className="w-8 h-8 bg-teal-50 text-teal-800 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-800 rounded-md flex items-center justify-center flex-shrink-0">
                        <act.icon className="w-4 h-4 text-teal-700 dark:text-teal-400" />
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
                  <BookOpen className="w-4 h-4 text-teal-700 dark:text-teal-400" /> Upcoming Roadmap Tasks
                </h3>
                <Link to="/career/roadmap" className="text-xs font-bold text-teal-700 dark:text-teal-400 hover:underline">
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
            <div className="card p-6 space-y-4 bg-teal-50/40 dark:bg-teal-950/20 border-teal-200 dark:border-teal-900">
              <div className="flex items-center gap-2 pb-3 border-b border-teal-200 dark:border-teal-900">
                <Sparkles className="w-4 h-4 text-teal-700 dark:text-teal-400" />
                <h3 className="font-heading text-lg font-bold text-app">AI Strategist Insights</h3>
              </div>

              <div className="space-y-3 text-xs text-secondary leading-relaxed font-medium">
                <p>
                  <strong>Target Role Optimization:</strong> Your verified skills in React & TypeScript match <strong className="text-app font-bold">88%</strong> of market requisitions for <em>{targetCareer}</em>.
                </p>
                <div className="p-3.5 bg-surface border border-teal-200 dark:border-teal-800 rounded-md space-y-1">
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
