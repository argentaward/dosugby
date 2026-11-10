import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router'

import { HomePage } from '@/pages/home'
import { PlacePage } from '@/pages/place'
import { QuizPage } from '@/pages/quiz'
import { ResultsPage } from '@/pages/results'
import { AppHeader } from '@/widgets/header'

export function AppRoutes() {
  return (
    <div className="min-h-screen bg-[#FAF5E0] text-[#1C1B18]">
      <AppHeader />
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/places/:placeId" element={<PlacePage />} />
        </Routes>
      </main>
    </div>
  )
}

export function App() {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60_000,
            retry: 1,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
