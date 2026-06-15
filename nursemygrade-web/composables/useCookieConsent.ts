type ConsentSource = 'banner' | 'settings' | 'footer' | 'api'

interface ConsentPreferences {
  necessary: boolean
  preferences: boolean
  analytics: boolean
  marketing: boolean
}

interface CookieConsentRecord {
  anonymous_id: string
  consent: ConsentPreferences & {
    id: number
    consent_version: string
    policy_version: string
    source: ConsentSource
    revoked_at: string | null
  }
}

interface CookieConsentCurrent {
  has_consent: boolean
  anonymous_id: string | null
  consent: CookieConsentRecord['consent'] | null
}

declare global {
  interface Window {
    dataLayer?: unknown[]
    gtag?: (...args: unknown[]) => void
  }
}

const DEFAULT_CONSENT: ConsentPreferences = {
  necessary: true,
  preferences: false,
  analytics: false,
  marketing: false,
}

const CONSENT_COOKIE = 'writing_system.cookie_consent_id'
const MAX_AGE = 60 * 60 * 24 * 365

function apiUrl(path: string) {
  const config = useRuntimeConfig()
  const base = String(config.public.apiBase || '').replace(/\/+$/, '')
  return `${base}${path}`
}

let ga4InjectedFor: string | null = null

export function useCookieConsent() {
  const preferences = useState<ConsentPreferences>('cookie-consent.preferences', () => ({ ...DEFAULT_CONSENT }))
  const loaded = useState('cookie-consent.loaded', () => false)
  const bannerOpen = useState('cookie-consent.bannerOpen', () => false)
  const settingsOpen = useState('cookie-consent.settingsOpen', () => false)
  const anonymousId = useCookie<string | null>(CONSENT_COOKIE, {
    maxAge: MAX_AGE,
    sameSite: 'lax',
    path: '/',
  })

  const analyticsAllowed = computed(() => preferences.value.analytics)
  const marketingAllowed = computed(() => preferences.value.marketing)

  async function init() {
    if (loaded.value || import.meta.server) return
    try {
      const headers: Record<string, string> = {}
      if (anonymousId.value) headers['X-Consent-ID'] = anonymousId.value
      const current = await $fetch<CookieConsentCurrent>(apiUrl('/api/v1/privacy/cookie-consent/current/'), {
        credentials: 'include',
        headers,
      })
      if (current.has_consent && current.consent) {
        preferences.value = {
          necessary: true,
          preferences: current.consent.preferences,
          analytics: current.consent.analytics,
          marketing: current.consent.marketing,
        }
        anonymousId.value = current.anonymous_id
        bannerOpen.value = false
      } else {
        bannerOpen.value = true
      }
    } catch {
      bannerOpen.value = !anonymousId.value
    } finally {
      loaded.value = true
    }
  }

  async function save(next: Partial<ConsentPreferences>, source: ConsentSource = 'settings') {
    preferences.value = {
      necessary: true,
      preferences: Boolean(next.preferences),
      analytics: Boolean(next.analytics),
      marketing: Boolean(next.marketing),
    }
    bannerOpen.value = false
    settingsOpen.value = false
    const response = await $fetch<CookieConsentRecord>(apiUrl('/api/v1/privacy/cookie-consent/'), {
      method: 'POST',
      credentials: 'include',
      body: {
        anonymous_id: anonymousId.value || undefined,
        preferences: Boolean(next.preferences),
        analytics: Boolean(next.analytics),
        marketing: Boolean(next.marketing),
        source,
      },
    })
    anonymousId.value = response.anonymous_id
    preferences.value = {
      necessary: true,
      preferences: response.consent.preferences,
      analytics: response.consent.analytics,
      marketing: response.consent.marketing,
    }
  }

  return {
    preferences,
    loaded,
    bannerOpen,
    settingsOpen,
    analyticsAllowed,
    marketingAllowed,
    init,
    save,
    acceptAll: () => save({ preferences: true, analytics: true, marketing: true }, 'banner'),
    rejectOptional: () => save({ preferences: false, analytics: false, marketing: false }, 'banner'),
    openSettings: () => {
      settingsOpen.value = true
      bannerOpen.value = true
    },
  }
}

export function injectConsentAwareGa4(measurementId: string | null | undefined, analyticsAllowed: boolean) {
  if (!measurementId || !analyticsAllowed || import.meta.server || ga4InjectedFor === measurementId) return
  ga4InjectedFor = measurementId
  window.dataLayer = window.dataLayer || []
  window.gtag = window.gtag || function (...args: unknown[]) {
    window.dataLayer!.push(args)
  }
  window.gtag('js', new Date())
  window.gtag('config', measurementId)
  const script = document.createElement('script')
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`
  script.async = true
  document.head.appendChild(script)
}
