"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { motion } from "framer-motion"

type VideoPlayerProps = {
  title?: string
  imageAlt?: string
}

export function VideoPlayer({
  title = "Manim Animation",
  imageAlt = "Placeholder animation for current topic",
}: VideoPlayerProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
      <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">
            {"📊 "}
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <img src="/abstract-neural-network-animation.png" alt={imageAlt} className="w-full rounded-md border" />
          <div className="mt-2 text-xs text-neutral-500">Current topic: "Neural Networks"</div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
