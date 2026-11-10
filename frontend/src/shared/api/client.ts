import createClient from 'openapi-fetch'

import type { paths } from './schema.gen'

const baseUrl = (import.meta.env['VITE_API_BASE_URL'] as string | undefined) ?? ''

export const apiClient = createClient<paths>({ baseUrl })
