import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Compass, Target, Award, ArrowRight, CheckCircle2,
  FileCheck, Bot, ChevronRight, BarChart2, Check
} from 'lucide-react'
import { BackgroundPaths } from '@/components/ui/background-paths'

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState<'alignment' | 'ats' | 'interview'>('alignment')

  return (
    <div className="min-h-screen bg-app text-app font-sans selection:bg-[#FF5722]/20 selection:text-[#FF5722]">
      {/* Navigation Header */}
      <header className="sticky top-0 z-40 bg-surface/90 backdrop-blur-md border-b border-app shadow-2xs">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-[#1a1f3a] dark:bg-[#141936] flex items-center justify-center flex-shrink-0 text-white shadow-xs">
              <Compass className="w-4.5 h-4.5 text-[#FF5722]" />
            </div>
            <div>
              <span className="font-heading text-lg font-extrabold tracking-tight text-app">
                CareerPilot <span className="text-[#FF5722] dark:text-[#FF7043] font-sans text-xs font-black uppercase tracking-wider ml-0.5">AI</span>
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-xs font-bold text-secondary">
            <a href="#matrix" className="hover:text-[#FF5722] dark:hover:text-[#FF7043] transition-colors">Readiness Matrix</a>
            <a href="#architecture" className="hover:text-[#FF5722] dark:hover:text-[#FF7043] transition-colors">Capabilities</a>
            <a href="#standards" className="hover:text-[#FF5722] dark:hover:text-[#FF7043] transition-colors">Audit Standards</a>
          </nav>

          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="text-xs font-bold text-secondary hover:text-[#FF5722] dark:hover:text-[#FF7043] transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="btn btn-primary text-xs shadow-md shadow-[#FF5722]/20"
            >
              Access Platform
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section with Animated Background Paths */}
      <BackgroundPaths intensity="full" className="pt-16 pb-20 md:pt-24 md:pb-28 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-12 gap-12 items-center">
            {/* Left Column: Asymmetrical Hero Content */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#FF5722]/20 text-[#FFAB91] border border-[#FF5722]/40 text-[11px] font-bold tracking-wide rounded-md">
                <span className="w-2 h-2 rounded-full bg-[#FF5722] animate-pulse" />
                <span>Verified Candidate Employability Intelligence</span>
              </div>

              <h1 className="font-heading text-4xl sm:text-5xl md:text-6xl font-extrabold text-white leading-[1.12] tracking-tight">
                Data-Grounded Candidate Employability & Profile Auditing.
              </h1>

              <p className="text-base text-white/70 font-medium max-w-xl leading-relaxed">
                CareerPilot AI audits verified credential certificates, diagnoses real-time market skill gaps, validates ATS parsing compliance, and conducts evidence-backed technical interviews.
              </p>

              <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <Link
                  to="/signup"
                  className="btn btn-primary text-xs py-3 px-6 gap-2"
                >
                  <span>Launch Candidate Dossier</span>
                  <ArrowRight className="w-4 h-4 text-white" />
                </Link>
                <Link
                  to="/login"
                  className="btn text-xs py-3 px-6 gap-2 bg-white/10 hover:bg-white/20 text-white border border-white/20 hover:border-white/40 transition-all"
                >
                  <span>Explore Interactive Demo</span>
                </Link>
              </div>

              {/* Horizontal Proof Points */}
              <div className="pt-8 border-t border-white/10 grid grid-cols-3 gap-6">
                <div>
                  <p className="font-heading text-2xl font-bold text-white">88<span className="text-[#FFAB91] text-sm font-normal">/100</span></p>
                  <p className="text-[11px] font-bold text-white/50 mt-0.5">Audit Benchmark</p>
                </div>
                <div className="border-l border-white/10 pl-6">
                  <p className="font-heading text-2xl font-bold text-white">94<span className="text-[#FFAB91] text-sm font-normal">%</span></p>
                  <p className="text-[11px] font-bold text-white/50 mt-0.5">Skill Precision</p>
                </div>
                <div className="border-l border-white/10 pl-6">
                  <p className="font-heading text-2xl font-bold text-white">STAR</p>
                  <p className="text-[11px] font-bold text-white/50 mt-0.5">Method Verifier</p>
                </div>
              </div>
            </div>

            {/* Right Column: Hero Graphic Preview Widget */}
            <div className="lg:col-span-5">
              <div className="card p-6 border-app space-y-5 bg-surface shadow-md">
                <div className="flex items-center justify-between pb-4 border-b border-app">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-[#FF5722]" />
                    <span className="text-xs font-mono text-app font-bold">LIVE AUDIT DEMO</span>
                  </div>
                  <span className="badge badge-emerald">
                    VERIFIED CANDIDATE
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-secondary">Target Role Track</span>
                    <span className="font-bold text-app">Full-Stack Engineer</span>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs font-medium">
                      <span className="text-secondary">Market Match Score</span>
                      <span className="text-[#FF5722] dark:text-[#FF7043] font-mono font-bold">92%</span>
                    </div>
                    <div className="w-full h-2 bg-subtle rounded-full overflow-hidden border border-app">
                      <div className="h-full bg-[#FF5722] rounded-full w-[92%]" />
                    </div>
                  </div>
                </div>

                <div className="p-3.5 bg-subtle rounded-lg border border-app space-y-2 text-xs">
                  <div className="flex items-center gap-2 text-[#FF5722] dark:text-[#FF7043] font-bold">
                    <CheckCircle2 className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                    <span>Verified Skill Badges</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {['React.js', 'TypeScript', 'Node.js', 'PostgreSQL', 'Vite', 'Docker'].map((s) => (
                      <span key={s} className="px-2 py-0.5 text-[10px] font-mono font-bold bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-secondary font-medium pt-2 border-t border-app">
                  <span>ATS Diagnostic Status: <strong className="text-[#FF5722] dark:text-[#FF7043] font-bold">Pass (88/100)</strong></span>
                  <ChevronRight className="w-4 h-4 text-secondary" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </BackgroundPaths>

      {/* Interactive Assessment Spotlight Section */}
      <section id="matrix" className="py-20 bg-subtle border-b border-app">
        <div className="max-w-7xl mx-auto px-6 space-y-10">
          {/* Asymmetrical Split Title Header */}
          <div className="grid md:grid-cols-12 gap-6 items-end">
            <div className="md:col-span-7 space-y-2">
              <span className="text-[11px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block">Audited Assessment Matrix</span>
              <h2 className="font-heading text-3xl sm:text-4xl font-extrabold text-app tracking-tight">
                Explainable Candidate Job Readiness
              </h2>
            </div>
            <div className="md:col-span-5">
              <p className="text-xs text-secondary font-medium leading-relaxed">
                Replaces speculative resume scoring with verifiable evidence metrics compiled from actual project code, OCR certificates, and STAR interview responses.
              </p>
            </div>
          </div>

          {/* Interactive Widget Box */}
          <div className="card border border-app overflow-hidden">
            {/* Tab Header Bar */}
            <div className="flex border-b border-app bg-surface overflow-x-auto p-1 gap-1">
              <button
                onClick={() => setActiveTab('alignment')}
                className={`px-5 py-3 text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap rounded-md ${
                  activeTab === 'alignment'
                    ? 'bg-[#FF5722]/10 text-[#FF5722] border-b-2 border-[#FF5722] dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043]'
                    : 'text-secondary hover:bg-subtle hover:text-app'
                }`}
              >
                <Target className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                <span>1. Tech Stack Alignment</span>
              </button>
              <button
                onClick={() => setActiveTab('ats')}
                className={`px-5 py-3 text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap rounded-md ${
                  activeTab === 'ats'
                    ? 'bg-[#FF5722]/10 text-[#FF5722] border-b-2 border-[#FF5722] dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043]'
                    : 'text-secondary hover:bg-subtle hover:text-app'
                }`}
              >
                <FileCheck className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                <span>2. ATS Parser Compliance</span>
              </button>
              <button
                onClick={() => setActiveTab('interview')}
                className={`px-5 py-3 text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap rounded-md ${
                  activeTab === 'interview'
                    ? 'bg-[#FF5722]/10 text-[#FF5722] border-b-2 border-[#FF5722] dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043]'
                    : 'text-secondary hover:bg-subtle hover:text-app'
                }`}
              >
                <Bot className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                <span>3. AI Evidence Interview Matrix</span>
              </button>
            </div>

            {/* Tab Content Display */}
            <div className="p-6 md:p-8 bg-surface">
              {activeTab === 'alignment' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between flex-wrap gap-4 pb-4 border-b border-app">
                    <div>
                      <span className="text-[10px] font-bold text-secondary uppercase tracking-wide">TARGET ROLE</span>
                      <h3 className="font-heading text-xl font-bold text-app">Senior Full-Stack Engineer Track</h3>
                    </div>
                    <span className="badge badge-emerald">
                      Alignment Grade: 94% • High Readiness
                    </span>
                  </div>

                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="p-5 bg-subtle border border-app rounded-xl space-y-2">
                      <span className="text-xs font-bold text-secondary uppercase tracking-wide block">Verified Tech Stack</span>
                      <p className="font-heading text-3xl font-bold text-app">14 Skills</p>
                      <p className="text-xs text-secondary font-medium">JavaScript, React, Node.js, Python, PostgreSQL, Git</p>
                    </div>
                    <div className="p-5 bg-subtle border border-app rounded-xl space-y-2">
                      <span className="text-xs font-bold text-secondary uppercase tracking-wide block">Priority Skill Gaps</span>
                      <p className="font-heading text-3xl font-bold text-app">2 Gaps</p>
                      <p className="text-xs text-secondary font-medium">GraphQL, Docker Container Orchestration</p>
                    </div>
                    <div className="p-5 bg-subtle border border-app rounded-xl space-y-2">
                      <span className="text-xs font-bold text-secondary uppercase tracking-wide block">Project Repositories</span>
                      <p className="font-heading text-3xl font-bold text-[#FF5722] dark:text-[#FF7043]">3 Verified</p>
                      <p className="text-xs text-secondary font-medium">Code structure & commits verified via GitHub</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'ats' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between flex-wrap gap-4 pb-4 border-b border-app">
                    <div>
                      <span className="text-[10px] font-bold text-secondary uppercase tracking-wide">ATS SCAN DIAGNOSTIC</span>
                      <h3 className="font-heading text-xl font-bold text-app">Corporate ATS Keyword & Structural Parser Audit</h3>
                    </div>
                    <span className="badge badge-emerald">
                      ATS Score: 88 / 100 • Parser Approved
                    </span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="p-5 bg-subtle border border-app rounded-xl space-y-3">
                      <h4 className="font-heading text-sm font-bold text-app flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                        <span>ATS Parsing Pass Items</span>
                      </h4>
                      <ul className="text-xs text-secondary font-medium space-y-1.5 list-disc pl-4">
                        <li>Standard PDF heading structure recognized without table wrap errors</li>
                        <li>High recruiter keyword density for Full-Stack, REST API, SQL</li>
                        <li>Contact details and LinkedIn URLs correctly identified</li>
                      </ul>
                    </div>
                    <div className="p-5 bg-subtle border border-app rounded-xl space-y-3">
                      <h4 className="font-heading text-sm font-bold text-app flex items-center gap-2">
                        <BarChart2 className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                        <span>Suggested Keyword Enhancements</span>
                      </h4>
                      <ul className="text-xs text-secondary font-medium space-y-1.5 list-disc pl-4">
                        <li>Add quantified metrics to project outcome section (e.g. &quot;improved latency by 35%&quot;)</li>
                        <li>Include CI/CD deployment pipeline keywords</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'interview' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between flex-wrap gap-4 pb-4 border-b border-app">
                    <div>
                      <span className="text-[10px] font-bold text-secondary uppercase tracking-wide">EVIDENCE EVALUATION</span>
                      <h3 className="font-heading text-xl font-bold text-app">STAR Method & Technical Depth Rubric</h3>
                    </div>
                    <span className="badge badge-emerald">
                      STAR Rubric: 4.8 / 5.0 • Strong Clarity
                    </span>
                  </div>

                  <div className="space-y-3">
                    <div className="p-4 bg-subtle border border-app rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-app">Technical Concept Articulation</span>
                        <span className="text-xs font-mono font-bold text-[#FF5722] dark:text-[#FF7043]">95% Score</span>
                      </div>
                      <p className="text-xs text-secondary font-medium">Candidate explained state management choices with precise architectural trade-offs.</p>
                    </div>
                    <div className="p-4 bg-subtle border border-app rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-app">Behavioral Situation-Action-Result Alignment</span>
                        <span className="text-xs font-mono font-bold text-[#FF5722] dark:text-[#FF7043]">90% Score</span>
                      </div>
                      <p className="text-xs text-secondary font-medium">Responses structured using STAR criteria with clear evidence of individual responsibility.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Architectural Grid Section */}
      <section id="architecture" className="py-20 bg-app border-b border-app">
        <div className="max-w-7xl mx-auto px-6 space-y-16">
          <div className="max-w-2xl space-y-2">
            <span className="text-[11px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block">Platform Architecture</span>
            <h2 className="font-heading text-3xl sm:text-4xl font-extrabold text-app tracking-tight">
              Integrated Employability Platform Engine
            </h2>
            <p className="text-xs text-secondary font-medium">
              Purpose-built tools for candidates who require rigorous proof of skill readiness.
            </p>
          </div>

          {/* Asymmetrical 2-Column Editorial Feature Composition */}
          <div className="grid lg:grid-cols-12 gap-10 items-start">
            {/* Sticky Left Philosophy Card */}
            <div className="lg:col-span-4 bg-surface text-app p-8 rounded-2xl border border-app space-y-6 lg:sticky lg:top-24 shadow-md">
              <span className="badge badge-emerald">
                FOUNDATIONAL PRINCIPLE
              </span>
              <h3 className="font-heading text-2xl font-bold leading-tight text-app">
                Audited proof over speculative claims.
              </h3>
              <p className="text-xs text-secondary font-medium leading-relaxed">
                Traditional career tools rely on self-reported survey data. CareerPilot AI parses documents, audits repositories, and verifies interview responses to create objective candidate dossiers.
              </p>
              <div className="pt-4 border-t border-app text-xs text-secondary font-bold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                <span>100% Transparent Methodology</span>
              </div>
            </div>

            {/* Right Column: 4 Horizontal Editorial Feature Rows */}
            <div className="lg:col-span-8 space-y-0 divide-y divide-app border-t border-b border-app">
              {/* Feature Row 1 */}
              <div className="py-8 grid sm:grid-cols-12 gap-4 items-start">
                <div className="sm:col-span-1">
                  <div className="w-9 h-9 rounded-md bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] flex items-center justify-center font-bold text-sm">
                    <Award className="w-4.5 h-4.5 text-[#FF5722] dark:text-[#FF7043]" />
                  </div>
                </div>
                <div className="sm:col-span-11 space-y-1.5 pl-2">
                  <h4 className="font-heading text-lg font-bold text-app">Certificate OCR Extractor</h4>
                  <p className="text-xs text-secondary font-medium leading-relaxed">
                    Optical character recognition extracts course credentials, issuing institutions, and verified dates directly from PDFs and images to eliminate manual entry friction.
                  </p>
                </div>
              </div>

              {/* Feature Row 2 */}
              <div className="py-8 grid sm:grid-cols-12 gap-4 items-start">
                <div className="sm:col-span-1">
                  <div className="w-9 h-9 rounded-md bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] flex items-center justify-center font-bold text-sm">
                    <Target className="w-4.5 h-4.5 text-[#FF5722] dark:text-[#FF7043]" />
                  </div>
                </div>
                <div className="sm:col-span-11 space-y-1.5 pl-2">
                  <h4 className="font-heading text-lg font-bold text-app">Market Skill Gap Matrix</h4>
                  <p className="text-xs text-secondary font-medium leading-relaxed">
                    Compares candidate verified skill trees against real-time recruiter expectations for top tech tracks to outline missing skills.
                  </p>
                </div>
              </div>

              {/* Feature Row 3 */}
              <div className="py-8 grid sm:grid-cols-12 gap-4 items-start">
                <div className="sm:col-span-1">
                  <div className="w-9 h-9 rounded-md bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] flex items-center justify-center font-bold text-sm">
                    <FileCheck className="w-4.5 h-4.5 text-[#FF5722] dark:text-[#FF7043]" />
                  </div>
                </div>
                <div className="sm:col-span-11 space-y-1.5 pl-2">
                  <h4 className="font-heading text-lg font-bold text-app">Resume ATS Diagnostic Engine</h4>
                  <p className="text-xs text-secondary font-medium leading-relaxed">
                    Audits document formatting, keyword density, and structural layout to guarantee applicant tracking system compliance.
                  </p>
                </div>
              </div>

              {/* Feature Row 4 */}
              <div className="py-8 grid sm:grid-cols-12 gap-4 items-start">
                <div className="sm:col-span-1">
                  <div className="w-9 h-9 rounded-md bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] flex items-center justify-center font-bold text-sm">
                    <Bot className="w-4.5 h-4.5 text-[#FF5722] dark:text-[#FF7043]" />
                  </div>
                </div>
                <div className="sm:col-span-11 space-y-1.5 pl-2">
                  <h4 className="font-heading text-lg font-bold text-app">AI Evidence Interview Loop</h4>
                  <p className="text-xs text-secondary font-medium leading-relaxed">
                    Simulates technical & behavioral interview rounds with evidence feedback on domain depth, answer structure, and conciseness.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Employability Standards & Audit Banner Section */}
      <section id="standards" className="py-20 bg-subtle border-b border-app">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          <div className="text-center max-w-xl mx-auto space-y-2">
            <span className="text-[11px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider">Placement Benchmarks</span>
            <h2 className="font-heading text-3xl font-extrabold text-app tracking-tight">
              Designed for Placement Standard Rigor
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 card space-y-2">
              <p className="font-heading text-3xl font-extrabold text-app">12+</p>
              <h4 className="font-heading text-sm font-bold text-app">Target Role Tracks</h4>
              <p className="text-xs text-secondary font-medium">From Frontend Engineering to Machine Learning and Product Operations.</p>
            </div>
            <div className="p-6 card space-y-2">
              <p className="font-heading text-3xl font-extrabold text-[#FF5722] dark:text-[#FF7043]">&lt; 2s</p>
              <h4 className="font-heading text-sm font-bold text-app">Instant Certificate OCR</h4>
              <p className="text-xs text-secondary font-medium">Fast document processing with automated skill mapping.</p>
            </div>
            <div className="p-6 card space-y-2">
              <p className="font-heading text-3xl font-extrabold text-app">STAR</p>
              <h4 className="font-heading text-sm font-bold text-app">Behavioral Framework</h4>
              <p className="text-xs text-secondary font-medium">Evaluates responses according to Situation, Task, Action, Result criteria.</p>
            </div>
            <div className="p-6 card space-y-2">
              <p className="font-heading text-3xl font-extrabold text-[#FF5722] dark:text-[#FF7043]">100%</p>
              <h4 className="font-heading text-sm font-bold text-app">Transparent Methodology</h4>
              <p className="text-xs text-secondary font-medium">Every score includes explainable evidence and improvement actions.</p>
            </div>
          </div>

          {/* Call to Action Box */}
          <div className="bg-[#1a1f3a] text-white rounded-2xl p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-8 border border-[#FF5722]/40 shadow-md">
            <div className="space-y-2 max-w-xl text-center md:text-left">
              <h3 className="font-heading text-2xl md:text-3xl font-bold tracking-tight text-white">
                Ready to Audit Your Candidate Profile?
              </h3>
              <p className="text-xs md:text-sm text-zinc-300 font-medium">
                Join students and placement candidates creating verified job readiness dossiers.
              </p>
            </div>
            <Link
              to="/signup"
              className="px-6 py-3.5 text-xs font-bold text-white bg-[#FF5722] hover:bg-[#E64A19] transition-all rounded-xl flex items-center gap-2 whitespace-nowrap shadow-xs"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-4 h-4 text-white" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-surface text-secondary border-t border-app">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-[#1a1f3a] text-white flex items-center justify-center">
              <Compass className="w-3.5 h-3.5 text-[#FF5722]" />
            </div>
            <span className="font-heading text-base font-bold text-app">CareerPilot AI</span>
          </div>
          <p className="text-xs text-secondary font-medium">
            © {new Date().getFullYear()} CareerPilot AI Platform. All rights reserved. Professional Candidate Intelligence System.
          </p>
        </div>
      </footer>
    </div>
  )
}
