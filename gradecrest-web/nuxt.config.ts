export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/sitemap'],

  compatibilityDate: '2026-06-10',

  // SSG — every marketing page pre-rendered at build time
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
        // Core service pages — crawlLinks discovers more from /services
        '/services/essay-writing',
        '/services/research-papers',
        '/services/dissertations',
        '/services/term-papers',
        '/services/case-studies',
        '/services/coursework',
        '/services/nursing-essays',
        '/services/admission-essays',
        '/services/editing-proofreading',
        '/services/literature-review',
        '/services/thesis-writing',
        '/services/data-analysis',
        '/services/online-class-help',
        '/services/homework-help',
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
