import { useState } from 'react'
import { FileCode, CheckCircle2, XCircle, Clock, ArrowRight, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

const MOCK_TESTS = [
  {
    id: 'dsa',
    title: 'Data Structures & Algorithms Core Assessment',
    category: 'Algorithms',
    questionsCount: 5,
    timeLimit: '20 mins',
    difficulty: 'Hard',
    questions: [
      {
        id: 1,
        q: 'Which data structure offers average O(1) time complexity for lookup, insert, and delete operations?',
        options: ['Binary Search Tree', 'Hash Table / Map', 'Linked List', 'Max Heap'],
        correct: 1,
        explanation: 'Hash tables leverage a hash function to map keys to bucket indices, yielding O(1) average time complexity.'
      },
      {
        id: 2,
        q: 'What is the time complexity of Breadth-First Search (BFS) on a graph with V vertices and E edges?',
        options: ['O(V * E)', 'O(V + E)', 'O(V^2)', 'O(log V)'],
        correct: 1,
        explanation: 'BFS visits every vertex once and explores every edge once, taking O(V + E) time.'
      },
      {
        id: 3,
        q: 'What is the primary advantage of a Red-Black Tree over a standard Binary Search Tree?',
        options: ['O(1) search time', 'Guaranteed O(log N) height balancing', 'Requires 50% less memory', 'Faster array allocation'],
        correct: 1,
        explanation: 'Red-Black Trees automatically rebalance during insertions/deletions, preventing worst-case O(N) degradation.'
      }
    ]
  },
  {
    id: 'react-arch',
    title: 'React.js & Architecture Benchmark',
    category: 'Frontend',
    questionsCount: 4,
    timeLimit: '15 mins',
    difficulty: 'Medium',
    questions: [
      {
        id: 1,
        q: 'What triggers a re-render in a React functional component?',
        options: ['Changes in state, props, or parent context', 'Calling a helper utility function', 'Mutating a regular let variable', 'Inspecting DOM nodes'],
        correct: 0,
        explanation: 'React components re-render whenever state updates (useState), prop values change, or parent context values mutate.'
      },
      {
        id: 2,
        q: 'What is the primary purpose of the useMemo hook?',
        options: ['To create side effects on mount', 'To memoize expensive calculations between renders', 'To replace Redux store', 'To lazy load components'],
        correct: 1,
        explanation: 'useMemo caches the result of a calculation between renders unless dependencies change.'
      }
    ]
  },
  {
    id: 'sql-db',
    title: 'SQL Performance & Database Design Drill',
    category: 'Database',
    questionsCount: 4,
    timeLimit: '15 mins',
    difficulty: 'Medium',
    questions: [
      {
        id: 1,
        q: 'Which SQL clause is used to filter aggregate query results (e.g. after GROUP BY)?',
        options: ['WHERE', 'HAVING', 'ORDER BY', 'FILTER BY'],
        correct: 1,
        explanation: 'WHERE filters rows before aggregation, while HAVING filters aggregated groups after GROUP BY execution.'
      }
    ]
  }
]

export default function MockTestsPage() {
  const [selectedTest, setSelectedTest] = useState<any>(null)
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [submitted, setSubmitted] = useState(false)

  const handleSelectOption = (qIdx: number, optIdx: number) => {
    if (submitted) return
    setAnswers(prev => ({ ...prev, [qIdx]: optIdx }))
  }

  const handleSubmit = () => {
    setSubmitted(true)
    toast.success('Mock Test Submitted! Performance score calculated.')
  }

  const resetTest = () => {
    setSelectedTest(null)
    setCurrentQ(0)
    setAnswers({})
    setSubmitted(false)
  }

  const calculateScore = () => {
    if (!selectedTest) return 0
    let correctCount = 0
    selectedTest.questions.forEach((q: any, idx: number) => {
      if (answers[idx] === q.correct) correctCount++
    })
    return Math.round((correctCount / selectedTest.questions.length) * 100)
  }

  return (
    <div className="space-y-6 text-app">
      {/* Header Banner */}
      <div className="card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-1">Technical Readiness Verification</span>
          <div className="flex items-center gap-3">
            <h2 className="font-heading text-3xl font-extrabold text-app">Technical Mock Test Drills</h2>
            <span className="badge badge-emerald flex items-center gap-1">
              <FileCode className="w-3 h-3 text-teal-700 dark:text-teal-400" /> Timed Drills
            </span>
          </div>
          <p className="text-secondary text-xs mt-1 font-medium">
            Test domain concept retention under real recruiter time constraints.
          </p>
        </div>
      </div>

      {!selectedTest ? (
        /* Test Selection Cards */
        <div className="grid md:grid-cols-3 gap-4">
          {MOCK_TESTS.map((test) => (
            <div key={test.id} className="card p-5 space-y-4 flex flex-col justify-between hover:border-teal-700/50 transition-all">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="badge badge-sand text-[10px]">{test.category}</span>
                  <span className={`badge ${test.difficulty === 'Hard' ? 'badge-red' : 'badge-amber'}`}>{test.difficulty}</span>
                </div>
                <h3 className="font-heading text-lg font-bold text-app">{test.title}</h3>
                <div className="flex items-center gap-4 text-xs font-semibold text-secondary mt-3">
                  <span className="flex items-center gap-1"><FileCode className="w-3.5 h-3.5" /> {test.questionsCount} Prompts</span>
                  <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {test.timeLimit}</span>
                </div>
              </div>

              <button
                onClick={() => { setSelectedTest(test); setCurrentQ(0); setAnswers({}); setSubmitted(false) }}
                className="btn btn-primary text-xs w-full justify-center gap-2"
              >
                Start Drill <ArrowRight className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
          ))}
        </div>
      ) : (
        /* Active Test Interface */
        <div className="max-w-3xl mx-auto space-y-4">
          <div className="flex items-center justify-between">
            <button onClick={resetTest} className="text-xs font-bold text-teal-700 dark:text-teal-400 hover:underline">
              ← Back to Test Catalog
            </button>
            <span className="badge badge-emerald">
              {selectedTest.title}
            </span>
          </div>

          <div className="card p-6 space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-app">
              <span className="text-xs font-bold text-secondary">
                Question {currentQ + 1} of {selectedTest.questions.length}
              </span>
              {submitted && (
                <span className="font-heading text-lg font-bold text-teal-700 dark:text-teal-400">
                  Score: {calculateScore()}%
                </span>
              )}
            </div>

            {/* Question Prompt */}
            <div>
              <h3 className="font-heading text-lg font-bold text-app mb-4">
                {selectedTest.questions[currentQ].q}
              </h3>

              <div className="space-y-2.5">
                {selectedTest.questions[currentQ].options.map((opt: string, optIdx: number) => {
                  const isSelected = answers[currentQ] === optIdx
                  const isCorrect = selectedTest.questions[currentQ].correct === optIdx

                  let btnStyle = 'border-app bg-surface text-app hover:bg-subtle font-medium'
                  if (submitted) {
                    if (isCorrect) btnStyle = 'border-teal-600 bg-teal-50 text-teal-950 font-bold dark:bg-teal-950/50 dark:text-teal-200'
                    else if (isSelected && !isCorrect) btnStyle = 'border-red-500 bg-red-50 text-red-950 font-bold dark:bg-red-950/50 dark:text-red-200'
                  } else if (isSelected) {
                    btnStyle = 'border-teal-700 bg-teal-50 text-teal-950 font-bold dark:bg-teal-950/40 dark:text-teal-200'
                  }

                  return (
                    <button
                      key={optIdx}
                      onClick={() => handleSelectOption(currentQ, optIdx)}
                      className={`w-full p-3.5 border rounded-md text-left text-xs transition-all flex items-center justify-between ${btnStyle}`}
                    >
                      <span>{opt}</span>
                      {submitted && isCorrect && <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0" />}
                      {submitted && isSelected && !isCorrect && <XCircle className="w-4 h-4 text-red-600 flex-shrink-0" />}
                    </button>
                  )
                })}
              </div>

              {submitted && (
                <div className="mt-4 p-3.5 bg-subtle border border-app rounded-md text-xs text-secondary leading-relaxed font-medium">
                  <strong className="text-app block mb-0.5">Explanation:</strong>
                  {selectedTest.questions[currentQ].explanation}
                </div>
              )}
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between pt-4 border-t border-app">
              <button
                onClick={() => setCurrentQ(prev => Math.max(0, prev - 1))}
                disabled={currentQ === 0}
                className="btn btn-secondary text-xs"
              >
                Previous
              </button>

              {currentQ < selectedTest.questions.length - 1 ? (
                <button
                  onClick={() => setCurrentQ(prev => prev + 1)}
                  className="btn btn-secondary text-xs"
                >
                  Next Prompt →
                </button>
              ) : !submitted ? (
                <button onClick={handleSubmit} className="btn btn-primary text-xs">
                  Submit Mock Test
                </button>
              ) : (
                <button onClick={resetTest} className="btn btn-primary text-xs gap-1.5">
                  <RefreshCw className="w-3.5 h-3.5" /> Retake Test
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
