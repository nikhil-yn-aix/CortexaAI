"use client"

import React from "react"
import { PageShell } from "@/components/page-shell"
import { EmotionIndicator } from "@/components/emotion-indicator"
import { PodcastPlayer } from "@/components/podcast-player"
import { VideoPlayer } from "@/components/video-player"
import { FlashcardViewer } from "@/components/flashcard-viewer"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Mic } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent } from "@/components/ui/card"
import { FadeInUp } from "@/components/animated"

export default function LearnPage() {
  const [progress, setProgress] = React.useState(67)

  return (
    <PageShell title="Learning Session" subtitle="Multi-modal dashboard, emotion-adaptive.">
      <div className="flex flex-col gap-4">
        {/* Top controls */}
        <FadeInUp>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="inline-flex items-center gap-2 text-sm text-neutral-700">
              <span className="inline-flex items-center gap-1.5">
                <Mic className="size-4" aria-hidden />
                <span className="font-medium">Recording</span>
                <span className="ml-1 inline-block h-2.5 w-2.5 rounded-full bg-red-500 animate-pulse" aria-hidden />
              </span>
            </div>
            <div className="flex-1 max-w-md mx-auto">
              <Progress value={progress} aria-label="Progress" />
              <div className="mt-1 text-center text-xs text-neutral-500">Progress: {progress}%</div>
            </div>
            <div className="min-w-[240px]">
              <EmotionIndicator emotion="happy" message="You seem engaged! Increasing difficulty." compact />
            </div>
          </div>
        </FadeInUp>

        {/* Rebalanced layout: give more space to Manim + Flashcards */}
        <div className="grid gap-4 md:grid-cols-5">
          {/* Left: Visual supports (larger) */}
          <div className="md:col-span-3 space-y-4">
            <VideoPlayer />
            <FlashcardViewer />
          </div>

          {/* Right: Audio and transcript (slightly smaller) */}
          <div className="md:col-span-2 space-y-4">
            <PodcastPlayer title={'"Let\'s explore machine learning concepts..."'} topic="Neural Networks" />
            <FadeInUp>
              <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
                <CardContent className="pt-4">
                  <div className="text-sm text-neutral-700 font-medium mb-2">Live Transcript</div>
                  <div className="rounded-md border p-4 bg-neutral-50 h-40 overflow-auto text-sm">
                    {'"Neural networks are computational models inspired by the human brain...'}
                  </div>
                </CardContent>
              </Card>
            </FadeInUp>
          </div>
        </div>

        {/* Bottom emotion banner */}
        <FadeInUp>
          <EmotionIndicator
            emotion="happy"
            message='Emotion Detected: Happy — "You seem engaged! Increasing difficulty."'
          />
        </FadeInUp>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Link href="/final-quiz">
            <Button variant="secondary">Finish & Go to Final Quiz</Button>
          </Link>
        </div>
      </div>
    </PageShell>
  )
}
