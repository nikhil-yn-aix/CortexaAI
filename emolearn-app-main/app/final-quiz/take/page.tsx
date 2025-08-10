"use client"

import React from "react"
import { PageShell } from "@/components/page-shell"
import { EmotionIndicator } from "@/components/emotion-indicator"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { FadeInUp } from "@/components/animated"

type Option = { key: string; label: string }
const question = {
  text: "What is the primary function of a neural network?",
  options: [
    { key: "A", label: "Store data efficiently" },
    { key: "B", label: "Process information like the brain" },
    { key: "C", label: "Generate random numbers" },
    { key: "D", label: "Sort databases" },
  ] as Option[],
  correct: "B",
}

export default function TakeFinalQuizPage() {
  const [current, setCurrent] = React.useState(3) // 1-indexed display; example question 3 of 5
  const [total] = React.useState(5)
  const [answer, setAnswer] = React.useState<string | null>(null)

  return (
    <PageShell title={`Final Quiz — Question ${current} of ${total}`} subtitle="Stay focused; you’re doing great.">
      <div className="grid gap-6">
        <FadeInUp>
          <div className="flex items-center justify-between">
            <div className="w-48 h-2 rounded bg-neutral-100 overflow-hidden">
              <div className="h-full bg-neutral-900 transition-all" style={{ width: `${(current / total) * 100}%` }} />
            </div>
            <EmotionIndicator emotion="happy" message="You sound confident — trust your instincts!" compact />
          </div>
        </FadeInUp>

        <FadeInUp delay={0.05}>
          <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Question</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-neutral-800">{question.text}</p>
              <div className="space-y-2">
                {question.options.map((opt) => (
                  <label
                    key={opt.key}
                    className={`flex items-center gap-3 rounded-md border p-3 text-sm cursor-pointer transition-colors ${
                      answer === opt.key ? "border-neutral-900 bg-neutral-900 text-white" : "hover:bg-neutral-50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="q"
                      value={opt.key}
                      checked={answer === opt.key}
                      onChange={() => setAnswer(opt.key)}
                      className="sr-only"
                      aria-label={`Option ${opt.key}`}
                    />
                    <span className="font-medium">{opt.key})</span>
                    <span className="flex-1">{opt.label}</span>
                  </label>
                ))}
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button
                  variant="secondary"
                  onClick={() => setCurrent((c) => Math.max(1, c - 1))}
                  disabled={current <= 1}
                >
                  Previous
                </Button>
                {current < total ? (
                  <Button onClick={() => setCurrent((c) => Math.min(total, c + 1))} disabled={!answer}>
                    Next Question →
                  </Button>
                ) : (
                  <Link href="/reports">
                    <Button disabled={!answer}>View Final Report</Button>
                  </Link>
                )}
              </div>

              <div className="text-xs text-neutral-500">
                {"💡 Hint: You sounded confident during the neural networks explanation — trust your instincts!"}
              </div>
            </CardContent>
          </Card>
        </FadeInUp>
      </div>
    </PageShell>
  )
}
