"use client"

import React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Pause, Play, SkipForward, Radio } from "lucide-react"
import { motion } from "framer-motion"

type PodcastPlayerProps = {
  title?: string
  topic?: string
}

export function PodcastPlayer({
  title = "Let’s explore machine learning concepts...",
  topic = "Neural Networks",
}: PodcastPlayerProps) {
  const [playing, setPlaying] = React.useState(true)
  const [progress, setProgress] = React.useState<number>(42)

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
      <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center justify-between">
            <span className="truncate inline-flex items-center gap-2">
              <Radio className="size-4 text-neutral-500" /> Podcast Learning
            </span>
            <span className="text-xs text-neutral-500">Topic: {topic}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-sm text-neutral-700">{`" ${title} "`}</div>
          <div className="flex items-center gap-2">
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Button
                variant="secondary"
                size="icon"
                onClick={() => setPlaying((p) => !p)}
                aria-label={playing ? "Pause" : "Play"}
              >
                {playing ? <Pause className="size-4" /> : <Play className="size-4" />}
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              <Button variant="secondary" size="icon" aria-label="Skip">
                <SkipForward className="size-4" />
              </Button>
            </motion.div>
            <div className="ml-2 flex-1">
              <Slider
                value={[progress]}
                max={100}
                step={1}
                onValueChange={(v) => setProgress(v[0] ?? 0)}
                aria-label="Playback progress"
              />
              <div className="mt-1 text-xs text-neutral-500">{progress}%</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
