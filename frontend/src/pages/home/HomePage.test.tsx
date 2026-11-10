import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'

import { HomePage } from './HomePage'

function renderHomePage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('HomePage', () => {
  it('renders capsule search controls, showcase grid, and floating map button', () => {
    renderHomePage()

    expect(screen.getByRole('heading', { name: /куда сходим сегодня\?/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^подобрать$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /мне повезёт/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /показать на карте/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /старый город на закате/i })).toBeInTheDocument()
  })

  it('allows selecting mood and time options and toggling map view', async () => {
    const user = userEvent.setup()
    renderHomePage()

    const moodSegment = screen.getByRole('button', { name: /выбор настроения/i })
    await user.click(moodSegment)

    const outdoorOption = screen.getByRole('button', { name: /на воздухе/i })
    await user.click(outdoorOption)

    const timeSegment = screen.getByRole('button', { name: /выбор времени/i })
    await user.click(timeSegment)

    const eveningOption = screen.getByRole('button', { name: /вечер/i })
    await user.click(eveningOption)

    const mapButton = screen.getByRole('button', { name: /показать на карте/i })
    await user.click(mapButton)
    expect(screen.getByRole('button', { name: /показать сеткой/i })).toBeInTheDocument()
  })
})
