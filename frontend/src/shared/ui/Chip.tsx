import type { ButtonHTMLAttributes, ReactNode } from 'react'

interface ChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean
  icon?: string | null
  children: ReactNode
}

export function Chip({ selected = false, icon, children, className = '', ...rest }: ChipProps) {
  const stateClass = selected
    ? 'border-[#F4912F] bg-[#F4912F] text-[#1C1B18] font-bold shadow-2xs'
    : 'border-[#E6DEC8] bg-white text-[#57534E] hover:border-[#1C1B18] hover:text-[#1C1B18]'
  return (
    <button
      type="button"
      aria-pressed={selected}
      className={`inline-flex items-center gap-2 rounded-xl border px-3.5 py-2 text-sm font-semibold transition-all active:scale-[0.98] ${stateClass} ${className}`.trim()}
      {...rest}
    >
      {icon ? <span aria-hidden="true">{icon}</span> : null}
      <span>{children}</span>
    </button>
  )
}
