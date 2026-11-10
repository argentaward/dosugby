import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonVariant = 'primary' | 'secondary' | 'ghost'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  children: ReactNode
}

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary:
    'bg-[#F4912F] text-[#1C1B18] hover:bg-[#E07D1B] active:scale-[0.98] shadow-xs disabled:bg-[#E6DEC8] disabled:text-[#57534E] disabled:shadow-none',
  secondary:
    'bg-white text-[#1C1B18] border border-[#E6DEC8] hover:bg-[#FAF5E0] hover:border-[#1C1B18] active:scale-[0.98] shadow-2xs disabled:border-[#E6DEC8] disabled:text-[#57534E]',
  ghost:
    'bg-transparent text-[#57534E] hover:bg-[#E6DEC8]/40 hover:text-[#1C1B18] active:scale-[0.98]',
}

export function Button({
  variant = 'primary',
  className = '',
  type = 'button',
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold transition-all duration-150 disabled:cursor-not-allowed ${VARIANT_CLASSES[variant]} ${className}`.trim()}
      {...rest}
    >
      {children}
    </button>
  )
}
