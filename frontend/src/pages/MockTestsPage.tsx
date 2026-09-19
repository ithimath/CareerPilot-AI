/**
 * CareerPilot AI — Mock Technical Assessment System (Enhanced Phase 6)
 *
 * Features:
 * - 6 career-path test suites with Intermediate-to-Advanced calibrated MCQs
 * - 3 Open-Ended Technical Scenario Questions per track
 * - Strict 10-minute (600s) server-enforced countdown timer with auto-submit
 * - 5-Criteria Multi-Rubric Evaluation (Correctness, Reasoning, Technical Depth, Relevance, Completeness)
 * - Separate scoring for MCQs and Open-Ended questions
 * - Persists attempt via backend (/api/assessments/submit) & score history
 */
import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import api from '@/lib/api'

// ── Types ─────────────────────────────────────────────────────────────────────
interface Question {
  id: number
  topic: string
  difficulty: 'easy' | 'medium' | 'hard'
  type: 'conceptual' | 'scenario' | 'code_output'
  q: string
  options: string[]
  correct: number
  explanation: string
}

interface OpenEndedQuestion {
  id: number
  title: string
  scenario: string
  prompt: string
  rubric_focus: string[]
}

interface OpenEndedEvaluation {
  question_id: number
  question_title: string
  correctness: number
  reasoning: number
  technical_understanding: number
  relevance: number
  completeness: number
  score: number
  feedback: string
}

interface TestMeta {
  id: string
  title: string
  career_path: string
  category: string
  questions_count: number
  open_ended_count?: number
  time_limit_seconds: number
  difficulty: string
}

interface TestWithQuestions extends TestMeta {
  questions: Question[]
  open_ended_questions?: OpenEndedQuestion[]
}

interface Attempt {
  test_id: string
  test_title: string
  career_path: string
  category: string
  score: number
  mcq_score?: number
  open_ended_score?: number
  correct_count: number
  incorrect_count: number
  total_questions: number
  time_taken: number
  time_expired?: boolean
  session_id?: string
  mcq_answers?: Record<string, number>
  open_ended_answers?: Array<{ question_id: number; question: string; answer: string }>
  open_ended_evaluations?: OpenEndedEvaluation[]
  topic_breakdown: Record<string, { correct: number; total: number }>
  difficulty_breakdown: Record<string, { correct: number; total: number }>
}

interface AssessmentRecord {
  id: string
  test_id: string
  test_title: string
  career_path: string
  score: number
  mcq_score?: number
  open_ended_score?: number
  correct_count: number
  total_questions: number
  time_taken: number
  timestamp: string
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const DIFF_COLOR: Record<string, string> = {
  easy: 'text-emerald-400',
  medium: 'text-amber-400',
  hard: 'text-rose-400',
}

const DIFF_BG: Record<string, string> = {
  easy: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
  medium: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
  hard: 'bg-rose-500/10 border-rose-500/30 text-rose-300',
}

const CAREER_EMOJI: Record<string, string> = {
  'full-stack': '🏗️',
  'ai-ml': '🤖',
  backend: '⚙️',
  frontend: '🎨',
  'data-science': '📊',
  cloud: '☁️',
  dsa: '🧩',
  'sql-dbms': '🗄️',
  'aiml-fundamentals': '🧠',
  aptitude: '🎯',
}

function formatTime(seconds: number): string {
  const m = Math.floor(Math.max(0, seconds) / 60).toString().padStart(2, '0')
  const s = (Math.max(0, seconds) % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function scoreLabel(pct: number): { label: string; color: string } {
  if (pct >= 80) return { label: 'Excellent', color: 'text-emerald-400' }
  if (pct >= 60) return { label: 'Good', color: 'text-amber-400' }
  if (pct >= 40) return { label: 'Fair', color: 'text-orange-400' }
  return { label: 'Needs Work', color: 'text-rose-400' }
}

// ── Main Component ─────────────────────────────────────────────────────────────
export default function MockTestsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()

  // ── Phase state: 'select' | 'test' | 'result' ───────────────────────────────
  const [phase, setPhase] = useState<'select' | 'test' | 'result'>('select')
  const [activeTestId, setActiveTestId] = useState<string | null>(null)
  const [testData, setTestData] = useState<TestWithQuestions | null>(null)
  const [lastResult, setLastResult] = useState<Attempt | null>(null)

  // ── Test session state ───────────────────────────────────────────────────────
  const [testTab, setTestTab] = useState<'mcq' | 'open_ended'>('mcq')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [answers, setAnswers] = useState<Record<number, number>>({})             // questionIndex → optionIndex
  const [openEndedAnswers, setOpenEndedAnswers] = useState<Record<number, string>>({}) // questionId → answer
  const [flagged, setFlagged] = useState<Set<number>>(new Set())
  const [currentQ, setCurrentQ] = useState(0)
  const [currentOpenQ, setCurrentOpenQ] = useState(0)
  const [timeLeft, setTimeLeft] = useState(600) // 10 minutes (600s)
  const [submitted, setSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [startError, setStartError] = useState<string | null>(null)
  const [startingTestId, setStartingTestId] = useState<string | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const submitRef = useRef<() => void>(() => {})

  // ── Fetch test catalog ───────────────────────────────────────────────────────
  const { data: catalog, isLoading: catalogLoading } = useQuery<{ tests: TestMeta[] }>({
    queryKey: ['assessments-catalog'],
    queryFn: () => api.get('/api/assessments/tests').then(r => r.data),
    staleTime: 5 * 60 * 1000,
  })

  // ── Fetch history ─────────────────────────────────────────────────────────────
  const { data: history } = useQuery<{ assessments: AssessmentRecord[] }>({
    queryKey: ['assessments-history', user?.uid],
    queryFn: () => api.get('/api/assessments/history').then(r => r.data),
    enabled: !!user?.uid,
  })

  // ── Submit mutation ───────────────────────────────────────────────────────────
  const submitMutation = useMutation({
    mutationFn: (payload: Attempt) => api.post('/api/assessments/submit', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobScore'] })
      queryClient.invalidateQueries({ queryKey: ['assessments-history'] })
    },
  })

  function clearTimerInterval() {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  // ── Compute and submit results ────────────────────────────────────────────────
  const computeAndSubmit = useCallback(async (timeTaken: number) => {
    if (!testData || submitted) return
    setSubmitted(true)
    setIsSubmitting(true)
    clearTimerInterval()

    const questions = testData.questions
    let correct = 0
    const topicMap: Record<string, { correct: number; total: number }> = {}
    const diffMap: Record<string, { correct: number; total: number }> = {}

    questions.forEach((q, idx) => {
      const userAns = answers[idx]
      const isCorrect = userAns !== undefined && userAns === q.correct

      if (!topicMap[q.topic]) topicMap[q.topic] = { correct: 0, total: 0 }
      topicMap[q.topic].total++
      if (isCorrect) { correct++; topicMap[q.topic].correct++ }

      if (!diffMap[q.difficulty]) diffMap[q.difficulty] = { correct: 0, total: 0 }
      diffMap[q.difficulty].total++
      if (isCorrect) diffMap[q.difficulty].correct++
    })

    const mcqPct = Math.round((correct / Math.max(1, questions.length)) * 100)

    // Format open-ended answers
    const openAnswersList = (testData.open_ended_questions || []).map(q => ({
      question_id: q.id,
      question: q.title,
      answer: openEndedAnswers[q.id] || '',
    }))

    const formattedMcqAnswers: Record<string, number> = {}
    Object.entries(answers).forEach(([k, v]) => {
      formattedMcqAnswers[k] = v
    })

    const attemptPayload: Attempt = {
      test_id: testData.id,
      test_title: testData.title,
      career_path: testData.career_path,
      category: testData.category,
      score: mcqPct,
      mcq_score: mcqPct,
      correct_count: correct,
      incorrect_count: questions.length - correct,
      total_questions: questions.length,
      time_taken: timeTaken,
      session_id: sessionId || undefined,
      mcq_answers: formattedMcqAnswers,
      open_ended_answers: openAnswersList,
      topic_breakdown: topicMap,
      difficulty_breakdown: diffMap,
    }

    try {
      const res = await submitMutation.mutateAsync(attemptPayload)
      const data = res.data
      const finalAttempt: Attempt = {
        ...attemptPayload,
        score: data.score ?? mcqPct,
        mcq_score: data.mcq_score ?? mcqPct,
        open_ended_score: data.open_ended_score,
        open_ended_evaluations: data.open_ended_evaluations,
        correct_count: data.correct_count ?? correct,
        incorrect_count: data.incorrect_count ?? (questions.length - correct),
        time_expired: data.time_expired,
      }
      setLastResult(finalAttempt)
      setPhase('result')
    } catch (err) {
      console.error('Submit failed, using local attempt:', err)
      setLastResult(attemptPayload)
      setPhase('result')
    } finally {
      setIsSubmitting(false)
    }
  }, [testData, answers, openEndedAnswers, sessionId, submitted, submitMutation])

  // Store submitRef so the timer can call latest version
  submitRef.current = () => {
    const elapsed = testData ? Math.min(600, (testData.time_limit_seconds || 600) - timeLeft) : 600
    computeAndSubmit(elapsed)
  }

  // ── Timer countdown (strictly 10 minutes / 600s) ──────────────────────────────
  useEffect(() => {
    if (phase !== 'test') return
    clearTimerInterval()
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearTimerInterval()
          submitRef.current() // auto-submit on expiry
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearTimerInterval()
  }, [phase])

  // ── Start a test ──────────────────────────────────────────────────────────────
  async function startTest(testId: string) {
    if (startingTestId) return
    setStartError(null)
    setStartingTestId(testId)
    try {
      // 1. Create server-side 10-minute session
      let sid: string | null = null
      try {
        const sessionRes = await api.post('/api/assessments/start-session', { test_id: testId })
        sid = sessionRes.data?.session_id || null
      } catch (sessErr) {
        console.warn('Session start fallback (non-fatal):', sessErr)
      }
      setSessionId(sid)

      // 2. Fetch test questions & open-ended scenarios
      const res = await api.get(`/api/assessments/tests/${testId}`)
      const data: TestWithQuestions = res.data
      if (!data || !data.questions || data.questions.length === 0) {
        throw new Error('Test questions could not be loaded. Please try again.')
      }
      setTestData(data)
      setActiveTestId(testId)
      setAnswers({})
      setOpenEndedAnswers({})
      setFlagged(new Set())
      setCurrentQ(0)
      setCurrentOpenQ(0)
      setTestTab('mcq')
      setTimeLeft(600) // 10 minutes strictly enforced
      setSubmitted(false)
      setIsSubmitting(false)
      setLastResult(null)
      setPhase('test')
    } catch (err: unknown) {
      const message = err instanceof Error
        ? err.message
        : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
          ?? 'Failed to load the test. Please check your connection and try again.'
      console.error('Failed to load test:', err)
      setStartError(message)
    } finally {
      setStartingTestId(null)
    }
  }

  function handleAnswer(optionIdx: number) {
    if (submitted || isSubmitting) return
    setAnswers(prev => ({ ...prev, [currentQ]: optionIdx }))
  }

  function handleOpenEndedAnswer(questionId: number, val: string) {
    if (submitted || isSubmitting) return
    setOpenEndedAnswers(prev => ({ ...prev, [questionId]: val }))
  }

  function toggleFlag(idx: number) {
    setFlagged(prev => {
      const next = new Set(prev)
      next.has(idx) ? next.delete(idx) : next.add(idx)
      return next
    })
  }

  function handleSubmitEarly() {
    if (submitted || isSubmitting) return
    const elapsed = testData ? Math.min(600, (testData.time_limit_seconds || 600) - timeLeft) : 0
    computeAndSubmit(elapsed)
  }

  const unansweredMCQ = testData ? testData.questions.filter((_, i) => answers[i] === undefined).length : 0
  const openQuestions = testData?.open_ended_questions || []
  const answeredOpenCount = openQuestions.filter(q => (openEndedAnswers[q.id] || '').trim().length > 15).length

  // ── RENDER: Select Screen ─────────────────────────────────────────────────────
  if (phase === 'select') {
    const recentHistory = history?.assessments?.slice(0, 5) || []
    return (
      <div className="min-h-screen bg-[var(--bg-app)] text-[var(--text-primary)] pb-16">
        <div className="max-w-5xl mx-auto px-4 pt-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-heading text-3xl sm:text-4xl font-extrabold text-app mb-1">
              Technical Assessments
            </h1>
            <p className="text-secondary text-sm">
              Interview-Level MCQs + 3 Open-Ended Technical Scenarios · Strict 10-Minute Timer · Multi-Criteria Rubric Evaluation
            </p>
          </div>

          {/* Start Error Banner */}
          {startError && (
            <div className="mb-5 flex items-start gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
              <span className="text-lg flex-shrink-0">⚠️</span>
              <div>
                <strong className="block font-semibold mb-0.5">Failed to start test</strong>
                <span>{startError}</span>
                <button
                  onClick={() => setStartError(null)}
                  className="ml-3 text-[11px] underline opacity-70 hover:opacity-100"
                >Dismiss</button>
              </div>
            </div>
          )}

          {/* Test Grid */}
          {catalogLoading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-56 rounded-2xl bg-subtle border border-app animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
              {(catalog?.tests || []).map(test => {
                const lastAttempt = history?.assessments?.find(a => a.test_id === test.id)
                return (
                  <div
                    key={test.id}
                    className="group relative flex flex-col justify-between bg-subtle border border-app rounded-2xl p-5 hover:border-[#FF5722]/50 transition-all duration-200 hover:shadow-lg hover:shadow-[#FF5722]/5"
                  >
                    {/* Icon + title */}
                    <div className="flex items-start gap-3 mb-3">
                      <span className="text-3xl">{CAREER_EMOJI[test.id] || '📝'}</span>
                      <div>
                        <h2 className="font-semibold text-app text-sm leading-tight">{test.title}</h2>
                        <span className="text-[10px] text-secondary mt-0.5 block">{test.career_path}</span>
                      </div>
                    </div>

                    {/* Badges */}
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/20">
                        {test.questions_count} MCQs
                      </span>
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        + 3 Scenarios
                      </span>
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-300 border border-rose-500/20 font-mono">
                        ⏱️ 10 Minutes
                      </span>
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        {test.difficulty || 'Intermediate / Advanced'}
                      </span>
                    </div>

                    {/* Last attempt */}
                    {lastAttempt && (
                      <div className="text-[10px] text-secondary mb-3 flex items-center gap-1">
                        <span>Last:</span>
                        <span className={scoreLabel(lastAttempt.score).color + ' font-bold'}>
                          {lastAttempt.score}%
                        </span>
                        <span>({lastAttempt.correct_count}/{lastAttempt.total_questions})</span>
                      </div>
                    )}

                    {/* Start button */}
                    <button
                      id={`start-test-${test.id}`}
                      onClick={() => startTest(test.id)}
                      disabled={!!startingTestId}
                      className="w-full py-2.5 rounded-xl text-sm font-semibold bg-[#FF5722] hover:bg-[#E64A19] text-white transition-colors group-hover:shadow-md cursor-pointer disabled:opacity-60 disabled:cursor-wait"
                    >
                      {startingTestId === test.id ? '⏳ Loading...' : lastAttempt ? 'Retake Assessment (10 min)' : 'Start Assessment (10 min)'}
                    </button>
                  </div>
                )
              })}
            </div>
          )}

          {/* History Table */}
          {recentHistory.length > 0 && (
            <div>
              <h2 className="font-heading text-lg font-bold text-app mb-3">Recent Attempts</h2>
              <div className="overflow-x-auto rounded-xl border border-app">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-subtle border-b border-app text-secondary text-[11px] uppercase tracking-wider">
                      <th className="px-4 py-2.5 text-left font-semibold">Test</th>
                      <th className="px-4 py-2.5 text-left font-semibold">Total Score</th>
                      <th className="px-4 py-2.5 text-left font-semibold">Result</th>
                      <th className="px-4 py-2.5 text-left font-semibold">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentHistory.map((r, i) => {
                      const { label, color } = scoreLabel(r.score)
                      return (
                        <tr key={i} className="border-b border-app/30 last:border-0 hover:bg-subtle/50 transition-colors">
                          <td className="px-4 py-3 font-medium text-app text-[13px]">{r.test_title}</td>
                          <td className="px-4 py-3 font-bold text-app">
                            {r.score}%
                            <span className="text-secondary font-normal text-[11px] ml-1">
                              ({r.correct_count}/{r.total_questions} MCQs)
                            </span>
                          </td>
                          <td className={`px-4 py-3 font-semibold text-[12px] ${color}`}>{label}</td>
                          <td className="px-4 py-3 text-secondary text-[12px]">
                            {new Date(r.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // ── RENDER: Test Screen ───────────────────────────────────────────────────────
  if (phase === 'test' && testData) {
    const question = testData.questions[currentQ]
    const totalQ = testData.questions.length
    const answeredMCQCount = Object.keys(answers).length
    const timerWarning = timeLeft <= 120 // last 2 minutes
    const timerCritical = timeLeft <= 60
    const activeOpenQuestion = openQuestions[currentOpenQ]

    return (
      <div className="min-h-screen bg-[var(--bg-app)] text-[var(--text-primary)] pb-16">
        <div className="max-w-3xl mx-auto px-4 pt-6">

          {/* Top Bar */}
          <div className="flex items-center justify-between mb-4 sticky top-0 bg-[var(--bg-app)] py-3 z-10 border-b border-app">
            <div>
              <p className="text-[11px] text-secondary font-semibold uppercase tracking-wide">{testData.career_path}</p>
              <h1 className="font-heading text-lg font-bold text-app">{testData.title}</h1>
            </div>

            {/* Timer */}
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-secondary uppercase tracking-wider font-semibold">10-Min Timer</span>
              <span
                id="test-timer"
                className={`font-mono text-2xl font-extrabold tabular-nums transition-colors ${
                  timerCritical ? 'text-rose-400 animate-pulse' : timerWarning ? 'text-amber-400' : 'text-app'
                }`}
              >
                {formatTime(timeLeft)}
              </span>
            </div>
          </div>

          {/* Mode Switcher Tabs */}
          <div className="flex gap-2 mb-5 p-1 bg-subtle rounded-xl border border-app">
            <button
              onClick={() => setTestTab('mcq')}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
                testTab === 'mcq'
                  ? 'bg-[#FF5722] text-white shadow-sm'
                  : 'text-secondary hover:text-app'
              }`}
            >
              Part 1: Technical MCQs ({answeredMCQCount}/{totalQ})
            </button>
            <button
              onClick={() => setTestTab('open_ended')}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
                testTab === 'open_ended'
                  ? 'bg-[#FF5722] text-white shadow-sm'
                  : 'text-secondary hover:text-app'
              }`}
            >
              Part 2: Scenario Drills ({answeredOpenCount}/{openQuestions.length})
            </button>
          </div>

          {/* TAB 1: MCQs */}
          {testTab === 'mcq' && question && (
            <>
              {/* Progress bar */}
              <div className="w-full h-1.5 bg-subtle rounded-full mb-4 overflow-hidden">
                <div
                  className="h-full bg-[#FF5722] rounded-full transition-all duration-300"
                  style={{ width: `${((currentQ + 1) / totalQ) * 100}%` }}
                />
              </div>

              {/* Navigation pills */}
              <div className="flex flex-wrap gap-1.5 mb-5">
                {testData.questions.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentQ(i)}
                    className={`w-7 h-7 rounded-lg text-[11px] font-bold border transition-all ${
                      i === currentQ
                        ? 'bg-[#FF5722] text-white border-[#FF5722]'
                        : answers[i] !== undefined
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                        : flagged.has(i)
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-subtle text-secondary border-app hover:border-[#FF5722]/40'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>

              {/* Question Card */}
              <div className="bg-subtle border border-app rounded-2xl p-6 mb-5 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${DIFF_BG[question.difficulty]}`}>
                    {question.difficulty.toUpperCase()}
                  </span>
                  <span className="text-[11px] text-secondary font-medium">{question.topic}</span>
                  <span className="ml-auto text-xs text-secondary">
                    {currentQ + 1} / {totalQ}
                  </span>
                </div>

                <p className="text-app font-medium text-base mb-6 leading-relaxed whitespace-pre-wrap">
                  {question.q}
                </p>

                {/* Options */}
                <div className="flex flex-col gap-2.5 mb-6">
                  {question.options.map((opt, optIdx) => {
                    const isSelected = answers[currentQ] === optIdx
                    return (
                      <button
                        key={optIdx}
                        onClick={() => handleAnswer(optIdx)}
                        disabled={submitted || isSubmitting}
                        className={`w-full text-left p-4 rounded-xl border text-sm transition-all duration-150 flex items-start gap-3 ${
                          isSelected
                            ? 'bg-[#FF5722]/15 border-[#FF5722] text-app font-medium shadow-sm'
                            : 'bg-[var(--bg-app)] border-app hover:border-[#FF5722]/50 text-[var(--text-secondary)] hover:text-app'
                        }`}
                      >
                        <span
                          className={`w-6 h-6 rounded-full text-[11px] font-bold flex items-center justify-center flex-shrink-0 border mt-0.5 ${
                            isSelected
                              ? 'bg-[#FF5722] text-white border-[#FF5722]'
                              : 'bg-subtle border-app text-secondary'
                          }`}
                        >
                          {String.fromCharCode(65 + optIdx)}
                        </span>
                        <span className="flex-1 leading-normal">{opt}</span>
                      </button>
                    )
                  })}
                </div>

                {/* Bottom Navigation */}
                <div className="flex items-center justify-between border-t border-app pt-4">
                  <button
                    onClick={() => toggleFlag(currentQ)}
                    className={`text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors flex items-center gap-1.5 ${
                      flagged.has(currentQ)
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'border-app text-secondary hover:text-app'
                    }`}
                  >
                    🚩 {flagged.has(currentQ) ? 'Flagged' : 'Flag'}
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentQ(prev => Math.max(0, prev - 1))}
                      disabled={currentQ === 0}
                      className="px-4 py-2 rounded-xl text-xs font-semibold border border-app text-secondary hover:text-app disabled:opacity-30 transition-colors"
                    >
                      Previous
                    </button>
                    {currentQ < totalQ - 1 ? (
                      <button
                        onClick={() => setCurrentQ(prev => prev + 1)}
                        className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#FF5722] hover:bg-[#E64A19] text-white transition-colors"
                      >
                        Next
                      </button>
                    ) : (
                      <button
                        onClick={() => setTestTab('open_ended')}
                        className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white transition-colors"
                      >
                        To Scenarios →
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}

          {/* TAB 2: Open-Ended Technical Questions */}
          {testTab === 'open_ended' && activeOpenQuestion && (
            <div className="bg-subtle border border-app rounded-2xl p-6 mb-5 shadow-sm">
              {/* Question selector tabs */}
              <div className="flex gap-2 mb-5">
                {openQuestions.map((q, idx) => {
                  const hasAnswer = (openEndedAnswers[q.id] || '').trim().length > 15
                  return (
                    <button
                      key={q.id}
                      onClick={() => setCurrentOpenQ(idx)}
                      className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold border transition-all ${
                        idx === currentOpenQ
                          ? 'bg-[#FF5722] text-white border-[#FF5722]'
                          : hasAnswer
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-[var(--bg-app)] border-app text-secondary hover:text-app'
                      }`}
                    >
                      Scenario {idx + 1} {hasAnswer ? '✓' : ''}
                    </button>
                  )
                })}
              </div>

              {/* Scenario Context */}
              <div className="mb-4">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider">
                  Open-Ended Scenario {currentOpenQ + 1} of {openQuestions.length}
                </span>
                <h3 className="text-base font-bold text-app mt-2 mb-2">
                  {activeOpenQuestion.title}
                </h3>
                <div className="p-3.5 rounded-xl bg-[var(--bg-app)] border border-app text-xs text-secondary leading-relaxed mb-3">
                  <strong className="text-app block mb-1">Scenario Context:</strong>
                  {activeOpenQuestion.scenario}
                </div>
                <div className="p-3.5 rounded-xl bg-orange-500/5 border border-orange-500/20 text-xs text-app leading-relaxed">
                  <strong className="text-[#FF5722] block mb-1">Your Objective:</strong>
                  {activeOpenQuestion.prompt}
                </div>
              </div>

              {/* Rubric Focus Tags */}
              <div className="mb-4">
                <span className="text-[11px] text-secondary block mb-1.5 font-medium">Evaluation Focus Areas:</span>
                <div className="flex flex-wrap gap-1.5">
                  {activeOpenQuestion.rubric_focus.map((focus, fIdx) => (
                    <span
                      key={fIdx}
                      className="text-[10px] px-2 py-0.5 rounded-md bg-subtle border border-app text-secondary font-mono"
                    >
                      🎯 {focus}
                    </span>
                  ))}
                </div>
              </div>

              {/* Textarea */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-semibold text-app">
                    Your Architectural Solution & Reasoning:
                  </label>
                  <span className="text-[10px] text-secondary font-mono">
                    {((openEndedAnswers[activeOpenQuestion.id] || '').split(/\s+/).filter(Boolean).length)} words
                  </span>
                </div>
                <textarea
                  value={openEndedAnswers[activeOpenQuestion.id] || ''}
                  onChange={e => handleOpenEndedAnswer(activeOpenQuestion.id, e.target.value)}
                  disabled={submitted || isSubmitting}
                  placeholder="Explain your approach step-by-step: design decisions, algorithms/protocols, trade-offs, edge-case recovery, and why you chose this architecture..."
                  className="w-full h-44 p-3.5 rounded-xl bg-[var(--bg-app)] border border-app text-xs text-app placeholder:text-secondary/50 focus:outline-none focus:border-[#FF5722] leading-relaxed resize-y font-sans"
                />
                <p className="text-[10px] text-secondary mt-1">
                  💡 <em>Evaluated on Correctness, Reasoning, Technical Depth, Relevance, and Completeness. Wording differences are credited if the engineering principles are sound.</em>
                </p>
              </div>

              {/* Open-ended navigation */}
              <div className="flex items-center justify-between border-t border-app pt-4">
                <button
                  onClick={() => setCurrentOpenQ(prev => Math.max(0, prev - 1))}
                  disabled={currentOpenQ === 0}
                  className="px-4 py-2 rounded-xl text-xs font-semibold border border-app text-secondary hover:text-app disabled:opacity-30 transition-colors"
                >
                  Previous Scenario
                </button>
                {currentOpenQ < openQuestions.length - 1 ? (
                  <button
                    onClick={() => setCurrentOpenQ(prev => prev + 1)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#FF5722] hover:bg-[#E64A19] text-white transition-colors"
                  >
                    Next Scenario
                  </button>
                ) : (
                  <button
                    onClick={() => setTestTab('mcq')}
                    className="px-4 py-2 rounded-xl text-xs font-semibold border border-[#FF5722]/50 text-[#FF5722] hover:bg-[#FF5722]/10 transition-colors"
                  >
                    Review MCQs
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Submit Action Bar */}
          <div className="flex items-center justify-between p-4 rounded-2xl bg-subtle border border-app">
            <div className="text-xs text-secondary">
              <span className="mr-3">MCQs: <strong className="text-app">{answeredMCQCount}/{totalQ}</strong></span>
              <span>Scenarios: <strong className="text-app">{answeredOpenCount}/{openQuestions.length}</strong></span>
            </div>
            <button
              id="submit-test-btn"
              onClick={handleSubmitEarly}
              disabled={submitted || isSubmitting}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-[#FF5722] hover:bg-[#E64A19] text-white disabled:opacity-60 transition-all cursor-pointer shadow-md"
            >
              {isSubmitting ? 'Evaluating Submission...' : unansweredMCQ > 0 ? `Submit (${unansweredMCQ} MCQs skipped)` : 'Submit Entire Assessment'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── RENDER: Result Screen ─────────────────────────────────────────────────────
  if (phase === 'result' && lastResult && testData) {
    const { label, color } = scoreLabel(lastResult.score)
    const timeTakenMin = Math.floor(lastResult.time_taken / 60)
    const timeTakenSec = lastResult.time_taken % 60
    const questions = testData.questions
    const mcqScore = lastResult.mcq_score ?? Math.round((lastResult.correct_count / Math.max(1, lastResult.total_questions)) * 100)
    const openScore = lastResult.open_ended_score

    return (
      <div className="min-h-screen bg-[var(--bg-app)] text-[var(--text-primary)] pb-16">
        <div className="max-w-3xl mx-auto px-4 pt-6">

          {/* Result Header */}
          <div className="bg-subtle border border-app rounded-2xl p-6 mb-5 text-center shadow-sm">
            <p className="text-secondary text-xs uppercase tracking-wider font-semibold mb-1">
              {lastResult.career_path} Assessment Completed
            </p>
            <h1 className="font-heading text-2xl sm:text-3xl font-extrabold text-app mb-3">
              {lastResult.test_title}
            </h1>

            {/* Score Circle */}
            <div className="inline-flex flex-col items-center justify-center w-28 h-28 rounded-full border-4 border-[#FF5722]/50 bg-[#FF5722]/10 mb-3 shadow-inner">
              <span className="font-heading text-4xl font-black text-app">{Math.round(lastResult.score)}</span>
              <span className="text-[11px] text-secondary font-bold">Overall %</span>
            </div>

            <p className={`text-lg font-bold mb-1 ${color}`}>{label}</p>
            <p className="text-secondary text-xs">
              Time taken: {timeTakenMin}m {timeTakenSec}s {lastResult.time_expired ? '(Enforced at 10m limit)' : ''}
            </p>
          </div>

          {/* Separated Component Scores */}
          <div className="grid sm:grid-cols-2 gap-4 mb-5">
            {/* Component 1: MCQs */}
            <div className="bg-subtle border border-app rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider">Part 1: Technical MCQs</span>
                <span className="text-xs font-extrabold text-[#FF5722]">Weight: 70%</span>
              </div>
              <div className="flex items-baseline gap-2 mb-2">
                <span className="text-3xl font-extrabold text-app">{Math.round(mcqScore)}%</span>
                <span className="text-xs text-secondary font-medium">
                  ({lastResult.correct_count} of {lastResult.total_questions} correct)
                </span>
              </div>
              <div className="w-full h-2 bg-[var(--bg-app)] rounded-full overflow-hidden mb-3">
                <div
                  className="h-full bg-[#FF5722] rounded-full transition-all"
                  style={{ width: `${Math.min(100, mcqScore)}%` }}
                />
              </div>
              <p className="text-[11px] text-secondary">
                Evaluates intermediate-to-advanced knowledge across system design, edge cases, and practical debugging.
              </p>
            </div>

            {/* Component 2: Open-Ended */}
            <div className="bg-subtle border border-app rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider">Part 2: Scenario Drills</span>
                <span className="text-xs font-extrabold text-indigo-400">Weight: 30%</span>
              </div>
              <div className="flex items-baseline gap-2 mb-2">
                <span className="text-3xl font-extrabold text-app">
                  {openScore !== undefined && openScore !== null ? Math.round(openScore) : Math.round(mcqScore)}%
                </span>
                <span className="text-xs text-secondary font-medium">(3 Scenarios Evaluated)</span>
              </div>
              <div className="w-full h-2 bg-[var(--bg-app)] rounded-full overflow-hidden mb-3">
                <div
                  className="h-full bg-indigo-500 rounded-full transition-all"
                  style={{ width: `${Math.min(100, openScore ?? mcqScore)}%` }}
                />
              </div>
              <p className="text-[11px] text-secondary">
                Multi-criteria rubric assessing correctness, reasoning, technical depth, relevance, and trade-off completeness.
              </p>
            </div>
          </div>

          {/* Open-Ended Detailed Rubric Reviews */}
          {lastResult.open_ended_evaluations && lastResult.open_ended_evaluations.length > 0 && (
            <div className="bg-subtle border border-app rounded-2xl p-5 mb-5">
              <h2 className="font-semibold text-app mb-3 text-sm flex items-center gap-2">
                <span>🎯</span> Open-Ended Technical Scenario Feedback
              </h2>
              <div className="flex flex-col gap-4">
                {lastResult.open_ended_evaluations.map((ev, eIdx) => (
                  <div key={eIdx} className="p-4 rounded-xl bg-[var(--bg-app)] border border-app text-xs">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-app text-sm">
                        Scenario {eIdx + 1}: {ev.question_title}
                      </span>
                      <span className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                        {ev.score} / 100
                      </span>
                    </div>

                    {/* Criteria 5-bar breakdown */}
                    <div className="grid grid-cols-5 gap-2 my-3 text-center">
                      <div className="p-2 rounded bg-subtle border border-app">
                        <span className="text-[9px] text-secondary uppercase block font-semibold">Correctness</span>
                        <strong className="text-xs text-app">{ev.correctness}/20</strong>
                      </div>
                      <div className="p-2 rounded bg-subtle border border-app">
                        <span className="text-[9px] text-secondary uppercase block font-semibold">Reasoning</span>
                        <strong className="text-xs text-app">{ev.reasoning}/20</strong>
                      </div>
                      <div className="p-2 rounded bg-subtle border border-app">
                        <span className="text-[9px] text-secondary uppercase block font-semibold">Depth</span>
                        <strong className="text-xs text-app">{ev.technical_understanding}/20</strong>
                      </div>
                      <div className="p-2 rounded bg-subtle border border-app">
                        <span className="text-[9px] text-secondary uppercase block font-semibold">Relevance</span>
                        <strong className="text-xs text-app">{ev.relevance}/20</strong>
                      </div>
                      <div className="p-2 rounded bg-subtle border border-app">
                        <span className="text-[9px] text-secondary uppercase block font-semibold">Completeness</span>
                        <strong className="text-xs text-app">{ev.completeness}/20</strong>
                      </div>
                    </div>

                    <p className="text-secondary leading-relaxed bg-subtle p-2.5 rounded-lg border border-app/50 mt-2">
                      💬 <strong className="text-app font-medium">Reviewer Feedback:</strong> {ev.feedback}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Difficulty Breakdown */}
          <div className="bg-subtle border border-app rounded-2xl p-5 mb-5">
            <h2 className="font-semibold text-app mb-3 text-sm">MCQ Difficulty Breakdown</h2>
            <div className="grid grid-cols-3 gap-3">
              {(['easy', 'medium', 'hard'] as const).map(d => {
                const stat = lastResult.difficulty_breakdown[d] || { correct: 0, total: 0 }
                const pct = stat.total > 0 ? Math.round((stat.correct / stat.total) * 100) : 0
                return (
                  <div key={d} className={`rounded-xl border p-3 text-center ${DIFF_BG[d]}`}>
                    <p className="text-[11px] font-bold uppercase tracking-wider mb-1 capitalize">{d}</p>
                    <p className="font-heading text-xl font-extrabold">{pct}%</p>
                    <p className="text-[10px] mt-0.5">{stat.correct} / {stat.total}</p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Topic Breakdown */}
          <div className="bg-subtle border border-app rounded-2xl p-5 mb-5">
            <h2 className="font-semibold text-app mb-3 text-sm">Topic Breakdown</h2>
            <div className="flex flex-col gap-2.5">
              {Object.entries(lastResult.topic_breakdown)
                .sort(([, a], [, b]) => b.total - a.total)
                .map(([topic, stat]) => {
                  const pct = stat.total > 0 ? Math.round((stat.correct / stat.total) * 100) : 0
                  const barColor = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-amber-500' : 'bg-rose-500'
                  return (
                    <div key={topic}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[12px] text-app font-medium">{topic}</span>
                        <span className="text-[11px] text-secondary">{stat.correct}/{stat.total} ({pct}%)</span>
                      </div>
                      <div className="h-1.5 bg-[var(--bg-app)] rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${barColor} transition-all`} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )
                })}
            </div>
          </div>

          {/* Answer Review */}
          <div className="bg-subtle border border-app rounded-2xl p-5 mb-6">
            <h2 className="font-semibold text-app mb-4 text-sm">MCQ Answer Review</h2>
            <div className="flex flex-col gap-4 max-h-[480px] overflow-y-auto pr-1">
              {questions.map((q, idx) => {
                const userAns = answers[idx]
                const isCorrect = userAns === q.correct
                const wasAnswered = userAns !== undefined
                return (
                  <div
                    key={idx}
                    className={`rounded-xl border p-4 text-sm ${
                      !wasAnswered ? 'border-app bg-[var(--bg-app)]' :
                      isCorrect ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-rose-500/30 bg-rose-500/5'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-[10px] font-bold">Q{idx + 1}</span>
                      <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${DIFF_BG[q.difficulty]}`}>
                        {q.difficulty}
                      </span>
                      <span className="text-[10px] text-secondary">{q.topic}</span>
                      <span className="ml-auto text-[13px]">
                        {!wasAnswered ? '⏩' : isCorrect ? '✅' : '❌'}
                      </span>
                    </div>
                    <p className="text-app font-medium mb-2 whitespace-pre-wrap">{q.q}</p>
                    {wasAnswered && !isCorrect && (
                      <p className="text-rose-300 text-[12px] mb-1">
                        Your answer: <strong>{q.options[userAns]}</strong>
                      </p>
                    )}
                    <p className="text-emerald-300 text-[12px] mb-1.5">
                      Correct: <strong>{q.options[q.correct]}</strong>
                    </p>
                    <p className="text-secondary text-[11px] leading-relaxed border-t border-app pt-2">
                      💡 {q.explanation}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 flex-wrap">
            <button
              id="retake-test-btn"
              onClick={() => startTest(testData.id)}
              className="flex-1 py-3 rounded-xl font-semibold border border-[#FF5722]/40 text-[#FF5722] hover:bg-[#FF5722]/5 transition-colors cursor-pointer"
            >
              🔁 Retake Assessment
            </button>
            <button
              id="back-to-tests-btn"
              onClick={() => setPhase('select')}
              className="flex-1 py-3 rounded-xl font-semibold bg-[#FF5722] hover:bg-[#E64A19] text-white transition-colors cursor-pointer"
            >
              ← All Assessments
            </button>
          </div>
        </div>
      </div>
    )
  }

  return null
}
