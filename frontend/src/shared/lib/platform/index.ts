/**
 * Изоляция платформенных возможностей (браузер / будущий Telegram WebApp).
 * Остальной код приложения вызывает только эти функции и не знает о среде запуска.
 */

export interface SharePayload {
  title: string
  url: string
}

export async function shareLink(payload: SharePayload): Promise<boolean> {
  if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
    try {
      await navigator.share(payload)
      return true
    } catch {
      return false
    }
  }
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    await navigator.clipboard.writeText(payload.url)
    return true
  }
  return false
}
