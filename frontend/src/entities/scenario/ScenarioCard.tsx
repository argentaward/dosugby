import type { components } from '@/shared/api'
import { Card } from '@/shared/ui'

export type ScenarioCardData = components['schemas']['ScenarioCard']
export type ScoredScenario = components['schemas']['ScoredScenario']

interface ScenarioCardProps {
  scenario: ScenarioCardData
}

export function ScenarioCard({ scenario }: ScenarioCardProps) {
  return (
    <Card className="flex flex-col gap-3 border-teal-200 bg-teal-50/40 transition-all duration-300 hover:border-teal-300 hover:bg-teal-50/60">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-base leading-tight font-black text-stone-900">{scenario.title}</h3>
        {typeof scenario.duration_min === 'number' ? (
          <span className="shrink-0 rounded-full bg-white/80 px-2.5 py-1 text-xs font-bold text-stone-600 shadow-sm">
            ~{scenario.duration_min} мин
          </span>
        ) : null}
      </div>
      {scenario.description ? (
        <p className="text-sm leading-relaxed font-medium text-stone-600">{scenario.description}</p>
      ) : null}
      <ol className="list-inside list-decimal space-y-1.5 text-sm text-stone-800">
        {scenario.steps.map((step) => (
          <li key={step.position}>
            <span className="font-bold">{step.place_name}</span>
            {step.note ? <span className="text-stone-600"> — {step.note}</span> : null}
          </li>
        ))}
      </ol>
    </Card>
  )
}
