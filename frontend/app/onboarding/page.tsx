"use client"

import React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { PageShell } from "@/components/page-shell"
import { FadeInUp, Stagger, StaggerItem } from "@/components/animated"

const subjects = ["Mathematics", "Physics", "Programming", "Biology"]

export default function OnboardingPage() {
  const [selected, setSelected] = React.useState<string>("Mathematics")

  return (
    <PageShell title="Let's Get Started" subtitle="Simple choices, big impact.">
      <div className="grid gap-6 md:grid-cols-2">
        <FadeInUp>
          <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            <CardHeader>
              <CardTitle className="text-base">How do you want to learn today?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Stagger>
                <div className="grid grid-cols-2 gap-3">
                  {subjects.map((s) => (
                    <StaggerItem key={s}>
                      <button
                        className={`rounded-md border px-4 py-3 text-sm text-left w-full ${
                          selected === s ? "border-neutral-900 bg-neutral-900 text-white" : "hover:bg-neutral-50"
                        }`}
                        onClick={() => setSelected(s)}
                        aria-pressed={selected === s}
                      >
                        {s}
                      </button>
                    </StaggerItem>
                  ))}
                </div>
              </Stagger>
              <div className="text-xs text-neutral-500">
                Selected subject: <span className="font-medium">{selected}</span>
              </div>
            </CardContent>
          </Card>
        </FadeInUp>

        <FadeInUp delay={0.05}>
          <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            <CardHeader>
              <CardTitle className="text-base">Upload PDFs or Paste Topic</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <label
                htmlFor="file"
                className="flex flex-col items-center justify-center gap-2 border-2 border-dashed rounded-md p-6 text-neutral-600 hover:bg-neutral-50 cursor-pointer"
              >
                <span className="text-sm">Drop files here or click to browse</span>
                <Input id="file" type="file" className="hidden" multiple />
              </label>
              <div className="space-y-2">
                <span className="text-sm text-neutral-700">What should I teach you?</span>
                <Textarea placeholder="e.g., Introduction to Neural Networks from my course notes..." />
              </div>
            </CardContent>
          </Card>
        </FadeInUp>
      </div>

      <div className="mt-6 flex justify-end">
        <Link href="/learn">
          <Button>Continue →</Button>
        </Link>
      </div>
    </PageShell>
  )
}
