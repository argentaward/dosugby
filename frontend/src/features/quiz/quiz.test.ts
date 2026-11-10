import { describe, expect, it } from 'vitest'

import { filtersToSearchParams, searchParamsToFilters, useQuizStore } from './index'

describe('quiz URL serialization', () => {
  it('round-trips filters through URLSearchParams', () => {
    const original = {
      city: 'grodno',
      tags: { audience: ['family', 'friends'], vibe: ['active'] },
      maxPrice: 1,
      indoor: false,
    }

    const params = filtersToSearchParams(original)
    const restored = searchParamsToFilters(params)

    expect(restored).toEqual(original)
  })

  it('falls back to default city when params are empty', () => {
    const restored = searchParamsToFilters(new URLSearchParams())
    expect(restored).toEqual({
      city: 'grodno',
      tags: {},
      maxPrice: null,
      indoor: null,
    })
  })
})

describe('useQuizStore', () => {
  it('toggles tag selection and resets state', () => {
    useQuizStore.getState().reset()
    useQuizStore.getState().toggleTag('audience', 'family')
    expect(useQuizStore.getState().tags['audience']).toEqual(['family'])

    useQuizStore.getState().toggleTag('audience', 'family')
    expect(useQuizStore.getState().tags['audience']).toEqual([])
  })
})
