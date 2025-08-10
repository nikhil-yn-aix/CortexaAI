"use client"

import type React from "react"
import { Smile, Meh, Frown, HelpCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"

export type Emotion = "happy" | "confused" | "frustrated" | "neutral"

type EmotionIndicatorProps = {
  emotion?: Emotion
  message?: string
  compact?: boolean
}

const emotionMap: Record<Emotion, { label: string; icon: React.ElementType; classes: string }> = {
  happy: {
    label: "Happy",
    icon: Smile,
    classes: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  },
  confused: {
    label: "Confused",
    icon: HelpCircle,
    classes: "bg-sky-50 text-sky-800 ring-sky-200",
  },
  frustrated: {
    label: "Frustrated",
    icon: Frown,
    classes: "bg-orange-50 text-orange-800 ring-orange-200",
  },
  neutral: {
    label: "Neutral",
    icon: Meh,
    classes: "bg-neutral-50 text-neutral-800 ring-neutral-200",
  },
}

export function EmotionIndicator({
  emotion = "happy",
  message = "You seem engaged! Increasing difficulty.",
  compact = false,
}: EmotionIndicatorProps) {
  const cfg = emotionMap[emotion]
  const Icon = cfg.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className={cn(
        "rounded-lg ring-1 p-3 flex items-center gap-3",
        cfg.classes,
        compact ? "py-1.5 px-2.5 text-sm" : "py-2.5 px-3",
      )}
      aria-live="polite"
    >
      <div className="flex items-center gap-2">
        <span className="inline-flex h-2.5 w-2.5 rounded-full bg-current/60" aria-hidden />
        <Icon className="size-4" aria-hidden />
        <span className="font-medium">{cfg.label}</span>
      </div>
      {!compact && <span className="text-sm opacity-90">{message}</span>}
    </motion.div>
  )
}
