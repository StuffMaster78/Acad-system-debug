interface ExitPopupConfig {
  is_enabled: boolean
  trigger?: 'exit_intent' | 'delay' | 'scroll_depth'
  title?: string
  body?: string
  primary_cta_label?: string
  primary_cta_url?: string
  secondary_cta_label?: string
  image_url?: string
  show_on_paths?: string[]
  suppress_on_paths?: string[]
  delay_seconds?: number
  scroll_depth_percent?: number
  cooldown_hours?: number
  max_shows_per_session?: number
  requires_marketing_consent?: boolean
}

const STORAGE_KEY = 'writing_system.exit_popup.dismissed_at'
const SESSION_KEY = 'writing_system.exit_popup.shown_count'

function apiUrl(path: string) {
  const config = useRuntimeConfig()
  const base = String(config.public.apiBase || '').replace(/\/+$/, '')
  return `${base}${path}`
}

function pathAllowed(config: ExitPopupConfig, path: string) {
  if ((config.suppress_on_paths || []).some((prefix) => path.startsWith(prefix))) return false
  const allowed = config.show_on_paths || []
  return allowed.length === 0 || allowed.some((prefix) => path.startsWith(prefix))
}

function coolingDown(config: ExitPopupConfig) {
  const dismissedAt = Number(localStorage.getItem(STORAGE_KEY) || 0)
  if (!dismissedAt) return false
  return Date.now() - dismissedAt < Number(config.cooldown_hours || 24) * 60 * 60 * 1000
}

export function useExitPopup() {
  const config = useState<ExitPopupConfig | null>('exit-popup.config', () => null)
  const open = useState('exit-popup.open', () => false)
  const loaded = useState('exit-popup.loaded', () => false)
  const armed = useState('exit-popup.armed', () => false)
  const consent = useCookieConsent()

  async function init() {
    if (loaded.value || import.meta.server) return
    loaded.value = true
    try {
      config.value = await $fetch<ExitPopupConfig>(apiUrl('/api/v1/privacy/exit-popup/'), { credentials: 'include' })
    } catch {
      config.value = { is_enabled: false }
    }
    if (!config.value?.is_enabled || !pathAllowed(config.value, window.location.pathname) || coolingDown(config.value)) return
    if (config.value.requires_marketing_consent && !consent.marketingAllowed.value) return
    if (Number(sessionStorage.getItem(SESSION_KEY) || 0) >= Number(config.value.max_shows_per_session || 1)) return
    armed.value = true
    if (config.value.trigger === 'delay') window.setTimeout(show, Number(config.value.delay_seconds || 15) * 1000)
    else if (config.value.trigger === 'scroll_depth') window.addEventListener('scroll', handleScroll, { passive: true })
    else document.addEventListener('mouseleave', handleMouseLeave)
  }

  function handleMouseLeave(event: MouseEvent) {
    if (event.clientY <= 0) show()
  }

  function handleScroll() {
    const height = document.documentElement.scrollHeight - window.innerHeight
    if (height > 0 && (window.scrollY / height) * 100 >= Number(config.value?.scroll_depth_percent || 65)) show()
  }

  function show() {
    if (!armed.value || open.value || !config.value?.is_enabled) return
    sessionStorage.setItem(SESSION_KEY, String(Number(sessionStorage.getItem(SESSION_KEY) || 0) + 1))
    open.value = true
    armed.value = false
    document.removeEventListener('mouseleave', handleMouseLeave)
    window.removeEventListener('scroll', handleScroll)
  }

  function dismiss() {
    localStorage.setItem(STORAGE_KEY, String(Date.now()))
    open.value = false
  }

  return { config, open, init, dismiss }
}
