import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { PageShell } from "@/components/page-shell"
import { Brain, Heart, BookOpen } from "lucide-react"
import { FadeInUp, Stagger, StaggerItem } from "@/components/animated"

export default function LandingPage() {
  return (
    <PageShell>
      <section className="text-center">
        <FadeInUp>
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="size-10 rounded-full bg-neutral-900 text-white flex items-center justify-center">
              <span className="text-sm font-semibold">C</span>
            </div>
            <span className="text-lg font-medium text-neutral-800">CortexAI</span>
          </div>
        </FadeInUp>

        <FadeInUp delay={0.05}>
          <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight text-neutral-900">
            AI That Reads Your Emotions
          </h1>
        </FadeInUp>

        <FadeInUp delay={0.1}>
          <p className="mt-4 text-neutral-600 max-w-2xl mx-auto">
            Traditional learning treats everyone the same. We adapt to how you FEEL while you learn.
          </p>
        </FadeInUp>

        <FadeInUp delay={0.15}>
          <div className="mt-6 flex items-center justify-center gap-3 text-neutral-700">
            <span className="inline-flex items-center gap-2 text-sm">
              <Brain className="size-4" /> Brain
            </span>
            <span className="inline-flex items-center gap-2 text-sm">
              <Heart className="size-4" /> Heart
            </span>
            <span className="inline-flex items-center gap-2 text-sm">
              <BookOpen className="size-4" /> Book
            </span>
          </div>
        </FadeInUp>

        <Stagger delay={0.2} className="mt-8 flex items-center justify-center gap-3">
          <StaggerItem>
            <Link href="/onboarding">
              <Button size="lg" className="px-6">
                Start Learning →
              </Button>
            </Link>
          </StaggerItem>
          <StaggerItem>
            <Link href="/learn">
              <Button size="lg" variant="secondary" className="px-6">
                Live Demo →
              </Button>
            </Link>
          </StaggerItem>
        </Stagger>

        <FadeInUp delay={0.25}>
          <Card className="mt-10 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            <CardContent className="py-6">
              <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-neutral-700">
                <span className="inline-flex items-center gap-2">{"✨ "}Emotion Detection</span>
                <span className="inline-flex items-center gap-2">{"📚 "}Adaptive Content</span>
                <span className="inline-flex items-center gap-2">{"🎥 "}Dynamic Videos</span>
                <span className="inline-flex items-center gap-2">{"🎯 "}Personalized Quizzes</span>
              </div>
            </CardContent>
          </Card>
        </FadeInUp>
      </section>
    </PageShell>
  )
}
