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
    '/services/**': { isr: 3600 },
    '/blog/**':     { ssr: true },
    '/blog':        { ssr: true },
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
        '/services/essay-writing',
        '/services/research-papers',
        '/services/dissertations',
        '/services/nursing-essays',
        '/services/editing-proofreading',
        '/services/data-analysis',
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
    apiBaseInternal: '', // NUXT_API_BASE_INTERNAL — http://web:8000 (server-only, bypasses nginx)
    public: {
      apiBase: '',       // NUXT_PUBLIC_API_BASE — https://gradecrest.com (browser-accessible)
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
    // Pulls all 160 CMS service page slugs at build/generate time
    sources: ['/api/__sitemap__/services'],
  },
})
