import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  Building2, Layers, HelpCircle, Search
} from 'lucide-react'

function CompanyLogo({ id, name, size = 'md' }: { id: string; name: string; size?: 'sm' | 'md' | 'lg' }) {
  const containerDim = size === 'lg' ? 'w-12 h-12' : size === 'sm' ? 'w-8 h-8' : 'w-10 h-10'
  const svgDim = size === 'lg' ? 'w-7 h-7' : size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'

  const companyId = id.toLowerCase()

  if (companyId === 'google') {
    return (
      <div className={`${containerDim} bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={svgDim} viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
      </div>
    )
  }

  if (companyId === 'microsoft') {
    return (
      <div className={`${containerDim} bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={svgDim} viewBox="0 0 23 23">
          <path fill="#F25022" d="M1 1h10v10H1z"/>
          <path fill="#7FBA00" d="M12 1h10v10H12z"/>
          <path fill="#00A4EF" d="M1 12h10v10H1z"/>
          <path fill="#FFB900" d="M12 12h10v10H12z"/>
        </svg>
      </div>
    )
  }

  if (companyId === 'meta') {
    return (
      <div className={`${containerDim} bg-[#0668E1]/10 border border-[#0668E1]/30 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={svgDim} viewBox="0 0 24 24" fill="#0668E1">
          <path d="M16.85 4.5C14.7 4.5 12.87 5.75 11.75 7.6C10.63 5.75 8.8 4.5 6.65 4.5C3.5 4.5 1 7.05 1 10.25C1 14.7 5.7 19.5 11.75 19.5C17.8 19.5 22.5 14.7 22.5 10.25C22.5 7.05 20 4.5 16.85 4.5ZM6.65 17C4.1 17 2.5 14.15 2.5 10.25C2.5 7.9 4.3 6 6.65 6C8.5 6 10.15 7.2 10.9 8.9L9.15 11.8C8.5 10.6 7.5 9.8 6.4 9.8C5.2 9.8 4.2 10.8 4.2 12C4.2 13.2 5.2 14.2 6.4 14.2C7.5 14.2 8.5 13.4 9.15 12.2L10.9 15.1C10.15 16.8 8.5 18 6.65 18V17Z" />
        </svg>
      </div>
    )
  }

  if (companyId === 'amazon') {
    return (
      <div className={`${containerDim} bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={svgDim} viewBox="0 0 24 24">
          <path fill="#FF9900" d="M14.5 18.5c-4.2 2-9.4 1-12.7-1.2-.3-.2-.1-.6.2-.5 4.1 1.7 8.9 1.3 12.4-.7.4-.2.8.2.1.4zm2.1-1.3c-.3-.4-1.9-.2-2.6 0-.2 0-.3-.2-.1-.3 1.3-.9 3.4-.6 3.7-.2.3.4.1 2.6-.9 3.7-.2.2-.4.1-.3-.1.3-.7.5-2.7.2-3.1z"/>
          <path fill="#18181B" className="dark:fill-white" d="M12.8 4c-3.1 0-5.7 1.8-5.7 4.8 0 1.9.9 3.2 2.4 3.9.3.2.6 0 .7-.3l.5-1.9c0-.2 0-.4-.3-.5-1-.5-1.5-1.2-1.5-2.2 0-1.8 1.6-3 3.8-3 2.1 0 3.3 1.1 3.3 2.7 0 1.5-.7 3.5-1.8 3.5-.6 0-1-.4-.8-1.2l.9-3.7c.1-.4-.1-.7-.5-.7-.7 0-1.7.7-1.7 2 0 .5.2.9.2.9l-1 4.2c-.3 1.3.1 2.5 1.2 2.5 2.2 0 3.8-2.3 3.8-4.9 0-3.3-2.6-5-5.5-5z"/>
        </svg>
      </div>
    )
  }

  if (companyId === 'apple') {
    return (
      <div className={`${containerDim} bg-zinc-100 dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={`${svgDim} fill-zinc-900 dark:fill-white`} viewBox="0 0 24 24">
          <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.32c.67-.82 1.12-1.96.99-3.1-.96.04-2.14.64-2.83 1.44-.61.71-1.14 1.87-.99 2.99 1.08.08 2.16-.51 2.83-1.33z"/>
        </svg>
      </div>
    )
  }

  if (companyId === 'netflix') {
    return (
      <div className={`${containerDim} bg-red-950/20 border border-red-800/40 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={svgDim} viewBox="0 0 24 24">
          <path fill="#E50914" d="M5.398 0v24l4.577-1.32V8.922l4.898 15.078H18.6V0l-4.577 1.32v13.758L9.125 0z"/>
        </svg>
      </div>
    )
  }

  if (companyId === 'uber') {
    return (
      <div className={`${containerDim} bg-zinc-900 dark:bg-zinc-800 border border-zinc-700 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={`${svgDim} fill-white`} viewBox="0 0 24 24">
          <path d="M12 24C18.6274 24 24 18.6274 24 12C24 5.37258 18.6274 0 12 0C5.37258 0 0 5.37258 0 12C0 18.6274 5.37258 24 12 24ZM7.5 7.5H16.5V11.25H12.75V16.5H11.25V11.25H7.5V7.5Z"/>
        </svg>
      </div>
    )
  }

  if (companyId === 'stripe') {
    return (
      <div className={`${containerDim} bg-[#635BFF]/10 border border-[#635BFF]/30 flex items-center justify-center flex-shrink-0 shadow-xs rounded-md`}>
        <svg className={svgDim} viewBox="0 0 24 24">
          <path fill="#635BFF" d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-4.716C17.65.688 15.14 0 12.35 0 6.945 0 3.3 2.766 3.3 7.07c0 5.867 7.747 6.302 7.747 9.544 0 .978-.813 1.542-2.164 1.542-2.585 0-5.38-1.155-7.14-2.196L.8 20.854C2.88 22.183 5.92 23 8.94 23c5.748 0 9.38-2.613 9.38-7.172 0-6.19-7.85-6.526-7.85-9.678h3.506z"/>
        </svg>
      </div>
    )
  }

  return (
    <div className={`${containerDim} bg-[#FF5722]/10 dark:bg-[#FF5722]/15 text-[#FF5722] dark:text-[#FF7043] border border-[#FF5722]/30 dark:border-[#FF5722]/40 flex items-center justify-center flex-shrink-0 font-bold font-heading rounded-md`}>
      {name?.[0] || 'C'}
    </div>
  )
}

export default function CompanyPrepPage() {
  const [selectedCompanyId, setSelectedCompanyId] = useState('google')
  const [search, setSearch] = useState('')

  const { data: companiesData } = useQuery({
    queryKey: ['companies', search],
    queryFn: () => api.get(`/api/company-prep/companies?search=${encodeURIComponent(search)}`).then((r) => r.data),
  })

  const { data: companyDetail } = useQuery({
    queryKey: ['companyDetail', selectedCompanyId],
    queryFn: () => api.get(`/api/company-prep/companies/${selectedCompanyId}`).then((r) => r.data),
    enabled: !!selectedCompanyId,
  })

  const companies = companiesData?.companies || [
    { id: 'google', name: 'Google', difficulty: 'Hard' },
    { id: 'microsoft', name: 'Microsoft', difficulty: 'Medium-Hard' },
    { id: 'amazon', name: 'Amazon', difficulty: 'Medium-Hard' },
    { id: 'meta', name: 'Meta', difficulty: 'Hard' },
    { id: 'apple', name: 'Apple', difficulty: 'Hard' },
    { id: 'netflix', name: 'Netflix', difficulty: 'Very Hard' },
    { id: 'uber', name: 'Uber', difficulty: 'Hard' },
    { id: 'stripe', name: 'Stripe', difficulty: 'Hard' },
  ]

  return (
    <div className="space-y-6 animate-fade-in text-app">
      {/* Header */}
      <div className="card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block mb-1">Target Organization Intelligence</span>
          <div className="flex items-center gap-3">
            <h2 className="font-heading text-3xl font-extrabold text-app">Target Company Interview Intelligence</h2>
            <span className="badge badge-emerald flex items-center gap-1">
              <Building2 className="w-3 h-3 text-[#FF5722] dark:text-[#FF7043]" /> Recruiter Intel
            </span>
          </div>
          <p className="text-secondary text-xs mt-1">
            Explore corporate interview loops, engineering culture briefs, and question banks.
          </p>
        </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Column: Search & Company List */}
        <div className="lg:col-span-4 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input
              type="text"
              placeholder="Search target company..."
              className="input pl-9 text-xs"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            {companies.map((comp: any) => (
              <button
                key={comp.id}
                onClick={() => setSelectedCompanyId(comp.id)}
                className={`w-full p-3.5 border rounded-md text-left transition-all flex items-center gap-3 ${
                  selectedCompanyId === comp.id
                    ? 'border-[#FF5722] bg-[#FF5722]/10 text-[#FF5722] font-semibold dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF7043] shadow-xs'
                    : 'border-app bg-surface text-secondary hover:bg-subtle'
                }`}
              >
                <CompanyLogo id={comp.id} name={comp.name} size="sm" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-bold text-app truncate">{comp.name}</p>
                  <p className="text-[10px] text-secondary font-medium">{comp.difficulty}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right Column: Company Intelligence Brief */}
        <div className="lg:col-span-8">
          {companyDetail ? (
            <div className="card p-6 space-y-6">
              <div className="flex items-center gap-4 pb-4 border-b border-app">
                <CompanyLogo id={companyDetail.id} name={companyDetail.name} size="lg" />
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-heading text-2xl font-bold text-app">{companyDetail.name}</h3>
                    <span className="badge badge-editorial">{companyDetail.difficulty}</span>
                  </div>
                  <p className="text-xs text-secondary mt-0.5">{companyDetail.culture}</p>
                </div>
              </div>

              {/* Hiring Rounds */}
              <div>
                <h4 className="font-heading text-sm font-bold text-app flex items-center gap-2 mb-3">
                  <Layers className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Standard Technical Interview Loop
                </h4>
                <div className="space-y-2">
                  {companyDetail.rounds?.map((round: string, idx: number) => (
                    <div key={idx} className="p-3.5 bg-subtle border border-app rounded-md text-xs font-medium text-app">
                      {round}
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Questions */}
              <div>
                <h4 className="font-heading text-sm font-bold text-app flex items-center gap-2 mb-3">
                  <HelpCircle className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" /> Frequent Technical Question Prompts
                </h4>
                <div className="space-y-2">
                  {companyDetail.sample_questions?.map((q: string, idx: number) => (
                    <div key={idx} className="p-3.5 bg-subtle border border-app rounded-md text-xs font-medium text-app font-mono leading-relaxed">
                      &quot;{q}&quot;
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="card p-12 text-center">
              <Building2 className="w-8 h-8 text-muted mx-auto mb-2" />
              <p className="text-xs text-secondary">Select a company on the left to view recruiter briefing</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
