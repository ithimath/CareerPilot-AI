import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  FileText, CheckCircle2, AlertTriangle,
  Search, Check, X, ShieldCheck
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function ResumePage() {
  const [resumeText, setResumeText] = useState('')
  const [targetRole, setTargetRole] = useState('Full-Stack Engineer')
  const [analysis, setAnalysis] = useState<any>(null)

  const analyzeMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/resume/analyze-ats', {
        resume_text: resumeText,
        target_role: targetRole,
      })
      return res.data
    },
    onSuccess: (data) => {
      setAnalysis(data)
      toast.success('ATS Diagnostic Analysis Complete!')
    },
    onError: (err: any) => {
      toast.error(err.message || 'Failed to analyze resume')
    }
  })

  return (
    <div className="space-y-6 animate-fade-in text-app">
      {/* Header */}
      <div className="card p-6 shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-1">Recruiter ATS Parser Compliance</span>
          <h2 className="font-heading text-3xl font-extrabold text-app">Resume ATS Diagnostic Scanner</h2>
          <p className="text-secondary text-xs mt-1 font-medium">Upload developer resume content for keyword density audit and structural parser compliance</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Column: Form & Input */}
        <div className="lg:col-span-5 space-y-4">
          <div className="card p-5 space-y-4">
            <div>
              <label className="text-xs font-bold text-secondary uppercase tracking-wider block mb-1.5">
                Target Role Benchmark
              </label>
              <input
                className="input"
                placeholder="e.g. Full-Stack Engineer, Data Scientist, Product Manager"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-secondary uppercase tracking-wider block">
                  Raw Resume Content
                </label>
                <button
                  onClick={() => {
                    setTargetRole('Full-Stack Engineer')
                    setResumeText(
                      `ALEX MORGAN
Email: alex.morgan@student.edu | Phone: (555) 019-2834 | Portfolio: alexmorgan.dev

PROFESSIONAL SUMMARY
Motivated Full-Stack Engineering candidate with expertise in React, TypeScript, Python, and SQL. Seeking software engineering roles.

SKILLS
- Frontend: React, TypeScript, JavaScript (ES6+), HTML5/CSS3, State Management
- Backend: Python, Node.js, Express, REST APIs, SQL, PostgreSQL
- Tools & DevOps: Git, GitHub, Docker, VS Code

WORK EXPERIENCE
Frontend Developer Intern | TechCorp (June 2025 - August 2025)
- Developed responsive user interfaces using React and TypeScript for cloud management dashboard.
- Reduced initial page load times by 25% by optimizing bundle sizes and implementing lazy loading.
- Collaborated with backend team to integrate RESTful API endpoints.

PROJECTS
Full-Stack AI Career Platform | React, TypeScript, FastAPI
- Built a career platform featuring job readiness scoring, ATS resume analysis, and interview simulations.`
                    )
                  }}
                  className="text-[11px] font-bold text-teal-700 dark:text-teal-400 hover:underline"
                >
                  ⚡ Auto-Fill Sample Resume
                </button>
              </div>
              <textarea
                className="input h-64 font-mono text-xs leading-relaxed"
                placeholder="Paste raw plain text from your resume here..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
              />
            </div>

            <button
              onClick={() => analyzeMutation.mutate()}
              disabled={analyzeMutation.isPending}
              className="btn btn-primary w-full justify-center gap-2 py-2.5"
            >
              {analyzeMutation.isPending ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Auditing Parser Standards...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 text-white" /> Execute ATS Parser Audit
                </>
              )}
            </button>
          </div>

          {/* Guidelines */}
          <div className="card p-5 space-y-2 bg-subtle">
            <h4 className="font-heading text-sm font-bold text-app flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-teal-700 dark:text-teal-400" /> ATS Screening Compliance Rules
            </h4>
            <ul className="text-xs text-secondary font-medium space-y-1.5 list-disc pl-4">
              <li>Use standard headers: Professional Summary, Experience, Skills, Education.</li>
              <li>Match exact target keywords from job description requisitions.</li>
              <li>Quantify metrics (% performance increase, latency reduction, user count).</li>
              <li>Avoid complex tables or unsupported graphical elements.</li>
            </ul>
          </div>
        </div>

        {/* Right Column: ATS Report Output */}
        <div className="lg:col-span-7">
          {analysis ? (
            <div className="space-y-4 animate-fade-in">
              {/* ATS Rating Header */}
              <div className="card p-6 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block">Audited Match Rating</span>
                  <h3 className="font-heading text-xl font-bold text-app">ATS Requisition Score</h3>
                </div>
                <div className="text-right">
                  <span className="font-heading text-3xl font-extrabold text-app">{analysis.score}</span>
                  <span className="text-xs font-bold text-secondary"> / 100</span>
                </div>
              </div>

              {/* Keyword Analysis Grid */}
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(analysis.keyword_analysis || {}).map(([key, val]: any) => (
                  <div key={key} className="card p-3 text-center">
                    <p className="text-[10px] font-bold text-secondary uppercase">{key}</p>
                    <p className="font-heading text-lg font-bold text-app mt-0.5">{val.score}%</p>
                  </div>
                ))}
              </div>

              {/* Detected Keywords */}
              <div className="card p-5 space-y-3">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Target Keywords Detected</span>
                <div className="flex flex-wrap gap-1.5">
                  {analysis.matching_keywords?.map((kw: string) => (
                    <span key={kw} className="badge badge-emerald flex items-center gap-1">
                      <Check className="w-3 h-3 text-teal-700 dark:text-teal-400" /> {kw}
                    </span>
                  ))}
                  {analysis.missing_keywords?.map((kw: string) => (
                    <span key={kw} className="badge badge-red flex items-center gap-1">
                      <X className="w-3 h-3 text-red-600 dark:text-red-400" /> {kw}
                    </span>
                  ))}
                </div>
              </div>

              {/* Structural Compliance Checklist */}
              <div className="card p-5 space-y-2">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Structural Section Compliance</span>
                {Object.entries(analysis.structure_checks || {}).map(([section, present]: any) => (
                  <div key={section} className="flex items-center justify-between text-xs py-1 border-b border-app">
                    <span className="capitalize font-bold text-app">{section} Section</span>
                    {present ? (
                      <span className="badge badge-emerald flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-teal-700 dark:text-teal-400" /> Detected</span>
                    ) : (
                      <span className="badge badge-amber flex items-center gap-1"><AlertTriangle className="w-3 h-3 text-amber-600 dark:text-amber-400" /> Missing</span>
                    )}
                  </div>
                ))}
              </div>

              {/* Improvement Recommendations */}
              <div className="card p-5 space-y-2">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Formatting Recommendations</span>
                <ul className="text-xs text-secondary font-medium space-y-1.5 list-disc pl-4">
                  {analysis.recommendations?.map((rec: string, idx: number) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="card p-12 flex flex-col items-center justify-center text-center h-full min-h-[380px]">
              <FileText className="w-8 h-8 text-secondary mb-3" />
              <h3 className="font-heading text-xl font-bold text-app">ATS Scanner Ready</h3>
              <p className="text-xs text-secondary font-medium mt-1 max-w-xs">
                Paste your developer resume on the left and click &quot;Execute ATS Parser Audit&quot; to review keyword match analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
