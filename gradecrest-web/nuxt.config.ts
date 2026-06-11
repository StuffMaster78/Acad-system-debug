import { fileURLToPath } from 'node:url'

export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@nuxtjs/sitemap'],

  compatibilityDate: '2026-06-10',

  alias: {
    '@lucide/vue': fileURLToPath(new URL('./utils/lucide-icons.ts', import.meta.url)),
  },

  // Hybrid rendering:
  // - Static marketing pages pre-rendered at build time (fast, cacheable)
  // - Service pages rendered per-request so Wagtail edits go live immediately
  routeRules: {
    '/services/**': { ssr: true },
  },

  nitro: {
    prerender: {
      crawlLinks: true,
      routes: [
        '/',
        '/pricing',
        '/writers',
        '/how-it-works',
        '/reviews',
        '/faq',
        '/about',
        '/contact',
        '/order',
        '/apply',
        '/blog',
        '/services',
        '/legal/terms',
        '/legal/privacy',
        '/legal/refunds',
        '/auth/login',
        '/auth/register',
        '/auth/magic-link',
      ],
    },
  },

  runtimeConfig: {
    public: {
      apiBase: '',       // NUXT_PUBLIC_API_BASE — Django backend
      appUrl: '',        // NUXT_PUBLIC_APP_URL  — client portal (for login/register links)
      siteUrl: 'https://gradecrest.com',
    },
  },

  site: {
    url: 'https://gradecrest.com',
  },

  app: {
    head: {
      htmlAttrs: { lang: 'en' },
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap',
        },
      ],
    },
  },

  sitemap: {
    hostname: 'https://gradecrest.com',
    exclude: ['/auth/**', '/legal/**'],
  },
})
