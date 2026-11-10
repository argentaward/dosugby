import type { HTMLAttributes, ReactNode } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export function Card({ children, className = '', ...rest }: CardProps) {
  return (
    <div
      className={`rounded-2xl border-2 border-[#D4C9B8] bg-white p-5 shadow-[0_2px_8px_rgba(28,27,24,0.06)] transition-all duration-200 hover:border-[#C9B8A0] hover:shadow-[0_6px_20px_rgba(28,27,24,0.10)] ${className}`.trim()}
      {...rest}
    >
      {children}
    </div>
  )
}
