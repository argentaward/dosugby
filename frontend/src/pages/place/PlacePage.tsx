import type { MouseEvent } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router'

import { formatIndoor, formatPriceLevel, usePlaceDetailQuery } from '@/entities/place'
import { filtersToSearchParams, useQuizStore } from '@/features/quiz'
import { Card } from '@/shared/ui'

function buildMapUrl(
  lat: number | null | undefined,
  lng: number | null | undefined,
): string | null {
  if (typeof lat !== 'number' || typeof lng !== 'number') {
    return null
  }
  return `https://www.openstreetmap.org/?mlat=${String(lat)}&mlon=${String(lng)}#map=17/${String(lat)}/${String(lng)}`
}

export function PlacePage() {
  const { placeId } = useParams<{ placeId: string }>()
  const numericId = Number(placeId)
  const { data: place, isLoading, isError } = usePlaceDetailQuery(numericId)

  const navigate = useNavigate()
  const location = useLocation()
  const quizState = useQuizStore()

  const stateFrom = (location.state as { from?: string } | null)?.from
  const storeParams = filtersToSearchParams(quizState).toString()
  const fallbackUrl = storeParams ? `/results?${storeParams}` : '/results'
  const backUrl = stateFrom || fallbackUrl

  const handleBack = (event: MouseEvent<HTMLAnchorElement>) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.button !== 0) {
      return
    }
    event.preventDefault()
    if (
      window.history.state &&
      typeof window.history.state.idx === 'number' &&
      window.history.state.idx > 0
    ) {
      navigate(-1)
    } else {
      void navigate(backUrl)
    }
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl">
        <Card>Загружаем карточку места…</Card>
      </div>
    )
  }

  if (isError || !place) {
    return (
      <div className="mx-auto max-w-3xl">
        <Card className="space-y-3">
          <p className="text-sm text-stone-700">Место не найдено.</p>
          <Link
            to={backUrl}
            onClick={handleBack}
            className="text-sm font-medium text-teal-800 hover:underline"
          >
            ← К списку рекомендаций
          </Link>
        </Card>
      </div>
    )
  }

  const mapUrl = buildMapUrl(place.lat, place.lng)

  return (
    <article className="mx-auto max-w-3xl space-y-4">
      <Link
        to={backUrl}
        onClick={handleBack}
        className="inline-block text-sm font-medium text-teal-800 hover:underline"
      >
        ← К результатам
      </Link>
      <Card className="space-y-4 p-6">
        {place.cover_url ? (
          <div className="relative overflow-hidden rounded-2xl bg-[#E6DEC8]/60">
            <img
              src={place.cover_url}
              alt=""
              aria-hidden="true"
              className="absolute inset-0 h-full w-full scale-110 object-cover opacity-35 blur-xl"
            />
            <img
              src={place.cover_url}
              alt={place.name}
              className="relative mx-auto max-h-[480px] w-full object-contain"
            />
          </div>
        ) : null}
        <div className="space-y-1">
          <h1 className="text-xl font-bold text-stone-900">{place.name}</h1>
          {place.summary ? <p className="text-sm text-stone-600">{place.summary}</p> : null}
        </div>
        {place.description ? (
          <p className="text-sm leading-relaxed text-stone-800">{place.description}</p>
        ) : null}
        <dl className="grid grid-cols-1 gap-3 pt-2 text-sm text-stone-700 sm:grid-cols-2">
          <div>
            <dt className="text-xs text-stone-500">Адрес</dt>
            <dd>{place.address || 'Не указан'}</dd>
          </div>
          <div>
            <dt className="text-xs text-stone-500">Бюджет и формат</dt>
            <dd>
              {formatPriceLevel(place.price_level)} · {formatIndoor(place.is_indoor)}
            </dd>
          </div>
          {place.opening_hours ? (
            <div>
              <dt className="text-xs text-stone-500">Время работы</dt>
              <dd>{place.opening_hours}</dd>
            </div>
          ) : null}
          {place.phone ? (
            <div>
              <dt className="text-xs text-stone-500">Телефон</dt>
              <dd>{place.phone}</dd>
            </div>
          ) : null}
        </dl>
        <div className="flex flex-wrap gap-3 pt-2 text-sm font-medium">
          {mapUrl ? (
            <a
              href={mapUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl bg-stone-100 px-3.5 py-2 text-stone-800 hover:bg-stone-200"
            >
              На карте
            </a>
          ) : null}
          {place.instagram_url ? (
            <a
              href={place.instagram_url}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl bg-stone-100 px-3.5 py-2 text-stone-800 hover:bg-stone-200"
            >
              Instagram
            </a>
          ) : null}
          {place.website_url ? (
            <a
              href={place.website_url}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl bg-stone-100 px-3.5 py-2 text-stone-800 hover:bg-stone-200"
            >
              Сайт
            </a>
          ) : null}
        </div>
      </Card>
    </article>
  )
}
