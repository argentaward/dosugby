import { Link, useSearchParams } from 'react-router'

import { PlaceCard } from '@/entities/place'
import { ScenarioCard } from '@/entities/scenario'
import { searchParamsToFilters, useRecommendationsQuery } from '@/features/quiz'
import { shareLink } from '@/shared/lib/platform'
import { Button, Card } from '@/shared/ui'

export function ResultsPage() {
  const [searchParams] = useSearchParams()
  const filters = searchParamsToFilters(searchParams)
  const { data, isLoading, isError } = useRecommendationsQuery(filters)

  const handleShare = () => {
    void shareLink({
      title: 'Подборка мест для отдыха — Dosug',
      url: window.location.href,
    })
  }

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold text-stone-900">Рекомендации</h1>
          <p className="text-xs text-stone-500">Отсортировано по совпадению с вашими фильтрами</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={handleShare}>
            Поделиться
          </Button>
          <Link
            to="/quiz"
            className="inline-flex items-center rounded-xl px-3 py-2 text-sm font-medium text-teal-800 hover:bg-teal-50"
          >
            Изменить фильтры
          </Link>
        </div>
      </div>

      {isLoading ? <Card>Подбираем лучшие места…</Card> : null}
      {isError ? <Card>Не удалось загрузить рекомендации.</Card> : null}

      {data && data.scenarios.length > 0 ? (
        <div className="space-y-3">
          <h2 className="text-base font-semibold text-stone-900">Готовые сценарии</h2>
          {data.scenarios.map((item) => (
            <ScenarioCard key={item.scenario.id} scenario={item.scenario} />
          ))}
        </div>
      ) : null}

      {data ? (
        <div className="space-y-3">
          <h2 className="text-base font-semibold text-stone-900">
            Места ({String(data.places.length)})
          </h2>
          {data.places.length === 0 ? (
            <Card>По этим фильтрам пока нет мест. Попробуйте ослабить условия.</Card>
          ) : (
            data.places.map((item) => (
              <PlaceCard key={item.place.id} place={item.place} score={item.score} />
            ))
          )}
        </div>
      ) : null}
    </section>
  )
}
