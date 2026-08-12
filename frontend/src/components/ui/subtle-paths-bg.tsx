import React from "react"
import { FloatingPaths } from "./background-paths"
import { cn } from "@/lib/utils"

interface SubtlePathsBgProps {
  className?: string
  /** 0.0–1.0, default 0.35 */
  opacity?: number
  /** Color of the paths, default 'currentColor' */
  color?: string
  /** How many path sets to render (1 or 2), default 2 */
  sets?: 1 | 2
}

/**
 * SubtlePathsBg — low-opacity animated path background for inner application pages.
 * Clearly visible stroke animations that add ambient motion across all pages.
 */
export const SubtlePathsBg = React.memo(function SubtlePathsBg({
  className,
  opacity = 0.35,
  color = "currentColor",
  sets = 2,
}: SubtlePathsBgProps) {
  return (
    <div
      className={cn(
        "absolute inset-0 pointer-events-none overflow-hidden transform-gpu z-0 opacity-40 dark:opacity-30",
        className
      )}
    >
      <FloatingPaths
        position={1}
        color={color}
        opacity={opacity}
        count={10}
      />
      {sets === 2 && (
        <FloatingPaths
          position={-1}
          color={color}
          opacity={opacity * 0.7}
          count={8}
        />
      )}
    </div>
  )
})
