"use client"
import { motion } from "framer-motion"

type Point = { time: string; happy: number; neutral: number; frustrated: number; confused: number }

type EmotionTimelineProps = {
  data?: Point[]
  height?: number
}

const defaultData: Point[] = [
  { time: "10:00", happy: 60, neutral: 20, frustrated: 10, confused: 10 },
  { time: "10:20", happy: 64, neutral: 18, frustrated: 9, confused: 9 },
  { time: "10:40", happy: 55, neutral: 22, frustrated: 12, confused: 11 },
  { time: "11:00", happy: 58, neutral: 21, frustrated: 11, confused: 10 },
  { time: "11:20", happy: 62, neutral: 19, frustrated: 8, confused: 11 },
  { time: "11:40", happy: 68, neutral: 16, frustrated: 6, confused: 10 },
  { time: "12:00", happy: 72, neutral: 14, frustrated: 6, confused: 8 },
  { time: "12:20", happy: 70, neutral: 15, frustrated: 7, confused: 8 },
  { time: "12:40", happy: 66, neutral: 17, frustrated: 8, confused: 9 },
  { time: "13:00", happy: 64, neutral: 19, frustrated: 8, confused: 9 },
]

const colors = {
  happy: "#10b981", // emerald-500
  neutral: "#a3a3a3", // neutral-400
  frustrated: "#fb923c", // orange-400
  confused: "#38bdf8", // sky-400
}

export function EmotionTimeline({ data = defaultData, height = 220 }: EmotionTimelineProps) {
  const padding = { top: 16, right: 16, bottom: 28, left: 32 }
  const width = 640

  const xScale = (i: number) =>
    padding.left + (i / Math.max(1, data.length - 1)) * (width - padding.left - padding.right)
  const yScale = (v: number) => padding.top + (1 - v / 100) * (height - padding.top - padding.bottom)

  const toPath = (key: keyof Point) => {
    const k = key as "happy" | "neutral" | "frustrated" | "confused"
    return data.map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(d[k])}`).join(" ")
  }

  const ticks = 5
  const yTicks = Array.from({ length: ticks + 1 }, (_, i) => Math.round((i * 100) / ticks)).reverse()

  return (
    <div className="w-full overflow-hidden">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
        {/* Grid */}
        {yTicks.map((t, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={yScale(t)}
              y2={yScale(t)}
              stroke="#e5e5e5"
              strokeWidth="1"
            />
            <text
              x={padding.left - 8}
              y={yScale(t)}
              fontSize="10"
              fill="#737373"
              textAnchor="end"
              dominantBaseline="middle"
            >
              {t}%
            </text>
          </g>
        ))}

        {/* X labels */}
        {data.map((d, i) => (
          <text key={d.time} x={xScale(i)} y={height - 8} fontSize="10" fill="#737373" textAnchor="middle">
            {d.time}
          </text>
        ))}

        {/* Lines with draw animation */}
        {(["happy", "neutral", "frustrated", "confused"] as const).map((k, idx) => (
          <motion.path
            key={k}
            d={toPath(k)}
            fill="none"
            stroke={colors[k]}
            strokeWidth={2}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1, ease: "easeInOut", delay: 0.1 * idx }}
          />
        ))}

        {/* Points */}
        {(["happy", "neutral", "frustrated", "confused"] as const).map((k) =>
          data.map((d, i) => <circle key={`${k}-${i}`} cx={xScale(i)} cy={yScale(d[k])} r={2.5} fill={colors[k]} />),
        )}
      </svg>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-neutral-600">
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded bg-emerald-500" /> 😊 Happy
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded bg-neutral-400" /> 😐 Neutral
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded bg-orange-400" /> 😤 Frustrated
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded bg-sky-400" /> 😕 Confused
        </span>
      </div>
    </div>
  )
}
