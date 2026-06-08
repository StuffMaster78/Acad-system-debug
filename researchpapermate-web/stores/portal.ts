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
}

// Shown before the real context loads — always has valid strings
const FALLBACK: PortalContext = {
  surface: 'client',
  portal: null,
  website: { id: 0, name: 'ResearchPaperMate', slug: 'researchpapermate', domain: 'researchpapermate.com' },
  branding: {
    brand_name: 'ResearchPaperMate',
    tagline: 'Reliable academic writing by humans, from $15/page.',
    logo_url: '',
    favicon_url: '',
    primary_color: '#163e88',
    secondary_color: '#0d2455',
    accent_color: '#14b8a6',
    homepage_headline: 'Get Research Papers, Essays & Assignments Done!',
    homepage_subheadline: 'Reliable research paper writing service from $15/page — written by human experts across 100+ subjects.',
  },
  payment_disclosure: {
    processor_name: 'OrderBridge Payments',
    processor_display_name: 'OrderBridge Payments',
    statement_descriptor: 'ORDERBRIDGE PAYMENTS',
    client_disclosure_text: '',
    support_contact: '',
    requires_acknowledgement: true,
    text: 'Your payment is securely processed by OrderBridge Payments.',
    pre_payment_notice: 'Payments are securely processed by OrderBridge Payments, our billing partner.',
  },
  allowed_roles: ['client'],
  ga4_measurement_id: null,
}

export const usePortalStore = defineStore('portal', {
  state: () => ({
    ctx: FALLBACK as PortalContext,
    ready: false,
    error: null as string | null,
  }),

  getters: {
    brandName:    (s) => s.ctx.branding?.brand_name    ?? s.ctx.website?.name ?? 'ResearchPaperMate',
    tagline:      (s) => s.ctx.branding?.tagline        ?? '',
    logo:         (s) => s.ctx.branding?.logo_url       ?? null,
    favicon:      (s) => s.ctx.branding?.favicon_url    ?? null,
    primaryColor: (s) => s.ctx.branding?.primary_color  ?? '#163e88',
    heroHeadline: (s) => s.ctx.branding?.homepage_headline    || FALLBACK.branding!.homepage_headline,
    heroSub:      (s) => s.ctx.branding?.homepage_subheadline || FALLBACK.branding!.homepage_subheadline,
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
        // Only accept a response with a valid website
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
