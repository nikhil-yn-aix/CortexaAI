"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { Download } from "lucide-react"
type FlashcardViewerProps = {
  front?: string
  back?: string
}

export function FlashcardViewer({
  front = "What is a perceptron?",
  back = "A perceptron is a simple linear binary classifier inspired by a biological neuron.",
}: FlashcardViewerProps) {
  const [flipped, setFlipped] = React.useState(false)
  const [downloading, setDownloading] = React.useState(false)

  async function downloadPPT() {
    try {
      setDownloading(true)
      const response = await fetch("/api/generate-pptx", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ front, back }),
      })

      if (!response.ok) {
        throw new Error("Failed to generate PPTX");
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "cortexai-flashcards.pptx"
      document.body.appendChild(a)
      a.click()
      a.remove()
    } finally {
      setDownloading(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
      <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">{"📚 "}Flashcards</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded-md border p-4 min-h-24 bg-neutral-50">
            <div className="text-sm">
              <span className="font-medium">{flipped ? "Back: " : "Front: "}</span>
              {flipped ? back : front}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button variant="secondary" onClick={() => setFlipped((f) => !f)}>
                {flipped ? "Show Front" : "Flip Card"}
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button onClick={downloadPPT} disabled={downloading}>
                <Download className="size-4 mr-2" />
                {downloading ? "Preparing PPT..." : "Download PPT"}
              </Button>
            </motion.div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
