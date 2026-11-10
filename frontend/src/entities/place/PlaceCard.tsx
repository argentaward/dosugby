import { Link, useLocation } from 'react-router'

import { Card } from '@/shared/ui'

import { formatIndoor, formatPriceLevel, type PlaceCardData } from './model'

interface PlaceCardProps {
  place: PlaceCardData
  score?: number
}

export function PlaceCard({ place, score }: PlaceCardProps) {
  const location = useLocation()
  const placeHref = `/places/${String(place.id)}`
  const linkState = { from: `${location.pathname}${location.search}` }

  return (
    <Card className="flex flex-col gap-3 sm:flex-row">
      {place.cover_url ? (
        <Link to={placeHref} state={linkState} className="block shrink-0">
          <img
            src={place.cover_url}
            alt={place.name}
            loading="lazy"
            className="h-40 w-full rounded-xl object-cover transition-transform duration-200 hover:scale-[1.02] sm:h-28 sm:w-36"
          />
        </Link>
      ) : null}
      <div className="flex flex-1 flex-col gap-2">
        <div className="flex items-start justify-between gap-2">
          <Link
            to={placeHref}
            state={linkState}
            className="text-base font-semibold text-stone-900 hover:text-teal-700"
          >
            {place.name}
          </Link>
          {typeof score === 'number' ? (
            <span className="shrink-0 rounded-full bg-teal-50 px-2.5 py-0.5 text-xs font-medium text-teal-800">
              совпадение: {score}
            </span>
          ) : null}
        </div>
        {place.summary ? <p className="text-sm text-stone-600">{place.summary}</p> : null}
        <div className="flex flex-wrap items-center gap-2 text-xs text-stone-500">
          <span>{formatPriceLevel(place.price_level)}</span>
          <span>·</span>
          <span>{formatIndoor(place.is_indoor)}</span>
          {place.address ? (
            <>
              <span>·</span>
              <span>{place.address}</span>
            </>
          ) : null}
        </div>
        {place.tags.length > 0 ? (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {place.tags.map((tag) => (
              <span
                key={`${tag.group}.${tag.code}`}
                className="rounded-full bg-stone-100 px-2.5 py-0.5 text-xs text-stone-700"
              >
                {tag.icon ? `${tag.icon} ` : ''}
                {tag.title}
              </span>
            ))}
          </div>
        ) : null}
      </div>
    </Card>
  )
}
