import { PageShell } from "@/components/page-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { EmotionTimeline } from "@/components/emotion-timeline"
import { FadeInUp } from "@/components/animated"

export default function ReportsPage() {
  return (
    <PageShell title="Your Learning Journey" subtitle="Analytics & mood tracking">
      <div className="grid gap-6 md:grid-cols-2">
        <FadeInUp>
          <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Emotion Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <EmotionTimeline />
            </CardContent>
          </Card>
        </FadeInUp>

        <div className="grid gap-6">
          <FadeInUp>
            <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <div className="rounded-md border p-4">
                  <div className="text-sm text-neutral-600">Quiz Accuracy</div>
                  <div className="mt-2 h-2 rounded bg-neutral-100 overflow-hidden">
                    <div className="h-full bg-neutral-900" style={{ width: "85%" }} />
                  </div>
                  <div className="mt-1 text-xs text-neutral-500">85%</div>
                </div>
                <div className="rounded-md border p-4">
                  <div className="text-sm text-neutral-600">Topics Mastered</div>
                  <div className="mt-2 h-2 rounded bg-neutral-100 overflow-hidden">
                    <div className="h-full bg-neutral-900" style={{ width: "75%" }} />
                  </div>
                  <div className="mt-1 text-xs text-neutral-500">12</div>
                </div>
              </CardContent>
            </Card>
          </FadeInUp>

          <FadeInUp>
            <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Improvement Areas</CardTitle>
              </CardHeader>
              <CardContent className="grid md:grid-cols-2 gap-4">
                <div className="rounded-md border p-4">
                  <div className="text-sm font-medium">Neural Networks</div>
                  <div className="text-xs text-neutral-500 mt-1">⭐⭐</div>
                </div>
                <div className="rounded-md border p-4">
                  <div className="text-sm font-medium">Deep Learning</div>
                  <div className="text-xs text-neutral-500 mt-1">⭐⭐⭐</div>
                </div>
                <div className="rounded-md border p-4">
                  <div className="text-sm font-medium">Backpropagation</div>
                  <div className="text-xs text-neutral-500 mt-1">⭐</div>
                </div>
                <div className="rounded-md border p-4">
                  <div className="text-sm font-medium">Regularization</div>
                  <div className="text-xs text-neutral-500 mt-1">⭐⭐</div>
                </div>
              </CardContent>
            </Card>
          </FadeInUp>
        </div>
      </div>

      <FadeInUp>
        <Card className="shadow-sm mt-6 transition-all hover:shadow-md hover:-translate-y-0.5">
          <CardContent className="p-4 grid md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm font-medium text-neutral-800">Insights</div>
              <ul className="mt-2 text-sm text-neutral-700 list-disc pl-5 space-y-1">
                <li>You learn best when happy and engaged</li>
                <li>Morning sessions = highest retention</li>
              </ul>
            </div>
            <div className="md:text-right">
              <Button>Download Report</Button>
            </div>
          </CardContent>
        </Card>
      </FadeInUp>
    </PageShell>
  )
}
