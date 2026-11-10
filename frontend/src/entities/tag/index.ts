import { useQuery } from '@tanstack/react-query'

import { apiClient, type components } from '@/shared/api'

export type TagGroup = components['schemas']['TagGroupOut']
export type TagOption = components['schemas']['TagOptionOut']
export type Tag = components['schemas']['TagOut']

export function useTagGroupsQuery() {
  return useQuery({
    queryKey: ['tag-groups'],
    queryFn: async (): Promise<TagGroup[]> => {
      const { data, error } = await apiClient.GET('/api/v1/tags')
      if (error || !data) {
        throw new Error('Не удалось загрузить категории квиза')
      }
      return data
    },
  })
}
