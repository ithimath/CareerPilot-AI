"use client"

import React, { useMemo } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface FloatingPathsProps {
  position?: number
  className?: string
  color?: string
  opacity?: number
  count?: number
}

/**
 * FloatingPaths — animated SVG curved paths layer with crisp, visible strokes.
 */
export const FloatingPaths = React.memo(function FloatingPaths({
  position = 1,
  className,
  color = "currentColor",
  opacity = 1,
  count = 14,
}: FloatingPathsProps) {
  const paths = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const duration = 16 + ((i * 4) % 10)
      const delay = (i * 0.4) % 4
      const pathWidth = 1.0 + i * 0.08
      const strokeOpacity = 0.4 + (i % 5) * 0.12

      return {
        id: i,
        d: `M-${380 - i * 10 * position} -${189 + i * 10}C-${
          380 - i * 10 * position
        } -${189 + i * 10} -${312 - i * 10 * position} ${216 - i * 10} ${
          152 - i * 10 * position
        } ${343 - i * 10}C${616 - i * 10 * position} ${470 - i * 10} ${
          684 - i * 10 * position
        } ${875 - i * 10} ${684 - i * 10 * position} ${875 - i * 10}`,
        width: pathWidth,
        strokeOpacity,
        duration,
        delay,
      }
    })
  }, [count, position])

  return (
    <div
      className={cn(
        "absolute inset-0 pointer-events-none overflow-hidden transform-gpu",
        className
      )}
      style={{ opacity }}
    >
      <svg
        className="absolute inset-0 w-full h-full transform-gpu"
        viewBox="0 0 696 316"
        fill="none"
        preserveAspectRatio="xMidYMid slice"
      >
        <title>Background paths decoration</title>
        {paths.map((path) => (
          <motion.path
            key={path.id}
            d={path.d}
            stroke={color}
            strokeWidth={path.width}
            strokeOpacity={path.strokeOpacity}
            initial={{ pathLength: 0.4, pathOffset: 0 }}
            animate={{
              pathLength: [0.4, 0.95, 0.4],
              pathOffset: [0, 1],
            }}
            transition={{
              duration: path.duration,
              repeat: Infinity,
              ease: "linear",
              delay: path.delay,
            }}
          />
        ))}
      </svg>
    </div>
  )
})

interface BackgroundPathsProps {
  children?: React.ReactNode
  className?: string
  /** Number of path sets (default 2 — one from each side) */
  pathSets?: 1 | 2
  /** Overall intensity: 'full' for landing, 'medium' for auth, 'subtle' for inner pages */
  intensity?: "full" | "medium" | "subtle"
  /** Override the gradient background. False = no gradient (use parent bg). */
  gradient?: string | false
}

/**
 * BackgroundPaths — full-section animated background wrapper.
 */
export function BackgroundPaths({
  children,
  className,
  pathSets = 2,
  intensity = "full",
  gradient,
}: BackgroundPathsProps) {
  const opacityMap = {
    full: 0.6,
    medium: 0.45,
    subtle: 0.35,
  }

  const pathCountMap = {
    full: 18,
    medium: 12,
    subtle: 10,
  }

  const pathOpacity = opacityMap[intensity]
  const count = pathCountMap[intensity]

  // Default gradient for full/landing use
  const defaultGradient =
    intensity === "full"
      ? "[background:radial-gradient(125%_125%_at_50%_10%,#000_40%,#6633ee_100%)]"
      : undefined

  const resolvedGradient =
    gradient === false ? undefined : (gradient ?? defaultGradient)

  return (
    <div
      className={cn(
        "relative overflow-hidden",
        resolvedGradient && resolvedGradient,
        className
      )}
    >
      {/* Animated path layers */}
      <FloatingPaths
        position={1}
        color={intensity === "full" ? "white" : "currentColor"}
        opacity={pathOpacity}
        count={count}
      />
      {pathSets === 2 && (
        <FloatingPaths
          position={-1}
          color={intensity === "full" ? "white" : "currentColor"}
          opacity={pathOpacity * 0.7}
          count={Math.max(4, Math.floor(count * 0.7))}
        />
      )}

      {/* Content on top */}
      <div className="relative z-10">{children}</div>
    </div>
  )
}
