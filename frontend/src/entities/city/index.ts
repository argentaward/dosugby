import { useQuery } from '@tanstack/react-query'

import { apiClient, type components } from '@/shared/api'

export type City = components['schemas']['CityOut']

export const DEFAULT_CITY_SLUG = 'grodno'

export function useCitiesQuery() {
  return useQuery({
    queryKey: ['cities'],
    queryFn: async (): Promise<City[]> => {
      const { data, error } = await apiClient.GET('/api/v1/cities')
      if (error || !data) {
        throw new Error(
          'Р СњР Вµ РЎС“Р Т‘Р В°Р В»Р С•РЎРѓРЎРЉ Р В·Р В°Р С–РЎР‚РЎС“Р В·Р С‘РЎвЂљРЎРЉ РЎРѓР С—Р С‘РЎРѓР С•Р С” Р С–Р С•РЎР‚Р С•Р Т‘Р С•Р Р†',
        )
      }
      return data
    },
  })
}
