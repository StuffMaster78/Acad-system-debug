import { defineStore } from 'pinia'

// Shape of the /api/v1/portal-context/ response
export interface PortalContext {
  surface: 'client' | 'writer' | 'staff'
  portal: { code: string; name: string } | null
  website: {
    id: number
    name: string
    slug: string
    domain: string
  } | null
  branding: {
    brand_name: string
    tagline: string
    logo_url: string
    favicon_url: string
    primary_color: string
    secondary_color: string
    accent_color: string
    homepage_headline: string
    homepage_subheadline: string
    social_twitter_url: string
    social_facebook_url: string
    social_instagram_url: string
    social_youtube_url: string
    social_tiktok_url: string
    social_linkedin_url: string
  } | null
  payment_disclosure: {
    processor_name: string
    processor_display_name: string
    statement_descriptor: string
    client_disclosure_text: string
    support_contact: string
    requires_acknowledgement: boolean
    text: string
    pre_payment_notice: string
  } | null
  allowed_roles: string[]
  ga4_measurement_id: string | null
  promo_bar: { enabled: boolean; code: string; message: string; suffix: string } | null
}

// Shown before the real context loads — always has valid strings
const FALLBACK: PortalContext = {
  surface: 'writer',
  portal: null,
  website: { id: 0, name: 'Writers Creek', slug: 'writerscreek', domain: 'writerscreek.com' },
  branding: {
    brand_name: 'Writers Creek',
    tagline: 'A selective academic writing network.',
    logo_url: '',
    favicon_url: '',
    primary_color: '#0f172a',
    secondary_color: '#1e293b',
    accent_color: '#38bdf8',
    homepage_headline: 'Write at the highest standard.',
    homepage_subheadline: 'Competitive per-page rates, flexible assignments, and reliable bi-weekly payouts — for writers who take their craft seriously.',
    social_twitter_url: '',
    social_facebook_url: '',
    social_instagram_url: '',
    social_youtube_url: '',
    social_tiktok_url: '',
    social_linkedin_url: '',
  },
  payment_disclosure: {
    processor_name: 'OrderBridge Payments',
    processor_display_name: 'OrderBridge Payments',
    statement_descriptor: 'ORDERBRIDGE PAYMENTS',
    client_disclosure_text: '',
    support_contact: '',
    requires_acknowledgement: true,
    text: 'Writer earnings are processed securely by OrderBridge Payments.',
    pre_payment_notice: 'Payouts are processed by OrderBridge Payments, our billing partner.',
  },
  allowed_roles: ['writer'],
  ga4_measurement_id: null,
  promo_bar: null,
}

export const usePortalStore = defineStore('portal', {
  state: () => ({
    ctx: FALLBACK as PortalContext,
    ready: false,
    error: null as string | null,
  }),

  getters: {
    brandName:    (s) => s.ctx.branding?.brand_name    ?? s.ctx.website?.name ?? 'Writers Creek',
    tagline:      (s) => s.ctx.branding?.tagline        ?? '',
    logo:         (s) => s.ctx.branding?.logo_url       ?? null,
    favicon:      (s) => s.ctx.branding?.favicon_url    ?? null,
    primaryColor: (s) => s.ctx.branding?.primary_color  ?? '#0f172a',
    heroHeadline: (s) => s.ctx.branding?.homepage_headline    || FALLBACK.branding!.homepage_headline,
    heroSub:      (s) => s.ctx.branding?.homepage_subheadline || FALLBACK.branding!.homepage_subheadline,
    socialLinks:  (s) => {
      const b = s.ctx.branding
      if (!b) return []
      return [
        { name: 'Twitter / X', href: b.social_twitter_url,   icon: 'twitter'   },
        { name: 'Facebook',    href: b.social_facebook_url,  icon: 'facebook'  },
        { name: 'Instagram',   href: b.social_instagram_url, icon: 'instagram' },
        { name: 'YouTube',     href: b.social_youtube_url,   icon: 'youtube'   },
        { name: 'TikTok',      href: b.social_tiktok_url,    icon: 'tiktok'    },
        { name: 'LinkedIn',    href: b.social_linkedin_url,  icon: 'linkedin'  },
      ].filter(l => !!l.href)
    },
    disclosure:   (s) => s.ctx.payment_disclosure,
    ga4Id:        (s) => s.ctx.ga4_measurement_id,
    surface:      (s) => s.ctx.surface,
  },

  actions: {
    async fetch() {
      if (this.ready) return
      const api = useApi()
      try {
        const data = await api<PortalContext>('/api/v1/portal-context/')
        if (data?.website) {
          this.ctx = data
        }
      } catch (e) {
        this.error = 'Portal context unavailable — using defaults'
      } finally {
        this.ready = true
      }
    },
  },
})
