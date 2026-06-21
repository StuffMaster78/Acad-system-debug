export interface PromoDisplay {
  active: boolean
  id?: number
  display_type?: 'banner_strip' | 'countdown_banner' | 'popup'
  color_scheme?: 'brand' | 'dark' | 'warm'
  badge_text?: string
  headline?: string
  subtext?: string
  cta_label?: string
  cta_url?: string
  discount_code?: string
  starts_at?: string
  ends_at?: string
}

const DISMISS_KEY = 'writing_system.promo.dismissed'

function apiBase() {
  const config = useRuntimeConfig()
  return String(config.public.apiBase || '').replace(/\/+$/, '')
}

function isDismissed(promo: PromoDisplay): boolean {
  if (!import.meta.client || !promo.id) return false
  try {
    const stored = JSON.parse(localStorage.getItem(DISMISS_KEY) || '{}')
    // Dismiss resets when a new promo launches (different id)
    return stored.id === promo.id
  } catch { return false }
}

function markDismissed(id: number) {
  try { localStorage.setItem(DISMISS_KEY, JSON.stringify({ id })) } catch {}
}

export function usePromoDisplay() {
  const promo   = useState<PromoDisplay | null>('promo-display', () => null)
  const visible = useState('promo-display.visible', () => false)
  const loaded  = useState('promo-display.loaded', () => false)

  async function init() {
    if (loaded.value || import.meta.server) return
    loaded.value = true
    try {
      const data = await $fetch<PromoDisplay>(`${apiBase()}/api/v1/discounts/active/`, {
        credentials: 'include',
      })
      promo.value = data
      if (data.active && !isDismissed(data)) visible.value = true
    } catch {
      promo.value = { active: false }
    }
  }

  function dismiss() {
    visible.value = false
    if (promo.value?.id) markDismissed(promo.value.id)
  }

  return { promo, visible, init, dismiss }
}
