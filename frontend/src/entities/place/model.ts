import { useQuery } from '@tanstack/react-query'

import { apiClient, type components } from '@/shared/api'

export type PlaceCardData = components['schemas']['PlaceCard']
export type PlaceDetailData = components['schemas']['PlaceDetail']
export type ScoredPlace = components['schemas']['ScoredPlace']

const PRICE_LABELS: Record<number, string> = {
  0: 'Бесплатно',
  1: 'Эконом',
  2: 'Средний',
  3: 'Комфорт',
}

export function formatPriceLevel(level: number): string {
  return PRICE_LABELS[level] ?? 'Бюджет не указан'
}

export function formatIndoor(isIndoor: boolean | null | undefined): string {
  if (isIndoor === true) return 'Под крышей'
  if (isIndoor === false) return 'На улице'
  return 'В любую погоду'
}

export function usePlaceDetailQuery(placeId: number) {
  return useQuery({
    queryKey: ['place', placeId],
    enabled: Number.isFinite(placeId) && placeId > 0,
    queryFn: async (): Promise<PlaceDetailData> => {
      const { data, error } = await apiClient.GET('/api/v1/places/{place_id}', {
        params: { path: { place_id: placeId } },
      })
      if (error || !data) {
        throw new Error('Место не найдено')
      }
      return data
    },
  })
}
