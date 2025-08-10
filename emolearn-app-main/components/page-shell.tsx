"use client"

import type React from "react"
import { usePathname, useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { ArrowLeft } from "lucide-react"
import { cn } from "@/lib/utils"

type PageShellProps = {
  title?: string
  subtitle?: string
  children: React.ReactNode
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "3xl" | "4xl" | "5xl" | "6xl" | "7xl"
  className?: string
}

export function PageShell({ title, subtitle, children, maxWidth = "5xl", className }: PageShellProps) {
  const pathname = usePathname()
  const router = useRouter()
  const isRoot = pathname === "/"

  const max = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    "3xl": "max-w-3xl",
    "4xl": "max-w-4xl",
    "5xl": "max-w-5xl",
    "6xl": "max-w-6xl",
    "7xl": "max-w-7xl",
  }[maxWidth]

  return (
    <div className="min-h-svh bg-white relative">
      {/* subtle gradient accent */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-[180px] bg-gradient-to-b from-neutral-100 to-transparent"
      />
      <div className={cn("relative mx-auto w-full px-4 sm:px-6 lg:px-8 py-10", max, className)}>
        {/* Header with optional Back */}
        {(title || subtitle) && (
          <header className="mb-8">
            <div className="flex items-center justify-between">
              {!isRoot ? (
                <motion.button
                  onClick={() => router.back()}
                  className="inline-flex items-center gap-2 text-sm text-neutral-700 hover:text-neutral-900 rounded-md px-2 py-1 -ml-1"
                  whileHover={{ x: -2 }}
                  whileTap={{ scale: 0.98 }}
                  aria-label="Go to previous page"
                >
                  <ArrowLeft className="size-4" />
                  <span>Back</span>
                </motion.button>
              ) : (
                <span aria-hidden className="w-[60px]" />
              )}
              <div className="text-center flex-1">
                {title ? (
                  <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-neutral-900">{title}</h1>
                ) : null}
                {subtitle ? <p className="mt-3 text-neutral-600">{subtitle}</p> : null}
              </div>
              {/* spacer for centering */}
              <span aria-hidden className="w-[60px]" />
            </div>
          </header>
        )}

        {/* Route-level motion container */}
        <motion.main
          key={pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
        >
          {children}
        </motion.main>
      </div>
    </div>
  )
}
