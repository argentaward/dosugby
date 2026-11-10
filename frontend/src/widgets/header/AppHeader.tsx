import { Link, useLocation } from 'react-router'

export function AppHeader() {
  const { pathname } = useLocation()

  return (
    <header className="sticky top-0 z-30 border-b border-[#E6DEC8] bg-[#FAF5E0]/95 backdrop-blur-md transition-all">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6 lg:px-8">
        <Link
          to="/"
          className="group flex items-center gap-2.5 text-lg font-extrabold tracking-tight text-[#1C1B18]"
        >
          <span
            aria-hidden="true"
            className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#F4912F] text-sm font-black text-[#1C1B18] shadow-2xs transition-transform group-hover:scale-105"
          >
            D
          </span>
          <div className="flex flex-col">
            <span className="leading-tight">Dosug</span>
            <span className="text-[11px] font-bold tracking-wider text-[#57534E]">
              ГРОДНО И ОБЛАСТЬ
            </span>
          </div>
        </Link>

        <nav
          aria-label="Основная навигация"
          className="flex items-center gap-6 text-sm font-semibold text-[#57534E]"
        >
          <Link
            to="/"
            className={`relative py-1 transition-colors hover:text-[#1C1B18] ${
              pathname === '/'
                ? 'font-bold text-[#1C1B18] after:absolute after:right-0 after:bottom-0 after:left-0 after:h-0.5 after:rounded-full after:bg-[#F4912F]'
                : ''
            }`}
          >
            Обзор
          </Link>
          <Link
            to="/quiz"
            className={`relative py-1 transition-colors hover:text-[#1C1B18] ${
              pathname === '/quiz'
                ? 'font-bold text-[#1C1B18] after:absolute after:right-0 after:bottom-0 after:left-0 after:h-0.5 after:rounded-full after:bg-[#F4912F]'
                : ''
            }`}
          >
            Квиз-подбор
          </Link>
          <Link
            to="/results"
            className={`relative py-1 transition-colors hover:text-[#1C1B18] ${
              pathname === '/results'
                ? 'font-bold text-[#1C1B18] after:absolute after:right-0 after:bottom-0 after:left-0 after:h-0.5 after:rounded-full after:bg-[#F4912F]'
                : ''
            }`}
          >
            Все места
          </Link>
        </nav>

        <div className="hidden items-center gap-2 rounded-full border border-[#E6DEC8] bg-white px-3.5 py-1.5 text-xs font-bold text-[#1C1B18] shadow-2xs sm:flex">
          <span className="h-2 w-2 rounded-full bg-[#128DC4]" />
          <span>Беларусь · Гродно</span>
        </div>
      </div>
    </header>
  )
}
