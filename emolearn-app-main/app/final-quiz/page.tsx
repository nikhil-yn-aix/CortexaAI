import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageShell } from "@/components/page-shell"
import { EmotionIndicator } from "@/components/emotion-indicator"
import { FadeInUp } from "@/components/animated"

export default function FinalQuizIntroPage() {
  return (
    <PageShell title="Final Quiz" subtitle="A focused check of your understanding.">
      <div className="grid gap-6 md:grid-cols-2">
        <FadeInUp>
          <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            <CardHeader>
              <CardTitle className="text-base">What to expect</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-neutral-700">
              <p>• 5 questions covering Neural Networks fundamentals</p>
              <p>• Adaptive hints based on your learning session</p>
              <p>• Review your final report after submitting</p>
            </CardContent>
          </Card>
        </FadeInUp>

        <FadeInUp delay={0.05}>
          <Card className="shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            <CardHeader>
              <CardTitle className="text-base">You’re ready</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <EmotionIndicator emotion="happy" message="Confidence detected during the session — you’ve got this!" />
              <div className="flex justify-end">
                <Link href="/final-quiz/take">
                  <Button>Start Final Quiz →</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </FadeInUp>
      </div>
    </PageShell>
  )
}
