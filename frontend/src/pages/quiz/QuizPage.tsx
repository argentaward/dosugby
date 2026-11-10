import { useNavigate } from 'react-router'

import { useTagGroupsQuery } from '@/entities/tag'
import { filtersToSearchParams, useQuizStore } from '@/features/quiz'
import { Button, Card, Chip } from '@/shared/ui'

const BUDGET_OPTIONS: ReadonlyArray<{ value: number | null; label: string }> = [
  { value: null, label: 'Любой' },
  { value: 0, label: 'Бесплатно' },
  { value: 1, label: 'Эконом' },
  { value: 2, label: 'Средний' },
]

const INDOOR_OPTIONS: ReadonlyArray<{ value: boolean | null; label: string }> = [
  { value: null, label: 'Не важно' },
  { value: false, label: '🌳 На улице' },
  { value: true, label: '🏠 Под крышей' },
]

export function QuizPage() {
  const navigate = useNavigate()
  const { data: tagGroups, isLoading, isError } = useTagGroupsQuery()
  const city = useQuizStore((state) => state.city)
  const tags = useQuizStore((state) => state.tags)
  const maxPrice = useQuizStore((state) => state.maxPrice)
  const indoor = useQuizStore((state) => state.indoor)
  const toggleTag = useQuizStore((state) => state.toggleTag)
  const setMaxPrice = useQuizStore((state) => state.setMaxPrice)
  const setIndoor = useQuizStore((state) => state.setIndoor)
  const reset = useQuizStore((state) => state.reset)

  const handleSubmit = () => {
    const params = filtersToSearchParams({ city, tags, maxPrice, indoor })
    void navigate(`/results?${params.toString()}`)
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-stone-900">Подбор досуга</h1>
        <Button variant="ghost" onClick={reset}>
          Сбросить
        </Button>
      </div>

      {isLoading ? <Card>Загружаем категории…</Card> : null}
      {isError ? <Card>Не удалось загрузить категории квиза.</Card> : null}

      {tagGroups?.map((group) => {
        const selectedCodes = tags[group.code] ?? []
        return (
          <Card key={group.code} className="space-y-3">
            <h2 className="text-base font-semibold text-stone-900">{group.title}</h2>
            <div className="flex flex-wrap gap-2">
              {group.tags.map((tag) => (
                <Chip
                  key={tag.code}
                  icon={tag.icon}
                  selected={selectedCodes.includes(tag.code)}
                  onClick={() => toggleTag(group.code, tag.code)}
                >
                  {tag.title}
                </Chip>
              ))}
            </div>
          </Card>
        )
      })}

      <Card className="space-y-3">
        <h2 className="text-base font-semibold text-stone-900">Погода / локация</h2>
        <div className="flex flex-wrap gap-2">
          {INDOOR_OPTIONS.map((option) => (
            <Chip
              key={String(option.value)}
              selected={indoor === option.value}
              onClick={() => setIndoor(option.value)}
            >
              {option.label}
            </Chip>
          ))}
        </div>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-base font-semibold text-stone-900">Бюджет</h2>
        <div className="flex flex-wrap gap-2">
          {BUDGET_OPTIONS.map((option) => (
            <Chip
              key={String(option.value)}
              selected={maxPrice === option.value}
              onClick={() => setMaxPrice(option.value)}
            >
              {option.label}
            </Chip>
          ))}
        </div>
      </Card>

      <div className="flex justify-end pt-2">
        <Button onClick={handleSubmit}>Показать варианты</Button>
      </div>
    </section>
  )
}
