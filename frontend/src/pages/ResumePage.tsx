import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  FileText, CheckCircle2, AlertTriangle,
  Search, Check, X, ShieldCheck, Sparkles, Award, Upload, FileCode
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function ResumePage() {
  const queryClient = useQueryClient()
  const [resumeText, setResumeText] = useState('')
  const [targetRole, setTargetRole] = useState('Full-Stack Engineer')
  const [analysis, setAnalysis] = useState<any>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const analyzeMutation = useMutation({
    mutationFn: async () => {
      if (selectedFile) {
        const formData = new FormData()
        formData.append('file', selectedFile)
        formData.append('target_role', targetRole)
        const res = await api.post('/api/resume/upload-ats', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        return res.data
      } else {
        const res = await api.post('/api/resume/analyze-ats', {
          resume_text: resumeText,
          target_role: targetRole,
        })
        return res.data
      }
    },
    onSuccess: (data) => {
      setAnalysis(data)
      // exact:false ensures Dashboard's ['jobScore', uid] key is also invalidated
      queryClient.invalidateQueries({ queryKey: ['jobScore'], exact: false })
      toast.success(`ATS Audit Complete! Match score: ${data.score || data.ats_score}%`)
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || err.message || 'Failed to analyze resume')
    }
  })

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setSelectedFile(file)
      toast.success(`File attached: ${file.name}`)
    }
  }

  const matchedKeywords = analysis?.matching_keywords || analysis?.matched_keywords || []
  const missingKeywords = analysis?.missing_keywords || []
  const additionalSkills = analysis?.additional_relevant_skills || []
  const skillDetails = analysis?.skill_match_details
  const evidenceDetails = analysis?.skill_evidence_details || []
  const weightedBreakdown = analysis?.weighted_breakdown || {}
  const recommendations = analysis?.recommendations || analysis?.improvements || []
  const strengths = analysis?.strengths || []

  return (
    <div className="space-y-6 animate-fade-in text-app">
      {/* Header */}
      <div className="card p-6 shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block mb-1">Enterprise ATS Parser Compliance</span>
          <h2 className="font-heading text-3xl font-extrabold text-app">Resume ATS Diagnostic & Evidence Analyzer</h2>
          <p className="text-secondary text-xs mt-1 font-medium">Upload PDF/DOCX or paste raw text for case-insensitive skill normalization, evidence weighting, and explainable scoring</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Column: Input Controls */}
        <div className="lg:col-span-5 space-y-4">
          <div className="card p-5 space-y-4">
            <div>
              <label className="text-xs font-bold text-secondary uppercase tracking-wider block mb-1.5">
                Target Role Requisition
              </label>
              <input
                className="input"
                placeholder="e.g. Full-Stack Engineer, Data Scientist, DevOps Engineer"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
              />
            </div>

            {/* Document File Upload */}
            <div>
              <label className="text-xs font-bold text-secondary uppercase tracking-wider block mb-1.5">
                Upload Resume Document (PDF / DOCX / TXT)
              </label>
              <label className="border-2 border-dashed border-app rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:border-[#FF5722] transition-colors bg-subtle">
                <Upload className="w-6 h-6 text-secondary mb-1" />
                <span className="text-xs font-bold text-app">
                  {selectedFile ? selectedFile.name : 'Click to select PDF, DOCX, or TXT file'}
                </span>
                <span className="text-[10px] text-secondary mt-0.5">Supports mixed-case, lowercase, or uppercase resumes</span>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                  onChange={handleFileUpload}
                />
              </label>

              {selectedFile && (
                <div className="flex items-center justify-between text-xs mt-1.5 px-1 text-secondary">
                  <span>Attached: <strong>{selectedFile.name}</strong></span>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-red-500 font-bold hover:underline text-[11px]"
                  >
                    Remove File
                  </button>
                </div>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-secondary uppercase tracking-wider block">
                  Or Paste Raw Resume Content
                </label>
                <button
                  onClick={() => {
                    setSelectedFile(null)
                    setTargetRole('Full-Stack Engineer')
                    setResumeText(
                      `ALEX MORGAN
Email: alex.morgan@student.edu | Phone: (555) 019-2834 | Portfolio: alexmorgan.dev

PROFESSIONAL SUMMARY
Motivated Full-Stack Engineering candidate with expertise in react.js, type script, python, nodejs, rest apis, and postgres.

SKILLS
- Frontend: react.js, type script, java script, HTML5/CSS3
- Backend: python, nodejs, FastAPI, REST APIs, SQL, postgresql
- Tools & DevOps: Git, GitHub, Docker, VS Code

WORK EXPERIENCE
Frontend Developer Intern | TechCorp (June 2025 - August 2025)
- Developed responsive user interfaces using react and typescript for cloud management dashboard.
- Reduced initial page load times by 25% by optimizing bundle sizes.

PROJECTS
Full-Stack AI Career Platform | React, TypeScript, FastAPI
- Built a high throughput microservice using FastAPI, Docker, and PostgreSQL scaling to 100k active users.`
                    )
                  }}
                  className="text-[11px] font-bold text-[#FF5722] dark:text-[#FF7043] hover:underline"
                >
                  ⚡ Auto-Fill Sample Resume
                </button>
              </div>
              <textarea
                className="input h-52 font-mono text-xs leading-relaxed"
                placeholder="Paste raw plain text from your resume here..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                disabled={!!selectedFile}
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
                  Running Contextual Audit Engine...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 text-white" /> Execute ATS Diagnostic Audit
                </>
              )}
            </button>
          </div>

          {/* Rules & Compliance Card */}
          <div className="card p-5 space-y-2 bg-subtle">
            <h4 className="font-heading text-sm font-bold text-app flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> 13-Point Compliance Engine Features
            </h4>
            <ul className="text-xs text-secondary font-medium space-y-1.5 list-disc pl-4">
              <li>Case-insensitive normalization (PYTHON = Python = python).</li>
              <li>Skill variation mapping (react.js $\leftrightarrow$ react, nodejs $\leftrightarrow$ node.js, ml $\leftrightarrow$ machine learning).</li>
              <li>False positive prevention (word boundary exact regex matching).</li>
              <li>Evidence weighting: higher weight given to skills in Projects & Experience.</li>
              <li>100% deterministic reproducibility across sessions.</li>
            </ul>
          </div>
        </div>

        {/* Right Column: Output Report */}
        <div className="lg:col-span-7">
          {analysis ? (
            <div className="space-y-4 animate-fade-in">
              {/* ATS Score Header */}
              <div className="card p-6 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block">Audited Requisition Rating</span>
                  <h3 className="font-heading text-xl font-bold text-app">Weighted ATS Score</h3>
                </div>
                <div className="text-right">
                  <span className="font-heading text-3xl font-extrabold text-app">{analysis.score || analysis.ats_score}</span>
                  <span className="text-xs font-bold text-secondary"> / 100</span>
                </div>
              </div>

              {/* Match Status Banner */}
              <div className={`card p-4 flex items-center justify-between border-l-4 ${
                skillDetails?.is_perfect_match ? 'border-emerald-500 bg-emerald-500/5' : 'border-[#FF5722] bg-[#FF5722]/5'
              }`}>
                <div className="flex items-center gap-3">
                  {skillDetails?.is_perfect_match ? (
                    <div className="w-9 h-9 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center shrink-0">
                      <Sparkles className="w-5 h-5" />
                    </div>
                  ) : (
                    <div className="w-9 h-9 rounded-full bg-[#FF5722]/10 text-[#FF5722] flex items-center justify-center shrink-0">
                      <Award className="w-5 h-5" />
                    </div>
                  )}
                  <div>
                    <h4 className="font-heading text-sm font-bold text-app">
                      {skillDetails?.is_perfect_match ? '🌟 100% Perfect Skill Match!' : 'Skill Keyword Match Status'}
                    </h4>
                    <p className="text-xs text-secondary font-medium mt-0.5">
                      Target Role: <strong className="text-app">{targetRole}</strong> — {skillDetails?.exact_count || matchedKeywords.length} of {skillDetails?.total_required || (matchedKeywords.length + missingKeywords.length)} core skills verified
                    </p>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-extrabold ${
                    skillDetails?.is_perfect_match ? 'bg-emerald-500 text-white' : 'bg-[#FF5722] text-white'
                  }`}>
                    {skillDetails?.status_label || `${skillDetails?.match_percentage || 80}% Match`}
                  </span>
                </div>
              </div>

              {/* Configurable Weighted Components Breakdown */}
              {weightedBreakdown.skills_score !== undefined && (
                <div className="card p-5 space-y-3">
                  <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Configurable Weighted Component Scores</span>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                    <div className="card p-2.5 text-center bg-subtle">
                      <span className="text-[10px] font-bold text-secondary uppercase block">Skills Match (35%)</span>
                      <span className="font-heading text-base font-extrabold text-app">{weightedBreakdown.skills_score}%</span>
                    </div>
                    <div className="card p-2.5 text-center bg-subtle">
                      <span className="text-[10px] font-bold text-secondary uppercase block">Projects (25%)</span>
                      <span className="font-heading text-base font-extrabold text-app">{weightedBreakdown.projects_score}%</span>
                    </div>
                    <div className="card p-2.5 text-center bg-subtle">
                      <span className="text-[10px] font-bold text-secondary uppercase block">Certs (15%)</span>
                      <span className="font-heading text-base font-extrabold text-app">{weightedBreakdown.certifications_score}%</span>
                    </div>
                    <div className="card p-2.5 text-center bg-subtle">
                      <span className="text-[10px] font-bold text-secondary uppercase block">Education (10%)</span>
                      <span className="font-heading text-base font-extrabold text-app">{weightedBreakdown.education_score}%</span>
                    </div>
                    <div className="card p-2.5 text-center bg-subtle">
                      <span className="text-[10px] font-bold text-secondary uppercase block">Completeness (10%)</span>
                      <span className="font-heading text-base font-extrabold text-app">{weightedBreakdown.completeness_score}%</span>
                    </div>
                    <div className="card p-2.5 text-center bg-subtle">
                      <span className="text-[10px] font-bold text-secondary uppercase block">Achievements (5%)</span>
                      <span className="font-heading text-base font-extrabold text-app">{weightedBreakdown.achievements_score}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Explainable Skill Evidence Breakdown */}
              {evidenceDetails.length > 0 && (
                <div className="card p-5 space-y-3">
                  <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Explainable Skill Evidence Rationale</span>
                  <div className="space-y-1.5">
                    {evidenceDetails.map((item: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between text-xs py-1.5 border-b border-app">
                        <div className="flex items-center gap-2">
                          {item.status === 'Matched' ? (
                            <Check className="w-3.5 h-3.5 text-emerald-500" />
                          ) : (
                            <X className="w-3.5 h-3.5 text-red-500" />
                          )}
                          <span className="font-bold text-app">{item.skill}</span>
                        </div>
                        <span className="text-secondary text-[11px] font-medium">{item.source}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detected, Missing, and Additional Skills */}
              <div className="card p-5 space-y-3">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Normalized Skill Extraction Audit</span>
                
                <div className="space-y-2">
                  <p className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400">✓ Verified Required Skills ({matchedKeywords.length})</p>
                  <div className="flex flex-wrap gap-1.5">
                    {matchedKeywords.map((kw: string) => (
                      <span key={kw} className="badge badge-emerald flex items-center gap-1">
                        <Check className="w-3 h-3 text-emerald-600 dark:text-emerald-400" /> {kw}
                      </span>
                    ))}
                  </div>
                </div>

                {additionalSkills.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-app">
                    <p className="text-[11px] font-bold text-blue-600 dark:text-blue-400">⚡ Additional Relevant Tech Stack ({additionalSkills.length})</p>
                    <div className="flex flex-wrap gap-1.5">
                      {additionalSkills.map((kw: string) => (
                        <span key={kw} className="badge badge-subtle flex items-center gap-1">
                          <FileCode className="w-3 h-3 text-blue-600 dark:text-blue-400" /> {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {missingKeywords.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-app">
                    <p className="text-[11px] font-bold text-red-600 dark:text-red-400">✗ Missing Requisition Skills for {targetRole} ({missingKeywords.length})</p>
                    <div className="flex flex-wrap gap-1.5">
                      {missingKeywords.map((kw: string) => (
                        <span key={kw} className="badge badge-red flex items-center gap-1">
                          <X className="w-3 h-3 text-red-600 dark:text-red-400" /> {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Structural Compliance Checklist */}
              <div className="card p-5 space-y-2">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Structural Section Compliance</span>
                {Object.entries(analysis.structure_checks || {}).map(([section, present]: any) => (
                  <div key={section} className="flex items-center justify-between text-xs py-1 border-b border-app">
                    <span className="capitalize font-bold text-app">{section} Section</span>
                    {present ? (
                      <span className="badge badge-emerald flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" /> Detected</span>
                    ) : (
                      <span className="badge badge-amber flex items-center gap-1"><AlertTriangle className="w-3 h-3 text-amber-600 dark:text-amber-400" /> Missing</span>
                    )}
                  </div>
                ))}
              </div>

              {/* Identified Strengths */}
              {strengths.length > 0 && (
                <div className="card p-5 space-y-2 bg-emerald-500/5">
                  <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">Audited Strengths</span>
                  <ul className="text-xs text-secondary font-medium space-y-1.5 list-disc pl-4">
                    {strengths.map((str: string, idx: number) => (
                      <li key={idx}>{str}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Improvement Recommendations */}
              <div className="card p-5 space-y-2">
                <span className="text-xs font-bold text-secondary uppercase tracking-wider block">Actionable Optimization Plan</span>
                <ul className="text-xs text-secondary font-medium space-y-1.5 list-disc pl-4">
                  {recommendations.map((rec: string, idx: number) => (
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
                Upload a PDF/DOCX resume or paste raw content on the left to review explainable skill evidence.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
