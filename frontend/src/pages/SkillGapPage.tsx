import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { CheckCircle2, AlertCircle, BookOpen, ExternalLink, Target, Layers, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface BenchmarkSkill {
  skill: string
  category: string
  candidateLevel: string
  requiredLevel: string
  gapLevel: 'None' | 'Minor' | 'Moderate' | 'Critical'
  importance: 'critical' | 'high' | 'medium'
  recommendedAction: string
  courseUrl?: string
}

export default function SkillGapPage() {
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/api/profile').then(r => r.data),
  })

  const targetCareer = profile?.target_career || 'Full-Stack Engineer'

  const { data } = useQuery({
    queryKey: ['skillGap', targetCareer],
    queryFn: () => api.get('/api/skill-gap').then(r => r.data),
  })

  const matchingSkills: string[] = data?.matching_skills || ['JavaScript', 'HTML/CSS', 'Git/GitHub']
  const missingSkills: any[] = data?.missing_skills || []

  // Market Benchmark Matrix for Target Role (e.g., Full-Stack Engineer)
  const fullStackBenchmarks: BenchmarkSkill[] = [
    {
      skill: 'JavaScript (ES6+)',
      category: 'Core Language',
      candidateLevel: matchingSkills.includes('JavaScript') ? 'Advanced' : 'Intermediate',
      requiredLevel: 'Advanced',
      gapLevel: matchingSkills.includes('JavaScript') ? 'None' : 'Minor',
      importance: 'critical',
      recommendedAction: 'Master Async/Await, Closures, and Event Loop internals',
      courseUrl: 'https://developer.mozilla.org/en-US/docs/Web/JavaScript'
    },
    {
      skill: 'React.js',
      category: 'Frontend Framework',
      candidateLevel: matchingSkills.includes('React') ? 'Proficient' : 'Foundational',
      requiredLevel: 'Advanced',
      gapLevel: matchingSkills.includes('React') ? 'None' : 'Moderate',
      importance: 'critical',
      recommendedAction: 'Build custom hooks, state management, and server side rendering',
      courseUrl: 'https://react.dev'
    },
    {
      skill: 'SQL & Database Architecture',
      category: 'Data Storage',
      candidateLevel: matchingSkills.includes('SQL') ? 'Intermediate' : 'Basic',
      requiredLevel: 'Proficient',
      gapLevel: matchingSkills.includes('SQL') ? 'None' : 'Critical',
      importance: 'critical',
      recommendedAction: 'Practice query optimization, indexing, and PostgreSQL schemas',
      courseUrl: 'https://www.postgresql.org/docs/'
    },
    {
      skill: 'Git / GitHub Workflow',
      category: 'Version Control',
      candidateLevel: matchingSkills.includes('Git') || matchingSkills.includes('Git/GitHub') ? 'Proficient' : 'Basic',
      requiredLevel: 'Proficient',
      gapLevel: 'None',
      importance: 'high',
      recommendedAction: 'Maintain clean commit history, pull request reviews, and rebase strategies',
      courseUrl: 'https://git-scm.com/doc'
    },
    {
      skill: 'REST & GraphQL APIs',
      category: 'Backend & Integration',
      candidateLevel: matchingSkills.includes('APIs') || matchingSkills.includes('Node.js') ? 'Proficient' : 'Basic',
      requiredLevel: 'Advanced',
      gapLevel: 'Moderate',
      importance: 'high',
      recommendedAction: 'Implement OAuth2 authentication, rate limiting, and API documentation',
      courseUrl: 'https://expressjs.com'
    },
    {
      skill: 'Docker & Containerization',
      category: 'DevOps & Deployment',
      candidateLevel: 'Unverified',
      requiredLevel: 'Intermediate',
      gapLevel: 'Critical',
      importance: 'medium',
      recommendedAction: 'Write Dockerfiles, multi-stage builds, and docker-compose configurations',
      courseUrl: 'https://docs.docker.com'
    }
  ]

  const combinedMatrix = fullStackBenchmarks.map(item => {
    const dynamicMatch = missingSkills.find(s => s.skill?.toLowerCase() === item.skill.toLowerCase())
    if (dynamicMatch) {
      return {
        ...item,
        gapLevel: dynamicMatch.importance === 'critical' ? 'Critical' as const : 'Moderate' as const,
        recommendedAction: dynamicMatch.courses?.[0]?.title
          ? `Enroll in: ${dynamicMatch.courses[0].title} (${dynamicMatch.courses[0].platform})`
          : item.recommendedAction
      }
    }
    return item
  })

  return (
    <div className="space-y-6 animate-fade-in text-app">
      {/* Header Banner */}
      <div className="card p-6 flex items-start justify-between gap-4 flex-wrap shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block mb-1">Market Benchmark Assessment</span>
          <h2 className="font-heading text-3xl font-extrabold text-app">Skill Gap Analysis Matrix</h2>
          <p className="text-secondary text-xs mt-1">
            Target Role: <strong className="text-app font-bold">{targetCareer}</strong> • Comparison Baseline: <span className="text-app font-semibold">2026 Tech Employability Standard</span>
          </p>
        </div>
        <Link to="/career/roadmap" className="btn btn-primary text-xs gap-2">
          <BookOpen className="w-3.5 h-3.5 text-white" /> View Recommended Roadmap
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="card p-5 flex items-center gap-3">
          <div className="w-10 h-10 bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded-md flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5 text-[#FF5722] dark:text-[#FF7043]" />
          </div>
          <div>
            <p className="font-heading text-3xl font-bold text-app">{matchingSkills.length}</p>
            <p className="text-[11px] font-bold text-secondary uppercase tracking-wider">Acquired Competencies</p>
          </div>
        </div>

        <div className="card p-5 flex items-center gap-3">
          <div className="w-10 h-10 bg-red-50 text-red-900 border border-red-200 dark:bg-red-950/40 dark:text-red-300 rounded-md flex items-center justify-center">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
          </div>
          <div>
            <p className="font-heading text-3xl font-bold text-app">{combinedMatrix.filter(s => s.gapLevel !== 'None').length}</p>
            <p className="text-[11px] font-bold text-secondary uppercase tracking-wider">Active Skill Gaps</p>
          </div>
        </div>

        <div className="card p-5 flex items-center gap-3">
          <div className="w-10 h-10 bg-subtle border border-app rounded-md flex items-center justify-center text-app">
            <Target className="w-5 h-5 text-[#FF5722] dark:text-[#FF7043]" />
          </div>
          <div>
            <p className="font-heading text-3xl font-bold text-app">
              {Math.round(((combinedMatrix.filter(s => s.gapLevel === 'None').length) / combinedMatrix.length) * 100)}%
            </p>
            <p className="text-[11px] font-bold text-secondary uppercase tracking-wider">Market Alignment Rate</p>
          </div>
        </div>
      </div>

      {/* Practical Market Comparison Matrix Table */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-app flex-wrap gap-2">
          <div>
            <span className="text-[11px] font-bold text-secondary uppercase tracking-wider block">Recruiter Evaluation Grid</span>
            <h3 className="font-heading text-xl font-bold text-app">Market Skill Comparison Matrix</h3>
          </div>
          <span className="text-xs font-semibold text-secondary">
            Evaluating Candidate vs. Standard Market Requirements for <strong className="text-app">{targetCareer}</strong>
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="editorial-table">
            <thead>
              <tr>
                <th>Market-Required Skill</th>
                <th>Category</th>
                <th>Candidate Level</th>
                <th>Required Benchmark</th>
                <th>Gap Severity</th>
                <th>Recommended Action</th>
              </tr>
            </thead>
            <tbody>
              {combinedMatrix.map((item, idx) => (
                <tr key={idx}>
                  <td className="font-bold text-app">
                    {item.skill}
                  </td>
                  <td className="text-xs text-secondary font-medium">{item.category}</td>
                  <td>
                    <span className={`text-xs font-bold ${item.candidateLevel === 'Unverified' ? 'text-muted' : 'text-app'}`}>
                      {item.candidateLevel}
                    </span>
                  </td>
                  <td className="text-xs font-mono font-bold text-app">{item.requiredLevel}</td>
                  <td>
                    {item.gapLevel === 'None' && <span className="badge badge-emerald">Aligned</span>}
                    {item.gapLevel === 'Minor' && <span className="badge badge-amber">Minor Gap</span>}
                    {item.gapLevel === 'Moderate' && <span className="badge badge-amber">Moderate Gap</span>}
                    {item.gapLevel === 'Critical' && <span className="badge badge-red">Critical Gap</span>}
                  </td>
                  <td className="max-w-xs text-xs text-secondary font-medium">
                    <div className="flex items-center justify-between gap-2">
                      <span>{item.recommendedAction}</span>
                      {item.courseUrl && (
                        <a
                          href={item.courseUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#FF5722] dark:text-[#FF7043] hover:underline flex-shrink-0"
                          title="View resource"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Curriculum Action Guide */}
      <div className="card p-6 space-y-3 bg-subtle">
        <h4 className="font-heading text-lg font-bold text-app flex items-center gap-2">
          <Layers className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Strategic Learning Recommendation
        </h4>
        <p className="text-xs text-secondary leading-relaxed font-medium">
          Closing your <strong className="text-app">Critical Gaps</strong> in SQL & Database Architecture and Docker containerization will increase your target role employability index from present level to over <strong className="text-app">85%</strong>.
        </p>
        <div className="pt-2 flex gap-3">
          <Link to="/career/roadmap" className="btn btn-primary text-xs gap-2">
            Start Learning Modules <ArrowRight className="w-3.5 h-3.5 text-white" />
          </Link>
          <Link to="/career/tracks" className="btn btn-secondary text-xs">
            Explore Alternate Role Tracks
          </Link>
        </div>
      </div>
    </div>
  )
}
