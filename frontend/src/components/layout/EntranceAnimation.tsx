import { useEffect, useState } from 'react'
import { Compass } from 'lucide-react'

export default function EntranceAnimation() {
  const [visible, setVisible] = useState(() => {
    if (typeof window !== 'undefined') {
      const hasEntered = sessionStorage.getItem('cp_has_entered')
      return !hasEntered
    }
    return false
  })

  // Animation phases: 'emerge' (0-420ms) -> 'branch' (420-920ms) -> 'converge' (920-1420ms) -> 'morph' (1420-1850ms) -> 'done'
  const [phase, setPhase] = useState<'emerge' | 'branch' | 'converge' | 'morph' | 'done'>('emerge')

  useEffect(() => {
    if (!visible) return

    const t1 = setTimeout(() => setPhase('branch'), 420)
    const t2 = setTimeout(() => setPhase('converge'), 920)
    const t3 = setTimeout(() => setPhase('morph'), 1420)
    const t4 = setTimeout(() => {
      setPhase('done')
      setVisible(false)
      sessionStorage.setItem('cp_has_entered', 'true')
    }, 1850)

    return () => {
      clearTimeout(t1)
      clearTimeout(t2)
      clearTimeout(t3)
      clearTimeout(t4)
    }
  }, [visible])

  if (!visible || phase === 'done') return null

  const y1Val = phase !== 'emerge' ? 100 : 160
  const y2Val = phase !== 'emerge' ? 220 : 160

  return (
    <div
      className={`fixed inset-0 z-50 bg-[#FAFAFA] dark:bg-[#090D16] flex flex-col items-center justify-center overflow-hidden transition-opacity duration-400 ease-out ${
        phase === 'morph' ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      {/* SVG Canvas for Center Line, 4 Branching Paths & Converging Network */}
      <div className="relative w-full max-w-xl h-80 flex items-center justify-center">
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 600 320" fill="none">
          {/* Phase 1: Emergent Center Vertical Line */}
          <line
            x1="300"
            y1={y1Val}
            x2="300"
            y2={y2Val}
            className="stroke-[#FF5722] dark:stroke-[#FF7043] stroke-2 transition-all duration-400 ease-out"
          />

          {/* Phase 2: 4 Branching Bezier Curves (Career, Interview, Skills, Growth) */}
          {(phase === 'branch' || phase === 'converge' || phase === 'morph') && (
            <>
              {/* Path 1: Top-Left (Career) */}
              <path
                d="M300 130 C220 110, 140 80, 100 60 C180 120, 240 150, 300 150"
                className="stroke-[#FF5722]/60 dark:stroke-[#FF7043]/70 stroke-[1.5] fill-none animate-pulse"
                strokeDasharray="4 2"
              />
              {/* Path 2: Top-Right (Interview) */}
              <path
                d="M300 130 C380 110, 460 80, 500 60 C420 120, 360 150, 300 150"
                className="stroke-[#FF5722]/60 dark:stroke-[#FF7043]/70 stroke-[1.5] fill-none animate-pulse"
                strokeDasharray="4 2"
              />
              {/* Path 3: Bottom-Left (Skills) */}
              <path
                d="M300 190 C220 210, 140 240, 100 260 C180 200, 240 170, 300 170"
                className="stroke-[#FF5722]/60 dark:stroke-[#FF7043]/70 stroke-[1.5] fill-none animate-pulse"
                strokeDasharray="4 2"
              />
              {/* Path 4: Bottom-Right (Growth) */}
              <path
                d="M300 190 C380 210, 460 240, 500 260 C420 200, 360 170, 300 170"
                className="stroke-[#FF5722]/60 dark:stroke-[#FF7043]/70 stroke-[1.5] fill-none animate-pulse"
                strokeDasharray="4 2"
              />
            </>
          )}
        </svg>

        {/* Floating Minimal Domain Path Labels */}
        {phase === 'branch' && (
          <>
            <span className="absolute top-10 left-16 text-[10px] font-bold tracking-widest text-[#FF5722] dark:text-[#FF7043] uppercase animate-fade-in">
              Career
            </span>
            <span className="absolute top-10 right-16 text-[10px] font-bold tracking-widest text-[#FF5722] dark:text-[#FF7043] uppercase animate-fade-in">
              Interview
            </span>
            <span className="absolute bottom-10 left-16 text-[10px] font-bold tracking-widest text-[#FF5722] dark:text-[#FF7043] uppercase animate-fade-in">
              Skills
            </span>
            <span className="absolute bottom-10 right-16 text-[10px] font-bold tracking-widest text-[#FF5722] dark:text-[#FF7043] uppercase animate-fade-in">
              Growth
            </span>
          </>
        )}

        {/* Phase 3: Converging Brand Logo & Center Ring */}
        <div
          className={`relative z-10 flex flex-col items-center justify-center transition-all duration-500 transform ${
            phase === 'converge' || phase === 'morph' ? 'scale-100 opacity-100' : 'scale-90 opacity-0'
          }`}
        >
          <div className="w-14 h-14 rounded-xl bg-[#1a1f3a] dark:bg-[#141936] text-white flex items-center justify-center shadow-md mb-3 border border-[#FF5722]/40">
            <Compass className="w-7 h-7 text-[#FF5722] animate-spin" style={{ animationDuration: '4s' }} />
          </div>
          <span className="font-heading text-2xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-100">
            CareerPilot <span className="text-[#FF5722] dark:text-[#FF7043] font-sans text-xs font-bold uppercase tracking-wider">AI</span>
          </span>
          <span className="text-[10px] uppercase tracking-widest font-semibold text-zinc-500 dark:text-zinc-400 mt-1">
            Navigating Candidate Readiness
          </span>
        </div>

        {/* Phase 4: Wireframe Outline of Top-Nav Dashboard Structure */}
        {phase === 'morph' && (
          <div className="absolute inset-0 border-t border-b border-[#FF5722]/30 dark:border-[#FF7043]/30 animate-pulse flex items-center justify-between px-8">
            <div className="w-24 h-2 bg-[#FF5722]/20 rounded" />
            <div className="flex gap-4">
              <div className="w-12 h-2 bg-[#FF5722]/20 rounded" />
              <div className="w-12 h-2 bg-[#FF5722]/20 rounded" />
              <div className="w-12 h-2 bg-[#FF5722]/20 rounded" />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
