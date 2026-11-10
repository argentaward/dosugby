import { useMutation, useQuery } from '@tanstack/react-query'
import { create } from 'zustand'

import { DEFAULT_CITY_SLUG } from '@/entities/city'
import type { PlaceCardData } from '@/entities/place'
import { apiClient, type components } from '@/shared/api'

export type RecommendationRequest = components['schemas']['RecommendationRequest']
export type RecommendationResponse = components['schemas']['RecommendationResponse']

export interface QuizFilterState {
  city: string
  tags: Record<string, string[]>
  maxPrice: number | null
  indoor: boolean | null
}

interface QuizStore extends QuizFilterState {
  setCity: (city: string) => void
  toggleTag: (group: string, code: string) => void
  setMaxPrice: (maxPrice: number | null) => void
  setIndoor: (indoor: boolean | null) => void
  reset: () => void
}

const INITIAL_STATE: QuizFilterState = {
  city: DEFAULT_CITY_SLUG,
  tags: {},
  maxPrice: null,
  indoor: null,
}

export const useQuizStore = create<QuizStore>((set) => ({
  ...INITIAL_STATE,
  setCity: (city) => set({ city }),
  toggleTag: (group, code) =>
    set((state) => {
      const current = state.tags[group] ?? []
      const exists = current.includes(code)
      const next = exists ? current.filter((item) => item !== code) : [...current, code]
      return { tags: { ...state.tags, [group]: next } }
    }),
  setMaxPrice: (maxPrice) => set({ maxPrice }),
  setIndoor: (indoor) => set({ indoor }),
  reset: () => set(INITIAL_STATE),
}))

/**
 * Сериализация фильтров квиза в URLSearchParams (чтобы результатами можно было делиться по ссылке).
 */
export function filtersToSearchParams(filters: QuizFilterState): URLSearchParams {
  const params = new URLSearchParams()
  params.set('city', filters.city)
  for (const [group, codes] of Object.entries(filters.tags)) {
    if (codes.length > 0) {
      params.set(`tag_${group}`, codes.join(','))
    }
  }
  if (filters.maxPrice !== null) {
    params.set('max_price', String(filters.maxPrice))
  }
  if (filters.indoor !== null) {
    params.set('indoor', filters.indoor ? '1' : '0')
  }
  return params
}

export function searchParamsToFilters(params: URLSearchParams): QuizFilterState {
  const city = params.get('city') || DEFAULT_CITY_SLUG
  const tags: Record<string, string[]> = {}
  for (const [key, value] of params.entries()) {
    if (key.startsWith('tag_') && value) {
      const group = key.slice(4)
      tags[group] = value
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)
    }
  }
  const rawPrice = params.get('max_price')
  const parsedPrice = rawPrice !== null && rawPrice !== '' ? Number(rawPrice) : null
  const maxPrice = parsedPrice !== null && Number.isFinite(parsedPrice) ? parsedPrice : null

  const rawIndoor = params.get('indoor')
  const indoor = rawIndoor === '1' ? true : rawIndoor === '0' ? false : null

  return { city, tags, maxPrice, indoor }
}

export function useRecommendationsQuery(filters: QuizFilterState) {
  return useQuery({
    queryKey: ['recommendations', filters],
    queryFn: async (): Promise<RecommendationResponse> => {
      const { data, error } = await apiClient.POST('/api/v1/recommendations', {
        body: {
          city: filters.city,
          tags: filters.tags,
          max_price: filters.maxPrice,
          indoor: filters.indoor,
          limit: 40,
        },
      })
      if (error || !data) {
        throw new Error('Не удалось получить рекомендации')
      }
      return data
    },
  })
}

export function useLuckyPlaceMutation() {
  return useMutation({
    mutationFn: async (city: string): Promise<PlaceCardData> => {
      const { data, error } = await apiClient.GET('/api/v1/recommendations/random', {
        params: { query: { city } },
      })
      if (error || !data) {
        throw new Error('Не удалось выбрать случайное место')
      }
      return data
    },
  })
}
