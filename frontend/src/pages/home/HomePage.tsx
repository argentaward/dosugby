import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'

import { DEFAULT_CITY_SLUG, useCitiesQuery } from '@/entities/city'
import { formatIndoor, formatPriceLevel, type PlaceCardData } from '@/entities/place'
import type { ScenarioCardData } from '@/entities/scenario'
import {
  filtersToSearchParams,
  type QuizFilterState,
  useLuckyPlaceMutation,
  useQuizStore,
  useRecommendationsQuery,
} from '@/features/quiz'

type MoodId = 'all' | 'outdoor' | 'cozy' | 'culture' | 'family'
type TimeId = '1-2h' | 'half-day' | 'evening'

interface MoodOption {
  id: MoodId
  title: string
  subtitle: string
  group?: 'vibe' | 'audience'
  tagCode?: string
  icon?: (props: { className?: string }) => ReactNode
}

interface TimeOption {
  id: TimeId
  label: string
  subtitle: string
}

interface ShowcaseItem {
  id: string
  kind: 'scenario' | 'place'
  placeId?: number
  title: string
  keyPoints: string
  duration: string
  transport: string
  priceLabel: string
  rating: string
  moods: MoodId[]
  times: TimeId[]
  imageUrl: string
}

const FALLBACK_IMAGE_DATA_URI =
  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='600' viewBox='0 0 800 600'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='%23C9F2EA'/><stop offset='100%' stop-color='%23FFDCE4'/></linearGradient></defs><rect width='800' height='600' fill='url(%23g)'/><circle cx='650' cy='140' r='70' fill='%23F4912F' fill-opacity='0.35'/><path d='M0 460 Q220 380 420 440 T800 410 L800 600 L0 600 Z' fill='%23128DC4' fill-opacity='0.25'/></svg>"

const CATEGORY_FALLBACK_IMAGES: Record<string, string> = {
  culture:
    'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
  food: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80',
  active:
    'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
  calm: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80',
}

function pickPlaceImage(place: PlaceCardData): string {
  if (place.cover_url) {
    return place.cover_url
  }
  for (const tag of place.tags) {
    if (tag.group === 'vibe' && CATEGORY_FALLBACK_IMAGES[tag.code]) {
      return CATEGORY_FALLBACK_IMAGES[tag.code] ?? FALLBACK_IMAGE_DATA_URI
    }
  }
  return CATEGORY_FALLBACK_IMAGES['culture'] ?? FALLBACK_IMAGE_DATA_URI
}

function placeToShowcaseItem(place: PlaceCardData, score: number): ShowcaseItem {
  const tagTitles = place.tags.map((t) => t.title).join(' · ')
  return {
    id: `place-${String(place.id)}`,
    kind: 'place',
    placeId: place.id,
    title: place.name,
    keyPoints: place.summary || tagTitles || place.address || 'Локация в Гродно',
    duration: place.is_indoor ? '1–2 часа' : 'Прогулка',
    transport: formatIndoor(place.is_indoor),
    priceLabel: formatPriceLevel(place.price_level),
    rating: score > 0 ? `★ +${String(score)}` : 'Гродно',
    moods: ['all'],
    times: ['1-2h', 'half-day', 'evening'],
    imageUrl: pickPlaceImage(place),
  }
}

function scenarioToShowcaseItem(scenario: ScenarioCardData): ShowcaseItem {
  const stepNames = scenario.steps.map((s) => s.place_name).join(' → ')
  const firstStepId = scenario.steps[0]?.place_id
  const base: ShowcaseItem = {
    id: `scenario-${String(scenario.id)}`,
    kind: 'scenario',
    title: scenario.title,
    keyPoints: stepNames || scenario.description,
    duration: scenario.duration_min ? `~${String(scenario.duration_min)} мин` : 'Полдня',
    transport: `${String(scenario.steps.length)} точки маршрута`,
    priceLabel: 'Готовый маршрут',
    rating: 'Маршрут',
    moods: ['all'],
    times: ['half-day'],
    imageUrl:
      'https://images.unsplash.com/photo-1519677100203-a0e668c92439?auto=format&fit=crop&w=800&q=80',
  }
  if (typeof firstStepId === 'number') {
    base.placeId = firstStepId
  }
  return base
}

function buildLiveFilters(
  city: string,
  selectedMood: MoodId,
  quickFilters: string[],
): QuizFilterState {
  const vibes = new Set<string>()
  const audiences = new Set<string>()
  let indoor: boolean | null = null
  let maxPrice: number | null = null

  if (selectedMood === 'outdoor') {
    vibes.add('active')
    vibes.add('calm')
    indoor = false
  } else if (selectedMood === 'cozy') {
    vibes.add('food')
    vibes.add('calm')
  } else if (selectedMood === 'culture') {
    vibes.add('culture')
  } else if (selectedMood === 'family') {
    audiences.add('family')
  }

  if (quickFilters.includes('free')) maxPrice = 0
  if (quickFilters.includes('indoor')) indoor = true
  if (quickFilters.includes('kids')) audiences.add('family')
  if (quickFilters.includes('photo')) vibes.add('culture')

  const tags: Record<string, string[]> = {}
  if (audiences.size > 0) tags['audience'] = [...audiences]
  if (vibes.size > 0) tags['vibe'] = [...vibes]

  return { city: city || DEFAULT_CITY_SLUG, tags, maxPrice, indoor }
}

function CoffeeIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
      <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
      <line x1="6" y1="1" x2="6" y2="4" />
      <line x1="10" y1="1" x2="10" y2="4" />
      <line x1="14" y1="1" x2="14" y2="4" />
    </svg>
  )
}

function TreeIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M12 2L4 14h5v6h6v-6h5z" />
    </svg>
  )
}

function CastleIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M2 20h20" />
      <path d="M5 20V9l3-2 3 2v11" />
      <path d="M13 20V9l3-2 3 2v11" />
      <path d="M10 14h4v6h-4z" />
    </svg>
  )
}

function UsersIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  )
}

function SearchIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  )
}

function DiceIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <rect x="3" y="3" width="18" height="18" rx="4" />
      <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
      <circle cx="15.5" cy="15.5" r="1.5" fill="currentColor" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
    </svg>
  )
}

function MapIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
      <line x1="8" y1="2" x2="8" y2="18" />
      <line x1="16" y1="6" x2="16" y2="22" />
    </svg>
  )
}

function HeartIcon({
  className = 'h-5 w-5',
  filled = false,
}: {
  className?: string
  filled?: boolean
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill={filled ? '#17e0c6ff' : 'rgba(28, 27, 24, 0.45)'}
      stroke="white"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </svg>
  )
}

const DEFAULT_MOOD_OPTION: MoodOption = {
  id: 'all',
  title: 'Все',
  subtitle: 'Любой формат отдыха в Гродно',
}

const MOOD_OPTIONS: MoodOption[] = [
  DEFAULT_MOOD_OPTION,
  {
    id: 'outdoor',
    title: 'На воздухе',
    subtitle: 'Парки, берег Немана и сосны',
    group: 'vibe',
    tagCode: 'active',
    icon: TreeIcon,
  },
  {
    id: 'cozy',
    title: 'Уют и кофе',
    subtitle: 'Кофейни старого города и беседы',
    group: 'vibe',
    tagCode: 'calm',
    icon: CoffeeIcon,
  },
  {
    id: 'culture',
    title: 'Замки и улочки',
    subtitle: 'Советская, Старый замок и панорамы',
    group: 'vibe',
    tagCode: 'culture',
    icon: CastleIcon,
  },
  {
    id: 'family',
    title: 'С семьёй',
    subtitle: 'Зоопарк, Жилибер и детские маршруты',
    group: 'audience',
    tagCode: 'family',
    icon: UsersIcon,
  },
]

const DEFAULT_TIME_OPTION: TimeOption = {
  id: '1-2h',
  label: '1–2 часа',
  subtitle: 'Быстрая прогулка или кофе',
}

const TIME_OPTIONS: TimeOption[] = [
  DEFAULT_TIME_OPTION,
  {
    id: 'half-day',
    label: 'Полдня',
    subtitle: 'Маршрут на 3–4 часа',
  },
  {
    id: 'evening',
    label: 'Вечер',
    subtitle: 'Закатные панорамы и ужин',
  },
]

const SHOWCASE_ITEMS: ShowcaseItem[] = [
  {
    id: 'sunset-old-town',
    kind: 'scenario',
    title: 'Старый город на закате',
    keyPoints: 'Кофе на Советской → Старый Замок → Набережная',
    duration: '1–2 часа',
    transport: 'Пешком · Вечер',
    priceLabel: '3 точки маршрута',
    rating: '4.96',
    moods: ['all', 'culture', 'cozy'],
    times: ['1-2h', 'evening'],
    imageUrl:
      'https://images.unsplash.com/photo-1519677100203-a0e668c92439?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'weekend-escape',
    kind: 'scenario',
    title: 'Загородный побег в сосны',
    keyPoints: 'Августовский канал → Шлюз Домбровка → Форты',
    duration: 'Полдня',
    transport: 'На авто или велосипеде',
    priceLabel: 'Маршрут за город',
    rating: '4.92',
    moods: ['all', 'outdoor', 'family'],
    times: ['half-day'],
    imageUrl:
      'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'coffee-promenade',
    kind: 'scenario',
    title: 'Кофейные дворики и брусчатка',
    keyPoints: 'Ул. Замковая → Дворик на Советской → Смотровая',
    duration: '1–2 часа',
    transport: 'Пешком · Неспешно',
    priceLabel: '3 камерных места',
    rating: '4.94',
    moods: ['all', 'cozy', 'culture'],
    times: ['1-2h', 'evening'],
    imageUrl:
      'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'family-zhiliber',
    kind: 'scenario',
    title: 'Семейный день в центре',
    keyPoints: 'Парк Жилибера → Швейцарская долина → Зоопарк',
    duration: 'Полдня',
    transport: 'Пешком · С детьми',
    priceLabel: 'Семейный маршрут',
    rating: '4.89',
    moods: ['all', 'family', 'outdoor'],
    times: ['half-day', '1-2h'],
    imageUrl:
      'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'place-pyshki',
    kind: 'place',
    placeId: 1,
    title: 'Лесопарк «Пышки»',
    keyPoints: 'Тропа здоровья · Берег Немана · Велодорожки',
    duration: '1–2 часа',
    transport: 'На улице · Природа',
    priceLabel: 'Бесплатный вход',
    rating: '4.98',
    moods: ['all', 'outdoor', 'family'],
    times: ['1-2h', 'half-day'],
    imageUrl:
      'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'place-old-castle',
    kind: 'place',
    placeId: 4,
    title: 'Старый замок на Замковой',
    keyPoints: 'Королевский дворец · Музей · Панорама Немана',
    duration: '1–2 часа',
    transport: 'В помещении и на улице',
    priceLabel: 'Билет в музей',
    rating: '4.95',
    moods: ['all', 'culture', 'family'],
    times: ['1-2h', 'half-day', 'evening'],
    imageUrl:
      'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'place-kolozha',
    kind: 'place',
    placeId: 5,
    title: 'Коложская церковь и парк',
    keyPoints: 'Памятник XII века · Высокий берег Немана',
    duration: '1–2 часа',
    transport: 'Пешком · Тишина',
    priceLabel: 'Свободный доступ',
    rating: '4.97',
    moods: ['all', 'culture', 'outdoor'],
    times: ['1-2h', 'evening'],
    imageUrl:
      'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'place-sovetskaya',
    kind: 'place',
    placeId: 2,
    title: 'Вечерняя улица Советская',
    keyPoints: 'Старинная брусчатка · Кофейни · Фонари',
    duration: 'Вечер',
    transport: 'Пешком · Центр Гродно',
    priceLabel: 'Прогулочная зона',
    rating: '4.93',
    moods: ['all', 'cozy', 'culture'],
    times: ['evening', '1-2h'],
    imageUrl:
      'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?auto=format&fit=crop&w=800&q=80',
  },
]

export function HomePage() {
  const navigate = useNavigate()
  const location = useLocation()
  const linkState = { from: `${location.pathname}${location.search}` }
  const { data: cities } = useCitiesQuery()
  const city = useQuizStore((state) => state.city)
  const setCity = useQuizStore((state) => state.setCity)
  const tags = useQuizStore((state) => state.tags)
  const toggleTag = useQuizStore((state) => state.toggleTag)
  const reset = useQuizStore((state) => state.reset)
  const luckyMutation = useLuckyPlaceMutation()

  const [selectedMood, setSelectedMood] = useState<MoodId>('all')
  const [selectedTime, setSelectedTime] = useState<TimeId>('1-2h')
  const [openDropdown, setOpenDropdown] = useState<'mood' | 'time' | null>(null)
  const [savedIds, setSavedIds] = useState<string[]>([])
  const [showMap, setShowMap] = useState(false)
  const [quickFilters, setQuickFilters] = useState<string[]>([])

  const capsuleRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (capsuleRef.current && !capsuleRef.current.contains(event.target as Node)) {
        setOpenDropdown(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const currentMoodOption =
    MOOD_OPTIONS.find((item) => item.id === selectedMood) ?? DEFAULT_MOOD_OPTION
  const currentTimeOption =
    TIME_OPTIONS.find((item) => item.id === selectedTime) ?? DEFAULT_TIME_OPTION

  const handleSelectMood = (option: MoodOption) => {
    if (selectedMood === option.id && option.id !== 'all') {
      setSelectedMood('all')
      reset()
    } else {
      reset()
      setSelectedMood(option.id)
      if (option.group && option.tagCode) {
        toggleTag(option.group, option.tagCode)
      }
    }
    setOpenDropdown(null)
  }

  const handleSelectTime = (option: TimeOption) => {
    setSelectedTime(option.id)
    setOpenDropdown(null)
  }

  const liveFilters = buildLiveFilters(city, selectedMood, quickFilters)
  const { data: liveData } = useRecommendationsQuery(liveFilters)

  const handleSearch = () => {
    setOpenDropdown(null)
    if (selectedMood === 'all' && quickFilters.length === 0) {
      void navigate('/quiz')
      return
    }
    const params = filtersToSearchParams({
      city: liveFilters.city,
      tags: Object.keys(liveFilters.tags).length > 0 ? liveFilters.tags : tags,
      maxPrice: liveFilters.maxPrice,
      indoor: liveFilters.indoor,
    })
    void navigate(`/results?${params.toString()}`)
  }

  const handleLucky = async () => {
    setOpenDropdown(null)
    try {
      const place = await luckyMutation.mutateAsync(city || DEFAULT_CITY_SLUG)
      await navigate(`/places/${String(place.id)}`, { state: linkState })
    } catch {
      // Ошибка отображается через luckyMutation.isError
    }
  }

  const toggleSaved = (id: string) => {
    setSavedIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]))
  }

  const toggleQuickFilter = (filter: string) => {
    setQuickFilters((prev) =>
      prev.includes(filter) ? prev.filter((f) => f !== filter) : [...prev, filter],
    )
  }

  const hasLiveResults =
    liveData !== undefined && (liveData.places.length > 0 || liveData.scenarios.length > 0)

  const filteredItems: ShowcaseItem[] = hasLiveResults
    ? [
        ...liveData.scenarios.map((item) => scenarioToShowcaseItem(item.scenario)),
        ...liveData.places
          .filter((item) => !quickFilters.includes('photo') || Boolean(item.place.cover_url))
          .map((item) => placeToShowcaseItem(item.place, item.score)),
      ]
    : SHOWCASE_ITEMS.filter((item) => selectedMood === 'all' || item.moods.includes(selectedMood))

  return (
    <div className="relative pb-28">
      {/* 1. Header & Title */}
      <section className="space-y-4 pt-2 pb-4">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="font-['Unbounded'] text-2xl font-medium tracking-tight text-[#1C1B18] sm:text-3xl">
            Куда сходим сегодня?
          </h1>
          <p className="mt-1 text-sm font-medium text-[#57534E]">
            Выберите настроение и время прогулки — покажем лучшие маршруты и места Гродно
          </p>
        </div>

        {/* Поисковая капсула фильтров */}
        <div className="relative mx-auto max-w-4xl" ref={capsuleRef}>
          <div className="flex items-center justify-between rounded-full border border-[#E6DEC8] bg-white p-1.5 shadow-[0_8px_32px_rgba(28,27,24,0.08)] transition-all duration-300 hover:shadow-[0_12px_40px_rgba(28,27,24,0.14)] sm:p-2">
            {/* Segment 1: Mood */}
            <button
              type="button"
              aria-label={`Выбор настроения: ${currentMoodOption.title}`}
              aria-expanded={openDropdown === 'mood'}
              onClick={() => setOpenDropdown((prev) => (prev === 'mood' ? null : 'mood'))}
              className={`flex flex-1 items-center justify-between rounded-full px-3 py-2 text-left transition-colors sm:px-5 ${
                openDropdown === 'mood'
                  ? 'bg-[#FAF5E0]/70 ring-2 ring-[#F4912F]'
                  : 'hover:bg-[#FAF5E0]/40'
              }`}
            >
              <div className="min-w-0 pr-1 sm:pr-2">
                <span className="block text-[10px] font-black tracking-[0.08em] text-[#57534E] uppercase sm:text-[11px]">
                  Настроение
                </span>
                <span className="block truncate text-xs font-black text-[#1C1B18] sm:text-sm">
                  {currentMoodOption.title}
                </span>
              </div>
              {selectedMood !== 'all' ? (
                <span
                  role="button"
                  tabIndex={0}
                  aria-label="Сбросить настроение"
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedMood('all')
                    reset()
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.stopPropagation()
                      setSelectedMood('all')
                      reset()
                    }
                  }}
                  className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#E6DEC8] text-xs font-bold text-[#1C1B18] hover:bg-[#DCD3B8]"
                >
                  ×
                </span>
              ) : (
                <span className="text-xs text-[#57534E]">▾</span>
              )}
            </button>

            <div className="h-7 w-px shrink-0 bg-[#E6DEC8] sm:h-8" aria-hidden="true" />

            {/* Segment 2: Time */}
            <button
              type="button"
              aria-label={`Выбор времени: ${currentTimeOption.label}`}
              aria-expanded={openDropdown === 'time'}
              onClick={() => setOpenDropdown((prev) => (prev === 'time' ? null : 'time'))}
              className={`flex flex-1 items-center justify-between rounded-full px-3 py-2 text-left transition-colors sm:px-5 ${
                openDropdown === 'time'
                  ? 'bg-[#FAF5E0]/70 ring-2 ring-[#F4912F]'
                  : 'hover:bg-[#FAF5E0]/40'
              }`}
            >
              <div className="min-w-0 pr-1 sm:pr-2">
                <span className="block text-[10px] font-black tracking-[0.08em] text-[#57534E] uppercase sm:text-[11px]">
                  Время
                </span>
                <span className="block truncate text-xs font-black text-[#1C1B18] sm:text-sm">
                  {currentTimeOption.label}
                </span>
              </div>
              <span className="text-xs text-[#57534E]">▾</span>
            </button>

            <div className="hidden h-8 w-px shrink-0 bg-[#E6DEC8] md:block" aria-hidden="true" />

            {/* Segment 3: City */}
            <div className="hidden flex-col px-5 py-2 md:flex">
              <span className="text-[11px] font-black tracking-[0.08em] text-[#57534E] uppercase">
                Город
              </span>
              {cities && cities.length > 1 ? (
                <select
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="cursor-pointer bg-transparent text-sm font-extrabold text-[#1C1B18] focus:outline-none"
                >
                  {cities.map((c) => (
                    <option key={c.slug} value={c.slug}>
                      {c.name}
                    </option>
                  ))}
                </select>
              ) : (
                <span className="text-sm font-extrabold text-[#1C1B18]">Гродно</span>
              )}
            </div>

            {/* Segment 4: Actions */}
            <div className="flex shrink-0 items-center gap-1.5 pl-1 sm:gap-2 sm:pl-2">
              <button
                type="button"
                onClick={handleSearch}
                aria-label="Подобрать"
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-full bg-[#F4912F] p-2.5 text-xs font-black whitespace-nowrap text-[#1C1B18] shadow-[0_4px_12px_rgba(244,145,47,0.25)] transition-all duration-200 hover:bg-[#E07D1B] hover:shadow-[0_6px_16px_rgba(244,145,47,0.35)] active:scale-[0.96] sm:px-5 sm:py-2.5 sm:text-sm"
              >
                <SearchIcon className="h-4 w-4 text-[#1C1B18]" />
                <span className="hidden sm:inline">Подобрать</span>
              </button>

              <button
                type="button"
                disabled={luckyMutation.isPending}
                onClick={() => void handleLucky()}
                aria-label="Мне повезёт"
                className="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-full border border-[#E6DEC8] bg-[#FAF5E0] p-2.5 text-xs font-bold whitespace-nowrap text-[#1C1B18] transition-all duration-200 hover:border-[#1C1B18] hover:shadow-[0_4px_12px_rgba(28,27,24,0.08)] active:scale-[0.96] disabled:opacity-60 sm:px-3.5 sm:py-2.5"
              >
                <DiceIcon className="h-4 w-4 text-[#1C1B18]" />
                <span className="hidden md:inline">
                  {luckyMutation.isPending ? 'Ищем…' : 'Мне повезёт'}
                </span>
              </button>
            </div>
          </div>

          {/* Выпадающее меню настроения */}
          {openDropdown === 'mood' ? (
            <div
              role="region"
              aria-label="Выбор настроения"
              className="absolute top-full left-0 z-40 mt-3 w-full max-w-sm rounded-3xl border border-[#E6DEC8] bg-white p-3 shadow-[0_20px_60px_rgba(28,27,24,0.16)] backdrop-blur-sm max-sm:max-w-[calc(100vw-2rem)]"
            >
              <div className="space-y-1">
                {MOOD_OPTIONS.map((option) => {
                  const Icon = option.icon
                  const active = selectedMood === option.id
                  return (
                    <button
                      key={option.id}
                      type="button"
                      aria-pressed={active}
                      onClick={() => handleSelectMood(option)}
                      className={`flex w-full items-center gap-3.5 rounded-2xl p-2.5 text-left transition-colors ${
                        active
                          ? 'bg-[#FAF5E0] font-bold text-[#1C1B18]'
                          : 'text-[#1C1B18] hover:bg-[#FAF5E0]/60'
                      }`}
                    >
                      <span
                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${
                          active
                            ? 'border-[#F4912F] bg-[#F4912F] text-[#1C1B18]'
                            : 'border-[#E6DEC8] bg-[#FAF5E0]/50 text-[#1C1B18]'
                        }`}
                      >
                        {Icon ? (
                          <Icon className="h-4 w-4" />
                        ) : (
                          <span className="text-xs font-bold">ALL</span>
                        )}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-extrabold text-[#1C1B18]">{option.title}</p>
                        <p className="truncate text-xs font-medium text-[#57534E]">
                          {option.subtitle}
                        </p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          ) : null}

          {/* Floating Popover: Time */}
          {openDropdown === 'time' ? (
            <div
              role="region"
              aria-label="Выбор времени"
              className="absolute top-full left-2 z-40 mt-3 w-72 rounded-3xl border border-[#E6DEC8] bg-white p-3 shadow-[0_20px_60px_rgba(28,27,24,0.16)] backdrop-blur-sm max-sm:max-w-[calc(100vw-2rem)] sm:left-40"
            >
              <div className="space-y-1">
                {TIME_OPTIONS.map((option) => {
                  const active = selectedTime === option.id
                  return (
                    <button
                      key={option.id}
                      type="button"
                      aria-pressed={active}
                      onClick={() => handleSelectTime(option)}
                      className={`flex w-full items-center justify-between rounded-2xl p-3 text-left transition-colors ${
                        active
                          ? 'bg-[#FAF5E0] font-bold text-[#1C1B18]'
                          : 'text-[#1C1B18] hover:bg-[#FAF5E0]/60'
                      }`}
                    >
                      <div>
                        <p className="text-sm font-extrabold text-[#1C1B18]">{option.label}</p>
                        <p className="text-xs font-medium text-[#57534E]">{option.subtitle}</p>
                      </div>
                      {active ? <span className="text-xs font-bold text-[#F4912F]">✓</span> : null}
                    </button>
                  )
                })}
              </div>
            </div>
          ) : null}
        </div>

        {luckyMutation.isError ? (
          <p className="mx-auto max-w-md rounded-xl border border-red-300 bg-white p-2.5 text-center text-xs font-semibold text-red-800">
            Не удалось выбрать случайное место. Попробуйте ещё раз.
          </p>
        ) : null}
      </section>

      {/* Быстрые фильтры */}
      <section className="mx-auto max-w-6xl px-4 pt-8 pb-2">
        <div className="scrollbar-hide flex items-center gap-3 overflow-x-auto">
          {[
            {
              id: 'free',
              label: 'Бесплатно',
              icon: (props: { className?: string }) => (
                <svg
                  {...props}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="12" cy="12" r="1" />
                  <path d="M19.22 4.78a9 9 0 0 0-12.73 0m12.73 14.44a9 9 0 0 1-12.73 0M1 12a11 11 0 0 0 22 0 11 11 0 0 0-22 0" />
                </svg>
              ),
            },
            {
              id: 'indoor',
              label: 'В помещении',
              icon: (props: { className?: string }) => (
                <svg
                  {...props}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                  <polyline points="9 22 9 12 15 12 15 22" />
                </svg>
              ),
            },
            {
              id: 'photo',
              label: 'Для фото',
              icon: (props: { className?: string }) => (
                <svg
                  {...props}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              ),
            },
            {
              id: 'kids',
              label: 'С детьми',
              icon: (props: { className?: string }) => (
                <svg
                  {...props}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="12" cy="8" r="4" />
                  <path d="M12 14c-4 0-6 2-6 4v3h12v-3c0-2-2-4-6-4z" />
                  <circle cx="16" cy="18" r="2.5" />
                  <circle cx="8" cy="18" r="2.5" />
                </svg>
              ),
            },
          ].map((filter) => (
            <button
              key={filter.id}
              type="button"
              onClick={() => toggleQuickFilter(filter.id)}
              className={`flex shrink-0 items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition-all duration-200 ${
                quickFilters.includes(filter.id)
                  ? 'bg-[#F4912F] text-white shadow-[0_4px_12px_rgba(244,145,47,0.3)]'
                  : 'border border-[#D4C9B8] bg-white text-[#1C1B18] hover:border-[#C9B8A0] hover:bg-[#FAF5E0]'
              }`}
            >
              <filter.icon className="h-4 w-4 flex-shrink-0" />
              <span>{filter.label}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Основной контент: сетка или карта */}
      <div className="pt-6">
        {showMap ? (
          <section
            aria-label="Карта локаций Гродно"
            className="overflow-hidden rounded-3xl border border-[#E6DEC8] bg-white p-6 shadow-xs"
          >
            <div className="flex flex-wrap items-center justify-between gap-2 pb-4">
              <div>
                <h2 className="text-lg font-extrabold text-[#1C1B18]">
                  Карта сценариев и мест · Гродно
                </h2>
                <p className="text-xs font-medium text-[#57534E]">
                  Нажмите на карточку локации для перехода к подробностям
                </p>
              </div>
              <Link to="/results" className="text-xs font-bold text-[#1C1B18] underline">
                Открыть полный список →
              </Link>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {filteredItems.map((item) => (
                <Link
                  key={item.id}
                  to={item.placeId ? `/places/${String(item.placeId)}` : '/results'}
                  state={linkState}
                  className="flex items-center gap-3 rounded-2xl border border-[#E6DEC8] bg-[#FAF5E0]/60 p-3 transition-colors hover:border-[#F4912F]"
                >
                  <img
                    src={item.imageUrl}
                    alt={item.title}
                    onError={(event) => {
                      event.currentTarget.src = FALLBACK_IMAGE_DATA_URI
                    }}
                    className="h-14 w-14 shrink-0 rounded-xl object-cover"
                  />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-bold text-[#1C1B18]">{item.title}</p>
                    <p className="truncate text-xs text-[#57534E]">{item.duration}</p>
                    <span
                      className={`mt-1 inline-block rounded-full px-2 py-0.5 text-[11px] font-bold text-[#1C1B18] ${
                        item.kind === 'scenario' ? 'bg-[#C9F2EA]' : 'bg-[#FFDCE4]'
                      }`}
                    >
                      {item.kind === 'scenario' ? 'Маршрут' : 'Место'}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        ) : (
          <section aria-label="Сценарии и популярные места" className="mx-auto max-w-6xl px-4">
            {/* Сетка карточек */}
            <div className="grid grid-cols-1 gap-x-6 gap-y-12 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {filteredItems.map((item) => {
                const isSaved = savedIds.includes(item.id)
                const targetHref = item.placeId ? `/places/${String(item.placeId)}` : '/results'

                return (
                  <article key={item.id} className="group relative flex flex-col">
                    {/* Rounded Photo Container */}
                    <div className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl bg-[#E6DEC8] shadow-[0_2px_12px_rgba(28,27,24,0.06)] transition-shadow duration-300 group-hover:shadow-[0_8px_24px_rgba(28,27,24,0.12)]">
                      <Link to={targetHref} state={linkState} className="block h-full w-full">
                        <img
                          src={item.imageUrl}
                          alt={item.title}
                          loading="lazy"
                          onError={(event) => {
                            event.currentTarget.src = FALLBACK_IMAGE_DATA_URI
                          }}
                          className="h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-[1.08]"
                        />
                      </Link>

                      {/* Top-left Category & Time Badges */}
                      <div className="pointer-events-none absolute top-3 left-3 flex items-center gap-1.5">
                        <span
                          className={`rounded-full px-2.5 py-1 text-[11px] font-black text-[#1C1B18] shadow-[0_2px_8px_rgba(28,27,24,0.15)] backdrop-blur-sm ${
                            item.kind === 'scenario' ? 'bg-[#C9F2EA]/95' : 'bg-[#FFDCE4]/95'
                          }`}
                        >
                          {item.kind === 'scenario' ? 'Маршрут' : 'Место'}
                        </span>
                        <span className="rounded-full bg-white/95 px-2.5 py-1 text-[11px] font-black text-[#1C1B18] shadow-[0_2px_8px_rgba(28,27,24,0.15)] backdrop-blur-sm">
                          <span
                            aria-hidden="true"
                            className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-[#128DC4]"
                          />
                          {item.duration}
                        </span>
                      </div>

                      {/* Top-right favorite heart button */}
                      <button
                        type="button"
                        aria-label={
                          isSaved
                            ? `Убрать «${item.title}» из избранного`
                            : `Сохранить «${item.title}»`
                        }
                        aria-pressed={isSaved}
                        onClick={() => toggleSaved(item.id)}
                        className="absolute top-3 right-3 flex h-8 w-8 items-center justify-center rounded-full backdrop-blur-sm transition-all duration-200 hover:scale-110 hover:backdrop-blur-md active:scale-95"
                      >
                        <HeartIcon className="h-5 w-5" filled={isSaved} />
                      </button>

                      {/* Bottom carousel dots motif */}
                      <div
                        aria-hidden="true"
                        className="pointer-events-none absolute bottom-3 left-1/2 flex -translate-x-1/2 items-center gap-1.5"
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-white shadow-2xs" />
                        <span className="h-1.5 w-1.5 rounded-full bg-white/65" />
                        <span className="h-1.5 w-1.5 rounded-full bg-white/65" />
                        <span className="h-1.5 w-1.5 rounded-full bg-white/45" />
                      </div>
                    </div>

                    {/* Описание карточки */}
                    <Link to={targetHref} state={linkState} className="pt-4 text-left">
                      <div className="flex items-baseline justify-between gap-2">
                        <h2 className="truncate text-[15px] leading-tight font-black text-[#1C1B18] transition-colors duration-200 group-hover:text-[#F4912F]">
                          {item.title}
                        </h2>
                        <span className="shrink-0 text-xs font-extrabold text-[#1C1B18]">
                          ★ {item.rating}
                        </span>
                      </div>

                      <p className="mt-2 line-clamp-2 text-sm font-medium text-[#57534E]">
                        {item.keyPoints}
                      </p>

                      <p className="mt-2 text-xs text-[#8B8680]">
                        {item.duration} · {item.transport}
                      </p>

                      <p className="pt-2 text-[13px] text-[#1C1B18]">
                        <span className="font-extrabold underline decoration-[#128DC4] decoration-2 underline-offset-[5px]">
                          {item.priceLabel}
                        </span>
                      </p>
                    </Link>
                  </article>
                )
              })}
            </div>
          </section>
        )}
      </div>

      {/* Кнопка переключения вида карты */}
      <div className="fixed bottom-7 left-1/2 z-30 -translate-x-1/2">
        <button
          type="button"
          onClick={() => setShowMap((prev) => !prev)}
          aria-pressed={showMap}
          className="inline-flex items-center gap-2 rounded-full bg-[#1C1B18] px-5 py-3 text-xs font-black text-[#FAF5E0] shadow-[0_12px_32px_rgba(28,27,24,0.32)] transition-all duration-300 hover:scale-[1.06] hover:shadow-[0_16px_40px_rgba(28,27,24,0.40)] active:scale-[0.98]"
        >
          <span>{showMap ? 'Показать сеткой' : 'Показать на карте'}</span>
          <MapIcon className="h-4 w-4 text-[#F4912F]" />
        </button>
      </div>
    </div>
  )
}
